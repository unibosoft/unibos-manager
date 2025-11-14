"""
UNIBOS Production CLI - Status Command
Simple system status check for end users
"""

import click
import subprocess
from pathlib import Path


@click.command(name='status')
def status_command():
    """📊 Show UNIBOS system status"""
    click.echo(click.style('📊 UNIBOS Status', fg='cyan', bold=True))
    click.echo()

    # Check if Django is running
    try:
        result = subprocess.run(
            ['pgrep', '-f', 'manage.py runserver'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            click.echo(f"  {click.style('✓', fg='green')} Django server running")
        else:
            click.echo(f"  {click.style('○', fg='yellow')} Django server stopped")
    except Exception:
        click.echo(f"  {click.style('?', fg='bright_black')} Django status unknown")

    # Check PostgreSQL
    try:
        result = subprocess.run(
            ['pg_isready'],
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0:
            click.echo(f"  {click.style('✓', fg='green')} PostgreSQL available")
        else:
            click.echo(f"  {click.style('✗', fg='red')} PostgreSQL unavailable")
    except Exception:
        click.echo(f"  {click.style('?', fg='bright_black')} PostgreSQL status unknown")

    # Check Redis
    try:
        result = subprocess.run(
            ['redis-cli', 'ping'],
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0 and 'PONG' in result.stdout:
            click.echo(f"  {click.style('✓', fg='green')} Redis available")
        else:
            click.echo(f"  {click.style('✗', fg='red')} Redis unavailable")
    except Exception:
        click.echo(f"  {click.style('?', fg='bright_black')} Redis status unknown")

    click.echo()
    click.echo(click.style('💡 Tip:', fg='yellow'))
    click.echo('  Run "unibos start" to start all services')
    click.echo('  Run "unibos logs" to view logs')
