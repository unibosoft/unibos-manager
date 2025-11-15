"""
UNIBOS Server Deployment
Production server deployment automation (rocksteady)

This module provides deployment tools for the central UNIBOS server:
- PostgreSQL database setup and migrations
- Gunicorn/Nginx configuration
- Redis and Celery setup
- SSL certificate management
- Service monitoring and health checks
- Backup and restore procedures
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional, Dict, List


class ServerDeployment:
    """
    Production server deployment manager

    Handles deployment to rocksteady.local (Ubuntu production server)
    """

    def __init__(self,
                 server_host: str = 'rocksteady',
                 server_user: str = 'berkhatirli',
                 deploy_path: str = '/var/www/unibos'):
        """
        Initialize server deployment

        Args:
            server_host: SSH hostname or IP
            server_user: SSH username
            deploy_path: Remote deployment path
        """
        self.server_host = server_host
        self.server_user = server_user
        self.deploy_path = deploy_path
        self.ssh_target = f"{server_user}@{server_host}"

    def check_connection(self) -> bool:
        """
        Check SSH connection to server

        Returns:
            bool: True if connection successful
        """
        try:
            result = subprocess.run(
                ['ssh', self.ssh_target, 'echo', 'ok'],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False

    def pull_latest(self) -> bool:
        """
        Pull latest code from Git on server

        Returns:
            bool: True if successful
        """
        cmd = f"cd {self.deploy_path} && git pull"
        result = subprocess.run(
            ['ssh', self.ssh_target, cmd],
            capture_output=True,
            text=True
        )
        return result.returncode == 0

    def install_dependencies(self) -> bool:
        """
        Install Python dependencies on server

        Returns:
            bool: True if successful
        """
        cmd = (
            f"cd {self.deploy_path} && "
            f"source venv/bin/activate && "
            f"pip install -r requirements.txt"
        )
        result = subprocess.run(
            ['ssh', self.ssh_target, cmd],
            capture_output=True,
            text=True
        )
        return result.returncode == 0

    def run_migrations(self) -> bool:
        """
        Run Django database migrations

        Returns:
            bool: True if successful
        """
        cmd = (
            f"cd {self.deploy_path}/core/clients/web && "
            f"source ../venv/bin/activate && "
            f"DJANGO_SETTINGS_MODULE=unibos_backend.settings.server "
            f"python manage.py migrate"
        )
        result = subprocess.run(
            ['ssh', self.ssh_target, cmd],
            capture_output=True,
            text=True
        )
        return result.returncode == 0

    def collect_static(self) -> bool:
        """
        Collect static files

        Returns:
            bool: True if successful
        """
        cmd = (
            f"cd {self.deploy_path}/core/clients/web && "
            f"source ../venv/bin/activate && "
            f"DJANGO_SETTINGS_MODULE=unibos_backend.settings.server "
            f"python manage.py collectstatic --noinput"
        )
        result = subprocess.run(
            ['ssh', self.ssh_target, cmd],
            capture_output=True,
            text=True
        )
        return result.returncode == 0

    def restart_services(self, services: Optional[List[str]] = None) -> bool:
        """
        Restart server services

        Args:
            services: List of service names (default: all)

        Returns:
            bool: True if successful
        """
        if services is None:
            services = ['gunicorn', 'nginx', 'celery', 'redis']

        for service in services:
            cmd = f"sudo systemctl restart {service}"
            result = subprocess.run(
                ['ssh', self.ssh_target, cmd],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                return False

        return True

    def health_check(self) -> Dict[str, bool]:
        """
        Run health check on all services

        Returns:
            dict: Service name -> status mapping
        """
        services = ['postgresql', 'redis', 'gunicorn', 'nginx', 'celery']
        status = {}

        for service in services:
            cmd = f"systemctl is-active {service}"
            result = subprocess.run(
                ['ssh', self.ssh_target, cmd],
                capture_output=True,
                text=True
            )
            status[service] = result.returncode == 0

        return status

    def deploy(self,
               skip_tests: bool = False,
               skip_migrations: bool = False) -> bool:
        """
        Full deployment workflow

        Args:
            skip_tests: Skip running tests
            skip_migrations: Skip database migrations

        Returns:
            bool: True if deployment successful
        """
        print("🚀 Starting UNIBOS Server deployment...")

        # Check connection
        print("📡 Checking SSH connection...")
        if not self.check_connection():
            print("❌ Cannot connect to server")
            return False
        print("✅ Connected to server")

        # Pull latest code
        print("📥 Pulling latest code...")
        if not self.pull_latest():
            print("❌ Git pull failed")
            return False
        print("✅ Code updated")

        # Install dependencies
        print("📦 Installing dependencies...")
        if not self.install_dependencies():
            print("❌ Dependency installation failed")
            return False
        print("✅ Dependencies installed")

        # Run migrations
        if not skip_migrations:
            print("🗄️  Running migrations...")
            if not self.run_migrations():
                print("❌ Migrations failed")
                return False
            print("✅ Migrations completed")

        # Collect static files
        print("📁 Collecting static files...")
        if not self.collect_static():
            print("❌ Static collection failed")
            return False
        print("✅ Static files collected")

        # Restart services
        print("🔄 Restarting services...")
        if not self.restart_services():
            print("❌ Service restart failed")
            return False
        print("✅ Services restarted")

        # Health check
        print("🏥 Running health check...")
        status = self.health_check()
        all_healthy = all(status.values())

        for service, healthy in status.items():
            emoji = "✅" if healthy else "❌"
            print(f"  {emoji} {service}")

        if all_healthy:
            print("\n🎉 Deployment successful!")
            return True
        else:
            print("\n⚠️  Deployment completed with warnings")
            return False


def deploy_to_server(**kwargs):
    """
    Deploy to production server

    Args:
        **kwargs: Passed to ServerDeployment.deploy()

    Returns:
        bool: True if successful
    """
    deployment = ServerDeployment()
    return deployment.deploy(**kwargs)
