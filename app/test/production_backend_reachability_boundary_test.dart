import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

import 'package:app/production/backend/production_backend_operation.dart';

void main() {
  test('production graph excludes transport and platform reachability', () {
    final source = _productionSource();
    final forbidden = <RegExp>[
      RegExp(r'\bBackendApiClient\b'),
      RegExp(
        r'''(?:import|export|part)\s+['"][^'"]*(?:services|operators|models|screens|widgets)/''',
      ),
      RegExp(r'https?://', caseSensitive: false),
      RegExp(r'localhost', caseSensitive: false),
      RegExp(r'127\.0\.0\.1'),
      RegExp(
        r'(?<!\d)(?:10\.(?:\d{1,3}\.){2}\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})(?!\d)',
      ),
      RegExp(r'''['"]/[^'"]+['"]'''),
      RegExp(r'package:http/'),
      RegExp(r'dart:io'),
      RegExp(r'\b(?:HttpClient|WebSocket|Socket|Client)\b'),
      RegExp(r'package:(?:permission_handler|device_info_plus|path_provider)/'),
    ];

    for (final pattern in forbidden) {
      expect(pattern.hasMatch(source), isFalse, reason: 'forbidden: $pattern');
    }
  });

  test('production graph excludes explicit non-product symbols and routes', () {
    final source = _productionSource();
    const forbiddenSymbols = <String>[
      'fetchHealthStatus',
      'fetchDemoStatus',
      'fetchGoogleHealthDiagnostics',
      'fetchGoogleHealthSelfCheck',
      'fetchGoogleHealthPreflight',
      'submitVoiceInputDemoRequest',
      'submitVoiceOutputDemoRequest',
      'submitMotionDemoRequest',
      'RealtimeTextStreamClient',
      'FrameworkV600RealtimeSessionClient',
      'CharacterMotionPresentationClient',
      'FrameworkVtsMotionPresentationClient',
    ];
    const forbiddenRouteFragments = <String>[
      '/demo/',
      '/realtime/',
      '/framework/',
      '/voice-input',
      '/voice-output',
      '/motion',
      '/google-health/diagnostics',
      '/google-health/self-check',
      '/google-health/preflight',
      '/health',
    ];

    for (final symbol in forbiddenSymbols) {
      expect(source, isNot(contains(symbol)), reason: symbol);
    }
    for (final route in forbiddenRouteFragments) {
      expect(source, isNot(contains(route)), reason: route);
    }
  });

  test('non-product names and routes are denied as unknown', () {
    const nonProductOperations = <String>[
      'fetchHealthStatus',
      'fetchDemoStatus',
      'fetchGoogleHealthDiagnostics',
      'fetchGoogleHealthSelfCheck',
      'fetchGoogleHealthPreflight',
      'submitVoiceInputDemoRequest',
      'submitVoiceOutputDemoRequest',
      'submitMotionDemoRequest',
      '/demo/status',
      '/realtime/session',
      '/framework/session/start',
      '/google-health/diagnostics',
      '/health',
    ];

    for (final operation in nonProductOperations) {
      expect(
        productionBackendAccessDecisionFor(operation),
        ProductionBackendAccessDecision.denyUnknown,
        reason: operation,
      );
      expect(isProductionBackendOperationAllowed(operation), isFalse);
    }
    expect(
      productionBackendAccessDecisionFor(Object()),
      ProductionBackendAccessDecision.denyUnknown,
    );
  });

  test('health-pending operations receive an explicit deny decision', () {
    const operations = <ProductionBackendOperation>{
      ProductionBackendOperation.loadFitbitConnectionStatus,
      ProductionBackendOperation.startFitbitConnection,
      ProductionBackendOperation.loadGoogleHealthConnectionGuidance,
    };

    for (final operation in operations) {
      expect(
        productionBackendAccessDecisionFor(operation),
        ProductionBackendAccessDecision.denyHealthPendingDecision,
      );
      expect(isProductionBackendOperationAllowed(operation), isFalse);
    }
  });

  test('legacy non-product methods remain outside production', () {
    final backendSource = File(
      'lib/services/backend_api_client.dart',
    ).readAsStringSync();
    for (final symbol in <String>[
      'fetchHealthStatus',
      'fetchDemoStatus',
      'fetchGoogleHealthDiagnostics',
      'fetchGoogleHealthSelfCheck',
      'fetchGoogleHealthPreflight',
      'submitVoiceInputDemoRequest',
      'submitVoiceOutputDemoRequest',
      'submitMotionDemoRequest',
    ]) {
      expect(backendSource, contains(symbol), reason: symbol);
    }
  });
}

String _productionSource() {
  final files = <File>[
    File('lib/main_production.dart'),
    ...Directory('lib/production')
        .listSync(recursive: true)
        .whereType<File>()
        .where((file) => file.path.endsWith('.dart')),
  ]..sort((left, right) => left.path.compareTo(right.path));
  return files.map((file) => file.readAsStringSync()).join('\n');
}
