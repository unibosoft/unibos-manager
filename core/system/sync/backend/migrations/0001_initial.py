# Generated manually for UNIBOS Sync Engine
# Migration: 0001_initial

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        # SyncSession - tracks sync operations
        migrations.CreateModel(
            name='SyncSession',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('node_id', models.UUIDField(db_index=True)),
                ('node_hostname', models.CharField(max_length=255)),
                ('direction', models.CharField(choices=[('push', 'Push to Hub'), ('pull', 'Pull from Hub'), ('bidirectional', 'Bidirectional')], default='bidirectional', max_length=20)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('completed', 'Completed'), ('failed', 'Failed'), ('cancelled', 'Cancelled'), ('conflict', 'Has Conflicts')], default='pending', max_length=20)),
                ('modules', models.JSONField(default=list)),
                ('node_version_vector', models.JSONField(default=dict)),
                ('hub_version_vector', models.JSONField(default=dict)),
                ('total_records', models.IntegerField(default=0)),
                ('processed_records', models.IntegerField(default=0)),
                ('conflicts_count', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('last_error', models.TextField(blank=True)),
                ('retry_count', models.IntegerField(default=0)),
            ],
            options={
                'db_table': 'sync_sessions',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='syncsession',
            index=models.Index(fields=['node_id', 'status'], name='sync_sess_node_status_idx'),
        ),
        migrations.AddIndex(
            model_name='syncsession',
            index=models.Index(fields=['created_at'], name='sync_sess_created_idx'),
        ),

        # SyncRecord - individual record changes
        migrations.CreateModel(
            name='SyncRecord',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('session', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='records', to='sync.syncsession')),
                ('model_name', models.CharField(db_index=True, max_length=100)),
                ('record_id', models.CharField(db_index=True, max_length=100)),
                ('operation', models.CharField(choices=[('create', 'Create'), ('update', 'Update'), ('delete', 'Delete')], max_length=10)),
                ('data', models.JSONField(default=dict)),
                ('checksum', models.CharField(max_length=64)),
                ('local_version', models.BigIntegerField(default=0)),
                ('remote_version', models.BigIntegerField(default=0)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('completed', 'Completed'), ('failed', 'Failed'), ('cancelled', 'Cancelled'), ('conflict', 'Has Conflicts')], default='pending', max_length=20)),
                ('local_modified_at', models.DateTimeField()),
                ('remote_modified_at', models.DateTimeField(blank=True, null=True)),
                ('synced_at', models.DateTimeField(blank=True, null=True)),
                ('error_message', models.TextField(blank=True)),
            ],
            options={
                'db_table': 'sync_records',
                'ordering': ['model_name', 'record_id'],
            },
        ),
        migrations.AddIndex(
            model_name='syncrecord',
            index=models.Index(fields=['session', 'status'], name='sync_rec_sess_status_idx'),
        ),
        migrations.AddIndex(
            model_name='syncrecord',
            index=models.Index(fields=['model_name', 'record_id'], name='sync_rec_model_id_idx'),
        ),

        # SyncConflict - data conflicts
        migrations.CreateModel(
            name='SyncConflict',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('session', models.ForeignKey(blank=True, null=True, on_delete=models.deletion.CASCADE, related_name='conflicts', to='sync.syncsession')),
                ('model_name', models.CharField(db_index=True, max_length=100)),
                ('record_id', models.CharField(db_index=True, max_length=100)),
                ('local_data', models.JSONField()),
                ('remote_data', models.JSONField()),
                ('local_modified_at', models.DateTimeField()),
                ('remote_modified_at', models.DateTimeField()),
                ('local_node_id', models.UUIDField()),
                ('remote_source', models.CharField(max_length=100)),
                ('strategy', models.CharField(choices=[('newer_wins', 'Newer Wins'), ('older_wins', 'Older Wins'), ('hub_wins', 'Hub Wins'), ('node_wins', 'Node Wins'), ('manual', 'Manual Resolution'), ('merge', 'Merge Fields'), ('keep_both', 'Keep Both')], default='manual', max_length=20)),
                ('resolved', models.BooleanField(default=False)),
                ('resolution_data', models.JSONField(blank=True, null=True)),
                ('resolved_by', models.UUIDField(blank=True, null=True)),
                ('resolved_at', models.DateTimeField(blank=True, null=True)),
                ('detected_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'sync_conflicts',
                'ordering': ['-detected_at'],
            },
        ),
        migrations.AddIndex(
            model_name='syncconflict',
            index=models.Index(fields=['model_name', 'record_id'], name='sync_conf_model_id_idx'),
        ),
        migrations.AddIndex(
            model_name='syncconflict',
            index=models.Index(fields=['resolved', 'detected_at'], name='sync_conf_resolved_idx'),
        ),

        # OfflineOperation - queued operations
        migrations.CreateModel(
            name='OfflineOperation',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('node_id', models.UUIDField(db_index=True)),
                ('operation_type', models.CharField(choices=[('hub_sync', 'Hub Sync'), ('hub_auth', 'Hub Authentication'), ('node_sync', 'Node-to-Node Sync'), ('api_call', 'External API Call'), ('webhook', 'Webhook Delivery')], max_length=50)),
                ('module', models.CharField(blank=True, max_length=50)),
                ('target_url', models.URLField(blank=True)),
                ('method', models.CharField(default='POST', max_length=10)),
                ('payload', models.JSONField(default=dict)),
                ('headers', models.JSONField(default=dict)),
                ('priority', models.IntegerField(default=5)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('completed', 'Completed'), ('failed', 'Failed'), ('cancelled', 'Cancelled'), ('conflict', 'Has Conflicts')], default='pending', max_length=20)),
                ('retry_count', models.IntegerField(default=0)),
                ('max_retries', models.IntegerField(default=5)),
                ('retry_delay_seconds', models.IntegerField(default=60)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('scheduled_for', models.DateTimeField()),
                ('last_attempt', models.DateTimeField(blank=True, null=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('last_error', models.TextField(blank=True)),
                ('expires_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'sync_offline_operations',
                'ordering': ['priority', 'created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='offlineoperation',
            index=models.Index(fields=['node_id', 'status'], name='sync_off_node_status_idx'),
        ),
        migrations.AddIndex(
            model_name='offlineoperation',
            index=models.Index(fields=['priority', 'scheduled_for'], name='sync_off_priority_idx'),
        ),
        migrations.AddIndex(
            model_name='offlineoperation',
            index=models.Index(fields=['operation_type', 'status'], name='sync_off_type_status_idx'),
        ),

        # VersionVector - sync version tracking
        migrations.CreateModel(
            name='VersionVector',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('node_id', models.UUIDField(db_index=True)),
                ('model_name', models.CharField(db_index=True, max_length=100)),
                ('version', models.BigIntegerField(default=0)),
                ('last_synced_version', models.BigIntegerField(default=0)),
                ('total_records', models.IntegerField(default=0)),
                ('pending_changes', models.IntegerField(default=0)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('last_synced', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'sync_version_vectors',
            },
        ),
        migrations.AddConstraint(
            model_name='versionvector',
            constraint=models.UniqueConstraint(fields=['node_id', 'model_name'], name='sync_vv_node_model_unique'),
        ),
        migrations.AddIndex(
            model_name='versionvector',
            index=models.Index(fields=['node_id'], name='sync_vv_node_idx'),
        ),
        migrations.AddIndex(
            model_name='versionvector',
            index=models.Index(fields=['model_name'], name='sync_vv_model_idx'),
        ),
    ]
