# Migration: 0001_initial
# P2P Communication models

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        # Peer model
        migrations.CreateModel(
            name='Peer',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('node_id', models.UUIDField(db_index=True, unique=True)),
                ('hostname', models.CharField(max_length=255)),
                ('addresses', models.JSONField(default=list)),
                ('primary_address', models.GenericIPAddressField(blank=True, null=True)),
                ('primary_port', models.PositiveIntegerField(default=8000)),
                ('status', models.CharField(
                    choices=[
                        ('discovered', 'Discovered'),
                        ('connecting', 'Connecting'),
                        ('connected', 'Connected'),
                        ('disconnected', 'Disconnected'),
                        ('unreachable', 'Unreachable'),
                        ('blocked', 'Blocked'),
                    ],
                    default='discovered',
                    max_length=20
                )),
                ('discovery_method', models.CharField(
                    choices=[
                        ('mdns', 'mDNS (Local Network)'),
                        ('hub', 'Hub Registry'),
                        ('manual', 'Manual Entry'),
                        ('broadcast', 'Network Broadcast'),
                    ],
                    default='mdns',
                    max_length=20
                )),
                ('version', models.CharField(blank=True, max_length=50)),
                ('platform', models.CharField(blank=True, max_length=50)),
                ('capabilities', models.JSONField(default=dict)),
                ('is_trusted', models.BooleanField(default=False)),
                ('trust_level', models.IntegerField(default=1)),
                ('public_key', models.TextField(blank=True)),
                ('last_seen', models.DateTimeField(auto_now=True)),
                ('last_connected', models.DateTimeField(blank=True, null=True)),
                ('connection_failures', models.IntegerField(default=0)),
                ('latency_ms', models.IntegerField(blank=True, null=True)),
                ('first_discovered', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'p2p_peers',
                'ordering': ['-last_seen'],
                'verbose_name': 'Peer',
                'verbose_name_plural': 'Peers',
            },
        ),
        migrations.AddIndex(
            model_name='peer',
            index=models.Index(fields=['status', 'last_seen'], name='p2p_peer_status_idx'),
        ),
        migrations.AddIndex(
            model_name='peer',
            index=models.Index(fields=['discovery_method'], name='p2p_peer_discovery_idx'),
        ),

        # P2PMessage model
        migrations.CreateModel(
            name='P2PMessage',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('from_node', models.UUIDField(db_index=True)),
                ('to_node', models.UUIDField(db_index=True)),
                ('message_type', models.CharField(
                    choices=[
                        ('ping', 'Ping'),
                        ('pong', 'Pong'),
                        ('discovery', 'Discovery'),
                        ('auth', 'Authentication'),
                        ('data', 'Data Transfer'),
                        ('sync', 'Sync Request'),
                        ('event', 'Real-time Event'),
                        ('ack', 'Acknowledgment'),
                    ],
                    default='data',
                    max_length=20
                )),
                ('payload', models.JSONField(default=dict)),
                ('via_hub', models.BooleanField(default=False)),
                ('direct', models.BooleanField(default=False)),
                ('sent_at', models.DateTimeField(auto_now_add=True)),
                ('delivered_at', models.DateTimeField(blank=True, null=True)),
                ('acknowledged_at', models.DateTimeField(blank=True, null=True)),
                ('signature', models.TextField(blank=True)),
                ('verified', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'p2p_messages',
                'ordering': ['-sent_at'],
                'verbose_name': 'P2P Message',
                'verbose_name_plural': 'P2P Messages',
            },
        ),
        migrations.AddIndex(
            model_name='p2pmessage',
            index=models.Index(fields=['from_node', 'sent_at'], name='p2p_msg_from_idx'),
        ),
        migrations.AddIndex(
            model_name='p2pmessage',
            index=models.Index(fields=['to_node', 'sent_at'], name='p2p_msg_to_idx'),
        ),
        migrations.AddIndex(
            model_name='p2pmessage',
            index=models.Index(fields=['message_type'], name='p2p_msg_type_idx'),
        ),

        # P2PConnection model
        migrations.CreateModel(
            name='P2PConnection',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('peer', models.ForeignKey(on_delete=models.CASCADE, related_name='connections', to='p2p.peer')),
                ('local_address', models.GenericIPAddressField()),
                ('local_port', models.PositiveIntegerField()),
                ('remote_address', models.GenericIPAddressField()),
                ('remote_port', models.PositiveIntegerField()),
                ('is_websocket', models.BooleanField(default=True)),
                ('is_incoming', models.BooleanField(default=False)),
                ('connected_at', models.DateTimeField(auto_now_add=True)),
                ('disconnected_at', models.DateTimeField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('messages_sent', models.IntegerField(default=0)),
                ('messages_received', models.IntegerField(default=0)),
                ('bytes_sent', models.BigIntegerField(default=0)),
                ('bytes_received', models.BigIntegerField(default=0)),
            ],
            options={
                'db_table': 'p2p_connections',
                'ordering': ['-connected_at'],
                'verbose_name': 'P2P Connection',
                'verbose_name_plural': 'P2P Connections',
            },
        ),
    ]
