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

    return Semantics(
      container: true,
      label: '${widget.item.order}. ${widget.item.title}',
      child: Card(
        margin: EdgeInsets.zero,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              ExcludeSemantics(
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    SizedBox(
                      width: 32,
                      child: Text(
                        '${widget.item.order}.',
                        style: theme.textTheme.titleMedium,
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        widget.item.title,
                        style: theme.textTheme.titleMedium,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 6),
              Text(widget.item.description, style: theme.textTheme.bodyMedium),
              const SizedBox(height: 12),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: [
                  for (final option in productionMoodOptions)
                    ChoiceChip(
                      label: Text('${option.emoji} ${option.label}'),
                      selected: _selectedMood == option.mood,
                      onSelected: (selected) {
                        if (selected) {
                          _select(option.mood);
                        }
                      },
                    ),
                ],
              ),
              const SizedBox(height: 12),
              Text(
                '選択中: ${selectedOption?.label ?? '未選択'}',
                style: theme.textTheme.bodyLarge,
              ),
              if (selectedOption != null) ...[
                const SizedBox(height: 6),
                Text(
                  selectedOption.supportMessage,
                  style: theme.textTheme.bodyMedium,
                ),
              ],
              const SizedBox(height: 8),
              Text(
                '選択内容の保存とアドバイスへの反映は準備中です。',
                style: theme.textTheme.bodySmall,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
