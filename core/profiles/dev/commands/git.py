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
    click.echo("📊 git status\n")

    # Check current branch
    result = run_command(['git', 'branch', '--show-current'])
    current_branch = result.stdout.strip()
    click.echo(f"   current branch: {current_branch}")

    # Check remotes
    click.echo("\n   remotes:")
    result = run_command(['git', 'remote', '-v'])
    for line in result.stdout.strip().split('\n'):
        if line:
            click.echo(f"   {line}")

    # Check status
    click.echo("\n   status:")
    result = run_command(['git', 'status', '--short'])
    if result.stdout.strip():
        click.echo(result.stdout)
    else:
        click.echo("   ✅ working directory clean")

    # Check unpushed commits
    if check_remote_exists('origin'):
        result = run_command(['git', 'log', f'origin/{current_branch}..HEAD', '--oneline'], check=False)
        if result.stdout.strip():
            click.echo(f"\n   📤 unpushed commits to origin:")
            for line in result.stdout.strip().split('\n'):
                click.echo(f"      {line}")

    if check_remote_exists('prod'):
        result = run_command(['git', 'log', f'prod/main..HEAD', '--oneline'], check=False)
        if result.returncode == 0 and result.stdout.strip():
            click.echo(f"\n   📤 unpushed commits to prod:")
            for line in result.stdout.strip().split('\n'):
                click.echo(f"      {line}")


@git_group.command('setup')
@click.option('--force', is_flag=True, help='Force setup even if remotes exist')
def git_setup(force):
    """Setup git remotes for dev, server, and prod repositories (3-repo architecture)"""
    click.echo("🔧 setting up git remotes (3-repo architecture)\n")

    dev_url = "https://github.com/unibosoft/unibos-dev.git"
    server_url = "https://github.com/unibosoft/unibos-server.git"
    prod_url = "https://github.com/unibosoft/unibos.git"

    # Check if remotes exist
    dev_exists = check_remote_exists('dev')
    server_exists = check_remote_exists('server')
    prod_exists = check_remote_exists('prod')

    # Setup dev
    if dev_exists and not force:
        click.echo(f"   ℹ️  remote 'dev' already exists")
        result = run_command(['git', 'remote', 'get-url', 'dev'])
        click.echo(f"      url: {result.stdout.strip()}")
    else:
        if dev_exists:
            click.echo(f"   🔄 updating remote 'dev'")
            run_command(['git', 'remote', 'set-url', 'dev', dev_url])
        else:
            click.echo(f"   ➕ adding remote 'dev' (development)")
            run_command(['git', 'remote', 'add', 'dev', dev_url])
        click.echo(f"      url: {dev_url}")

    # Setup server
    if server_exists and not force:
        click.echo(f"\n   ℹ️  remote 'server' already exists")
        result = run_command(['git', 'remote', 'get-url', 'server'])
        click.echo(f"      url: {result.stdout.strip()}")
    else:
        if server_exists:
            click.echo(f"\n   🔄 updating remote 'server'")
            run_command(['git', 'remote', 'set-url', 'server', server_url])
        else:
            click.echo(f"\n   ➕ adding remote 'server' (production server)")
            run_command(['git', 'remote', 'add', 'server', server_url])
        click.echo(f"      url: {server_url}")

    # Setup prod
    if prod_exists and not force:
        click.echo(f"\n   ℹ️  remote 'prod' already exists")
        result = run_command(['git', 'remote', 'get-url', 'prod'])
        click.echo(f"      url: {result.stdout.strip()}")
    else:
        if prod_exists:
            click.echo(f"\n   🔄 updating remote 'prod'")
            run_command(['git', 'remote', 'set-url', 'prod', prod_url])
        else:
            click.echo(f"\n   ➕ adding remote 'prod' (production nodes)")
            run_command(['git', 'remote', 'add', 'prod', prod_url])
        click.echo(f"      url: {prod_url}")

    click.echo("\n✅ git remotes configured successfully (3 repositories)")


@git_group.command('push-dev')
@click.option('--force', '-f', is_flag=True, help='Force push (use with caution)')
@click.option('--branch', '-b', help='Branch to push (default: current branch)')
def push_dev(force, branch):
    """Push current branch to development repository (origin)"""
    click.echo("📤 pushing to development repository\n")

    # Get current branch
    result = run_command(['git', 'branch', '--show-current'])
    current_branch = branch or result.stdout.strip()

    if not current_branch:
        click.echo("❌ not on any branch", err=True)
        sys.exit(1)

    # Check status
    if not check_git_status():
        sys.exit(1)

    # Check if remote exists
    if not check_remote_exists('origin'):
        click.echo("❌ remote 'origin' not found. run 'unibos git setup' first.", err=True)
        sys.exit(1)

    # Push to main branch
    cmd = ['git', 'push']
    if force:
        cmd.append('--force')
        click.echo("   ⚠️  force push enabled")
    cmd.extend(['origin', current_branch])

    click.echo(f"   pushing branch '{current_branch}' to origin...")
    result = run_command(cmd)

    if "Everything up-to-date" in result.stderr:
        click.echo("   ✅ everything up-to-date")
    else:
        click.echo("   ✅ pushed successfully")

    # Also push to v533 branch
    click.echo(f"\n   pushing to origin/v533...")
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
    click.echo("📤 pushing to production repository\n")

    if dry_run:
        click.echo("   🔍 dry-run mode: no changes will be made\n")

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
        click.echo("❌ remote 'prod' not found. run 'unibos git setup' first.", err=True)
        sys.exit(1)

    # CRITICAL: Verify no sensitive files in git
    click.echo("   🔍 verifying no sensitive files in repository...")
    if not verify_no_sensitive_files():
        click.echo("\n❌ aborting production push due to sensitive files.", err=True)
        click.echo("   please clean up git repository before pushing to production.\n", err=True)
        sys.exit(1)
    click.echo("   ✅ repository verification passed\n")

    # Get current commit
    result = run_command(['git', 'rev-parse', 'HEAD'])
    current_commit = result.stdout.strip()[:8]

    # Show warning
    click.echo("   ⚠️  this will push a filtered version to prod remote")
    click.echo(f"   📝 current commit: {current_commit}")
    click.echo(f"   📋 exclusion file: .prodignore")

    if dry_run:
        click.echo("\n   📊 files that would be excluded:")
        # Show sample of excluded files
        result = run_command(['rsync', '-n', '-av', '--exclude-from=.prodignore',
                            '--include=*/', '--exclude=*', './', '/tmp/prod_dry_run/'],
                           check=False)
        click.echo("\n   ℹ️  dry-run complete. run without --dry-run to actually push.")
        return

    if not force:
        if not click.confirm("\n   continue with production push?", default=False):
            click.echo("   ❌ cancelled")
            sys.exit(0)

    # Create temporary prod branch
    temp_branch = f"prod-push-{current_commit}"
    click.echo(f"\n   🔄 creating temporary branch: {temp_branch}")

    # Save current branch
    result = run_command(['git', 'branch', '--show-current'])
    original_branch = result.stdout.strip()

    try:
        # Create and checkout new branch
        run_command(['git', 'checkout', '-b', temp_branch])

        # Remove files according to .prodignore
        click.echo("   🗑️  removing excluded files...")

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
        click.echo("   💾 committing filtered tree...")
        # ⚠️ CRITICAL: DO NOT use 'git add -A' here!
        # 'git rm' already staged the deletions, 'git add -A' would re-add them from working directory
        # Just commit the staged changes (deletions only)
        run_command(['git', 'commit', '-m', f'production build from {current_commit}',
                    '--allow-empty'])

        # Push to prod main
        cmd = ['git', 'push', 'prod', f'{temp_branch}:main']
        if force:
            cmd.append('--force')

        click.echo("   📤 pushing to prod/main...")
        run_command(cmd)
        click.echo("   ✅ pushed to prod/main")

        # Push to prod v533
        cmd_v533 = ['git', 'push', 'prod', f'{temp_branch}:v533']
        if force:
            cmd_v533.append('--force')

        click.echo("   📤 pushing to prod/v533...")
        run_command(cmd_v533)
        click.echo("   ✅ pushed to prod/v533")

        click.echo("\n✅ successfully pushed to production repository (main and v533)")

    except Exception as e:
        click.echo(f"\n❌ error during push: {e}", err=True)
        click.echo("   🔄 cleaning up...")

    finally:
        # Always return to original branch and cleanup
        click.echo(f"\n   🔄 returning to branch: {original_branch}")
        run_command(['git', 'checkout', original_branch])

        click.echo(f"   🗑️  deleting temporary branch: {temp_branch}")
        run_command(['git', 'branch', '-D', temp_branch], check=False)


@git_group.command('push-all')
@click.argument('message', required=False, default=None)
@click.option('--repos', '-r',
              type=click.Choice(['dev', 'server', 'manager', 'prod', 'all']),
              default='all',
              help='Which repositories to push to (default: all)')
@click.option('--dry-run', '-d', is_flag=True,
              help='Show what would be pushed without actually pushing')
def push_all(message, repos, dry_run):
    """
    Push to multiple repositories with correct .gitignore templates

    3-REPO ARCHITECTURE:
    - dev: All CLIs, all settings (development)
    - server: cli_server + cli_node, no cli_dev (production server)
    - prod: cli_node only, minimal (production nodes)

    USAGE:
        unibos-dev git push-all                    # Push existing commits
        unibos-dev git push-all "feat: feature"   # Commit and push
        unibos-dev git push-all --repos dev       # Push to dev only
        unibos-dev git push-all --dry-run         # Simulate

    This command:
    1. Optionally commits changes with provided message
    2. Pushes to each repo with appropriate .gitignore template
    3. Ensures security (cli_dev never goes to server/prod)
    """
    project_root = get_project_root()

    # Verify .gitignore templates exist
    templates = {
        'dev': project_root / '.gitignore.dev',
        'server': project_root / '.gitignore.server',
        'manager': project_root / '.gitignore.manager',
        'prod': project_root / '.gitignore.prod'
    }

    missing = [name for name, path in templates.items() if not path.exists()]
    if missing:
        click.echo(f"❌ error: missing .gitignore templates: {', '.join(missing)}", err=True)
        sys.exit(1)

    click.echo(f"{'🔍 dry run mode' if dry_run else '🚀 pushing to repositories'}")
    if message:
        click.echo(f"📝 commit message: {message}")
    else:
        click.echo("📝 pushing existing commits (no new commit)")
    click.echo("")

    # Determine which repos to push to
    repo_list = []
    if repos == 'all':
        repo_list = ['dev', 'server', 'manager', 'prod']
    else:
        repo_list = [repos]

    click.echo(f"📦 target repositories: {', '.join(repo_list)}")
    click.echo("")

    # Step 1: Ensure we're on main branch
    try:
        result = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                              capture_output=True, text=True, check=True)
        current_branch = result.stdout.strip()

        if current_branch != 'main':
            click.echo(f"⚠️  Warning: Currently on branch '{current_branch}'", err=True)
            if not dry_run and not click.confirm("Continue anyway?"):
                sys.exit(0)
    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Error checking git branch: {e}", err=True)
        sys.exit(1)

    # Step 2: Stage and commit changes (only if message provided)
    if message:
        click.echo("1️⃣  staging and committing changes...")
        if not dry_run:
            try:
                # Stage all changes
                subprocess.run(['git', 'add', '-A'], check=True)

                # Create commit
                subprocess.run(['git', 'commit', '-m', message], check=True)
                click.echo("   ✅ commit created")
            except subprocess.CalledProcessError as e:
                # Check if it's just "nothing to commit"
                if 'nothing to commit' in str(e):
                    click.echo("   ℹ️  no changes to commit, pushing existing commits")
                else:
                    click.echo(f"   ❌ commit failed: {e}", err=True)
                    sys.exit(1)
        else:
            click.echo("   [dry run] would create commit")
    else:
        click.echo("1️⃣  skipping commit (no message provided)")

    click.echo("")

    # Step 3: Push to each repository
    for i, repo in enumerate(repo_list, 1):
        _push_to_single_repo(repo, dry_run, project_root, i, len(repo_list))

    # Step 4: Restore dev .gitignore
    click.echo(f"{len(repo_list) + 1}️⃣  restoring .gitignore.dev as active...")
    if not dry_run:
        subprocess.run(['cp', str(templates['dev']), str(project_root / '.gitignore')], check=True)
        click.echo("   ✅ .gitignore restored to dev template")
    else:
        click.echo("   [dry run] would restore .gitignore.dev")

    click.echo("")
    click.echo("✅ done")
    click.echo("")
    click.echo("📊 summary:")
    for repo in repo_list:
        repo_name = 'unibos' if repo == 'prod' else f'unibos-{repo}'
        click.echo(f"   ✓ {repo:6s} → https://github.com/unibosoft/{repo_name}.git")


def _push_to_single_repo(repo, dry_run, root_dir, step_num, total_steps):
    """Helper function to push to a single repository with correct .gitignore"""

    # Map repo name to template and remote
    repo_config = {
        'dev': {
            'template': '.gitignore.dev',
            'remote': 'dev',
            'url': 'unibos-dev',
            'description': 'full codebase'
        },
        'server': {
            'template': '.gitignore.server',
            'remote': 'server',
            'url': 'unibos-server',
            'description': 'server + node'
        },
        'manager': {
            'template': '.gitignore.manager',
            'remote': 'manager',
            'url': 'unibos-manager',
            'description': 'manager tools'
        },
        'prod': {
            'template': '.gitignore.prod',
            'remote': 'prod',
            'url': 'unibos',
            'description': 'node only, minimal'
        }
    }

    config = repo_config[repo]

    click.echo(f"{step_num + 1}️⃣  pushing to {repo} repo ({config['description']})...")

    # Copy appropriate .gitignore
    if not dry_run:
        subprocess.run(['cp', str(root_dir / config['template']),
                       str(root_dir / '.gitignore')], check=True)
        click.echo(f"   ✅ {config['template']} activated")
    else:
        click.echo(f"   [dry run] would activate {config['template']}")

    # Push to remote
    if not dry_run:
        try:
            result = subprocess.run(
                ['git', 'push', config['remote'], 'main'],
                capture_output=True, text=True, check=True
            )
            if "Everything up-to-date" in result.stderr:
                click.echo(f"   ✅ already up-to-date")
            else:
                click.echo(f"   ✅ pushed to {config['url']}")
        except subprocess.CalledProcessError as e:
            click.echo(f"   ❌ push failed: {e.stderr}", err=True)
            click.echo(f"   continuing with other repositories...")
    else:
        click.echo(f"   [dry run] would push to {config['remote']}")

    click.echo("")


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
    click.echo("🔄 syncing to local production directory\n")

    if dry_run:
        click.echo("   🔍 dry-run mode: no changes will be made\n")

    project_root = get_project_root()
    prodignore = project_root / '.prodignore'

    # Check if .prodignore exists
    if not prodignore.exists():
        click.echo("❌ .prodignore file not found", err=True)
        sys.exit(1)

    # Show info
    click.echo(f"   📂 source: {project_root}")
    click.echo(f"   📂 destination: {path}")
    click.echo(f"   📋 exclusion file: .prodignore")

    # Create destination if it doesn't exist
    if not path.exists():
        if not dry_run:
            click.echo(f"\n   ➕ creating directory: {path}")
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
    click.echo("\n   🔄 syncing files...")
    result = run_command(cmd, cwd=project_root, check=False)

    if dry_run:
        # Show summary of what would be done
        lines = result.stdout.strip().split('\n')
        file_count = len([l for l in lines if l and not l.endswith('/')])
        dir_count = len([l for l in lines if l.endswith('/')])

        click.echo(f"\n   📊 summary:")
        click.echo(f"      files: {file_count}")
        click.echo(f"      directories: {dir_count}")
        click.echo("\n   ℹ️  dry-run complete. run without --dry-run to actually sync.")
    else:
        # Show result
        if result.returncode == 0:
            click.echo("\n✅ successfully synced to production directory")

            # Show size
            result = run_command(['du', '-sh', str(path)])
            size = result.stdout.split('\t')[0]
            click.echo(f"   📊 production directory size: {size}")
        else:
            click.echo("\n❌ sync failed", err=True)
            sys.exit(1)


# Export for main CLI
__all__ = ['git_group']
