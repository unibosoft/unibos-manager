"""
CCTV Views
Web interface for camera monitoring and management
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from modules.web_ui.backend.views import BaseUIView
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, StreamingHttpResponse, HttpResponse
from django.utils import timezone
from django.db.models import Count, Q, Sum
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
import json
import uuid
from datetime import datetime, timedelta
import subprocess
from pathlib import Path

# Optional imports for video processing
try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    cv2 = None
    np = None

from .models import (
    Camera, CameraStream, RecordingSession, 
    RecordingSchedule, Alert, CameraGroup, StorageConfiguration
)


class CCTVDashboardView(LoginRequiredMixin, BaseUIView):
    """Main CCTV dashboard with camera grid"""
    template_name = 'cctv/dashboard.html'
    login_url = '/login/'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get user's cameras
        cameras = Camera.objects.filter(user=self.request.user, is_active=True)
        
        # Get camera statistics
        total_cameras = cameras.count()
        online_cameras = cameras.filter(status='online').count()
        recording_cameras = cameras.filter(status='recording').count()
        
        # Get recent alerts
        recent_alerts = Alert.objects.filter(
            camera__user=self.request.user,
            is_resolved=False
        ).order_by('-timestamp')[:10]
        
        # Get active recordings
        active_recordings = RecordingSession.objects.filter(
            user=self.request.user,
            status='recording'
        ).select_related('camera')
        
        # Get camera groups
        camera_groups = CameraGroup.objects.filter(user=self.request.user)
        
        # Storage statistics
        try:
            storage = StorageConfiguration.objects.filter(is_active=True).first()
            storage_percent = storage.get_usage_percent() if storage else 0
        except:
            storage = None
            storage_percent = 0
        
        context.update({
            'cameras': cameras,
            'total_cameras': total_cameras,
            'online_cameras': online_cameras,
            'recording_cameras': recording_cameras,
            'recent_alerts': recent_alerts,
            'active_recordings': active_recordings,
            'camera_groups': camera_groups,
            'storage': storage,
            'storage_percent': storage_percent,
            'page_title': 'cctv dashboard',
            'current_module': 'cctv',
        })
        
        return context


class CameraGridView(LoginRequiredMixin, BaseUIView):
    """Multi-camera grid view for monitoring"""
    template_name = 'cctv/camera_grid.html'
    login_url = '/login/'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get grid layout from query params
        layout = self.request.GET.get('layout', '2x2')
        group_id = self.request.GET.get('group', None)
        
        # Get cameras
        if group_id:
            try:
                group = CameraGroup.objects.get(id=group_id, user=self.request.user)
                cameras = group.cameras.filter(is_active=True)
                layout = group.grid_layout
            except CameraGroup.DoesNotExist:
                cameras = Camera.objects.filter(user=self.request.user, is_active=True)
        else:
            cameras = Camera.objects.filter(user=self.request.user, is_active=True)
        
        # Calculate grid dimensions - Extended for more cameras
        grid_map = {
            '1x1': (1, 1),
            '2x2': (2, 2),
            '2x3': (2, 3),
            '3x2': (3, 2),
            '3x3': (3, 3),
            '4x4': (4, 4),
            '4x5': (4, 5),
            '5x4': (5, 4),
            '5x5': (5, 5),
            '6x6': (6, 6),
            '8x4': (8, 4),  # 32 cameras
        }
        rows, cols = grid_map.get(layout, (2, 2))
        max_cameras = rows * cols
        
        context.update({
            'cameras': cameras[:max_cameras],
            'layout': layout,
            'rows': rows,
            'cols': cols,
            'camera_groups': CameraGroup.objects.filter(user=self.request.user),
            'selected_group': group_id,
            'page_title': 'camera grid view',
            'current_module': 'cctv',
        })
        
        return context


class CameraDetailView(LoginRequiredMixin, BaseUIView, DetailView):
    """Individual camera view with controls"""
    model = Camera
    template_name = 'cctv/camera_detail.html'
    context_object_name = 'camera'
    login_url = '/login/'
    
    def get_queryset(self):
        return Camera.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        camera = self.get_object()
        
        # Get camera streams
        streams = camera.streams.filter(is_active=True)
        
        # Get recent recordings
        recent_recordings = RecordingSession.objects.filter(
            camera=camera
        ).order_by('-start_time')[:10]
        
        # Get recent alerts
        recent_alerts = Alert.objects.filter(
            camera=camera
        ).order_by('-timestamp')[:10]
        
        # Get schedules
        schedules = RecordingSchedule.objects.filter(camera=camera)
        
        # Check if currently recording
        active_recording = RecordingSession.objects.filter(
            camera=camera,
            status='recording'
        ).first()
        
        context.update({
            'streams': streams,
            'recent_recordings': recent_recordings,
            'recent_alerts': recent_alerts,
            'schedules': schedules,
            'active_recording': active_recording,
            'page_title': f'camera: {camera.name}',
            'current_module': 'cctv',
        })
        
        return context


class LiveStreamView(LoginRequiredMixin, View):
    """Live stream endpoint for cameras"""
    
    def get(self, request, camera_id):
        """Get live stream for a camera"""
        camera = get_object_or_404(Camera, id=camera_id, user=request.user)
        
        # Check if camera is online
        if camera.status not in ['online', 'recording']:
            return JsonResponse({'error': 'camera is offline'}, status=503)
        
        # Get stream URL
        stream_url = camera.get_rtsp_url()
        if not stream_url:
            return JsonResponse({'error': 'stream url not available'}, status=404)
        
        # Return stream info for frontend
        return JsonResponse({
            'camera_id': str(camera.id),
            'name': camera.name,
            'stream_url': stream_url,
            'protocol': camera.protocol,
            'status': camera.status,
            'has_ptz': camera.has_ptz,
        })


class StreamProxyView(LoginRequiredMixin, View):
    """Proxy RTSP stream to browser-compatible format"""
    
    def get(self, request, camera_id):
        """Stream video to browser using MJPEG"""
        camera = get_object_or_404(Camera, id=camera_id, user=request.user)
        
        def generate():
            """Generate MJPEG stream"""
            rtsp_url = camera.get_rtsp_url()
            if not rtsp_url:
                return
            
            # Open video capture if cv2 available
            if not CV2_AVAILABLE:
                return
            
            cap = cv2.VideoCapture(rtsp_url)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            try:
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    # Encode frame as JPEG
                    _, buffer = cv2.imencode('.jpg', frame)
                    frame_bytes = buffer.tobytes()
                    
                    # Yield frame in MJPEG format
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            finally:
                cap.release()
        
        return StreamingHttpResponse(
            generate(),
            content_type='multipart/x-mixed-replace; boundary=frame'
        )


class SnapshotView(LoginRequiredMixin, View):
    """Get snapshot from camera"""
    
    def get(self, request, camera_id):
        """Get current snapshot from camera"""
        camera = get_object_or_404(Camera, id=camera_id, user=request.user)
        
        # Get snapshot URL
        snapshot_url = camera.get_snapshot_url()
        if snapshot_url:
            # Fetch snapshot from camera
            import requests
            try:
                response = requests.get(snapshot_url, timeout=5)
                if response.status_code == 200:
                    return HttpResponse(response.content, content_type='image/jpeg')
            except:
                pass
        
        # Fallback: capture frame from stream
        rtsp_url = camera.get_rtsp_url()
        if rtsp_url and CV2_AVAILABLE:
            cap = cv2.VideoCapture(rtsp_url)
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                _, buffer = cv2.imencode('.jpg', frame)
                return HttpResponse(buffer.tobytes(), content_type='image/jpeg')
        
        return HttpResponse(status=404)


class RecordingListView(LoginRequiredMixin, ListView):
    """List all recordings"""
    model = RecordingSession
    template_name = 'cctv/recordings.html'
    context_object_name = 'recordings'
    paginate_by = 20
    login_url = '/login/'
    
    def get_queryset(self):
        queryset = RecordingSession.objects.filter(
            user=self.request.user
        ).select_related('camera')
        
        # Filter by camera
        camera_id = self.request.GET.get('camera')
        if camera_id:
            queryset = queryset.filter(camera_id=camera_id)
        
        # Filter by date
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        if date_from:
            queryset = queryset.filter(start_time__gte=date_from)
        if date_to:
            queryset = queryset.filter(start_time__lte=date_to)
        
        # Filter by type
        recording_type = self.request.GET.get('type')
        if recording_type:
            queryset = queryset.filter(recording_type=recording_type)
        
        return queryset.order_by('-start_time')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'cameras': Camera.objects.filter(user=self.request.user),
            'page_title': 'recordings',
            'current_module': 'cctv',
        })
        return context


class RecordingPlaybackView(LoginRequiredMixin, DetailView):
    """Playback recorded video"""
    model = RecordingSession
    template_name = 'cctv/playback.html'
    context_object_name = 'recording'
    login_url = '/login/'
    
    def get_queryset(self):
        return RecordingSession.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        recording = self.get_object()
        
        # Get timeline events (motion, alerts)
        alerts = Alert.objects.filter(
            camera=recording.camera,
            timestamp__gte=recording.start_time,
            timestamp__lte=recording.end_time if recording.end_time else timezone.now()
        ).order_by('timestamp')
        
        context.update({
            'alerts': alerts,
            'page_title': f'playback: {recording.camera.name}',
            'current_module': 'cctv',
        })
        return context


class AlertListView(LoginRequiredMixin, ListView):
    """List all alerts"""
    model = Alert
    template_name = 'cctv/alerts.html'
    context_object_name = 'alerts'
    paginate_by = 20
    login_url = '/login/'
    
    def get_queryset(self):
        queryset = Alert.objects.filter(
            user=self.request.user
        ).select_related('camera')
        
        # Filter by status
        status = self.request.GET.get('status', 'unresolved')
        if status == 'unresolved':
            queryset = queryset.filter(is_resolved=False)
        elif status == 'resolved':
            queryset = queryset.filter(is_resolved=True)
        
        # Filter by type
        alert_type = self.request.GET.get('type')
        if alert_type:
            queryset = queryset.filter(alert_type=alert_type)
        
        # Filter by priority
        priority = self.request.GET.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
        
        return queryset.order_by('-timestamp')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get alert statistics
        total_alerts = Alert.objects.filter(user=self.request.user).count()
        unresolved_alerts = Alert.objects.filter(
            user=self.request.user,
            is_resolved=False
        ).count()
        
        context.update({
            'total_alerts': total_alerts,
            'unresolved_alerts': unresolved_alerts,
            'page_title': 'security alerts',
            'current_module': 'cctv',
        })
        return context


class CameraSettingsView(LoginRequiredMixin, TemplateView):
    """Camera configuration and settings"""
    template_name = 'cctv/settings.html'
    login_url = '/login/'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all cameras
        cameras = Camera.objects.filter(user=self.request.user)
        
        # Get camera groups
        camera_groups = CameraGroup.objects.filter(user=self.request.user)
        
        # Get storage configuration
        storage = StorageConfiguration.objects.filter(is_active=True).first()
        
        context.update({
            'cameras': cameras,
            'camera_groups': camera_groups,
            'storage': storage,
            'page_title': 'cctv settings',
            'current_module': 'cctv',
        })
        
        return context


# API Views for AJAX operations

@login_required
@csrf_exempt
def start_recording(request, camera_id):
    """Start recording for a camera"""
    if request.method != 'POST':
        return JsonResponse({'error': 'method not allowed'}, status=405)
    
    camera = get_object_or_404(Camera, id=camera_id, user=request.user)
    
    # Check if already recording
    existing = RecordingSession.objects.filter(
        camera=camera,
        status='recording'
    ).first()
    
    if existing:
        return JsonResponse({'error': 'already recording'}, status=400)
    
    # Create new recording session
    recording = RecordingSession.objects.create(
        camera=camera,
        user=request.user,
        recording_type='manual',
        status='recording',
        start_time=timezone.now()
    )
    
    # Update camera status
    camera.status = 'recording'
    camera.save()
    
    return JsonResponse({
        'success': True,
        'recording_id': str(recording.id),
        'message': 'recording started'
    })


@login_required
@csrf_exempt
def stop_recording(request, camera_id):
    """Stop recording for a camera"""
    if request.method != 'POST':
        return JsonResponse({'error': 'method not allowed'}, status=405)
    
    camera = get_object_or_404(Camera, id=camera_id, user=request.user)
    
    # Find active recording
    recording = RecordingSession.objects.filter(
        camera=camera,
        status='recording'
    ).first()
    
    if not recording:
        return JsonResponse({'error': 'no active recording'}, status=404)
    
    # Stop recording
    recording.end_time = timezone.now()
    recording.status = 'completed'
    recording.calculate_duration()
    recording.save()
    
    # Update camera status
    camera.status = 'online'
    camera.save()
    
    return JsonResponse({
        'success': True,
        'recording_id': str(recording.id),
        'duration': recording.duration,
        'message': 'recording stopped'
    })


@login_required
def camera_ptz_control(request, camera_id):
    """Control PTZ camera movements"""
    camera = get_object_or_404(Camera, id=camera_id, user=request.user)
    
    if not camera.has_ptz:
        return JsonResponse({'error': 'camera does not support ptz'}, status=400)
    
    command = request.GET.get('command')
    if command not in ['up', 'down', 'left', 'right', 'zoom_in', 'zoom_out', 'home']:
        return JsonResponse({'error': 'invalid command'}, status=400)
    
    # PTZ control implementation would go here
    # This would integrate with camera-specific APIs
    
    return JsonResponse({
        'success': True,
        'command': command,
        'message': f'ptz command {command} executed'
    })


@login_required
def resolve_alert(request, alert_id):
    """Mark alert as resolved"""
    if request.method != 'POST':
        return JsonResponse({'error': 'method not allowed'}, status=405)
    
    alert = get_object_or_404(Alert, id=alert_id, user=request.user)
    
    data = json.loads(request.body)
    notes = data.get('notes', '')
    
    alert.resolve(request.user, notes)
    
    return JsonResponse({
        'success': True,
        'alert_id': str(alert.id),
        'message': 'alert resolved'
    })


@login_required
def camera_status(request):
    """Get status of all cameras"""
    cameras = Camera.objects.filter(user=request.user)
    
    status_data = []
    for camera in cameras:
        status_data.append({
            'id': str(camera.id),
            'name': camera.name,
            'location': camera.location,
            'status': camera.status,
            'is_active': camera.is_active,
            'recording_enabled': camera.recording_enabled,
            'last_seen': camera.last_seen.isoformat() if camera.last_seen else None,
        })
    
    return JsonResponse({
        'cameras': status_data,
        'timestamp': timezone.now().isoformat()
    })