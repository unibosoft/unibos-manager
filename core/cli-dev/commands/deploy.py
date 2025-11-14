"""
UNIBOS CLI - Deployment Commands
Handles deployment to various environments (rocksteady, local, raspberry)
"""

import click
import subprocess
import sys
from pathlib import Path


@click.group(name='deploy')
def deploy_group():
    """🚀 Deployment commands for UNIBOS"""
    pass


@deploy_group.command(name='rocksteady')
@click.option('--quick', is_flag=True, help='Skip pre-flight checks')
@click.option('--check-only', is_flag=True, help='Only run health checks')
def deploy_rocksteady(quick, check_only):
    """Deploy to Rocksteady VPS (production)"""
    click.echo(click.style('🚀 Deploying to Rocksteady...', fg='cyan', bold=True))

    # Get repository root
    root_dir = Path(__file__).parent.parent.parent.parent
    deploy_script = root_dir / 'core' / 'deployment' / 'rocksteady_deploy.sh'

    if not deploy_script.exists():
        click.echo(click.style(f'❌ Error: Deployment script not found at {deploy_script}', fg='red'))
        sys.exit(1)

    # Build command
    cmd = [str(deploy_script)]

    if check_only:
        cmd.append('check')
    elif quick:
        cmd.append('sync')  # Quick sync without full checks
    else:
        cmd.append('deploy')  # Full deployment

    # Execute deployment script
    try:
        result = subprocess.run(cmd, cwd=str(root_dir))
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        click.echo(click.style('\n⚠️  Deployment interrupted by user', fg='yellow'))
        sys.exit(130)
    except Exception as e:
        click.echo(click.style(f'❌ Deployment failed: {e}', fg='red'))
        sys.exit(1)


@deploy_group.command(name='check')
def deploy_check():
    """Run health checks on deployed system"""
    click.echo(click.style('🔍 Running health checks...', fg='cyan'))

    root_dir = Path(__file__).parent.parent.parent.parent
    deploy_script = root_dir / 'core' / 'deployment' / 'rocksteady_deploy.sh'

    try:
        result = subprocess.run([str(deploy_script), 'check'], cwd=str(root_dir))
        sys.exit(result.returncode)
    except Exception as e:
        click.echo(click.style(f'❌ Health check failed: {e}', fg='red'))
        sys.exit(1)


@deploy_group.command(name='local')
@click.option('--path', default='/Users/berkhatirli/Applications/unibos/', help='Deployment path')
def deploy_local(path):
    """Deploy to local production environment"""
    click.echo(click.style(f'🏠 Deploying to local: {path}', fg='cyan'))
    click.echo(click.style('⚠️  Local deployment not yet implemented', fg='yellow'))
    click.echo('This will deploy UNIBOS to a local production environment')


@deploy_group.command(name='raspberry')
@click.argument('target', required=False)
def deploy_raspberry(target):
    """Deploy to Raspberry Pi edge device"""
    if not target:
        click.echo(click.style('❌ Error: Target IP/hostname required', fg='red'))
        click.echo('Usage: unibos deploy raspberry 192.168.1.100')
        sys.exit(1)

    click.echo(click.style(f'🥧 Deploying to Raspberry Pi: {target}', fg='cyan'))
    click.echo(click.style('⚠️  Raspberry Pi deployment not yet implemented', fg='yellow'))
    click.echo('This will deploy UNIBOS to a Raspberry Pi edge device')
