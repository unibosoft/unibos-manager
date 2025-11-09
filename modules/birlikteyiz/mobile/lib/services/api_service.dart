import 'dart:io';
import 'package:dio/dio.dart';
import 'package:retrofit/retrofit.dart';
import '../models/earthquake.dart';

part 'api_service.g.dart';

@RestApi(baseUrl: "http://localhost:8000/birlikteyiz/api/")
abstract class ApiService {
  factory ApiService(Dio dio, {String baseUrl}) = _ApiService;

  // Get recent earthquakes
  @GET("/earthquakes/recent/")
  Future<EarthquakeResponse> getRecentEarthquakes(
    @Query("limit") int limit,
  );

  // Get earthquakes with filters
  @GET("/earthquakes/")
  Future<EarthquakeResponse> getEarthquakes({
    @Query("days") int? days,
    @Query("min_magnitude") double? minMagnitude,
    @Query("source") String? source,
    @Query("city") String? city,
    @Query("limit") int? limit,
  });

  // Get earthquake statistics
  @GET("/earthquakes/stats/")
  Future<EarthquakeStats> getStats();

  // Get single earthquake
  @GET("/earthquakes/{id}/")
  Future<Earthquake> getEarthquake(@Path("id") int id);
}

// API Client Configuration
class ApiClient {
  // Use 10.0.2.2 for Android emulator to connect to host machine's localhost
  // Use localhost for iOS simulator
  static String get baseUrl {
    if (Platform.isAndroid) {
      return "http://10.0.2.2:8000";
    }
    return "http://localhost:8000";
  }

  static const String apiPath = "/birlikteyiz/api";

  static Dio createDio() {
    final dio = Dio(BaseOptions(
      baseUrl: baseUrl + apiPath,
      connectTimeout: const Duration(seconds: 30),
      receiveTimeout: const Duration(seconds: 30),
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    ));

    // Add interceptors for logging
    dio.interceptors.add(LogInterceptor(
      request: true,
      requestHeader: true,
      requestBody: true,
      responseHeader: true,
      responseBody: true,
      error: true,
    ));

    return dio;
  }

  static ApiService createApiService() {
    final dio = createDio();
    return ApiService(dio, baseUrl: baseUrl + apiPath);
  }
}
