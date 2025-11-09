"""
Birlikteyiz models for UNIBOS
Emergency mesh network communication system
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex, GistIndex
# GIS imports temporarily disabled - need GDAL installation
# from django.contrib.gis.db import models as gis_models
# from django.contrib.gis.geos import Point
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
import hashlib

User = get_user_model()


class MeshNode(models.Model):
    """Physical mesh network nodes (LoRa devices)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    node_id = models.CharField(max_length=16, unique=True)  # Hardware ID
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mesh_nodes')
    
    # Node info
    name = models.CharField(max_length=100)
    device_type = models.CharField(
        max_length=20,
        choices=[
            ('raspberry_pi', 'Raspberry Pi'),
            ('orange_pi', 'Orange Pi'),
            ('arduino', 'Arduino'),
            ('esp32', 'ESP32'),
            ('mobile', 'Mobile Device'),
        ]
    )
    firmware_version = models.CharField(max_length=20)
    
    # Location
    # GIS field disabled - need GDAL installation
    # location = gis_models.PointField(geography=True, null=True, blank=True)
    location_lat = models.FloatField(null=True, blank=True)
    location_lon = models.FloatField(null=True, blank=True)
    altitude = models.IntegerField(null=True, blank=True)  # Meters above sea level
    location_accuracy = models.FloatField(null=True, blank=True)  # Meters
    
    # LoRa settings
    frequency = models.FloatField(default=433.0)  # MHz
    spreading_factor = models.IntegerField(
        default=7,
        validators=[MinValueValidator(7), MaxValueValidator(12)]
    )
    bandwidth = models.IntegerField(default=125)  # kHz
    tx_power = models.IntegerField(
        default=20,
        validators=[MinValueValidator(0), MaxValueValidator(20)]
    )  # dBm
    
    # Status
    is_active = models.BooleanField(default=True)
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(null=True, blank=True)
    battery_level = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Network stats
    messages_sent = models.BigIntegerField(default=0)
    messages_received = models.BigIntegerField(default=0)
    messages_relayed = models.BigIntegerField(default=0)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'birlikteyiz_mesh_nodes'
        indexes = [
            models.Index(fields=['owner', 'is_active']),
            models.Index(fields=['is_online', 'last_seen']),
            # GistIndex(fields=['location']),  # Disabled - need GDAL
        ]
    
    def __str__(self):
        return f"{self.name} ({self.node_id})"


class EmergencyMessage(models.Model):
    """Emergency messages sent through the mesh network"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message_id = models.CharField(max_length=32, unique=True)  # Hash for deduplication
    
    # Sender info
    sender_node = models.ForeignKey(
        MeshNode,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    sender_name = models.CharField(max_length=100)
    
    # Message content
    message_type = models.CharField(
        max_length=20,
        choices=[
            ('sos', 'SOS'),
            ('ok', 'I am OK'),
            ('need_help', 'Need Help'),
            ('danger', 'Danger'),
            ('evacuation', 'Evacuation'),
            ('medical', 'Medical Emergency'),
            ('supplies', 'Need Supplies'),
            ('info', 'Information'),
            ('custom', 'Custom Message'),
        ]
    )
    content = models.TextField(max_length=250)  # Limited by LoRa packet size
    priority = models.IntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    
    # Location
    # GIS field disabled - need GDAL installation
    # location = gis_models.PointField(geography=True)
    location_lat = models.FloatField()
    location_lon = models.FloatField()
    location_accuracy = models.FloatField(null=True, blank=True)
    
    # Routing info
    hop_count = models.IntegerField(default=0)
    max_hops = models.IntegerField(default=10)
    ttl = models.IntegerField(default=24)  # Time to live in hours
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()
    
    # Delivery tracking
    is_delivered = models.BooleanField(default=False)
    delivered_count = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'birlikteyiz_emergency_messages'
        indexes = [
            models.Index(fields=['message_type', 'created_at']),
            models.Index(fields=['expires_at']),
            # GistIndex(fields=['location']),  # Disabled - need GDAL
        ]
        ordering = ['-created_at', '-priority']
    
    def __str__(self):
        return f"{self.message_type}: {self.content[:50]}"
    
    def generate_message_id(self):
        """Generate unique message ID for deduplication"""
        content = f"{self.sender_node.node_id}{self.content}{self.created_at.timestamp()}"
        return hashlib.md5(content.encode()).hexdigest()


class MessageRelay(models.Model):
    """Track message relay path through the network"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.ForeignKey(
        EmergencyMessage,
        on_delete=models.CASCADE,
        related_name='relays'
    )
    relay_node = models.ForeignKey(
        MeshNode,
        on_delete=models.CASCADE,
        related_name='relayed_messages'
    )
    
    # Relay info
    received_at = models.DateTimeField(auto_now_add=True)
    signal_strength = models.IntegerField()  # RSSI in dBm
    snr = models.FloatField()  # Signal-to-noise ratio
    
    # Previous hop
    previous_node = models.ForeignKey(
        MeshNode,
        on_delete=models.CASCADE,
        related_name='messages_sent_to',
        null=True,
        blank=True
    )
    
    class Meta:
        db_table = 'birlikteyiz_message_relays'
        unique_together = ['message', 'relay_node']
        indexes = [
            models.Index(fields=['message', 'received_at']),
            models.Index(fields=['relay_node', 'received_at']),
        ]
        ordering = ['received_at']
    
    def __str__(self):
        return f"Relay by {self.relay_node.name} at {self.received_at}"


class EmergencyContact(models.Model):
    """Emergency contacts for users"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='emergency_contacts')
    
    # Contact info
    name = models.CharField(max_length=100)
    relationship = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    
    # Notification preferences
    notify_sms = models.BooleanField(default=True)
    notify_email = models.BooleanField(default=True)
    notify_mesh = models.BooleanField(default=True)
    
    # Priority
    priority = models.IntegerField(default=1)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'birlikteyiz_emergency_contacts'
        ordering = ['priority', 'name']
        indexes = [
            models.Index(fields=['user', 'priority']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.relationship})"


class DisasterZone(models.Model):
    """Defined disaster zones for monitoring"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    
    # Zone definition
    zone_type = models.CharField(
        max_length=20,
        choices=[
            ('earthquake', 'Earthquake'),
            ('flood', 'Flood'),
            ('fire', 'Fire'),
            ('landslide', 'Landslide'),
            ('storm', 'Storm'),
            ('other', 'Other'),
        ]
    )
    
    # Geographic boundary
    # GIS fields disabled - need GDAL installation
    # boundary = gis_models.PolygonField(geography=True)
    # center = gis_models.PointField(geography=True)
    boundary = models.JSONField()  # Store as GeoJSON
    center_lat = models.FloatField()
    center_lon = models.FloatField()
    radius = models.IntegerField()  # Approximate radius in meters
    
    # Status
    severity = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('critical', 'Critical'),
        ]
    )
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    declared_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Statistics
    affected_population = models.IntegerField(null=True, blank=True)
    messages_sent = models.IntegerField(default=0)
    nodes_active = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'birlikteyiz_disaster_zones'
        indexes = [
            models.Index(fields=['is_active', 'severity']),
            models.Index(fields=['declared_at']),
            # GistIndex(fields=['boundary']),  # Disabled - need GDAL
            # GistIndex(fields=['center']),  # Disabled - need GDAL
        ]
        ordering = ['-declared_at', '-severity']
    
    def __str__(self):
        return f"{self.name} ({self.zone_type})"


class ResourcePoint(models.Model):
    """Resource distribution points"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    
    # Location
    # GIS field disabled - need GDAL installation
    # location = gis_models.PointField(geography=True)
    location_lat = models.FloatField()
    location_lon = models.FloatField()
    address = models.TextField()
    
    # Resource info
    resource_type = models.CharField(
        max_length=20,
        choices=[
            ('shelter', 'Shelter'),
            ('food', 'Food Distribution'),
            ('water', 'Water Distribution'),
            ('medical', 'Medical Aid'),
            ('charging', 'Charging Station'),
            ('communication', 'Communication Hub'),
            ('transport', 'Transportation'),
        ]
    )
    
    # Capacity
    capacity = models.IntegerField(null=True, blank=True)
    current_occupancy = models.IntegerField(default=0)
    
    # Status
    is_operational = models.BooleanField(default=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    # Contact
    contact_name = models.CharField(max_length=100, blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    
    # Operating hours
    operating_hours = models.JSONField(default=dict)
    
    class Meta:
        db_table = 'birlikteyiz_resource_points'
        indexes = [
            models.Index(fields=['resource_type', 'is_operational']),
            # GistIndex(fields=['location']),  # Disabled - need GDAL
        ]
    
    def __str__(self):
        return f"{self.name} ({self.resource_type})"


class NetworkTopology(models.Model):
    """Network topology snapshot for analysis"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Snapshot info
    snapshot_time = models.DateTimeField(default=timezone.now)
    total_nodes = models.IntegerField()
    active_nodes = models.IntegerField()
    
    # Network metrics
    average_signal_strength = models.FloatField()
    network_coverage_area = models.FloatField()  # Square kilometers
    max_hop_distance = models.IntegerField()
    
    # Topology data
    node_connections = models.JSONField(default=dict)  # Adjacency matrix
    central_nodes = models.JSONField(default=list)  # Most connected nodes
    isolated_nodes = models.JSONField(default=list)
    
    # Performance metrics
    average_latency = models.FloatField()  # Milliseconds
    packet_loss_rate = models.FloatField()  # Percentage
    throughput = models.FloatField()  # Messages per hour
    
    class Meta:
        db_table = 'birlikteyiz_network_topology'
        ordering = ['-snapshot_time']
        indexes = [
            models.Index(fields=['snapshot_time']),
        ]
    
    def __str__(self):
        return f"Network snapshot at {self.snapshot_time}"


class EmergencyProtocol(models.Model):
    """Pre-defined emergency protocols"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    
    # Protocol details
    description = models.TextField()
    emergency_type = models.CharField(
        max_length=20,
        choices=[
            ('earthquake', 'Earthquake'),
            ('flood', 'Flood'),
            ('fire', 'Fire'),
            ('medical', 'Medical'),
            ('security', 'Security'),
        ]
    )
    
    # Actions
    steps = models.JSONField(default=list)  # List of action steps
    required_resources = models.JSONField(default=list)
    estimated_duration = models.IntegerField()  # Minutes
    
    # Activation
    is_active = models.BooleanField(default=True)
    auto_activate = models.BooleanField(default=False)
    activation_conditions = models.JSONField(default=dict)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'birlikteyiz_emergency_protocols'
        ordering = ['emergency_type', 'name']
    
    def __str__(self):
        return f"{self.code}: {self.name}"


class Earthquake(models.Model):
    """Deprem verilerini saklar"""
    
    SOURCE_CHOICES = [
        ('KANDILLI', 'Kandilli Rasathanesi'),
        ('AFAD', 'AFAD'),
        ('TDBS', 'TDBS'),
        ('USGS', 'USGS'),
        ('EMSC', 'EMSC'),
    ]
    
    # Benzersiz tanımlayıcı (kaynak + olay ID)
    unique_id = models.CharField(max_length=100, unique=True)
    
    # Kaynak bilgisi
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    source_id = models.CharField(max_length=50, null=True, blank=True)
    
    # Deprem bilgileri
    magnitude = models.DecimalField(max_digits=3, decimal_places=1)
    depth = models.DecimalField(max_digits=6, decimal_places=2)  # km
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    
    # Lokasyon
    location = models.CharField(max_length=255)
    city = models.CharField(max_length=100, null=True, blank=True)
    district = models.CharField(max_length=100, null=True, blank=True)
    
    # Zaman
    occurred_at = models.DateTimeField()
    fetched_at = models.DateTimeField(default=timezone.now)
    
    # Ek bilgiler
    intensity = models.CharField(max_length=10, null=True, blank=True)
    solution_type = models.CharField(max_length=50, null=True, blank=True)
    
    # Kullanıcı yorumları için
    is_felt = models.BooleanField(default=False)
    felt_reports = models.IntegerField(default=0)
    
    # Meta veri
    raw_data = models.JSONField(null=True, blank=True)
    
    class Meta:
        db_table = 'birlikteyiz_earthquakes'
        ordering = ['-occurred_at']
        indexes = [
            models.Index(fields=['-occurred_at']),
            models.Index(fields=['magnitude']),
            models.Index(fields=['source']),
            models.Index(fields=['city']),
        ]
        
    def __str__(self):
        return f"{self.magnitude} - {self.location} ({self.occurred_at})"


class EarthquakeComment(models.Model):
    """Deprem hakkında kullanıcı yorumları"""
    
    earthquake = models.ForeignKey(Earthquake, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Yorum
    comment = models.TextField()
    felt_it = models.BooleanField(default=False)
    intensity_felt = models.IntegerField(null=True, blank=True, choices=[
        (1, 'Çok hafif'),
        (2, 'Hafif'),
        (3, 'Orta'),
        (4, 'Güçlü'),
        (5, 'Çok güçlü'),
    ])
    
    # Lokasyon
    user_city = models.CharField(max_length=100, null=True, blank=True)
    user_district = models.CharField(max_length=100, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'birlikteyiz_earthquake_comments'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Comment on {self.earthquake} by {self.user}"


class EarthquakeDataSource(models.Model):
    """Veri kaynaklarının durumu ve konfigürasyonu"""

    # Basic Info
    name = models.CharField(max_length=50, unique=True)
    url = models.URLField()
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    # Fetch Configuration
    fetch_interval_minutes = models.IntegerField(default=5, help_text="Kaç dakikada bir veri çekilecek")
    min_magnitude = models.DecimalField(max_digits=3, decimal_places=1, default=2.5, help_text="Minimum deprem büyüklüğü")
    max_results = models.IntegerField(default=100, help_text="Maksimum sonuç sayısı")

    # Geographic Filters
    use_geographic_filter = models.BooleanField(default=False, help_text="Coğrafi filtreleme kullan")
    filter_min_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    filter_max_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    filter_min_lon = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    filter_max_lon = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    filter_region_name = models.CharField(max_length=100, null=True, blank=True, help_text="Örn: Türkiye, Küresel, vb.")

    # Statistics
    last_fetch = models.DateTimeField(null=True, blank=True)
    last_success = models.DateTimeField(null=True, blank=True)
    last_error = models.TextField(null=True, blank=True)
    last_error_time = models.DateTimeField(null=True, blank=True)
    fetch_count = models.IntegerField(default=0)
    error_count = models.IntegerField(default=0)
    success_count = models.IntegerField(default=0)
    total_earthquakes_fetched = models.IntegerField(default=0)

    # Performance
    avg_response_time = models.FloatField(null=True, blank=True, help_text="Ortalama yanıt süresi (saniye)")
    last_response_time = models.FloatField(null=True, blank=True, help_text="Son yanıt süresi (saniye)")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        db_table = 'birlikteyiz_earthquake_sources'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_success_rate(self):
        """Başarı oranını hesapla"""
        if self.fetch_count == 0:
            return 0
        return round((self.success_count / self.fetch_count) * 100, 1)

    def get_geographic_bounds(self):
        """Coğrafi sınırları dict olarak döndür"""
        if not self.use_geographic_filter:
            return None
        return {
            'min_lat': float(self.filter_min_lat) if self.filter_min_lat else None,
            'max_lat': float(self.filter_max_lat) if self.filter_max_lat else None,
            'min_lon': float(self.filter_min_lon) if self.filter_min_lon else None,
            'max_lon': float(self.filter_max_lon) if self.filter_max_lon else None,
        }


class CronJob(models.Model):
    """Cron job takibi için genel model"""
    
    STATUS_CHOICES = [
        ('pending', 'Bekliyor'),
        ('running', 'Çalışıyor'),
        ('success', 'Başarılı'),
        ('failed', 'Başarısız'),
    ]
    
    name = models.CharField(max_length=100)
    command = models.CharField(max_length=255)
    schedule = models.CharField(max_length=100)  # Cron formatı veya açıklama
    
    is_active = models.BooleanField(default=True)
    last_run = models.DateTimeField(null=True, blank=True)
    next_run = models.DateTimeField(null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    last_result = models.TextField(null=True, blank=True)
    
    run_count = models.IntegerField(default=0)
    success_count = models.IntegerField(default=0)
    error_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'birlikteyiz_cronjobs'
        ordering = ['name']
        
    def __str__(self):
        return f"{self.name} ({self.schedule})"