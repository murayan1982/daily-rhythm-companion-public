import 'package:app/main.dart';
import 'package:app/services/framework_vts_motion_presentation_client.dart';
import 'package:app/services/framework_vts_motion_presentation_controller.dart';
import 'package:app/models/character_preset.dart';
import 'package:app/models/demo_status.dart';
import 'package:app/models/sleep_provider_selection.dart';
import 'package:app/models/sleep_summary.dart';
import 'package:app/services/backend_api_client.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('default main app keeps configured VTS motion unconfigured', (
    tester,
  ) async {
    await tester.pumpWidget(
      const DailyRhythmCompanionApp(apiClient: _FakeBackendApiClient()),
    );
    await tester.pumpAndSettle();
    expect(
      _detailText(tester, 'framework-vts-motion-configuration'),
      'unconfigured',
    );
    expect(_detailText(tester, 'framework-vts-motion-opt-in-status'), 'off');
    expect(
      find.byKey(const ValueKey('framework-vts-motion-selector')),
      findsNothing,
    );
    expect(
      _button(tester, 'framework-vts-motion-apply-button').enabled,
      isFalse,
    );
  });

  testWidgets('main injects one default-off VTS controller without transport', (
    tester,
  ) async {
    var factoryCalls = 0;
    var transportCalls = 0;
    late _TrackingVtsController controller;
    await tester.pumpWidget(
      DailyRhythmCompanionApp(
        apiClient: const _FakeBackendApiClient(),
        frameworkVtsMotionPresentationControllerFactory: () {
          factoryCalls += 1;
          controller = _TrackingVtsController(
            client: FrameworkVtsMotionPresentationClient(
              transport: (_) async {
                transportCalls += 1;
                return _vtsResult();
              },
            ),
          );
          return controller;
        },
      ),
    );
    await tester.pumpAndSettle();
    expect(factoryCalls, 1);
    expect(transportCalls, 0);
    expect(
      _detailText(tester, 'framework-vts-motion-configuration'),
      'configured',
    );
    expect(_detailText(tester, 'framework-vts-motion-opt-in-status'), 'off');
    expect(
      find.byKey(const ValueKey('framework-vts-motion-selector')),
      findsNothing,
    );
    await tester.pumpWidget(const MaterialApp(home: SizedBox.shrink()));
    await tester.pumpAndSettle();
    expect(controller.disposeCalls, 1);
  });
}

class _TrackingVtsController extends FrameworkVtsMotionPresentationController {
  _TrackingVtsController({required super.client});
  int disposeCalls = 0;
  @override
  void dispose() {
    disposeCalls += 1;
    super.dispose();
  }
}

ButtonStyleButton _button(WidgetTester tester, String key) =>
    tester.widget<ButtonStyleButton>(find.byKey(ValueKey(key)));
String _detailText(WidgetTester tester, String key) {
  final row = find.byKey(ValueKey(key));
  return tester
      .widgetList<Text>(find.descendant(of: row, matching: find.byType(Text)))
      .map((w) => w.data)
      .whereType<String>()
      .toList()
      .last;
}

Map<String, Object?> _vtsResult() => <String, Object?>{
  'schema_version': 'drc.v3.framework-vts-motion-execution.1',
  'status': 'disabled',
  'commands_requested': 1,
  'commands_applied': 0,
  'commands_completed': 0,
  'optional_commands_skipped': 0,
  'command_results': <Object?>[],
  'event_types': <Object?>[],
  'framework_import_attempted': false,
  'session_created': false,
  'session_closed': false,
  'adapter': 'vts',
  'real_adapter_enabled': false,
  'provider_execution_allowed': false,
  'provider_execution_attempted': false,
  'network_execution_attempted': false,
  'real_motion_executed': false,
  'reason_code': 'framework_vts_motion_disabled',
  'safe_message': 'disabled',
};

class _FakeBackendApiClient extends BackendApiClient {
  const _FakeBackendApiClient() : super(baseUrl: 'http://backend.test');

  @override
  Future<String> fetchHealthStatus() async => 'ok / API v2.1.0';

  @override
  Future<List<CharacterPreset>> fetchCharacters() async =>
      const <CharacterPreset>[
        CharacterPreset(
          characterId: 'gentle_mina',
          displayName: 'Mina',
          description: 'Gentle test character',
          personalityType: 'gentle',
          speakingStyle: 'casual',
          adviceStyle: 'rest_focused',
        ),
      ];

  @override
  Future<SleepSummary> fetchSleepSummary() async => const SleepSummary(
    date: '2026-08-01',
    totalSleepMinutes: 420,
    efficiency: 88,
    deepSleepMinutes: 80,
    remSleepMinutes: 90,
    awakeMinutes: 20,
    source: 'mock',
    available: true,
  );

  @override
  Future<SleepProviderSelectionStatus>
  fetchSleepProviderSelectionStatus() async =>
      const SleepProviderSelectionStatus(
        configuredProvider: 'mock',
        configuredProviderLabel: 'Mock',
        configuredProviderRole: 'credential_free_default',
        configuredProviderSupported: true,
        selectionMode: 'backend_config',
        changeRequiresBackendRestart: true,
        availableProviders: <SleepProviderOption>[],
        message: 'Mock provider selected.',
      );

  @override
  Future<DemoStatus> fetchDemoStatus() async => const DemoStatus(
    engine: 'mock',
    mode: 'mock_safe',
    capabilities: <String, DemoCapabilityStatus>{
      'llm_response': DemoCapabilityStatus(
        status: 'unavailable',
        source: 'mock',
        message: 'LLM unavailable.',
      ),
      'voice_input': DemoCapabilityStatus(
        status: 'unavailable',
        source: 'not_implemented',
        message: 'Voice input unavailable.',
      ),
      'voice_output': DemoCapabilityStatus(
        status: 'unavailable',
        source: 'not_implemented',
        message: 'Voice output unavailable.',
      ),
      'live2d_motion': DemoCapabilityStatus(
        status: 'unavailable',
        source: 'not_implemented',
        message: 'Motion unavailable.',
      ),
    },
  );
}
