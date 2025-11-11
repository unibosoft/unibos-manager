"""
UNIBOS Web UI API Views
RESTful API endpoints for the web interface
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from django.db.models import Count, Q
from datetime import timedelta

from .models import SessionLog, ModuleAccess, UIPreferences, SystemStatus, CommandHistory
from .serializers import (
    SessionLogSerializer,
    ModuleAccessSerializer,
    UIPreferencesSerializer,
    SystemStatusSerializer,
    CommandHistorySerializer,
    CommandExecuteSerializer
)


class SessionLogViewSet(viewsets.ModelViewSet):
    """Session log management"""
    queryset = SessionLog.objects.all()
    serializer_class = SessionLogSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            # Regular users can only see their own sessions
            queryset = queryset.filter(user=self.request.user)
        return queryset
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active sessions"""
        active_sessions = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(active_sessions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def end(self, request, pk=None):
        """End a session"""
        session = self.get_object()
        session.end_session()
        return Response({'status': 'session ended'})


class ModuleAccessViewSet(viewsets.ReadOnlyModelViewSet):
    """Module access tracking"""
    queryset = ModuleAccess.objects.all()
    serializer_class = ModuleAccessSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        return queryset
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get module usage statistics"""
        # Get statistics for the last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        stats = self.get_queryset().filter(
            accessed_at__gte=thirty_days_ago
        ).values('module').annotate(
            access_count=Count('id')
        ).order_by('-access_count')
        
        return Response({
            'period': '30_days',
            'statistics': stats
        })
    
    @action(detail=False, methods=['post'])
    def track(self, request):
        """Track module access"""
        module = request.data.get('module')
        action = request.data.get('action')
        data = request.data.get('data')
        
        access = ModuleAccess.objects.create(
            user=request.user,
            module=module,
            action=action,
            data=data
        )
        
        serializer = self.get_serializer(access)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UIPreferencesViewSet(viewsets.ModelViewSet):
    """User UI preferences"""
    serializer_class = UIPreferencesSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return UIPreferences.objects.filter(user=self.request.user)
    
    def get_object(self):
        """Get or create preferences for the current user"""
        preferences, created = UIPreferences.objects.get_or_create(
            user=self.request.user
        )
        return preferences
    
    @action(detail=False, methods=['get', 'patch'])
    def current(self, request):
        """Get or update current user's preferences"""
        preferences = self.get_object()
        
        if request.method == 'GET':
            serializer = self.get_serializer(preferences)
            return Response(serializer.data)
        
        elif request.method == 'PATCH':
            serializer = self.get_serializer(
                preferences,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class SystemStatusViewSet(viewsets.ReadOnlyModelViewSet):
    """System status monitoring"""
    queryset = SystemStatus.objects.all()
    serializer_class = SystemStatusSerializer
    permission_classes = [AllowAny]  # Public status endpoint
    
    @action(detail=False, methods=['get'])
    def overall(self, request):
        """Get overall system status"""
        overall_status = SystemStatus.get_overall_status()
        modules = self.get_queryset()
        
        return Response({
            'overall_status': overall_status,
            'modules': SystemStatusSerializer(modules, many=True).data,
            'timestamp': timezone.now().isoformat()
        })
    
    @action(detail=False, methods=['get'])
    def health(self, request):
        """Health check endpoint"""
        modules = self.get_queryset()
        unhealthy = modules.filter(
            Q(status='offline') | Q(health_score__lt=50)
        ).exists()
        
        return Response({
            'healthy': not unhealthy,
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK if not unhealthy else status.HTTP_503_SERVICE_UNAVAILABLE)


class CommandHistoryViewSet(viewsets.ModelViewSet):
    """Command history and execution"""
    queryset = CommandHistory.objects.all()
    serializer_class = CommandHistorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        
        # Filter by module if specified
        module = self.request.query_params.get('module')
        if module:
            queryset = queryset.filter(module=module)
        
        return queryset
    
    @action(detail=False, methods=['post'])
    def execute(self, request):
        """Execute a command and save to history"""
        serializer = CommandExecuteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        command = serializer.validated_data['command']
        module = serializer.validated_data.get('module')
        
        # Execute the command (mock implementation)
        import time
        start_time = time.time()
        
        try:
            # Here you would execute the actual command
            # For now, we'll just simulate it
            output = f"Command '{command}' executed successfully"
            success = True
            error_message = None
        except Exception as e:
            output = None
            success = False
            error_message = str(e)
        
        execution_time = time.time() - start_time
        
        # Save to history
        history = CommandHistory.objects.create(
            user=request.user,
            command=command,
            module=module,
            success=success,
            output=output,
            error_message=error_message,
            execution_time=execution_time
        )
        
        return Response({
            'id': history.id,
            'command': command,
            'success': success,
            'output': output,
            'error_message': error_message,
            'execution_time': execution_time
        })
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent command history"""
        limit = int(request.query_params.get('limit', 10))
        recent = self.get_queryset()[:limit]
        serializer = self.get_serializer(recent, many=True)
        return Response(serializer.data)