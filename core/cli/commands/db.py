"""
UNIBOS CLI - Database Commands
Backup, restore, migrate database operations
"""

import click
import subprocess
import sys
from pathlib import Path


def get_django_python():
    """Get Python executable from Django venv, fallback to system Python"""
    # Use git to find repository root
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

    django_path = root_dir / 'core' / 'web'
    venv_python = django_path / 'venv' / 'bin' / 'python3'

    if venv_python.exists():
        return str(venv_python)

    # Fallback to system python3
    return 'python3'


@click.group(name='db')
def db_group():
    """🗄️  Database commands"""
    pass


@db_group.command(name='backup')
@click.option('--verify', is_flag=True, help='Verify backup after creation')
def db_backup(verify):
    """Create database backup"""
    click.echo(click.style('💾 Creating database backup...', fg='cyan', bold=True))

    root_dir = Path(__file__).parent.parent.parent.parent
    backup_script = root_dir / 'tools' / 'scripts' / 'backup_database.sh'

    if not backup_script.exists():
        click.echo(click.style(f'❌ Error: Backup script not found at {backup_script}', fg='red'))
        sys.exit(1)

    try:
        result = subprocess.run([str(backup_script)], cwd=str(root_dir))

        if result.returncode == 0 and verify:
            click.echo(click.style('🔍 Verifying backup...', fg='cyan'))
            verify_script = root_dir / 'tools' / 'scripts' / 'verify_database_backup.sh'
            if verify_script.exists():
                subprocess.run([str(verify_script)], cwd=str(root_dir))

        sys.exit(result.returncode)
    except Exception as e:
        click.echo(click.style(f'❌ Backup failed: {e}', fg='red'))
        sys.exit(1)


@db_group.command(name='restore')
@click.argument('backup_file', required=False)
def db_restore(backup_file):
    """Restore database from backup"""
    if not backup_file:
        click.echo(click.style('❌ Error: Backup file path required', fg='red'))
        click.echo('Usage: unibos db restore <backup_file>')
        sys.exit(1)

    backup_path = Path(backup_file)
    if not backup_path.exists():
        click.echo(click.style(f'❌ Error: Backup file not found: {backup_file}', fg='red'))
        sys.exit(1)

    click.echo(click.style(f'⚠️  Warning: This will restore database from {backup_file}', fg='yellow', bold=True))
    if not click.confirm('Are you sure you want to continue?'):
        click.echo('Restore cancelled')
        return

    click.echo(click.style('📥 Restoring database...', fg='cyan'))
    click.echo(click.style('⚠️  Database restore not yet fully implemented', fg='yellow'))
    # TODO: Implement restore logic


@db_group.command(name='migrate')
def db_migrate():
    """Run database migrations"""
    click.echo(click.style('🔄 Running migrations...', fg='cyan'))

    root_dir = Path(__file__).parent.parent.parent.parent
    django_path = root_dir / 'core' / 'web'

    import os
    env = os.environ.copy()
    env['DJANGO_SETTINGS_MODULE'] = 'unibos_backend.settings.development'
    env['PYTHONPATH'] = f"{django_path}:{root_dir}"

    result = subprocess.run(
        [get_django_python(), 'manage.py', 'migrate'],
        cwd=str(django_path),
        env=env
    )
    sys.exit(result.returncode)


@db_group.command(name='status')
def db_status():
    """Show database migration status"""
    click.echo(click.style('📊 Checking migration status...', fg='cyan'))

    root_dir = Path(__file__).parent.parent.parent.parent
    django_path = root_dir / 'core' / 'web'

    import os
    env = os.environ.copy()
    env['DJANGO_SETTINGS_MODULE'] = 'unibos_backend.settings.development'
    env['PYTHONPATH'] = f"{django_path}:{root_dir}"

    result = subprocess.run(
        [get_django_python(), 'manage.py', 'showmigrations'],
        cwd=str(django_path),
        env=env
    )
    sys.exit(result.returncode)
