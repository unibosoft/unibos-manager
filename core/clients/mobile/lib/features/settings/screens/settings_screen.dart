import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/theme/colors.dart';
import '../../../core/auth/auth_service.dart';
import '../../../core/config/app_config.dart';
import '../../../core/config/environment.dart';
import '../../../core/version/version_info.dart';

class SettingsScreen extends ConsumerWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final config = ref.watch(appConfigProvider);

    return ListView(
        children: [
          // server section
          _buildSectionHeader(context, 'server'),
          ListTile(
            leading: const Icon(Icons.cloud_outlined),
            title: const Text('server'),
            subtitle: Text(config.environment.name),
            trailing: const Icon(Icons.chevron_right),
            onTap: () {
              _showServerDialog(context, ref);
            },
          ),
          ListTile(
            leading: const Icon(Icons.link),
            title: const Text('server url'),
            subtitle: Text(
              config.environment.baseUrl,
              style: const TextStyle(fontSize: 12),
            ),
          ),
          const Divider(),

          // appearance section
          _buildSectionHeader(context, 'appearance'),
          SwitchListTile(
            secondary: const Icon(Icons.dark_mode),
            title: const Text('dark mode'),
            subtitle: const Text('terminal-style dark theme'),
            value: config.isDarkMode,
            onChanged: (value) {
              ref.read(appConfigProvider.notifier).setDarkMode(value);
            },
          ),
          ListTile(
            leading: const Icon(Icons.language),
            title: const Text('language'),
            subtitle: Text(config.language),
            trailing: const Icon(Icons.chevron_right),
            onTap: () {
              _showLanguageDialog(context, ref);
            },
          ),
          const Divider(),

          // about section
          _buildSectionHeader(context, 'about'),
          ref.watch(versionInfoProvider).when(
                data: (version) => ListTile(
                  leading: const Icon(Icons.info_outline),
                  title: const Text('version'),
                  subtitle: Text(version.fullDisplayVersion),
                ),
                loading: () => const ListTile(
                  leading: Icon(Icons.info_outline),
                  title: Text('version'),
                  subtitle: Text('loading...'),
                ),
                error: (_, __) => ListTile(
                  leading: const Icon(Icons.info_outline),
                  title: const Text('version'),
                  subtitle: Text(VersionInfo.fallback().displayVersion),
                ),
              ),
          ref.watch(versionInfoProvider).when(
                data: (version) => ListTile(
                  leading: const Icon(Icons.code),
                  title: Text('unibos mobile - ${version.codename}'),
                  subtitle: const Text('universal basic operating system'),
                  onTap: () {
                    showAboutDialog(
                      context: context,
                      applicationName: 'UNIBOS Mobile',
                      applicationVersion: version.fullDisplayVersion,
                      applicationIcon:
                          const Text('🦄', style: TextStyle(fontSize: 48)),
                      children: [
                        Text(
                          'Universal Basic Operating System - Mobile App\n'
                          'Release: ${version.releaseType}\n'
                          'Build: ${version.buildDate} ${version.buildTime}',
                          style: const TextStyle(color: UnibosColors.gray),
                        ),
                      ],
                    );
                  },
                ),
                loading: () => const ListTile(
                  leading: Icon(Icons.code),
                  title: Text('unibos mobile'),
                  subtitle: Text('universal basic operating system'),
                ),
                error: (_, __) => ListTile(
                  leading: const Icon(Icons.code),
                  title: const Text('unibos mobile'),
                  subtitle: const Text('universal basic operating system'),
                  onTap: () {
                    showAboutDialog(
                      context: context,
                      applicationName: 'UNIBOS Mobile',
                      applicationVersion:
                          VersionInfo.fallback().fullDisplayVersion,
                      applicationIcon:
                          const Text('🦄', style: TextStyle(fontSize: 48)),
                      children: const [
                        Text(
                          'Universal Basic Operating System - Mobile App',
                          style: TextStyle(color: UnibosColors.gray),
                        ),
                      ],
                    );
                  },
                ),
              ),
          const Divider(),

          // account section
          _buildSectionHeader(context, 'account'),
          ListTile(
            leading: const Icon(Icons.logout, color: UnibosColors.danger),
            title: const Text(
              'logout',
              style: TextStyle(color: UnibosColors.danger),
            ),
            onTap: () {
              _showLogoutDialog(context, ref);
            },
          ),
          const SizedBox(height: 32),
        ],
    );
  }

  Widget _buildSectionHeader(BuildContext context, String title) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
      child: Row(
        children: [
          Container(
            width: 4,
            height: 16,
            decoration: BoxDecoration(
              color: UnibosColors.orange,
              borderRadius: BorderRadius.circular(2),
            ),
          ),
          const SizedBox(width: 8),
          Text(
            title,
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
                  color: UnibosColors.orange,
                  fontWeight: FontWeight.bold,
                ),
          ),
        ],
      ),
    );
  }

  void _showServerDialog(BuildContext context, WidgetRef ref) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('select server'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              title: const Text('production'),
              subtitle: const Text('recaria.org'),
              onTap: () {
                ref.read(appConfigProvider.notifier).setEnvironment(
                      EnvironmentConfig.production,
                    );
                Navigator.pop(context);
              },
            ),
            ListTile(
              title: const Text('development'),
              subtitle: const Text('localhost:8000'),
              onTap: () {
                ref.read(appConfigProvider.notifier).setEnvironment(
                      EnvironmentConfig.development,
                    );
                Navigator.pop(context);
              },
            ),
            ListTile(
              title: const Text('custom node'),
              subtitle: const Text('enter hostname'),
              onTap: () {
                Navigator.pop(context);
                _showCustomNodeDialog(context, ref);
              },
            ),
          ],
        ),
      ),
    );
  }

  void _showCustomNodeDialog(BuildContext context, WidgetRef ref) {
    final controller = TextEditingController();
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('custom node'),
        content: TextField(
          controller: controller,
          decoration: const InputDecoration(
            hintText: 'hostname (e.g., unicorn-main.local)',
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              if (controller.text.isNotEmpty) {
                ref.read(appConfigProvider.notifier).setCustomNode(
                      controller.text.trim(),
                    );
              }
              Navigator.pop(context);
            },
            child: const Text('save'),
          ),
        ],
      ),
    );
  }

  void _showLanguageDialog(BuildContext context, WidgetRef ref) {
    final languages = [
      ('en', 'english', '🇬🇧'),
      ('tr', 'türkçe', '🇹🇷'),
      ('es', 'español', '🇪🇸'),
      ('fr', 'français', '🇫🇷'),
      ('de', 'deutsch', '🇩🇪'),
    ];

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('select language'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: languages.map((lang) {
            return ListTile(
              leading: Text(lang.$3, style: const TextStyle(fontSize: 24)),
              title: Text(lang.$2),
              onTap: () {
                ref.read(appConfigProvider.notifier).setLanguage(lang.$1);
                Navigator.pop(context);
              },
            );
          }).toList(),
        ),
      ),
    );
  }

  void _showLogoutDialog(BuildContext context, WidgetRef ref) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('logout'),
        content: const Text('are you sure you want to logout?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('cancel'),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: UnibosColors.danger,
            ),
            onPressed: () {
              Navigator.pop(context);
              ref.read(authServiceProvider).logout();
            },
            child: const Text('logout'),
          ),
        ],
      ),
    );
  }
}
