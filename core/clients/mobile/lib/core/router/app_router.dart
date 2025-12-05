import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../auth/auth_provider.dart';
import '../theme/colors.dart';
import '../version/version_info.dart';
import '../../features/auth/screens/login_screen.dart';
import '../../features/dashboard/screens/dashboard_screen.dart';
import '../../features/settings/screens/settings_screen.dart';

/// route paths
class AppRoutes {
  AppRoutes._();

  static const String splash = '/';
  static const String login = '/login';
  static const String register = '/register';
  static const String dashboard = '/dashboard';
  static const String settings = '/settings';
  static const String profile = '/profile';

  // module routes
  static const String currencies = '/modules/currencies';
  static const String movies = '/modules/movies';
  static const String music = '/modules/music';
  static const String birlikteyiz = '/modules/birlikteyiz';
  static const String documents = '/modules/documents';
  static const String cctv = '/modules/cctv';
  static const String restopos = '/modules/restopos';
  static const String wimm = '/modules/wimm';
  static const String wims = '/modules/wims';
  static const String personalInflation = '/modules/personal-inflation';
  static const String solitaire = '/modules/solitaire';
  static const String store = '/modules/store';
  static const String recaria = '/modules/recaria';
}

/// router provider
final routerProvider = Provider<GoRouter>((ref) {
  final authState = ref.watch(authStateProvider);

  return GoRouter(
    initialLocation: AppRoutes.splash,
    debugLogDiagnostics: true,
    redirect: (context, state) {
      final isAuthenticated = authState.isAuthenticated;
      final isLoggingIn = state.matchedLocation == AppRoutes.login;
      final isRegistering = state.matchedLocation == AppRoutes.register;
      final isSplash = state.matchedLocation == AppRoutes.splash;

      // if on splash and initial, stay there (app will redirect after checking auth)
      if (isSplash && authState.status == AuthStatus.initial) {
        return null;
      }

      // if not authenticated and not on login/register, go to login
      if (!isAuthenticated && !isLoggingIn && !isRegistering) {
        return AppRoutes.login;
      }

      // if authenticated and on login/register, go to dashboard
      if (isAuthenticated && (isLoggingIn || isRegistering || isSplash)) {
        return AppRoutes.dashboard;
      }

      return null;
    },
    routes: [
      // splash screen
      GoRoute(
        path: AppRoutes.splash,
        builder: (context, state) => const SplashScreen(),
      ),

      // auth routes
      GoRoute(
        path: AppRoutes.login,
        builder: (context, state) => const LoginScreen(),
      ),

      // main app routes with bottom navigation
      ShellRoute(
        builder: (context, state, child) {
          return MainShell(child: child);
        },
        routes: [
          GoRoute(
            path: AppRoutes.dashboard,
            pageBuilder: (context, state) => const NoTransitionPage(
              child: DashboardScreen(),
            ),
          ),
          GoRoute(
            path: AppRoutes.settings,
            pageBuilder: (context, state) => const NoTransitionPage(
              child: SettingsScreen(),
            ),
          ),
        ],
      ),

      // module routes (placeholder for now)
      GoRoute(
        path: '/modules/:moduleId',
        builder: (context, state) {
          final moduleId = state.pathParameters['moduleId'] ?? '';
          return ModulePlaceholderScreen(moduleId: moduleId);
        },
      ),
    ],
  );
});

/// splash screen while checking auth
class SplashScreen extends ConsumerStatefulWidget {
  const SplashScreen({super.key});

  @override
  ConsumerState<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends ConsumerState<SplashScreen> {
  @override
  void initState() {
    super.initState();
    _checkAuthAndNavigate();
  }

  Future<void> _checkAuthAndNavigate() async {
    // small delay for splash effect
    await Future.delayed(const Duration(milliseconds: 1500));

    if (!mounted) return;

    // for now, just set unauthenticated to go to login
    // TODO: check stored token and validate
    ref.read(authStateProvider.notifier).setUnauthenticated();
  }

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              '🦄',
              style: TextStyle(fontSize: 64),
            ),
            SizedBox(height: 16),
            Text(
              'unibos',
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
              ),
            ),
            SizedBox(height: 32),
            CircularProgressIndicator(),
          ],
        ),
      ),
    );
  }
}

/// main shell with bottom navigation and shared app bar
class MainShell extends ConsumerWidget {
  final Widget child;

  const MainShell({super.key, required this.child});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authStateProvider);

    return Scaffold(
      appBar: AppBar(
        toolbarHeight: 36,
        title: Row(
          children: [
            const Text('unibos'),
            const SizedBox(width: 8),
            ref.watch(versionInfoProvider).when(
                  data: (version) => Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                    decoration: BoxDecoration(
                      color: UnibosColors.bgBlack.withValues(alpha: 0.2),
                      borderRadius: BorderRadius.circular(3),
                    ),
                    child: Text(
                      version.displayVersion,
                      style: const TextStyle(
                        fontSize: 10,
                        fontWeight: FontWeight.normal,
                      ),
                    ),
                  ),
                  loading: () => Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                    decoration: BoxDecoration(
                      color: UnibosColors.bgBlack.withValues(alpha: 0.2),
                      borderRadius: BorderRadius.circular(3),
                    ),
                    child: const Text(
                      '...',
                      style: TextStyle(
                        fontSize: 10,
                        fontWeight: FontWeight.normal,
                      ),
                    ),
                  ),
                  error: (_, __) => Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                    decoration: BoxDecoration(
                      color: UnibosColors.bgBlack.withValues(alpha: 0.2),
                      borderRadius: BorderRadius.circular(3),
                    ),
                    child: Text(
                      VersionInfo.fallback().displayVersion,
                      style: const TextStyle(
                        fontSize: 10,
                        fontWeight: FontWeight.normal,
                      ),
                    ),
                  ),
                ),
          ],
        ),
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 12),
            child: Row(
              children: [
                const Icon(
                  Icons.person,
                  size: 16,
                  color: UnibosColors.bgBlack,
                ),
                const SizedBox(width: 4),
                Text(
                  authState.username ?? 'user',
                  style: const TextStyle(
                    fontSize: 12,
                    color: UnibosColors.bgBlack,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
      body: child,
      bottomNavigationBar: NavigationBar(
        height: 60,
        selectedIndex: _calculateSelectedIndex(context),
        onDestinationSelected: (index) => _onItemTapped(index, context),
        labelBehavior: NavigationDestinationLabelBehavior.alwaysShow,
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.dashboard_outlined),
            selectedIcon: Icon(Icons.dashboard),
            label: 'Dashboard',
          ),
          NavigationDestination(
            icon: Icon(Icons.settings_outlined),
            selectedIcon: Icon(Icons.settings),
            label: 'Settings',
          ),
        ],
      ),
    );
  }

  int _calculateSelectedIndex(BuildContext context) {
    final location = GoRouterState.of(context).matchedLocation;
    if (location.startsWith(AppRoutes.dashboard)) return 0;
    if (location.startsWith(AppRoutes.settings)) return 1;
    return 0;
  }

  void _onItemTapped(int index, BuildContext context) {
    switch (index) {
      case 0:
        context.go(AppRoutes.dashboard);
        break;
      case 1:
        context.go(AppRoutes.settings);
        break;
    }
  }
}

/// placeholder for module screens
class ModulePlaceholderScreen extends StatelessWidget {
  final String moduleId;

  const ModulePlaceholderScreen({super.key, required this.moduleId});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(moduleId),
      ),
      body: Center(
        child: Text(
          '$moduleId module\n(coming soon)',
          textAlign: TextAlign.center,
          style: Theme.of(context).textTheme.headlineMedium,
        ),
      ),
    );
  }
}
