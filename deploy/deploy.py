"""
unibos server deployer
handles complete server deployment lifecycle
"""

import subprocess
import datetime
from pathlib import Path
from typing import Optional, Callable, List
from dataclasses import dataclass, field

from deploy.config import DeployConfig


@dataclass
class DeployResult:
    """result of a deployment operation"""
    success: bool
    message: str
    details: Optional[str] = None
    duration: float = 0.0


@dataclass
class DeployLog:
    """deploy operation log entry"""
    timestamp: str
    server: str
    success: bool
    duration: float
    steps_completed: int
    total_steps: int
    error: Optional[str] = None

    def to_line(self) -> str:
        """format as log line"""
        status = "✓" if self.success else "✗"
        return f"{self.timestamp} | {status} {self.server} | {self.steps_completed}/{self.total_steps} steps | {self.duration:.1f}s"


class ServerDeployer:
    """
    server deployment automation for unibos

    handles:
    - ssh connection and command execution
    - git clone/pull from unibos-server repo
    - python venv setup and dependencies
    - environment file creation
    - module registry setup (.enabled files)
    - django migrations and static files
    - systemd service management
    - health checks
    """

    # deployment steps definition
    STEPS = [
        ("validate", "validating configuration"),
        ("ssh_check", "checking ssh connectivity"),
        ("backup_db", "backing up database"),
        ("prepare", "preparing deployment directory"),
        ("clone", "cloning repository"),
        ("venv", "setting up python environment"),
        ("deps", "installing dependencies"),
        ("cli", "installing unibos cli"),
        ("env", "creating environment file"),
        ("modules", "setting up module registry"),
        ("data", "setting up data directory"),
        ("database", "setting up postgresql database"),
        ("migrate", "running database migrations"),
        ("static", "collecting static files"),
        ("systemd", "setting up systemd service"),
        ("start", "starting service"),
        ("health", "health check"),
    ]

    def __init__(
        self,
        config: DeployConfig,
        dry_run: bool = False,
        verbose: bool = True,
        log_callback: Optional[Callable[[str], None]] = None
    ):
        self.config = config
        self.dry_run = dry_run
        self.verbose = verbose
        self.log_callback = log_callback or self._default_log
        self.current_step = 0
        self.start_time = None
        self._log_lines: List[str] = []

    def _default_log(self, message: str) -> None:
        """default logging to stdout"""
        if self.verbose:
            print(message)

    def log(self, message: str) -> None:
        """log a message"""
        self._log_lines.append(message)
        self.log_callback(message)

    def log_step(self, step_id: str) -> None:
        """log a step header"""
        self.current_step += 1
        step_name = next((s[1] for s in self.STEPS if s[0] == step_id), step_id)
        total = len(self.STEPS)
        self.log(f"\n→ [{self.current_step}/{total}] {step_name}")

    def ssh_cmd(self, command: str, check: bool = True, quiet: bool = False) -> subprocess.CompletedProcess:
        """execute command on remote server via ssh"""
        ssh_command = [
            'ssh',
            '-o', 'StrictHostKeyChecking=no',
            '-o', 'BatchMode=yes',
            f'-p{self.config.port}',
            self.config.ssh_target,
            command
        ]

        if self.dry_run:
            self.log(f"  [dry run] ssh: {command[:60]}...")
            return subprocess.CompletedProcess(ssh_command, 0, '', '')

        if not quiet:
            # show shortened command
            short_cmd = command[:80] + "..." if len(command) > 80 else command
            self.log(f"  $ {short_cmd}")

        result = subprocess.run(
            ssh_command,
            capture_output=True,
            text=True
        )

        if result.stdout and not quiet:
            lines = result.stdout.strip().split('\n')
            # show max 5 lines, summarize rest
            for line in lines[:5]:
                self.log(f"    {line}")
            if len(lines) > 5:
                self.log(f"    ... ({len(lines) - 5} more lines)")

        if result.returncode != 0 and check:
            if result.stderr:
                self.log(f"  ✗ error: {result.stderr[:200]}")
            raise subprocess.CalledProcessError(
                result.returncode, command, result.stdout, result.stderr
            )

        return result

    def _save_deploy_log(self, result: DeployResult) -> None:
        """save deployment log to file"""
        log_dir = Path(__file__).parent.parent / "data" / "deploy_logs"
        log_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = log_dir / f"deploy_{self.config.name}_{timestamp}.log"

        # write detailed log
        with open(log_file, 'w') as f:
            f.write(f"deploy log: {self.config.name}\n")
            f.write(f"timestamp: {timestamp}\n")
            f.write(f"duration: {result.duration:.1f}s\n")
            f.write(f"result: {'success' if result.success else 'failed'}\n")
            f.write(f"steps: {self.current_step}/{len(self.STEPS)}\n")
            f.write("-" * 60 + "\n\n")
            f.write("\n".join(self._log_lines))

        # append to summary log
        summary_file = log_dir / "deploy_history.log"
        log_entry = DeployLog(
            timestamp=timestamp,
            server=self.config.name,
            success=result.success,
            duration=result.duration,
            steps_completed=self.current_step,
            total_steps=len(self.STEPS),
            error=result.message if not result.success else None
        )
        with open(summary_file, 'a') as f:
            f.write(log_entry.to_line() + "\n")

        self.log(f"\n  log saved: {log_file.name}")

    def deploy(self) -> DeployResult:
        """
        run complete deployment pipeline

        steps:
        1. validate configuration
        2. check ssh connectivity
        3. prepare deployment directory
        4. clone repository
        5. setup python venv
        6. install dependencies
        7. install unibos cli
        8. create .env file
        9. setup module registry
        10. setup data directory
        11. setup postgresql database
        12. run migrations
        13. collect static files
        14. setup systemd service
        15. start service
        16. health check
        """
        import time
        self.start_time = time.time()
        self.current_step = 0

        # header
        self.log(f"deploying to {self.config.name}")
        self.log(f"  target: {self.config.host}")
        self.log(f"  path: {self.config.deploy_path}")
        self.log(f"  mode: {'dry run' if self.dry_run else 'live'}")

        try:
            # step 1: validate config
            self.log_step("validate")
            errors = self.config.validate()
            if errors:
                result = DeployResult(False, "configuration errors", "\n".join(errors))
                self._save_deploy_log(result)
                return result
            self.log("  ✓ configuration valid")

            # step 2: check ssh
            self.log_step("ssh_check")
            result = self.ssh_cmd("echo 'ok'", check=False, quiet=True)
            if result.returncode != 0:
                result = DeployResult(False, "ssh connection failed", result.stderr)
                self._save_deploy_log(result)
                return result
            self.log("  ✓ ssh connection successful")

            # step 3: backup database before deployment
            self.log_step("backup_db")
            backup_result = self._backup_database_before_deploy()
            if backup_result:
                self.log(f"  ✓ {backup_result}")
            else:
                self.log("  · no existing database to backup")

            # step 4: prepare deployment directory
            self.log_step("prepare")
            data_dir = self.config.data_dir

            # check if data directory exists and preserve it
            data_exists_result = self.ssh_cmd(
                f"[ -d {data_dir} ] && echo 'yes' || echo 'no'",
                check=False, quiet=True
            )
            data_exists = data_exists_result.stdout.strip() == 'yes'

            if data_exists:
                self.log(f"  preserving data directory")
                self.ssh_cmd(f"mv {data_dir} /tmp/unibos_data_backup", quiet=True)
            else:
                self.log("  no existing data to preserve")

            # clean deployment directory
            self.ssh_cmd(f"sudo rm -rf {self.config.deploy_path}", quiet=True)
            self.ssh_cmd(f"mkdir -p {self.config.deploy_path}", quiet=True)
            self.log("  ✓ directory prepared")

            # step 4: clone repository
            self.log_step("clone")
            self.ssh_cmd(
                f"git clone -b {self.config.branch} {self.config.repo_url} {self.config.deploy_path}",
                quiet=True
            )
            self.log(f"  ✓ cloned from {self.config.branch}")

            # restore data directory if it was preserved
            if data_exists:
                self.ssh_cmd(f"mv /tmp/unibos_data_backup {data_dir}", quiet=True)
                self.log("  ✓ data directory restored")

            # step 5: setup venv
            self.log_step("venv")
            self.ssh_cmd(f"cd {self.config.web_dir} && python3 -m venv venv", quiet=True)
            self.log("  ✓ virtual environment created")

            # step 6: install dependencies
            self.log_step("deps")
            self.ssh_cmd(
                f"cd {self.config.web_dir} && "
                f"./venv/bin/pip install --upgrade pip -q && "
                f"./venv/bin/pip install -r requirements.txt -q",
                quiet=True
            )
            self.log("  ✓ dependencies installed")

            # step 7: install unibos cli
            self.log_step("cli")
            self.ssh_cmd(
                f"cd {self.config.deploy_path} && "
                f"{self.config.venv_path}/bin/pip install -e . -q",
                quiet=True
            )
            self.log("  ✓ unibos-server cli installed")

            # step 8: create .env file
            self.log_step("env")
            self._create_env_file()
            self.log("  ✓ environment file created")

            # step 9: setup module registry
            self.log_step("modules")
            self._setup_modules()

            # step 10: setup data directory
            self.log_step("data")
            self._setup_data_directory()

            # step 11: setup postgresql database
            self.log_step("database")
            self._setup_database()

            # step 12: run migrations
            self.log_step("migrate")
            self._run_django_command("migrate --noinput")
            self.log("  ✓ migrations applied")

            # step 13: collect static files
            self.log_step("static")
            self._run_django_command("collectstatic --noinput")
            # copy install.sh to staticfiles for https://recaria.org/install.sh
            install_src = f"{self.config.deploy_path}/tools/install/install.sh"
            install_dst = f"{self.config.deploy_path}/core/clients/web/staticfiles/install.sh"
            self.ssh_cmd(f"cp {install_src} {install_dst} 2>/dev/null || true", quiet=True)
            self.log("  ✓ static files collected")

            # step 14: setup systemd
            self.log_step("systemd")
            self._setup_systemd()
            self.log("  ✓ systemd service configured")

            # step 15: start service
            self.log_step("start")
            self.ssh_cmd(f"sudo systemctl daemon-reload", quiet=True)
            self.ssh_cmd(f"sudo systemctl enable {self.config.service_name}", quiet=True)
            self.ssh_cmd(f"sudo systemctl restart {self.config.service_name}", quiet=True)
            self.log("  ✓ service started")

            # step 16: health check
            self.log_step("health")
            success = self._health_check()

            duration = time.time() - self.start_time

            if success:
                self.log(f"\n✓ deployment complete ({duration:.1f}s)")
                result = DeployResult(True, "deployment successful", duration=duration)
            else:
                result = DeployResult(False, "health check failed", duration=duration)

            self._save_deploy_log(result)
            return result

        except subprocess.CalledProcessError as e:
            duration = time.time() - self.start_time if self.start_time else 0
            result = DeployResult(False, f"command failed: {e.cmd[:50]}...", e.stderr, duration=duration)
            self._save_deploy_log(result)
            return result
        except Exception as e:
            duration = time.time() - self.start_time if self.start_time else 0
            result = DeployResult(False, f"deployment error: {str(e)}", duration=duration)
            self._save_deploy_log(result)
            return result

    def _create_env_file(self) -> None:
        """create .env file on server"""
        env_content = "\n".join(
            f"{key}={value}"
            for key, value in self.config.env_vars.items()
        )

        self.ssh_cmd(
            f"cat > {self.config.web_dir}/.env << 'EOF'\n{env_content}\nEOF",
            quiet=True
        )

    def _setup_modules(self) -> None:
        """setup module registry with .enabled files"""
        # create modules __init__.py
        self.ssh_cmd(
            f"touch {self.config.modules_dir}/__init__.py",
            quiet=True
        )

        # get list of modules
        result = self.ssh_cmd(
            f"ls -d {self.config.modules_dir}/*/ 2>/dev/null | xargs -n1 basename",
            check=False, quiet=True
        )

        enabled_count = 0
        if result.returncode == 0 and result.stdout:
            modules = result.stdout.strip().split('\n')

            for module in modules:
                if module and module != '__pycache__':
                    # enable all modules or only specified ones
                    if not self.config.enabled_modules or module in self.config.enabled_modules:
                        self.ssh_cmd(
                            f"touch {self.config.modules_dir}/{module}/.enabled",
                            quiet=True
                        )
                        enabled_count += 1

        self.log(f"  ✓ {enabled_count} modules enabled")

    def _setup_data_directory(self) -> None:
        """setup data directory structure"""
        data_dir = self.config.data_dir

        # create data directory and subdirectories
        subdirs = ['logs', 'media', 'cache', 'backups']

        self.ssh_cmd(f"mkdir -p {data_dir}", quiet=True)

        for subdir in subdirs:
            self.ssh_cmd(f"mkdir -p {data_dir}/{subdir}", quiet=True)

        # set proper ownership
        self.ssh_cmd(f"chown -R {self.config.user}:{self.config.user} {data_dir}", quiet=True)
        self.log(f"  ✓ data directories created ({', '.join(subdirs)})")

    def _backup_database_before_deploy(self) -> Optional[str]:
        """
        backup database before deployment
        returns backup filename if successful, None if no db exists
        """
        db_name = self.config.env_vars.get('DB_NAME', f'unibos_{self.config.name}')

        # check if database exists
        check_db = self.ssh_cmd(
            f"sudo -u postgres psql -lqt | cut -d \\| -f 1 | grep -qw {db_name} && echo 'exists' || echo 'not_exists'",
            check=False, quiet=True
        )

        if 'not_exists' in check_db.stdout:
            return None  # no database to backup

        if self.dry_run:
            return f"[dry run] would backup {db_name}"

        # create backups directory if needed
        backup_dir = f"{self.config.data_dir}/backups"
        self.ssh_cmd(f"mkdir -p {backup_dir}", check=False, quiet=True)

        # create timestamped backup with server name for clarity
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f"{backup_dir}/{self.config.name}_{db_name}_predeploy_{timestamp}.sql.gz"

        # run pg_dump
        result = self.ssh_cmd(
            f"sudo -u postgres pg_dump {db_name} | gzip > {backup_file}",
            check=False, quiet=True
        )

        if result.returncode != 0:
            self.log(f"  ⚠ backup warning: {result.stderr[:100] if result.stderr else 'unknown error'}")
            return None

        # set ownership
        self.ssh_cmd(
            f"chown {self.config.user}:{self.config.user} {backup_file}",
            check=False, quiet=True
        )

        # get file size
        size_result = self.ssh_cmd(
            f"ls -lh {backup_file} | awk '{{print $5}}'",
            check=False, quiet=True
        )
        size = size_result.stdout.strip() if size_result.stdout else "unknown"

        return f"backup saved: {backup_file} ({size})"

    def _setup_database(self) -> None:
        """setup postgresql database for this server"""
        db_name = self.config.env_vars.get('DB_NAME', f'unibos_{self.config.name}')
        db_user = self.config.env_vars.get('DB_USER', 'unibos')
        db_password = self.config.env_vars.get('DB_PASSWORD', 'unibos')

        # check if database exists
        check_db = self.ssh_cmd(
            f"sudo -u postgres psql -lqt | cut -d \\| -f 1 | grep -qw {db_name} && echo 'exists' || echo 'not_exists'",
            check=False, quiet=True
        )

        if 'not_exists' in check_db.stdout:
            self.log(f"  creating database: {db_name}")

            # create user if not exists
            self.ssh_cmd(
                f"sudo -u postgres psql -c \"DO \\$\\$ BEGIN "
                f"CREATE USER {db_user} WITH PASSWORD '{db_password}'; "
                f"EXCEPTION WHEN duplicate_object THEN NULL; END \\$\\$;\"",
                check=False, quiet=True
            )

            # create database
            self.ssh_cmd(
                f"sudo -u postgres createdb -O {db_user} {db_name}",
                check=False, quiet=True
            )

            self.log(f"  ✓ database created: {db_name}")
        else:
            self.log(f"  ✓ database exists: {db_name}")

    def _run_django_command(self, command: str) -> None:
        """run django management command"""
        self.ssh_cmd(
            f"cd {self.config.web_dir} && "
            f"PYTHONPATH=\"{self.config.web_dir}:{self.config.deploy_path}\" "
            f"DJANGO_SETTINGS_MODULE={self.config.django_settings} "
            f"./venv/bin/python manage.py {command}",
            quiet=True
        )

    def _setup_systemd(self) -> None:
        """create and install systemd service"""
        service_content = f"""[Unit]
Description=unibos server ({self.config.name})
After=network.target postgresql.service redis.service

[Service]
Type=simple
User={self.config.user}
Group={self.config.user}
WorkingDirectory={self.config.web_dir}
Environment="PYTHONPATH={self.config.web_dir}:{self.config.deploy_path}"
Environment="DJANGO_SETTINGS_MODULE={self.config.django_settings}"
ExecStart={self.config.venv_path}/bin/uvicorn unibos_backend.asgi:application --host {self.config.server_host} --port {self.config.server_port}
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
"""
        self.ssh_cmd(
            f"sudo bash -c 'cat > /etc/systemd/system/{self.config.service_name}.service << EOF\n{service_content}EOF'",
            quiet=True
        )

    def _health_check(self) -> bool:
        """check if service is running and healthy"""
        import time

        # in dry run mode, skip actual health check
        if self.dry_run:
            self.log("  [dry run] skipping health check")
            return True

        # wait a moment for service to start
        self.log("  waiting for service...")
        time.sleep(3)

        # check systemd status
        result = self.ssh_cmd(
            f"systemctl is-active {self.config.service_name}",
            check=False, quiet=True
        )

        if result.stdout.strip() == 'active':
            self.log("  ✓ service is active")

            # check http response
            http_result = self.ssh_cmd(
                f"curl -s -o /dev/null -w '%{{http_code}}' http://127.0.0.1:{self.config.server_port}/api/system-status/health/ || echo 'failed'",
                check=False, quiet=True
            )

            status_code = http_result.stdout.strip()
            self.log(f"  ✓ http status: {status_code}")

            return status_code in ['200', '301', '302', '403']

        self.log(f"  ✗ service status: {result.stdout.strip()}")
        return False

    def stop(self) -> DeployResult:
        """stop the service"""
        try:
            self.ssh_cmd(f"sudo systemctl stop {self.config.service_name}", quiet=True)
            return DeployResult(True, "service stopped")
        except subprocess.CalledProcessError as e:
            return DeployResult(False, "failed to stop service", e.stderr)

    def start(self) -> DeployResult:
        """start the service"""
        try:
            self.ssh_cmd(f"sudo systemctl start {self.config.service_name}", quiet=True)
            return DeployResult(True, "service started")
        except subprocess.CalledProcessError as e:
            return DeployResult(False, "failed to start service", e.stderr)

    def restart(self) -> DeployResult:
        """restart the service"""
        try:
            self.ssh_cmd(f"sudo systemctl restart {self.config.service_name}", quiet=True)
            return DeployResult(True, "service restarted")
        except subprocess.CalledProcessError as e:
            return DeployResult(False, "failed to restart service", e.stderr)

    def status(self) -> DeployResult:
        """get service status"""
        try:
            ssh_command = [
                'ssh',
                '-o', 'StrictHostKeyChecking=no',
                '-o', 'BatchMode=yes',
                f'-p{self.config.port}',
                self.config.ssh_target,
                f"systemctl status {self.config.service_name}"
            ]
            result = subprocess.run(ssh_command, capture_output=True, text=True)

            # combine stdout and stderr for output
            output = result.stdout or result.stderr or "no output"

            return DeployResult(
                result.returncode == 0,
                "active" if result.returncode == 0 else "inactive/not found",
                output
            )
        except Exception as e:
            return DeployResult(False, f"failed to get status: {e}")

    def logs(self, lines: int = 50, follow: bool = False) -> DeployResult:
        """get service logs"""
        try:
            follow_flag = "-f" if follow else ""
            ssh_command = [
                'ssh',
                '-o', 'StrictHostKeyChecking=no',
                '-o', 'BatchMode=yes',
                f'-p{self.config.port}',
                self.config.ssh_target,
                f"sudo journalctl -u {self.config.service_name} -n {lines} {follow_flag}"
            ]
            result = subprocess.run(ssh_command, capture_output=True, text=True)
            return DeployResult(True, "service logs", result.stdout)
        except Exception as e:
            return DeployResult(False, f"failed to get logs: {e}")

    def backup(self) -> DeployResult:
        """create database backup in data/backups/"""
        try:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

            db_name = self.config.env_vars.get('DB_NAME', f'unibos_{self.config.name}')
            backup_file = f"{self.config.data_dir}/backups/{self.config.name}_{db_name}_{timestamp}.sql.gz"

            self.log(f"creating backup: {backup_file}")

            # create backup using pg_dump
            result = self.ssh_cmd(
                f"sudo -u postgres pg_dump {db_name} | gzip > {backup_file}",
                check=False, quiet=True
            )

            if result.returncode == 0:
                # set ownership
                self.ssh_cmd(f"chown {self.config.user}:{self.config.user} {backup_file}", quiet=True)

                # get file size
                size_result = self.ssh_cmd(f"ls -lh {backup_file} | awk '{{print $5}}'", check=False, quiet=True)
                size = size_result.stdout.strip()

                return DeployResult(True, f"backup created: {backup_file} ({size})")
            else:
                return DeployResult(False, "backup failed", result.stderr)

        except subprocess.CalledProcessError as e:
            return DeployResult(False, "failed to create backup", e.stderr)

    def restore(self, backup_file: str) -> DeployResult:
        """restore database from backup file"""
        try:
            db_name = self.config.env_vars.get('DB_NAME', f'unibos_{self.config.name}')

            self.log(f"restoring from: {backup_file}")
            self.log(f"target database: {db_name}")

            # stop service before restore
            self.ssh_cmd(f"sudo systemctl stop {self.config.service_name}", check=False, quiet=True)

            # restore database
            if backup_file.endswith('.gz'):
                result = self.ssh_cmd(
                    f"gunzip -c {backup_file} | sudo -u postgres psql {db_name}",
                    check=False, quiet=True
                )
            else:
                result = self.ssh_cmd(
                    f"sudo -u postgres psql {db_name} < {backup_file}",
                    check=False, quiet=True
                )

            # start service after restore
            self.ssh_cmd(f"sudo systemctl start {self.config.service_name}", check=False, quiet=True)

            if result.returncode == 0:
                return DeployResult(True, f"database restored from {backup_file}")
            else:
                return DeployResult(False, "restore failed", result.stderr)

        except subprocess.CalledProcessError as e:
            return DeployResult(False, "failed to restore backup", e.stderr)

    def list_backups(self) -> DeployResult:
        """list available backups"""
        try:
            result = self.ssh_cmd(
                f"ls -lht {self.config.data_dir}/backups/*.sql.gz 2>/dev/null || echo 'no backups found'",
                check=False, quiet=True
            )
            return DeployResult(True, "available backups", result.stdout)
        except subprocess.CalledProcessError as e:
            return DeployResult(False, "failed to list backups", e.stderr)
