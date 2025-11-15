"""
UNIBOS Node Setup
Standalone node installation and configuration (raspberry pi, local mac)

This module provides setup tools for UNIBOS nodes:
- Local PostgreSQL database setup
- Lightweight service configuration
- P2P mesh networking setup
- Offline queue initialization
- Optional Redis installation
- Node identity generation
"""

import os
import subprocess
import sys
import uuid
import json
from pathlib import Path
from typing import Optional, Dict


class NodeSetup:
    """
    Standalone node setup manager

    Handles installation and configuration of UNIBOS nodes
    for offline-first, autonomous operation
    """

    def __init__(self,
                 install_path: str = '/opt/unibos',
                 data_path: str = '/var/lib/unibos'):
        """
        Initialize node setup

        Args:
            install_path: Installation directory
            data_path: Data storage directory
        """
        self.install_path = Path(install_path)
        self.data_path = Path(data_path)
        self.venv_path = self.install_path / 'venv'
        self.config_path = self.data_path / 'config'

    def generate_node_identity(self) -> Dict[str, str]:
        """
        Generate unique node identity

        Returns:
            dict: Node identity information
        """
        import socket

        identity = {
            'node_id': str(uuid.uuid4()),
            'node_name': os.environ.get('NODE_NAME', socket.gethostname()),
            'node_type': 'standalone',
            'created_at': str(subprocess.run(
                ['date', '-Iseconds'],
                capture_output=True,
                text=True
            ).stdout.strip())
        }

        return identity

    def save_node_identity(self, identity: Dict[str, str]) -> bool:
        """
        Save node identity to disk

        Args:
            identity: Node identity dict

        Returns:
            bool: True if successful
        """
        try:
            identity_file = self.config_path / 'node_identity.json'
            identity_file.parent.mkdir(parents=True, exist_ok=True)

            with open(identity_file, 'w') as f:
                json.dump(identity, f, indent=2)

            print(f"✅ Node identity saved: {identity['node_id']}")
            print(f"   Name: {identity['node_name']}")
            return True
        except Exception as e:
            print(f"❌ Failed to save node identity: {e}")
            return False

    def install_postgresql(self) -> bool:
        """
        Install and configure PostgreSQL

        Returns:
            bool: True if successful
        """
        print("📦 Installing PostgreSQL...")

        # Detect OS and use appropriate package manager
        if Path('/etc/debian_version').exists():
            # Debian/Ubuntu/Raspberry Pi OS
            cmds = [
                ['sudo', 'apt-get', 'update'],
                ['sudo', 'apt-get', 'install', '-y', 'postgresql', 'postgresql-contrib'],
                ['sudo', 'systemctl', 'enable', 'postgresql'],
                ['sudo', 'systemctl', 'start', 'postgresql'],
            ]
        elif Path('/etc/redhat-release').exists():
            # RedHat/CentOS/Fedora
            cmds = [
                ['sudo', 'dnf', 'install', '-y', 'postgresql-server', 'postgresql-contrib'],
                ['sudo', 'postgresql-setup', '--initdb'],
                ['sudo', 'systemctl', 'enable', 'postgresql'],
                ['sudo', 'systemctl', 'start', 'postgresql'],
            ]
        elif sys.platform == 'darwin':
            # macOS
            cmds = [
                ['brew', 'install', 'postgresql@14'],
                ['brew', 'services', 'start', 'postgresql@14'],
            ]
        else:
            print("❌ Unsupported operating system")
            return False

        for cmd in cmds:
            result = subprocess.run(cmd, capture_output=True)
            if result.returncode != 0:
                print(f"❌ Command failed: {' '.join(cmd)}")
                return False

        print("✅ PostgreSQL installed")
        return True

    def setup_database(self) -> bool:
        """
        Create node database and user

        Returns:
            bool: True if successful
        """
        print("🗄️  Setting up database...")

        db_name = 'unibos_node_db'
        db_user = 'unibos_node_user'
        db_password = 'unibos_node_password'

        # Create database and user
        sql_cmds = [
            f"CREATE USER {db_user} WITH PASSWORD '{db_password}';",
            f"CREATE DATABASE {db_name} OWNER {db_user};",
            f"GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {db_user};",
        ]

        for sql in sql_cmds:
            result = subprocess.run(
                ['sudo', '-u', 'postgres', 'psql', '-c', sql],
                capture_output=True,
                text=True
            )
            # Ignore "already exists" errors
            if result.returncode != 0 and 'already exists' not in result.stderr:
                print(f"❌ SQL failed: {sql}")
                return False

        print("✅ Database created")
        return True

    def install_redis(self, optional: bool = True) -> bool:
        """
        Install Redis (optional for nodes)

        Args:
            optional: If True, don't fail if installation fails

        Returns:
            bool: True if successful or optional
        """
        print("📦 Installing Redis (optional)...")

        # Detect OS and use appropriate package manager
        if Path('/etc/debian_version').exists():
            cmd = ['sudo', 'apt-get', 'install', '-y', 'redis-server']
        elif Path('/etc/redhat-release').exists():
            cmd = ['sudo', 'dnf', 'install', '-y', 'redis']
        elif sys.platform == 'darwin':
            cmd = ['brew', 'install', 'redis']
        else:
            if optional:
                print("⚠️  Skipping Redis installation (unsupported OS)")
                return True
            return False

        result = subprocess.run(cmd, capture_output=True)

        if result.returncode != 0:
            if optional:
                print("⚠️  Redis installation failed (optional)")
                return True
            return False

        print("✅ Redis installed")
        return True

    def install_dependencies(self) -> bool:
        """
        Install Python dependencies

        Returns:
            bool: True if successful
        """
        print("📦 Installing Python dependencies...")

        # Create virtual environment
        subprocess.run(['python3', '-m', 'venv', str(self.venv_path)])

        # Install requirements
        pip = self.venv_path / 'bin' / 'pip'
        requirements = self.install_path / 'requirements.txt'

        if not requirements.exists():
            print("⚠️  No requirements.txt found")
            return True

        result = subprocess.run(
            [str(pip), 'install', '-r', str(requirements)],
            capture_output=True
        )

        if result.returncode != 0:
            print("❌ Dependency installation failed")
            return False

        print("✅ Dependencies installed")
        return True

    def run_migrations(self) -> bool:
        """
        Run initial database migrations

        Returns:
            bool: True if successful
        """
        print("🗄️  Running migrations...")

        manage_py = self.install_path / 'core' / 'web' / 'manage.py'
        python = self.venv_path / 'bin' / 'python'

        env = os.environ.copy()
        env['DJANGO_SETTINGS_MODULE'] = 'unibos_backend.settings.node'

        result = subprocess.run(
            [str(python), str(manage_py), 'migrate'],
            env=env,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"❌ Migrations failed: {result.stderr}")
            return False

        print("✅ Migrations completed")
        return True

    def create_systemd_service(self) -> bool:
        """
        Create systemd service for node

        Returns:
            bool: True if successful
        """
        print("⚙️  Creating systemd service...")

        service_content = f"""[Unit]
Description=UNIBOS Node Service
After=network.target postgresql.service

[Service]
Type=notify
User={os.getlogin()}
WorkingDirectory={self.install_path}/core/clients/web
Environment="DJANGO_SETTINGS_MODULE=unibos_backend.settings.node"
Environment="PATH={self.venv_path}/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart={self.venv_path}/bin/gunicorn unibos_backend.wsgi:application \\
    --bind 0.0.0.0:8000 \\
    --workers 2 \\
    --threads 2 \\
    --timeout 60 \\
    --access-logfile - \\
    --error-logfile -
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
"""

        service_file = Path('/etc/systemd/system/unibos-node.service')

        try:
            with open('/tmp/unibos-node.service', 'w') as f:
                f.write(service_content)

            subprocess.run(['sudo', 'mv', '/tmp/unibos-node.service', str(service_file)])
            subprocess.run(['sudo', 'systemctl', 'daemon-reload'])
            subprocess.run(['sudo', 'systemctl', 'enable', 'unibos-node'])

            print("✅ Systemd service created")
            return True
        except Exception as e:
            print(f"❌ Service creation failed: {e}")
            return False

    def setup(self,
              skip_postgres: bool = False,
              skip_redis: bool = False) -> bool:
        """
        Complete node setup workflow

        Args:
            skip_postgres: Skip PostgreSQL installation
            skip_redis: Skip Redis installation

        Returns:
            bool: True if setup successful
        """
        print("🚀 Starting UNIBOS Node setup...")
        print(f"   Install path: {self.install_path}")
        print(f"   Data path: {self.data_path}")

        # Generate node identity
        print("\n🆔 Generating node identity...")
        identity = self.generate_node_identity()
        if not self.save_node_identity(identity):
            return False

        # Install PostgreSQL
        if not skip_postgres:
            if not self.install_postgresql():
                return False
            if not self.setup_database():
                return False

        # Install Redis (optional)
        if not skip_redis:
            self.install_redis(optional=True)

        # Install dependencies
        if not self.install_dependencies():
            return False

        # Run migrations
        if not self.run_migrations():
            return False

        # Create systemd service
        if not self.create_systemd_service():
            print("⚠️  Service creation failed (you can start manually)")

        print("\n🎉 Node setup complete!")
        print(f"\n📝 Node ID: {identity['node_id']}")
        print(f"📝 Node Name: {identity['node_name']}")
        print("\n🚀 Start the node with:")
        print("   sudo systemctl start unibos-node")
        print("\n📊 Check status with:")
        print("   sudo systemctl status unibos-node")

        return True


def setup_node(**kwargs):
    """
    Setup UNIBOS node

    Args:
        **kwargs: Passed to NodeSetup.setup()

    Returns:
        bool: True if successful
    """
    setup = NodeSetup()
    return setup.setup(**kwargs)
