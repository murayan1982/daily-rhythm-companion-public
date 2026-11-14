import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:drc_production/components/production_character_selection.dart';
import 'package:drc_production/components/production_journey_overview.dart';
import 'package:drc_production/components/production_mood_check_in.dart';
import 'package:drc_production/core/production_capability.dart';
import 'package:drc_production/core/production_journey_step.dart';
import 'package:drc_production/production_app.dart';

void main() {
  test('journey model is the approved three-step Public Beta mapping', () {
    expect(productionJourneyItems, hasLength(3));
    expect(ProductionJourneyStep.values, hasLength(6));
    expect(
      productionJourneyItems.map((item) => item.step).toList(),
      <ProductionJourneyStep>[
        ProductionJourneyStep.moodCheckIn,
        ProductionJourneyStep.characterSelection,
        ProductionJourneyStep.dailyAdvice,
      ],
    );
    expect(
      productionJourneyItems.map((item) => item.capability).toList(),
      <ProductionCapability>[
        ProductionCapability.moodCheckIn,
        ProductionCapability.characterSelection,
        ProductionCapability.dailyAdvice,
      ],
    );
    expect(productionJourneyItems.map((item) => item.order).toList(), <int>[
      1,
      2,
      3,
    ]);
    expect(productionJourneyItems.every((item) => !item.isOptional), isTrue);
    expect(ProductionCapability.values, hasLength(6));
    expect(
      ProductionJourneyStep.values.toSet().difference(
        productionJourneyItems.map((item) => item.step).toSet(),
      ),
      <ProductionJourneyStep>{
        ProductionJourneyStep.sleepStatus,
        ProductionJourneyStep.optionalTextChat,
        ProductionJourneyStep.history,
      },
    );

    final localItems = productionJourneyItems.where(
      (item) =>
          item.state == ProductionJourneyStepState.localSelectionAvailable,
    );
    expect(localItems, hasLength(2));
    expect(localItems.map((item) => item.step).toSet(), <ProductionJourneyStep>{
      ProductionJourneyStep.moodCheckIn,
      ProductionJourneyStep.characterSelection,
    });

    final resultItems = productionJourneyItems.where(
      (item) => item.state == ProductionJourneyStepState.localResultAvailable,
    );
    expect(resultItems, hasLength(1));
    expect(resultItems.single.step, ProductionJourneyStep.dailyAdvice);
  });

  testWidgets('overview shows only the ordered three-step Public Beta flow', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const _OverviewHost());

    for (final item in productionJourneyItems) {
      expect(
        find.text(
          item.step == ProductionJourneyStep.dailyAdvice
              ? '${item.order}. ${item.title}'
              : item.title,
        ),
        findsOneWidget,
      );
    }

    const currentNotice = '選択内容はこの画面のメッセージに反映されます。保存は準備中です。';
    const staleNotice = '選択内容の保存とアドバイスへの反映は準備中です。';
    expect(find.text(currentNotice), findsNWidgets(2));
    expect(find.text(staleNotice), findsNothing);

    final moodItem = productionJourneyItems.singleWhere(
      (item) => item.step == ProductionJourneyStep.moodCheckIn,
    );
    expect(
      moodItem.description,
      '今日の気分を3つから選べます。選択内容はこの画面のメッセージに反映されますが、保存されません。',
    );
    final characterItem = productionJourneyItems.singleWhere(
      (item) => item.step == ProductionJourneyStep.characterSelection,
    );
    expect(
      characterItem.description,
      '3人のキャラクターから、今の自分に合う相棒を選べます。選択内容はこの画面のメッセージに反映されますが、保存されません。',
    );

    expect(find.text('睡眠を確認'), findsNothing);
    expect(find.text('会話を続ける'), findsNothing);
    expect(find.text('履歴を振り返る'), findsNothing);
  });

  testWidgets(
    'overview exposes only the six choice chips and no other actions',
    (WidgetTester tester) async {
      await tester.pumpWidget(const _OverviewHost());

      expect(find.byType(ChoiceChip), findsNWidgets(6));
      expect(find.byType(ProductionMoodCheckIn), findsOneWidget);
      expect(find.byType(ProductionCharacterSelection), findsOneWidget);
      expect(find.byType(ButtonStyleButton), findsNothing);
      expect(find.byType(IconButton), findsNothing);

      for (final value in <String>[
        'developer',
        'operator',
        'demo',
        'diagnostic',
        'localhost',
        'Backend',
        'endpoint',
        'engine',
        'mode',
        'session ID',
        'technical code',
        'realtime',
        'framework',
        'http://',
        'https://',
      ]) {
        expect(find.textContaining(value, findRichText: true), findsNothing);
      }
    },
  );

  testWidgets('character selection is available inside the journey', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const _OverviewHost());

    expect(find.text('選択中: 未選択'), findsNWidgets(2));
    await tester.tap(find.text('ミナ'));
    await tester.pump();
    expect(find.text('選択中: ミナ'), findsOneWidget);
    expect(find.text('選択中: 未選択'), findsOneWidget);
  });

  testWidgets('advice follows lifted mood and character selections', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const _OverviewHost());
    expect(find.text('気分とキャラクターを選ぶと、今日のメッセージを表示します。'), findsOneWidget);

    await tester.ensureVisible(find.text('☀️ 元気'));
    await tester.tap(find.text('☀️ 元気'));
    await tester.pump();
    expect(find.text('キャラクターを選ぶと、今日のメッセージを表示します。'), findsOneWidget);

    await tester.ensureVisible(find.text('ミナ'));
    await tester.tap(find.text('ミナ'));
    await tester.pump();
    expect(find.text('キャラクター: ミナ'), findsOneWidget);
    expect(find.text('気分: 元気'), findsOneWidget);
    expect(find.text('今日は前向きに動けそうです。'), findsOneWidget);
    expect(find.textContaining('今日は調子がよさそうですね'), findsOneWidget);

    await tester.ensureVisible(find.text('ソラ'));
    await tester.tap(find.text('ソラ'));
    await tester.pump();
    expect(find.text('キャラクター: ソラ'), findsOneWidget);
    expect(find.text('気分: 元気'), findsOneWidget);
    expect(find.text('今日は前向きに動けそうです。'), findsOneWidget);
    expect(find.textContaining('いい調子ですね！'), findsOneWidget);
    expect(find.textContaining('今日は調子がよさそうですね'), findsNothing);

    await tester.ensureVisible(find.text('😪 だるい'));
    await tester.tap(find.text('😪 だるい'));
    await tester.ensureVisible(find.text('レイ'));
    await tester.tap(find.text('レイ'));
    await tester.pump();
    expect(find.text('キャラクター: レイ'), findsOneWidget);
    expect(find.text('気分: だるい'), findsOneWidget);
    expect(find.textContaining('今日はタスクを増やさない'), findsOneWidget);
  });

  testWidgets('character-only journey state requests a mood', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const _OverviewHost());
    await tester.ensureVisible(find.text('ソラ'));
    await tester.tap(find.text('ソラ'));
    await tester.pump();
    expect(find.text('気分を選ぶと、今日のメッセージを表示します。'), findsOneWidget);
  });

  testWidgets('mood selection resets with a fresh journey instance', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const _OverviewHost());

    final moodSelection = find.descendant(
      of: find.byType(ProductionMoodCheckIn),
      matching: find.text('選択中: 未選択'),
    );
    expect(moodSelection, findsOneWidget);

    await tester.ensureVisible(find.text('☀️ 元気'));
    await tester.tap(find.text('☀️ 元気'));
    await tester.pump();
    expect(
      find.descendant(
        of: find.byType(ProductionMoodCheckIn),
        matching: find.text('選択中: 元気'),
      ),
      findsOneWidget,
    );

    await tester.ensureVisible(find.text('ミナ'));
    await tester.tap(find.text('ミナ'));
    await tester.pump();
    expect(find.text('キャラクター: ミナ'), findsOneWidget);
    expect(find.text('気分: 元気'), findsOneWidget);
    expect(find.textContaining('今日は調子がよさそうですね'), findsOneWidget);

    await tester.pumpWidget(const SizedBox.shrink());
    await tester.pump();
    await tester.pumpWidget(const _OverviewHost());
    await tester.pump();

    expect(moodSelection, findsOneWidget);
    expect(find.text('選択中: 元気'), findsNothing);
    expect(find.text('気分とキャラクターを選ぶと、今日のメッセージを表示します。'), findsOneWidget);
    expect(find.textContaining('今日は調子がよさそうですね'), findsNothing);
  });

  testWidgets('journey shell fits a narrow viewport without exceptions', (
    WidgetTester tester,
  ) async {
    tester.view.physicalSize = const Size(320, 568);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    await tester.pumpWidget(const ProductionApp());
    await tester.pumpAndSettle();

    expect(tester.takeException(), isNull);
    expect(find.byType(ProductionJourneyOverview), findsOneWidget);
  });

  testWidgets('journey shell supports 2.0 text scaling without exceptions', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: MediaQuery(
          data: MediaQueryData(textScaler: TextScaler.linear(2)),
          child: Scaffold(
            body: SingleChildScrollView(child: ProductionJourneyOverview()),
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(tester.takeException(), isNull);
  });

  testWidgets('semantics exposes the ordered three-step labels', (
    WidgetTester tester,
  ) async {
    final handle = tester.ensureSemantics();
    try {
      await tester.pumpWidget(const _OverviewHost());

      final moodItem = productionJourneyItems.singleWhere(
        (item) => item.step == ProductionJourneyStep.moodCheckIn,
      );
      expect(
        find.bySemanticsLabel('${moodItem.order}. ${moodItem.title}'),
        findsOneWidget,
      );

      final characterItem = productionJourneyItems.singleWhere(
        (item) => item.step == ProductionJourneyStep.characterSelection,
      );
      expect(
        find.bySemanticsLabel('${characterItem.order}. ${characterItem.title}'),
        findsOneWidget,
      );

      expect(find.bySemanticsLabel(RegExp('今日のアドバイス、準備中')), findsOneWidget);
      expect(find.bySemanticsLabel(RegExp('睡眠を確認')), findsNothing);
      expect(find.bySemanticsLabel(RegExp('会話を続ける')), findsNothing);
      expect(find.bySemanticsLabel(RegExp('履歴を振り返る')), findsNothing);
    } finally {
      handle.dispose();
    }
  });
}

class _OverviewHost extends StatelessWidget {
  const _OverviewHost();

  @override
  Widget build(BuildContext context) {
    return const MaterialApp(
      home: Scaffold(
        body: SingleChildScrollView(child: ProductionJourneyOverview()),
      ),
    );
  }
}
