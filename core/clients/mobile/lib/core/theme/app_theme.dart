import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'colors.dart';

/// UNIBOS app theme - terminal-style dark theme matching web UI
class UnibosTheme {
  UnibosTheme._();

  static ThemeData get darkTheme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      colorScheme: UnibosColors.darkColorScheme,
      scaffoldBackgroundColor: UnibosColors.bgBlack,

      // typography - jetbrains mono like web (using Google Fonts)
      textTheme: GoogleFonts.jetBrainsMonoTextTheme(_textTheme),
      fontFamily: GoogleFonts.jetBrainsMono().fontFamily,

      // app bar
      appBarTheme: const AppBarTheme(
        backgroundColor: UnibosColors.orange,
        foregroundColor: UnibosColors.bgBlack,
        elevation: 0,
        centerTitle: false,
        titleTextStyle: TextStyle(
          fontFamily: 'JetBrainsMono',
          fontSize: 16,
          fontWeight: FontWeight.bold,
          color: UnibosColors.bgBlack,
          letterSpacing: 1,
        ),
      ),

      // bottom navigation (Material 3 NavigationBar)
      navigationBarTheme: NavigationBarThemeData(
        height: 60,
        backgroundColor: UnibosColors.bgDark,
        indicatorColor: UnibosColors.orange.withValues(alpha: 0.2),
        iconTheme: WidgetStateProperty.resolveWith((states) {
          if (states.contains(WidgetState.selected)) {
            return const IconThemeData(color: UnibosColors.orange, size: 22);
          }
          return const IconThemeData(color: UnibosColors.gray, size: 22);
        }),
        labelTextStyle: WidgetStateProperty.resolveWith((states) {
          if (states.contains(WidgetState.selected)) {
            return const TextStyle(
              fontSize: 10,
              fontWeight: FontWeight.w600,
              color: UnibosColors.orange,
            );
          }
          return const TextStyle(
            fontSize: 10,
            fontWeight: FontWeight.normal,
            color: UnibosColors.gray,
          );
        }),
        elevation: 0,
        surfaceTintColor: Colors.transparent,
      ),

      // cards
      cardTheme: CardThemeData(
        color: UnibosColors.bgDark,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(5),
          side: const BorderSide(color: UnibosColors.darkGray),
        ),
      ),

      // elevated button (primary)
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: UnibosColors.orange,
          foregroundColor: UnibosColors.bgBlack,
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(3),
          ),
          textStyle: const TextStyle(
            fontFamily: 'JetBrainsMono',
            fontWeight: FontWeight.w500,
            letterSpacing: 0.5,
          ),
        ),
      ),

      // outlined button (secondary)
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: UnibosColors.white,
          side: const BorderSide(color: UnibosColors.darkGray),
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(3),
          ),
          textStyle: const TextStyle(
            fontFamily: 'JetBrainsMono',
            fontWeight: FontWeight.w500,
          ),
        ),
      ),

      // text button
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          foregroundColor: UnibosColors.cyan,
          textStyle: const TextStyle(
            fontFamily: 'JetBrainsMono',
          ),
        ),
      ),

      // input decoration
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: UnibosColors.bgBlack,
        contentPadding:
            const EdgeInsets.symmetric(horizontal: 12, vertical: 14),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(3),
          borderSide: const BorderSide(color: UnibosColors.darkGray),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(3),
          borderSide: const BorderSide(color: UnibosColors.darkGray),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(3),
          borderSide: const BorderSide(color: UnibosColors.orange, width: 2),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(3),
          borderSide: const BorderSide(color: UnibosColors.danger),
        ),
        labelStyle: const TextStyle(
          color: UnibosColors.gray,
          fontFamily: 'JetBrainsMono',
          fontSize: 14,
        ),
        hintStyle: const TextStyle(
          color: UnibosColors.gray,
          fontFamily: 'JetBrainsMono',
          fontSize: 14,
        ),
      ),

      // divider
      dividerTheme: const DividerThemeData(
        color: UnibosColors.darkGray,
        thickness: 1,
      ),

      // icon theme
      iconTheme: const IconThemeData(
        color: UnibosColors.orange,
        size: 24,
      ),

      // snackbar
      snackBarTheme: SnackBarThemeData(
        backgroundColor: UnibosColors.bgDark,
        contentTextStyle: const TextStyle(
          fontFamily: 'JetBrainsMono',
          color: UnibosColors.white,
        ),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(3),
          side: const BorderSide(color: UnibosColors.darkGray),
        ),
      ),

      // dialog
      dialogTheme: DialogThemeData(
        backgroundColor: UnibosColors.bgDark,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(5),
          side: const BorderSide(color: UnibosColors.orange),
        ),
        titleTextStyle: const TextStyle(
          fontFamily: 'JetBrainsMono',
          fontSize: 18,
          fontWeight: FontWeight.bold,
          color: UnibosColors.orange,
        ),
      ),

      // list tile
      listTileTheme: const ListTileThemeData(
        textColor: UnibosColors.white,
        iconColor: UnibosColors.orange,
        contentPadding: EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      ),

      // floating action button
      floatingActionButtonTheme: const FloatingActionButtonThemeData(
        backgroundColor: UnibosColors.orange,
        foregroundColor: UnibosColors.bgBlack,
      ),

      // progress indicator
      progressIndicatorTheme: const ProgressIndicatorThemeData(
        color: UnibosColors.orange,
        circularTrackColor: UnibosColors.darkGray,
      ),

      // switch
      switchTheme: SwitchThemeData(
        thumbColor: WidgetStateProperty.resolveWith((states) {
          if (states.contains(WidgetState.selected)) {
            return UnibosColors.orange;
          }
          return UnibosColors.gray;
        }),
        trackColor: WidgetStateProperty.resolveWith((states) {
          if (states.contains(WidgetState.selected)) {
            return UnibosColors.orange.withValues(alpha: 0.5);
          }
          return UnibosColors.darkGray;
        }),
      ),

      // chip
      chipTheme: ChipThemeData(
        backgroundColor: UnibosColors.bgDark,
        selectedColor: UnibosColors.orange,
        labelStyle: const TextStyle(
          fontFamily: 'JetBrainsMono',
          fontSize: 12,
          color: UnibosColors.white,
        ),
        side: const BorderSide(color: UnibosColors.darkGray),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(3),
        ),
      ),
    );
  }

  static TextTheme get _textTheme {
    return const TextTheme(
      // display styles
      displayLarge: TextStyle(
        fontSize: 32,
        fontWeight: FontWeight.bold,
        color: UnibosColors.orange,
        letterSpacing: 1,
      ),
      displayMedium: TextStyle(
        fontSize: 28,
        fontWeight: FontWeight.bold,
        color: UnibosColors.orange,
        letterSpacing: 1,
      ),
      displaySmall: TextStyle(
        fontSize: 24,
        fontWeight: FontWeight.bold,
        color: UnibosColors.orange,
      ),

      // headline styles (h1-h4 from web)
      headlineLarge: TextStyle(
        fontSize: 28,
        fontWeight: FontWeight.bold,
        color: UnibosColors.orange,
      ),
      headlineMedium: TextStyle(
        fontSize: 21,
        fontWeight: FontWeight.bold,
        color: UnibosColors.orange,
      ),
      headlineSmall: TextStyle(
        fontSize: 17.5,
        fontWeight: FontWeight.bold,
        color: UnibosColors.cyan,
      ),

      // title styles
      titleLarge: TextStyle(
        fontSize: 15.4,
        fontWeight: FontWeight.bold,
        color: UnibosColors.white,
      ),
      titleMedium: TextStyle(
        fontSize: 14,
        fontWeight: FontWeight.w600,
        color: UnibosColors.white,
      ),
      titleSmall: TextStyle(
        fontSize: 13,
        fontWeight: FontWeight.w500,
        color: UnibosColors.white,
      ),

      // body styles (base 14px from web)
      bodyLarge: TextStyle(
        fontSize: 16,
        fontWeight: FontWeight.normal,
        color: UnibosColors.white,
        height: 1.4,
      ),
      bodyMedium: TextStyle(
        fontSize: 14,
        fontWeight: FontWeight.normal,
        color: UnibosColors.white,
        height: 1.4,
      ),
      bodySmall: TextStyle(
        fontSize: 12,
        fontWeight: FontWeight.normal,
        color: UnibosColors.gray,
        height: 1.4,
      ),

      // label styles
      labelLarge: TextStyle(
        fontSize: 14,
        fontWeight: FontWeight.w500,
        color: UnibosColors.white,
      ),
      labelMedium: TextStyle(
        fontSize: 12,
        fontWeight: FontWeight.w500,
        color: UnibosColors.gray,
      ),
      labelSmall: TextStyle(
        fontSize: 11,
        fontWeight: FontWeight.w500,
        color: UnibosColors.gray,
        letterSpacing: 0.5,
      ),
    );
  }
}
