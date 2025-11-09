import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'screens/home_screen.dart';
import 'services/notification_service.dart';
import 'theme/app_theme.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // initialize notification service
  final notificationService = NotificationService();
  await notificationService.initialize();

  // start polling for new earthquakes (every 30 seconds for testing, change to 5 minutes in production)
  notificationService.startPolling(interval: const Duration(seconds: 30));

  runApp(
    const ProviderScope(
      child: BirlikteyizApp(),
    ),
  );
}

class BirlikteyizApp extends StatelessWidget {
  const BirlikteyizApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'birlikteyiz',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.darkTheme,
      home: const HomeScreen(),
    );
  }
}
