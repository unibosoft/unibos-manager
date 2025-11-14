#!/usr/bin/env python3
"""
UNIBOS CLI - Main Entry Point
Universal Integrated Backend and Operating System
"""

import click
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.cli_dev.ui.splash import show_splash_screen, show_compact_header
from core.cli_dev.commands.deploy import deploy_group
from core.cli_dev.commands.dev import dev_group
from core.cli_dev.commands.db import db_group
from core.cli_dev.commands.status import status_command
from core.cli_dev.commands.git import git_group


@click.group()
@click.version_option(version='533+', prog_name='unibos-dev')
@click.option('--no-splash', is_flag=True, help='Skip splash screen')
@click.pass_context
def cli(ctx, no_splash):
    """🔧 UNIBOS Developer CLI - Development & Deployment Tools

    Developer-focused CLI for UNIBOS development, git workflows,
    versioning, and deployment operations.

    Examples:
        unibos-dev status              # Show system status
        unibos-dev dev run             # Start development server
        unibos-dev deploy rocksteady   # Deploy to production
        unibos-dev db backup           # Create database backup
        unibos-dev git push-dev        # Push to dev repository
        unibos-dev git sync-prod       # Sync to local prod directory
    """
    # Store context for subcommands
    ctx.ensure_object(dict)
    ctx.obj['no_splash'] = no_splash

    # Show splash only for main command (no subcommand)
    if ctx.invoked_subcommand is None and not no_splash:
        show_splash_screen(quick=False)
        click.echo()
        click.echo("💡 Run 'unibos-dev --help' to see available commands")
    elif ctx.invoked_subcommand and not no_splash:
        # Show compact header for subcommands
        show_compact_header()


# Register command groups
cli.add_command(deploy_group)
cli.add_command(dev_group)
cli.add_command(db_group)
cli.add_command(status_command)
cli.add_command(git_group)


def main():
    """Main entry point for the CLI"""
    try:
        cli(obj={})
    except KeyboardInterrupt:
        click.echo("\n\n👋 Interrupted by user")
        sys.exit(130)
    except Exception as e:
        click.echo(f"\n❌ Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
