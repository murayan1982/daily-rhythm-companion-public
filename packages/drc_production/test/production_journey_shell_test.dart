import 'dart:ui' show SemanticsAction;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:drc_production/components/production_character_selection.dart';
import 'package:drc_production/components/production_journey_overview.dart';
import 'package:drc_production/components/production_mood_check_in.dart';
import 'package:drc_production/core/production_capability.dart';
import 'package:drc_production/core/production_journey_step.dart';
import 'package:drc_production/production_about_screen.dart';
import 'package:drc_production/production_app.dart';
import 'package:drc_production/production_home_screen.dart';

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
      expect(find.text(item.title), findsOneWidget);
    }

    expect(find.textContaining('保存'), findsNothing);

    final moodItem = productionJourneyItems.singleWhere(
      (item) => item.step == ProductionJourneyStep.moodCheckIn,
    );
    expect(moodItem.description, '今日の気分を3つから選びます。');
    final characterItem = productionJourneyItems.singleWhere(
      (item) => item.step == ProductionJourneyStep.characterSelection,
    );
    expect(characterItem.description, '3人のキャラクターから、今の自分に合う相棒を選びます。');

    expect(find.text('睡眠を確認'), findsNothing);
    expect(find.text('会話を続ける'), findsNothing);
    expect(find.text('履歴を振り返る'), findsNothing);
  });

  testWidgets('overview exposes three mood chips and three character cards', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const _OverviewHost());

    expect(find.byType(ChoiceChip), findsNWidgets(3));
    expect(
      find.descendant(
        of: find.byType(ProductionCharacterSelection),
        matching: find.byType(InkWell),
      ),
      findsNWidgets(3),
    );
    expect(find.byType(ProductionMoodCheckIn), findsOneWidget);
    expect(find.byType(ProductionCharacterSelection), findsOneWidget);
    final generate = find.widgetWithText(FilledButton, 'アドバイス生成');
    expect(generate, findsOneWidget);
    expect(tester.widget<FilledButton>(generate).onPressed, isNull);
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
  });

  testWidgets('character selection is available inside the journey', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const _OverviewHost());

    expect(find.byIcon(Icons.check_circle), findsNothing);
    await tester.tap(find.text('ミナ'));
    await tester.pump();
    expect(find.byIcon(Icons.check_circle), findsOneWidget);
    expect(find.text('気分を選んでください。'), findsOneWidget);
  });

  testWidgets('advice follows lifted mood and character selections', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const _OverviewHost());
    expect(find.text('気分とキャラクターを選んでください。'), findsOneWidget);

    await tester.ensureVisible(find.text('☀️ 元気'));
    await tester.tap(find.text('☀️ 元気'));
    await tester.pump();
    expect(find.text('キャラクターを選んでください。'), findsOneWidget);

    await tester.ensureVisible(find.text('ミナ'));
    await tester.tap(find.text('ミナ'));
    await tester.pump();
    expect(find.textContaining('今日は調子がよさそうですね'), findsNothing);
    await _generateAdvice(tester);
    expect(find.text('キャラクター: ミナ'), findsOneWidget);
    expect(find.text('気分: 元気'), findsOneWidget);
    expect(find.text('今日は前向きに動けそうです。'), findsOneWidget);
    expect(find.textContaining('今日は調子がよさそうですね'), findsOneWidget);

    await tester.ensureVisible(find.text('ソラ'));
    await tester.tap(find.text('ソラ'));
    await tester.pump();
    expect(find.textContaining('今日は調子がよさそうですね'), findsNothing);
    expect(find.textContaining('いい調子ですね！'), findsNothing);
    await _generateAdvice(tester);
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
    await _generateAdvice(tester);
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
    expect(find.text('気分を選んでください。'), findsOneWidget);
  });

  testWidgets('journey selections survive lifecycle pause and resume', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const _OverviewHost());

    await tester.ensureVisible(find.text('☀️ 元気'));
    await tester.tap(find.text('☀️ 元気'));
    await tester.pump();
    await tester.ensureVisible(find.text('ミナ'));
    await tester.tap(find.text('ミナ'));
    await tester.pump();

    await _generateAdvice(tester);
    expect(find.text('気分: 元気'), findsOneWidget);
    expect(find.text('キャラクター: ミナ'), findsOneWidget);
    expect(find.textContaining('今日は調子がよさそうですね'), findsOneWidget);

    tester.binding.handleAppLifecycleStateChanged(AppLifecycleState.paused);
    await tester.pump();
    expect(tester.binding.lifecycleState, AppLifecycleState.paused);

    tester.binding.handleAppLifecycleStateChanged(AppLifecycleState.resumed);
    await tester.pump();
    expect(tester.binding.lifecycleState, AppLifecycleState.resumed);
    expect(
      tester
          .widget<ChoiceChip>(find.widgetWithText(ChoiceChip, '☀️ 元気'))
          .selected,
      isTrue,
    );
    expect(find.byIcon(Icons.check_circle), findsOneWidget);
    expect(find.text('気分: 元気'), findsOneWidget);
    expect(find.text('キャラクター: ミナ'), findsOneWidget);
    expect(find.textContaining('今日は調子がよさそうですね'), findsOneWidget);
  });

  testWidgets('both selections reset with a fresh journey instance', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const _OverviewHost());

    final moodChoice = find.widgetWithText(ChoiceChip, '☀️ 元気');
    expect(tester.widget<ChoiceChip>(moodChoice).selected, isFalse);
    expect(find.byIcon(Icons.check_circle), findsNothing);

    await tester.ensureVisible(find.text('☀️ 元気'));
    await tester.tap(find.text('☀️ 元気'));
    await tester.pump();
    expect(tester.widget<ChoiceChip>(moodChoice).selected, isTrue);

    await tester.ensureVisible(find.text('ミナ'));
    await tester.tap(find.text('ミナ'));
    await tester.pump();
    await _generateAdvice(tester);
    expect(find.byIcon(Icons.check_circle), findsOneWidget);
    expect(find.text('キャラクター: ミナ'), findsOneWidget);
    expect(find.text('気分: 元気'), findsOneWidget);
    expect(find.textContaining('今日は調子がよさそうですね'), findsOneWidget);

    await tester.pumpWidget(const SizedBox.shrink());
    await tester.pump();
    await tester.pumpWidget(const _OverviewHost());
    await tester.pump();

    expect(tester.widget<ChoiceChip>(moodChoice).selected, isFalse);
    expect(find.byIcon(Icons.check_circle), findsNothing);
    expect(find.text('気分: 元気'), findsNothing);
    expect(find.text('キャラクター: ミナ'), findsNothing);
    expect(find.text('気分とキャラクターを選んでください。'), findsOneWidget);
    expect(find.textContaining('今日は調子がよさそうですね'), findsNothing);
  });

  testWidgets('about route is accessible and preserves journey state', (
    WidgetTester tester,
  ) async {
    final handle = tester.ensureSemantics();
    try {
      await tester.pumpWidget(const ProductionApp());
      await tester.pumpAndSettle();

      final aboutSemantics = find.semantics.byLabel('アプリについて');
      expect(aboutSemantics, findsOne);
      final aboutNode = aboutSemantics.evaluate().single;
      expect(aboutNode.getSemanticsData().flagsCollection.isButton, isTrue);
      expect(
        aboutNode.getSemanticsData().hasAction(SemanticsAction.tap),
        isTrue,
      );

      await tester.ensureVisible(find.text('☀️ 元気'));
      await tester.tap(find.text('☀️ 元気'));
      await tester.pump();
      await tester.ensureVisible(find.text('ミナ'));
      await tester.tap(find.text('ミナ'));
      await tester.pump();
      await _generateAdvice(tester);
      expect(find.text('気分: 元気'), findsOneWidget);
      expect(find.text('キャラクター: ミナ'), findsOneWidget);
      expect(find.textContaining('今日は調子がよさそうですね'), findsOneWidget);

      tester.semantics.tap(aboutSemantics);
      await tester.pumpAndSettle();

      expect(find.byType(ProductionAboutScreen), findsOneWidget);
      expect(find.text('アプリについて'), findsOneWidget);
      expect(
        find.text(
          'このベータ版では、気分とキャラクターを選び、「アドバイス生成」を押すと、'
          '端末内で今日のアドバイスを表示します。',
        ),
        findsOneWidget,
      );
      expect(find.text('選択内容は保存されません。'), findsOneWidget);

      await tester.pageBack();
      await tester.pumpAndSettle();

      expect(find.byType(ProductionAboutScreen), findsNothing);
      expect(find.text('気分: 元気'), findsOneWidget);
      expect(find.text('キャラクター: ミナ'), findsOneWidget);
      expect(find.textContaining('今日は調子がよさそうですね'), findsOneWidget);

      await tester.tap(find.byTooltip('アプリについて'));
      await tester.pumpAndSettle();
      expect(find.byType(ProductionAboutScreen), findsOneWidget);

      await tester.pageBack();
      await tester.pumpAndSettle();
      expect(find.text('気分: 元気'), findsOneWidget);
      expect(find.text('キャラクター: ミナ'), findsOneWidget);
      expect(find.textContaining('今日は調子がよさそうですね'), findsOneWidget);
    } finally {
      handle.dispose();
    }
  });

  testWidgets('about route fits a narrow viewport without exceptions', (
    WidgetTester tester,
  ) async {
    tester.view.physicalSize = const Size(320, 568);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    await tester.pumpWidget(const ProductionApp());
    await tester.tap(find.byTooltip('アプリについて'));
    await tester.pumpAndSettle();

    expect(tester.takeException(), isNull);
    expect(find.byType(ProductionAboutScreen), findsOneWidget);
  });

  testWidgets('about route supports 2.0 text scaling without exceptions', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: MediaQuery(
          data: MediaQueryData(textScaler: TextScaler.linear(2)),
          child: ProductionHomeScreen(),
        ),
      ),
    );
    await tester.tap(find.byTooltip('アプリについて'));
    await tester.pumpAndSettle();

    expect(tester.takeException(), isNull);
    expect(find.byType(ProductionAboutScreen), findsOneWidget);
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

  testWidgets('selections work at 320 × 568 with 2.0 text scaling', (
    WidgetTester tester,
  ) async {
    tester.view.physicalSize = const Size(320, 568);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
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
    for (final label in ['🌿 ふつう', 'ソラ']) {
      final choice = find.text(label);
      await tester.ensureVisible(choice);
      await tester.tap(choice);
      await tester.pumpAndSettle();
    }
    final mood = tester.widget<ChoiceChip>(
      find.widgetWithText(ChoiceChip, '🌿 ふつう'),
    );
    expect(mood.selected, isTrue);
    final character = find.widgetWithText(InkWell, 'ソラ');
    expect(
      find.descendant(of: character, matching: find.byIcon(Icons.check_circle)),
      findsOneWidget,
    );
    await _generateAdvice(tester);
    expect(find.textContaining('今日は小さく動き出せれば'), findsOneWidget);
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
      expect(find.bySemanticsLabel(moodItem.title), findsOneWidget);

      final characterItem = productionJourneyItems.singleWhere(
        (item) => item.step == ProductionJourneyStep.characterSelection,
      );
      expect(find.bySemanticsLabel(characterItem.title), findsOneWidget);

      expect(find.bySemanticsLabel('今日のアドバイス'), findsOneWidget);
      expect(find.bySemanticsLabel(RegExp('準備中')), findsNothing);
      expect(find.bySemanticsLabel(RegExp('睡眠を確認')), findsNothing);
      expect(find.bySemanticsLabel(RegExp('会話を続ける')), findsNothing);
      expect(find.bySemanticsLabel(RegExp('履歴を振り返る')), findsNothing);
    } finally {
      handle.dispose();
    }
  });
}

Future<void> _generateAdvice(WidgetTester tester) async {
  final button = find.text('アドバイス生成');
  await tester.ensureVisible(button);
  await tester.tap(button);
  await tester.pumpAndSettle();
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
