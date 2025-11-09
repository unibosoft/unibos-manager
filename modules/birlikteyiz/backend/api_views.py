from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q

from .models import Earthquake, EarthquakeDataSource, DisasterZone, MeshNode
from .serializers import (
    EarthquakeSerializer,
    EarthquakeListSerializer,
    DataSourceSerializer,
    DisasterZoneSerializer,
    MeshNodeSerializer,
    EarthquakeStatsSerializer,
)


class EarthquakeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for earthquakes

    list: Get all earthquakes with filters
    retrieve: Get single earthquake detail
    stats: Get earthquake statistics
    recent: Get recent earthquakes
    """

    queryset = Earthquake.objects.all().order_by('-occurred_at')
    permission_classes = [AllowAny]  # Public API for mobile app

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return EarthquakeSerializer
        return EarthquakeListSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by days
        days = self.request.query_params.get('days', None)
        if days:
            try:
                days = int(days)
                queryset = queryset.filter(
                    occurred_at__gte=timezone.now() - timedelta(days=days)
                )
            except ValueError:
                pass

        # Filter by magnitude
        min_magnitude = self.request.query_params.get('min_magnitude', None)
        if min_magnitude:
            try:
                queryset = queryset.filter(magnitude__gte=float(min_magnitude))
            except ValueError:
                pass

        # Filter by source
        source = self.request.query_params.get('source', None)
        if source:
            queryset = queryset.filter(source=source.upper())

        # Filter by city
        city = self.request.query_params.get('city', None)
        if city:
            queryset = queryset.filter(
                Q(city__icontains=city) | Q(location__icontains=city)
            )

        # Limit results for performance
        limit = self.request.query_params.get('limit', 100)
        try:
            limit = min(int(limit), 500)  # Max 500
        except ValueError:
            limit = 100

        return queryset[:limit]

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get earthquake statistics"""

        # Base queryset for last 7 days
        last_7d = Earthquake.objects.filter(
            occurred_at__gte=timezone.now() - timedelta(days=7)
        )

        # Count by magnitude
        total = last_7d.count()
        major = last_7d.filter(magnitude__gte=5.0).count()
        moderate = last_7d.filter(magnitude__gte=4.0, magnitude__lt=5.0).count()
        minor = last_7d.filter(magnitude__gte=3.0, magnitude__lt=4.0).count()

        # Last 24h
        last_24h = Earthquake.objects.filter(
            occurred_at__gte=timezone.now() - timedelta(hours=24)
        ).count()

        # Strongest and latest
        strongest = last_7d.order_by('-magnitude').first()
        latest = last_7d.first()

        stats_data = {
            'total': total,
            'major': major,
            'moderate': moderate,
            'minor': minor,
            'last_24h': last_24h,
            'last_7d': total,
            'strongest': strongest,
            'latest': latest,
        }

        serializer = EarthquakeStatsSerializer(stats_data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get most recent earthquakes"""

        limit = request.query_params.get('limit', 50)
        try:
            limit = min(int(limit), 100)
        except ValueError:
            limit = 50

        earthquakes = self.get_queryset()[:limit]
        serializer = self.get_serializer(earthquakes, many=True)

        return Response({
            'count': len(earthquakes),
            'results': serializer.data
        })

    @action(detail=False, methods=['get'])
    def map_data(self, request):
        """Get earthquake data optimized for map display"""

        # Get filter parameters
        days = request.query_params.get('days', 7)
        min_magnitude = request.query_params.get('min_magnitude', 2.5)

        try:
            days = int(days)
            min_magnitude = float(min_magnitude)
        except ValueError:
            days = 7
            min_magnitude = 2.5

        # Query earthquakes
        earthquakes = Earthquake.objects.filter(
            occurred_at__gte=timezone.now() - timedelta(days=days),
            magnitude__gte=min_magnitude
        ).order_by('-occurred_at')[:500]

        # Lightweight data for map
        map_data = []
        for eq in earthquakes:
            map_data.append({
                'id': eq.id,
                'lat': float(eq.latitude),
                'lon': float(eq.longitude),
                'mag': float(eq.magnitude),
                'depth': float(eq.depth),
                'loc': eq.location,
                'city': eq.city or '',
                'src': eq.source,
                'time': eq.occurred_at.isoformat(),
            })

        return Response({
            'count': len(map_data),
            'earthquakes': map_data
        })


class DataSourceViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for earthquake data sources"""

    queryset = EarthquakeDataSource.objects.all()
    serializer_class = DataSourceSerializer
    permission_classes = [IsAuthenticated]


class DisasterZoneViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for disaster zones"""

    queryset = DisasterZone.objects.filter(is_active=True)
    serializer_class = DisasterZoneSerializer
    permission_classes = [IsAuthenticated]


class MeshNodeViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for mesh network nodes"""

    queryset = MeshNode.objects.all()
    serializer_class = MeshNodeSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def online(self, request):
        """Get only online nodes"""
        online_nodes = self.queryset.filter(is_online=True)
        serializer = self.get_serializer(online_nodes, many=True)
        return Response(serializer.data)
