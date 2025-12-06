import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:logger/logger.dart';
import '../config/app_config.dart';
import 'auth_interceptor.dart';

final logger = Logger(
  printer: PrettyPrinter(
    methodCount: 0,
    errorMethodCount: 5,
    lineLength: 80,
    colors: true,
    printEmojis: true,
  ),
);

/// dio client provider
final dioProvider = Provider<Dio>((ref) {
  final config = ref.watch(appConfigProvider);
  final dio = Dio(BaseOptions(
    baseUrl: config.environment.apiBaseUrl,
    connectTimeout: const Duration(seconds: 30),
    receiveTimeout: const Duration(seconds: 30),
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
  ));

  // add auth interceptor
  dio.interceptors.add(AuthInterceptor(ref));

  // add logging interceptor (only in debug mode)
  dio.interceptors.add(LogInterceptor(
    requestBody: true,
    responseBody: true,
    logPrint: (obj) => logger.d(obj),
  ));

  return dio;
});

/// api client for making http requests
class ApiClient {
  final Dio _dio;

  ApiClient(this._dio);

  // generic GET request
  Future<T> get<T>(
    String path, {
    Map<String, dynamic>? queryParameters,
    T Function(dynamic)? fromJson,
  }) async {
    try {
      final response = await _dio.get(path, queryParameters: queryParameters);
      if (fromJson != null) {
        return fromJson(response.data);
      }
      return response.data as T;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  // generic POST request
  Future<T> post<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    T Function(dynamic)? fromJson,
  }) async {
    try {
      final response = await _dio.post(
        path,
        data: data,
        queryParameters: queryParameters,
      );
      if (fromJson != null) {
        return fromJson(response.data);
      }
      return response.data as T;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  // generic PUT request
  Future<T> put<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    T Function(dynamic)? fromJson,
  }) async {
    try {
      final response = await _dio.put(
        path,
        data: data,
        queryParameters: queryParameters,
      );
      if (fromJson != null) {
        return fromJson(response.data);
      }
      return response.data as T;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  // generic PATCH request
  Future<T> patch<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    T Function(dynamic)? fromJson,
  }) async {
    try {
      final response = await _dio.patch(
        path,
        data: data,
        queryParameters: queryParameters,
      );
      if (fromJson != null) {
        return fromJson(response.data);
      }
      return response.data as T;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  // generic DELETE request
  Future<T> delete<T>(
    String path, {
    Map<String, dynamic>? queryParameters,
    T Function(dynamic)? fromJson,
  }) async {
    try {
      final response =
          await _dio.delete(path, queryParameters: queryParameters);
      if (fromJson != null) {
        return fromJson(response.data);
      }
      return response.data as T;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  ApiException _handleError(DioException e) {
    switch (e.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        return ApiException(
          message: 'connection timeout',
          statusCode: null,
        );
      case DioExceptionType.badResponse:
        final statusCode = e.response?.statusCode;
        final data = e.response?.data;
        String message = 'server error';

        // Handle string responses (like plain "Server Error")
        if (data is String && data.isNotEmpty) {
          message = data.toLowerCase();
        } else if (data is Map) {
          // UNIBOS API format: {"error": true, "message": "...", "details": {...}}
          if (data.containsKey('message')) {
            message = data['message'].toString();
          } else if (data.containsKey('detail')) {
            message = data['detail'].toString();
          }
          // Check nested details for validation errors
          if (data.containsKey('details') && data['details'] is Map) {
            final details = data['details'] as Map;
            if (details.containsKey('detail')) {
              message = details['detail'].toString();
            } else {
              // Collect field-specific validation errors
              final errors = <String>[];
              details.forEach((key, value) {
                if (value is List && value.isNotEmpty) {
                  // Format: "password: [error1, error2]"
                  errors.add('$key: ${value.first}');
                } else if (value is String) {
                  errors.add('$key: $value');
                }
              });
              if (errors.isNotEmpty) {
                message = errors.join('\n');
              }
            }
          }
        }

        // Make error messages user-friendly
        if (statusCode == 401) {
          message = 'invalid username or password';
        } else if (statusCode == 500 && message.contains('json parse')) {
          message = 'invalid characters in credentials';
        }

        return ApiException(message: message, statusCode: statusCode);
      case DioExceptionType.cancel:
        return ApiException(message: 'request cancelled', statusCode: null);
      case DioExceptionType.connectionError:
        return ApiException(
          message: 'connection error - check your network',
          statusCode: null,
        );
      default:
        return ApiException(
          message: e.message ?? 'network error',
          statusCode: null,
        );
    }
  }
}

/// api exception
class ApiException implements Exception {
  final String message;
  final int? statusCode;

  ApiException({required this.message, this.statusCode});

  bool get isUnauthorized => statusCode == 401;
  bool get isForbidden => statusCode == 403;
  bool get isNotFound => statusCode == 404;
  bool get isServerError => statusCode != null && statusCode! >= 500;

  @override
  String toString() => 'ApiException: $message (status: $statusCode)';
}

/// api client provider
final apiClientProvider = Provider<ApiClient>((ref) {
  final dio = ref.watch(dioProvider);
  return ApiClient(dio);
});
