"""
Sync API Views

Handles sync operations between Nodes and Hub.
"""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from django.db import transaction
from django.db.models import Count, Q

from .models import (
    SyncSession, SyncRecord, SyncConflict,
    OfflineOperation, VersionVector,
    SyncStatus as SyncStatusEnum, ConflictStrategy,
    DataExportSettings, DataExportLog, ExportStatus, ExportDestination
)
from .serializers import (
    SyncInitRequestSerializer, SyncInitResponseSerializer,
    SyncPullRequestSerializer, SyncPullResponseSerializer,
    SyncPushRequestSerializer, SyncPushResponseSerializer,
    SyncConflictSerializer, ConflictResolveRequestSerializer,
    SyncSessionSerializer, OfflineOperationSerializer,
    SyncStatusSerializer, VersionVectorSerializer,
    DataExportSettingsSerializer, ExportSettingsUpdateSerializer,
    ModulePermissionSerializer, KillSwitchSerializer,
    DataExportLogSerializer, ExportStatsSerializer,
    ExportCheckRequestSerializer, ExportCheckResponseSerializer
)


class SyncInitView(APIView):
    """
    Initialize a sync session between Node and Hub.

    POST /api/v1/sync/init/
    """
    permission_classes = [AllowAny]  # Nodes authenticate via token

    def post(self, request):
        serializer = SyncInitRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        node_id = data['node_id']
        node_hostname = data['node_hostname']
        modules = data.get('modules', [])
        node_version_vector = data.get('version_vector', {})

        # Get Hub's version vectors for requested modules
        hub_version_vector = {}
        changes_available = 0

        for model_name in node_version_vector.keys():
            hub_vv = VersionVector.objects.filter(
                node_id=node_id,  # Hub tracks versions per node
                model_name=model_name
            ).first()

            if hub_vv:
                hub_version_vector[model_name] = hub_vv.version
                # Calculate changes: hub version - node's last synced version
                node_version = node_version_vector.get(model_name, 0)
                if hub_vv.version > node_version:
                    changes_available += hub_vv.version - node_version
            else:
                hub_version_vector[model_name] = 0

        # Check for existing conflicts
        conflicts_detected = SyncConflict.objects.filter(
            local_node_id=node_id,
            resolved=False
        ).count()

        # Create sync session
        session = SyncSession.objects.create(
            node_id=node_id,
            node_hostname=node_hostname,
            direction=data.get('direction', 'bidirectional'),
            modules=modules,
            node_version_vector=node_version_vector,
            hub_version_vector=hub_version_vector,
            total_records=changes_available,
            conflicts_count=conflicts_detected
        )

        response_data = {
            'session_id': session.id,
            'hub_version_vector': hub_version_vector,
            'changes_available': changes_available,
            'conflicts_detected': conflicts_detected,
            'modules': modules
        }

        return Response(
            SyncInitResponseSerializer(response_data).data,
            status=status.HTTP_200_OK
        )


class SyncPullView(APIView):
    """
    Pull changes from Hub to Node.

    POST /api/v1/sync/pull/
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SyncPullRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        session_id = data['session_id']
        batch_size = data.get('batch_size', 100)
        offset = data.get('offset', 0)
        models_filter = data.get('models', [])

        # Get session
        try:
            session = SyncSession.objects.get(id=session_id)
        except SyncSession.DoesNotExist:
            return Response(
                {'error': 'Session not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Mark session as in progress
        if session.status == SyncStatusEnum.PENDING:
            session.start()

        # Get pending records for this session
        records_query = SyncRecord.objects.filter(
            session=session,
            status=SyncStatusEnum.PENDING
        )

        if models_filter:
            records_query = records_query.filter(model_name__in=models_filter)

        total_count = records_query.count()
        records = records_query[offset:offset + batch_size]

        has_more = (offset + batch_size) < total_count
        next_offset = offset + batch_size if has_more else offset

        response_data = {
            'records': SyncRecordSerializer(records, many=True).data,
            'total_count': total_count,
            'has_more': has_more,
            'next_offset': next_offset
        }

        return Response(response_data, status=status.HTTP_200_OK)


class SyncPushView(APIView):
    """
    Push changes from Node to Hub.

    POST /api/v1/sync/push/
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SyncPushRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        session_id = data['session_id']
        records = data['records']

        # Get session
        try:
            session = SyncSession.objects.get(id=session_id)
        except SyncSession.DoesNotExist:
            return Response(
                {'error': 'Session not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Mark session as in progress
        if session.status == SyncStatusEnum.PENDING:
            session.start()

        accepted = 0
        rejected = 0
        conflicts = 0
        errors = []

        with transaction.atomic():
            for record_data in records:
                try:
                    result = self._process_record(session, record_data)
                    if result == 'accepted':
                        accepted += 1
                    elif result == 'conflict':
                        conflicts += 1
                    else:
                        rejected += 1
                        errors.append({
                            'record_id': record_data.get('record_id'),
                            'error': result
                        })
                except Exception as e:
                    rejected += 1
                    errors.append({
                        'record_id': record_data.get('record_id'),
                        'error': str(e)
                    })

        # Update session progress
        session.processed_records += accepted
        session.conflicts_count += conflicts
        session.save(update_fields=['processed_records', 'conflicts_count'])

        response_data = {
            'accepted': accepted,
            'rejected': rejected,
            'conflicts': conflicts,
            'errors': errors
        }

        return Response(response_data, status=status.HTTP_200_OK)

    def _process_record(self, session, record_data):
        """Process a single sync record"""
        model_name = record_data.get('model_name')
        record_id = record_data.get('record_id')
        operation = record_data.get('operation')
        data = record_data.get('data', {})
        local_version = record_data.get('local_version', 0)
        local_modified_at = record_data.get('local_modified_at')

        # Check for conflicts - is there a newer version on Hub?
        existing_record = SyncRecord.objects.filter(
            session=session,
            model_name=model_name,
            record_id=record_id
        ).first()

        if existing_record and existing_record.remote_version > local_version:
            # Conflict detected
            SyncConflict.objects.create(
                session=session,
                model_name=model_name,
                record_id=record_id,
                local_data=data,
                remote_data=existing_record.data,
                local_modified_at=local_modified_at or timezone.now(),
                remote_modified_at=existing_record.remote_modified_at or timezone.now(),
                local_node_id=session.node_id,
                remote_source='hub',
                strategy=ConflictStrategy.MANUAL
            )
            return 'conflict'

        # Create or update sync record
        sync_record, created = SyncRecord.objects.update_or_create(
            session=session,
            model_name=model_name,
            record_id=record_id,
            defaults={
                'operation': operation,
                'data': data,
                'local_version': local_version,
                'local_modified_at': local_modified_at or timezone.now(),
                'status': SyncStatusEnum.COMPLETED,
                'synced_at': timezone.now()
            }
        )

        # Update version vector
        vv = VersionVector.get_or_create_for_model(session.node_id, model_name)
        vv.version = max(vv.version, local_version)
        vv.last_synced = timezone.now()
        vv.save()

        return 'accepted'


class SyncCompleteView(APIView):
    """
    Mark a sync session as complete.

    POST /api/v1/sync/complete/
    """
    permission_classes = [AllowAny]

    def post(self, request):
        session_id = request.data.get('session_id')

        try:
            session = SyncSession.objects.get(id=session_id)
        except SyncSession.DoesNotExist:
            return Response(
                {'error': 'Session not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check for unresolved conflicts
        if session.conflicts_count > 0:
            unresolved = SyncConflict.objects.filter(
                session=session,
                resolved=False
            ).count()
            if unresolved > 0:
                session.status = SyncStatusEnum.CONFLICT
                session.save(update_fields=['status'])
                return Response({
                    'status': 'conflict',
                    'unresolved_conflicts': unresolved,
                    'message': f'{unresolved} conflicts need resolution'
                })

        session.complete()

        return Response({
            'status': 'completed',
            'session_id': session.id,
            'processed_records': session.processed_records,
            'completed_at': session.completed_at
        })


class SyncConflictViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing sync conflicts.
    """
    serializer_class = SyncConflictSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = SyncConflict.objects.all()

        # Filter by node
        node_id = self.request.query_params.get('node_id')
        if node_id:
            queryset = queryset.filter(local_node_id=node_id)

        # Filter by resolved status
        resolved = self.request.query_params.get('resolved')
        if resolved is not None:
            queryset = queryset.filter(resolved=resolved.lower() == 'true')

        return queryset

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Resolve a conflict"""
        conflict = self.get_object()

        serializer = ConflictResolveRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        strategy = data['strategy']
        resolution_data = data.get('resolution_data')

        # Apply resolution strategy
        if strategy == ConflictStrategy.NEWER_WINS:
            if conflict.local_modified_at > conflict.remote_modified_at:
                resolution_data = conflict.local_data
            else:
                resolution_data = conflict.remote_data
        elif strategy == ConflictStrategy.HUB_WINS:
            resolution_data = conflict.remote_data
        elif strategy == ConflictStrategy.NODE_WINS:
            resolution_data = conflict.local_data
        elif strategy == ConflictStrategy.KEEP_BOTH:
            # Don't resolve - mark for manual handling
            pass

        # Get user ID if authenticated
        user_id = None
        if request.user and request.user.is_authenticated:
            user_id = getattr(request.user, 'id', None)

        conflict.resolve(strategy, resolution_data, user_id)

        return Response(SyncConflictSerializer(conflict).data)


class SyncStatusView(APIView):
    """
    Get overall sync status for a node.

    GET /api/v1/sync/status/?node_id=<uuid>
    """
    permission_classes = [AllowAny]

    def get(self, request):
        node_id = request.query_params.get('node_id')
        if not node_id:
            return Response(
                {'error': 'node_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get version vectors
        version_vectors = VersionVector.objects.filter(node_id=node_id)

        # Calculate pending changes
        pending_push = sum(vv.pending_changes for vv in version_vectors)

        # Get last sync time
        last_sync = None
        last_session = SyncSession.objects.filter(
            node_id=node_id,
            status=SyncStatusEnum.COMPLETED
        ).order_by('-completed_at').first()
        if last_session:
            last_sync = last_session.completed_at

        # Count unresolved conflicts
        unresolved_conflicts = SyncConflict.objects.filter(
            local_node_id=node_id,
            resolved=False
        ).count()

        # Count pending offline operations
        offline_operations = OfflineOperation.objects.filter(
            node_id=node_id,
            status=SyncStatusEnum.PENDING
        ).count()

        # Check if fully synced
        is_synced = (
            pending_push == 0 and
            unresolved_conflicts == 0 and
            offline_operations == 0
        )

        response_data = {
            'node_id': node_id,
            'is_synced': is_synced,
            'last_sync': last_sync,
            'pending_push': pending_push,
            'pending_pull': 0,  # Calculated on demand
            'unresolved_conflicts': unresolved_conflicts,
            'offline_operations': offline_operations,
            'version_vectors': VersionVectorSerializer(version_vectors, many=True).data
        }

        return Response(response_data)


class OfflineOperationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing offline operations.
    """
    serializer_class = OfflineOperationSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = OfflineOperation.objects.all()

        # Filter by node
        node_id = self.request.query_params.get('node_id')
        if node_id:
            queryset = queryset.filter(node_id=node_id)

        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset

    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending operations ready to execute"""
        node_id = request.query_params.get('node_id')
        limit = int(request.query_params.get('limit', 100))

        operations = OfflineOperation.get_pending(node_id=node_id, limit=limit)
        return Response(OfflineOperationSerializer(operations, many=True).data)

    @action(detail=True, methods=['post'])
    def retry(self, request, pk=None):
        """Manually retry an operation"""
        operation = self.get_object()

        if operation.status == SyncStatusEnum.COMPLETED:
            return Response(
                {'error': 'Operation already completed'},
                status=status.HTTP_400_BAD_REQUEST
            )

        operation.status = SyncStatusEnum.PENDING
        operation.scheduled_for = timezone.now()
        operation.save(update_fields=['status', 'scheduled_for'])

        return Response(OfflineOperationSerializer(operation).data)

    @action(detail=False, methods=['post'])
    def cleanup(self, request):
        """Clean up old completed operations"""
        days = int(request.data.get('days', 7))
        deleted_count, _ = OfflineOperation.cleanup_completed(days=days)

        return Response({
            'deleted': deleted_count,
            'message': f'Deleted {deleted_count} completed operations older than {days} days'
        })


# =============================================================================
# DATA EXPORT CONTROL VIEWS
# =============================================================================

class ExportSettingsView(APIView):
    """
    Get or update export settings for a node.

    GET /api/v1/sync/export/settings/?node_id=<uuid>
    PUT /api/v1/sync/export/settings/
    """
    permission_classes = [AllowAny]

    def get(self, request):
        node_id = request.query_params.get('node_id')
        if not node_id:
            return Response(
                {'error': 'node_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        settings_obj = DataExportSettings.get_for_node(node_id)
        return Response(DataExportSettingsSerializer(settings_obj).data)

    def put(self, request):
        node_id = request.data.get('node_id')
        if not node_id:
            return Response(
                {'error': 'node_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ExportSettingsUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        settings_obj = DataExportSettings.get_for_node(node_id)

        # Update fields
        for field, value in serializer.validated_data.items():
            if value is not None:
                setattr(settings_obj, field, value)
        settings_obj.save()

        return Response(DataExportSettingsSerializer(settings_obj).data)


class KillSwitchView(APIView):
    """
    Toggle master kill switch.

    POST /api/v1/sync/export/kill-switch/
    """
    permission_classes = [AllowAny]

    def post(self, request):
        node_id = request.data.get('node_id')
        if not node_id:
            return Response(
                {'error': 'node_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = KillSwitchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        settings_obj = DataExportSettings.get_for_node(node_id)

        if serializer.validated_data['enabled']:
            settings_obj.enable_kill_switch()
            action = 'enabled'
        else:
            settings_obj.disable_kill_switch()
            action = 'disabled'

        return Response({
            'success': True,
            'kill_switch': settings_obj.master_kill_switch,
            'message': f'Kill switch {action}'
        })


class ModulePermissionView(APIView):
    """
    Set export permission for a module.

    POST /api/v1/sync/export/module-permission/
    """
    permission_classes = [AllowAny]

    def post(self, request):
        node_id = request.data.get('node_id')
        if not node_id:
            return Response(
                {'error': 'node_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ModulePermissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        settings_obj = DataExportSettings.get_for_node(node_id)
        settings_obj.set_module_permission(
            module=data['module'],
            data_type=data.get('data_type'),
            allowed=data['allowed']
        )

        return Response({
            'success': True,
            'module': data['module'],
            'data_type': data.get('data_type'),
            'allowed': data['allowed'],
            'module_settings': settings_obj.module_settings
        })


class ExportCheckView(APIView):
    """
    Check if export is allowed for a module/data_type.

    POST /api/v1/sync/export/check/
    """
    permission_classes = [AllowAny]

    def post(self, request):
        node_id = request.data.get('node_id')
        if not node_id:
            return Response(
                {'error': 'node_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ExportCheckRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        settings_obj = DataExportSettings.get_for_node(node_id)
        module = data['module']
        data_type = data.get('data_type')

        allowed = settings_obj.can_export(module, data_type)

        reason = ''
        if not allowed:
            if settings_obj.master_kill_switch:
                reason = 'Master kill switch is enabled'
            else:
                reason = f'Export disabled for {module}'
                if data_type:
                    reason += f'.{data_type}'

        return Response({
            'allowed': allowed,
            'reason': reason,
            'kill_switch_active': settings_obj.master_kill_switch,
            'module_allowed': settings_obj.can_export(module) if not settings_obj.master_kill_switch else False
        })


class ExportLogsView(APIView):
    """
    Get export logs for a node.

    GET /api/v1/sync/export/logs/?node_id=<uuid>&status=<status>&days=<days>
    """
    permission_classes = [AllowAny]

    def get(self, request):
        node_id = request.query_params.get('node_id')
        if not node_id:
            return Response(
                {'error': 'node_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        days = int(request.query_params.get('days', 7))
        status_filter = request.query_params.get('status')
        module_filter = request.query_params.get('module')
        limit = int(request.query_params.get('limit', 100))

        from datetime import timedelta
        cutoff = timezone.now() - timedelta(days=days)

        logs = DataExportLog.objects.filter(
            node_id=node_id,
            timestamp__gte=cutoff
        )

        if status_filter:
            logs = logs.filter(status=status_filter)
        if module_filter:
            logs = logs.filter(module=module_filter)

        logs = logs[:limit]

        return Response({
            'logs': DataExportLogSerializer(logs, many=True).data,
            'count': logs.count()
        })


class ExportStatsView(APIView):
    """
    Get export statistics for a node.

    GET /api/v1/sync/export/stats/?node_id=<uuid>&days=<days>
    """
    permission_classes = [AllowAny]

    def get(self, request):
        node_id = request.query_params.get('node_id')
        if not node_id:
            return Response(
                {'error': 'node_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        days = int(request.query_params.get('days', 7))
        stats = DataExportLog.get_stats(node_id, days=days)

        return Response(stats)
