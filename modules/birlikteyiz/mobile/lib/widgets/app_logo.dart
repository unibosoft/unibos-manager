import 'package:flutter/material.dart';

class AppLogo extends StatelessWidget {
  final double size;

  const AppLogo({
    super.key,
    this.size = 32,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Image.asset(
          'assets/icon/app_icon.png',
          width: size,
          height: size,
          fit: BoxFit.contain,
        ),
        const SizedBox(width: 12),
        Text(
          'birlikteyiz',
          style: TextStyle(
            fontSize: size * 0.7,
            fontWeight: FontWeight.w600,
            color: const Color(0xFFC9D1D9),
            letterSpacing: 0.5,
          ),
        ),
      ],
    );
  }
}
