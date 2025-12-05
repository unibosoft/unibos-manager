# Migration: 0002_export_control
# Data Export Control models

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('sync', '0001_initial'),
    ]

    operations = [
        # DataExportSettings - per-node export control
        migrations.CreateModel(
            name='DataExportSettings',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('node_id', models.UUIDField(db_index=True, unique=True)),
                ('node_hostname', models.CharField(blank=True, max_length=255)),
                ('master_kill_switch', models.BooleanField(default=False)),
                ('module_settings', models.JSONField(default=dict)),
                ('new_modules_default_export', models.BooleanField(default=False)),
                ('require_confirmation', models.BooleanField(default=True)),
                ('confirmation_timeout_seconds', models.IntegerField(default=30)),
                ('log_all_exports', models.BooleanField(default=True)),
                ('log_blocked_exports', models.BooleanField(default=True)),
                ('allow_local_mesh', models.BooleanField(default=True)),
                ('emergency_bypass', models.JSONField(default=list)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'export_settings',
                'verbose_name': 'Data Export Settings',
                'verbose_name_plural': 'Data Export Settings',
            },
        ),

        # DataExportLog - audit log
        migrations.CreateModel(
            name='DataExportLog',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('node_id', models.UUIDField(db_index=True)),
                ('module', models.CharField(db_index=True, max_length=50)),
                ('data_type', models.CharField(db_index=True, max_length=100)),
                ('model_name', models.CharField(blank=True, max_length=100)),
                ('destination_type', models.CharField(choices=[('hub', 'Hub Server'), ('node', 'Another Node'), ('external', 'External API'), ('file', 'File Export'), ('unknown', 'Unknown')], default='unknown', max_length=20)),
                ('destination_id', models.CharField(blank=True, max_length=255)),
                ('destination_name', models.CharField(blank=True, max_length=255)),
                ('status', models.CharField(choices=[('allowed', 'Allowed'), ('blocked', 'Blocked'), ('pending', 'Pending Confirmation'), ('cancelled', 'Cancelled by User')], default='allowed', max_length=20)),
                ('blocked_reason', models.CharField(blank=True, max_length=255)),
                ('record_count', models.IntegerField(default=0)),
                ('size_bytes', models.BigIntegerField(default=0)),
                ('request_path', models.CharField(blank=True, max_length=500)),
                ('request_method', models.CharField(blank=True, max_length=10)),
                ('user_id', models.UUIDField(blank=True, null=True)),
                ('user_ip', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.TextField(blank=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('extra_data', models.JSONField(default=dict)),
            ],
            options={
                'db_table': 'export_logs',
                'ordering': ['-timestamp'],
                'verbose_name': 'Data Export Log',
                'verbose_name_plural': 'Data Export Logs',
            },
        ),
        migrations.AddIndex(
            model_name='dataexportlog',
            index=models.Index(fields=['node_id', 'timestamp'], name='export_log_node_ts_idx'),
        ),
        migrations.AddIndex(
            model_name='dataexportlog',
            index=models.Index(fields=['module', 'data_type'], name='export_log_module_idx'),
        ),
        migrations.AddIndex(
            model_name='dataexportlog',
            index=models.Index(fields=['status', 'timestamp'], name='export_log_status_idx'),
        ),
    ]
