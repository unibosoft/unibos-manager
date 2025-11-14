"""
UNIBOS Production CLI - Start Command
Start UNIBOS services
"""

import click
import subprocess
import sys
import os
from pathlib import Path


def get_django_path():
    """Get Django path using git root"""
    result = subprocess.run(
        ['git', 'rev-parse', '--show-toplevel'],
        capture_output=True,
        text=True,
        check=False
    )
    if result.returncode == 0:
        root_dir = Path(result.stdout.strip())
    else:
        root_dir = Path(__file__).parent.parent.parent.parent

    return root_dir / 'core' / 'web'


def get_django_python():
    """Get Django venv Python"""
    django_path = get_django_path()
    venv_python = django_path / 'venv' / 'bin' / 'python3'

    if venv_python.exists():
        return str(venv_python)
    return 'python3'


@click.command(name='start')
@click.option('--port', default=8000, help='Port for Django server')
def start_command(port):
    """🚀 Start UNIBOS services"""
    click.echo(click.style('🚀 Starting UNIBOS...', fg='cyan', bold=True))
    click.echo()

    django_path = get_django_path()

    # Set environment
    env = os.environ.copy()
    env['DJANGO_SETTINGS_MODULE'] = 'unibos_backend.settings.development'
    env['PYTHONPATH'] = f"{django_path}:{django_path.parent}"

    click.echo(f"  📡 Starting Django on port {port}...")

    try:
        subprocess.run(
            [get_django_python(), 'manage.py', 'runserver', f'0.0.0.0:{port}'],
            cwd=str(django_path),
            env=env
        )
    except KeyboardInterrupt:
        click.echo()
        click.echo(click.style('👋 Stopped', fg='yellow'))
        sys.exit(0)
