import 'package:app/models/framework_vts_motion_presentation.dart';
import 'package:app/screens/home_screen.dart';
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
  testWidgets('HomeScreen keeps VTS motion unconfigured by default', (
    tester,
  ) async {
    await tester.pumpWidget(
      const MaterialApp(home: HomeScreen(apiClient: _FakeBackendApiClient())),
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

  testWidgets('configured HomeScreen sends only one explicit Apply request', (
    tester,
  ) async {
    var calls = 0;
    final controller = FrameworkVtsMotionPresentationController(
      client: FrameworkVtsMotionPresentationClient(
        transport: (request) async {
          calls += 1;
          expect(request.intent, FrameworkVtsMotionIntent.expression);
          expect(request.selectorValue, 'smile');
          expect(request.characterId, 'gentle_mina');
          return _vtsResult();
        },
      ),
    );
    await tester.pumpWidget(
      MaterialApp(
        home: HomeScreen(
          apiClient: const _FakeBackendApiClient(),
          frameworkVtsMotionPresentationControllerFactory: () => controller,
        ),
      ),
    );
    await tester.pumpAndSettle();
    expect(calls, 0);
    await tester.ensureVisible(
      find.byKey(const ValueKey('framework-vts-motion-opt-in')),
    );
    await tester.tap(find.byKey(const ValueKey('framework-vts-motion-opt-in')));
    await tester.pumpAndSettle();
    expect(calls, 0);
    expect(
      find.byKey(const ValueKey('framework-vts-motion-selector')),
      findsOneWidget,
    );
    await tester.ensureVisible(
      find.byKey(const ValueKey('framework-vts-motion-apply-button')),
    );
    await tester.tap(
      find.byKey(const ValueKey('framework-vts-motion-apply-button')),
    );
    await tester.pumpAndSettle();
    expect(calls, 1);
    expect(_detailText(tester, 'framework-vts-motion-status'), 'disabled');
  });

  testWidgets(
    'Control D reset opt-out and disposal stay local after one completed Apply',
    (tester) async {
      var calls = 0;
      final controller = FrameworkVtsMotionPresentationController(
        client: FrameworkVtsMotionPresentationClient(
          transport: (request) async {
            calls += 1;
            expect(request.intent, FrameworkVtsMotionIntent.expression);
            expect(request.selectorValue, 'smile');
            return _completedVtsResult();
          },
        ),
      );

      await tester.pumpWidget(
        MaterialApp(
          home: HomeScreen(
            apiClient: const _FakeBackendApiClient(),
            frameworkVtsMotionPresentationControllerFactory: () => controller,
          ),
        ),
      );
      await tester.pumpAndSettle();

      final optIn = find.byKey(
        const ValueKey('framework-vts-motion-opt-in'),
      );
      await tester.ensureVisible(optIn);
      await tester.tap(optIn);
      await tester.pumpAndSettle();
      expect(calls, 0);

      final apply = find.byKey(
        const ValueKey('framework-vts-motion-apply-button'),
      );
      await tester.ensureVisible(apply);
      await tester.tap(apply);
      await tester.pumpAndSettle();

      expect(calls, 1);
      expect(_detailText(tester, 'framework-vts-motion-phase'), 'completed');
      expect(_detailText(tester, 'framework-vts-motion-status'), 'completed');
      expect(
        _detailText(tester, 'framework-vts-motion-commands-requested'),
        '1',
      );

      final reset = find.byKey(
        const ValueKey('framework-vts-motion-reset-button'),
      );
      await tester.ensureVisible(reset);
      await tester.tap(reset);
      await tester.pumpAndSettle();

      expect(calls, 1, reason: 'Reset local state must not call transport.');
      expect(_detailText(tester, 'framework-vts-motion-phase'), 'idle');
      expect(_detailText(tester, 'framework-vts-motion-status'), '-');
      expect(
        _detailText(tester, 'framework-vts-motion-commands-requested'),
        '0',
      );
      expect(_detailText(tester, 'framework-vts-motion-opt-in-status'), 'on');

      await tester.ensureVisible(optIn);
      await tester.tap(optIn);
      await tester.pumpAndSettle();

      expect(calls, 1, reason: 'Opt-in OFF must not call transport.');
      expect(_detailText(tester, 'framework-vts-motion-opt-in-status'), 'off');
      expect(_detailText(tester, 'framework-vts-motion-phase'), 'idle');

      await tester.pumpWidget(const SizedBox.shrink());
      await tester.pumpAndSettle();

      expect(calls, 1, reason: 'HomeScreen disposal must not call transport.');
    },
  );
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

Map<String, Object?> _completedVtsResult() => <String, Object?>{
  'schema_version': 'drc.v3.framework-vts-motion-execution.1',
  'status': 'completed',
  'commands_requested': 1,
  'commands_applied': 1,
  'commands_completed': 1,
  'optional_commands_skipped': 0,
  'command_results': <Object?>[
    <String, Object?>{
      'order': 1,
      'intent': 'expression',
      'outcome': 'completed',
      'state': 'idle',
      'adapter_status': 'configured',
      'public_error_code': 'none',
      'retryable': false,
      'skipped': false,
      'safe_message': '',
    },
  ],
  'event_types': <Object?>[],
  'framework_import_attempted': true,
  'session_created': true,
  'session_closed': true,
  'adapter': 'vts',
  'real_adapter_enabled': true,
  'provider_execution_allowed': true,
  'provider_execution_attempted': true,
  'network_execution_attempted': true,
  'real_motion_executed': false,
  'reason_code': 'framework_vts_motion_completed',
  'safe_message': 'Framework VTS motion commands completed.',
};

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
  'safe_message': 'Framework VTS motion execution is disabled.',
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
