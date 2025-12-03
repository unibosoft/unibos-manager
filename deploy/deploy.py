"""
UNIBOS Server Deployer
Handles complete server deployment lifecycle
"""

import subprocess
from typing import Optional, Callable
from dataclasses import dataclass

from deploy.config import DeployConfig


@dataclass
class DeployResult:
    """Result of a deployment operation"""
    success: bool
    message: str
    details: Optional[str] = None


class ServerDeployer:
    """
    Server deployment automation for UNIBOS

    Handles:
    - SSH connection and command execution
    - Git clone/pull from unibos-server repo
    - Python venv setup and dependencies
    - Environment file creation
    - Module registry setup (.enabled files)
    - Django migrations and static files
    - Systemd service management
    - Health checks
    """

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

    def _default_log(self, message: str) -> None:
        """Default logging to stdout"""
        if self.verbose:
            print(message)

    def log(self, message: str) -> None:
        """Log a message"""
        self.log_callback(message)

    def log_step(self, step: str) -> None:
        """Log a step header"""
        self.log(f"\n{'='*60}")
        self.log(f"  {step}")
        self.log(f"{'='*60}")

    def ssh_cmd(self, command: str, check: bool = True) -> subprocess.CompletedProcess:
        """Execute command on remote server via SSH"""
        ssh_command = [
            'ssh',
            '-o', 'StrictHostKeyChecking=no',
            '-o', 'BatchMode=yes',
            f'-p{self.config.port}',
            self.config.ssh_target,
            command
        ]

        if self.dry_run:
            self.log(f"[DRY RUN] ssh {self.config.ssh_target} '{command}'")
            return subprocess.CompletedProcess(ssh_command, 0, '', '')

        self.log(f"$ {command}")

        result = subprocess.run(
            ssh_command,
            capture_output=True,
            text=True
        )

        if result.stdout:
            for line in result.stdout.strip().split('\n'):
                self.log(f"  {line}")

        if result.returncode != 0 and check:
            if result.stderr:
                self.log(f"  [ERROR] {result.stderr}")
            raise subprocess.CalledProcessError(
                result.returncode, command, result.stdout, result.stderr
            )

        return result

    def deploy(self) -> DeployResult:
        """
        Run complete deployment pipeline

        Steps:
        1. Validate configuration
        2. Check SSH connectivity
        3. Clean old deployment (if exists)
        4. Clone repository
        5. Setup Python venv
        6. Install dependencies
        7. Create .env file
        8. Setup module registry
        9. Setup data directory
        10. Setup PostgreSQL database
        11. Run migrations
        12. Collect static files
        13. Setup systemd service
        14. Start service
        15. Health check
        """
        self.log_step("UNIBOS Server Deployment")
        self.log(f"Target: {self.config.name} ({self.config.host})")
        self.log(f"Path: {self.config.deploy_path}")
        self.log(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE'}")

        try:
            # Step 1: Validate config
            self.log_step("1. Validating Configuration")
            errors = self.config.validate()
            if errors:
                return DeployResult(False, "Configuration errors", "\n".join(errors))
            self.log("Configuration valid")

            # Step 2: Check SSH
            self.log_step("2. Checking SSH Connectivity")
            result = self.ssh_cmd("echo 'SSH OK'", check=False)
            if result.returncode != 0:
                return DeployResult(False, "SSH connection failed", result.stderr)
            self.log("SSH connection successful")

            # Step 3: Backup data directory if exists
            self.log_step("3. Preparing Deployment Directory")
            data_dir = self.config.data_dir

            # Check if data directory exists and preserve it
            data_exists_result = self.ssh_cmd(
                f"[ -d {data_dir} ] && echo 'YES' || echo 'NO'",
                check=False
            )
            data_exists = data_exists_result.stdout.strip() == 'YES'

            if data_exists:
                self.log(f"Preserving existing data directory: {data_dir}")
                # Move data to temp location
                self.ssh_cmd(f"mv {data_dir} /tmp/unibos_data_backup")
            else:
                self.log("No existing data directory to preserve")

            # Clean deployment directory (excluding data which we moved)
            # Use sudo to handle locked files (e.g., venv packages with special permissions)
            self.ssh_cmd(f"sudo rm -rf {self.config.deploy_path}")
            self.ssh_cmd(f"mkdir -p {self.config.deploy_path}")

            # Step 4: Clone repository
            self.log_step("4. Cloning Repository")
            self.ssh_cmd(
                f"git clone -b {self.config.branch} {self.config.repo_url} {self.config.deploy_path}"
            )

            # Restore data directory if it was preserved
            if data_exists:
                self.log("Restoring data directory")
                self.ssh_cmd(f"mv /tmp/unibos_data_backup {data_dir}")

            # Step 5: Setup venv
            self.log_step("5. Setting Up Python Virtual Environment")
            self.ssh_cmd(f"cd {self.config.web_dir} && python3 -m venv venv")

            # Step 6: Install dependencies
            self.log_step("6. Installing Dependencies")
            self.ssh_cmd(
                f"cd {self.config.web_dir} && "
                f"./venv/bin/pip install --upgrade pip && "
                f"./venv/bin/pip install -r requirements.txt"
            )

            # Step 7: Install UNIBOS CLI (unibos-server command)
            self.log_step("7. Installing UNIBOS CLI")
            self.ssh_cmd(
                f"cd {self.config.deploy_path} && "
                f"{self.config.venv_path}/bin/pip install -e ."
            )
            self.log("  unibos-server command installed")

            # Step 8: Create .env file
            self.log_step("8. Creating Environment File")
            self._create_env_file()

            # Step 9: Setup module registry
            self.log_step("9. Setting Up Module Registry")
            self._setup_modules()

            # Step 10: Setup data directory
            self.log_step("10. Setting Up Data Directory")
            self._setup_data_directory()

            # Step 11: Setup PostgreSQL database
            self.log_step("11. Setting Up PostgreSQL Database")
            self._setup_database()

            # Step 12: Run migrations
            self.log_step("12. Running Database Migrations")
            self._run_django_command("migrate --noinput")

            # Step 13: Collect static files
            self.log_step("13. Collecting Static Files")
            self._run_django_command("collectstatic --noinput")

            # Step 14: Setup systemd
            self.log_step("14. Setting Up Systemd Service")
            self._setup_systemd()

            # Step 15: Start service
            self.log_step("15. Starting Service")
            self.ssh_cmd(f"sudo systemctl daemon-reload")
            self.ssh_cmd(f"sudo systemctl enable {self.config.service_name}")
            self.ssh_cmd(f"sudo systemctl restart {self.config.service_name}")

            # Step 16: Health check
            self.log_step("16. Health Check")
            success = self._health_check()

            if success:
                self.log_step("Deployment Complete!")
                return DeployResult(True, "Deployment successful")
            else:
                return DeployResult(False, "Health check failed")

        except subprocess.CalledProcessError as e:
            return DeployResult(False, f"Command failed: {e.cmd}", e.stderr)
        except Exception as e:
            return DeployResult(False, f"Deployment error: {str(e)}")

    def _create_env_file(self) -> None:
        """Create .env file on server"""
        env_content = "\n".join(
            f"{key}={value}"
            for key, value in self.config.env_vars.items()
        )

        self.ssh_cmd(
            f"cat > {self.config.web_dir}/.env << 'EOF'\n{env_content}\nEOF"
        )

    def _setup_modules(self) -> None:
        """Setup module registry with .enabled files"""
        # Create modules __init__.py
        self.ssh_cmd(
            f"touch {self.config.modules_dir}/__init__.py"
        )

        # Get list of modules
        result = self.ssh_cmd(
            f"ls -d {self.config.modules_dir}/*/ 2>/dev/null | xargs -n1 basename",
            check=False
        )

        if result.returncode == 0 and result.stdout:
            modules = result.stdout.strip().split('\n')

            for module in modules:
                if module and module != '__pycache__':
                    # Enable all modules or only specified ones
                    if not self.config.enabled_modules or module in self.config.enabled_modules:
                        self.ssh_cmd(
                            f"touch {self.config.modules_dir}/{module}/.enabled"
                        )
                        self.log(f"  Enabled: {module}")

    def _setup_data_directory(self) -> None:
        """Setup data directory structure"""
        data_dir = self.config.data_dir

        # Create data directory and subdirectories
        subdirs = ['logs', 'media', 'cache', 'backups']

        self.ssh_cmd(f"mkdir -p {data_dir}")

        for subdir in subdirs:
            self.ssh_cmd(f"mkdir -p {data_dir}/{subdir}")
            self.log(f"  Created: data/{subdir}/")

        # Set proper ownership
        self.ssh_cmd(f"chown -R {self.config.user}:{self.config.user} {data_dir}")

    def _setup_database(self) -> None:
        """Setup PostgreSQL database for this server"""
        db_name = self.config.env_vars.get('DB_NAME', f'unibos_{self.config.name}')
        db_user = self.config.env_vars.get('DB_USER', 'unibos')
        db_password = self.config.env_vars.get('DB_PASSWORD', 'unibos')

        # Check if database exists
        check_db = self.ssh_cmd(
            f"sudo -u postgres psql -lqt | cut -d \\| -f 1 | grep -qw {db_name} && echo 'EXISTS' || echo 'NOT_EXISTS'",
            check=False
        )

        if 'NOT_EXISTS' in check_db.stdout:
            self.log(f"Creating database: {db_name}")

            # Create user if not exists
            self.ssh_cmd(
                f"sudo -u postgres psql -c \"DO \\$\\$ BEGIN "
                f"CREATE USER {db_user} WITH PASSWORD '{db_password}'; "
                f"EXCEPTION WHEN duplicate_object THEN NULL; END \\$\\$;\"",
                check=False
            )

            # Create database
            self.ssh_cmd(
                f"sudo -u postgres createdb -O {db_user} {db_name}",
                check=False
            )

            self.log(f"  Database created: {db_name}")
            self.log(f"  Owner: {db_user}")
        else:
            self.log(f"Database already exists: {db_name}")

    def _run_django_command(self, command: str) -> None:
        """Run Django management command"""
        self.ssh_cmd(
            f"cd {self.config.web_dir} && "
            f"PYTHONPATH=\"{self.config.web_dir}:{self.config.deploy_path}\" "
            f"DJANGO_SETTINGS_MODULE={self.config.django_settings} "
            f"./venv/bin/python manage.py {command}"
        )

    def _setup_systemd(self) -> None:
        """Create and install systemd service"""
        service_content = f"""[Unit]
Description=UNIBOS Server ({self.config.name})
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
            f"sudo bash -c 'cat > /etc/systemd/system/{self.config.service_name}.service << EOF\n{service_content}EOF'"
        )

    def _health_check(self) -> bool:
        """Check if service is running and healthy"""
        import time

        # In dry run mode, skip actual health check
        if self.dry_run:
            self.log("[DRY RUN] Skipping health check")
            return True

        # Wait a moment for service to start
        self.log("Waiting for service to start...")
        time.sleep(3)

        # Check systemd status
        result = self.ssh_cmd(
            f"systemctl is-active {self.config.service_name}",
            check=False
        )

        if result.stdout.strip() == 'active':
            self.log("Service is active")

            # Check HTTP response
            http_result = self.ssh_cmd(
                f"curl -s -o /dev/null -w '%{{http_code}}' http://127.0.0.1:{self.config.server_port}/api/status/ || echo 'FAILED'",
                check=False
            )

            status_code = http_result.stdout.strip()
            self.log(f"HTTP status: {status_code}")

            return status_code in ['200', '301', '302', '403']

        self.log(f"Service status: {result.stdout.strip()}")
        return False

    def stop(self) -> DeployResult:
        """Stop the service"""
        try:
            self.ssh_cmd(f"sudo systemctl stop {self.config.service_name}")
            return DeployResult(True, "Service stopped")
        except subprocess.CalledProcessError as e:
            return DeployResult(False, "Failed to stop service", e.stderr)

    def start(self) -> DeployResult:
        """Start the service"""
        try:
            self.ssh_cmd(f"sudo systemctl start {self.config.service_name}")
            return DeployResult(True, "Service started")
        except subprocess.CalledProcessError as e:
            return DeployResult(False, "Failed to start service", e.stderr)

    def restart(self) -> DeployResult:
        """Restart the service"""
        try:
            self.ssh_cmd(f"sudo systemctl restart {self.config.service_name}")
            return DeployResult(True, "Service restarted")
        except subprocess.CalledProcessError as e:
            return DeployResult(False, "Failed to restart service", e.stderr)

    def status(self) -> DeployResult:
        """Get service status"""
        try:
            result = self.ssh_cmd(
                f"systemctl status {self.config.service_name}",
                check=False
            )
            return DeployResult(
                result.returncode == 0,
                "Service status",
                result.stdout
            )
        except subprocess.CalledProcessError as e:
            return DeployResult(False, "Failed to get status", e.stderr)

    def logs(self, lines: int = 50, follow: bool = False) -> DeployResult:
        """Get service logs"""
        try:
            follow_flag = "-f" if follow else ""
            result = self.ssh_cmd(
                f"sudo journalctl -u {self.config.service_name} -n {lines} {follow_flag}",
                check=False
            )
            return DeployResult(True, "Service logs", result.stdout)
        except subprocess.CalledProcessError as e:
            return DeployResult(False, "Failed to get logs", e.stderr)

    def backup(self) -> DeployResult:
        """Create database backup in data/backups/"""
        try:
            import datetime
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

            db_name = self.config.env_vars.get('DB_NAME', f'unibos_{self.config.name}')
            backup_file = f"{self.config.data_dir}/backups/{db_name}_{timestamp}.sql.gz"

            self.log(f"Creating backup: {backup_file}")

            # Create backup using pg_dump
            result = self.ssh_cmd(
                f"sudo -u postgres pg_dump {db_name} | gzip > {backup_file}",
                check=False
            )

            if result.returncode == 0:
                # Set ownership
                self.ssh_cmd(f"chown {self.config.user}:{self.config.user} {backup_file}")

                # Get file size
                size_result = self.ssh_cmd(f"ls -lh {backup_file} | awk '{{print $5}}'", check=False)
                size = size_result.stdout.strip()

                return DeployResult(True, f"Backup created: {backup_file} ({size})")
            else:
                return DeployResult(False, "Backup failed", result.stderr)

        except subprocess.CalledProcessError as e:
            return DeployResult(False, "Failed to create backup", e.stderr)

    def restore(self, backup_file: str) -> DeployResult:
        """Restore database from backup file"""
        try:
            db_name = self.config.env_vars.get('DB_NAME', f'unibos_{self.config.name}')

            self.log(f"Restoring from: {backup_file}")
            self.log(f"Target database: {db_name}")

            # Stop service before restore
            self.ssh_cmd(f"sudo systemctl stop {self.config.service_name}", check=False)

            # Restore database
            if backup_file.endswith('.gz'):
                result = self.ssh_cmd(
                    f"gunzip -c {backup_file} | sudo -u postgres psql {db_name}",
                    check=False
                )
            else:
                result = self.ssh_cmd(
                    f"sudo -u postgres psql {db_name} < {backup_file}",
                    check=False
                )

            # Start service after restore
            self.ssh_cmd(f"sudo systemctl start {self.config.service_name}", check=False)

            if result.returncode == 0:
                return DeployResult(True, f"Database restored from {backup_file}")
            else:
                return DeployResult(False, "Restore failed", result.stderr)

        except subprocess.CalledProcessError as e:
            return DeployResult(False, "Failed to restore backup", e.stderr)

    def list_backups(self) -> DeployResult:
        """List available backups"""
        try:
            result = self.ssh_cmd(
                f"ls -lht {self.config.data_dir}/backups/*.sql.gz 2>/dev/null || echo 'No backups found'",
                check=False
            )
            return DeployResult(True, "Available backups", result.stdout)
        except subprocess.CalledProcessError as e:
            return DeployResult(False, "Failed to list backups", e.stderr)
