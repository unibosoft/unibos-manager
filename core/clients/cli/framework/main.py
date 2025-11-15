#!/usr/bin/env python3
"""
UNIBOS Production CLI - Main Entry Point
Simple, user-friendly CLI for UNIBOS users
"""

import click
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.clients.cli.framework.ui.splash import show_splash, show_header
from core.clients.cli.framework.commands.status import status_command
from core.clients.cli.framework.commands.start import start_command
from core.clients.cli.framework.commands.stop import stop_command
from core.clients.cli.framework.commands.logs import logs_command
from core.clients.cli.framework.commands.platform import platform_command
from core.clients.cli.framework.commands.node import node_group
from core.clients.cli.framework.commands.module import module_group
from core.version import __version__


@click.group()
@click.version_option(version=__version__, prog_name='unibos')
@click.option('--no-splash', is_flag=True, help='Skip splash screen')
@click.pass_context
def cli(ctx, no_splash):
    """🪐 UNIBOS - Your Personal Operating System

    Simple commands to manage your UNIBOS instance.

    Examples:
        unibos status          # Check system status
        unibos start           # Start UNIBOS services
        unibos logs            # View logs
        unibos logs -f         # Follow logs in real-time
    """
    ctx.ensure_object(dict)
    ctx.obj['no_splash'] = no_splash

    # Show splash only for main command
    if ctx.invoked_subcommand is None and not no_splash:
        show_splash()
        click.echo("💡 Run 'unibos --help' to see available commands")
    elif ctx.invoked_subcommand and not no_splash:
        show_header()


# Register commands
cli.add_command(status_command)
cli.add_command(start_command)
cli.add_command(stop_command)
cli.add_command(logs_command)
cli.add_command(platform_command)
cli.add_command(node_group)
cli.add_command(module_group)


def main():
    """Main entry point"""
    try:
        cli(obj={})
    except KeyboardInterrupt:
        click.echo("\n\n👋 Goodbye")
        sys.exit(130)
    except Exception as e:
        click.echo(f"\n❌ Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
