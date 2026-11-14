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
          _buildActiveStep(item),
          if (item != productionJourneyItems.last) const SizedBox(height: 12),
        ],
      ],
    );
  }

  Widget _buildActiveStep(ProductionJourneyItem item) {
    return switch (item.step) {
      ProductionJourneyStep.moodCheckIn => ProductionMoodCheckIn(
        item: item,
        onChanged: (mood) => setState(() => _selectedMood = mood),
      ),
      ProductionJourneyStep.characterSelection => ProductionCharacterSelection(
        item: item,
        onChanged: (character) =>
            setState(() => _selectedCharacter = character),
      ),
      ProductionJourneyStep.dailyAdvice => ProductionDailyAdvice(
        item: item,
        selectedMood: _selectedMood,
        selectedCharacter: _selectedCharacter,
      ),
      _ => throw StateError('Inactive step in the Public Beta journey.'),
    };
  }
}
