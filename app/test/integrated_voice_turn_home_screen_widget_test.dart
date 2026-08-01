import 'package:app/models/character_preset.dart';
import 'package:app/models/demo_status.dart';
import 'package:app/models/sleep_provider_selection.dart';
import 'package:app/models/sleep_summary.dart';
import 'package:app/screens/home_screen.dart';
import 'package:app/services/backend_api_client.dart';
import 'package:app/services/integrated_voice_turn_coordinator.dart';
import 'package:app/services/integrated_voice_turn_home_screen_binding.dart';
import 'package:app/services/microphone_capture.dart';
import 'package:app/services/microphone_permission.dart';
import 'package:app/services/realtime_terminal_voice_output_orchestrator.dart';
import 'package:app/services/speech_activity_source.dart';
import 'package:app/services/voice_output_queue.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('configured section is session-local and execution-free on toggle', (
    tester,
  ) async {
    final fixture = _WidgetBindingFixture();

    await tester.pumpWidget(
      MaterialApp(
        home: HomeScreen(
          apiClient: const _FakeBackendApiClient(),
          integratedVoiceTurnBindingFactory: () => fixture.binding,
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Integrated Voice Turn'), findsOne);
    expect(find.text('Integrated configuration: configured'), findsOne);
    expect(find.text('Integrated opt-in: off'), findsOne);
    expect(find.text('Coordinator phase: idle'), findsOne);
    expect(find.text('Speech source phase: idle'), findsOne);
    expect(
      find.text(
        'The integrated runtime owns a dedicated stream controller, TTS queue, orchestrator, and local player; it does not share the manual RT-4f4 / RT-5e resources.',
      ),
      findsOne,
    );

    final switchFinder = find.byKey(
      const Key('integrated-voice-turn-opt-in'),
    );
    await tester.ensureVisible(switchFinder);
    await tester.tap(switchFinder);
    await tester.pump();

    expect(find.text('Integrated opt-in: on'), findsOne);
    expect(fixture.engine.startCalls, 0);
    expect(fixture.source.armCalls, 0);
    expect(fixture.synthesisCalls, 0);
    expect(fixture.playbackCalls, 0);

    final startButton = tester.widget<ElevatedButton>(
      find.byKey(const Key('integrated-voice-turn-start-button')),
    );
    expect(startButton.onPressed, isNotNull);
    final stopButton = tester.widget<OutlinedButton>(
      find.byKey(const Key('integrated-voice-turn-stop-capture-button')),
    );
    expect(stopButton.onPressed, isNull);

    await tester.pumpWidget(const MaterialApp(home: SizedBox.shrink()));
    await tester.pumpAndSettle();
    expect(fixture.disposeOwnedCalls, 1);
  });

  testWidgets('unconfigured section remains disabled and uniquely labelled', (
    tester,
  ) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: HomeScreen(apiClient: _FakeBackendApiClient()),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Integrated configuration: unconfigured'), findsOne);
    expect(find.text('Integrated opt-in: off'), findsOne);
    expect(find.text('Configuration: unconfigured'), findsOne);
    expect(find.text('Opt-in: off'), findsOne);

    final integratedSwitch = tester.widget<SwitchListTile>(
      find.byKey(const Key('integrated-voice-turn-opt-in')),
    );
    expect(integratedSwitch.value, isFalse);
    expect(integratedSwitch.onChanged, isNull);
  });

  testWidgets('metadata section never renders private sentinel values', (
    tester,
  ) async {
    final fixture = _WidgetBindingFixture();
    await tester.pumpWidget(
      MaterialApp(
        home: HomeScreen(
          apiClient: const _FakeBackendApiClient(),
          integratedVoiceTurnBindingFactory: () => fixture.binding,
        ),
      ),
    );
    await tester.pumpAndSettle();

    final renderedText = tester
        .widgetList<Text>(find.byType(Text))
        .map((widget) => widget.data ?? widget.textSpan?.toPlainText() ?? '')
        .join('|');
    for (final forbidden in <String>[
      'private transcript sentinel',
      'private generated response sentinel',
      'private capture path sentinel',
      'private provider payload sentinel',
      'speech-private-event-id',
    ]) {
      expect(renderedText, isNot(contains(forbidden)));
    }

    await tester.pumpWidget(const MaterialApp(home: SizedBox.shrink()));
    await tester.pumpAndSettle();
  });
}

class _WidgetBindingFixture {
  _WidgetBindingFixture() {
    engine = FakeMicrophoneCaptureEngine();
    final captureSession = IntegratedVoiceTurnCaptureSession(
      controller: MicrophoneCaptureController(
        permissionGateway: FakeMicrophonePermissionGateway(
          initialStatus: MicrophonePermissionStatus.granted,
        ),
        engine: engine,
        maximumAllowedDuration: integratedVoiceTurnCaptureMaximumDuration,
      ),
    );
    source = _IdleSpeechActivitySource();
    queue = VoiceOutputQueueController(stopLocalPlayback: () async {});
    voiceOutput = RealtimeTerminalVoiceOutputOrchestrator(
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
    final coordinator = IntegratedVoiceTurnCoordinator(
      captureCompleted: captureSession.captureCompleted,
      stageCapture: (_) async => throw StateError(
        'private capture path sentinel',
      ),
      streamControllerFactory: () => throw StateError(
        'private provider payload sentinel',
      ),
      transcriptHandoffFactory: (_) => throw StateError(
        'private transcript sentinel',
      ),
      voiceOutput: voiceOutput,
    );
    binding = IntegratedVoiceTurnHomeScreenBinding(
      coordinator: coordinator,
      captureSession: captureSession,
      speechActivitySource: source,
      observeApplicationLifecycle: false,
      initialForeground: true,
      disposeOwnedResources: () {
        disposeOwnedCalls += 1;
        voiceOutput.dispose();
        queue.dispose();
      },
    );
  }

  late final FakeMicrophoneCaptureEngine engine;
  late final _IdleSpeechActivitySource source;
  late final VoiceOutputQueueController queue;
  late final RealtimeTerminalVoiceOutputOrchestrator voiceOutput;
  late final IntegratedVoiceTurnHomeScreenBinding binding;
  int synthesisCalls = 0;
  int playbackCalls = 0;
  int disposeOwnedCalls = 0;
}

class _IdleSpeechActivitySource extends SpeechActivitySource {
  SpeechActivitySourceState _state =
      const SpeechActivitySourceState.idle();
  int armCalls = 0;

  @override
  SpeechActivitySourceState get state => _state;

  @override
  void setEventHandler(SpeechActivityEventHandler? handler) {}

  @override
  Future<bool> arm({required int generation, required bool foreground}) async {
    armCalls += 1;
    _state = SpeechActivitySourceState(
      phase: SpeechActivitySourcePhase.armed,
      armingGeneration: generation,
      emittedEventCount: 0,
      foreground: foreground,
    );
    notifyListeners();
    return true;
  }

  @override
  Future<void> setForeground(bool foreground) async {
    _state = SpeechActivitySourceState(
      phase: _state.phase,
      armingGeneration: _state.armingGeneration,
      emittedEventCount: _state.emittedEventCount,
      foreground: foreground,
    );
  }

  @override
  Future<void> disarm() async {
    if (_state.isActive) {
      _state = SpeechActivitySourceState(
        phase: SpeechActivitySourcePhase.stopped,
        armingGeneration: _state.armingGeneration,
        emittedEventCount: _state.emittedEventCount,
        foreground: _state.foreground,
      );
      notifyListeners();
    }
  }

  @override
  Future<void> close() async {
    _state = SpeechActivitySourceState(
      phase: SpeechActivitySourcePhase.disposed,
      armingGeneration: _state.armingGeneration,
      emittedEventCount: _state.emittedEventCount,
      foreground: false,
    );
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
      date: '2026-08-01',
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
