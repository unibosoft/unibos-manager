"""
unibos cli - help command
comprehensive help and documentation for all cli commands
"""

import click
from core.version import __version__, __build__


HELP_TEXT = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                        unibos-dev cli reference                              ║
║                     v{version}+build.{build}                            ║
╚══════════════════════════════════════════════════════════════════════════════╝

usage
    unibos-dev                      launch interactive tui
    unibos-dev [command]            run specific command
    unibos-dev [command] --help     get help for command

────────────────────────────────────────────────────────────────────────────────
quick start
────────────────────────────────────────────────────────────────────────────────

  start development server
    unibos-dev run                  start uvicorn server (foreground)
    unibos-dev run -b               start in background mode
    unibos-dev stop                 stop the server
    unibos-dev status               check system status

  database operations
    unibos-dev migrate              run migrations
    unibos-dev shell                open django shell

  release & version
    unibos-dev release run build    create new build (timestamp only)
    unibos-dev release info         show version details

────────────────────────────────────────────────────────────────────────────────
command groups
────────────────────────────────────────────────────────────────────────────────

  dev         development server commands
  db          database management
  git         git repository operations
  deploy      production deployment
  release     version & release management
  platform    hardware & os information
  manager     remote node management

────────────────────────────────────────────────────────────────────────────────
dev commands (unibos-dev dev ...)
────────────────────────────────────────────────────────────────────────────────

  run [--port] [--host] [-b]        start uvicorn asgi server
                                    -b, --background  run in background
                                    --port PORT       default: 8000
                                    --host HOST       default: 127.0.0.1

  stop                              stop running development server
  status                            check if server is running
  shell                             open django interactive shell
  test [args]                       run django tests
  migrate [--app]                   apply database migrations
  makemigrations [--app]            create new migrations
  logs [-n] [-f]                    view development logs
                                    -n, --lines       number of lines
                                    -f, --follow      follow log output

  shortcuts (top-level):
    unibos-dev run      = unibos-dev dev run
    unibos-dev stop     = unibos-dev dev stop
    unibos-dev shell    = unibos-dev dev shell
    unibos-dev migrate  = unibos-dev dev migrate

────────────────────────────────────────────────────────────────────────────────
database commands (unibos-dev db ...)
────────────────────────────────────────────────────────────────────────────────

  status                            check postgresql status
  create                            create unibos database
  migrate                           run django migrations
  backup                            create database backup
  restore                           restore from backup

────────────────────────────────────────────────────────────────────────────────
git commands (unibos-dev git ...)
────────────────────────────────────────────────────────────────────────────────

  status                            show dev/prod repository status
  push-dev                          push to dev remote (origin)
  push-all                          push to dev, server, manager, prod
  push-prod                         push filtered to production
  sync-prod                         sync code to local prod directory
  setup                             configure git remotes

────────────────────────────────────────────────────────────────────────────────
release commands (unibos-dev release ...)
────────────────────────────────────────────────────────────────────────────────

  info                              show detailed version info
  current                           show current version (short)

  run [TYPE] [-m MSG]               run release pipeline
                                    TYPE: build | patch | minor | major

      build   new timestamp, same version (v1.0.0 → v1.0.0)
      patch   bug fix release          (v1.0.0 → v1.0.1)
      minor   feature release          (v1.0.0 → v1.1.0)
      major   breaking change          (v1.0.0 → v2.0.0)

      options:
        -m, --message   custom commit message
        --dry-run       simulate without executing
        -r, --repos     target repos (default: dev,server,manager,prod)

  archives [-n LIMIT] [--json]      browse version archives
  analyze                           show archive statistics

  examples:
    unibos-dev release run build
    unibos-dev release run minor -m "feat: new feature"
    unibos-dev release run patch --dry-run
    unibos-dev release archives --limit 20

────────────────────────────────────────────────────────────────────────────────
deploy commands (unibos-dev deploy ...)
────────────────────────────────────────────────────────────────────────────────

  rocksteady                        deploy to rocksteady server
  status [server]                   check server status
  logs [server]                     view server logs
  backup [server]                   create server backup
  ssh [server]                      ssh to server

────────────────────────────────────────────────────────────────────────────────
other commands
────────────────────────────────────────────────────────────────────────────────

  status                            system health check
  platform [--json] [-v]            show platform information
  manager                           remote management tools

────────────────────────────────────────────────────────────────────────────────
examples
────────────────────────────────────────────────────────────────────────────────

  # daily workflow
  unibos-dev run -b                 # start server in background
  unibos-dev status                 # check status
  # ... make changes ...
  unibos-dev release run build      # create new build
  unibos-dev deploy rocksteady      # deploy to production

  # database workflow
  unibos-dev db status              # check postgresql
  unibos-dev makemigrations         # create migrations
  unibos-dev migrate                # apply migrations
  unibos-dev shell                  # test in django shell

  # git workflow
  unibos-dev git status             # check git status
  unibos-dev git push-dev           # push to dev remote
  unibos-dev git push-all           # push to all remotes
  unibos-dev git push-prod          # push to production

────────────────────────────────────────────────────────────────────────────────
interactive mode
────────────────────────────────────────────────────────────────────────────────

  run `unibos-dev` without arguments to launch the interactive tui.

  tui navigation:
    ↑/↓         navigate menu items
    enter/→     select item / enter submenu
    esc/←       go back / exit submenu
    q           quit tui
    ?           show help in tui

────────────────────────────────────────────────────────────────────────────────
more information
────────────────────────────────────────────────────────────────────────────────

  unibos-dev [command] --help       detailed help for any command
  unibos-dev --version              show version

  project: /Users/berkhatirli/Desktop/unibos-dev
  docs:    https://github.com/berkhatirli/unibos

"""


@click.command(name='help')
@click.argument('topic', required=False)
def help_command(topic):
    """show comprehensive cli help and documentation

    examples:
        unibos-dev help           show full help
        unibos-dev help dev       help for dev commands
        unibos-dev help release   help for release commands
    """
    if topic:
        # show topic-specific help
        show_topic_help(topic)
    else:
        # show full help
        formatted = HELP_TEXT.format(
            version=__version__,
            build=__build__[:8] + '...'
        )
        click.echo(formatted)


def show_topic_help(topic):
    """show help for specific topic"""
    topics = {
        'dev': """
dev commands
════════════

  unibos-dev dev run [options]
      start uvicorn asgi development server

      options:
        --port INTEGER    port to run on (default: 8000)
        --host TEXT       host to bind to (default: 127.0.0.1)
        --reload/--no-reload  enable auto-reload (default: enabled)
        -b, --background  run in background mode

      examples:
        unibos-dev dev run              # start in foreground
        unibos-dev dev run -b           # start in background
        unibos-dev dev run --port 8080  # custom port

  unibos-dev dev stop
      stop the running development server

  unibos-dev dev status
      check if development server is running

  unibos-dev dev shell
      open django interactive shell (ipython if available)

  unibos-dev dev test [args]
      run django tests

      examples:
        unibos-dev dev test                    # run all tests
        unibos-dev dev test myapp              # run app tests
        unibos-dev dev test myapp.tests.MyTest # run specific test

  unibos-dev dev migrate [options]
      apply database migrations

      options:
        --app TEXT    specific app to migrate

  unibos-dev dev makemigrations [options]
      create new database migrations

      options:
        --app TEXT    specific app to create migrations for

  unibos-dev dev logs [options]
      view development server logs

      options:
        -n, --lines INTEGER   number of lines to show (default: 50)
        -f, --follow          follow log output (like tail -f)
""",
        'release': """
release commands
════════════════

  unibos-dev release info
      show detailed version information including:
      - current version and build timestamp
      - codename and release type
      - build date and time
      - archive name
      - feature flags status

  unibos-dev release current
      show just the current version string
      output: v1.0.0+build.20251203004540

  unibos-dev release run [type] [options]
      run the release pipeline to create a new version

      types:
        build   keep same version, new timestamp only
        patch   increment patch version (x.y.Z) - bug fixes
        minor   increment minor version (x.Y.0) - new features
        major   increment major version (X.0.0) - breaking changes

      options:
        -m, --message TEXT    custom commit message
        --dry-run             simulate without making changes
        -r, --repos TEXT      target repositories (can specify multiple)
                              default: dev, server, manager, prod

      pipeline steps:
        1. update changelog.md (from conventional commits)
        2. update version files (VERSION.json, core/version.py)
        3. create archive snapshot
        4. git commit
        5. create git tag
        6. push to all repositories

      examples:
        unibos-dev release run build
        unibos-dev release run minor -m "feat: add new feature"
        unibos-dev release run patch --dry-run
        unibos-dev release run build -r dev -r server

  unibos-dev release archives [options]
      browse version archives

      options:
        -n, --limit INTEGER   number of archives to show (default: 15)
        --json                output as json format

      examples:
        unibos-dev release archives
        unibos-dev release archives --limit 30
        unibos-dev release archives --json

  unibos-dev release analyze
      analyze archive directory statistics:
      - total number of archives
      - total disk space used
      - average archive size
      - largest archives
      - anomaly detection (archives >2x average)
""",
        'db': """
database commands
═════════════════

  unibos-dev db status
      check postgresql installation and connection status

  unibos-dev db create
      create the unibos database (unibos_dev)

  unibos-dev db migrate
      run django database migrations
      (same as: unibos-dev migrate)

  unibos-dev db backup
      create a timestamped database backup
      backups stored in: data/backups/

  unibos-dev db restore
      restore database from a backup file
""",
        'git': """
git commands
════════════

  unibos-dev git status
      show dev and prod repository status (branch, changes, remotes)

  unibos-dev git push-dev
      push current branch to 'origin' (development repository)
      includes all files in the repository

  unibos-dev git push-all [MESSAGE]
      push to multiple repositories with correct .gitignore templates:
      - dev     : full codebase (3 CLIs)
      - server  : excludes cli_dev (2 CLIs)
      - prod    : cli_node only, minimal (1 CLI)

      options:
        MESSAGE               optional commit message (if omitted, pushes existing)
        -r, --repos REPO      target specific repo (dev/server/prod/all)
        -d, --dry-run         simulate without pushing

  unibos-dev git push-prod
      push filtered code to production repository
      uses .prodignore to exclude development files

  unibos-dev git sync-prod
      sync current code to local production directory (filtered)
      useful for testing production builds locally

  unibos-dev git setup
      configure git remotes for dev, server, manager, and prod repositories
      sets up all required remotes for push operations

configured remotes
  origin   development repository (full codebase)
  dev      alias for origin
  server   server deployment (excludes dev tools)
  manager  manager tools repository
  prod     production nodes (minimal, filtered)

examples
  unibos-dev git status                        # check repo status
  unibos-dev git push-dev                      # push to development
  unibos-dev git push-all                      # push existing to all repos
  unibos-dev git push-all "feat: new feature"  # commit and push to all
  unibos-dev git push-all --repos dev          # push to dev only
  unibos-dev git push-prod                     # push to production only
""",
        'deploy': """
deploy commands
═══════════════

  unibos-dev deploy run [server] [options]
      run full deployment to a server

      options:
        --dry-run     simulate without making changes

      pipeline steps:
        1. validate configuration
        2. check ssh connectivity
        3. clone repository from git
        4. setup python venv
        5. install dependencies
        6. create .env file
        7. setup module registry
        8. setup data directory
        9. setup postgresql database
        10. run migrations
        11. collect static files
        12. setup systemd service
        13. start service
        14. health check

      examples:
        unibos-dev deploy run                  # deploy to rocksteady
        unibos-dev deploy run rocksteady       # deploy to rocksteady
        unibos-dev deploy run --dry-run        # simulate deployment

  unibos-dev deploy status [server]
      check service status on server

  unibos-dev deploy start [server]
      start unibos service

  unibos-dev deploy stop [server]
      stop unibos service

  unibos-dev deploy restart [server]
      restart unibos service

  unibos-dev deploy logs [server] [options]
      view service logs from server

      options:
        -n, --lines INTEGER   number of lines (default: 50)
        -f, --follow          follow log output

  unibos-dev deploy backup [server]
      create database backup on server
      backups are stored in data/backups/ on the server

  unibos-dev deploy backups [server]
      list available backups on server

  unibos-dev deploy ssh [server]
      open ssh connection to server

  unibos-dev deploy list
      list available server configurations

server configuration
  servers are configured via *.config.json files in project root
  example: rocksteady.config.json

  config file structure:
    {
      "name": "rocksteady",
      "host": "rocksteady",
      "user": "ubuntu",
      "deploy_path": "/home/ubuntu/unibos",
      "env_vars": {
        "SECRET_KEY": "...",
        "DB_NAME": "unibos_rocksteady",
        "DB_USER": "unibos",
        "DB_PASSWORD": "..."
      }
    }
""",
        'platform': """
platform command
════════════════

  unibos-dev platform [options]
      display platform and hardware information

      options:
        --json      output as json format
        -v          verbose output with all details

      information displayed:
        - operating system and version
        - hardware specifications (cpu, ram, disk)
        - device type classification
        - network information
        - unibos capabilities

      examples:
        unibos-dev platform           # human-readable output
        unibos-dev platform --json    # json format for scripts
        unibos-dev platform -v        # verbose details
"""
    }

    topic_lower = topic.lower()

    if topic_lower in topics:
        click.echo(topics[topic_lower])
    else:
        click.echo(f"unknown topic: {topic}")
        click.echo()
        click.echo("available topics:")
        for t in sorted(topics.keys()):
            click.echo(f"  {t}")
        click.echo()
        click.echo("usage: unibos-dev help [topic]")
