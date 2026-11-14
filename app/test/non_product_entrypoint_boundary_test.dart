import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

import 'package:app/main.dart' as default_entrypoint;

void main() {
  test('main.dart is only the non-product compatibility shim', () {
    final source = File('lib/main.dart').readAsStringSync();

    expect(
      source,
      "import 'main_non_product.dart' as non_product;\n"
      '\n'
      "export 'main_non_product.dart' show DailyRhythmCompanionApp;\n"
      '\n'
      'void main() => non_product.main();\n',
    );
    expect(source, isNot(contains("import 'package:flutter/material.dart'")));
    expect(source, isNot(contains("import 'screens/home_screen.dart'")));
    expect(source, isNot(contains('BackendApiClient')));
    expect(source, isNot(contains('services/')));
    expect(source, isNot(contains('operators/')));
    expect(source, isNot(contains('production/')));
  });

  test('package:app/main.dart still exports DailyRhythmCompanionApp', () {
    expect(default_entrypoint.DailyRhythmCompanionApp, isNotNull);
  });

  test('main_non_product.dart owns the mixed HomeScreen composition', () {
    final source = File('lib/main_non_product.dart').readAsStringSync();

    expect(source, contains("import 'package:flutter/material.dart';"));
    expect(source, contains("import 'screens/home_screen.dart';"));
    expect(source, contains("import 'services/backend_api_client.dart';"));
    expect(source, contains('class DailyRhythmCompanionApp'));
    expect(source, contains('BackendApiClient()'));
    expect(source, contains('HomeScreen('));
    expect(source, contains('ConfiguredRealtimeTextStreamRuntime'));
    expect(source, contains('ConfiguredRealtimeTerminalVoiceOutputRuntime'));
    expect(source, contains('ConfiguredIntegratedVoiceTurnRuntime'));
    expect(source, contains('ConfiguredCharacterMotionPresentationRuntime'));
    expect(source, contains('ConfiguredFrameworkVtsMotionPresentationRuntime'));
    expect(source, contains('ConfiguredFrameworkV600RealtimeSessionRuntime'));
  });

  test('main_non_product.dart does not import production source', () {
    final directives = _directiveUris(File('lib/main_non_product.dart'));

    expect(directives, isNot(contains('main_production.dart')));
    expect(directives.any((uri) => uri.startsWith('production/')), isFalse);
    expect(
      directives.any((uri) => uri.startsWith('package:app/production/')),
      isFalse,
    );
    expect(
      directives.any((uri) => uri.startsWith('package:drc_production/')),
      isFalse,
    );
  });

  test('operator entrypoint keeps operator composition outside production', () {
    final source = File('lib/main_rt2ec_operator.dart').readAsStringSync();
    final directives = _directiveUris(File('lib/main_rt2ec_operator.dart'));

    expect(source, contains('Rt2ecOperatorCaptureApp'));
    expect(source, contains('Rt2ecOperatorCaptureDependencies'));
    expect(source, contains('PermissionHandlerMicrophonePermissionGateway'));
    expect(source, contains('RecordMicrophoneCaptureEngine.mobile()'));
    expect(directives, isNot(contains('main_non_product.dart')));
    expect(directives, isNot(contains('main_production.dart')));
    expect(directives.any((uri) => uri.startsWith('production/')), isFalse);
    expect(
      directives.any((uri) => uri.startsWith('package:app/production/')),
      isFalse,
    );
    expect(
      directives.any((uri) => uri.startsWith('package:drc_production/')),
      isFalse,
    );
  });

  test('production graph does not reference non-product entrypoints or UI', () {
    final productionSources = <File>[
      File('lib/main_production.dart'),
      ...Directory('../packages/drc_production/lib')
          .listSync(recursive: true)
          .whereType<File>()
          .where((file) => file.path.endsWith('.dart')),
    ];
    final combined = productionSources
        .map((file) => file.readAsStringSync())
        .join('\n');

    for (final pattern in <RegExp>[
      RegExp(r'\bmain_non_product\.dart\b'),
      RegExp(r'\bmain_rt2ec_operator\.dart\b'),
      RegExp(r'\bmain\.dart\b'),
      RegExp(r'\bDailyRhythmCompanionApp\b'),
      RegExp(r'\bHomeScreen\b'),
      RegExp(r'developer', caseSensitive: false),
      RegExp(r'operator', caseSensitive: false),
      RegExp(r'demo', caseSensitive: false),
      RegExp(r'diagnostic', caseSensitive: false),
    ]) {
      expect(
        pattern.hasMatch(combined),
        isFalse,
        reason: 'forbidden production reference: $pattern',
      );
    }
  });

  test('source hiding and feature flags are not production boundary proof', () {
    final productionSources = <File>[
      File('lib/main_production.dart'),
      ...Directory('../packages/drc_production/lib')
          .listSync(recursive: true)
          .whereType<File>()
          .where((file) => file.path.endsWith('.dart')),
    ];
    final combined = productionSources
        .map((file) => file.readAsStringSync())
        .join('\n');

    for (final pattern in <RegExp>[
      RegExp(r'\bVisibility\b'),
      RegExp(r'\bOffstage\b'),
      RegExp(r'\bOpacity\b'),
      RegExp(r'bool\.fromEnvironment'),
      RegExp(r'String\.fromEnvironment'),
      RegExp(r'feature', caseSensitive: false),
    ]) {
      expect(
        pattern.hasMatch(combined),
        isFalse,
        reason: 'not structural boundary proof: $pattern',
      );
    }
  });
}

List<String> _directiveUris(File file) {
  final source = file.readAsStringSync();
  final pattern = RegExp(
    r'''^\s*(?:import|export|part)\s+['"]([^'"]+)['"]''',
    multiLine: true,
  );
  return pattern.allMatches(source).map((match) => match.group(1)!).toList();
}
