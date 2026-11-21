import 'dart:io';

import 'package:drc_public_app/main_sleep_debug.dart' as sleep_debug;
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  const portraitChannel = MethodChannel('drc/debug_character_images');

  testWidgets('debug portraits match their character choices', (tester) async {
    const names = {
      'gentle_mina': 'ミナ',
      'cheerful_sora': 'ソラ',
      'cool_rei': 'レイ',
    };
    final portraits = {
      for (final id in names.keys)
        id: File(
          'android/app/src/debug/assets/character_portraits/${id}_demo.png',
        ).readAsBytesSync(),
    };
    final messenger =
        TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger;
    messenger.setMockMethodCallHandler(portraitChannel, (call) async {
      expect(call.method, 'load');
      return portraits;
    });
    addTearDown(
      () => messenger.setMockMethodCallHandler(portraitChannel, null),
    );

    sleep_debug.main();
    await tester.pumpAndSettle();
    await tester.tap(find.text('☀️ 元気'));
    await tester.pumpAndSettle();

    for (final entry in names.entries) {
      final choice = find.widgetWithText(ChoiceChip, entry.value);
      final row = find.ancestor(of: choice, matching: find.byType(Wrap)).first;
      final imageFinder = find.descendant(
        of: row,
        matching: find.byType(Image),
      );
      final image = tester.widget<Image>(imageFinder);
      final memory = (image.image as ResizeImage).imageProvider as MemoryImage;
      expect(memory.bytes, orderedEquals(portraits[entry.key]!));

      await tester.ensureVisible(choice);
      await tester.tap(choice);
      await tester.pumpAndSettle();
      expect(tester.widget<ChoiceChip>(choice).selected, isTrue);
      expect(find.text('キャラクター: ${entry.value}'), findsOneWidget);
    }
  });
}
