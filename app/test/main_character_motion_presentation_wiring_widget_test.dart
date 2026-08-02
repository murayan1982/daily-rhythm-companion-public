import 'package:app/main.dart';
import 'package:app/models/character_motion_presentation.dart';
import 'package:app/models/character_preset.dart';
import 'package:app/models/demo_status.dart';
import 'package:app/models/sleep_provider_selection.dart';
import 'package:app/models/sleep_summary.dart';
import 'package:app/services/backend_api_client.dart';
import 'package:app/services/character_motion_presentation_client.dart';
import 'package:app/services/character_motion_presentation_controller.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('default main app keeps character motion unconfigured', (
    tester,
  ) async {
    await tester.pumpWidget(
      const DailyRhythmCompanionApp(apiClient: _FakeBackendApiClient()),
    );
    await tester.pumpAndSettle();

    expect(
      _detailText(tester, 'character-motion-configuration'),
      'unconfigured',
    );
    expect(_detailText(tester, 'character-motion-opt-in-status'), 'off');
    expect(_button(tester, 'character-motion-apply-button').enabled, isFalse);
    expect(
      find.byKey(const Key('character-display-static-baseline')),
      findsOne,
    );
  });

  testWidgets(
    'main injects one default-off controller with no transport call',
    (tester) async {
      var factoryCalls = 0;
      var transportCalls = 0;
      late _TrackingController controller;

      await tester.pumpWidget(
        DailyRhythmCompanionApp(
          apiClient: const _FakeBackendApiClient(),
          characterMotionPresentationControllerFactory: () {
            factoryCalls += 1;
            controller = _TrackingController(
              client: CharacterMotionPresentationClient(
                transport: (request) async {
                  transportCalls += 1;
                  return _result(request);
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
        _detailText(tester, 'character-motion-configuration'),
        'configured',
      );
      expect(_detailText(tester, 'character-motion-opt-in-status'), 'off');
      expect(_button(tester, 'character-motion-apply-button').enabled, isFalse);

      await tester.pumpWidget(const MaterialApp(home: SizedBox.shrink()));
      await tester.pumpAndSettle();
      expect(controller.disposeCalls, 1);
    },
  );
}

class _TrackingController extends CharacterMotionPresentationController {
  _TrackingController({required super.client});

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
  final texts = tester
      .widgetList<Text>(find.descendant(of: row, matching: find.byType(Text)))
      .map((widget) => widget.data)
      .whereType<String>()
      .toList();
  return texts.last;
}

Map<String, Object?> _result(CharacterMotionPresentationRequest request) =>
    <String, Object?>{
      'schema_version': 'drc.v3.framework-mock-motion-execution.1',
      'status': 'disabled',
      'source_fact': request.sourceFact.wireName,
      'cue': null,
      'source_event_type': request.sourceEventType,
      'source_session_id': null,
      'source_turn_id': null,
      'character_id': request.characterId,
      'commands_requested': 1,
      'commands_completed': 0,
      'command_results': <Object?>[],
      'event_types': <String>[],
      'framework_import_attempted': false,
      'session_created': false,
      'session_closed': false,
      'adapter': 'mock',
      'real_adapter_enabled': false,
      'provider_execution_allowed': false,
      'provider_execution_attempted': false,
      'network_execution': false,
      'reason_code': 'framework_mock_motion_disabled',
      'safe_message': 'Framework mock motion execution is disabled.',
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
