import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'environment.dart';

/// app configuration provider
final appConfigProvider = StateNotifierProvider<AppConfigNotifier, AppConfig>(
  (ref) => AppConfigNotifier(),
);

class AppConfig {
  final EnvironmentConfig environment;
  final String? customNodeUrl;
  final bool isDarkMode;
  final String language;

  const AppConfig({
    required this.environment,
    this.customNodeUrl,
    this.isDarkMode = true,
    this.language = 'en',
  });

  AppConfig copyWith({
    EnvironmentConfig? environment,
    String? customNodeUrl,
    bool? isDarkMode,
    String? language,
  }) {
    return AppConfig(
      environment: environment ?? this.environment,
      customNodeUrl: customNodeUrl ?? this.customNodeUrl,
      isDarkMode: isDarkMode ?? this.isDarkMode,
      language: language ?? this.language,
    );
  }
}

class AppConfigNotifier extends StateNotifier<AppConfig> {
  AppConfigNotifier()
      : super(const AppConfig(
          environment: EnvironmentConfig.production,
        ));

  static const _envKey = 'environment';
  static const _customNodeKey = 'custom_node_url';
  static const _darkModeKey = 'dark_mode';
  static const _languageKey = 'language';

  Future<void> loadFromPreferences() async {
    final prefs = await SharedPreferences.getInstance();
    final envName = prefs.getString(_envKey) ?? 'production';
    final customNode = prefs.getString(_customNodeKey);
    final darkMode = prefs.getBool(_darkModeKey) ?? true;
    final language = prefs.getString(_languageKey) ?? 'en';

    EnvironmentConfig env;
    if (envName == 'development') {
      env = EnvironmentConfig.development;
    } else if (envName == 'custom' && customNode != null) {
      env = EnvironmentConfig.customNode(customNode);
    } else {
      env = EnvironmentConfig.production;
    }

    state = AppConfig(
      environment: env,
      customNodeUrl: customNode,
      isDarkMode: darkMode,
      language: language,
    );
  }

  Future<void> setEnvironment(EnvironmentConfig env) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_envKey, env.name);
    state = state.copyWith(environment: env);
  }

  Future<void> setCustomNode(String hostname) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_envKey, 'custom');
    await prefs.setString(_customNodeKey, hostname);
    state = state.copyWith(
      environment: EnvironmentConfig.customNode(hostname),
      customNodeUrl: hostname,
    );
  }

  Future<void> setDarkMode(bool value) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_darkModeKey, value);
    state = state.copyWith(isDarkMode: value);
  }

  Future<void> setLanguage(String lang) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_languageKey, lang);
    state = state.copyWith(language: lang);
  }
}
