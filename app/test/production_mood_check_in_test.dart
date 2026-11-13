import 'dart:ui' show Tristate;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:app/production/components/production_mood_check_in.dart';
import 'package:app/production/core/production_journey_step.dart';
import 'package:app/production/core/production_mood.dart';

void main() {
  final moodItem = productionJourneyItems.singleWhere(
    (item) => item.step == ProductionJourneyStep.moodCheckIn,
  );

  test('mood model has the exact approved mapping', () {
    expect(ProductionMood.values, <ProductionMood>[
      ProductionMood.energetic,
      ProductionMood.normal,
      ProductionMood.tired,
    ]);
    expect(productionMoodOptions, hasLength(3));
    expect(
      productionMoodOptions
          .map(
            (option) => <String>[
              option.code,
              option.emoji,
              option.label,
              option.supportMessage,
            ],
          )
          .toList(),
      <List<String>>[
        <String>['energetic', '☀️', '元気', '今日は前向きに動けそうです。'],
        <String>['normal', '🌿', 'ふつう', '今日はいつも通り過ごせそうです。'],
        <String>['tired', '😪', 'だるい', '今日は回復を優先したい状態です。'],
      ],
    );
    for (final mood in ProductionMood.values) {
      expect(productionMoodOptionFor(mood).mood, mood);
    }
  });

  testWidgets('starts unselected with exactly three choices', (tester) async {
    var callbacks = 0;
    await tester.pumpWidget(
      _Host(item: moodItem, onChanged: (_) => callbacks++),
    );

    expect(find.byType(ChoiceChip), findsNWidgets(3));
    expect(find.text('選択中: 未選択'), findsOneWidget);
    expect(callbacks, 0);
    for (final chip in tester.widgetList<ChoiceChip>(find.byType(ChoiceChip))) {
      expect(chip.selected, isFalse);
    }
    expect(find.text('選択内容の保存とアドバイスへの反映は準備中です。'), findsOneWidget);
  });

  testWidgets('selection is exclusive and reports changes once', (
    tester,
  ) async {
    final changes = <ProductionMood>[];
    await tester.pumpWidget(_Host(item: moodItem, onChanged: changes.add));

    await tester.tap(find.text('☀️ 元気'));
    await tester.pump();
    expect(find.text('選択中: 元気'), findsOneWidget);
    expect(find.text('今日は前向きに動けそうです。'), findsOneWidget);
    expect(_selectedChips(tester), <String>['☀️ 元気']);
    expect(changes, <ProductionMood>[ProductionMood.energetic]);

    await tester.tap(find.text('🌿 ふつう'));
    await tester.pump();
    expect(find.text('選択中: ふつう'), findsOneWidget);
    expect(_selectedChips(tester), <String>['🌿 ふつう']);
    expect(changes.last, ProductionMood.normal);

    await tester.tap(find.text('😪 だるい'));
    await tester.pump();
    expect(find.text('選択中: だるい'), findsOneWidget);
    expect(find.text('今日は回復を優先したい状態です。'), findsOneWidget);
    expect(_selectedChips(tester), <String>['😪 だるい']);
    expect(changes.last, ProductionMood.tired);
    expect(changes, hasLength(3));
  });

  testWidgets('choice semantics expose labels and selected state', (
    tester,
  ) async {
    final handle = tester.ensureSemantics();
    try {
      await tester.pumpWidget(_Host(item: moodItem));
      for (final label in <String>['☀️ 元気', '🌿 ふつう', '😪 だるい']) {
        expect(find.bySemanticsLabel(label), findsOneWidget);
      }

      await tester.tap(find.text('☀️ 元気'));
      await tester.pump();
      final semantics = tester.getSemantics(find.bySemanticsLabel('☀️ 元気'));
      expect(
        semantics.getSemanticsData().flagsCollection.isSelected,
        Tristate.isTrue,
      );
    } finally {
      handle.dispose();
    }
  });

  testWidgets('fits a 320x568 viewport', (tester) async {
    tester.view.physicalSize = const Size(320, 568);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    await tester.pumpWidget(_Host(item: moodItem));
    await tester.pumpAndSettle();
    expect(tester.takeException(), isNull);
  });

  testWidgets('fits with 2.0 text scaling', (tester) async {
    await tester.pumpWidget(
      MediaQuery(
        data: const MediaQueryData(textScaler: TextScaler.linear(2)),
        child: _Host(item: moodItem),
      ),
    );
    await tester.pumpAndSettle();
    expect(tester.takeException(), isNull);
  });
}

List<String> _selectedChips(WidgetTester tester) {
  return tester
      .widgetList<ChoiceChip>(find.byType(ChoiceChip))
      .where((chip) => chip.selected)
      .map((chip) => (chip.label as Text).data!)
      .toList();
}

class _Host extends StatelessWidget {
  const _Host({required this.item, this.onChanged});

  final ProductionJourneyItem item;
  final ValueChanged<ProductionMood>? onChanged;

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Scaffold(
        body: SingleChildScrollView(
          child: ProductionMoodCheckIn(item: item, onChanged: onChanged),
        ),
      ),
    );
  }
}
