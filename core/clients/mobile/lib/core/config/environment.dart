/// server environment configuration
enum Environment {
  production,
  development,
  local,
}

class EnvironmentConfig {
  final Environment environment;
  final String baseUrl;
  final String name;

  const EnvironmentConfig._({
    required this.environment,
    required this.baseUrl,
    required this.name,
  });

  // production server
  static const production = EnvironmentConfig._(
    environment: Environment.production,
    baseUrl: 'https://recaria.org',
    name: 'production',
  );

  // local development
  static const development = EnvironmentConfig._(
    environment: Environment.development,
    baseUrl: 'http://localhost:8000',
    name: 'development',
  );

  // custom node (can be set dynamically)
  static EnvironmentConfig customNode(String hostname) {
    return EnvironmentConfig._(
      environment: Environment.local,
      baseUrl: 'http://$hostname:8000',
      name: hostname,
    );
  }

  // api endpoints
  String get apiBaseUrl => '$baseUrl/api/v1';
  String get authUrl => '$apiBaseUrl/auth';
  String get healthUrl => '$baseUrl/health';

  bool get isProduction => environment == Environment.production;
  bool get isDevelopment => environment == Environment.development;
}
