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
    tools = [
        {'id': 'system_scrolls', 'name': 'system scrolls', 'icon': '📊'},
        {'id': 'web_forge', 'name': 'web forge', 'icon': '🌐'},
    ]
    
    # Add administration for admin users
    if request.user.is_authenticated:
        if request.user.is_superuser or request.user.username == 'berkhatirli':
            tools.append({'id': 'administration', 'name': 'administration', 'icon': '🔐'})
    
    # Dev tools
    dev_tools = [
        {'id': 'ai_builder', 'name': 'ai builder', 'icon': '🤖'},
        {'id': 'database_setup', 'name': 'database setup', 'icon': '🗄️'},
        {'id': 'web_forge_dev', 'name': 'web forge', 'icon': '🌐'},
        {'id': 'sd_card', 'name': 'sd card', 'icon': '💾'},
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
    Tries multiple paths: project root, backend, src
    """
    import json
    from pathlib import Path

    version_data = None

    try:
        # Path resolution: modules/web_ui/backend -> project root
        # modules/web_ui/backend -> modules -> project_root (4 levels up)
        project_root = Path(__file__).parent.parent.parent.parent

        # Try paths in priority order:
        version_paths = [
            project_root / 'VERSION.json',  # Project root (v533+)
            project_root / 'platform' / 'runtime' / 'web' / 'backend' / 'VERSION.json',  # Backend (v533+)
            project_root / 'platform' / 'runtime' / 'cli' / 'src' / 'VERSION.json',  # CLI src (v533+)
        ]

        for version_file in version_paths:
            if version_file.exists():
                with open(version_file, 'r') as f:
                    version_data = json.load(f)
                break

        # If still not found, use fallback
        if not version_data:
            version_data = {
                "version": "v533",
                "build_number": "unknown",
                "release_date": "2025-11-10"
            }
    except Exception as e:
        # Fallback version on any error
        version_data = {
            "version": "v533",
            "build_number": "unknown",
            "release_date": "2025-11-10"
        }

    return {
        'version': version_data.get('version', 'v533'),
        'build_number': version_data.get('build_number', 'unknown'),
        'release_date': version_data.get('release_date', '2025-11-10'),
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