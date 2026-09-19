import 'package:flutter/material.dart';

import '../core/production_journey_step.dart';

class ProductionJourneyOverview extends StatelessWidget {
  const ProductionJourneyOverview({super.key});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        for (final item in productionJourneyItems) ...[
          _JourneyCard(item: item),
          if (item != productionJourneyItems.last) const SizedBox(height: 12),
        ],
      ],
    );
  }
}

class _JourneyCard extends StatelessWidget {
  const _JourneyCard({required this.item});

  final ProductionJourneyItem item;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final optionalLabel = item.isOptional ? '\u3001\u4efb\u610f' : '';
    final semanticsLabel =
        '${item.order}. ${item.title}$optionalLabel\u3002${item.description}';

    return Semantics(
      container: true,
      label: semanticsLabel,
      child: ExcludeSemantics(
        child: Card(
          margin: EdgeInsets.zero,
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                SizedBox(
                  width: 32,
                  child: Text(
                    '${item.order}.',
                    style: theme.textTheme.titleMedium,
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(item.title, style: theme.textTheme.titleMedium),
                      if (item.isOptional) ...[
                        const SizedBox(height: 4),
                        Text('\u4efb\u610f', style: theme.textTheme.labelLarge),
                      ],
                      const SizedBox(height: 6),
                      Text(item.description, style: theme.textTheme.bodyMedium),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
