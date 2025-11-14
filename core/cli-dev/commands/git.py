#!/usr/bin/env python3
"""
UNIBOS CLI - Git Management Commands
Handles dev/prod git repository operations

Related Documentation:
- docs/guides/development.md - Development workflow
- .prodignore - Production exclusion patterns
"""

import click
import subprocess
import sys
from pathlib import Path
from typing import Optional


def run_command(cmd: list, cwd: Optional[Path] = None, check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=check
        )
        return result
    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Command failed: {' '.join(cmd)}", err=True)
        click.echo(f"   Error: {e.stderr}", err=True)
        sys.exit(1)


def get_project_root() -> Path:
    """Get the project root directory (git repository root)"""
    # Use git to find repository root (works from anywhere in the repo)
    result = subprocess.run(
        ['git', 'rev-parse', '--show-toplevel'],
        capture_output=True,
        text=True,
        check=False
    )
    if result.returncode == 0:
        return Path(result.stdout.strip())
    # Fallback to __file__ based path (for development)
    return Path(__file__).parent.parent.parent.parent


def check_git_status() -> bool:
    """Check if working directory is clean"""
    result = run_command(['git', 'status', '--porcelain'], check=False)
    if result.stdout.strip():
        click.echo("⚠️  Warning: Working directory has uncommitted changes")
        click.echo(result.stdout)
        if not click.confirm("Continue anyway?", default=False):
            return False
    return True


def check_remote_exists(remote: str) -> bool:
    """Check if a git remote exists"""
    result = run_command(['git', 'remote'], check=False)
    return remote in result.stdout.split('\n')


def verify_no_sensitive_files() -> bool:
    """Verify no sensitive files are tracked in git before prod push

    This function checks for patterns that should NEVER be in production:
    - archive/ directories (except allowed planning/ and docs/)
    - data/ directories (runtime data, backups, databases)
    - Large SQL files (database backups)
    - Environment files (.env, secrets)

    Returns:
        bool: True if safe to push, False if sensitive files detected
    """
    # Critical patterns that must not be in git
    sensitive_patterns = [
        ('archive/versions/', 'Version archives'),
        ('archive/code/', 'Archived code'),
        ('archive/data/', 'Archived data'),
        ('archive/database/', 'Database archives'),
        ('data/', 'Runtime data'),
        ('*.sql', 'SQL database files'),
        ('*.db', 'SQLite database files'),
        ('.env', 'Environment files')
    ]

    issues_found = False

    for pattern, description in sensitive_patterns:
        result = run_command(['git', 'ls-files', pattern], check=False)
        if result.stdout.strip():
            if not issues_found:
                click.echo("\n❌ CRITICAL: Sensitive files detected in git!\n", err=True)
                issues_found = True

            # Count files
            files = result.stdout.strip().split('\n')
            count = len(files)

            click.echo(f"   ⚠️  {description}: {count} file(s)", err=True)
            # Show first 3 files as examples
            for file in files[:3]:
                click.echo(f"      - {file}", err=True)
            if count > 3:
                click.echo(f"      ... and {count - 3} more", err=True)

    if issues_found:
        click.echo("\n💡 These files should be removed from git before production push.", err=True)
        click.echo("   Use: git rm --cached <file>  (keeps file on disk)\n", err=True)
        return False

    return True


@click.group()
def git_group():
    """🔀 Git repository management (dev/prod)

    Manage development and production git repositories.

    Examples:
        unibos git push-dev              # Push to dev repo
        unibos git push-prod             # Push to prod repo (filtered)
        unibos git status                # Show git status for both repos
        unibos git setup                 # Setup git remotes
    """
    pass


@git_group.command('status')
def git_status():
    """Show git status for dev and prod repositories"""
    click.echo("📊 Git Status\n")

    # Check current branch
    result = run_command(['git', 'branch', '--show-current'])
    current_branch = result.stdout.strip()
    click.echo(f"   Current branch: {current_branch}")

    # Check remotes
    click.echo("\n   Remotes:")
    result = run_command(['git', 'remote', '-v'])
    for line in result.stdout.strip().split('\n'):
        if line:
            click.echo(f"   {line}")

    # Check status
    click.echo("\n   Status:")
    result = run_command(['git', 'status', '--short'])
    if result.stdout.strip():
        click.echo(result.stdout)
    else:
        click.echo("   ✅ Working directory clean")

    # Check unpushed commits
    if check_remote_exists('origin'):
        result = run_command(['git', 'log', f'origin/{current_branch}..HEAD', '--oneline'], check=False)
        if result.stdout.strip():
            click.echo(f"\n   📤 Unpushed commits to origin:")
            for line in result.stdout.strip().split('\n'):
                click.echo(f"      {line}")

    if check_remote_exists('prod'):
        result = run_command(['git', 'log', f'prod/main..HEAD', '--oneline'], check=False)
        if result.returncode == 0 and result.stdout.strip():
            click.echo(f"\n   📤 Unpushed commits to prod:")
            for line in result.stdout.strip().split('\n'):
                click.echo(f"      {line}")


@git_group.command('setup')
@click.option('--force', is_flag=True, help='Force setup even if remotes exist')
def git_setup(force):
    """Setup git remotes for dev and prod repositories"""
    click.echo("🔧 Setting up git remotes\n")

    dev_url = "https://github.com/unibosoft/unibos_dev.git"
    prod_url = "https://github.com/unibosoft/unibos.git"

    # Check if remotes exist
    origin_exists = check_remote_exists('origin')
    prod_exists = check_remote_exists('prod')

    # Setup origin (dev)
    if origin_exists and not force:
        click.echo(f"   ℹ️  Remote 'origin' already exists")
        result = run_command(['git', 'remote', 'get-url', 'origin'])
        click.echo(f"      URL: {result.stdout.strip()}")
    else:
        if origin_exists:
            click.echo(f"   🔄 Updating remote 'origin'")
            run_command(['git', 'remote', 'set-url', 'origin', dev_url])
        else:
            click.echo(f"   ➕ Adding remote 'origin' (dev)")
            run_command(['git', 'remote', 'add', 'origin', dev_url])
        click.echo(f"      URL: {dev_url}")

    # Setup prod
    if prod_exists and not force:
        click.echo(f"\n   ℹ️  Remote 'prod' already exists")
        result = run_command(['git', 'remote', 'get-url', 'prod'])
        click.echo(f"      URL: {result.stdout.strip()}")
    else:
        if prod_exists:
            click.echo(f"\n   🔄 Updating remote 'prod'")
            run_command(['git', 'remote', 'set-url', 'prod', prod_url])
        else:
            click.echo(f"\n   ➕ Adding remote 'prod'")
            run_command(['git', 'remote', 'add', 'prod', prod_url])
        click.echo(f"      URL: {prod_url}")

    click.echo("\n✅ Git remotes configured successfully")


@git_group.command('push-dev')
@click.option('--force', '-f', is_flag=True, help='Force push (use with caution)')
@click.option('--branch', '-b', help='Branch to push (default: current branch)')
def push_dev(force, branch):
    """Push current branch to development repository (origin)"""
    click.echo("📤 Pushing to development repository\n")

    # Get current branch
    result = run_command(['git', 'branch', '--show-current'])
    current_branch = branch or result.stdout.strip()

    if not current_branch:
        click.echo("❌ Not on any branch", err=True)
        sys.exit(1)

    # Check status
    if not check_git_status():
        sys.exit(1)

    # Check if remote exists
    if not check_remote_exists('origin'):
        click.echo("❌ Remote 'origin' not found. Run 'unibos git setup' first.", err=True)
        sys.exit(1)

    # Push to main branch
    cmd = ['git', 'push']
    if force:
        cmd.append('--force')
        click.echo("   ⚠️  Force push enabled")
    cmd.extend(['origin', current_branch])

    click.echo(f"   Pushing branch '{current_branch}' to origin...")
    result = run_command(cmd)

    if "Everything up-to-date" in result.stderr:
        click.echo("   ✅ Everything up-to-date")
    else:
        click.echo("   ✅ Pushed successfully")

    # Also push to v533 branch
    click.echo(f"\n   Pushing to origin/v533...")
    cmd_v533 = ['git', 'push']
    if force:
        cmd_v533.append('--force')
    cmd_v533.extend(['origin', f'{current_branch}:v533'])

    result_v533 = run_command(cmd_v533)

    if "Everything up-to-date" in result_v533.stderr:
        click.echo("   ✅ v533 up-to-date")
    else:
        click.echo("   ✅ v533 pushed successfully")

    if result.stderr.strip():
        click.echo(f"\n{result.stderr}")


@git_group.command('push-prod')
@click.option('--dry-run', is_flag=True, help='Show what would be pushed without actually pushing')
@click.option('--force', '-f', is_flag=True, help='Force push (use with caution)')
def push_prod(dry_run, force):
    """Push to production repository (filtered with .prodignore)

    This command creates a filtered copy of the repository excluding
    development-only files (defined in .prodignore) and pushes to the
    prod remote.

    ⚠️  WARNING: This is a destructive operation for the prod repo.
    Use --dry-run first to verify changes.
    """
    click.echo("📤 Pushing to production repository\n")

    if dry_run:
        click.echo("   🔍 Dry-run mode: No changes will be made\n")

    project_root = get_project_root()
    prodignore = project_root / '.prodignore'

    # Check if .prodignore exists
    if not prodignore.exists():
        click.echo("❌ .prodignore file not found", err=True)
        sys.exit(1)

    # Check status
    if not check_git_status():
        sys.exit(1)

    # Check if remote exists
    if not check_remote_exists('prod'):
        click.echo("❌ Remote 'prod' not found. Run 'unibos git setup' first.", err=True)
        sys.exit(1)

    # CRITICAL: Verify no sensitive files in git
    click.echo("   🔍 Verifying no sensitive files in repository...")
    if not verify_no_sensitive_files():
        click.echo("\n❌ Aborting production push due to sensitive files.", err=True)
        click.echo("   Please clean up git repository before pushing to production.\n", err=True)
        sys.exit(1)
    click.echo("   ✅ Repository verification passed\n")

    # Get current commit
    result = run_command(['git', 'rev-parse', 'HEAD'])
    current_commit = result.stdout.strip()[:8]

    # Show warning
    click.echo("   ⚠️  This will push a filtered version to prod remote")
    click.echo(f"   📝 Current commit: {current_commit}")
    click.echo(f"   📋 Exclusion file: .prodignore")

    if dry_run:
        click.echo("\n   📊 Files that would be excluded:")
        # Show sample of excluded files
        result = run_command(['rsync', '-n', '-av', '--exclude-from=.prodignore',
                            '--include=*/', '--exclude=*', './', '/tmp/prod_dry_run/'],
                           check=False)
        click.echo("\n   ℹ️  Dry-run complete. Run without --dry-run to actually push.")
        return

    if not force:
        if not click.confirm("\n   Continue with production push?", default=False):
            click.echo("   ❌ Cancelled")
            sys.exit(0)

    # Create temporary prod branch
    temp_branch = f"prod-push-{current_commit}"
    click.echo(f"\n   🔄 Creating temporary branch: {temp_branch}")

    # Save current branch
    result = run_command(['git', 'branch', '--show-current'])
    original_branch = result.stdout.strip()

    try:
        # Create and checkout new branch
        run_command(['git', 'checkout', '-b', temp_branch])

        # Remove files according to .prodignore
        click.echo("   🗑️  Removing excluded files...")

        # Read .prodignore patterns
        with open(prodignore) as f:
            patterns = [line.strip() for line in f
                       if line.strip() and not line.strip().startswith('#')]

        # Remove each pattern
        for pattern in patterns:
            # Skip patterns that start with ! (keep patterns)
            if pattern.startswith('!'):
                continue

            # Use git rm for tracked files
            result = run_command(['git', 'rm', '-r', '--force', '--ignore-unmatch', pattern],
                               check=False)

        # Commit changes
        click.echo("   💾 Committing filtered tree...")
        # ⚠️ CRITICAL: DO NOT use 'git add -A' here!
        # 'git rm' already staged the deletions, 'git add -A' would re-add them from working directory
        # Just commit the staged changes (deletions only)
        run_command(['git', 'commit', '-m', f'Production build from {current_commit}',
                    '--allow-empty'])

        # Push to prod main
        cmd = ['git', 'push', 'prod', f'{temp_branch}:main']
        if force:
            cmd.append('--force')

        click.echo("   📤 Pushing to prod/main...")
        run_command(cmd)
        click.echo("   ✅ Pushed to prod/main")

        # Push to prod v533
        cmd_v533 = ['git', 'push', 'prod', f'{temp_branch}:v533']
        if force:
            cmd_v533.append('--force')

        click.echo("   📤 Pushing to prod/v533...")
        run_command(cmd_v533)
        click.echo("   ✅ Pushed to prod/v533")

        click.echo("\n✅ Successfully pushed to production repository (main and v533)")

    except Exception as e:
        click.echo(f"\n❌ Error during push: {e}", err=True)
        click.echo("   🔄 Cleaning up...")

    finally:
        # Always return to original branch and cleanup
        click.echo(f"\n   🔄 Returning to branch: {original_branch}")
        run_command(['git', 'checkout', original_branch])

        click.echo(f"   🗑️  Deleting temporary branch: {temp_branch}")
        run_command(['git', 'branch', '-D', temp_branch], check=False)


@git_group.command('sync-prod')
@click.option('--path', '-p',
              type=click.Path(exists=False, path_type=Path),
              default='/Users/berkhatirli/Applications/unibos',
              help='Path to prod installation directory')
@click.option('--dry-run', is_flag=True, help='Show what would be synced without actually syncing')
def sync_prod(path, dry_run):
    """Sync current code to local production directory (filtered)

    This command syncs the current codebase to a local production
    directory, excluding development-only files.

    Default path: /Users/berkhatirli/Applications/unibos
    """
    click.echo("🔄 Syncing to local production directory\n")

    if dry_run:
        click.echo("   🔍 Dry-run mode: No changes will be made\n")

    project_root = get_project_root()
    prodignore = project_root / '.prodignore'

    # Check if .prodignore exists
    if not prodignore.exists():
        click.echo("❌ .prodignore file not found", err=True)
        sys.exit(1)

    # Show info
    click.echo(f"   📂 Source: {project_root}")
    click.echo(f"   📂 Destination: {path}")
    click.echo(f"   📋 Exclusion file: .prodignore")

    # Create destination if it doesn't exist
    if not path.exists():
        if not dry_run:
            click.echo(f"\n   ➕ Creating directory: {path}")
            path.mkdir(parents=True, exist_ok=True)

    # Build rsync command
    cmd = ['rsync', '-av']
    if dry_run:
        cmd.append('--dry-run')
    cmd.extend([
        '--exclude-from=.prodignore',
        '--delete',  # Remove files in dest that don't exist in source
        './',
        f'{path}/'
    ])

    # Run rsync
    click.echo("\n   🔄 Syncing files...")
    result = run_command(cmd, cwd=project_root, check=False)

    if dry_run:
        # Show summary of what would be done
        lines = result.stdout.strip().split('\n')
        file_count = len([l for l in lines if l and not l.endswith('/')])
        dir_count = len([l for l in lines if l.endswith('/')])

        click.echo(f"\n   📊 Summary:")
        click.echo(f"      Files: {file_count}")
        click.echo(f"      Directories: {dir_count}")
        click.echo("\n   ℹ️  Dry-run complete. Run without --dry-run to actually sync.")
    else:
        # Show result
        if result.returncode == 0:
            click.echo("\n✅ Successfully synced to production directory")

            # Show size
            result = run_command(['du', '-sh', str(path)])
            size = result.stdout.split('\t')[0]
            click.echo(f"   📊 Production directory size: {size}")
        else:
            click.echo("\n❌ Sync failed", err=True)
            sys.exit(1)


# Export for main CLI
__all__ = ['git_group']
