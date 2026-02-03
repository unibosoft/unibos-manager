"""
UNIBOS Release Pipeline
Automated release workflow: archive + git + multi-repo push

Usage:
    from core.profiles.dev.release_pipeline import ReleasePipeline

    pipeline = ReleasePipeline()
    result = pipeline.run(release_type='minor', message='feat: new feature')
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Optional, Callable, Dict, Any


@dataclass
class PipelineStep:
    """A single step in the release pipeline"""
    id: str
    name: str
    status: str = "pending"  # pending, running, success, failed, skipped
    message: str = ""
    duration: float = 0.0


@dataclass
class PipelineResult:
    """Result of pipeline execution"""
    success: bool
    steps: List[PipelineStep]
    version: str
    build: str
    archive_path: Optional[str] = None
    error: Optional[str] = None
    duration: float = 0.0


class ReleasePipeline:
    """
    Self-hosted CI/CD pipeline for UNIBOS releases

    Release Types:
    - daily: Tag only (fast, no archive)
    - minor: Tag + Archive (standard release)
    - major: Tag + Archive + Branch (milestone)

    Repositories:
    - dev: Full codebase (development)
    - hub: Hub server deployment
    - manager: Manager tools
    - node: Node deployment (end user)
    - worker: Worker deployment (dedicated)
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or self._find_project_root()
        self.steps: List[PipelineStep] = []
        self.current_step: Optional[PipelineStep] = None

        # Callbacks for UI updates
        self.on_step_start: Optional[Callable[[PipelineStep], None]] = None
        self.on_step_complete: Optional[Callable[[PipelineStep], None]] = None
        self.on_progress: Optional[Callable[[str], None]] = None

    def _find_project_root(self) -> Path:
        """Find project root using git"""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--show-toplevel'],
                capture_output=True, text=True, check=True
            )
            return Path(result.stdout.strip())
        except:
            return Path(__file__).parent.parent.parent.parent

    def _log(self, message: str):
        """Log message and call progress callback"""
        if self.on_progress:
            self.on_progress(message)

    def _run_command(self, cmd: List[str], check: bool = True,
                     cwd: Optional[Path] = None) -> subprocess.CompletedProcess:
        """Run shell command"""
        return subprocess.run(
            cmd,
            cwd=cwd or self.project_root,
            capture_output=True,
            text=True,
            check=check
        )

    def get_current_version(self) -> tuple:
        """Get current version and build from core/version.py"""
        version_file = self.project_root / "core" / "version.py"

        version = "0.0.0"
        build = ""

        if version_file.exists():
            content = version_file.read_text()
            for line in content.split('\n'):
                if line.startswith('__version__'):
                    version = line.split('=')[1].strip().strip('"\'')
                elif line.startswith('__build__'):
                    build = line.split('=')[1].strip().strip('"\'')

        return version, build

    def get_new_build(self) -> str:
        """Generate new build timestamp"""
        return datetime.now().strftime("%Y%m%d%H%M%S")

    def calculate_new_version(self, release_type: str) -> str:
        """Calculate new version based on release type"""
        current_version, _ = self.get_current_version()
        parts = [int(x) for x in current_version.split('.')]

        if release_type == 'major':
            parts[0] += 1
            parts[1] = 0
            parts[2] = 0
        elif release_type == 'minor':
            parts[1] += 1
            parts[2] = 0
        elif release_type == 'patch':
            parts[2] += 1
        # 'daily' keeps same version, just new build

        return '.'.join(map(str, parts))

    def run(self, release_type: str = 'minor',
            message: str = '',
            repos: List[str] = None,
            skip_tests: bool = False,
            dry_run: bool = False) -> PipelineResult:
        """
        Run the release pipeline

        Args:
            release_type: 'daily', 'patch', 'minor', or 'major'
            message: Commit message
            repos: List of repos to push to ['dev', 'hub', 'manager', 'node', 'worker']
            skip_tests: Skip test execution
            dry_run: Don't actually execute, just simulate

        Returns:
            PipelineResult with success status and details
        """
        start_time = datetime.now()

        # Default repos
        if repos is None:
            repos = ['dev', 'hub', 'manager', 'node', 'worker']

        # Calculate version
        new_version = self.calculate_new_version(release_type)
        new_build = self.get_new_build()

        # Default message
        if not message:
            message = f"chore: release v{new_version}+build.{new_build}"

        # Initialize steps based on release type
        self.steps = self._get_pipeline_steps(release_type, repos)

        archive_path = None

        try:
            # Execute each step
            for step in self.steps:
                self.current_step = step
                step.status = "running"
                step_start = datetime.now()

                if self.on_step_start:
                    self.on_step_start(step)

                try:
                    if dry_run:
                        step.status = "skipped"
                        step.message = "dry run"
                    else:
                        # Execute step
                        if step.id == "update_changelog":
                            self._step_update_changelog(new_version, new_build)
                        elif step.id == "update_version":
                            self._step_update_version(new_version, new_build)
                        elif step.id == "create_archive":
                            archive_path = self._step_create_archive(new_version, new_build)
                        elif step.id == "git_commit":
                            self._step_git_commit(message)
                        elif step.id == "git_tag":
                            self._step_git_tag(new_version)
                        elif step.id == "git_branch":
                            self._step_git_branch(new_version, new_build)
                        elif step.id.startswith("push_"):
                            repo = step.id.replace("push_", "")
                            self._step_push_repo(repo, version=new_version, build=new_build)

                        step.status = "success"

                except Exception as e:
                    step.status = "failed"
                    step.message = str(e)
                    raise

                finally:
                    step.duration = (datetime.now() - step_start).total_seconds()
                    if self.on_step_complete:
                        self.on_step_complete(step)

            total_duration = (datetime.now() - start_time).total_seconds()

            return PipelineResult(
                success=True,
                steps=self.steps,
                version=new_version,
                build=new_build,
                archive_path=archive_path,
                duration=total_duration
            )

        except Exception as e:
            total_duration = (datetime.now() - start_time).total_seconds()

            return PipelineResult(
                success=False,
                steps=self.steps,
                version=new_version,
                build=new_build,
                archive_path=archive_path,
                error=str(e),
                duration=total_duration
            )

    def _get_pipeline_steps(self, release_type: str, repos: List[str]) -> List[PipelineStep]:
        """Get pipeline steps based on release type"""
        steps = []

        # Update changelog first (before version bump)
        steps.append(PipelineStep("update_changelog", "update changelog"))

        # Always update version
        steps.append(PipelineStep("update_version", "update version files"))

        # Archive for all release types (every build gets archived)
        steps.append(PipelineStep("create_archive", "create archive"))

        # Git operations
        steps.append(PipelineStep("git_commit", "git commit"))
        steps.append(PipelineStep("git_tag", "create git tag"))

        # Branch for major
        if release_type == 'major':
            steps.append(PipelineStep("git_branch", "create git branch"))

        # Push to repos
        for repo in repos:
            steps.append(PipelineStep(f"push_{repo}", f"push to {repo}"))

        return steps

    def _step_update_changelog(self, version: str, build: str):
        """Update CHANGELOG.md from Conventional Commits"""
        self._log("checking for changelog updates")

        try:
            from core.profiles.dev.changelog_manager import ChangelogManager

            manager = ChangelogManager(self.project_root)
            changes = manager.get_unreleased_changes()

            if changes:
                self._log(f"found {sum(len(v) for v in changes.values())} changes")
                manager.update_changelog(version, build)
                self._log("changelog updated")
            else:
                self._log("no conventional commits found, skipping changelog")

        except ImportError:
            self._log("changelog manager not available, skipping")
        except Exception as e:
            self._log(f"changelog update warning: {e}")
            # Don't fail the pipeline for changelog issues

    def _step_update_version(self, version: str, build: str):
        """Update VERSION.json and core/version.py"""
        self._log(f"updating to v{version}+build.{build}")

        # Update VERSION.json
        version_json = self.project_root / "VERSION.json"
        if version_json.exists():
            with open(version_json) as f:
                data = json.load(f)

            parts = [int(x) for x in version.split('.')]
            data['version'] = {
                'major': parts[0],
                'minor': parts[1],
                'patch': parts[2],
                'build': build
            }

            # Update display info to match current version
            build_date = build[:8]  # YYYYMMDD
            build_time = build[8:]  # HHMMSS
            short_date = f"{build_date[4:6]}{build_date[6:8]}"  # MMDD
            short_time = f"{build_time[:2]}{build_time[2:4]}"  # HHMM
            data['display'] = {
                'semantic': version,
                'full': f"{version}+build.{build}",
                'short': f"v{version} @{build_time[:2]}:{build_time[2:4]}",
                'compact': f"v{version} {short_date}@{short_time}",
                'archive': f"unibos_v{version}_b{build}"
            }

            data['build_info'] = {
                'date': datetime.now().strftime("%Y-%m-%d"),
                'time': datetime.now().strftime("%H:%M:%S"),
                'timestamp': build
            }

            with open(version_json, 'w') as f:
                json.dump(data, f, indent=2)

        # Update core/version.py
        version_py = self.project_root / "core" / "version.py"
        if version_py.exists():
            content = version_py.read_text()
            lines = content.split('\n')
            new_lines = []

            for line in lines:
                if line.startswith('__version__'):
                    new_lines.append(f'__version__ = "{version}"')
                elif line.startswith('__build__'):
                    new_lines.append(f'__build__ = "{build}"')
                elif line.startswith('__version_info__'):
                    parts = [int(x) for x in version.split('.')]
                    new_lines.append(f'__version_info__ = ({parts[0]}, {parts[1]}, {parts[2]})')
                else:
                    new_lines.append(line)

            version_py.write_text('\n'.join(new_lines))

    def _step_create_archive(self, version: str, build: str) -> str:
        """Create version archive"""
        archive_name = f"unibos_v{version}_b{build}"
        archive_dir = self.project_root / "archive" / "versions" / archive_name

        self._log(f"creating {archive_name}/")

        # Directories to completely exclude (won't be copied at all)
        exclude_dirs = {
            '.git',
            '__pycache__',
            'node_modules',
            'venv',
            '.venv',
            'dist',
            'build',
            '.pytest_cache',
            # Flutter/Mobile SDK directories
            '.dart_tool',
            'Pods',
            '.symlinks',
            'ephemeral',
            '.pub-cache',
            '.pub',
            '.gradle',
        }

        # Files to exclude
        exclude_files = {
            '.DS_Store',
            '.coverage',
            # Flutter/Mobile files
            '.flutter-plugins',
            '.flutter-plugins-dependencies',
            '.packages',
            'Podfile.lock',
            'local.properties',
            'Generated.xcconfig',
            'ServiceDefinitions.json',
            'flutter_export_environment.sh',
        }

        # File extensions to exclude
        exclude_extensions = {'.pyc', '.sql'}

        # Paths relative to project root to exclude
        exclude_paths = {
            'archive',  # Don't copy archive directory at all
            'data',     # Runtime data (logs, backups, cache, media)
            'data_db',  # Database files
            'core/clients/mobile',  # Mobile SDK source (development only)
        }

        def ignore_patterns(directory, files):
            ignored = []
            rel_dir = os.path.relpath(directory, self.project_root)

            for f in files:
                full_path = os.path.join(directory, f)
                rel_path = os.path.relpath(full_path, self.project_root)

                # Check if it's an excluded directory
                if f in exclude_dirs:
                    ignored.append(f)
                    continue

                # Check if it's an excluded file
                if f in exclude_files:
                    ignored.append(f)
                    continue

                # Check file extension
                if any(f.endswith(ext) for ext in exclude_extensions):
                    ignored.append(f)
                    continue

                # Check if path starts with excluded path
                if any(rel_path.startswith(ep) or rel_path == ep for ep in exclude_paths):
                    ignored.append(f)
                    continue

                # Check for .egg-info directories
                if f.endswith('.egg-info'):
                    ignored.append(f)
                    continue

            return ignored

        # Create archive
        shutil.copytree(
            self.project_root,
            archive_dir,
            ignore=ignore_patterns,
            dirs_exist_ok=False
        )

        # Create README
        readme = archive_dir / "README.txt"
        readme.write_text(
            f"v{version}+build.{build}\n"
            f"Archived: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        )

        return str(archive_dir)

    def _step_git_commit(self, message: str):
        """Git add and commit"""
        self._log("staging changes")
        self._run_command(['git', 'add', '-A'])

        self._log("creating commit")
        # Check if there are changes to commit
        result = self._run_command(['git', 'status', '--porcelain'], check=False)

        if result.stdout.strip():
            self._run_command(['git', 'commit', '-m', message])
        else:
            self._log("no changes to commit")

    def _step_git_tag(self, version: str):
        """Create git tag"""
        tag_name = f"v{version}"
        self._log(f"creating tag {tag_name}")

        # Delete tag if exists
        self._run_command(['git', 'tag', '-d', tag_name], check=False)

        # Create annotated tag
        self._run_command([
            'git', 'tag', '-a', tag_name,
            '-m', f'Release {tag_name}'
        ])

    def _step_git_branch(self, version: str, build: str = None):
        """Create git branch for major releases"""
        if build:
            branch_name = f"v{version}+build.{build}"
        else:
            branch_name = f"v{version}"
        self._log(f"creating branch {branch_name}")

        # Create branch from current HEAD
        self._run_command(['git', 'branch', '-f', branch_name], check=False)

    def _step_push_repo(self, repo: str, version: str = None, build: str = None):
        """Push to specific repository with correct gitignore"""
        self._log(f"pushing to {repo}")

        # Map repo to template
        templates = {
            'dev': '.gitignore.dev',
            'hub': '.gitignore.hub',
            'manager': '.gitignore.manager',
            'node': '.gitignore.node',
            'worker': '.gitignore.worker'
        }

        template = templates.get(repo)
        if not template:
            raise ValueError(f"Unknown repo: {repo}")

        template_path = self.project_root / template
        gitignore_path = self.project_root / '.gitignore'

        # Backup current gitignore
        original_gitignore = gitignore_path.read_text() if gitignore_path.exists() else ""

        try:
            # Copy template to .gitignore
            if template_path.exists():
                shutil.copy(template_path, gitignore_path)

            # Push main branch
            self._log(f"pushing main to {repo}")
            result = self._run_command(
                ['git', 'push', repo, 'main', '--force'],
                check=False
            )

            if result.returncode != 0:
                # Try without force
                result = self._run_command(
                    ['git', 'push', repo, 'main'],
                    check=False
                )

            if result.returncode != 0:
                raise Exception(f"Push main failed: {result.stderr}")

            # Push version+build branch (e.g., v1.0.0+build.20251201235836)
            if version and build:
                branch_name = f"v{version}+build.{build}"
                # Create or update the version branch
                self._run_command(['git', 'branch', '-f', branch_name], check=False)

                self._log(f"pushing {branch_name} to {repo}")
                result = self._run_command(
                    ['git', 'push', repo, branch_name, '--force'],
                    check=False
                )
                if result.returncode != 0:
                    self._log(f"warning: could not push {branch_name} to {repo}")

            # Push tags
            self._log(f"pushing tags to {repo}")
            self._run_command(['git', 'push', repo, '--tags', '--force'], check=False)

        finally:
            # Restore original gitignore
            gitignore_path.write_text(original_gitignore)


def run_release(release_type: str = 'minor',
                message: str = '',
                repos: List[str] = None,
                dry_run: bool = False) -> PipelineResult:
    """
    Convenience function to run release pipeline

    Usage:
        from core.profiles.dev.release_pipeline import run_release
        result = run_release('minor', 'feat: add new feature')
    """
    pipeline = ReleasePipeline()
    return pipeline.run(
        release_type=release_type,
        message=message,
        repos=repos,
        dry_run=dry_run
    )
