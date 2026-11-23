import 'dart:ui' show SemanticsAction;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:drc_production/components/production_daily_advice.dart';
import 'package:drc_production/core/production_character.dart';
import 'package:drc_production/core/production_journey_step.dart';
import 'package:drc_production/core/production_local_advice.dart';
import 'package:drc_production/core/production_mood.dart';

void main() {
  final adviceItem = productionJourneyItems.singleWhere(
    (item) => item.step == ProductionJourneyStep.dailyAdvice,
  );
  const matrix = <(ProductionCharacter, ProductionMood), String>{
    (ProductionCharacter.gentleMina, ProductionMood.energetic):
        '今日は調子がよさそうですね。無理に予定を増やさず、気持ちよいペースを保っていきましょう。',
    (ProductionCharacter.gentleMina, ProductionMood.normal):
        'いつもの調子を大切に、ひとつずつ進めてみましょう。少し疲れたら、早めに休憩して大丈夫です。',
    (ProductionCharacter.gentleMina, ProductionMood.tired):
        '今日は無理に頑張りすぎなくて大丈夫です。まずは短い休憩と、できることをひとつだけにしましょう。',
    (ProductionCharacter.cheerfulSora, ProductionMood.energetic):
        'いい調子ですね！今の勢いを使って、やりたいことをひとつ始めてみましょう。',
    (ProductionCharacter.cheerfulSora, ProductionMood.normal):
        '今日は小さく動き出せれば十分です。まずは気軽にひとつ、始めてみましょう！',
    (ProductionCharacter.cheerfulSora, ProductionMood.tired):
        '疲れている日は小さな一歩でOKです。水分をとって、負担の少ないことから始めましょう。',
    (ProductionCharacter.coolRei, ProductionMood.energetic):
        '調子は良好です。優先することを一つ決め、終えたら次へ進みましょう。',
    (ProductionCharacter.coolRei, ProductionMood.normal):
        '今日の優先事項を一つ決めましょう。終えたら短い休憩を入れてください。',
    (ProductionCharacter.coolRei, ProductionMood.tired):
        '今日はタスクを増やさない方がよいでしょう。必要なことを一つに絞り、終えたら休みましょう。',
  };

  test('exactly nine deterministic mappings preserve inputs and copy', () {
    expect(matrix, hasLength(9));
    final results = <ProductionLocalAdvice>[];
    for (final entry in matrix.entries) {
      final result = productionLocalAdviceFor(
        character: entry.key.$1,
        mood: entry.key.$2,
      );
      expect(result.character, entry.key.$1);
      expect(result.mood, entry.key.$2);
      expect(result.message, entry.value);
      expect(
        productionLocalAdviceFor(
          character: entry.key.$1,
          mood: entry.key.$2,
        ).message,
        result.message,
      );
      results.add(result);
    }
    expect(results.map((result) => result.message).toSet(), hasLength(9));
  });

  testWidgets('shows guidance for every readiness state', (tester) async {
    await tester.pumpWidget(_Host(item: adviceItem));
    expect(find.text('気分とキャラクターを選んでください。'), findsOneWidget);

    await tester.pumpWidget(
      _Host(item: adviceItem, character: ProductionCharacter.gentleMina),
    );
    expect(find.text('気分を選んでください。'), findsOneWidget);

    await tester.pumpWidget(
      _Host(item: adviceItem, mood: ProductionMood.energetic),
    );
    expect(find.text('キャラクターを選んでください。'), findsOneWidget);
  });

  testWidgets('button shows selection, message, and source notice', (
    tester,
  ) async {
    final expected = productionLocalAdviceFor(
      mood: ProductionMood.tired,
      character: ProductionCharacter.coolRei,
    );
    await tester.pumpWidget(
      _Host(
        item: adviceItem,
        mood: expected.mood,
        character: expected.character,
      ),
    );
    expect(find.text('今日のアドバイス'), findsOneWidget);
    expect(find.text(expected.message), findsNothing);
    expect(find.text(ProductionDailyAdvice.localRuleNotice), findsNothing);
    await tester.tap(find.text('アドバイス生成'));
    await tester.pump();
    expect(find.text('キャラクター: レイ'), findsOneWidget);
    expect(find.text('気分: だるい'), findsOneWidget);
    expect(find.text(expected.message), findsOneWidget);
    expect(find.text(ProductionDailyAdvice.localRuleNotice), findsOneWidget);
    expect(find.text(ProductionDailyAdvice.noSendNotice), findsOneWidget);
    expect(find.text(ProductionDailyAdvice.medicalNotice), findsOneWidget);
  });

  testWidgets('generated body is readable without being an action', (
    tester,
  ) async {
    final handle = tester.ensureSemantics();
    try {
      await tester.pumpWidget(
        _Host(
          item: adviceItem,
          mood: ProductionMood.normal,
          character: ProductionCharacter.cheerfulSora,
        ),
      );
      await tester.tap(find.text('アドバイス生成'));
      await tester.pump();
      final finder = find.bySemanticsLabel(RegExp('^今日は小さく'));
      expect(finder, findsOneWidget);
      final data = tester.getSemantics(finder).getSemanticsData();
      expect(data.hasAction(SemanticsAction.tap), isFalse);
      expect(data.hasAction(SemanticsAction.longPress), isFalse);
    } finally {
      handle.dispose();
    }
  });

  testWidgets('semantics explains each incomplete selection state', (
    tester,
  ) async {
    final handle = tester.ensureSemantics();
    try {
      await tester.pumpWidget(_Host(item: adviceItem));
      expect(find.bySemanticsLabel('気分とキャラクターを選んでください。'), findsOneWidget);

      await tester.pumpWidget(
        _Host(item: adviceItem, character: ProductionCharacter.gentleMina),
      );
      expect(find.bySemanticsLabel('気分を選んでください。'), findsOneWidget);

      await tester.pumpWidget(
        _Host(item: adviceItem, mood: ProductionMood.energetic),
      );
      expect(find.bySemanticsLabel('キャラクターを選んでください。'), findsOneWidget);
    } finally {
      handle.dispose();
    }
  });

  testWidgets('fits a 320x568 viewport and 2.0 text scaling', (tester) async {
    tester.view.physicalSize = const Size(320, 568);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    await tester.pumpWidget(
      MediaQuery(
        data: const MediaQueryData(textScaler: TextScaler.linear(2)),
        child: _Host(
          item: adviceItem,
          mood: ProductionMood.energetic,
          character: ProductionCharacter.gentleMina,
        ),
      ),
    );
    await tester.pumpAndSettle();
    expect(tester.takeException(), isNull);
  });

  test('model exposes no integration configuration', () {
    final combined = matrix.values.join(' ');
    for (final forbidden in <String>[
      'http://',
      'https://',
      'endpoint',
      'API key',
      'storage',
      'persist',
      'Framework',
      'provider',
      'LLM',
    ]) {
      expect(combined, isNot(contains(forbidden)));
    }
  });
}

class _Host extends StatelessWidget {
  const _Host({required this.item, this.mood, this.character});

  final ProductionJourneyItem item;
  final ProductionMood? mood;
  final ProductionCharacter? character;

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Scaffold(
        body: SingleChildScrollView(
          child: ProductionDailyAdvice(
            item: item,
            selectedMood: mood,
            selectedCharacter: character,
          ),
        ),
      ),
    );
  }
}
