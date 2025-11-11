#!/usr/bin/env python3
"""
UNIBOS Git Versioning Tool
Ensures both main and vXXX branches are created and pushed
"""

import json
import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime
import argparse

# ANSI color codes
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
CYAN = '\033[0;36m'
NC = '\033[0m'  # No Color


def print_colored(message, color=NC):
    """Print colored message"""
    print(f"{color}{message}{NC}")


def run_command(cmd, capture=True):
    """Run a shell command and return output"""
    try:
        if capture:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                return None, result.stderr
            return result.stdout.strip(), None
        else:
            result = subprocess.run(cmd, shell=True)
            return None, None if result.returncode == 0 else "Command failed"
    except Exception as e:
        return None, str(e)


def get_version_from_json():
    """Extract version from VERSION.json"""
    paths = [
        Path("src/VERSION.json"),
        Path("../src/VERSION.json"),
        Path("../../src/VERSION.json")
    ]
    
    for path in paths:
        if path.exists():
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                    return data.get('version', '')
            except Exception:
                pass
    return None


def check_git_status():
    """Check if there are uncommitted changes"""
    output, error = run_command("git status --porcelain")
    if error:
        return False, error
    return len(output) > 0 if output else False, None


def cleanup_old_comm_logs():
    """Keep only the 3 most recent communication logs"""
    import glob
    
    print_colored("\n🧹 Cleaning up old communication logs...", CYAN)
    
    # Find all communication log files
    comm_logs = glob.glob('CLAUDE_COMMUNICATION_LOG_*.md')
    
    if len(comm_logs) > 3:
        # Sort by modification time
        comm_logs.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        
        # Delete older logs
        for old_log in comm_logs[3:]:
            try:
                os.remove(old_log)
                print_colored(f"   ✓ Deleted old log: {old_log}", YELLOW)
            except Exception as e:
                print_colored(f"   ✗ Failed to delete {old_log}: {e}", RED)
    else:
        print_colored(f"   ℹ Found {len(comm_logs)} logs, no cleanup needed", CYAN)


def create_and_push_version(version, message, auto_confirm=False):
    """Create version and push to both main and vXXX branches"""
    
    print_colored(f"\n📦 Creating version: {version}", GREEN)
    print_colored(f"📝 Commit message: {message}", YELLOW)
    
    if not auto_confirm:
        confirm = input(f"\n{YELLOW}Proceed with versioning? (y/n): {NC}")
        if confirm.lower() != 'y':
            print_colored("❌ Versioning cancelled", RED)
            return False
    
    # Step 1: Stage all changes
    print_colored("\n1️⃣  Staging all changes...", YELLOW)
    _, error = run_command("git add -A", capture=False)
    if error:
        print_colored(f"❌ Failed to stage changes: {error}", RED)
        return False
    
    # Step 2: Commit changes
    print_colored("2️⃣  Committing changes...", YELLOW)
    commit_msg = f"{version}: {message}"
    _, error = run_command(f'git commit -m "{commit_msg}"', capture=False)
    if error and "nothing to commit" not in str(error):
        print_colored("⚠️  No changes to commit", YELLOW)
        # Continue anyway to ensure branches are in sync
    
    # Step 3: Push to main
    print_colored("3️⃣  Pushing to main branch...", YELLOW)
    _, error = run_command("git push origin main", capture=False)
    if error:
        print_colored(f"❌ Failed to push to main: {error}", RED)
        return False
    
    # Step 4: Handle version branch
    print_colored(f"4️⃣  Creating/updating {version} branch...", YELLOW)
    
    # Check if branch exists locally
    branch_exists, _ = run_command(f"git show-ref --verify refs/heads/{version}")
    
    if branch_exists:
        print_colored(f"   Branch {version} exists, updating...", CYAN)
        _, error = run_command(f"git checkout {version}", capture=False)
        if not error:
            run_command("git merge main --no-edit", capture=False)
    else:
        print_colored(f"   Creating new branch {version}...", CYAN)
        _, error = run_command(f"git checkout -b {version}", capture=False)
    
    if error:
        print_colored(f"❌ Failed to create/update {version} branch: {error}", RED)
        run_command("git checkout main", capture=False)
        return False
    
    # Step 5: Push version branch
    print_colored(f"5️⃣  Pushing {version} branch to remote...", YELLOW)
    _, error = run_command(f"git push origin {version}", capture=False)
    if error:
        print_colored(f"❌ Failed to push {version} branch: {error}", RED)
        run_command("git checkout main", capture=False)
        return False
    
    # Step 6: Return to main
    print_colored("6️⃣  Returning to main branch...", YELLOW)
    run_command("git checkout main", capture=False)
    
    # Step 7: Cleanup old communication logs
    cleanup_old_comm_logs()
    
    # Success message
    print_colored(f"\n✅ Version {version} successfully created and pushed!", GREEN)
    print_colored("   ✓ main branch: updated", GREEN)
    print_colored(f"   ✓ {version} branch: created/updated", GREEN)
    
    # Show GitHub URLs
    remote_url, _ = run_command("git config --get remote.origin.url")
    if remote_url and "github.com" in remote_url:
        repo_path = remote_url.replace("git@github.com:", "").replace("https://github.com/", "").replace(".git", "")
        print_colored(f"\n🔗 GitHub Links:", CYAN)
        print_colored(f"   Main: https://github.com/{repo_path}/tree/main", CYAN)
        print_colored(f"   {version}: https://github.com/{repo_path}/tree/{version}", CYAN)
    
    return True


def update_version_json(version, description):
    """Update VERSION.json with new version info"""
    paths = [
        Path("src/VERSION.json"),
        Path("../src/VERSION.json"),
        Path("../../src/VERSION.json")
    ]
    
    for path in paths:
        if path.exists():
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                
                # Update version info
                data['version'] = version
                data['build_number'] = datetime.now().strftime("%Y%m%d_%H%M")
                data['release_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S +03:00")
                data['description'] = description
                
                with open(path, 'w') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                print_colored(f"✓ Updated {path}", GREEN)
                return True
            except Exception as e:
                print_colored(f"❌ Failed to update {path}: {e}", RED)
    return False


def main():
    """Main execution"""
    parser = argparse.ArgumentParser(description='UNIBOS Git Versioning Tool')
    parser.add_argument('version', nargs='?', help='Version number (e.g., v395)')
    parser.add_argument('message', nargs='?', help='Commit message')
    parser.add_argument('--auto', action='store_true', help='Auto-confirm without prompting')
    parser.add_argument('--update-json', action='store_true', help='Update VERSION.json automatically')
    
    args = parser.parse_args()
    
    print_colored("🚀 UNIBOS Git Versioning Tool", GREEN)
    print_colored("=" * 40, GREEN)
    
    # Check if in git repository
    _, error = run_command("git rev-parse --git-dir")
    if error:
        print_colored("❌ Error: Not in a git repository", RED)
        sys.exit(1)
    
    # Get version
    version = args.version
    if not version:
        version = get_version_from_json()
        if not version:
            print_colored("❌ Error: Could not find version in VERSION.json", RED)
            print_colored("Usage: git_version.py <version> <message>", YELLOW)
            print_colored("Example: git_version.py v395 \"Fixed authentication bug\"", YELLOW)
            sys.exit(1)
    
    # Get commit message
    message = args.message
    if not message:
        has_changes, _ = check_git_status()
        if has_changes:
            print_colored(f"\n📝 Enter commit message for {version}:", YELLOW)
            message = input("> ")
        else:
            message = "Version sync"
    
    if not message:
        print_colored("❌ Error: Commit message is required", RED)
        sys.exit(1)
    
    # Update VERSION.json if requested
    if args.update_json:
        print_colored("\n📄 Updating VERSION.json...", YELLOW)
        update_version_json(version, message)
    
    # Create and push version
    success = create_and_push_version(version, message, args.auto)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()