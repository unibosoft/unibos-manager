"""
UNIBOS Context Processors
Provides global context variables for all templates
"""

def sidebar_context(request):
    """
    Provides sidebar data for all views
    Single source of truth for navigation
    """
    
    # Base modules - always visible (using CLI emojis)
    modules = [
        {'id': 'messenger', 'name': 'messenger', 'icon': '💬'},
        {'id': 'recaria', 'name': 'recaria', 'icon': '🪐'},
        {'id': 'birlikteyiz', 'name': 'birlikteyiz', 'icon': '📡'},
        {'id': 'kisisel_enflasyon', 'name': 'kişisel enflasyon', 'icon': '📈'},
        {'id': 'currencies', 'name': 'currencies', 'icon': '💰'},
        {'id': 'wimm', 'name': 'wimm', 'icon': '💸'},
        {'id': 'wims', 'name': 'wims', 'icon': '📦'},
        {'id': 'store', 'name': 'store', 'icon': '🛍️'},
        {'id': 'cctv', 'name': 'cctv', 'icon': '📹'},
        {'id': 'documents', 'name': 'documents', 'icon': '📄'},
        {'id': 'movies', 'name': 'movies', 'icon': '🎬'},
        {'id': 'music', 'name': 'music', 'icon': '🎵'},
        {'id': 'restopos', 'name': 'restopos', 'icon': '🍽️'},
    ]
    
    # Base tools - conditionally add administration (using CLI emojis)
    tools = []
    
    # Add administration for admin users
    if request.user.is_authenticated:
        if request.user.is_superuser or request.user.username == 'berkhatirli':
            tools.append({'id': 'administration', 'name': 'administration', 'icon': '🔐'})
    
    # Dev tools
    dev_tools = [
        {'id': 'database_setup', 'name': 'database setup', 'icon': '🗄️'},
        {'id': 'version_manager', 'name': 'version manager', 'icon': '📊', 'url': '/version-manager/'},
    ]
    
    # Create a list of dev tool IDs for template checks
    dev_tools_list = [tool['id'] for tool in dev_tools]
    
    return {
        'modules': modules,
        'tools': tools,
        'dev_tools': dev_tools,
        'dev_tools_list': dev_tools_list,
    }


def version_context(request):
    """
    Provides version information for all templates
    Supports both old and new VERSION.json formats
    """
    import json
    from pathlib import Path

    version_data = None

    try:
        # Path resolution: core/system/web_ui/backend -> project root (4 levels up)
        project_root = Path(__file__).parent.parent.parent.parent.parent

        # Try paths in priority order:
        version_paths = [
            project_root / 'VERSION.json',  # Project root
            project_root / 'core' / 'clients' / 'web' / 'VERSION.json',  # Web client specific
        ]

        for version_file in version_paths:
            if version_file.exists():
                with open(version_file, 'r', encoding='utf-8') as f:
                    version_data = json.load(f)
                break

    except Exception:
        pass

    # Parse version data - support both old and new formats
    if version_data:
        version_field = version_data.get('version')

        # New format: version is a dict with major/minor/patch/build
        if isinstance(version_field, dict):
            major = version_field.get('major', 0)
            minor = version_field.get('minor', 0)
            patch = version_field.get('patch', 0)
            version = f"v{major}.{minor}.{patch}"

            # Get build from version dict or build_info
            build = version_field.get('build', '')
            if not build and 'build_info' in version_data:
                build = version_data['build_info'].get('timestamp', '')

            # Format build as YYYYMMDD_HHMM for display
            if build and len(build) == 14:
                build = f"{build[:8]}_{build[8:12]}"

            # Get release date
            release_date = version_data.get('build_info', {}).get('date', '')
            if not release_date:
                release_date = version_data.get('release_info', {}).get('release_date', '2025-12-01')

        # Old format: version is a string
        else:
            version = version_field if version_field else 'v0.534.0'
            build = version_data.get('build') or version_data.get('build_number', '20251116_0550')
            release_date = version_data.get('release_date', '2025-11-16')
    else:
        # Fallback
        version = 'v1.0.0'
        build = '20251201_2225'
        release_date = '2025-12-01'

    return {
        'version': version,
        'build_number': build,
        'release_date': release_date,
    }


def unibos_context(request):
    """
    General UNIBOS context data
    """
    from datetime import datetime
    import sys
    from pathlib import Path
    
    # Add src directory to path to import system_info
    src_path = Path(__file__).parent.parent.parent.parent / 'src'
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    # Import system info
    try:
        from system_info import system_info
        hostname = system_info.hostname
        environment = system_info.environment
        display_name = system_info.display_name
    except ImportError:
        import socket
        hostname = socket.gethostname()
        environment = 'unknown'
        display_name = hostname
    
    # Check online status
    def check_online_status():
        try:
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except:
            return False
    
    return {
        'current_time': datetime.now().strftime('%H:%M:%S'),
        'current_date': datetime.now().strftime('%Y-%m-%d'),
        'location': 'bitez, bodrum',
        'online_status': check_online_status(),
        'user': request.user if request.user.is_authenticated else None,
        'hostname': hostname,
        'environment': environment,
        'display_name': display_name,
        'footer_nav': '↑↓ navigate | enter/→ select | esc/← back | tab switch | L language | M minimize | q quit',
    }