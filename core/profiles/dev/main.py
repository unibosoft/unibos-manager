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

from core.profiles.dev.ui.splash import show_splash_screen, show_compact_header
from core.profiles.dev.commands.deploy import deploy_group
from core.profiles.dev.commands.dev import dev_group
from core.profiles.dev.commands.db import db_group
from core.profiles.dev.commands.status import status_command
from core.profiles.dev.commands.git import git_group
from core.profiles.dev.commands.platform import platform_command
from core.profiles.dev.commands.release import release_group
from core.profiles.dev.commands.help import help_command
from core.version import __version__

# Import manager profile CLI
from core.profiles.manager.main import cli as manager_cli

# Import individual dev commands for top-level access
from core.profiles.dev.commands.dev import (
    dev_run, dev_stop, dev_shell, dev_test,
    dev_migrate, dev_makemigrations, dev_logs
)


@click.group()
@click.version_option(version=__version__, prog_name='unibos-dev')
@click.option('--no-splash', is_flag=True, help='Skip splash screen')
@click.pass_context
def cli(ctx, no_splash):
    """🔧 UNIBOS Developer CLI - Development & Deployment Tools

    Developer-focused CLI for UNIBOS development, git workflows,
    versioning, and deployment operations.

    Examples:
        unibos-dev                     # Launch interactive TUI
        unibos-dev status              # Show system status
        unibos-dev run                 # Start development server (shortcut)
        unibos-dev shell               # Open Django shell (shortcut)
        unibos-dev dev run             # Start development server (full path)
        unibos-dev deploy rocksteady   # Deploy to production
        unibos-dev db backup           # Create database backup
        unibos-dev git push-dev        # Push to dev repository
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


# Register command groups (full paths - backwards compatibility)
cli.add_command(deploy_group)
cli.add_command(dev_group)
cli.add_command(db_group)
cli.add_command(status_command)
cli.add_command(git_group)
cli.add_command(platform_command)
cli.add_command(release_group)
cli.add_command(help_command)

# Register manager profile as a command group
cli.add_command(manager_cli, name='manager')

# Register top-level shortcuts for common dev commands
# These allow: unibos-dev run instead of unibos-dev dev run
cli.add_command(dev_run, name='run')
cli.add_command(dev_stop, name='stop')
cli.add_command(dev_shell, name='shell')
cli.add_command(dev_test, name='test')
cli.add_command(dev_migrate, name='migrate')
cli.add_command(dev_makemigrations, name='makemigrations')
cli.add_command(dev_logs, name='logs')


def main():
    """
    Main entry point for the CLI

    Hybrid mode:
    - With arguments → Click commands
    - Without arguments → Interactive TUI mode
    """
    # Check if running in interactive mode (no arguments provided)
    if len(sys.argv) == 1:
        # No arguments - run interactive TUI mode
        try:
            from core.profiles.dev.interactive import run_interactive
            run_interactive()
        except KeyboardInterrupt:
            click.echo("\n\n👋 Goodbye!")
            sys.exit(0)
        except Exception as e:
            click.echo(f"\n❌ Error: {e}", err=True)
            sys.exit(1)
    else:
        # Arguments provided - run Click CLI
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
