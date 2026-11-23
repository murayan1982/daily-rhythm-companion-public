import 'package:flutter/material.dart';

import '../core/production_character.dart';
import '../core/production_journey_step.dart';
import '../core/production_mood.dart';
import 'production_character_selection.dart';
import 'production_daily_advice.dart';
import 'production_mood_check_in.dart';

typedef JourneyAdviceBuilder =
    Widget Function(ProductionMood? mood, ProductionCharacter? character);

class ProductionJourneyOverview extends StatefulWidget {
  const ProductionJourneyOverview({
    super.key,
    this.characterPortrait,
    this.adviceExtension,
    this.onlineAdvice,
  });

  final CharacterPortraitBuilder? characterPortrait;
  final JourneyAdviceBuilder? adviceExtension;
  final ProductionOnlineAdvice? onlineAdvice;

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
          if (item != productionJourneyItems.last) const SizedBox(height: 20),
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
        characterPortrait: widget.characterPortrait,
        onChanged: (character) =>
            setState(() => _selectedCharacter = character),
      ),
      ProductionJourneyStep.dailyAdvice => ProductionDailyAdvice(
        item: item,
        selectedMood: _selectedMood,
        selectedCharacter: _selectedCharacter,
        onlineAdvice: widget.onlineAdvice,
        extension: widget.adviceExtension?.call(
          _selectedMood,
          _selectedCharacter,
        ),
      ),
      _ => throw StateError('Inactive step in the Public Beta journey.'),
    };
  }
}
