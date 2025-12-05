/// Typing Indicator Widget
///
/// Animated indicator showing who is typing.

import 'package:flutter/material.dart';
import '../../../core/theme/colors.dart';

class TypingIndicator extends StatefulWidget {
  final List<String> usernames;

  const TypingIndicator({
    super.key,
    required this.usernames,
  });

  @override
  State<TypingIndicator> createState() => _TypingIndicatorState();
}

class _TypingIndicatorState extends State<TypingIndicator>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1200),
    )..repeat();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (widget.usernames.isEmpty) return const SizedBox.shrink();

    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        // Animated dots
        AnimatedBuilder(
          animation: _controller,
          builder: (context, child) {
            return Row(
              mainAxisSize: MainAxisSize.min,
              children: List.generate(3, (index) {
                final delay = index * 0.2;
                final animation = Tween<double>(begin: 0.0, end: 1.0).animate(
                  CurvedAnimation(
                    parent: _controller,
                    curve: Interval(
                      delay,
                      delay + 0.4,
                      curve: Curves.easeInOut,
                    ),
                  ),
                );

                return Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 1),
                  child: Transform.translate(
                    offset: Offset(0, -2 * animation.value),
                    child: Container(
                      width: 6,
                      height: 6,
                      decoration: const BoxDecoration(
                        color: UnibosColors.textMuted,
                        shape: BoxShape.circle,
                      ),
                    ),
                  ),
                );
              }),
            );
          },
        ),

        const SizedBox(width: 8),

        // Username(s)
        Text(
          _buildTypingText(),
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: UnibosColors.textMuted,
                fontStyle: FontStyle.italic,
              ),
        ),
      ],
    );
  }

  String _buildTypingText() {
    if (widget.usernames.isEmpty) return '';
    if (widget.usernames.length == 1) {
      return '${widget.usernames.first} is typing';
    }
    if (widget.usernames.length == 2) {
      return '${widget.usernames[0]} and ${widget.usernames[1]} are typing';
    }
    return '${widget.usernames.length} people are typing';
  }
}

/// Simple animated builder helper
class AnimatedBuilder extends StatelessWidget {
  final Animation<double> animation;
  final Widget Function(BuildContext, Widget?) builder;

  const AnimatedBuilder({
    super.key,
    required this.animation,
    required this.builder,
  });

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder2(
      animation: animation,
      builder: builder,
    );
  }
}

class AnimatedBuilder2 extends AnimatedWidget {
  final Widget Function(BuildContext, Widget?) builder;

  const AnimatedBuilder2({
    super.key,
    required super.listenable,
    required this.builder,
  });

  Animation<double> get animation => listenable as Animation<double>;

  @override
  Widget build(BuildContext context) {
    return builder(context, null);
  }
}
