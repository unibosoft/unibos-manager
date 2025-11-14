"""
UNIBOS CLI - Status & Health Commands
System health checks and status information
"""

import click
import subprocess
import sys
from pathlib import Path


@click.command(name='status')
@click.option('--detailed', is_flag=True, help='Show detailed status')
def status_command(detailed):
    """📊 Show system status and health"""
    click.echo(click.style('📊 UNIBOS System Status', fg='cyan', bold=True))
    click.echo()

    root_dir = Path(__file__).parent.parent.parent.parent

    # Version info
    try:
        import json
        version_file = root_dir / 'VERSION.json'
        if version_file.exists():
            with open(version_file) as f:
                version_info = json.load(f)
                click.echo(f"Version: {click.style(version_info.get('version', 'unknown'), fg='yellow')}")
                if detailed:
                    click.echo(f"Build: {version_info.get('build', 'unknown')}")
                    click.echo(f"Date: {version_info.get('build_date', 'unknown')}")
    except Exception:
        click.echo("Version: unknown")

    click.echo()

    # Directory structure
    dirs_to_check = [
        ('Core', root_dir / 'core'),
        ('Modules', root_dir / 'modules'),
        ('Data', root_dir / 'data'),
        ('Deployment', root_dir / 'core' / 'deployment'),
    ]

    click.echo(click.style('📁 Directory Structure:', fg='cyan'))
    for name, path in dirs_to_check:
        status = '✓' if path.exists() else '✗'
        color = 'green' if path.exists() else 'red'
        click.echo(f"  {click.style(status, fg=color)} {name}: {path}")

    click.echo()

    # Django status
    django_path = root_dir / 'core' / 'web' / 'manage.py'
    if django_path.exists():
        click.echo(click.style('🌐 Django:', fg='cyan'))
        click.echo(f"  {click.style('✓', fg='green')} Django installed")

        if detailed:
            # Try to get Django version
            try:
                result = subprocess.run(
                    [sys.executable, str(django_path), '--version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    click.echo(f"  Version: {result.stdout.strip()}")
            except Exception:
                pass
    else:
        click.echo(f"  {click.style('✗', fg='red')} Django not found")

    click.echo()

    # Database
    click.echo(click.style('🗄️  Database:', fg='cyan'))
    data_db = root_dir / 'data_db'
    if data_db.exists():
        click.echo(f"  {click.style('✓', fg='green')} Database directory exists")
    else:
        click.echo(f"  {click.style('⚠', fg='yellow')} Database directory not found (may use PostgreSQL)")

    # Check for PostgreSQL
    try:
        result = subprocess.run(
            ['psql', '--version'],
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            click.echo(f"  {click.style('✓', fg='green')} PostgreSQL available: {version}")
    except Exception:
        pass

    if detailed:
        click.echo()
        click.echo(click.style('💡 Tip:', fg='yellow'))
        click.echo('  Run "unibos-dev deploy check" for deployment health check')
        click.echo('  Run "unibos-dev dev run" to start development server')
        click.echo('  Run "unibos-dev --help" for all available commands')
