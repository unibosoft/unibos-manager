import 'dart:convert';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// unibos version information from core VERSION.json
class VersionInfo {
  final int major;
  final int minor;
  final int patch;
  final String build;
  final String semantic;
  final String full;
  final String short;
  final String compact;
  final String buildDate;
  final String buildTime;
  final String codename;
  final String releaseType;

  const VersionInfo({
    required this.major,
    required this.minor,
    required this.patch,
    required this.build,
    required this.semantic,
    required this.full,
    required this.short,
    required this.compact,
    required this.buildDate,
    required this.buildTime,
    required this.codename,
    required this.releaseType,
  });

  /// fallback version if file read fails
  factory VersionInfo.fallback() {
    return const VersionInfo(
      major: 1,
      minor: 1,
      patch: 4,
      build: '20251204072502',
      semantic: '1.1.4',
      full: '1.1.4+build.20251204072502',
      short: 'v1.1.4',
      compact: 'v1.1.4',
      buildDate: '2025-12-04',
      buildTime: '07:25:02',
      codename: 'Phoenix Rising',
      releaseType: 'stable',
    );
  }

  factory VersionInfo.fromJson(Map<String, dynamic> json) {
    final version = json['version'] as Map<String, dynamic>;
    final display = json['display'] as Map<String, dynamic>;
    final buildInfo = json['build_info'] as Map<String, dynamic>;
    final releaseInfo = json['release_info'] as Map<String, dynamic>? ?? {};

    return VersionInfo(
      major: version['major'] as int,
      minor: version['minor'] as int,
      patch: version['patch'] as int,
      build: version['build'] as String,
      semantic: display['semantic'] as String,
      full: display['full'] as String,
      short: display['short'] as String,
      compact: display['compact'] as String,
      buildDate: buildInfo['date'] as String,
      buildTime: buildInfo['time'] as String,
      codename: releaseInfo['codename'] as String? ?? 'Phoenix Rising',
      releaseType: releaseInfo['release_type'] as String? ?? 'stable',
    );
  }

  /// display version for ui (e.g., "v1.1.4")
  String get displayVersion => 'v$semantic';

  /// full version with build (e.g., "v1.1.4 (20251204072502)")
  String get fullDisplayVersion => 'v$semantic ($build)';

  /// app store version string (e.g., "1.1.4")
  String get appStoreVersion => semantic;

  /// build number for app store (integer from timestamp)
  int get buildNumber => int.tryParse(build) ?? 1;
}

/// version info provider - loads from bundled VERSION.json
final versionInfoProvider = FutureProvider<VersionInfo>((ref) async {
  try {
    final jsonString = await rootBundle.loadString('assets/VERSION.json');
    final json = jsonDecode(jsonString) as Map<String, dynamic>;
    return VersionInfo.fromJson(json);
  } catch (e) {
    // fallback to hardcoded version if file not found
    return VersionInfo.fallback();
  }
});

/// synchronous version info (use after initial load)
final versionInfoStateProvider = StateProvider<VersionInfo>((ref) {
  return VersionInfo.fallback();
});
