import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:geolocator/geolocator.dart';
import '../models/earthquake.dart';
import '../providers/earthquake_provider.dart';
import '../services/location_service.dart';
import '../widgets/app_logo.dart';

class EarthquakeListScreen extends ConsumerStatefulWidget {
  const EarthquakeListScreen({super.key});

  @override
  ConsumerState<EarthquakeListScreen> createState() =>
      _EarthquakeListScreenState();
}

class _EarthquakeListScreenState extends ConsumerState<EarthquakeListScreen> {
  int _selectedDays = 7;
  double _selectedMinMagnitude = 2.5;
  final LocationService _locationService = LocationService();
  Position? _userLocation;

  @override
  void initState() {
    super.initState();
    _getUserLocation();
  }

  Future<void> _getUserLocation() async {
    final position = await _locationService.getCurrentLocation();
    if (position != null && mounted) {
      setState(() {
        _userLocation = position;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final earthquakesAsync = ref.watch(
      earthquakesProvider((_selectedDays, _selectedMinMagnitude)),
    );
    final statsAsync = ref.watch(earthquakeStatsProvider);

    return Scaffold(
      appBar: AppBar(
        title: const AppLogo(size: 28),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              ref.invalidate(earthquakesProvider);
              ref.invalidate(earthquakeStatsProvider);
            },
          ),
        ],
      ),
      body: Column(
        children: [
          // Statistics Header
          statsAsync.when(
            data: (stats) => _buildStatsHeader(stats),
            loading: () => const LinearProgressIndicator(
              color: Color(0xFF00ff00),
              backgroundColor: Color(0xFF1a1a1a),
            ),
            error: (error, stack) => const SizedBox.shrink(),
          ),

          // Filters
          _buildFilters(),

          // Earthquake List with Pull-to-Refresh
          Expanded(
            child: earthquakesAsync.when(
              data: (earthquakes) => RefreshIndicator(
                onRefresh: () async {
                  ref.invalidate(earthquakesProvider);
                  ref.invalidate(earthquakeStatsProvider);
                  await _getUserLocation();
                },
                color: const Color(0xFF00ff00),
                backgroundColor: const Color(0xFF1a1a1a),
                child: _buildEarthquakeList(earthquakes),
              ),
              loading: () => const Center(
                child: CircularProgressIndicator(
                  color: Color(0xFF00ff00),
                ),
              ),
              error: (error, stack) => Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Icon(Icons.error_outline, size: 48, color: Color(0xFFff4444)),
                    const SizedBox(height: 16),
                    Text(
                      'hata: ${error.toString()}',
                      style: const TextStyle(color: Color(0xFFff4444)),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 16),
                    ElevatedButton(
                      onPressed: () {
                        ref.invalidate(earthquakesProvider);
                      },
                      child: const Text('tekrar dene'),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatsHeader(EarthquakeStats stats) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: const BoxDecoration(
        color: Color(0xFF0f0f0f),
        border: Border(
          bottom: BorderSide(color: Color(0xFF00ff00), width: 2),
        ),
      ),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildStatCard('toplam', stats.total.toString(), const Color(0xFF00ff00), Icons.analytics),
              _buildStatCard('büyük', stats.major.toString(), const Color(0xFFff4444), Icons.warning),
              _buildStatCard('orta', stats.moderate.toString(), const Color(0xFFff8c00), Icons.info),
              _buildStatCard('küçük', stats.minor.toString(), const Color(0xFFffff00), Icons.circle),
            ],
          ),
          const SizedBox(height: 12),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            decoration: BoxDecoration(
              border: Border.all(color: const Color(0xFF00ff00), width: 1),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(Icons.access_time, size: 14, color: Color(0xFF00ff00)),
                const SizedBox(width: 6),
                Text(
                  'son 24 saat: ${stats.last24h} | son 7 gün: ${stats.last7d}',
                  style: const TextStyle(
                    fontSize: 11,
                    color: Color(0xFF00ff00),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatCard(String label, String value, Color color, IconData icon) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        border: Border.all(color: color, width: 1),
      ),
      child: Column(
        children: [
          Icon(icon, size: 16, color: color),
          const SizedBox(height: 4),
          Text(
            value,
            style: TextStyle(
              fontSize: 22,
              fontWeight: FontWeight.bold,
              color: color,
              fontFamily: 'monospace',
            ),
          ),
          const SizedBox(height: 2),
          Text(
            label,
            style: const TextStyle(
              fontSize: 9,
              color: Color(0xFF666666),
              letterSpacing: 0.5,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFilters() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: const BoxDecoration(
        border: Border(
          bottom: BorderSide(color: Color(0xFF00ff00), width: 1),
        ),
      ),
      child: Row(
        children: [
          Expanded(
            child: DropdownButtonFormField<int>(
              initialValue: _selectedDays,
              decoration: const InputDecoration(
                labelText: 'zaman',
                labelStyle: TextStyle(fontSize: 12),
                border: OutlineInputBorder(),
              ),
              items: const [
                DropdownMenuItem(value: 1, child: Text('son 24 saat')),
                DropdownMenuItem(value: 3, child: Text('son 3 gün')),
                DropdownMenuItem(value: 7, child: Text('son 7 gün')),
                DropdownMenuItem(value: 14, child: Text('son 14 gün')),
                DropdownMenuItem(value: 30, child: Text('son 30 gün')),
              ],
              onChanged: (value) {
                if (value != null) {
                  setState(() => _selectedDays = value);
                }
              },
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: DropdownButtonFormField<double>(
              initialValue: _selectedMinMagnitude,
              decoration: const InputDecoration(
                labelText: 'büyüklük',
                labelStyle: TextStyle(fontSize: 12),
                border: OutlineInputBorder(),
              ),
              items: const [
                DropdownMenuItem(value: 2.0, child: Text('2.0+')),
                DropdownMenuItem(value: 2.5, child: Text('2.5+')),
                DropdownMenuItem(value: 3.0, child: Text('3.0+')),
                DropdownMenuItem(value: 4.0, child: Text('4.0+')),
                DropdownMenuItem(value: 5.0, child: Text('5.0+')),
              ],
              onChanged: (value) {
                if (value != null) {
                  setState(() => _selectedMinMagnitude = value);
                }
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEarthquakeList(List<Earthquake> earthquakes) {
    if (earthquakes.isEmpty) {
      return const Center(
        child: Text(
          'deprem verisi bulunamadı',
          style: TextStyle(color: Color(0xFF666666)),
        ),
      );
    }

    return ListView.builder(
      itemCount: earthquakes.length,
      itemBuilder: (context, index) {
        final earthquake = earthquakes[index];
        return _buildEarthquakeCard(earthquake);
      },
    );
  }

  Widget _buildEarthquakeCard(Earthquake earthquake) {
    final magnitudeColor = _getMagnitudeColor(earthquake.magnitude);

    // Calculate distance if user location is available
    String? distanceText;
    if (_userLocation != null) {
      final distance = _locationService.calculateDistance(
        _userLocation!.latitude,
        _userLocation!.longitude,
        earthquake.latitude,
        earthquake.longitude,
      );
      distanceText = _locationService.formatDistance(distance);
    }

    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        border: Border.all(color: const Color(0xFF00ff00), width: 1),
      ),
      child: ListTile(
        leading: Container(
          width: 48,
          height: 48,
          decoration: BoxDecoration(
            color: magnitudeColor.withValues(alpha: 0.2),
            border: Border.all(color: magnitudeColor, width: 2),
          ),
          child: Center(
            child: Text(
              earthquake.magnitude.toStringAsFixed(1),
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: magnitudeColor,
              ),
            ),
          ),
        ),
        title: Text(
          earthquake.location,
          style: const TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.bold,
          ),
          maxLines: 2,
          overflow: TextOverflow.ellipsis,
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 4),
            Text(
              'derinlik: ${earthquake.depth.toStringAsFixed(1)} km',
              style: const TextStyle(fontSize: 12, color: Color(0xFF666666)),
            ),
            if (distanceText != null)
              Row(
                children: [
                  const Icon(
                    Icons.location_on,
                    size: 12,
                    color: Color(0xFF00ffff),
                  ),
                  const SizedBox(width: 4),
                  Text(
                    distanceText,
                    style: const TextStyle(
                      fontSize: 11,
                      color: Color(0xFF00ffff),
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(width: 8),
                  Text(
                    earthquake.timeAgo ?? '',
                    style: const TextStyle(fontSize: 10, color: Color(0xFF666666)),
                  ),
                ],
              )
            else
              Text(
                earthquake.timeAgo ?? '',
                style: const TextStyle(fontSize: 10, color: Color(0xFF666666)),
              ),
          ],
        ),
        trailing: Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          decoration: BoxDecoration(
            border: Border.all(color: const Color(0xFF00ffff), width: 1),
          ),
          child: Text(
            earthquake.source.toLowerCase(),
            style: const TextStyle(
              fontSize: 10,
              color: Color(0xFF00ffff),
            ),
          ),
        ),
      ),
    );
  }

  Color _getMagnitudeColor(double magnitude) {
    if (magnitude >= 5.0) return const Color(0xFFff4444);
    if (magnitude >= 4.0) return const Color(0xFFff8c00);
    if (magnitude >= 3.0) return const Color(0xFFffff00);
    return const Color(0xFF00ff00);
  }
}
