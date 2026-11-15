import 'dart:ui' show Tristate;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:drc_production/components/production_character_selection.dart';
import 'package:drc_production/core/production_character.dart';
import 'package:drc_production/core/production_journey_step.dart';

void main() {
  final characterItem = productionJourneyItems.singleWhere(
    (item) => item.step == ProductionJourneyStep.characterSelection,
  );

  test('character model preserves the exact stable catalog and copy', () {
    expect(ProductionCharacter.values, hasLength(3));
    expect(productionCharacterOptions, hasLength(3));
    expect(
      productionCharacterOptions
          .map(
            (option) => <String>[
              option.characterId,
              option.displayName,
              option.headline,
              option.tagline,
              option.toneLabel,
              option.summary,
            ],
          )
          .toList(),
      <List<String>>[
        <String>[
          'gentle_mina',
          'ミナ',
          'やさしく整える',
          '休息に寄り添う落ち着いた相棒',
          '休息重視 / やさしい',
          '疲れ気味の日でも、無理なく整える一言をくれるキャラクター。',
        ],
        <String>[
          'cheerful_sora',
          'ソラ',
          '明るく背中を押す',
          '前向きな勢いをくれる相棒',
          '前向き / 元気',
          '少し気分を上げたい日に、軽く動き出せる言葉をくれるキャラクター。',
        ],
        <String>[
          'cool_rei',
          'レイ',
          '短く実用的に整理する',
          '落ち着いて次の一手を出す相棒',
          '実用重視 / 端的',
          '忙しい日でも、今できる小さな行動へ整理してくれるキャラクター。',
        ],
      ],
    );
    for (final character in ProductionCharacter.values) {
      expect(productionCharacterOptionFor(character).character, character);
    }
  });

  testWidgets('starts unselected with exactly three choices and all copy', (
    tester,
  ) async {
    var callbacks = 0;
    await tester.pumpWidget(
      _Host(item: characterItem, onChanged: (_) => callbacks++),
    );

    expect(find.byType(ChoiceChip), findsNWidgets(3));
    expect(find.text('選択中: 未選択'), findsOneWidget);
    expect(callbacks, 0);
    for (final option in productionCharacterOptions) {
      expect(find.text(option.displayName), findsOneWidget);
      expect(find.text(option.headline), findsOneWidget);
      expect(find.text(option.tagline), findsOneWidget);
      expect(find.text(option.toneLabel), findsOneWidget);
      expect(find.text(option.summary), findsOneWidget);
    }
    expect(find.textContaining('保存'), findsNothing);
    expect(find.text('選択内容の保存とアドバイスへの反映は準備中です。'), findsNothing);
  });

  testWidgets('selection is exclusive and callback fires only on change', (
    tester,
  ) async {
    final changes = <ProductionCharacter>[];
    await tester.pumpWidget(_Host(item: characterItem, onChanged: changes.add));

    await tester.tap(find.text('ミナ'));
    await tester.pump();
    expect(find.text('選択中: ミナ'), findsOneWidget);
    expect(_selectedChips(tester), <String>['ミナ']);
    expect(changes, <ProductionCharacter>[ProductionCharacter.gentleMina]);

    await tester.tap(find.text('ミナ'));
    await tester.pump();
    expect(_selectedChips(tester), <String>['ミナ']);
    expect(changes, hasLength(1));

    await tester.tap(find.text('ソラ'));
    await tester.pump();
    expect(find.text('選択中: ソラ'), findsOneWidget);
    expect(_selectedChips(tester), <String>['ソラ']);
    expect(changes, <ProductionCharacter>[
      ProductionCharacter.gentleMina,
      ProductionCharacter.cheerfulSora,
    ]);
  });

  testWidgets('accessible labels expose selected semantics', (tester) async {
    final handle = tester.ensureSemantics();
    try {
      await tester.pumpWidget(_Host(item: characterItem));
      for (final option in productionCharacterOptions) {
        expect(find.bySemanticsLabel(_accessibleLabel(option)), findsOneWidget);
      }

      await tester.tap(find.text('レイ'));
      await tester.pump();
      final semantics = tester.getSemantics(
        find.bySemanticsLabel(
          _accessibleLabel(productionCharacterOptions.last),
        ),
      );
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
    await tester.pumpWidget(_Host(item: characterItem));
    await tester.pumpAndSettle();
    expect(tester.takeException(), isNull);
  });

  testWidgets('fits with 2.0 text scaling', (tester) async {
    await tester.pumpWidget(
      MediaQuery(
        data: const MediaQueryData(textScaler: TextScaler.linear(2)),
        child: _Host(item: characterItem),
      ),
    );
    await tester.pumpAndSettle();
    expect(tester.takeException(), isNull);
  });

  test('production character source has no integration wiring', () {
    const source = <String>[
      'Backend',
      'http://',
      'https://',
      'endpoint',
      'storage',
      'persist',
      'Framework',
      'provider',
      'package:app/models/',
      'package:app/services/',
    ];
    final combined = productionCharacterOptions
        .map(
          (option) =>
              '${option.characterId} ${option.displayName} '
              '${option.headline} ${option.tagline} '
              '${option.toneLabel} ${option.summary}',
        )
        .join(' ');
    for (final forbidden in source) {
      expect(combined, isNot(contains(forbidden)));
    }
  });
}

String _accessibleLabel(ProductionCharacterOption option) {
  return '${option.displayName}。${option.headline}。${option.tagline}。'
      '${option.toneLabel}。${option.summary}';
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
  final ValueChanged<ProductionCharacter>? onChanged;

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Scaffold(
        body: SingleChildScrollView(
          child: ProductionCharacterSelection(item: item, onChanged: onChanged),
        ),
      ),
    );
  }
}
