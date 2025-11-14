"""
UNIBOS Server CLI - Splash Screen
"""

import click


def show_splash():
    """Show server CLI splash"""
    click.echo(click.style('\n🖥️  UNIBOS Server', fg='magenta', bold=True))
    click.echo(click.style('   Server Management & Monitoring\n', fg='bright_black'))


def show_header():
    """Show compact header"""
    click.echo(click.style('🖥️  unibos-server', fg='magenta') + click.style(' v533+', fg='bright_black'))
