"""
UNIBOS Production CLI - Simplified Splash Screen
"""

import click


def show_splash():
    """Show simplified UNIBOS splash"""
    click.echo(click.style('\n🪐 UNIBOS', fg='cyan', bold=True))
    click.echo(click.style('   Universal Integrated Backend and Operating System\n', fg='bright_black'))


def show_header():
    """Show compact header for commands"""
    click.echo(click.style('🪐 unibos', fg='cyan') + click.style(' v533+', fg='bright_black'))
