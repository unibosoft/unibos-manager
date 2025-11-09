import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:geolocator/geolocator.dart';
import '../providers/earthquake_provider.dart';
import '../services/location_service.dart';
import '../widgets/app_logo.dart';

class EarthquakeMapScreen extends ConsumerStatefulWidget {
  const EarthquakeMapScreen({super.key});

  @override
  ConsumerState<EarthquakeMapScreen> createState() => _EarthquakeMapScreenState();
}

class _EarthquakeMapScreenState extends ConsumerState<EarthquakeMapScreen> {
  int _selectedDays = 7;
  double _selectedMinMagnitude = 2.5;
  final LocationService _locationService = LocationService();
  Position? _userLocation;
  final MapController _mapController = MapController();
  bool _isLoadingLocation = false;

  @override
  Widget build(BuildContext context) {
    final mapDataAsync = ref.watch(
      mapDataProvider((_selectedDays, _selectedMinMagnitude)),
    );

    return Scaffold(
      appBar: AppBar(
        title: const AppLogo(size: 28),
        actions: [
          // Location button
          IconButton(
            icon: Icon(
              _userLocation != null ? Icons.my_location : Icons.location_off,
              color: _userLocation != null ? const Color(0xFF00ffff) : null,
            ),
            onPressed: _isLoadingLocation ? null : _getUserLocation,
          ),
          // Refresh button
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              ref.invalidate(mapDataProvider);
            },
          ),
        ],
      ),
      body: Column(
        children: [
          _buildFilters(),
          Expanded(
            child: mapDataAsync.when(
              data: (data) => _buildMap(data),
              loading: () => const Center(
                child: CircularProgressIndicator(
                  color: Color(0xFF00ff00),
                ),
              ),
              error: (error, stack) => Center(
                child: Text(
                  'hata: ${error.toString()}',
                  style: const TextStyle(color: Color(0xFFff4444)),
                ),
              ),
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

  Widget _buildMap(Map<String, dynamic> data) {
    final earthquakes = data['earthquakes'] as List<dynamic>;

    if (earthquakes.isEmpty) {
      return const Center(
        child: Text(
          'haritada gösterilecek deprem yok',
          style: TextStyle(color: Color(0xFF666666)),
        ),
      );
    }

    // Prepare earthquake markers
    final earthquakeMarkers = earthquakes
        .map((eq) {
          // Parse values safely with null checks
          final lat = _parseDouble(eq['latitude']);
          final lon = _parseDouble(eq['longitude']);
          final mag = _parseDouble(eq['magnitude']);

          if (lat == null || lon == null || mag == null) {
            return null; // Skip invalid entries
          }

          final color = _getMagnitudeColor(mag);
          final size = _getMarkerSize(mag);

          return Marker(
            point: LatLng(lat, lon),
            width: size,
            height: size,
            child: GestureDetector(
              onTap: () => _showEarthquakeDialog(context, eq),
              child: Container(
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: color.withValues(alpha: 0.7),
                  border: Border.all(color: Colors.white, width: 2),
                ),
              ),
            ),
          );
        })
        .whereType<Marker>()
        .toList();

    // Add user location marker if available
    if (_userLocation != null) {
      earthquakeMarkers.add(
        Marker(
          point: LatLng(_userLocation!.latitude, _userLocation!.longitude),
          width: 40,
          height: 40,
          child: Container(
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: const Color(0xFF00ffff).withValues(alpha: 0.3),
              border: Border.all(color: const Color(0xFF00ffff), width: 3),
            ),
            child: const Center(
              child: Icon(
                Icons.person_pin_circle,
                color: Color(0xFF00ffff),
                size: 24,
              ),
            ),
          ),
        ),
      );
    }

    return FlutterMap(
      mapController: _mapController,
      options: MapOptions(
        initialCenter: _userLocation != null
            ? LatLng(_userLocation!.latitude, _userLocation!.longitude)
            : const LatLng(39.0, 35.0),
        initialZoom: _userLocation != null ? 8.0 : 6.0,
        maxZoom: 18.0,
        minZoom: 3.0,
        interactionOptions: const InteractionOptions(
          flags: InteractiveFlag.pinchZoom |
                 InteractiveFlag.doubleTapZoom |
                 InteractiveFlag.drag |
                 InteractiveFlag.flingAnimation |
                 InteractiveFlag.pinchMove |
                 InteractiveFlag.doubleTapDragZoom,
        ),
      ),
      children: [
        TileLayer(
          urlTemplate: 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png',
          subdomains: const ['a', 'b', 'c', 'd'],
        ),
        MarkerLayer(markers: earthquakeMarkers),
      ],
    );
  }

  // Get user location
  Future<void> _getUserLocation() async {
    setState(() {
      _isLoadingLocation = true;
    });

    try {
      final position = await _locationService.getCurrentLocation();

      if (position != null) {
        setState(() {
          _userLocation = position;
          _isLoadingLocation = false;
        });

        // Move map to user location
        _mapController.move(
          LatLng(position.latitude, position.longitude),
          10.0,
        );

        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('konum alındı'),
              backgroundColor: Color(0xFF00ff00),
              duration: Duration(seconds: 2),
            ),
          );
        }
      } else {
        setState(() {
          _isLoadingLocation = false;
        });

        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('konum alınamadı. izinleri kontrol edin.'),
              backgroundColor: Color(0xFFff4444),
              duration: Duration(seconds: 3),
            ),
          );
        }
      }
    } catch (e) {
      setState(() {
        _isLoadingLocation = false;
      });

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('hata: $e'),
            backgroundColor: const Color(0xFFff4444),
            duration: const Duration(seconds: 3),
          ),
        );
      }
    }
  }

  Color _getMagnitudeColor(double magnitude) {
    if (magnitude >= 5.0) return const Color(0xFFff4444);
    if (magnitude >= 4.0) return const Color(0xFFff8c00);
    if (magnitude >= 3.0) return const Color(0xFFffff00);
    return const Color(0xFF00ff00);
  }

  double _getMarkerSize(double magnitude) {
    if (magnitude >= 5.0) return 20.0;
    if (magnitude >= 4.0) return 16.0;
    if (magnitude >= 3.0) return 12.0;
    return 8.0;
  }

  // Helper method to parse double values safely
  double? _parseDouble(dynamic value) {
    if (value == null) return null;
    if (value is double) return value;
    if (value is int) return value.toDouble();
    if (value is String) {
      try {
        return double.parse(value);
      } catch (e) {
        return null;
      }
    }
    return null;
  }

  void _showEarthquakeDialog(BuildContext context, Map<String, dynamic> eq) {
    final mag = _parseDouble(eq['magnitude']) ?? 0.0;
    final depth = _parseDouble(eq['depth']) ?? 0.0;

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: const Color(0xFF1a1a1a),
        title: Text(
          'M${mag.toStringAsFixed(1)}',
          style: TextStyle(
            color: _getMagnitudeColor(mag),
            fontWeight: FontWeight.bold,
          ),
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('lokasyon: ${eq['location'] ?? 'bilinmiyor'}'),
            if (eq['city'] != null && eq['city'] != '')
              Text('şehir: ${eq['city']}'),
            Text('derinlik: ${depth.toStringAsFixed(2)} km'),
            Text('kaynak: ${eq['source'] ?? 'bilinmiyor'}'),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('kapat'),
          ),
        ],
      ),
    );
  }
}
