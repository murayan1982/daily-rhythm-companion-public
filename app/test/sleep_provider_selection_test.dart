import 'package:flutter_test/flutter_test.dart';

import 'package:app/models/sleep_provider_selection.dart';

void main() {
  test('parses backend-owned provider selection metadata', () {
    final status = SleepProviderSelectionStatus.fromJson({
      'configured_provider': 'google_health',
      'configured_provider_label': 'Google Health',
      'configured_provider_role': 'configured_real_provider',
      'configured_provider_supported': true,
      'selection_mode': 'backend_config',
      'change_requires_backend_restart': true,
      'provider_options': [
        {
          'provider': 'google_health',
          'display_label': 'Google Health',
          'role': 'configured_real_provider',
          'deprecated': false,
          'alias_for': null,
          'real_operator_verification_required': false,
        },
      ],
      'message': 'Selected by backend configuration.',
    });

    expect(status.configuredProvider, 'google_health');
    expect(status.configuredProviderLabel, 'Google Health');
    expect(status.isGoogleHealth, isTrue);
    expect(status.isFitbit, isFalse);
    expect(status.displaySelectionMode, 'バックエンド設定');
    expect(status.displayConfiguredState, '設定済み');
    expect(status.changeRequiresBackendRestart, isTrue);
  });

  test('marks legacy Fitbit as migration reference', () {
    final status = SleepProviderSelectionStatus.fromJson({
      'configured_provider': 'fitbit',
      'configured_provider_label': 'Fitbit（旧Web API・移行参照）',
      'configured_provider_role': 'legacy_migration_reference',
      'configured_provider_supported': true,
      'selection_mode': 'backend_config',
      'change_requires_backend_restart': true,
      'provider_options': [
        {
          'provider': 'fitbit',
          'display_label': 'Fitbit（旧Web API・移行参照）',
          'role': 'legacy_migration_reference',
          'deprecated': false,
          'alias_for': null,
          'real_operator_verification_required': false,
        },
      ],
      'message': 'Selected by backend configuration.',
    });

    expect(status.isFitbit, isTrue);
    expect(status.requiresRealOperatorVerification, isFalse);
    expect(status.displayConfiguredState, '移行参照のみ');
    expect(status.configuredOption?.displayRole, '旧Web API・移行参照');
  });

  test('marks deprecated compatibility aliases conservatively', () {
    final status = SleepProviderSelectionStatus.fromJson({
      'configured_provider': 'fitbit_stub',
      'configured_provider_label': 'ウェアラブル連携サンプル（旧設定）',
      'configured_provider_role': 'deprecated_alias',
      'configured_provider_supported': true,
      'provider_options': [
        {
          'provider': 'fitbit_stub',
          'display_label': 'ウェアラブル連携サンプル（旧設定）',
          'role': 'deprecated_alias',
          'deprecated': true,
          'alias_for': 'wearable_stub',
        },
      ],
      'message': '',
    });

    expect(status.isMockSafeProvider, isTrue);
    expect(status.displayConfiguredState, '旧設定');
    expect(status.configuredOption?.aliasFor, 'wearable_stub');
  });

  test('reports unsupported selection without inventing availability', () {
    final status = SleepProviderSelectionStatus.fromJson({
      'configured_provider': 'private_provider',
      'configured_provider_label': '未対応のsleep provider設定',
      'configured_provider_role': 'unsupported',
      'configured_provider_supported': false,
      'provider_options': const [],
      'message': '',
    });

    expect(status.configuredProviderSupported, isFalse);
    expect(status.displayConfiguredState, '未対応');
    expect(status.configuredOption, isNull);
  });
}
