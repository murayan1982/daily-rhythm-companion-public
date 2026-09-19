import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

import 'package:app/production/backend/production_backend_operation.dart';
import 'package:app/production/core/production_capability.dart';

void main() {
  test('approved production capability set is exact', () {
    expect(productionCapabilities, <ProductionCapability>{
      ProductionCapability.sleepHealthConnection,
      ProductionCapability.moodCheckIn,
      ProductionCapability.characterSelection,
      ProductionCapability.dailyAdvice,
      ProductionCapability.optionalTextChat,
      ProductionCapability.history,
    });
    expect(productionCapabilities, hasLength(6));
    expect(productionCapabilities, ProductionCapability.values.toSet());
  });

  test('symbolic production Backend operation set is exact', () {
    expect(
      productionBackendOperationDispositions.keys.toSet(),
      ProductionBackendOperation.values.toSet(),
    );
    expect(ProductionBackendOperation.values, hasLength(14));
  });

  test('every operation has exactly one disposition', () {
    expect(productionBackendOperationDispositions, hasLength(14));
    for (final operation in ProductionBackendOperation.values) {
      expect(productionBackendDispositionFor(operation), isNotNull);
      expect(
        productionBackendOperationDispositions.keys.where(
          (candidate) => candidate == operation,
        ),
        hasLength(1),
      );
    }
  });

  test('health operations remain pending and inactive', () {
    const healthOperations = <ProductionBackendOperation>{
      ProductionBackendOperation.loadFitbitConnectionStatus,
      ProductionBackendOperation.startFitbitConnection,
      ProductionBackendOperation.loadGoogleHealthConnectionGuidance,
    };

    for (final operation in healthOperations) {
      expect(
        productionBackendDispositionFor(operation),
        ProductionBackendOperationDisposition.healthPendingDecision,
      );
      expect(activeProductionBackendOperations, isNot(contains(operation)));
      expect(isActiveProductionBackendOperation(operation), isFalse);
    }
    expect(activeProductionBackendOperations, hasLength(11));
  });

  test('unknown operations are denied by default', () {
    expect(productionBackendDispositionFor('unknown'), isNull);
    expect(isActiveProductionBackendOperation('unknown'), isFalse);
    expect(isActiveProductionBackendOperation(Object()), isFalse);
  });

  test('production boundary sources contain no transport configuration', () {
    final source = _boundarySource();
    final forbidden = <RegExp>[
      RegExp(r'https?://', caseSensitive: false),
      RegExp(
        'local'
        'host',
        caseSensitive: false,
      ),
      RegExp(r'127\.0\.0\.1'),
      RegExp(
        r'(?<!\d)(?:10\.(?:\d{1,3}\.){2}\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})(?!\d)',
      ),
      RegExp(r'''['"]/[A-Za-z0-9]'''),
      RegExp(
        'Backend'
        'ApiClient',
      ),
      RegExp(r"package:http/"),
      RegExp(r"dart:io"),
    ];

    for (final pattern in forbidden) {
      expect(pattern.hasMatch(source), isFalse, reason: '$pattern');
    }
  });

  test('production sources keep non-product and legacy imports excluded', () {
    final source = _boundarySource();
    final forbiddenTerms = <String>[
      'voice',
      'real'
          'time',
      'motion',
      'demo',
      'developer',
      'operator',
      'diagnostic',
      'frame'
          'work',
    ];
    for (final term in forbiddenTerms) {
      expect(source.toLowerCase(), isNot(contains(term)));
    }

    final productionSources = Directory('lib/production')
        .listSync(recursive: true)
        .whereType<File>()
        .where((file) => file.path.endsWith('.dart'));
    for (final file in productionSources) {
      final contents = file.readAsStringSync();
      for (final directory in <String>[
        'screens/',
        'services/',
        'models/',
        'widgets/',
      ]) {
        expect(contents, isNot(contains(directory)), reason: directory);
      }
    }
  });
}

String _boundarySource() => <String>[
  File('lib/production/core/production_capability.dart').readAsStringSync(),
  File(
    'lib/production/backend/production_backend_operation.dart',
  ).readAsStringSync(),
].join('\n');
