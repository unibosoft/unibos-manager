"""
Module Registry Admin Interface
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import ModuleConfig


@admin.register(ModuleConfig)
class ModuleConfigAdmin(admin.ModelAdmin):
    """Admin interface for module configuration"""

    list_display = [
        'module_icon',
        'module_id',
        'name',
        'version',
        'status_badge',
        'health_badge',
        'installed_at',
        'actions_column',
    ]

    list_filter = [
        'enabled',
        'installed',
        'health_status',
    ]

    search_fields = [
        'module_id',
        'name',
        'description',
    ]

    readonly_fields = [
        'module_id',
        'installed_at',
        'updated_at',
        'last_enabled_at',
        'last_disabled_at',
        'last_health_check',
        'manifest_path',
        'module_path',
    ]

    fieldsets = (
        ('Basic Info', {
            'fields': (
                'module_id',
                'name',
                'version',
                'description',
                'icon',
            )
        }),
        ('State', {
            'fields': (
                'enabled',
                'installed',
            )
        }),
        ('Timestamps', {
            'fields': (
                'installed_at',
                'updated_at',
                'last_enabled_at',
                'last_disabled_at',
            ),
            'classes': ('collapse',)
        }),
        ('Health', {
            'fields': (
                'health_status',
                'health_message',
                'last_health_check',
            )
        }),
        ('Configuration', {
            'fields': (
                'config_json',
                'settings_json',
            ),
            'classes': ('collapse',)
        }),
        ('Paths', {
            'fields': (
                'manifest_path',
                'module_path',
            ),
            'classes': ('collapse',)
        }),
    )

    actions = ['enable_modules', 'disable_modules', 'sync_from_disk']

    def module_icon(self, obj):
        """Display module icon"""
        return obj.icon or '📦'
    module_icon.short_description = ''

    def status_badge(self, obj):
        """Display status badge"""
        if obj.enabled:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 10px; '
                'border-radius: 3px; font-size: 11px;">ENABLED</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #dc3545; color: white; padding: 3px 10px; '
                'border-radius: 3px; font-size: 11px;">DISABLED</span>'
            )
    status_badge.short_description = 'Status'

    def health_badge(self, obj):
        """Display health status badge"""
        colors = {
            'healthy': '#28a745',
            'degraded': '#ffc107',
            'unhealthy': '#dc3545',
            'unknown': '#6c757d',
        }

        color = colors.get(obj.health_status, '#6c757d')

        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.health_status.upper()
        )
    health_badge.short_description = 'Health'

    def actions_column(self, obj):
        """Display action buttons"""
        if obj.enabled:
            return format_html(
                '<a class="button" href="/admin/module_registry/moduleconfig/{}/change/" '
                'style="padding: 5px 10px; background-color: #007bff; color: white; '
                'text-decoration: none; border-radius: 3px;">Configure</a>',
                obj.pk
            )
        else:
            return format_html(
                '<a class="button" href="/admin/module_registry/moduleconfig/{}/change/" '
                'style="padding: 5px 10px; background-color: #6c757d; color: white; '
                'text-decoration: none; border-radius: 3px;">Enable</a>',
                obj.pk
            )
    actions_column.short_description = 'Actions'

    def enable_modules(self, request, queryset):
        """Enable selected modules"""
        count = 0
        for module in queryset:
            module.enable()
            count += 1

        self.message_user(request, f'{count} module(s) enabled successfully.')
    enable_modules.short_description = 'Enable selected modules'

    def disable_modules(self, request, queryset):
        """Disable selected modules"""
        count = 0
        for module in queryset:
            module.disable()
            count += 1

        self.message_user(request, f'{count} module(s) disabled successfully.')
    disable_modules.short_description = 'Disable selected modules'

    def sync_from_disk(self, request, queryset):
        """Sync modules from disk"""
        from .registry import module_registry

        module_registry.reload()
        module_registry.sync_to_database()

        self.message_user(request, 'Module registry synced from disk.')
    sync_from_disk.short_description = 'Sync from disk (reload)'
