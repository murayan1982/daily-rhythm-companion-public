import 'package:app/main.dart';
import 'package:app/models/character_preset.dart';
import 'package:app/models/demo_status.dart';
import 'package:app/models/sleep_provider_selection.dart';
import 'package:app/models/sleep_summary.dart';
import 'package:app/services/backend_api_client.dart';
import 'package:app/services/realtime_terminal_voice_output_home_screen_binding.dart';
import 'package:app/services/realtime_terminal_voice_output_orchestrator.dart';
import 'package:app/services/realtime_text_stream_client.dart';
import 'package:app/services/realtime_text_stream_controller.dart';
import 'package:app/services/voice_output_queue.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;

void main() {
  testWidgets('default app leaves RT-5 voice output unconfigured', (
    tester,
  ) async {
    await tester.pumpWidget(
      const DailyRhythmCompanionApp(apiClient: _FakeBackendApiClient()),
    );
    await tester.pumpAndSettle();

    expect(find.text('Configuration: unconfigured'), findsOne);
    expect(find.text('Enable manual voice output'), findsOne);
    expect(_switch(tester).value, isFalse);
    expect(_switch(tester).onChanged, isNull);
  });

  testWidgets('configured factories build one ready default-off binding', (
    tester,
  ) async {
    final fixture = _BindingFixture();
    var bindingFactoryCalls = 0;

    await tester.pumpWidget(
      DailyRhythmCompanionApp(
        apiClient: const _FakeBackendApiClient(),
        realtimeTextStreamControllerFactory: _streamController,
        realtimeTerminalVoiceOutputBindingFactory: () {
          bindingFactoryCalls += 1;
          return fixture.binding;
        },
      ),
    );
    await tester.pumpAndSettle();

    expect(bindingFactoryCalls, 1);
    expect(find.text('Configuration: configured'), findsOne);
    expect(find.text('Opt-in: off'), findsOne);
    expect(fixture.synthesisCalls, 0);
    expect(fixture.playbackCalls, 0);
    expect(fixture.localStopCalls, 0);
    expect(
      find.text(
        'This RT-5 binding owns a separate local player and does not control the existing Voice Output Demo player.',
      ),
      findsOne,
    );
  });

  testWidgets('binding factory is not called without realtime stream', (
    tester,
  ) async {
    var bindingFactoryCalls = 0;

    await tester.pumpWidget(
      DailyRhythmCompanionApp(
        apiClient: const _FakeBackendApiClient(),
        realtimeTerminalVoiceOutputBindingFactory: () {
          bindingFactoryCalls += 1;
          return _BindingFixture().binding;
        },
      ),
    );
    await tester.pumpAndSettle();

    expect(bindingFactoryCalls, 0);
    expect(find.text('Configuration: unconfigured'), findsOne);
  });

  testWidgets('app teardown disposes the configured binding once', (
    tester,
  ) async {
    final fixture = _BindingFixture();

    await tester.pumpWidget(
      DailyRhythmCompanionApp(
        apiClient: const _FakeBackendApiClient(),
        realtimeTextStreamControllerFactory: _streamController,
        realtimeTerminalVoiceOutputBindingFactory: () => fixture.binding,
      ),
    );
    await tester.pumpAndSettle();

    await tester.pumpWidget(const MaterialApp(home: SizedBox.shrink()));
    await tester.pump();

    expect(fixture.disposeOwnedCalls, 1);
    expect(fixture.synthesisCalls, 0);
    expect(fixture.playbackCalls, 0);
  });
}

SwitchListTile _switch(WidgetTester tester) {
  return tester.widget<SwitchListTile>(
    find.byKey(const Key('realtime-terminal-voice-output-opt-in')),
  );
}

RealtimeTextStreamController _streamController() {
  return RealtimeTextStreamController(
    client: RealtimeTextStreamClient(
      baseUrl: 'https://backend.test',
      client: _NoopHttpClient(),
    ),
  );
}

class _BindingFixture {
  _BindingFixture() {
    queue = VoiceOutputQueueController(
      stopLocalPlayback: () async {
        localStopCalls += 1;
      },
    );
    orchestrator = RealtimeTerminalVoiceOutputOrchestrator(
      queue: queue,
      synthesize: (_) async {
        synthesisCalls += 1;
        return const RealtimeTerminalVoiceSynthesisResult.rejected();
      },
      playToTerminal: (_) async {
        playbackCalls += 1;
        return const RealtimeTerminalVoicePlaybackResult.failed();
      },
    );
    binding = OwnedRealtimeTerminalVoiceOutputHomeScreenBinding(
      orchestrator: orchestrator,
      disposeOwnedResources: () {
        disposeOwnedCalls += 1;
        queue.dispose();
      },
    );
  }

  late final VoiceOutputQueueController queue;
  late final RealtimeTerminalVoiceOutputOrchestrator orchestrator;
  late final OwnedRealtimeTerminalVoiceOutputHomeScreenBinding binding;

  int synthesisCalls = 0;
  int playbackCalls = 0;
  int localStopCalls = 0;
  int disposeOwnedCalls = 0;
}

class _NoopHttpClient extends http.BaseClient {
  @override
  Future<http.StreamedResponse> send(http.BaseRequest request) async {
    fail('Main RT-5e wiring tests must not execute stream HTTP requests.');
  }
}

class _FakeBackendApiClient extends BackendApiClient {
  const _FakeBackendApiClient() : super(baseUrl: 'https://backend.test');

  @override
  Future<String> fetchHealthStatus() async => 'ok / API v2.1.0';

  @override
  Future<List<CharacterPreset>> fetchCharacters() async {
    return const <CharacterPreset>[
      CharacterPreset(
        characterId: 'default',
        displayName: 'Default',
        description: 'Default test character',
        personalityType: 'friendly',
        speakingStyle: 'casual',
        adviceStyle: 'light',
      ),
    ];
  }

  @override
  Future<SleepSummary> fetchSleepSummary() async {
    return const SleepSummary(
      date: '2026-07-31',
      totalSleepMinutes: 420,
      efficiency: 88,
      deepSleepMinutes: 80,
      remSleepMinutes: 90,
      awakeMinutes: 20,
      source: 'mock',
      available: true,
    );
  }

  @override
  Future<SleepProviderSelectionStatus>
  fetchSleepProviderSelectionStatus() async {
    return const SleepProviderSelectionStatus(
      configuredProvider: 'mock',
      configuredProviderLabel: 'Mock',
      configuredProviderRole: 'credential_free_default',
      configuredProviderSupported: true,
      selectionMode: 'backend_config',
      changeRequiresBackendRestart: true,
      availableProviders: <SleepProviderOption>[],
      message: 'Mock provider selected.',
    );
  }

  @override
  Future<DemoStatus> fetchDemoStatus() async {
    return const DemoStatus(
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
}
