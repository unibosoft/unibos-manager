"""
UNIBOS CLI - Release Commands
Version management, archiving, and release pipeline
"""

import click
import sys
import json
import re
from pathlib import Path
from datetime import datetime


def get_project_root():
    """Get UNIBOS project root directory"""
    import subprocess as sp
    result = sp.run(
        ['git', 'rev-parse', '--show-toplevel'],
        capture_output=True,
        text=True,
        check=False
    )
    if result.returncode == 0:
        return Path(result.stdout.strip())
    return Path(__file__).parent.parent.parent.parent.parent


@click.group(name='release')
def release_group():
    """📦 Release and version management"""
    pass


@release_group.command(name='info')
def release_info():
    """Show detailed version information"""
    from core.version import (
        __version__, __build__, parse_build_timestamp, get_archive_name,
        FEATURES, VERSION_CODENAME, RELEASE_DATE, RELEASE_TYPE
    )

    click.echo(click.style(f'v{__version__}+build.{__build__}', fg='cyan', bold=True))
    click.echo(click.style(f'{VERSION_CODENAME.lower()} · {RELEASE_TYPE.lower()} · {RELEASE_DATE}', dim=True))
    click.echo()

    build_info = parse_build_timestamp(__build__)
    if build_info:
        click.echo(f"built: {build_info['date']} {build_info['time']}")
        click.echo()

    click.echo(f"archive: {get_archive_name()}")
    click.echo()

    click.echo("features:")
    for feature, enabled in FEATURES.items():
        status = click.style("✓", fg='green') if enabled else click.style("·", dim=True)
        click.echo(f"  {status} {feature}")


@release_group.command(name='run')
@click.argument('release_type', type=click.Choice(['build', 'patch', 'minor', 'major']), default='build')
@click.option('--message', '-m', default='', help='Custom commit message')
@click.option('--dry-run', is_flag=True, help='Simulate without executing')
@click.option('--repos', '-r', multiple=True, default=['dev', 'hub', 'manager', 'node', 'worker'],
              help='Repositories to push to')
def release_run(release_type, message, dry_run, repos):
    """Run release pipeline

    Release types:
      build  - New timestamp only (same version)
      patch  - Bug fix release (x.y.Z)
      minor  - Feature release (x.Y.0)
      major  - Breaking change (X.0.0)

    Examples:
      unibos-dev release run build
      unibos-dev release run minor -m "feat: new feature"
      unibos-dev release run patch --dry-run
    """
    from core.profiles.dev.release_pipeline import ReleasePipeline, PipelineStep

    # Map 'build' to 'daily' for pipeline
    pipeline_type = 'daily' if release_type == 'build' else release_type

    pipeline = ReleasePipeline()
    new_version = pipeline.calculate_new_version(pipeline_type)
    new_build = pipeline.get_new_build()

    click.echo(click.style(f'🚀 releasing v{new_version}+build.{new_build}', fg='cyan', bold=True))
    click.echo()

    if dry_run:
        click.echo(click.style('  [dry run mode - no changes will be made]', fg='yellow'))
        click.echo()

    # Progress callback
    def on_step_start(step: PipelineStep):
        click.echo(f"  ◦ {step.name}...", nl=False)

    def on_step_complete(step: PipelineStep):
        if step.status == "success":
            click.echo(click.style(" ✓", fg='green'))
        elif step.status == "failed":
            click.echo(click.style(f" ✗ {step.message}", fg='red'))
        elif step.status == "skipped":
            click.echo(click.style(" (skipped)", dim=True))

    def on_progress(msg: str):
        pass  # Suppress detailed progress in CLI

    # Set callbacks
    pipeline.on_step_start = on_step_start
    pipeline.on_step_complete = on_step_complete
    pipeline.on_progress = on_progress

    # Run pipeline
    result = pipeline.run(
        release_type=pipeline_type,
        message=message or f"chore: release v{new_version}",
        repos=list(repos),
        dry_run=dry_run
    )

    click.echo()

    if result.success:
        click.echo(click.style(f'✅ released v{result.version}+build.{result.build}', fg='green', bold=True))
        click.echo(click.style(f'   completed in {result.duration:.1f}s', dim=True))
        if result.archive_path:
            archive_name = Path(result.archive_path).name
            click.echo(click.style(f'   archive: {archive_name}', dim=True))
    else:
        click.echo(click.style(f'❌ release failed: {result.error}', fg='red'))
        sys.exit(1)


@release_group.command(name='archives')
@click.option('--limit', '-n', default=15, help='Number of archives to show')
@click.option('--json', 'as_json', is_flag=True, help='Output as JSON')
def release_archives(limit, as_json):
    """Browse version archives"""
    archive_dir = get_project_root() / "archive" / "versions"

    if not archive_dir.exists():
        click.echo(click.style(f'⚠️  archive directory not found: {archive_dir}', fg='yellow'))
        sys.exit(1)

    archives = []

    for item in sorted(archive_dir.iterdir(), reverse=True):
        if item.is_dir():
            archive_info = {
                'path': str(item),
                'name': item.name,
                'version': 'unknown',
                'build': None,
                'date': None,
                'format': 'unknown'
            }

            # Try to read VERSION.json
            version_file = item / 'VERSION.json'
            if version_file.exists():
                try:
                    with open(version_file) as f:
                        data = json.load(f)

                        if 'version' in data and isinstance(data['version'], dict):
                            v = data['version']
                            archive_info['version'] = f"{v.get('major', 0)}.{v.get('minor', 0)}.{v.get('patch', 0)}"
                            archive_info['build'] = v.get('build')
                            archive_info['format'] = 'new'
                            if 'build_info' in data:
                                archive_info['date'] = data['build_info'].get('date')
                        else:
                            archive_info['version'] = data.get('version', 'unknown')
                            archive_info['build'] = data.get('build_number') or data.get('build')
                            archive_info['date'] = data.get('release_date', '')[:10] if data.get('release_date') else None
                            archive_info['format'] = 'old'
                except:
                    pass

            # Parse from directory name if not found
            if archive_info['version'] == 'unknown':
                new_match = re.match(r'unibos_v(\d+\.\d+\.\d+)_b(\d{14})', item.name)
                if new_match:
                    archive_info['version'] = new_match.group(1)
                    archive_info['build'] = new_match.group(2)
                    archive_info['format'] = 'new'
                else:
                    old_match = re.match(r'unibos_v(\d+)_(\d{8})', item.name)
                    if old_match:
                        archive_info['version'] = f"0.{old_match.group(1)}.0"
                        archive_info['date'] = f"{old_match.group(2)[:4]}-{old_match.group(2)[4:6]}-{old_match.group(2)[6:8]}"
                        archive_info['format'] = 'old'

            archives.append(archive_info)

    if as_json:
        click.echo(json.dumps(archives[:limit], indent=2))
        return

    click.echo(click.style(f'{len(archives)} archives', fg='cyan', bold=True))
    click.echo()

    if archives:
        for archive in archives[:limit]:
            if archive['format'] == 'new' and archive['build']:
                b = archive['build']
                if len(b) == 14:
                    date_str = f"{b[0:4]}-{b[4:6]}-{b[6:8]} {b[8:10]}:{b[10:12]}"
                else:
                    date_str = f"b{archive['build']}"
            else:
                date_str = archive['date'] or ''

            click.echo(f"  v{archive['version']:8} · {date_str}")

        if len(archives) > limit:
            click.echo()
            click.echo(click.style(f"  +{len(archives) - limit} more (use --limit to show more)", dim=True))
    else:
        click.echo("  no archives found")


@release_group.command(name='analyze')
def release_analyze():
    """Analyze archive statistics"""
    archive_dir = get_project_root() / "archive" / "versions"

    def format_size(size):
        if size >= 1024 * 1024 * 1024:
            return f"{size / (1024*1024*1024):.1f}gb"
        elif size >= 1024 * 1024:
            return f"{size / (1024*1024):.1f}mb"
        elif size >= 1024:
            return f"{size / 1024:.1f}kb"
        return f"{size}b"

    if not archive_dir.exists():
        click.echo(click.style(f'⚠️  archive directory not found', fg='yellow'))
        sys.exit(1)

    total_size = 0
    sizes = []

    click.echo(click.style('📈 analyzing archives...', dim=True))

    for item in archive_dir.iterdir():
        if item.is_dir():
            dir_size = sum(f.stat().st_size for f in item.rglob('*') if f.is_file())
            total_size += dir_size
            sizes.append((item.name, dir_size))

    click.echo()
    click.echo(click.style(f'{len(sizes)} archives · {format_size(total_size)} total', fg='cyan', bold=True))
    click.echo()

    if sizes:
        avg_size = total_size / len(sizes)
        click.echo(f"average: {format_size(int(avg_size))}")
        click.echo()

        sizes.sort(key=lambda x: x[1], reverse=True)
        click.echo("largest archives:")
        for name, size in sizes[:5]:
            short_name = name[:40] + "..." if len(name) > 43 else name
            click.echo(f"  {format_size(size):>8}  {short_name}")

        anomalies = [s for s in sizes if s[1] > avg_size * 2]
        if anomalies:
            click.echo()
            click.echo(click.style(f"⚠ {len(anomalies)} anomalies (>2x average size)", fg='yellow'))


@release_group.command(name='current')
def release_current():
    """Show current version (short format)"""
    from core.version import __version__, __build__
    click.echo(f"v{__version__}+build.{__build__}")
