import 'package:flutter/material.dart';

/// UNIBOS color palette - matches web UI (base.css)
class UnibosColors {
  UnibosColors._();

  // background colors
  static const Color bgBlack = Color(0xFF000000);
  static const Color bgDark = Color(0xFF0A0A0A);

  // primary colors
  static const Color orange = Color(0xFFFF8C00);
  static const Color orangeBright = Color(0xFFFFA500);

  // accent colors
  static const Color green = Color(0xFF00FF00);
  static const Color cyan = Color(0xFF00FFFF);
  static const Color yellow = Color(0xFFFFFF00);
  static const Color magenta = Color(0xFFFF00FF);

  // neutral colors
  static const Color white = Color(0xFFFFFFFF);
  static const Color gray = Color(0xFF808080);
  static const Color darkGray = Color(0xFF404040);
  static const Color red = Color(0xFFFF0000);

  // semantic colors
  static const Color success = Color(0xFF4CAF50);
  static const Color warning = Color(0xFFFFC107);
  static const Color danger = Color(0xFFDC3545);
  static const Color info = Color(0xFF17A2B8);

  // gradient backgrounds (like web sidebar)
  static const LinearGradient darkGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [Color(0xFF1A1A1A), Color(0xFF2A2A2A)],
  );

  // color scheme for theme
  static ColorScheme get darkColorScheme => const ColorScheme.dark(
        primary: orange,
        primaryContainer: orangeBright,
        secondary: cyan,
        secondaryContainer: Color(0xFF00CCCC),
        surface: bgDark,
        error: danger,
        onPrimary: bgBlack,
        onSecondary: bgBlack,
        onSurface: white,
        onError: white,
      );
}
