import 'package:flutter/material.dart';

import '../core/production_character.dart';
import '../core/production_journey_step.dart';
import '../core/production_local_advice.dart';
import '../core/production_mood.dart';

class ProductionDailyAdvice extends StatelessWidget {
  const ProductionDailyAdvice({
    required this.item,
    required this.selectedMood,
    required this.selectedCharacter,
    this.extension,
    super.key,
  });

  final ProductionJourneyItem item;
  final ProductionMood? selectedMood;
  final ProductionCharacter? selectedCharacter;
  final Widget? extension;

  static const localRuleNotice = '端末内のルールで作成したアドバイスです。';
  static const noSendNotice = '端末内アドバイスでは選択内容を外部に送りません。';
  static const medicalNotice = '医療的な診断や治療の助言ではありません。';

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final advice = selectedMood != null && selectedCharacter != null
        ? productionLocalAdviceFor(
            mood: selectedMood!,
            character: selectedCharacter!,
          )
        : null;
    final moodOption = selectedMood == null
        ? null
        : productionMoodOptionFor(selectedMood!);
    final characterOption = selectedCharacter == null
        ? null
        : productionCharacterOptionFor(selectedCharacter!);
    final guidance = switch ((selectedMood, selectedCharacter)) {
      (null, null) => '気分とキャラクターを選んでください。',
      (null, _) => '気分を選んでください。',
      (_, null) => 'キャラクターを選んでください。',
      (_, _) => null,
    };
    final readinessLabel = advice == null
        ? guidance!
        : '選択した気分は${moodOption!.label}。'
              '選択したキャラクターは${characterOption!.displayName}。'
              'アドバイス。${advice.message}';

    return Card(
      margin: EdgeInsets.zero,
      elevation: 0,
      color: theme.colorScheme.surfaceContainer,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Semantics(
              container: true,
              header: true,
              child: Text(item.title, style: theme.textTheme.titleLarge),
            ),
            const SizedBox(height: 8),
            Semantics(
              container: true,
              liveRegion: true,
              label: readinessLabel,
              excludeSemantics: true,
              child: guidance != null
                  ? Text(guidance, style: theme.textTheme.bodyMedium)
                  : Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        Text(
                          advice!.message,
                          style: theme.textTheme.bodyLarge?.copyWith(
                            height: 1.6,
                          ),
                        ),
                        const SizedBox(height: 10),
                        Wrap(
                          spacing: 12,
                          children: [
                            Text(
                              'キャラクター: ${characterOption!.displayName}',
                              style: theme.textTheme.labelMedium,
                            ),
                            Text(
                              '気分: ${moodOption!.label}',
                              style: theme.textTheme.labelMedium,
                            ),
                          ],
                        ),
                      ],
                    ),
            ),
            const SizedBox(height: 12),
            for (final notice in [
              if (advice != null) localRuleNotice,
              noSendNotice,
              medicalNotice,
            ])
              Text(
                notice,
                style: theme.textTheme.bodySmall?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
            if (extension case final child?) ...[
              const Divider(height: 24),
              child,
            ],
          ],
        ),
      ),
    );
  }
}
