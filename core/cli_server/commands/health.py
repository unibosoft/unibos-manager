"""
UNIBOS Server CLI - Health Command
Comprehensive health checks for server
"""

import click
import subprocess


@click.command(name='health')
def health_command():
    """🏥 Comprehensive server health check"""
    click.echo(click.style('🏥 Server Health Check', fg='magenta', bold=True))
    click.echo()

    checks = {
        'Django': ['pgrep', '-f', 'manage.py'],
        'Gunicorn': ['pgrep', '-f', 'gunicorn'],
        'Celery Worker': ['pgrep', '-f', 'celery worker'],
        'Celery Beat': ['pgrep', '-f', 'celery beat'],
        'PostgreSQL': ['pg_isready'],
        'Redis': ['redis-cli', 'ping'],
        'Nginx': ['pgrep', '-f', 'nginx'],
    }

    for service, command in checks.items():
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                click.echo(f"  {click.style('✓', fg='green')} {service}")
            else:
                click.echo(f"  {click.style('✗', fg='red')} {service}")
        except Exception:
            click.echo(f"  {click.style('?', fg='yellow')} {service} (check failed)")

    click.echo()
    click.echo(click.style('💡 Tip:', fg='yellow'))
    click.echo('  Run "unibos-server stats" for performance metrics')
    click.echo('  Run "unibos-server logs" to view logs')
