"""
UNIBOS CLI - Development Commands
Local development server, shell, tests, migrations
"""

import click
import subprocess
import sys
import os
from pathlib import Path


def get_django_path():
    """Get path to Django manage.py"""
    # Use git to find repository root (works from anywhere in the repo)
    import subprocess as sp
    result = sp.run(
        ['git', 'rev-parse', '--show-toplevel'],
        capture_output=True,
        text=True,
        check=False
    )
    if result.returncode == 0:
        root_dir = Path(result.stdout.strip())
    else:
        # Fallback to __file__ based path
        root_dir = Path(__file__).parent.parent.parent.parent

    return root_dir / 'core' / 'web'


def get_django_python():
    """Get Python executable from Django venv, fallback to system Python"""
    django_path = get_django_path()
    venv_python = django_path / 'venv' / 'bin' / 'python3'

    if venv_python.exists():
        return str(venv_python)

    # Fallback to system python3
    return 'python3'


@click.group(name='dev')
def dev_group():
    """💻 Development commands"""
    pass


@dev_group.command(name='run')
@click.option('--port', default=8000, help='Port to run on')
@click.option('--host', default='127.0.0.1', help='Host to bind to')
def dev_run(port, host):
    """Run Django development server"""
    click.echo(click.style(f'🔥 Starting development server on {host}:{port}...', fg='cyan', bold=True))

    django_path = get_django_path()

    if not (django_path / 'manage.py').exists():
        click.echo(click.style(f'❌ Error: manage.py not found in {django_path}', fg='red'))
        sys.exit(1)

    # Set environment
    env = os.environ.copy()
    env['DJANGO_SETTINGS_MODULE'] = 'unibos_backend.settings.development'
    env['PYTHONPATH'] = f"{django_path}:{django_path.parent}"

    try:
        subprocess.run(
            [get_django_python(), 'manage.py', 'runserver', f'{host}:{port}'],
            cwd=str(django_path),
            env=env
        )
    except KeyboardInterrupt:
        click.echo(click.style('\n👋 Server stopped', fg='yellow'))


@dev_group.command(name='shell')
def dev_shell():
    """Open Django shell"""
    click.echo(click.style('🐚 Opening Django shell...', fg='cyan'))

    django_path = get_django_path()

    env = os.environ.copy()
    env['DJANGO_SETTINGS_MODULE'] = 'unibos_backend.settings.development'
    env['PYTHONPATH'] = f"{django_path}:{django_path.parent}"

    try:
        subprocess.run(
            [get_django_python(), 'manage.py', 'shell'],
            cwd=str(django_path),
            env=env
        )
    except KeyboardInterrupt:
        click.echo()


@dev_group.command(name='test')
@click.argument('args', nargs=-1)
def dev_test(args):
    """Run tests"""
    click.echo(click.style('🧪 Running tests...', fg='cyan'))

    django_path = get_django_path()

    env = os.environ.copy()
    env['DJANGO_SETTINGS_MODULE'] = 'unibos_backend.settings.development'
    env['PYTHONPATH'] = f"{django_path}:{django_path.parent}"

    cmd = [get_django_python(), 'manage.py', 'test'] + list(args)

    result = subprocess.run(cmd, cwd=str(django_path), env=env)
    sys.exit(result.returncode)


@dev_group.command(name='migrate')
@click.option('--app', help='Specific app to migrate')
def dev_migrate(app):
    """Run database migrations"""
    click.echo(click.style('🔄 Running migrations...', fg='cyan'))

    django_path = get_django_path()

    env = os.environ.copy()
    env['DJANGO_SETTINGS_MODULE'] = 'unibos_backend.settings.development'
    env['PYTHONPATH'] = f"{django_path}:{django_path.parent}"

    cmd = [get_django_python(), 'manage.py', 'migrate']
    if app:
        cmd.append(app)

    result = subprocess.run(cmd, cwd=str(django_path), env=env)
    sys.exit(result.returncode)


@dev_group.command(name='makemigrations')
@click.option('--app', help='Specific app to create migrations for')
def dev_makemigrations(app):
    """Create new migrations"""
    click.echo(click.style('📝 Creating migrations...', fg='cyan'))

    django_path = get_django_path()

    env = os.environ.copy()
    env['DJANGO_SETTINGS_MODULE'] = 'unibos_backend.settings.development'
    env['PYTHONPATH'] = f"{django_path}:{django_path.parent}"

    cmd = [get_django_python(), 'manage.py', 'makemigrations']
    if app:
        cmd.append(app)

    result = subprocess.run(cmd, cwd=str(django_path), env=env)
    sys.exit(result.returncode)


@dev_group.command(name='logs')
@click.option('--lines', '-n', default=50, help='Number of lines to show')
@click.option('--follow', '-f', is_flag=True, help='Follow log output')
def dev_logs(lines, follow):
    """View development logs"""
    click.echo(click.style(f'📋 Showing last {lines} log lines...', fg='cyan'))

    root_dir = Path(__file__).parent.parent.parent.parent
    log_file = root_dir / 'data' / 'core' / 'logs' / 'django' / 'debug.log'

    if not log_file.exists():
        click.echo(click.style(f'⚠️  Log file not found: {log_file}', fg='yellow'))
        return

    try:
        if follow:
            subprocess.run(['tail', '-f', '-n', str(lines), str(log_file)])
        else:
            subprocess.run(['tail', '-n', str(lines), str(log_file)])
    except KeyboardInterrupt:
        click.echo()
