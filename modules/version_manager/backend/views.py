"""
Version Manager Views
Handles version archive analysis and git operations with real-time updates
"""

import os
import glob
import statistics
import subprocess
import json
from pathlib import Path
from datetime import datetime

from django.shortcuts import render, redirect
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.core.cache import cache

from .models import VersionArchive, ScanSession, GitStatus
from apps.web_ui.views import BaseUIView
from django.core.paginator import Paginator
from django.db.models import Q, Avg, Count


class VersionManagerView(LoginRequiredMixin, BaseUIView):
    """Main version manager dashboard view"""
    template_name = 'version_manager/dashboard.html'
    login_url = '/accounts/login/'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Perform real-time scan of archive directory
        import os
        import glob
        # Path from: apps/web/backend/apps/version_manager/views.py
        # Need to go up 6 levels to reach unibos root
        base_dir = Path(__file__).parent.parent.parent.parent.parent.parent
        archive_path = base_dir / "archive" / "versions"
        
        # Get all version directories and calculate real-time stats
        version_dirs = sorted(glob.glob(f"{archive_path}/unibos_v*"))
        total_archives = len(version_dirs)
        total_size_bytes = 0
        archives_data = []
        
        for version_dir in version_dirs:
            if os.path.isdir(version_dir):
                dirname = os.path.basename(version_dir)
                # Calculate directory size
                dir_size = 0
                file_count = 0
                for dirpath, dirnames, filenames in os.walk(version_dir):
                    file_count += len(filenames)
                    for filename in filenames:
                        filepath = os.path.join(dirpath, filename)
                        try:
                            dir_size += os.path.getsize(filepath)
                        except:
                            pass
                
                total_size_bytes += dir_size
                
                # Extract version number
                parts = dirname.split('_')
                if len(parts) >= 2:
                    version_num = parts[1][1:] if parts[1].startswith('v') else parts[1]
                    archives_data.append({
                        'version': version_num,
                        'size_mb': dir_size / (1024 * 1024),
                        'file_count': file_count,
                        'dirname': dirname
                    })
        
        # Sort by version number (descending)
        archives_data.sort(key=lambda x: int(x['version']) if x['version'].isdigit() else 0, reverse=True)
        
        # Calculate statistics
        if total_archives > 0:
            total_size_gb = total_size_bytes / (1024**3)
            avg_size_mb = (total_size_bytes / (1024**2)) / total_archives
            
            # Calculate anomalies based on Z-score
            import statistics
            if len(archives_data) > 2:
                # Work directly with MB values for consistency
                sizes_mb = [a['size_mb'] for a in archives_data]
                mean_size_mb = statistics.mean(sizes_mb)
                stdev_size_mb = statistics.stdev(sizes_mb) if len(sizes_mb) > 1 else 0

                anomaly_count = 0
                for archive in archives_data:
                    if stdev_size_mb > 0:
                        # Z-score: how many standard deviations away from mean
                        z_score = abs((archive['size_mb'] - mean_size_mb) / stdev_size_mb)
                        archive['z_score'] = z_score
                        # Use threshold of 2.5 to reduce false positives (99% confidence)
                        archive['is_anomaly'] = z_score > 2.5
                        if archive['is_anomaly']:
                            anomaly_count += 1
                    else:
                        archive['z_score'] = 0
                        archive['is_anomaly'] = False
            else:
                anomaly_count = 0
        else:
            total_size_gb = 0
            avg_size_mb = 0
            anomaly_count = 0
        
        # Get or update database records for display
        archives = []
        for data in archives_data[:20]:  # Show top 20
            # Extract build info from dirname (format: unibos_vXXX_YYYYMMDD_HHMM)
            build = None
            if '_' in data['dirname']:
                parts = data['dirname'].split('_')
                if len(parts) >= 3:
                    # Get the date and time parts
                    build = f"{parts[-2]}_{parts[-1]}" if len(parts) >= 4 else parts[-1]
            
            archive, created = VersionArchive.objects.get_or_create(
                version=data['version'],
                defaults={
                    'path': f"{archive_path}/{data['dirname']}",
                    'size_bytes': int(data['size_mb'] * 1024 * 1024),
                    'size_mb': data['size_mb'],
                    'file_count': data['file_count'],
                    'z_score': data.get('z_score', 0),
                    'is_anomaly': data.get('is_anomaly', False),
                }
            )
            # Update if exists
            if not created:
                archive.size_bytes = int(data['size_mb'] * 1024 * 1024)
                archive.size_mb = data['size_mb']
                archive.file_count = data['file_count']
                archive.z_score = data.get('z_score', 0)
                archive.is_anomaly = data.get('is_anomaly', False)
                archive.save()
            
            # Add build info to archive object
            archive.build = build
            archives.append(archive)
        
        # Get latest scan session
        latest_scan = ScanSession.objects.first()
        
        # Get latest git status
        latest_git = GitStatus.objects.first()
        
        context.update({
            'archives': archives,
            'total_archives': total_archives,
            'total_size_gb': total_size_gb,
            'average_size_mb': avg_size_mb,
            'anomaly_count': anomaly_count,
            'latest_scan': latest_scan,
            'latest_git': latest_git,
            'archive_path': str(archive_path),
        })
        
        return context


class ArchiveAnalyzerView(LoginRequiredMixin, BaseUIView):
    """Archive size analyzer view with real-time scanning"""
    template_name = 'version_manager/analyzer.html'
    login_url = '/accounts/login/'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Calculate dynamic archive path
        # Path from: apps/web/backend/apps/version_manager/views.py
        # Need to go up 6 levels to reach unibos root
        base_dir = Path(__file__).parent.parent.parent.parent.parent.parent
        archive_path = base_dir / "archive" / "versions"

        # Get all archives ordered by version
        archives = VersionArchive.objects.all()

        # Calculate statistics if we have data
        if archives.exists():
            sizes = [a.size_bytes for a in archives]
            mean_size = statistics.mean(sizes)
            stdev_size = statistics.stdev(sizes) if len(sizes) > 1 else 0

            # Update Z-scores and anomalies
            for archive in archives:
                if stdev_size > 0:
                    archive.z_score = abs((archive.size_bytes - mean_size) / stdev_size)
                    # Use threshold of 2.5 to reduce false positives (99% confidence)
                    archive.is_anomaly = archive.z_score > 2.5
                else:
                    archive.z_score = 0
                    archive.is_anomaly = False

        context.update({
            'archives': archives,
            'archive_path': str(archive_path),
        })

        return context


@method_decorator(csrf_exempt, name='dispatch')
class StartScanView(LoginRequiredMixin, View):
    """Start archive scanning process"""
    
    def post(self, request):
        """Start a new scan session"""
        
        # Create new scan session
        scan_session = ScanSession.objects.create(
            started_by=request.user,
            status_message="Initializing scan..."
        )
        
        # Store session ID in cache for progress tracking
        cache.set(f'scan_session_{scan_session.id}', scan_session.id, 3600)
        
        # Start scanning in background thread
        import threading
        scan_thread = threading.Thread(target=self._perform_scan, args=(scan_session,))
        scan_thread.daemon = True
        scan_thread.start()
        
        return JsonResponse({
            'success': True,
            'session_id': scan_session.id,
            'message': 'Scan started successfully'
        })
    
    def _add_log(self, session_id, log_type, message):
        """Add a log entry to the cache for real-time display"""
        logs_key = f'scan_logs_{session_id}'
        logs = cache.get(logs_key, [])
        
        log_entry = {
            'index': len(logs),
            'type': log_type,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        logs.append(log_entry)
        
        # Keep only last 100 logs
        if len(logs) > 100:
            logs = logs[-100:]
        
        cache.set(logs_key, logs, 3600)
        return log_entry
    
    def _perform_scan(self, scan_session):
        """Perform the actual scanning with detailed logging"""
        # Use correct path to unibos project root
        import os
        # Path from: apps/web/backend/apps/version_manager/views.py
        # Need to go up 6 levels to reach unibos root
        base_dir = Path(__file__).parent.parent.parent.parent.parent.parent
        archive_path = base_dir / "archive" / "versions"
        session_id = scan_session.id
        
        try:
            # Clear previous logs
            cache.delete(f'scan_logs_{session_id}')
            cache.delete(f'scan_current_{session_id}')
            cache.delete(f'scan_anomaly_{session_id}')
            
            self._add_log(session_id, 'info', f'Starting scan of archive directory: {archive_path}')
            
            # Get all version directories
            self._add_log(session_id, 'info', 'Searching for version directories...')
            version_dirs = sorted(glob.glob(f"{archive_path}/unibos_v*"))
            total_dirs = len(version_dirs)
            
            self._add_log(session_id, 'success', f'Found {total_dirs} version directories')
            
            if total_dirs == 0:
                self._add_log(session_id, 'warning', 'No version archives found in the specified path')
                scan_session.status_message = "No version archives found"
                scan_session.is_complete = True
                scan_session.completed_at = timezone.now()
                scan_session.save()
                return
            
            scan_session.total_archives = total_dirs
            scan_session.save()
            
            archives_data = []
            total_size = 0
            
            for idx, version_dir in enumerate(version_dirs):
                if os.path.isdir(version_dir):
                    # Update progress
                    progress = int((idx + 1) / total_dirs * 100)
                    dirname = os.path.basename(version_dir)
                    
                    scan_session.progress_percent = progress
                    scan_session.current_archive = dirname
                    scan_session.status_message = f"Scanning {dirname}..."
                    scan_session.save()
                    
                    self._add_log(session_id, 'info', f'[{idx+1}/{total_dirs}] Scanning: {dirname}')
                    
                    # Extract version info
                    parts = dirname.split('_')
                    if len(parts) >= 2:
                        version_num = parts[1][1:] if parts[1].startswith('v') else parts[1]
                        
                        # Calculate directory size and file count
                        dir_size = 0
                        file_count = 0
                        dir_count = 0
                        
                        self._add_log(session_id, 'debug', f'  analyzing directory structure...')
                        
                        for dirpath, dirnames, filenames in os.walk(version_dir):
                            file_count += len(filenames)
                            dir_count += len(dirnames)
                            for filename in filenames:
                                filepath = os.path.join(dirpath, filename)
                                try:
                                    dir_size += os.path.getsize(filepath)
                                except:
                                    pass
                        
                        # Store current archive details in cache
                        cache.set(f'scan_current_{session_id}', {
                            'size': dir_size,
                            'files': file_count,
                            'dirs': dir_count
                        }, 60)
                        
                        self._add_log(session_id, 'success', 
                            f'  → Size: {dir_size / (1024*1024):.2f} MB | Files: {file_count} | Dirs: {dir_count}')
                        
                        # Store archive data
                        archive_data = {
                            'version': version_num,
                            'path': version_dir,
                            'size_bytes': dir_size,
                            'size_mb': dir_size / (1024 * 1024),
                            'file_count': file_count,
                            'directory_count': dir_count,
                        }
                        archives_data.append(archive_data)
                        total_size += dir_size
            
            # Calculate statistics for anomaly detection
            self._add_log(session_id, 'info', 'analyzing archive sizes for anomalies...')
            
            if len(archives_data) > 2:
                sizes = [a['size_bytes'] for a in archives_data]
                mean_size = statistics.mean(sizes)
                stdev_size = statistics.stdev(sizes) if len(sizes) > 1 else 0
                
                self._add_log(session_id, 'debug', 
                    f'Statistics: Mean={mean_size/(1024*1024):.2f}MB, StdDev={stdev_size/(1024*1024):.2f}MB')
                
                for archive in archives_data:
                    if stdev_size > 0:
                        z_score = abs((archive['size_bytes'] - mean_size) / stdev_size)
                        archive['z_score'] = z_score
                        # Use threshold of 2.5 to reduce false positives (99% confidence)
                        archive['is_anomaly'] = z_score > 2.5
                        
                        # Determine status based on size (like terminal version)
                        size_mb = archive['size_mb']
                        if size_mb < 50:
                            archive['status'] = 'normal'
                        elif size_mb < 200:
                            archive['status'] = 'large'
                        elif size_mb < 500:
                            archive['status'] = 'very_large'
                        else:
                            archive['status'] = 'huge'
                        
                        if archive['is_anomaly']:
                            self._add_log(session_id, 'warning', 
                                f'⚠️ Anomaly detected: v{archive["version"]} (Z-score: {z_score:.2f}, Size: {size_mb:.2f}MB)')
                            
                            # Store anomaly info in cache
                            cache.set(f'scan_anomaly_{session_id}', {
                                'archive': f'v{archive["version"]}',
                                'zscore': z_score,
                                'size_mb': size_mb
                            }, 60)
                    else:
                        archive['z_score'] = 0
                        archive['is_anomaly'] = False
                        archive['status'] = 'normal'
            
            # Save archives to database
            self._add_log(session_id, 'info', 'Saving archive data to database...')
            anomaly_count = 0
            
            with transaction.atomic():
                for archive_data in archives_data:
                    archive, created = VersionArchive.objects.update_or_create(
                        version=archive_data['version'],
                        defaults={
                            'path': archive_data['path'],
                            'size_bytes': archive_data['size_bytes'],
                            'size_mb': archive_data['size_mb'],
                            'file_count': archive_data['file_count'],
                            'directory_count': archive_data['directory_count'],
                            'z_score': archive_data.get('z_score', 0),
                            'is_anomaly': archive_data.get('is_anomaly', False),
                            'status': archive_data.get('status', 'normal'),
                        }
                    )
                    # Don't call update_status() since we're setting it directly
                    archive.save()
                    
                    if archive.is_anomaly:
                        anomaly_count += 1
                        self._add_log(session_id, 'info', 
                            f'  ✓ v{archive.version}: {archive.size_mb:.2f}MB - anomaly detected')
                    else:
                        # Log with color coding based on status
                        status_icon = '🟢' if archive.status == 'normal' else '🟡' if archive.status == 'large' else '🟠' if archive.status == 'very_large' else '🔴'
                        self._add_log(session_id, 'success', 
                            f'  {status_icon} v{archive.version}: {archive.size_mb:.2f}MB - {archive.status}')
            
            self._add_log(session_id, 'success', f'Database updated: {len(archives_data)} archives saved')
            
            # Update scan session
            scan_session.total_size_bytes = total_size
            scan_session.total_size_gb = total_size / (1024**3)
            scan_session.average_size_mb = (total_size / (1024**2)) / len(archives_data) if archives_data else 0
            scan_session.anomaly_count = anomaly_count
            scan_session.is_complete = True
            scan_session.completed_at = timezone.now()
            scan_session.status_message = f"Scan complete: {len(archives_data)} archives processed"
            scan_session.save()
            
        except Exception as e:
            scan_session.has_errors = True
            scan_session.error_message = str(e)
            scan_session.status_message = "Scan failed"
            scan_session.is_complete = True
            scan_session.completed_at = timezone.now()
            scan_session.save()


class ScanProgressView(LoginRequiredMixin, View):
    """Get scan progress for AJAX updates with detailed logs"""
    
    def get(self, request, session_id):
        """Get current scan progress with real-time logs"""
        try:
            scan_session = ScanSession.objects.get(id=session_id)
            
            # Get logs from cache
            logs_key = f'scan_logs_{session_id}'
            logs = cache.get(logs_key, [])
            
            # Get current archive details from cache
            current_details_key = f'scan_current_{session_id}'
            current_details = cache.get(current_details_key, {})
            
            # Get anomaly details from cache
            anomaly_key = f'scan_anomaly_{session_id}'
            anomaly_info = cache.get(anomaly_key, {})
            
            # Get archives found count
            archives_found = VersionArchive.objects.filter(
                last_scanned__gte=scan_session.started_at
            ).count() if scan_session.started_at else 0
            
            response_data = {
                'success': True,
                'progress': scan_session.progress_percent,
                'current_archive': scan_session.current_archive,
                'status_message': scan_session.status_message,
                'is_complete': scan_session.is_complete,
                'has_errors': scan_session.has_errors,
                'error_message': scan_session.error_message,
                'total_archives': scan_session.total_archives,
                'duration': scan_session.duration_formatted(),
                'archives_found': archives_found,
                'logs': logs,
            }
            
            # Add current archive details if available
            if current_details:
                response_data.update({
                    'current_size': current_details.get('size'),
                    'current_files': current_details.get('files'),
                    'current_dirs': current_details.get('dirs'),
                })
            
            # Add anomaly info if detected
            if anomaly_info:
                response_data.update({
                    'anomaly_detected': True,
                    'anomaly_archive': anomaly_info.get('archive'),
                    'anomaly_zscore': anomaly_info.get('zscore'),
                })
            
            # Add completion stats
            if scan_session.is_complete:
                response_data.update({
                    'total_size': scan_session.total_size_bytes,
                    'anomalies_count': scan_session.anomaly_count,
                })
            
            return JsonResponse(response_data)
            
        except ScanSession.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Session not found'
            })


class StopScanView(LoginRequiredMixin, View):
    """Stop a running scan"""
    
    def post(self, request, session_id):
        """Stop the scan session"""
        try:
            scan_session = ScanSession.objects.get(id=session_id)
            
            if not scan_session.is_complete:
                scan_session.is_complete = True
                scan_session.completed_at = timezone.now()
                scan_session.status_message = "Scan stopped by user"
                scan_session.save()
                
                # Add log entry
                logs_key = f'scan_logs_{session_id}'
                logs = cache.get(logs_key, [])
                logs.append({
                    'index': len(logs),
                    'type': 'warning',
                    'message': 'Scan stopped by user request',
                    'timestamp': datetime.now().isoformat()
                })
                cache.set(logs_key, logs, 3600)
            
            return JsonResponse({
                'success': True,
                'message': 'Scan stopped'
            })
            
        except ScanSession.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Session not found'
            })


class GitStatusView(LoginRequiredMixin, View):
    """Get current git status"""
    
    def get(self, request):
        """Fetch and return git status"""
        # Calculate repo path dynamically
        # Path from: apps/web/backend/apps/version_manager/views.py
        # Need to go up 6 levels to reach unibos root
        repo_path = str(Path(__file__).parent.parent.parent.parent.parent.parent)

        try:
            # Get branch name
            branch_result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                capture_output=True, text=True, cwd=repo_path
            )
            branch = branch_result.stdout.strip()
            
            # Get latest commit info
            commit_result = subprocess.run(
                ['git', 'log', '-1', '--format=%H|%s|%an'],
                capture_output=True, text=True, cwd=repo_path
            )
            commit_parts = commit_result.stdout.strip().split('|')
            commit_hash = commit_parts[0] if commit_parts else ''
            commit_message = commit_parts[1] if len(commit_parts) > 1 else ''
            author = commit_parts[2] if len(commit_parts) > 2 else ''
            
            # Get file status
            status_result = subprocess.run(
                ['git', 'status', '--porcelain'],
                capture_output=True, text=True, cwd=repo_path
            )
            
            modified_files = []
            untracked_files = []
            staged_files = []
            
            for line in status_result.stdout.strip().split('\n'):
                if line:
                    status = line[:2]
                    filename = line[3:]
                    
                    if status[0] in ['M', 'A', 'D', 'R']:
                        staged_files.append(filename)
                    if status[1] == 'M':
                        modified_files.append(filename)
                    if status == '??':
                        untracked_files.append(filename)
            
            has_changes = bool(modified_files or untracked_files or staged_files)
            
            # Save to database
            git_status = GitStatus.objects.create(
                branch=branch,
                commit_hash=commit_hash,
                commit_message=commit_message,
                author=author,
                modified_files=modified_files,
                untracked_files=untracked_files,
                staged_files=staged_files,
                has_changes=has_changes,
            )
            
            return JsonResponse({
                'success': True,
                'branch': branch,
                'commit': commit_hash[:8],
                'message': commit_message,
                'author': author,
                'has_changes': has_changes,
                'summary': git_status.get_status_summary(),
                'modified': len(modified_files),
                'untracked': len(untracked_files),
                'staged': len(staged_files),
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })


class RefreshArchivesView(LoginRequiredMixin, View):
    """Refresh archive list without full scan"""
    
    def post(self, request):
        """Quick refresh of archive list"""
        # If no archives exist, perform initial scan
        archives = VersionArchive.objects.all()
        
        if not archives.exists():
            # Trigger a scan instead
            scan_view = StartScanView()
            scan_view.request = request
            return scan_view.post(request)
        
        # Recalculate statistics
        if archives.exists():
            sizes = [a.size_bytes for a in archives]
            mean_size = statistics.mean(sizes)
            stdev_size = statistics.stdev(sizes) if len(sizes) > 1 else 0
            
            with transaction.atomic():
                for archive in archives:
                    if stdev_size > 0:
                        archive.z_score = abs((archive.size_bytes - mean_size) / stdev_size)
                        # Use threshold of 2.5 to reduce false positives (99% confidence)
                        archive.is_anomaly = archive.z_score > 2.5
                    else:
                        archive.z_score = 0
                        archive.is_anomaly = False
                    
                    # Update status based on size
                    archive.update_status()
                    archive.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Archives refreshed',
            'total': archives.count()
        })


class AnomalyDetectionView(LoginRequiredMixin, BaseUIView):
    """Anomaly detection dashboard for version archives"""
    template_name = 'version_manager/anomaly_detection.html'
    login_url = '/accounts/login/'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all anomalies
        anomalies = VersionArchive.objects.filter(is_anomaly=True).order_by('-z_score')
        
        # Get scan history
        scan_sessions = ScanSession.objects.all().order_by('-started_at')[:10]
        
        # Statistics
        total_archives = VersionArchive.objects.count()
        anomaly_count = anomalies.count()
        anomaly_percentage = (anomaly_count / total_archives * 100) if total_archives > 0 else 0
        
        # Get size distribution
        archives = VersionArchive.objects.all()
        if archives.exists():
            sizes = [a.size_bytes for a in archives]
            avg_size = statistics.mean(sizes)
            std_size = statistics.stdev(sizes) if len(sizes) > 1 else 0
            min_size = min(sizes)
            max_size = max(sizes)
        else:
            avg_size = std_size = min_size = max_size = 0
        
        # Group anomalies by type
        oversized = anomalies.filter(z_score__gt=0)
        undersized = anomalies.filter(z_score__lt=0)
        
        context.update({
            'anomalies': anomalies,
            'scan_sessions': scan_sessions,
            'total_archives': total_archives,
            'anomaly_count': anomaly_count,
            'anomaly_percentage': round(anomaly_percentage, 1),
            'oversized_count': oversized.count(),
            'undersized_count': undersized.count(),
            'avg_size_mb': avg_size / (1024*1024) if avg_size > 0 else 0,
            'std_size_mb': std_size / (1024*1024) if std_size > 0 else 0,
            'min_size_mb': min_size / (1024*1024) if min_size > 0 else 0,
            'max_size_mb': max_size / (1024*1024) if max_size > 0 else 0,
        })
        
        return context


class ScanHistoryView(LoginRequiredMixin, BaseUIView):
    """View scan history and details"""
    template_name = 'version_manager/scan_history.html'
    login_url = '/accounts/login/'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all scan sessions with pagination
        scan_list = ScanSession.objects.all().order_by('-started_at')
        paginator = Paginator(scan_list, 20)
        
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Calculate statistics
        total_scans = scan_list.count()
        successful_scans = scan_list.filter(status='completed').count()
        failed_scans = scan_list.filter(status='failed').count()
        
        # Average scan duration
        completed_scans = scan_list.filter(status='completed', completed_at__isnull=False)
        if completed_scans.exists():
            durations = []
            for scan in completed_scans:
                if scan.completed_at and scan.started_at:
                    duration = (scan.completed_at - scan.started_at).total_seconds()
                    durations.append(duration)
            avg_duration = statistics.mean(durations) if durations else 0
        else:
            avg_duration = 0
        
        context.update({
            'page_obj': page_obj,
            'total_scans': total_scans,
            'successful_scans': successful_scans,
            'failed_scans': failed_scans,
            'success_rate': (successful_scans / total_scans * 100) if total_scans > 0 else 0,
            'avg_duration': avg_duration,
        })
        
        return context


class ArchiveOperationsView(LoginRequiredMixin, BaseUIView):
    """Web-based archive operations"""
    template_name = 'version_manager/archive_operations.html'
    login_url = '/accounts/login/'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get archives with filters
        archives = VersionArchive.objects.all()
        
        # Apply filters
        filter_type = self.request.GET.get('filter', 'all')
        if filter_type == 'anomaly':
            archives = archives.filter(is_anomaly=True)
        elif filter_type == 'oversized':
            archives = archives.filter(z_score__gt=2)
        elif filter_type == 'undersized':
            archives = archives.filter(z_score__lt=-2)
        elif filter_type == 'normal':
            archives = archives.filter(is_anomaly=False)
        
        # Apply search
        search = self.request.GET.get('search')
        if search:
            archives = archives.filter(
                Q(version__icontains=search) |
                Q(build_date__icontains=search)
            )
        
        # Sort
        sort_by = self.request.GET.get('sort', '-build_date')
        archives = archives.order_by(sort_by)
        
        # Paginate
        paginator = Paginator(archives, 50)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Calculate total size of filtered archives
        total_size = sum(a.size_bytes for a in archives) / (1024**3)  # GB
        
        context.update({
            'page_obj': page_obj,
            'filter_type': filter_type,
            'search': search,
            'sort_by': sort_by,
            'total_filtered': archives.count(),
            'total_size_gb': round(total_size, 2),
        })
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle archive operations"""
        action = request.POST.get('action')
        archive_ids = request.POST.getlist('archive_ids')
        
        if action == 'delete' and archive_ids:
            # Delete selected archives
            archives = VersionArchive.objects.filter(id__in=archive_ids)
            deleted_count = archives.count()
            
            # Actually delete the files
            for archive in archives:
                archive_path = Path(archive.path)
                if archive_path.exists():
                    # Use rm -rf for directories
                    subprocess.run(['rm', '-rf', str(archive_path)], capture_output=True)
            
            # Delete from database
            archives.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'Deleted {deleted_count} archives'
            })
        
        elif action == 'analyze' and archive_ids:
            # Re-analyze selected archives
            archives = VersionArchive.objects.filter(id__in=archive_ids)
            
            # Recalculate z-scores
            all_archives = VersionArchive.objects.all()
            sizes = [a.size_bytes for a in all_archives]
            mean_size = statistics.mean(sizes)
            stdev_size = statistics.stdev(sizes) if len(sizes) > 1 else 0
            
            analyzed_count = 0
            for archive in archives:
                if stdev_size > 0:
                    archive.z_score = abs((archive.size_bytes - mean_size) / stdev_size)
                    # Use threshold of 2.5 to reduce false positives (99% confidence)
                    archive.is_anomaly = archive.z_score > 2.5
                    archive.save()
                    analyzed_count += 1
            
            return JsonResponse({
                'success': True,
                'message': f'Analyzed {analyzed_count} archives'
            })
        
        return JsonResponse({
            'success': False,
            'error': 'Invalid action or no archives selected'
        })
