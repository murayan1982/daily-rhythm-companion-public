import 'package:flutter/material.dart';

import '../core/production_character.dart';
import '../core/production_journey_step.dart';

typedef CharacterPortraitBuilder =
    Widget? Function(ProductionCharacterOption option, Widget fallback);

class ProductionCharacterSelection extends StatefulWidget {
  const ProductionCharacterSelection({
    required this.item,
    this.onChanged,
    this.characterPortrait,
    super.key,
  });

  final ProductionJourneyItem item;
  final ValueChanged<ProductionCharacter>? onChanged;
  final CharacterPortraitBuilder? characterPortrait;

  @override
  State<ProductionCharacterSelection> createState() =>
      _ProductionCharacterSelectionState();
}

class _ProductionCharacterSelectionState
    extends State<ProductionCharacterSelection> {
  ProductionCharacter? _selectedCharacter;

  void _select(ProductionCharacter character) {
    if (_selectedCharacter == character) return;
    setState(() => _selectedCharacter = character);
    widget.onChanged?.call(character);
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Semantics(
          header: true,
          child: Text(widget.item.title, style: theme.textTheme.titleMedium),
        ),
        const SizedBox(height: 8),
        LayoutBuilder(
          builder: (context, constraints) {
            const gap = 8.0;
            final largeText = MediaQuery.textScalerOf(context).scale(14) > 20;
            final width = largeText || constraints.maxWidth < 270
                ? constraints.maxWidth
                : (constraints.maxWidth - gap * 2) / 3;
            return Wrap(
              spacing: gap,
              runSpacing: gap,
              children: [
                for (final option in productionCharacterOptions)
                  SizedBox(
                    width: width,
                    child: _CharacterOptionCard(
                      option: option,
                      portraitBuilder: widget.characterPortrait,
                      selected: _selectedCharacter == option.character,
                      onSelected: () => _select(option.character),
                    ),
                  ),
              ],
            );
          },
        ),
      ],
    );
  }
}

class _CharacterOptionCard extends StatelessWidget {
  const _CharacterOptionCard({
    required this.option,
    required this.portraitBuilder,
    required this.selected,
    required this.onSelected,
  });

  final ProductionCharacterOption option;
  final CharacterPortraitBuilder? portraitBuilder;
  final bool selected;
  final VoidCallback onSelected;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colors = theme.colorScheme;
    final (tone, tint, ink) = switch (option.character) {
      ProductionCharacter.gentleMina => (
        'やさしい',
        const Color(0xFFF4DCD1),
        const Color(0xFF783F32),
      ),
      ProductionCharacter.cheerfulSora => (
        '明るい',
        const Color(0xFFF6E4BC),
        const Color(0xFF684711),
      ),
      ProductionCharacter.coolRei => (
        '落ち着き',
        const Color(0xFFE1E8DE),
        const Color(0xFF365645),
      ),
    };
    final shape = RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(16),
      side: BorderSide(
        color: selected ? colors.primary : colors.outlineVariant,
        width: selected ? 2 : 1,
      ),
    );
    final initial = Center(
      child: Text(
        option.displayName.substring(0, 1),
        textScaler: TextScaler.noScaling,
        style: theme.textTheme.titleLarge?.copyWith(
          color: ink,
          fontWeight: FontWeight.w700,
        ),
      ),
    );

    return Semantics(
      label: '${option.displayName}、$tone',
      button: true,
      selected: selected,
      onTap: onSelected,
      excludeSemantics: true,
      child: Material(
        color: selected ? colors.primaryContainer : colors.surface,
        shape: shape,
        clipBehavior: Clip.antiAlias,
        child: InkWell(
          onTap: onSelected,
          child: Stack(
            children: [
              Padding(
                padding: const EdgeInsets.fromLTRB(6, 12, 6, 10),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Center(
                      child: SizedBox.square(
                        dimension: 56,
                        child: ClipOval(
                          child: ColoredBox(
                            color: tint,
                            child:
                                portraitBuilder?.call(option, initial) ??
                                initial,
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      option.displayName,
                      textAlign: TextAlign.center,
                      style: theme.textTheme.titleSmall,
                    ),
                    Text(
                      tone,
                      textAlign: TextAlign.center,
                      style: theme.textTheme.bodySmall,
                    ),
                  ],
                ),
              ),
              if (selected)
                PositionedDirectional(
                  top: 6,
                  end: 6,
                  child: Icon(
                    Icons.check_circle,
                    size: 18,
                    color: colors.primary,
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }
}
