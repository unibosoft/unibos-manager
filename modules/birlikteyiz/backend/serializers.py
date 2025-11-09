from rest_framework import serializers
from .models import Earthquake, EarthquakeDataSource, DisasterZone, MeshNode


class EarthquakeSerializer(serializers.ModelSerializer):
    """Serializer for Earthquake model"""

    class Meta:
        model = Earthquake
        fields = [
            'id',
            'unique_id',
            'source',
            'source_id',
            'magnitude',
            'depth',
            'latitude',
            'longitude',
            'location',
            'city',
            'district',
            'occurred_at',
            'fetched_at',
            'intensity',
            'solution_type',
            'is_felt',
            'felt_reports',
        ]
        read_only_fields = ['id', 'unique_id', 'fetched_at']


class EarthquakeListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list view"""

    time_ago = serializers.SerializerMethodField()

    class Meta:
        model = Earthquake
        fields = [
            'id',
            'magnitude',
            'depth',
            'latitude',
            'longitude',
            'location',
            'city',
            'source',
            'occurred_at',
            'time_ago',
        ]

    def get_time_ago(self, obj):
        from django.utils import timezone
        delta = timezone.now() - obj.occurred_at

        if delta.days > 0:
            return f"{delta.days} gün önce"
        elif delta.seconds // 3600 > 0:
            return f"{delta.seconds // 3600} saat önce"
        else:
            return f"{delta.seconds // 60} dakika önce"


class DataSourceSerializer(serializers.ModelSerializer):
    """Serializer for earthquake data sources"""

    health_status = serializers.SerializerMethodField()

    class Meta:
        model = EarthquakeDataSource
        fields = [
            'id',
            'name',
            'url',
            'is_active',
            'last_fetch_at',
            'last_success_at',
            'fetch_count',
            'error_count',
            'health_status',
        ]

    def get_health_status(self, obj):
        if not obj.is_active:
            return 'inactive'

        if obj.error_count > 10:
            return 'error'
        elif obj.last_success_at:
            from django.utils import timezone
            from datetime import timedelta
            if timezone.now() - obj.last_success_at < timedelta(hours=1):
                return 'healthy'

        return 'warning'


class DisasterZoneSerializer(serializers.ModelSerializer):
    """Serializer for disaster zones"""

    class Meta:
        model = DisasterZone
        fields = [
            'id',
            'name',
            'zone_type',
            'severity',
            'latitude',
            'longitude',
            'radius',
            'is_active',
            'declared_at',
            'resolved_at',
            'description',
        ]


class MeshNodeSerializer(serializers.ModelSerializer):
    """Serializer for mesh network nodes"""

    class Meta:
        model = MeshNode
        fields = [
            'id',
            'node_id',
            'name',
            'device_type',
            'latitude',
            'longitude',
            'is_online',
            'battery_level',
            'last_seen_at',
            'signal_strength',
        ]


class EarthquakeStatsSerializer(serializers.Serializer):
    """Serializer for earthquake statistics"""

    total = serializers.IntegerField()
    major = serializers.IntegerField()
    moderate = serializers.IntegerField()
    minor = serializers.IntegerField()
    last_24h = serializers.IntegerField()
    last_7d = serializers.IntegerField()
    strongest = EarthquakeListSerializer(allow_null=True)
    latest = EarthquakeListSerializer(allow_null=True)
