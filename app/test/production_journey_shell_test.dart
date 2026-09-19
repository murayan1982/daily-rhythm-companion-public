import 'dart:ui' show SemanticsAction;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:app/production/components/production_journey_overview.dart';
import 'package:app/production/core/production_capability.dart';
import 'package:app/production/core/production_journey_step.dart';
import 'package:app/production/production_app.dart';

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
  });

  testWidgets('overview shows every title once and marks text chat optional', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const _OverviewHost());

    for (final item in productionJourneyItems) {
      expect(find.text(item.title), findsOneWidget);
    }

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

  testWidgets('overview has no action controls or raw non-product copy', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const _OverviewHost());

    expect(find.byType(ButtonStyleButton), findsNothing);
    expect(find.byType(IconButton), findsNothing);
    expect(find.byType(InkWell), findsNothing);
    expect(find.byType(GestureDetector), findsNothing);

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
    return const MaterialApp(home: Scaffold(body: ProductionJourneyOverview()));
  }
}
