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
    First tries backend/VERSION.json, then src/VERSION.json
    """
    import json
    from pathlib import Path
    
    version_data = None
    
    try:
        # First try backend VERSION.json (same directory as manage.py)
        backend_path = Path(__file__).parent.parent.parent
        backend_version_file = backend_path / 'VERSION.json'
        
        if backend_version_file.exists():
            with open(backend_version_file, 'r') as f:
                version_data = json.load(f)
        
        # If not found, try src/VERSION.json
        if not version_data:
            src_path = backend_path.parent / 'src'
            src_version_file = src_path / 'VERSION.json'
            
            if src_version_file.exists():
                with open(src_version_file, 'r') as f:
                    version_data = json.load(f)
        
        # If still not found, use fallback
        if not version_data:
            version_data = {
                "version": "v517",
                "build_number": "20250826_1733",
                "release_date": "2025-08-26"
            }
    except Exception as e:
        # Fallback version on any error
        version_data = {
            "version": "v517",
            "build_number": "20250826_1733",
            "release_date": "2025-08-26"
        }
    
    return {
        'version': version_data.get('version', 'v517'),
        'build_number': version_data.get('build_number', '20250826_1733'),
        'release_date': version_data.get('release_date', '2025-08-26'),
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