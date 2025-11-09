# Generated manually
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('solitaire', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SolitairePlayer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_key', models.CharField(db_index=True, max_length=100)),
                ('ip_address', models.GenericIPAddressField()),
                ('user_agent', models.TextField(blank=True)),
                ('display_name', models.CharField(blank=True, max_length=100)),
                ('is_anonymous', models.BooleanField(default=True)),
                ('first_seen', models.DateTimeField(auto_now_add=True)),
                ('last_seen', models.DateTimeField(auto_now=True)),
                ('total_sessions', models.IntegerField(default=0)),
                ('country', models.CharField(blank=True, max_length=100)),
                ('city', models.CharField(blank=True, max_length=100)),
                ('is_active', models.BooleanField(default=True)),
                ('is_banned', models.BooleanField(default=False)),
                ('ban_reason', models.TextField(blank=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='solitaire_players', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-last_seen'],
            },
        ),
        migrations.CreateModel(
            name='SolitaireGameSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_id', models.CharField(db_index=True, max_length=100, unique=True)),
                ('started_at', models.DateTimeField(auto_now_add=True)),
                ('ended_at', models.DateTimeField(blank=True, null=True)),
                ('game_state', models.JSONField(default=dict)),
                ('moves_count', models.IntegerField(default=0)),
                ('score', models.IntegerField(default=0)),
                ('time_played', models.IntegerField(default=0)),
                ('is_completed', models.BooleanField(default=False)),
                ('is_won', models.BooleanField(default=False)),
                ('is_abandoned', models.BooleanField(default=False)),
                ('browser_info', models.JSONField(default=dict)),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='game_sessions', to='solitaire.solitaireplayer')),
            ],
            options={
                'ordering': ['-started_at'],
            },
        ),
        migrations.CreateModel(
            name='SolitaireActivity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('start', 'Game Started'), ('move', 'Card Move'), ('undo', 'Undo Move'), ('hint', 'Hint Used'), ('auto', 'Auto Complete'), ('win', 'Game Won'), ('abandon', 'Game Abandoned'), ('pause', 'Game Paused'), ('resume', 'Game Resumed')], max_length=20)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('details', models.JSONField(default=dict)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activities', to='solitaire.solitairegamesession')),
            ],
            options={
                'ordering': ['session', 'timestamp'],
            },
        ),
        migrations.AddIndex(
            model_name='solitaireplayer',
            index=models.Index(fields=['session_key', 'ip_address'], name='solitaire_s_session_cc5e15_idx'),
        ),
        migrations.AddIndex(
            model_name='solitaireplayer',
            index=models.Index(fields=['last_seen'], name='solitaire_s_last_se_6b1f8e_idx'),
        ),
        migrations.AddIndex(
            model_name='solitairegamesession',
            index=models.Index(fields=['player', 'started_at'], name='solitaire_s_player__c0e8e9_idx'),
        ),
        migrations.AddIndex(
            model_name='solitairegamesession',
            index=models.Index(fields=['is_won', 'is_completed'], name='solitaire_s_is_won_58e8a5_idx'),
        ),
        migrations.AddIndex(
            model_name='solitaireactivity',
            index=models.Index(fields=['session', 'action'], name='solitaire_s_session_f0e3e1_idx'),
        ),
        migrations.AddIndex(
            model_name='solitaireactivity',
            index=models.Index(fields=['timestamp'], name='solitaire_s_timesta_c8e5e4_idx'),
        ),
    ]