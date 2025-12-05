import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'app.dart';
import 'core/config/app_config.dart';
import 'core/auth/auth_service.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // set preferred orientations
  await SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
    DeviceOrientation.portraitDown,
  ]);

  // set system ui overlay style (status bar)
  SystemChrome.setSystemUIOverlayStyle(const SystemUiOverlayStyle(
    statusBarColor: Colors.transparent,
    statusBarIconBrightness: Brightness.light,
    systemNavigationBarColor: Colors.black,
    systemNavigationBarIconBrightness: Brightness.light,
  ));

  // create container for initialization
  final container = ProviderContainer();

  // load config from preferences
  await container.read(appConfigProvider.notifier).loadFromPreferences();

  // restore auth state
  await container.read(authServiceProvider).restoreAuthState();

  runApp(
    UncontrolledProviderScope(
      container: container,
      child: const UnibosApp(),
    ),
  );
}
