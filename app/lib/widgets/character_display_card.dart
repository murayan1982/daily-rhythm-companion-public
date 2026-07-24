import 'package:flutter/material.dart';

import '../models/character_display_presentation.dart';
import '../models/character_preset.dart';
import '../ui/character_asset_catalog.dart';

class CharacterDisplayCard extends StatelessWidget {
  const CharacterDisplayCard({
    super.key,
    required this.character,
    required this.presentation,
    required this.imageAssetPath,
    this.fallbackImageAssetPath = CharacterAssetCatalog.fallbackCharacter,
    this.imageKey = const ValueKey<String>('selected-character-image'),
  });

  final CharacterPreset? character;
  final CharacterDisplayPresentation presentation;
  final String imageAssetPath;
  final String fallbackImageAssetPath;
  final Key imageKey;

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Container(
      key: const Key('character-display-card'),
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(12),
        color: colorScheme.surfaceContainerHighest,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            '選択中のキャラクター',
            style: TextStyle(fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 12),
          Center(
            child: ClipRRect(
              borderRadius: BorderRadius.circular(16),
              child: Image.asset(
                imageAssetPath,
                key: imageKey,
                width: 180,
                height: 180,
                fit: BoxFit.contain,
                errorBuilder: (context, error, stackTrace) {
                  return Image.asset(
                    fallbackImageAssetPath,
                    key: const ValueKey<String>(
                      'selected-character-fallback-image',
                    ),
                    width: 180,
                    height: 180,
                    fit: BoxFit.contain,
                    errorBuilder: (context, error, stackTrace) {
                      return Container(
                        key: const Key('character-display-missing-image'),
                        width: 180,
                        height: 180,
                        alignment: Alignment.center,
                        color: colorScheme.surface,
                        child: const Icon(
                          Icons.image_not_supported_outlined,
                          size: 48,
                        ),
                      );
                    },
                  );
                },
              ),
            ),
          ),
          const SizedBox(height: 12),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              Chip(
                key: const Key('character-display-content-state'),
                avatar: Icon(_contentIcon(presentation.contentState), size: 18),
                label: Text(presentation.contentLabel),
              ),
              Chip(
                key: const Key('character-display-activity-state'),
                avatar: _buildActivityIcon(presentation.activityState),
                label: Text(presentation.activityLabel),
              ),
              const Chip(
                key: Key('character-display-static-baseline'),
                avatar: Icon(Icons.photo_outlined, size: 18),
                label: Text('静的表示'),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            presentation.title,
            key: const Key('character-display-title'),
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
          ),
          const SizedBox(height: 6),
          Text(
            presentation.message,
            key: const Key('character-display-message'),
          ),
          const SizedBox(height: 6),
          Text(
            presentation.activityMessage,
            key: const Key('character-display-activity-message'),
            style: Theme.of(context).textTheme.bodySmall,
          ),
          const SizedBox(height: 12),
          _DetailRow(
            key: const Key('character-display-name'),
            label: 'Name',
            value: character?.displayName.trim().isNotEmpty == true
                ? character!.displayName
                : '未選択',
          ),
          if (character != null) ...[
            _DetailRow(
              key: const Key('character-display-personality'),
              label: 'Personality',
              value: character!.personalityType,
            ),
            _DetailRow(
              key: const Key('character-display-speaking'),
              label: 'Speaking',
              value: character!.speakingStyle,
            ),
            _DetailRow(
              key: const Key('character-display-advice-style'),
              label: 'Advice style',
              value: character!.adviceStyle,
            ),
            const SizedBox(height: 8),
            const Text(
              'このキャラクターの話し方で、今日の気分と睡眠コンテキストをもとにアドバイスします。',
              key: Key('character-display-profile-note'),
            ),
          ],
          if (presentation.isFallback) ...[
            const SizedBox(height: 8),
            const Text(
              '通常の静的表示です。Live2D / VTube Studioの実行状態は表していません。',
              key: Key('character-display-fallback-note'),
            ),
          ],
        ],
      ),
    );
  }

  static IconData _contentIcon(CharacterDisplayContentState state) {
    switch (state) {
      case CharacterDisplayContentState.mood:
        return Icons.mood_outlined;
      case CharacterDisplayContentState.advice:
        return Icons.lightbulb_outline;
      case CharacterDisplayContentState.fallback:
        return Icons.shield_outlined;
    }
  }

  static Widget _buildActivityIcon(CharacterDisplayActivityState state) {
    switch (state) {
      case CharacterDisplayActivityState.idle:
        return const Icon(Icons.pause_circle_outline, size: 18);
      case CharacterDisplayActivityState.loading:
        return const SizedBox.square(
          dimension: 16,
          child: CircularProgressIndicator(strokeWidth: 2),
        );
      case CharacterDisplayActivityState.speaking:
        return const Icon(Icons.volume_up_outlined, size: 18);
    }
  }
}

class _DetailRow extends StatelessWidget {
  const _DetailRow({
    super.key,
    required this.label,
    required this.value,
  });

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 92,
            child: Text(
              label,
              style: const TextStyle(fontWeight: FontWeight.w600),
            ),
          ),
          Expanded(child: Text(value.trim().isEmpty ? '-' : value)),
        ],
      ),
    );
  }
}
