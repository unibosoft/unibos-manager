import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../core/theme/colors.dart';
import '../../../shared/models/module.dart';

/// module card widget for dashboard grid
class ModuleCard extends StatelessWidget {
  final UnibosModule module;

  const ModuleCard({super.key, required this.module});

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: module.isEnabled ? () => context.push(module.route) : null,
        borderRadius: BorderRadius.circular(5),
        splashColor: UnibosColors.orange.withValues(alpha: 0.2),
        highlightColor: UnibosColors.orange.withValues(alpha: 0.1),
        child: Container(
          decoration: BoxDecoration(
            color: UnibosColors.bgDark,
            borderRadius: BorderRadius.circular(5),
            border: Border.all(
              color: module.isEnabled
                  ? UnibosColors.darkGray
                  : UnibosColors.darkGray.withValues(alpha: 0.5),
            ),
          ),
          child: Opacity(
            opacity: module.isEnabled ? 1.0 : 0.5,
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  // module icon
                  Text(
                    module.icon,
                    style: const TextStyle(fontSize: 36),
                  ),
                  const SizedBox(height: 12),

                  // module name
                  Text(
                    module.name,
                    textAlign: TextAlign.center,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          color: UnibosColors.orange,
                          fontWeight: FontWeight.bold,
                        ),
                  ),
                  const SizedBox(height: 4),

                  // module description
                  Text(
                    module.description,
                    textAlign: TextAlign.center,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: UnibosColors.gray,
                          fontSize: 11,
                        ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
