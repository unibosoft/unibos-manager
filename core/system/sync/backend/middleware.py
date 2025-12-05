"""
Data Export Control Middleware

Intercepts outgoing data requests and enforces export policies.
"""

import re
import json
import logging
from django.conf import settings
from django.http import JsonResponse

from .models import DataExportSettings, DataExportLog, ExportDestination, ExportStatus

logger = logging.getLogger(__name__)


class DataExportControlMiddleware:
    """
    Middleware to enforce data export controls.

    Checks all outgoing API responses against export settings
    and blocks or logs accordingly.
    """

    # Paths that are always allowed (no export control)
    EXEMPT_PATHS = [
        r'^/api/v1/auth/',           # Auth endpoints
        r'^/api/v1/sync/',           # Sync endpoints (handled separately)
        r'^/api/v1/nodes/',          # Node registry
        r'^/health/',                 # Health checks
        r'^/admin/',                  # Admin interface
        r'^/static/',                 # Static files
        r'^/media/',                  # Media files
    ]

    # Paths that are incoming data (not exports)
    INCOMING_PATHS = [
        r'^/api/v1/currencies/rates/',   # Exchange rate updates
        r'^/api/v1/birlikteyiz/alerts/', # Earthquake alerts
    ]

    # Module path mappings
    MODULE_PATH_MAP = {
        'currencies': r'^/api/v1/currencies/',
        'documents': r'^/api/v1/documents/|^/documents/',
        'wimm': r'^/api/v1/wimm/',
        'wims': r'^/api/v1/wims/',
        'cctv': r'^/api/v1/cctv/|^/cctv/',
        'birlikteyiz': r'^/api/v1/birlikteyiz/|^/birlikteyiz/',
        'movies': r'^/movies/',
        'music': r'^/music/',
        'restopos': r'^/restopos/',
        'personal_inflation': r'^/personal-inflation/',
        'recaria': r'^/recaria/',
    }

    def __init__(self, get_response):
        self.get_response = get_response
        self.exempt_patterns = [re.compile(p) for p in self.EXEMPT_PATHS]
        self.incoming_patterns = [re.compile(p) for p in self.INCOMING_PATHS]

    def __call__(self, request):
        # Get response first
        response = self.get_response(request)

        # Only check on successful responses with data
        if response.status_code not in [200, 201]:
            return response

        # Skip exempt paths
        if self._is_exempt(request.path):
            return response

        # Skip incoming data
        if self._is_incoming(request.path):
            return response

        # Only check GET and POST responses that return data
        if request.method not in ['GET', 'POST']:
            return response

        # Check if this is a data export
        if self._is_export_response(response):
            return self._check_export(request, response)

        return response

    def _is_exempt(self, path):
        """Check if path is exempt from export control"""
        return any(p.match(path) for p in self.exempt_patterns)

    def _is_incoming(self, path):
        """Check if path is for incoming data (not an export)"""
        return any(p.match(path) for p in self.incoming_patterns)

    def _is_export_response(self, response):
        """Check if response contains exportable data"""
        content_type = response.get('Content-Type', '')
        return 'application/json' in content_type

    def _get_module_from_path(self, path):
        """Extract module name from request path"""
        for module, pattern in self.MODULE_PATH_MAP.items():
            if re.match(pattern, path):
                return module
        return None

    def _get_data_type_from_path(self, path):
        """Extract data type from request path"""
        # Parse path to get resource type
        # e.g., /api/v1/currencies/portfolio/ -> portfolio
        parts = path.strip('/').split('/')
        if len(parts) >= 3:
            return parts[-1] if parts[-1] else parts[-2]
        return 'unknown'

    def _get_node_id(self, request):
        """Get current node ID from settings"""
        return getattr(settings, 'NODE_UUID', None)

    def _check_export(self, request, response):
        """Check if export is allowed and log it"""
        node_id = self._get_node_id(request)
        if not node_id:
            return response  # Can't check without node ID

        module = self._get_module_from_path(request.path)
        if not module:
            return response  # Unknown module, allow by default

        data_type = self._get_data_type_from_path(request.path)

        # Get export settings
        export_settings = DataExportSettings.get_for_node(node_id)

        # Check if export is allowed
        if not export_settings.can_export(module, data_type):
            # Block the export
            blocked_reason = self._get_blocked_reason(export_settings, module, data_type)

            # Log the blocked attempt
            if export_settings.log_blocked_exports:
                self._log_export(
                    request, response, node_id, module, data_type,
                    ExportStatus.BLOCKED, blocked_reason
                )

            logger.warning(
                f"Export blocked: {module}.{data_type} - {blocked_reason}",
                extra={'node_id': str(node_id), 'path': request.path}
            )

            return JsonResponse({
                'error': 'export_blocked',
                'message': f'Data export is blocked: {blocked_reason}',
                'module': module,
                'data_type': data_type,
            }, status=403)

        # Log allowed export
        if export_settings.log_all_exports:
            self._log_export(
                request, response, node_id, module, data_type,
                ExportStatus.ALLOWED
            )

        return response

    def _get_blocked_reason(self, settings, module, data_type):
        """Get human-readable reason for block"""
        if settings.master_kill_switch:
            return "Master kill switch is enabled"
        if module not in settings.module_settings:
            return f"Module '{module}' export not configured"
        return f"Export disabled for {module}.{data_type}"

    def _log_export(self, request, response, node_id, module, data_type, status, reason=''):
        """Log the export attempt"""
        try:
            # Calculate data size
            size_bytes = len(response.content) if hasattr(response, 'content') else 0

            # Try to count records
            record_count = 0
            if hasattr(response, 'content'):
                try:
                    data = json.loads(response.content)
                    if isinstance(data, list):
                        record_count = len(data)
                    elif isinstance(data, dict):
                        if 'results' in data:
                            record_count = len(data['results'])
                        elif 'count' in data:
                            record_count = data['count']
                        else:
                            record_count = 1
                except (json.JSONDecodeError, TypeError):
                    pass

            # Determine destination
            destination_type = ExportDestination.UNKNOWN
            destination_id = ''

            # Check for known patterns
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            if 'UNIBOS-Node' in user_agent:
                destination_type = ExportDestination.NODE
            elif 'UNIBOS-Hub' in user_agent:
                destination_type = ExportDestination.HUB
            elif request.path.startswith('/api/'):
                destination_type = ExportDestination.EXTERNAL_API

            # Get user info
            user_id = None
            if hasattr(request, 'user') and request.user.is_authenticated:
                user_id = getattr(request.user, 'id', None)

            DataExportLog.log_export(
                node_id=node_id,
                module=module,
                data_type=data_type,
                destination_type=destination_type,
                status=status,
                blocked_reason=reason,
                record_count=record_count,
                size_bytes=size_bytes,
                request_path=request.path,
                request_method=request.method,
                user_id=user_id,
                user_ip=self._get_client_ip(request),
                user_agent=user_agent[:500],
            )
        except Exception as e:
            logger.error(f"Failed to log export: {e}")

    def _get_client_ip(self, request):
        """Get client IP from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')


class ExportBlockedException(Exception):
    """Exception raised when an export is blocked"""
    def __init__(self, module, data_type, reason):
        self.module = module
        self.data_type = data_type
        self.reason = reason
        super().__init__(f"Export blocked for {module}.{data_type}: {reason}")
