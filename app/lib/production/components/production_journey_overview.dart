import 'package:flutter/material.dart';

import '../core/production_character.dart';
import '../core/production_journey_step.dart';
import '../core/production_mood.dart';
import 'production_character_selection.dart';
import 'production_daily_advice.dart';
import 'production_mood_check_in.dart';

class ProductionJourneyOverview extends StatefulWidget {
  const ProductionJourneyOverview({super.key});

  @override
  State<ProductionJourneyOverview> createState() =>
      _ProductionJourneyOverviewState();
}

class _ProductionJourneyOverviewState extends State<ProductionJourneyOverview> {
  ProductionMood? _selectedMood;
  ProductionCharacter? _selectedCharacter;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        for (final item in productionJourneyItems) ...[
          if (item.step == ProductionJourneyStep.moodCheckIn)
            ProductionMoodCheckIn(
              item: item,
              onChanged: (mood) => setState(() => _selectedMood = mood),
            )
          else if (item.step == ProductionJourneyStep.characterSelection)
            ProductionCharacterSelection(
              item: item,
              onChanged: (character) =>
                  setState(() => _selectedCharacter = character),
            )
          else if (item.step == ProductionJourneyStep.dailyAdvice)
            ProductionDailyAdvice(
              item: item,
              selectedMood: _selectedMood,
              selectedCharacter: _selectedCharacter,
            )
          else
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
