"""
Module Registry Models

Database models for tracking module state and configuration.
"""

from django.db import models
from django.utils import timezone


class ModuleConfig(models.Model):
    """
    Module configuration and state tracking

    Stores runtime state for each UNIBOS module including
    enabled/disabled status, installation info, and settings.
    """

    # Basic module info (synced from module.json)
    module_id = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text="Unique module identifier (from module.json)"
    )

    name = models.CharField(
        max_length=200,
        help_text="Module display name"
    )

    version = models.CharField(
        max_length=50,
        help_text="Current installed version (semantic versioning)"
    )

    description = models.TextField(
        blank=True,
        help_text="Module description"
    )

    icon = models.CharField(
        max_length=10,
        blank=True,
        help_text="Module icon (emoji)"
    )

    # State management
    enabled = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Is module currently enabled?"
    )

    installed = models.BooleanField(
        default=False,
        help_text="Is module installed?"
    )

    # Installation tracking
    installed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When module was first installed"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last time module was updated"
    )

    last_enabled_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last time module was enabled"
    )

    last_disabled_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last time module was disabled"
    )

    # Configuration
    config_json = models.JSONField(
        default=dict,
        blank=True,
        help_text="Module-specific configuration (from module.json)"
    )

    settings_json = models.JSONField(
        default=dict,
        blank=True,
        help_text="Runtime settings overrides"
    )

    # Metadata
    manifest_path = models.CharField(
        max_length=500,
        blank=True,
        help_text="Path to module.json file"
    )

    module_path = models.CharField(
        max_length=500,
        blank=True,
        help_text="Path to module directory"
    )

    # Health status
    last_health_check = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last health check timestamp"
    )

    health_status = models.CharField(
        max_length=50,
        blank=True,
        choices=[
            ('healthy', 'Healthy'),
            ('degraded', 'Degraded'),
            ('unhealthy', 'Unhealthy'),
            ('unknown', 'Unknown'),
        ],
        default='unknown',
        help_text="Current health status"
    )

    health_message = models.TextField(
        blank=True,
        help_text="Health check message/errors"
    )

    class Meta:
        db_table = 'unibos_module_config'
        ordering = ['module_id']
        verbose_name = 'Module Configuration'
        verbose_name_plural = 'Module Configurations'

    def __str__(self):
        status = "✓" if self.enabled else "✗"
        return f"{status} {self.name} ({self.module_id}) v{self.version}"

    def enable(self):
        """Enable this module"""
        self.enabled = True
        self.last_enabled_at = timezone.now()
        self.save(update_fields=['enabled', 'last_enabled_at', 'updated_at'])

    def disable(self):
        """Disable this module"""
        self.enabled = False
        self.last_disabled_at = timezone.now()
        self.save(update_fields=['enabled', 'last_disabled_at', 'updated_at'])

    def mark_installed(self):
        """Mark module as installed"""
        if not self.installed:
            self.installed = True
            self.installed_at = timezone.now()
            self.save(update_fields=['installed', 'installed_at', 'updated_at'])

    def update_health(self, status: str, message: str = ''):
        """Update health status"""
        self.health_status = status
        self.health_message = message
        self.last_health_check = timezone.now()
        self.save(update_fields=['health_status', 'health_message', 'last_health_check', 'updated_at'])

    def update_from_manifest(self, manifest: dict):
        """Update module info from manifest data"""
        self.name = manifest.get('name', self.name)
        self.version = manifest.get('version', self.version)
        self.description = manifest.get('description', self.description)
        self.icon = manifest.get('icon', self.icon)
        self.config_json = manifest
        self.save()
