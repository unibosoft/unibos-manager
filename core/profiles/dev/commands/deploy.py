"""
UNIBOS CLI - Deployment Commands
Handles deployment to various servers using the deploy module
"""

import click
import sys
from pathlib import Path


# Add project root to path for deploy module
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))


@click.group(name='deploy')
def deploy_group():
    """deployment commands for UNIBOS servers"""
    pass


@deploy_group.command(name='run')
@click.argument('server', default='rocksteady')
@click.option('--dry-run', is_flag=True, help='simulate without making changes')
@click.option('--verbose', '-v', is_flag=True, default=True, help='show detailed output')
def deploy_run(server, dry_run, verbose):
    """run full deployment to a server

    examples:
        unibos-dev deploy run                  # deploy to rocksteady
        unibos-dev deploy run rocksteady       # deploy to rocksteady
        unibos-dev deploy run --dry-run        # simulate deployment
    """
    try:
        from deploy.config import DeployConfig
        from deploy.deploy import ServerDeployer
    except ImportError as e:
        click.echo(click.style(f'error: deploy module not found: {e}', fg='red'))
        sys.exit(1)

    config_file = project_root / f"{server}.config.json"

    if not config_file.exists():
        click.echo(click.style(f'error: config file not found: {config_file}', fg='red'))
        click.echo(f'create {server}.config.json in project root')
        sys.exit(1)

    click.echo(click.style(f'deploying to {server}...', fg='cyan', bold=True))

    if dry_run:
        click.echo(click.style('[DRY RUN MODE]', fg='yellow'))

    try:
        config = DeployConfig.load(config_file)
        deployer = ServerDeployer(config, dry_run=dry_run, verbose=verbose)
        result = deployer.deploy()

        if result.success:
            click.echo(click.style(f'\n{result.message}', fg='green', bold=True))
        else:
            click.echo(click.style(f'\nerror: {result.message}', fg='red'))
            if result.details:
                click.echo(result.details)
            sys.exit(1)

    except Exception as e:
        click.echo(click.style(f'deployment failed: {e}', fg='red'))
        sys.exit(1)


@deploy_group.command(name='status')
@click.argument('server', default='rocksteady')
def deploy_status(server):
    """check deployment status on a server

    examples:
        unibos-dev deploy status               # check rocksteady
        unibos-dev deploy status rocksteady    # check rocksteady
    """
    try:
        from deploy.config import DeployConfig
        from deploy.deploy import ServerDeployer
    except ImportError as e:
        click.echo(click.style(f'error: deploy module not found: {e}', fg='red'))
        sys.exit(1)

    config_file = project_root / f"{server}.config.json"

    if not config_file.exists():
        click.echo(click.style(f'error: config file not found: {config_file}', fg='red'))
        sys.exit(1)

    try:
        config = DeployConfig.load(config_file)
        deployer = ServerDeployer(config, verbose=False)
        result = deployer.status()

        click.echo(click.style(f'status: {server}', fg='cyan', bold=True))
        click.echo(result.details or result.message)

    except Exception as e:
        click.echo(click.style(f'error: {e}', fg='red'))
        sys.exit(1)


@deploy_group.command(name='start')
@click.argument('server', default='rocksteady')
def deploy_start(server):
    """start service on a server"""
    try:
        from deploy.config import DeployConfig
        from deploy.deploy import ServerDeployer
    except ImportError as e:
        click.echo(click.style(f'error: deploy module not found: {e}', fg='red'))
        sys.exit(1)

    config_file = project_root / f"{server}.config.json"

    if not config_file.exists():
        click.echo(click.style(f'error: config file not found: {config_file}', fg='red'))
        sys.exit(1)

    try:
        config = DeployConfig.load(config_file)
        deployer = ServerDeployer(config)
        result = deployer.start()

        if result.success:
            click.echo(click.style(f'service started on {server}', fg='green'))
        else:
            click.echo(click.style(f'error: {result.message}', fg='red'))
            sys.exit(1)

    except Exception as e:
        click.echo(click.style(f'error: {e}', fg='red'))
        sys.exit(1)


@deploy_group.command(name='stop')
@click.argument('server', default='rocksteady')
def deploy_stop(server):
    """stop service on a server"""
    try:
        from deploy.config import DeployConfig
        from deploy.deploy import ServerDeployer
    except ImportError as e:
        click.echo(click.style(f'error: deploy module not found: {e}', fg='red'))
        sys.exit(1)

    config_file = project_root / f"{server}.config.json"

    if not config_file.exists():
        click.echo(click.style(f'error: config file not found: {config_file}', fg='red'))
        sys.exit(1)

    try:
        config = DeployConfig.load(config_file)
        deployer = ServerDeployer(config)
        result = deployer.stop()

        if result.success:
            click.echo(click.style(f'service stopped on {server}', fg='green'))
        else:
            click.echo(click.style(f'error: {result.message}', fg='red'))
            sys.exit(1)

    except Exception as e:
        click.echo(click.style(f'error: {e}', fg='red'))
        sys.exit(1)


@deploy_group.command(name='restart')
@click.argument('server', default='rocksteady')
def deploy_restart(server):
    """restart service on a server"""
    try:
        from deploy.config import DeployConfig
        from deploy.deploy import ServerDeployer
    except ImportError as e:
        click.echo(click.style(f'error: deploy module not found: {e}', fg='red'))
        sys.exit(1)

    config_file = project_root / f"{server}.config.json"

    if not config_file.exists():
        click.echo(click.style(f'error: config file not found: {config_file}', fg='red'))
        sys.exit(1)

    try:
        config = DeployConfig.load(config_file)
        deployer = ServerDeployer(config)
        result = deployer.restart()

        if result.success:
            click.echo(click.style(f'service restarted on {server}', fg='green'))
        else:
            click.echo(click.style(f'error: {result.message}', fg='red'))
            sys.exit(1)

    except Exception as e:
        click.echo(click.style(f'error: {e}', fg='red'))
        sys.exit(1)


@deploy_group.command(name='logs')
@click.argument('server', default='rocksteady')
@click.option('-n', '--lines', default=50, help='number of lines to show')
@click.option('-f', '--follow', is_flag=True, help='follow log output')
def deploy_logs(server, lines, follow):
    """view service logs from a server

    examples:
        unibos-dev deploy logs                 # last 50 lines
        unibos-dev deploy logs -n 100          # last 100 lines
        unibos-dev deploy logs -f              # follow logs
    """
    try:
        from deploy.config import DeployConfig
        from deploy.deploy import ServerDeployer
    except ImportError as e:
        click.echo(click.style(f'error: deploy module not found: {e}', fg='red'))
        sys.exit(1)

    config_file = project_root / f"{server}.config.json"

    if not config_file.exists():
        click.echo(click.style(f'error: config file not found: {config_file}', fg='red'))
        sys.exit(1)

    try:
        config = DeployConfig.load(config_file)
        deployer = ServerDeployer(config, verbose=False)
        result = deployer.logs(lines=lines, follow=follow)

        if result.details:
            click.echo(result.details)

    except Exception as e:
        click.echo(click.style(f'error: {e}', fg='red'))
        sys.exit(1)


@deploy_group.command(name='ssh')
@click.argument('server', default='rocksteady')
def deploy_ssh(server):
    """open ssh connection to a server

    example:
        unibos-dev deploy ssh rocksteady
    """
    import subprocess

    try:
        from deploy.config import DeployConfig
    except ImportError as e:
        click.echo(click.style(f'error: deploy module not found: {e}', fg='red'))
        sys.exit(1)

    config_file = project_root / f"{server}.config.json"

    if not config_file.exists():
        click.echo(click.style(f'error: config file not found: {config_file}', fg='red'))
        sys.exit(1)

    try:
        config = DeployConfig.load(config_file)
        click.echo(click.style(f'connecting to {server}...', fg='cyan'))

        subprocess.run(['ssh', f'-p{config.port}', config.ssh_target])

    except Exception as e:
        click.echo(click.style(f'error: {e}', fg='red'))
        sys.exit(1)


@deploy_group.command(name='list')
def deploy_list():
    """list available server configurations

    shows all *.config.json files in project root
    """
    configs = list(project_root.glob('*.config.json'))

    if not configs:
        click.echo(click.style('no server configurations found', fg='yellow'))
        click.echo('create a config file like rocksteady.config.json')
        return

    click.echo(click.style('available servers:', fg='cyan', bold=True))
    for config_file in sorted(configs):
        server_name = config_file.stem.replace('.config', '')
        click.echo(f'  {server_name}')


@deploy_group.command(name='backup')
@click.argument('server', default='rocksteady')
def deploy_backup(server):
    """create database backup on server

    backups are stored in data/backups/ on the server

    example:
        unibos-dev deploy backup rocksteady
    """
    try:
        from deploy.config import DeployConfig
        from deploy.deploy import ServerDeployer
    except ImportError as e:
        click.echo(click.style(f'error: deploy module not found: {e}', fg='red'))
        sys.exit(1)

    config_file = project_root / f"{server}.config.json"

    if not config_file.exists():
        click.echo(click.style(f'error: config file not found: {config_file}', fg='red'))
        sys.exit(1)

    try:
        config = DeployConfig.load(config_file)
        deployer = ServerDeployer(config)
        result = deployer.backup()

        if result.success:
            click.echo(click.style(result.message, fg='green'))
        else:
            click.echo(click.style(f'error: {result.message}', fg='red'))
            if result.details:
                click.echo(result.details)
            sys.exit(1)

    except Exception as e:
        click.echo(click.style(f'error: {e}', fg='red'))
        sys.exit(1)


@deploy_group.command(name='backups')
@click.argument('server', default='rocksteady')
def deploy_backups(server):
    """list available backups on server

    example:
        unibos-dev deploy backups rocksteady
    """
    try:
        from deploy.config import DeployConfig
        from deploy.deploy import ServerDeployer
    except ImportError as e:
        click.echo(click.style(f'error: deploy module not found: {e}', fg='red'))
        sys.exit(1)

    config_file = project_root / f"{server}.config.json"

    if not config_file.exists():
        click.echo(click.style(f'error: config file not found: {config_file}', fg='red'))
        sys.exit(1)

    try:
        config = DeployConfig.load(config_file)
        deployer = ServerDeployer(config, verbose=False)
        result = deployer.list_backups()

        click.echo(click.style(f'backups on {server}:', fg='cyan', bold=True))
        if result.details:
            click.echo(result.details)

    except Exception as e:
        click.echo(click.style(f'error: {e}', fg='red'))
        sys.exit(1)


# Legacy commands for backwards compatibility
@deploy_group.command(name='rocksteady')
@click.option('--dry-run', is_flag=True, help='simulate without making changes')
@click.pass_context
def deploy_rocksteady(ctx, dry_run):
    """deploy to rocksteady server (alias for 'deploy run rocksteady')"""
    ctx.invoke(deploy_run, server='rocksteady', dry_run=dry_run, verbose=True)
