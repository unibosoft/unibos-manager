"""
UNIBOS Server CLI - Stats Command
System performance statistics
"""

import click

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


@click.command(name='stats')
def stats_command():
    """📊 Show server performance statistics"""
    if not PSUTIL_AVAILABLE:
        click.echo(click.style('❌ psutil not installed', fg='red'))
        click.echo('   Install with: pip install psutil')
        return

    click.echo(click.style('📊 Server Statistics', fg='magenta', bold=True))
    click.echo()

    # CPU
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_count = psutil.cpu_count()
    click.echo(click.style('CPU:', fg='cyan'))
    click.echo(f"  Usage: {cpu_percent}%")
    click.echo(f"  Cores: {cpu_count}")

    # Memory
    mem = psutil.virtual_memory()
    click.echo()
    click.echo(click.style('Memory:', fg='cyan'))
    click.echo(f"  Total: {mem.total / 1024**3:.1f} GB")
    click.echo(f"  Used: {mem.used / 1024**3:.1f} GB ({mem.percent}%)")
    click.echo(f"  Available: {mem.available / 1024**3:.1f} GB")

    # Disk
    disk = psutil.disk_usage('/')
    click.echo()
    click.echo(click.style('Disk (/):', fg='cyan'))
    click.echo(f"  Total: {disk.total / 1024**3:.1f} GB")
    click.echo(f"  Used: {disk.used / 1024**3:.1f} GB ({disk.percent}%)")
    click.echo(f"  Free: {disk.free / 1024**3:.1f} GB")

    # Network
    try:
        net = psutil.net_io_counters()
        click.echo()
        click.echo(click.style('Network:', fg='cyan'))
        click.echo(f"  Sent: {net.bytes_sent / 1024**3:.2f} GB")
        click.echo(f"  Received: {net.bytes_recv / 1024**3:.2f} GB")
    except:
        pass
