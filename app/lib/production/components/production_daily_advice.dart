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
    super.key,
  });

  final ProductionJourneyItem item;
  final ProductionMood? selectedMood;
  final ProductionCharacter? selectedCharacter;

  static const localRuleNotice =
      'この機能のメッセージは、気分とキャラクターから端末内の固定ルールで作成されます。';
  static const noSendNotice = 'この機能では、入力内容をAIや外部サーバーへ送信しません。';
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
      (null, null) => '気分とキャラクターを選ぶと、今日のメッセージを表示します。',
      (null, _) => '気分を選ぶと、今日のメッセージを表示します。',
      (_, null) => 'キャラクターを選ぶと、今日のメッセージを表示します。',
      (_, _) => null,
    };
    final readinessLabel = advice == null
        ? '今日のアドバイス、準備中。$guidance'
        : '今日のアドバイス、表示準備完了。'
              'キャラクター、${characterOption!.displayName}。'
              '気分、${moodOption!.label}。${advice.message}';

    return Semantics(
      container: true,
      label: '${item.order}. ${item.title}。$readinessLabel',
      child: Card(
        margin: EdgeInsets.zero,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              ExcludeSemantics(
                child: Text(
                  '${item.order}. ${item.title}',
                  style: theme.textTheme.titleMedium,
                ),
              ),
              const SizedBox(height: 8),
              if (guidance != null)
                Text(guidance)
              else ...[
                Text('キャラクター: ${characterOption!.displayName}'),
                Text('気分: ${moodOption!.label}'),
                const SizedBox(height: 8),
                Text(advice!.message, style: theme.textTheme.bodyLarge),
              ],
              const SizedBox(height: 12),
              const Text(localRuleNotice),
              const Text(noSendNotice),
              const Text(medicalNotice),
            ],
          ),
        ),
      ),
    );
  }
}
