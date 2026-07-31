import 'dart:async';

import 'package:app/models/demo_status.dart';
import 'package:app/models/realtime_text_stream.dart';
import 'package:app/models/voice_output_demo.dart';
import 'package:app/services/backend_api_client.dart';
import 'package:app/services/configured_realtime_terminal_voice_output_runtime.dart';
import 'package:app/services/realtime_terminal_voice_output_orchestrator.dart';
import 'package:app/services/realtime_text_stream_controller.dart';
import 'package:app/services/voice_output_audio_player.dart';
import 'package:flutter_test/flutter_test.dart';

const String _opaqueAudioPath =
    '/demo/voice-output/audio/0123456789abcdef0123456789abcdef';

void main() {
  group('ConfiguredRealtimeTerminalVoiceOutputRuntime', () {
    test('disabled runtime returns no binding factory', () {
      var engineFactoryCalls = 0;
      final runtime = ConfiguredRealtimeTerminalVoiceOutputRuntime(
        enabled: false,
        apiClient: _FakeBackendApiClient(response: _generatedResponse()),
        audioEngineFactory: () {
          engineFactoryCalls += 1;
          return _FakeVoiceOutputAudioEngine();
        },
      );

      expect(runtime.buildBindingFactory(), isNull);
      expect(engineFactoryCalls, 0);
    });

    test('invalid Backend base URL fails closed', () {
      final runtime = ConfiguredRealtimeTerminalVoiceOutputRuntime(
        enabled: true,
        apiClient: _FakeBackendApiClient(
          baseUrl: 'file:///private/backend',
          response: _generatedResponse(),
        ),
      );

      expect(runtime.buildBindingFactory(), isNull);
    });

    test('binding construction starts no synthesis or playback', () async {
      final backend = _FakeBackendApiClient(response: _generatedResponse());
      final engine = _FakeVoiceOutputAudioEngine();
      final runtime = ConfiguredRealtimeTerminalVoiceOutputRuntime(
        enabled: true,
        apiClient: backend,
        audioEngineFactory: () => engine,
      );

      final binding = runtime.buildBindingFactory()!.call();

      expect(binding.orchestrator.state.pendingCount, 0);
      expect(backend.submitCalls, 0);
      expect(engine.loadedSources, isEmpty);
      expect(engine.playCalls, 0);
      expect(engine.stopCalls, 0);

      binding.dispose();
      await Future<void>.delayed(Duration.zero);
    });

    test(
      'one explicit process uses exact Backend contract and dedicated player',
      () async {
        final backend = _FakeBackendApiClient(response: _generatedResponse());
        final engine = _FakeVoiceOutputAudioEngine();
        final runtime = ConfiguredRealtimeTerminalVoiceOutputRuntime(
          enabled: true,
          apiClient: backend,
          audioEngineFactory: () => engine,
        );
        final binding = runtime.buildBindingFactory()!.call();

        final enqueue = binding.orchestrator.enqueueCompletedTerminal(
          _completedTerminal(text: 'operator approved one shot'),
        );
        expect(enqueue.accepted, isTrue);
        expect(backend.submitCalls, 0);

        final processFuture = binding.orchestrator.processNext();
        await Future<void>.delayed(Duration.zero);

        expect(backend.submitCalls, 1);
        expect(
          backend.lastRequest?.clientEventId,
          configuredRealtimeTerminalVoiceOutputClientEventId,
        );
        expect(backend.lastRequest?.outputMode, 'tts');
        expect(backend.lastRequest?.textContent, 'operator approved one shot');
        expect(backend.lastRequest?.characterId, isNull);
        expect(backend.lastRequest?.voiceProfileId, isNull);
        expect(backend.lastRequest?.audioFormat, 'mp3');
        expect(
          backend.lastRequest?.utterancePurpose,
          configuredRealtimeTerminalVoiceOutputPurpose,
        );
        expect(engine.loadedSources, <Uri>[
          Uri.parse('https://backend.test$_opaqueAudioPath'),
        ]);
        expect(engine.playCalls, 1);

        engine.emit(
          const VoiceOutputAudioEngineEvent(
            type: VoiceOutputAudioEngineEventType.completed,
          ),
        );
        final processResult = await processFuture;

        expect(
          processResult.outcome,
          RealtimeTerminalVoiceOutputProcessOutcome.completed,
        );
        expect(binding.orchestrator.state.pendingCount, 0);
        expect(binding.orchestrator.state.activeItem, isNull);

        binding.dispose();
        await Future<void>.delayed(Duration.zero);
      },
    );

    test('wrong FW API name is rejected before local playback', () async {
      final backend = _FakeBackendApiClient(
        response: _generatedResponse(frameworkApiName: 'framework.internal'),
      );
      final engine = _FakeVoiceOutputAudioEngine();
      final binding = ConfiguredRealtimeTerminalVoiceOutputRuntime(
        enabled: true,
        apiClient: backend,
        audioEngineFactory: () => engine,
      ).buildBindingFactory()!.call();

      binding.orchestrator.enqueueCompletedTerminal(
        _completedTerminal(text: 'must not play'),
      );
      final result = await binding.orchestrator.processNext();

      expect(
        result.outcome,
        RealtimeTerminalVoiceOutputProcessOutcome.synthesisFailed,
      );
      expect(engine.loadedSources, isEmpty);
      expect(engine.playCalls, 0);

      binding.dispose();
      await Future<void>.delayed(Duration.zero);
    });

    test(
      'absolute or non-opaque audio handoff is rejected before playback',
      () async {
        final backend = _FakeBackendApiClient(
          response: _generatedResponse(
            audioUrl: 'https://provider.invalid/private.mp3',
          ),
        );
        final engine = _FakeVoiceOutputAudioEngine();
        final binding = ConfiguredRealtimeTerminalVoiceOutputRuntime(
          enabled: true,
          apiClient: backend,
          audioEngineFactory: () => engine,
        ).buildBindingFactory()!.call();

        binding.orchestrator.enqueueCompletedTerminal(
          _completedTerminal(text: 'reject provider URL'),
        );
        final result = await binding.orchestrator.processNext();

        expect(
          result.outcome,
          RealtimeTerminalVoiceOutputProcessOutcome.synthesisFailed,
        );
        expect(engine.loadedSources, isEmpty);

        binding.dispose();
        await Future<void>.delayed(Duration.zero);
      },
    );

    test(
      'flush clears pending work and stops only the dedicated player',
      () async {
        final backend = _FakeBackendApiClient(response: _generatedResponse());
        final engine = _FakeVoiceOutputAudioEngine();
        final binding = ConfiguredRealtimeTerminalVoiceOutputRuntime(
          enabled: true,
          apiClient: backend,
          audioEngineFactory: () => engine,
        ).buildBindingFactory()!.call();

        binding.orchestrator.enqueueCompletedTerminal(
          _completedTerminal(
            text: 'first',
            sessionId: 'session-one',
            turnId: 'turn-one',
            sequence: 1,
          ),
        );
        binding.orchestrator.enqueueCompletedTerminal(
          _completedTerminal(
            text: 'second',
            sessionId: 'session-two',
            turnId: 'turn-two',
            sequence: 2,
          ),
        );

        final processFuture = binding.orchestrator.processNext();
        await Future<void>.delayed(Duration.zero);
        expect(engine.playCalls, 1);
        expect(binding.orchestrator.state.pendingCount, 1);

        final flushResult = await binding.orchestrator.flush();
        final processResult = await processFuture;

        expect(flushResult.clearedPendingCount, 1);
        expect(flushResult.localPlaybackStopRequested, isTrue);
        expect(flushResult.localPlaybackStopSucceeded, isTrue);
        expect(engine.stopCalls, 1);
        expect(
          processResult.outcome,
          RealtimeTerminalVoiceOutputProcessOutcome.invalidated,
        );
        expect(binding.orchestrator.state.pendingCount, 0);
        expect(binding.orchestrator.state.activeItem, isNull);
        expect(backend.submitCalls, 1);

        binding.dispose();
        await Future<void>.delayed(Duration.zero);
      },
    );

    test(
      'binding dispose is idempotent and disposes its dedicated engine once',
      () async {
        final engine = _FakeVoiceOutputAudioEngine();
        final binding = ConfiguredRealtimeTerminalVoiceOutputRuntime(
          enabled: true,
          apiClient: _FakeBackendApiClient(response: _generatedResponse()),
          audioEngineFactory: () => engine,
        ).buildBindingFactory()!.call();

        binding.dispose();
        binding.dispose();
        await Future<void>.delayed(Duration.zero);

        expect(engine.disposeCalls, 1);
      },
    );
  });
}

VoiceOutputDemoRequestResponse _generatedResponse({
  String frameworkApiName =
      configuredRealtimeTerminalVoiceOutputFrameworkApiName,
  String audioUrl = _opaqueAudioPath,
}) {
  return VoiceOutputDemoRequestResponse(
    accepted: true,
    requestState: 'generated',
    engine: 'framework',
    mode: 'framework_local',
    adapterMode: 'framework',
    realTtsEnabled: true,
    outputMode: 'tts',
    capability: const DemoCapabilityStatus(
      status: 'available',
      source: 'framework_voice_output_runtime_enabled',
      message: 'available',
    ),
    message: 'generated',
    frameworkCallState: 'generated',
    audioPlaybackStatus: 'not_started',
    evidenceStatus: 'not_evidence',
    frameworkApiName: frameworkApiName,
    audioUrl: audioUrl,
    audioArtifactRef: null,
    audioFormat: 'mp3',
    audioReady: true,
    audioHandoffKind: 'url',
    hasAudioHandoff: true,
    isGenerated: true,
  );
}

RealtimeTextStreamControllerState _completedTerminal({
  required String text,
  String sessionId = 'session-one',
  String turnId = 'turn-one',
  int sequence = 1,
}) {
  return RealtimeTextStreamControllerState(
    phase: RealtimeTextStreamControllerPhase.completed,
    outputText: text,
    lastSequence: sequence,
    cancelMode: 'cooperative',
    hardCancelSupported: false,
    createResponse: RealtimeTextStreamCreateResponse(
      accepted: true,
      session: RealtimeTextStreamSession(
        sessionId: sessionId,
        state: RealtimeTextStreamState.streaming,
        activeTurnId: turnId,
        lastSequence: 0,
        isClosed: false,
        cancelMode: 'cooperative',
        hardCancelSupported: false,
      ),
      turn: RealtimeTextStreamTurn(
        sessionId: sessionId,
        turnId: turnId,
        state: RealtimeTextStreamState.streaming,
        chunkCount: 1,
        outputCharCount: text.runes.length,
        cancelRequested: false,
        terminalOutcome: null,
      ),
      eventsPath: '/realtime/text/sessions/$sessionId/events',
      cancelPath: '/realtime/text/sessions/$sessionId/cancel',
      idleTtlSeconds: 30,
      maxDurationSeconds: 120,
      maxPendingEvents: 64,
      maxEventBytes: 32768,
    ),
    terminal: RealtimeTextStreamTerminal(
      sequence: sequence,
      outcome: RealtimeTextStreamTerminalOutcome.completed,
      finalText: text,
      outputCharCount: text.runes.length,
      publicErrorCode: null,
      safeMessage: '',
      retryable: false,
    ),
  );
}

class _VoiceOutputRequestCapture {
  const _VoiceOutputRequestCapture({
    required this.clientEventId,
    required this.outputMode,
    required this.textContent,
    required this.characterId,
    required this.voiceProfileId,
    required this.audioFormat,
    required this.utterancePurpose,
  });

  final String clientEventId;
  final String outputMode;
  final String? textContent;
  final String? characterId;
  final String? voiceProfileId;
  final String? audioFormat;
  final String utterancePurpose;
}

class _FakeBackendApiClient extends BackendApiClient {
  _FakeBackendApiClient({
    required this.response,
    super.baseUrl = 'https://backend.test',
  });

  final VoiceOutputDemoRequestResponse response;
  int submitCalls = 0;
  _VoiceOutputRequestCapture? lastRequest;

  @override
  Future<VoiceOutputDemoRequestResponse> submitVoiceOutputDemoRequest({
    required String clientEventId,
    String outputMode = 'tts',
    String? textContent,
    String? characterId,
    String? voiceProfileId,
    String? audioFormat,
    String utterancePurpose = 'daily_advice',
  }) async {
    submitCalls += 1;
    lastRequest = _VoiceOutputRequestCapture(
      clientEventId: clientEventId,
      outputMode: outputMode,
      textContent: textContent,
      characterId: characterId,
      voiceProfileId: voiceProfileId,
      audioFormat: audioFormat,
      utterancePurpose: utterancePurpose,
    );
    return response;
  }
}

class _FakeVoiceOutputAudioEngine implements VoiceOutputAudioEngine {
  final StreamController<VoiceOutputAudioEngineEvent> _events =
      StreamController<VoiceOutputAudioEngineEvent>.broadcast(sync: true);

  final List<Uri> loadedSources = <Uri>[];
  int playCalls = 0;
  int stopCalls = 0;
  int disposeCalls = 0;

  @override
  Stream<VoiceOutputAudioEngineEvent> get events => _events.stream;

  void emit(VoiceOutputAudioEngineEvent event) => _events.add(event);

  @override
  Future<void> load(Uri source) async {
    loadedSources.add(source);
  }

  @override
  Future<void> play() async {
    playCalls += 1;
  }

  @override
  Future<void> stop() async {
    stopCalls += 1;
  }

  @override
  Future<void> seekToStart() async {}

  @override
  Future<void> dispose() async {
    disposeCalls += 1;
    await _events.close();
  }
}
