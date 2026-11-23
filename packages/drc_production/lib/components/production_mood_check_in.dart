import 'package:flutter/material.dart';

import '../core/production_journey_step.dart';
import '../core/production_mood.dart';

class ProductionMoodCheckIn extends StatefulWidget {
  const ProductionMoodCheckIn({required this.item, this.onChanged, super.key});

  final ProductionJourneyItem item;
  final ValueChanged<ProductionMood>? onChanged;

  @override
  State<ProductionMoodCheckIn> createState() => _ProductionMoodCheckInState();
}

class _ProductionMoodCheckInState extends State<ProductionMoodCheckIn> {
  ProductionMood? _selectedMood;

  void _select(ProductionMood mood) {
    if (_selectedMood == mood) {
      return;
    }
    setState(() {
      _selectedMood = mood;
    });
    widget.onChanged?.call(mood);
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final selectedOption = _selectedMood == null
        ? null
        : productionMoodOptionFor(_selectedMood!);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Semantics(
          header: true,
          child: Text(widget.item.title, style: theme.textTheme.titleMedium),
        ),
        const SizedBox(height: 4),
        Wrap(
          spacing: 8,
          children: [
            for (final option in productionMoodOptions)
              ChoiceChip(
                label: Text('${option.emoji} ${option.label}'),
                selected: _selectedMood == option.mood,
                selectedColor: theme.colorScheme.primaryContainer,
                onSelected: (selected) {
                  if (selected) _select(option.mood);
                },
              ),
          ],
        ),
        if (selectedOption != null)
          Text(selectedOption.supportMessage, style: theme.textTheme.bodySmall),
      ],
    );
  }
}
