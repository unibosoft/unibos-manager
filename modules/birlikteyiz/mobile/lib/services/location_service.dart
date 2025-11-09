import 'package:geolocator/geolocator.dart';
import 'dart:math' show sqrt, asin;

class LocationService {
  static final LocationService _instance = LocationService._internal();
  factory LocationService() => _instance;
  LocationService._internal();

  Position? _currentPosition;
  bool _permissionGranted = false;

  // get current user location
  Future<Position?> getCurrentLocation() async {
    try {
      // check if location services are enabled
      bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
      if (!serviceEnabled) {
        print('📍 Location services are disabled');
        return null;
      }

      // check permission status using Geolocator
      LocationPermission permission = await Geolocator.checkPermission();

      if (permission == LocationPermission.denied) {
        print('📍 Location permission denied, requesting...');
        permission = await Geolocator.requestPermission();

        if (permission == LocationPermission.denied) {
          print('📍 Location permission denied by user');
          _permissionGranted = false;
          return null;
        }
      }

      if (permission == LocationPermission.deniedForever) {
        print('📍 Location permission permanently denied');
        _permissionGranted = false;
        return null;
      }

      _permissionGranted = true;
      print('📍 Location permission granted');

      // get current position
      _currentPosition = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high,
        timeLimit: const Duration(seconds: 10),
      );

      print('📍 Location obtained: ${_currentPosition?.latitude}, ${_currentPosition?.longitude}');
      return _currentPosition;
    } catch (e) {
      print('📍 Error getting location: $e');
      return null;
    }
  }

  // get last known position
  Position? get lastKnownPosition => _currentPosition;

  // check if permission is granted
  bool get hasPermission => _permissionGranted;

  // calculate distance between two points using haversine formula
  // returns distance in kilometers
  double calculateDistance(
    double lat1,
    double lon1,
    double lat2,
    double lon2,
  ) {
    const double earthRadius = 6371; // km

    final dLat = _toRadians(lat2 - lat1);
    final dLon = _toRadians(lon2 - lon1);

    final a = (sin(dLat / 2) * sin(dLat / 2)) +
        (cos(_toRadians(lat1)) *
            cos(_toRadians(lat2)) *
            sin(dLon / 2) *
            sin(dLon / 2));

    final c = 2 * asin(sqrt(a));

    return earthRadius * c;
  }

  double _toRadians(double degrees) {
    return degrees * (3.141592653589793 / 180.0);
  }

  double sin(double x) {
    return _taylorSin(x);
  }

  double cos(double x) {
    return _taylorCos(x);
  }

  // taylor series approximation for sin
  double _taylorSin(double x) {
    double sum = 0;
    double term = x;
    int n = 1;

    while (term.abs() > 1e-10 && n < 20) {
      sum += term;
      term *= -x * x / ((2 * n) * (2 * n + 1));
      n++;
    }

    return sum;
  }

  // taylor series approximation for cos
  double _taylorCos(double x) {
    double sum = 1;
    double term = 1;
    int n = 1;

    while (term.abs() > 1e-10 && n < 20) {
      term *= -x * x / ((2 * n - 1) * (2 * n));
      sum += term;
      n++;
    }

    return sum;
  }

  // calculate distance from user's current location to a point
  double? distanceFromUser(double lat, double lon) {
    if (_currentPosition == null) return null;

    return calculateDistance(
      _currentPosition!.latitude,
      _currentPosition!.longitude,
      lat,
      lon,
    );
  }

  // format distance for display
  String formatDistance(double distanceKm) {
    if (distanceKm < 1) {
      return '${(distanceKm * 1000).round()} m';
    } else if (distanceKm < 10) {
      return '${distanceKm.toStringAsFixed(1)} km';
    } else {
      return '${distanceKm.round()} km';
    }
  }
}
