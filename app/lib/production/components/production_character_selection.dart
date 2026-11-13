import 'package:flutter/material.dart';

import '../core/production_character.dart';
import '../core/production_journey_step.dart';

class ProductionCharacterSelection extends StatefulWidget {
  const ProductionCharacterSelection({
    required this.item,
    this.onChanged,
    super.key,
  });

  final ProductionJourneyItem item;
  final ValueChanged<ProductionCharacter>? onChanged;

  @override
  State<ProductionCharacterSelection> createState() =>
      _ProductionCharacterSelectionState();
}

class _ProductionCharacterSelectionState
    extends State<ProductionCharacterSelection> {
  ProductionCharacter? _selectedCharacter;

  void _select(ProductionCharacter character) {
    if (_selectedCharacter == character) {
      return;
    }
    setState(() {
      _selectedCharacter = character;
    });
    widget.onChanged?.call(character);
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final selectedOption = _selectedCharacter == null
        ? null
        : productionCharacterOptionFor(_selectedCharacter!);

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
              for (final option in productionCharacterOptions) ...[
                _CharacterOptionCard(
                  option: option,
                  selected: _selectedCharacter == option.character,
                  onSelected: () => _select(option.character),
                ),
                if (option != productionCharacterOptions.last)
                  const SizedBox(height: 8),
              ],
              const SizedBox(height: 12),
              Text(
                '選択中: ${selectedOption?.displayName ?? '未選択'}',
                style: theme.textTheme.bodyLarge,
              ),
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

class _CharacterOptionCard extends StatelessWidget {
  const _CharacterOptionCard({
    required this.option,
    required this.selected,
    required this.onSelected,
  });

  final ProductionCharacterOption option;
  final bool selected;
  final VoidCallback onSelected;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final accessibleLabel =
        '${option.displayName}。${option.headline}。${option.tagline}。'
        '${option.toneLabel}。${option.summary}';

    return Semantics(
      label: accessibleLabel,
      selected: selected,
      child: Card(
        margin: EdgeInsets.zero,
        color: selected ? theme.colorScheme.secondaryContainer : null,
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Align(
                alignment: AlignmentDirectional.centerStart,
                child: ChoiceChip(
                  label: Text(option.displayName),
                  selected: selected,
                  onSelected: (_) => onSelected(),
                ),
              ),
              const SizedBox(height: 6),
              Text(option.headline, style: theme.textTheme.titleSmall),
              const SizedBox(height: 2),
              Text(option.tagline, style: theme.textTheme.bodyMedium),
              const SizedBox(height: 2),
              Text(option.toneLabel, style: theme.textTheme.labelMedium),
              const SizedBox(height: 4),
              Text(option.summary, style: theme.textTheme.bodySmall),
            ],
          ),
        ),
      ),
    );
  }
}
