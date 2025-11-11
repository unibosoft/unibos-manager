"""
WSGI config for UNIBOS Backend project.
"""

import sys
import os
from pathlib import Path
from django.core.wsgi import get_wsgi_application

# Add UNIBOS root directory to Python path so modules/ can be imported
# This file is in: platform/runtime/web/backend/unibos_backend/wsgi.py
# Path: wsgi.py → unibos_backend/ → backend/ → web/ → runtime/ → core/ → (UNIBOS root)
# UNIBOS root is 6 levels up
_unibos_root = Path(__file__).resolve().parent.parent.parent.parent.parent.parent
if str(_unibos_root) not in sys.path:
    sys.path.insert(0, str(_unibos_root))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unibos_backend.settings.production')

application = get_wsgi_application()