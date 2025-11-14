"""
UNIBOS Production CLI - Logs Command
View UNIBOS logs
"""

import click
import subprocess
from pathlib import Path


@click.command(name='logs')
@click.option('--lines', '-n', default=50, help='Number of lines')
@click.option('--follow', '-f', is_flag=True, help='Follow log output')
def logs_command(lines, follow):
    """📋 View UNIBOS logs"""
    # Find git root
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

    log_file = root_dir / 'data' / 'core' / 'logs' / 'django' / 'debug.log'

    if not log_file.exists():
        click.echo(click.style(f'⚠️  Log file not found', fg='yellow'))
        click.echo(f'   Expected: {log_file}')
        return

    click.echo(click.style(f'📋 UNIBOS Logs', fg='cyan', bold=True))
    click.echo()

    try:
        if follow:
            subprocess.run(['tail', '-f', '-n', str(lines), str(log_file)])
        else:
            subprocess.run(['tail', '-n', str(lines), str(log_file)])
    except KeyboardInterrupt:
        click.echo()
