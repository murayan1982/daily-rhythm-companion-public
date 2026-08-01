import 'package:app/main.dart';
import 'package:app/models/character_preset.dart';
import 'package:app/models/demo_status.dart';
import 'package:app/models/sleep_provider_selection.dart';
import 'package:app/models/sleep_summary.dart';
import 'package:app/services/backend_api_client.dart';
import 'package:app/services/configured_integrated_voice_turn_runtime.dart';
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
  TestWidgetsFlutterBinding.ensureInitialized();

  test('configured runtime requires every compile-time prerequisite', () async {
    final fixture = _MainBindingFixture();
    var builderCalls = 0;

    ConfiguredIntegratedVoiceTurnRuntime runtime({
      required bool enabled,
      required bool textStreamEnabled,
      required bool voiceOutputEnabled,
      bool supportedPlatform = true,
      String baseUrl = 'https://backend.test',
    }) {
      return ConfiguredIntegratedVoiceTurnRuntime(
        enabled: enabled,
        textStreamEnabled: textStreamEnabled,
        voiceOutputEnabled: voiceOutputEnabled,
        supportedPlatform: supportedPlatform,
        apiClient: _FakeBackendApiClient(baseUrl: baseUrl),
        bindingBuilder: () {
          builderCalls += 1;
          return fixture.binding;
        },
      );
    }

    expect(
      runtime(
        enabled: false,
        textStreamEnabled: true,
        voiceOutputEnabled: true,
      ).buildBindingFactory(),
      isNull,
    );
    expect(
      runtime(
        enabled: true,
        textStreamEnabled: false,
        voiceOutputEnabled: true,
      ).buildBindingFactory(),
      isNull,
    );
    expect(
      runtime(
        enabled: true,
        textStreamEnabled: true,
        voiceOutputEnabled: false,
      ).buildBindingFactory(),
      isNull,
    );
    expect(
      runtime(
        enabled: true,
        textStreamEnabled: true,
        voiceOutputEnabled: true,
        supportedPlatform: false,
      ).buildBindingFactory(),
      isNull,
    );
    expect(
      runtime(
        enabled: true,
        textStreamEnabled: true,
        voiceOutputEnabled: true,
        baseUrl: 'file:///private/path',
      ).buildBindingFactory(),
      isNull,
    );
    expect(
      runtime(
        enabled: true,
        textStreamEnabled: true,
        voiceOutputEnabled: true,
        baseUrl: 'https://backend.test/path',
      ).buildBindingFactory(),
      isNull,
    );
    expect(
      runtime(
        enabled: true,
        textStreamEnabled: true,
        voiceOutputEnabled: true,
        baseUrl: 'https://backend.test?private=query',
      ).buildBindingFactory(),
      isNull,
    );

    final factory = runtime(
      enabled: true,
      textStreamEnabled: true,
      voiceOutputEnabled: true,
    ).buildBindingFactory();
    expect(factory, isNotNull);
    expect(builderCalls, 0);
    expect(fixture.engine.startCalls, 0);
    expect(fixture.synthesisCalls, 0);
    expect(fixture.playbackCalls, 0);

    expect(factory!.call(), same(fixture.binding));
    expect(builderCalls, 1);

    await fixture.binding.close();
  });

  testWidgets('default main app keeps integrated wiring unconfigured', (
    tester,
  ) async {
    await tester.pumpWidget(
      DailyRhythmCompanionApp(
        apiClient: const _FakeBackendApiClient(),
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

  testWidgets('main builds one default-off binding with no side effects', (
    tester,
  ) async {
    final fixture = _MainBindingFixture();
    var factoryCalls = 0;

    await tester.pumpWidget(
      DailyRhythmCompanionApp(
        apiClient: const _FakeBackendApiClient(),
        integratedVoiceTurnBindingFactory: () {
          factoryCalls += 1;
          return fixture.binding;
        },
      ),
    );
    await tester.pumpAndSettle();

    expect(factoryCalls, 1);
    expect(find.text('Integrated configuration: configured'), findsOne);
    expect(find.text('Integrated opt-in: off'), findsOne);
    expect(fixture.engine.startCalls, 0);
    expect(fixture.source.armCalls, 0);
    expect(fixture.synthesisCalls, 0);
    expect(fixture.playbackCalls, 0);

    await tester.pumpWidget(const MaterialApp(home: SizedBox.shrink()));
    await tester.pumpAndSettle();

    expect(fixture.disposeOwnedCalls, 1);
    expect(fixture.engine.disposeCalls, 1);
  });
}

class _MainBindingFixture {
  _MainBindingFixture() {
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
    source = _MainSpeechActivitySource();
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
      stageCapture: (_) async => throw StateError('must not stage'),
      streamControllerFactory: () => throw StateError('must not stream'),
      transcriptHandoffFactory: (_) =>
          throw StateError('must not acquire transcript'),
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
  late final _MainSpeechActivitySource source;
  late final VoiceOutputQueueController queue;
  late final RealtimeTerminalVoiceOutputOrchestrator voiceOutput;
  late final IntegratedVoiceTurnHomeScreenBinding binding;
  int synthesisCalls = 0;
  int playbackCalls = 0;
  int disposeOwnedCalls = 0;
}

class _MainSpeechActivitySource extends SpeechActivitySource {
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
  const _FakeBackendApiClient({super.baseUrl = 'https://backend.test'});

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
