#!/usr/bin/env python3
"""
UNIBOS Server CLI - Main Entry Point
Server management and monitoring for Rocksteady
"""

import click
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.cli_server.ui.splash import show_splash, show_header
from core.cli_server.commands.health import health_command
from core.cli_server.commands.stats import stats_command


@click.group()
@click.version_option(version='533+', prog_name='unibos-server')
@click.option('--no-splash', is_flag=True, help='Skip splash screen')
@click.pass_context
def cli(ctx, no_splash):
    """🖥️  UNIBOS Server - Server Management & Monitoring

    Production server management CLI for Rocksteady.

    Examples:
        unibos-server health       # Comprehensive health check
        unibos-server stats        # Performance statistics
        unibos-server logs django  # View Django logs
    """
    ctx.ensure_object(dict)
    ctx.obj['no_splash'] = no_splash

    if ctx.invoked_subcommand is None and not no_splash:
        show_splash()
        click.echo("💡 Run 'unibos-server --help' for available commands")
    elif ctx.invoked_subcommand and not no_splash:
        show_header()


# Register commands
cli.add_command(health_command)
cli.add_command(stats_command)


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
