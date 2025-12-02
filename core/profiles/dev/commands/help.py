"""
UNIBOS CLI - Help Command
Comprehensive help and documentation for all CLI commands
"""

import click
from core.version import __version__, __build__


HELP_TEXT = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                        UNIBOS-DEV CLI REFERENCE                              ║
║                     v{version}+build.{build}                            ║
╚══════════════════════════════════════════════════════════════════════════════╝

USAGE
    unibos-dev                      Launch interactive TUI
    unibos-dev [command]            Run specific command
    unibos-dev [command] --help     Get help for command

────────────────────────────────────────────────────────────────────────────────
QUICK START
────────────────────────────────────────────────────────────────────────────────

  Start Development Server
    unibos-dev run                  Start uvicorn server (foreground)
    unibos-dev run -b               Start in background mode
    unibos-dev stop                 Stop the server
    unibos-dev status               Check system status

  Database Operations
    unibos-dev migrate              Run migrations
    unibos-dev shell                Open Django shell

  Release & Version
    unibos-dev release run build    Create new build (timestamp only)
    unibos-dev release info         Show version details

────────────────────────────────────────────────────────────────────────────────
COMMAND GROUPS
────────────────────────────────────────────────────────────────────────────────

  dev         Development server commands
  db          Database management
  git         Git repository operations
  deploy      Production deployment
  release     Version & release management
  platform    Hardware & OS information
  manager     Remote node management

────────────────────────────────────────────────────────────────────────────────
DEV COMMANDS (unibos-dev dev ...)
────────────────────────────────────────────────────────────────────────────────

  run [--port] [--host] [-b]        Start uvicorn ASGI server
                                    -b, --background  Run in background
                                    --port PORT       Default: 8000
                                    --host HOST       Default: 127.0.0.1

  stop                              Stop running development server
  status                            Check if server is running
  shell                             Open Django interactive shell
  test [args]                       Run Django tests
  migrate [--app]                   Apply database migrations
  makemigrations [--app]            Create new migrations
  logs [-n] [-f]                    View development logs
                                    -n, --lines       Number of lines
                                    -f, --follow      Follow log output

  Shortcuts (top-level):
    unibos-dev run      = unibos-dev dev run
    unibos-dev stop     = unibos-dev dev stop
    unibos-dev shell    = unibos-dev dev shell
    unibos-dev migrate  = unibos-dev dev migrate

────────────────────────────────────────────────────────────────────────────────
DATABASE COMMANDS (unibos-dev db ...)
────────────────────────────────────────────────────────────────────────────────

  status                            Check PostgreSQL status
  create                            Create UNIBOS database
  migrate                           Run Django migrations
  backup                            Create database backup
  restore                           Restore from backup

────────────────────────────────────────────────────────────────────────────────
GIT COMMANDS (unibos-dev git ...)
────────────────────────────────────────────────────────────────────────────────

  status                            Show repository status
  push-dev                          Push to dev remote
  push-prod                         Push to prod remote
  pull                              Pull from remote
  sync                              Sync all remotes

────────────────────────────────────────────────────────────────────────────────
RELEASE COMMANDS (unibos-dev release ...)
────────────────────────────────────────────────────────────────────────────────

  info                              Show detailed version info
  current                           Show current version (short)

  run [TYPE] [-m MSG]               Run release pipeline
                                    TYPE: build | patch | minor | major

      build   New timestamp, same version (v1.0.0 → v1.0.0)
      patch   Bug fix release          (v1.0.0 → v1.0.1)
      minor   Feature release          (v1.0.0 → v1.1.0)
      major   Breaking change          (v1.0.0 → v2.0.0)

      Options:
        -m, --message   Custom commit message
        --dry-run       Simulate without executing
        -r, --repos     Target repos (default: dev,server,manager,prod)

  archives [-n LIMIT] [--json]      Browse version archives
  analyze                           Show archive statistics

  Examples:
    unibos-dev release run build
    unibos-dev release run minor -m "feat: new feature"
    unibos-dev release run patch --dry-run
    unibos-dev release archives --limit 20

────────────────────────────────────────────────────────────────────────────────
DEPLOY COMMANDS (unibos-dev deploy ...)
────────────────────────────────────────────────────────────────────────────────

  rocksteady                        Deploy to Rocksteady server
  status [server]                   Check server status
  logs [server]                     View server logs
  backup [server]                   Create server backup
  ssh [server]                      SSH to server

────────────────────────────────────────────────────────────────────────────────
OTHER COMMANDS
────────────────────────────────────────────────────────────────────────────────

  status                            System health check
  platform [--json] [-v]            Show platform information
  manager                           Remote management tools

────────────────────────────────────────────────────────────────────────────────
EXAMPLES
────────────────────────────────────────────────────────────────────────────────

  # Daily workflow
  unibos-dev run -b                 # Start server in background
  unibos-dev status                 # Check status
  # ... make changes ...
  unibos-dev release run build      # Create new build
  unibos-dev deploy rocksteady      # Deploy to production

  # Database workflow
  unibos-dev db status              # Check PostgreSQL
  unibos-dev makemigrations         # Create migrations
  unibos-dev migrate                # Apply migrations
  unibos-dev shell                  # Test in Django shell

  # Git workflow
  unibos-dev git status             # Check git status
  unibos-dev git push-dev           # Push to dev remote

────────────────────────────────────────────────────────────────────────────────
INTERACTIVE MODE
────────────────────────────────────────────────────────────────────────────────

  Run `unibos-dev` without arguments to launch the interactive TUI.

  TUI Navigation:
    ↑/↓         Navigate menu items
    Enter/→     Select item / Enter submenu
    Esc/←       Go back / Exit submenu
    q           Quit TUI
    ?           Show help in TUI

────────────────────────────────────────────────────────────────────────────────
MORE INFORMATION
────────────────────────────────────────────────────────────────────────────────

  unibos-dev [command] --help       Detailed help for any command
  unibos-dev --version              Show version

  Project: /Users/berkhatirli/Desktop/unibos-dev
  Docs:    https://github.com/berkhatirli/unibos

"""


@click.command(name='help')
@click.argument('topic', required=False)
def help_command(topic):
    """Show comprehensive CLI help and documentation

    Examples:
        unibos-dev help           Show full help
        unibos-dev help dev       Help for dev commands
        unibos-dev help release   Help for release commands
    """
    if topic:
        # Show topic-specific help
        show_topic_help(topic)
    else:
        # Show full help
        formatted = HELP_TEXT.format(
            version=__version__,
            build=__build__[:8] + '...'
        )
        click.echo(formatted)


def show_topic_help(topic):
    """Show help for specific topic"""
    topics = {
        'dev': """
DEV COMMANDS
════════════

  unibos-dev dev run [OPTIONS]
      Start uvicorn ASGI development server

      Options:
        --port INTEGER    Port to run on (default: 8000)
        --host TEXT       Host to bind to (default: 127.0.0.1)
        --reload/--no-reload  Enable auto-reload (default: enabled)
        -b, --background  Run in background mode

      Examples:
        unibos-dev dev run              # Start in foreground
        unibos-dev dev run -b           # Start in background
        unibos-dev dev run --port 8080  # Custom port

  unibos-dev dev stop
      Stop the running development server

  unibos-dev dev status
      Check if development server is running

  unibos-dev dev shell
      Open Django interactive shell (IPython if available)

  unibos-dev dev test [ARGS]
      Run Django tests

      Examples:
        unibos-dev dev test                    # Run all tests
        unibos-dev dev test myapp              # Run app tests
        unibos-dev dev test myapp.tests.MyTest # Run specific test

  unibos-dev dev migrate [OPTIONS]
      Apply database migrations

      Options:
        --app TEXT    Specific app to migrate

  unibos-dev dev makemigrations [OPTIONS]
      Create new database migrations

      Options:
        --app TEXT    Specific app to create migrations for

  unibos-dev dev logs [OPTIONS]
      View development server logs

      Options:
        -n, --lines INTEGER   Number of lines to show (default: 50)
        -f, --follow          Follow log output (like tail -f)
""",
        'release': """
RELEASE COMMANDS
════════════════

  unibos-dev release info
      Show detailed version information including:
      - Current version and build timestamp
      - Codename and release type
      - Build date and time
      - Archive name
      - Feature flags status

  unibos-dev release current
      Show just the current version string
      Output: v1.0.0+build.20251203004540

  unibos-dev release run [TYPE] [OPTIONS]
      Run the release pipeline to create a new version

      Types:
        build   Keep same version, new timestamp only
        patch   Increment patch version (x.y.Z) - bug fixes
        minor   Increment minor version (x.Y.0) - new features
        major   Increment major version (X.0.0) - breaking changes

      Options:
        -m, --message TEXT    Custom commit message
        --dry-run             Simulate without making changes
        -r, --repos TEXT      Target repositories (can specify multiple)
                              Default: dev, server, manager, prod

      Pipeline Steps:
        1. Update CHANGELOG.md (from conventional commits)
        2. Update version files (VERSION.json, core/version.py)
        3. Create archive snapshot
        4. Git commit
        5. Create git tag
        6. Push to all repositories

      Examples:
        unibos-dev release run build
        unibos-dev release run minor -m "feat: add new feature"
        unibos-dev release run patch --dry-run
        unibos-dev release run build -r dev -r server

  unibos-dev release archives [OPTIONS]
      Browse version archives

      Options:
        -n, --limit INTEGER   Number of archives to show (default: 15)
        --json                Output as JSON format

      Examples:
        unibos-dev release archives
        unibos-dev release archives --limit 30
        unibos-dev release archives --json

  unibos-dev release analyze
      Analyze archive directory statistics:
      - Total number of archives
      - Total disk space used
      - Average archive size
      - Largest archives
      - Anomaly detection (archives >2x average)
""",
        'db': """
DATABASE COMMANDS
═════════════════

  unibos-dev db status
      Check PostgreSQL installation and connection status

  unibos-dev db create
      Create the UNIBOS database (unibos_dev)

  unibos-dev db migrate
      Run Django database migrations
      (Same as: unibos-dev migrate)

  unibos-dev db backup
      Create a timestamped database backup
      Backups stored in: data/backups/

  unibos-dev db restore
      Restore database from a backup file
""",
        'git': """
GIT COMMANDS
════════════

  unibos-dev git status
      Show current repository status (branch, changes, remotes)

  unibos-dev git push-dev
      Push current branch to 'dev' remote repository

  unibos-dev git push-prod
      Push current branch to 'prod' remote repository

  unibos-dev git pull
      Pull latest changes from remote

  unibos-dev git sync
      Synchronize all configured remotes

CONFIGURED REMOTES
  dev      Development repository (full codebase)
  server   Server deployment (excludes dev tools)
  manager  Manager tools repository
  prod     Production nodes (minimal)
""",
        'deploy': """
DEPLOY COMMANDS
═══════════════

  unibos-dev deploy rocksteady
      Deploy UNIBOS to Rocksteady production server

      This command:
      1. Syncs files via rsync (respecting .rsyncignore)
      2. Runs migrations on server
      3. Restarts services
      4. Verifies deployment

  unibos-dev deploy status [SERVER]
      Check deployment status on server

      Example:
        unibos-dev deploy status rocksteady

  unibos-dev deploy logs [SERVER]
      View production server logs

      Example:
        unibos-dev deploy logs rocksteady

  unibos-dev deploy backup [SERVER]
      Create backup on production server

  unibos-dev deploy ssh [SERVER]
      Open SSH connection to server

SERVER CONFIGURATION
  Servers are configured in: core/profiles/dev/servers.json
  SSH config should be set up in: ~/.ssh/config
""",
        'platform': """
PLATFORM COMMAND
════════════════

  unibos-dev platform [OPTIONS]
      Display platform and hardware information

      Options:
        --json      Output as JSON format
        -v          Verbose output with all details

      Information displayed:
        - Operating system and version
        - Hardware specifications (CPU, RAM, disk)
        - Device type classification
        - Network information
        - UNIBOS capabilities

      Examples:
        unibos-dev platform           # Human-readable output
        unibos-dev platform --json    # JSON format for scripts
        unibos-dev platform -v        # Verbose details
"""
    }

    topic_lower = topic.lower()

    if topic_lower in topics:
        click.echo(topics[topic_lower])
    else:
        click.echo(f"Unknown topic: {topic}")
        click.echo()
        click.echo("Available topics:")
        for t in sorted(topics.keys()):
            click.echo(f"  {t}")
        click.echo()
        click.echo("Usage: unibos-dev help [topic]")
