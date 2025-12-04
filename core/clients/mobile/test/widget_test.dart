// Basic Flutter widget test for UNIBOS Mobile

import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:unibos_mobile/app.dart';

void main() {
  testWidgets('App loads smoke test', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(
      const ProviderScope(
        child: UnibosApp(),
      ),
    );

    // Verify app loads (splash screen shows)
    expect(find.text('unibos'), findsOneWidget);
  });
}
