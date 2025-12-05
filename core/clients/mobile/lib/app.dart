import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'core/theme/app_theme.dart';
import 'core/router/app_router.dart';

/// main app widget
class UnibosApp extends ConsumerWidget {
  const UnibosApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(routerProvider);

    return MaterialApp.router(
      title: 'UNIBOS',
      debugShowCheckedModeBanner: false,
      theme: UnibosTheme.darkTheme,
      routerConfig: router,
    );
  }
}
