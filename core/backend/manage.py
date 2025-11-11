#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path


def main():
    """Run administrative tasks."""
    # Add UNIBOS root directory to Python path so modules/ can be imported
    # manage.py is in: core/backend/
    # UNIBOS root is 2 levels up
    unibos_root = Path(__file__).resolve().parent.parent
    if str(unibos_root) not in sys.path:
        sys.path.insert(0, str(unibos_root))

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unibos_backend.settings.development')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()