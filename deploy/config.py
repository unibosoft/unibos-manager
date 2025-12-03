"""
UNIBOS Deploy Configuration
Handles server deployment configuration loading and validation
"""

import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class DeployConfig:
    """Server deployment configuration"""

    # Server identification
    name: str
    host: str
    user: str = "ubuntu"
    port: int = 22

    # Deployment paths
    deploy_path: str = "/home/ubuntu/unibos"
    venv_path: str = "/home/ubuntu/unibos/core/clients/web/venv"

    # Git settings
    repo_url: str = "git@github.com:unibosoft/unibos-server.git"
    branch: str = "main"

    # Django settings
    django_settings: str = "unibos_backend.settings.server"

    # Server settings
    server_port: int = 8000
    server_host: str = "0.0.0.0"

    # Systemd service
    service_name: str = "unibos"

    # Environment variables (will be written to .env)
    env_vars: dict = field(default_factory=dict)

    # Modules to enable (empty = all)
    enabled_modules: list = field(default_factory=list)

    @classmethod
    def load(cls, config_path: Path) -> 'DeployConfig':
        """Load configuration from JSON file"""
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path) as f:
            data = json.load(f)

        return cls(**data)

    @classmethod
    def load_by_name(cls, server_name: str, project_root: Optional[Path] = None) -> 'DeployConfig':
        """Load configuration by server name from root directory"""
        if project_root is None:
            project_root = Path(__file__).parent.parent

        config_path = project_root / f"{server_name}.config.json"
        return cls.load(config_path)

    def save(self, config_path: Path) -> None:
        """Save configuration to JSON file"""
        data = {
            'name': self.name,
            'host': self.host,
            'user': self.user,
            'port': self.port,
            'deploy_path': self.deploy_path,
            'venv_path': self.venv_path,
            'repo_url': self.repo_url,
            'branch': self.branch,
            'django_settings': self.django_settings,
            'server_port': self.server_port,
            'server_host': self.server_host,
            'service_name': self.service_name,
            'env_vars': self.env_vars,
            'enabled_modules': self.enabled_modules,
        }

        with open(config_path, 'w') as f:
            json.dump(data, f, indent=2)

    @property
    def ssh_target(self) -> str:
        """SSH connection string"""
        return f"{self.user}@{self.host}"

    @property
    def web_dir(self) -> str:
        """Django project directory"""
        return f"{self.deploy_path}/core/clients/web"

    @property
    def modules_dir(self) -> str:
        """Modules directory"""
        return f"{self.deploy_path}/modules"

    @property
    def data_dir(self) -> str:
        """Data directory for runtime files"""
        return f"{self.deploy_path}/data"

    def validate(self) -> list:
        """Validate configuration and return list of errors"""
        errors = []

        if not self.name:
            errors.append("Server name is required")
        if not self.host:
            errors.append("Server host is required")
        if not self.repo_url:
            errors.append("Repository URL is required")
        if 'SECRET_KEY' not in self.env_vars:
            errors.append("SECRET_KEY is required in env_vars")

        return errors
