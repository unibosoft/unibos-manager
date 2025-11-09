import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/earthquake.dart';
import '../services/api_service.dart';

// API Service Provider
final apiServiceProvider = Provider<ApiService>((ref) {
  return ApiClient.createApiService();
});

// Earthquakes Provider with filters
final earthquakesProvider = FutureProvider.family<List<Earthquake>, (int, double)>(
  (ref, params) async {
    final (days, minMagnitude) = params;
    final apiService = ref.watch(apiServiceProvider);

    try {
      final response = await apiService.getEarthquakes(
        days: days,
        minMagnitude: minMagnitude,
        limit: 100,
      );
      return response.results;
    } catch (e) {
      throw Exception('veri çekilemedi: $e');
    }
  },
);

// Recent Earthquakes Provider
final recentEarthquakesProvider = FutureProvider<List<Earthquake>>((ref) async {
  final apiService = ref.watch(apiServiceProvider);

  try {
    final response = await apiService.getRecentEarthquakes(50);
    return response.results;
  } catch (e) {
    throw Exception('son depremler çekilemedi: $e');
  }
});

// Earthquake Stats Provider
final earthquakeStatsProvider = FutureProvider<EarthquakeStats>((ref) async {
  final apiService = ref.watch(apiServiceProvider);

  try {
    return await apiService.getStats();
  } catch (e) {
    throw Exception('istatistikler çekilemedi: $e');
  }
});

// Map Data Provider
final mapDataProvider = FutureProvider.family<Map<String, dynamic>, (int, double)>(
  (ref, params) async {
    final (days, minMagnitude) = params;
    final apiService = ref.watch(apiServiceProvider);

    try {
      final response = await apiService.getEarthquakes(
        days: days,
        minMagnitude: minMagnitude,
        limit: 1000, // High limit for map display
      );

      // Convert to map format expected by the UI
      return {
        'earthquakes': response.results.map((e) => e.toJson()).toList(),
        'count': response.count,
      };
    } catch (e) {
      throw Exception('harita verisi çekilemedi: $e');
    }
  },
);

// Single Earthquake Provider
final earthquakeDetailProvider = FutureProvider.family<Earthquake, int>(
  (ref, id) async {
    final apiService = ref.watch(apiServiceProvider);

    try {
      return await apiService.getEarthquake(id);
    } catch (e) {
      throw Exception('deprem detayı çekilemedi: $e');
    }
  },
);
