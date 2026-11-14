import 'dart:ui' show SemanticsAction;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:drc_production/components/production_character_selection.dart';
import 'package:drc_production/components/production_journey_overview.dart';
import 'package:drc_production/components/production_mood_check_in.dart';
import 'package:drc_production/core/production_capability.dart';
import 'package:drc_production/core/production_journey_step.dart';
import 'package:drc_production/production_app.dart';

void main() {
  test('journey model is the exact approved six-step mapping', () {
    expect(productionJourneyItems, hasLength(6));
    expect(ProductionJourneyStep.values, hasLength(6));
    expect(
      productionJourneyItems.map((item) => item.step).toSet(),
      ProductionJourneyStep.values.toSet(),
    );
    expect(
      productionJourneyItems.map((item) => item.capability).toSet(),
      ProductionCapability.values.toSet(),
    );
    expect(productionJourneyItems.map((item) => item.order).toList(), <int>[
      1,
      2,
      3,
      4,
      5,
      6,
    ]);

    final optionalItems = productionJourneyItems.where(
      (item) => item.isOptional,
    );
    expect(optionalItems, hasLength(1));
    expect(optionalItems.single.step, ProductionJourneyStep.optionalTextChat);

    final pendingItems = productionJourneyItems.where(
      (item) => item.state == ProductionJourneyStepState.decisionPending,
    );
    expect(pendingItems, hasLength(1));
    expect(pendingItems.single.step, ProductionJourneyStep.sleepStatus);

    final localItems = productionJourneyItems.where(
      (item) =>
          item.state == ProductionJourneyStepState.localSelectionAvailable,
    );
    expect(localItems, hasLength(2));
    expect(localItems.map((item) => item.step).toSet(), <ProductionJourneyStep>{
      ProductionJourneyStep.moodCheckIn,
      ProductionJourneyStep.characterSelection,
    });

    final plannedItems = productionJourneyItems.where(
      (item) => item.state == ProductionJourneyStepState.planned,
    );
    expect(plannedItems, hasLength(2));

    final resultItems = productionJourneyItems.where(
      (item) => item.state == ProductionJourneyStepState.localResultAvailable,
    );
    expect(resultItems, hasLength(1));
    expect(resultItems.single.step, ProductionJourneyStep.dailyAdvice);
  });

  testWidgets('overview shows every title once and marks text chat optional', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const _OverviewHost());

    for (final item in productionJourneyItems) {
      if (item.step == ProductionJourneyStep.dailyAdvice) {
        expect(find.text('${item.order}. ${item.title}'), findsOneWidget);
      } else {
        expect(find.text(item.title), findsOneWidget);
      }
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

    final chatItem = productionJourneyItems.singleWhere(
      (item) => item.step == ProductionJourneyStep.optionalTextChat,
    );
    expect(find.text('\u4efb\u610f'), findsOneWidget);
    expect(
      find.ancestor(of: find.text('\u4efb\u610f'), matching: find.byType(Card)),
      findsOneWidget,
    );
    expect(
      find.descendant(
        of: find.ancestor(
          of: find.text('\u4efb\u610f'),
          matching: find.byType(Card),
        ),
        matching: find.text(chatItem.title),
      ),
      findsOneWidget,
    );
  });

  testWidgets(
    'overview exposes only the six approved local selection actions',
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
    expect(find.textContaining('今日は調子がよさそうですね'), findsOneWidget);

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

  testWidgets('semantics exposes complete six-step labels without actions', (
    WidgetTester tester,
  ) async {
    final handle = tester.ensureSemantics();
    try {
      await tester.pumpWidget(const _OverviewHost());

      for (final item in productionJourneyItems) {
        if (item.step == ProductionJourneyStep.moodCheckIn ||
            item.step == ProductionJourneyStep.characterSelection ||
            item.step == ProductionJourneyStep.dailyAdvice) {
          continue;
        }
        final semanticsLabel = _semanticsLabelFor(item);
        expect(find.bySemanticsLabel(semanticsLabel), findsOneWidget);

        final semantics = tester.getSemantics(
          find.bySemanticsLabel(semanticsLabel),
        );
        expect(
          semantics.getSemanticsData().hasAction(SemanticsAction.tap),
          isFalse,
        );
        expect(
          semantics.getSemanticsData().hasAction(SemanticsAction.longPress),
          isFalse,
        );
      }

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

      final sleepItem = productionJourneyItems.singleWhere(
        (item) => item.step == ProductionJourneyStep.sleepStatus,
      );
      expect(sleepItem.state, ProductionJourneyStepState.decisionPending);
      expect(_semanticsLabelFor(sleepItem), contains(sleepItem.description));
      expect(
        find.bySemanticsLabel(_semanticsLabelFor(sleepItem)),
        findsOneWidget,
      );

      final chatItem = productionJourneyItems.singleWhere(
        (item) => item.step == ProductionJourneyStep.optionalTextChat,
      );
      expect(_semanticsLabelFor(chatItem), contains('\u4efb\u610f'));
      expect(
        find.bySemanticsLabel(_semanticsLabelFor(chatItem)),
        findsOneWidget,
      );
    } finally {
      handle.dispose();
    }
  });
}

String _semanticsLabelFor(ProductionJourneyItem item) {
  final optionalLabel = item.isOptional ? '\u3001\u4efb\u610f' : '';
  return '${item.order}. ${item.title}$optionalLabel\u3002${item.description}';
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
