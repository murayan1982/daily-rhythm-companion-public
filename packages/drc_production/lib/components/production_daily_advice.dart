import 'package:flutter/material.dart';

import '../core/production_character.dart';
import '../core/production_journey_step.dart';
import '../core/production_local_advice.dart';
import '../core/production_mood.dart';

typedef ProductionGeneratedAdvice = ({String message, Widget? audioControls});

typedef ProductionAdviceGenerator =
    Future<ProductionGeneratedAdvice> Function(
      ProductionMood mood,
      ProductionCharacter character,
    );

typedef ProductionOnlineAdvice = ({
  Widget settings,
  ProductionAdviceGenerator? generate,
});

class ProductionDailyAdvice extends StatefulWidget {
  const ProductionDailyAdvice({
    required this.item,
    required this.selectedMood,
    required this.selectedCharacter,
    this.extension,
    this.onlineAdvice,
    super.key,
  });

  final ProductionJourneyItem item;
  final ProductionMood? selectedMood;
  final ProductionCharacter? selectedCharacter;
  final Widget? extension;
  final ProductionOnlineAdvice? onlineAdvice;

  static const localRuleNotice = '端末内のルールで作成したアドバイスです。';
  static const noSendNotice = '端末内アドバイスでは選択内容を外部に送りません。';
  static const medicalNotice = '医療的な診断や治療の助言ではありません。';
  static const fallbackNotice = 'AIアドバイスを取得できなかったため、端末内のアドバイスを表示しています';

  @override
  State<ProductionDailyAdvice> createState() => _ProductionDailyAdviceState();
}

class _ProductionDailyAdviceState extends State<ProductionDailyAdvice> {
  int _requestId = 0;
  bool _generating = false;
  ({String message, Widget? audioControls, bool isLocal, bool onlineFailed})?
  _result;

  @override
  void didUpdateWidget(ProductionDailyAdvice oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.selectedMood != widget.selectedMood ||
        oldWidget.selectedCharacter != widget.selectedCharacter ||
        oldWidget.onlineAdvice?.generate != widget.onlineAdvice?.generate) {
      _requestId++;
      _generating = false;
      _result = null;
    }
  }

  Future<void> _generate() async {
    final mood = widget.selectedMood;
    final character = widget.selectedCharacter;
    if (_generating || mood == null || character == null) return;

    final online = widget.onlineAdvice?.generate;
    ProductionGeneratedAdvice? onlineResult;
    if (online != null) {
      FocusScope.of(context).unfocus();
      final requestId = ++_requestId;
      setState(() {
        _generating = true;
        _result = null;
      });
      try {
        onlineResult = await online(mood, character);
      } on Exception {
        // A current request can fall back to the same selection below.
      }
      if (!mounted || requestId != _requestId) return;
    }

    final message =
        onlineResult?.message ??
        productionLocalAdviceFor(mood: mood, character: character).message;
    setState(() {
      _generating = false;
      _result = (
        message: message,
        audioControls: onlineResult?.audioControls,
        isLocal: onlineResult == null,
        onlineFailed: online != null && onlineResult == null,
      );
    });
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final result = _result;
    final guidance = switch ((widget.selectedMood, widget.selectedCharacter)) {
      (null, null) => '気分とキャラクターを選んでください。',
      (null, _) => '気分を選んでください。',
      (_, null) => 'キャラクターを選んでください。',
      (_, _) => null,
    };
    final mood = widget.selectedMood;
    final character = widget.selectedCharacter;

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
              child: Text(widget.item.title, style: theme.textTheme.titleLarge),
            ),
            const SizedBox(height: 8),
            if (guidance != null)
              Semantics(
                container: true,
                liveRegion: true,
                child: Text(guidance, style: theme.textTheme.bodyMedium),
              ),
            if (widget.onlineAdvice case final online?) online.settings,
            Align(
              alignment: AlignmentDirectional.centerStart,
              child: FilledButton(
                onPressed: guidance == null && !_generating ? _generate : null,
                child: const Text('アドバイス生成'),
              ),
            ),
            if (_generating)
              Semantics(
                liveRegion: true,
                child: const Text('AIアドバイスを生成しています。'),
              ),
            if (result != null && mood != null && character != null) ...[
              const SizedBox(height: 8),
              Semantics(
                container: true,
                liveRegion: true,
                child: Text(
                  result.message,
                  style: theme.textTheme.bodyLarge?.copyWith(height: 1.6),
                ),
              ),
              if (result.audioControls case final controls?) controls,
              if (result.onlineFailed)
                Text(ProductionDailyAdvice.fallbackNotice),
              const SizedBox(height: 10),
              Wrap(
                spacing: 12,
                children: [
                  Text(
                    'キャラクター: ${productionCharacterOptionFor(character).displayName}',
                    style: theme.textTheme.labelMedium,
                  ),
                  Text(
                    '気分: ${productionMoodOptionFor(mood).label}',
                    style: theme.textTheme.labelMedium,
                  ),
                ],
              ),
            ],
            const SizedBox(height: 12),
            for (final notice in [
              if (result?.isLocal ?? false)
                ProductionDailyAdvice.localRuleNotice,
              ProductionDailyAdvice.noSendNotice,
              ProductionDailyAdvice.medicalNotice,
            ])
              Text(
                notice,
                style: theme.textTheme.bodySmall?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
            if (widget.extension case final child?) ...[
              const Divider(height: 24),
              child,
            ],
          ],
        ),
      ),
    );
  }
}
