import 'dart:async';

import 'package:app/services/integrated_voice_turn_coordinator.dart';
import 'package:app/services/integrated_voice_turn_home_screen_binding.dart';
import 'package:app/services/microphone_capture.dart';
import 'package:app/services/microphone_capture_host_audio_handoff.dart';
import 'package:app/services/microphone_permission.dart';
import 'package:app/services/realtime_terminal_voice_output_orchestrator.dart';
import 'package:app/services/speech_activity_source.dart';
import 'package:app/services/voice_output_queue.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  group('IntegratedVoiceTurnHomeScreenBinding', () {
    test('session opt-in defaults off and toggle alone has no execution', () async {
      final fixture = _BindingFixture();

      expect(fixture.binding.state.optedIn, isFalse);
      expect(fixture.binding.canStartVoiceTurn, isFalse);
      fixture.binding.setOptIn(true);
      await _drainMicrotasks();

      expect(fixture.binding.state.optedIn, isTrue);
      expect(fixture.engine.startCalls, 0);
      expect(fixture.source.armCalls, 0);
      expect(fixture.stagingCalls, 0);
      expect(fixture.synthesisCalls, 0);
      expect(fixture.playbackCalls, 0);
      await fixture.close();
    });

    test('speech source stays disarmed during capture and arms after stop', () async {
      final fixture = _BindingFixture();
      fixture.binding.setOptIn(true);

      final turnFuture = fixture.binding.startVoiceTurn();
      await _waitFor(() => fixture.engine.startCalls == 1);

      expect(
        fixture.binding.coordinator.state.phase,
        IntegratedVoiceTurnPhase.capturing,
      );
      expect(fixture.source.armCalls, 0);
      expect(fixture.binding.canStopCapture, isTrue);

      final stopResult = await fixture.binding.stopCapture();
      expect(stopResult?.isCompleted, isTrue);
      await _waitFor(() => fixture.source.armCalls == 1);

      expect(
        fixture.binding.coordinator.state.phase,
        IntegratedVoiceTurnPhase.staging,
      );
      expect(fixture.source.lastArmingGeneration, 1);
      expect(fixture.source.state.isActive, isTrue);

      fixture.staging.complete(_rejectedStaging());
      expect(
        (await turnFuture)?.outcome,
        IntegratedVoiceTurnOutcome.stagingRejected,
      );
      await _waitFor(() => fixture.source.disarmCalls > 0);
      await fixture.close();
    });

    test('source operations serialize across capture-to-staging transition', () async {
      final fixture = _BindingFixture();
      await _drainMicrotasks();
      fixture.binding.setOptIn(true);
      await _drainMicrotasks();

      final delayedDisarm = Completer<void>();
      final initialDisarmCalls = fixture.source.disarmCalls;
      fixture.source.nextDisarmBarrier = delayedDisarm;
      final turnFuture = fixture.binding.startVoiceTurn();
      await _waitFor(() => fixture.engine.startCalls == 1);
      await _waitFor(
        () => fixture.source.disarmCalls > initialDisarmCalls,
      );

      await fixture.binding.stopCapture();
      await _drainMicrotasks();
      expect(fixture.source.armCalls, 0);

      delayedDisarm.complete();
      await _waitFor(() => fixture.source.armCalls == 1);
      expect(fixture.source.state.isActive, isTrue);

      fixture.staging.complete(_rejectedStaging());
      await turnFuture;
      await fixture.close();
    });

    test('opt-out disarms activity and cancels an active capture', () async {
      final fixture = _BindingFixture();
      fixture.binding.setOptIn(true);
      final turnFuture = fixture.binding.startVoiceTurn();
      await _waitFor(() => fixture.engine.startCalls == 1);

      fixture.binding.setOptIn(false);
      await _waitFor(() => fixture.engine.cancelCalls == 1);

      expect(fixture.binding.state.optedIn, isFalse);
      expect(fixture.source.disarmCalls, greaterThanOrEqualTo(1));
      expect(
        (await turnFuture)?.outcome,
        IntegratedVoiceTurnOutcome.captureRejected,
      );
      await fixture.close();
    });

    test('background transition disarms active source', () async {
      final fixture = _BindingFixture();
      fixture.binding.setOptIn(true);
      final turnFuture = fixture.binding.startVoiceTurn();
      await _waitFor(() => fixture.engine.startCalls == 1);
      await fixture.binding.stopCapture();
      await _waitFor(() => fixture.source.armCalls == 1);

      await fixture.binding.setForeground(false);

      expect(fixture.binding.state.foreground, isFalse);
      expect(fixture.source.foregroundValues.last, isFalse);
      expect(fixture.source.disarmCalls, greaterThanOrEqualTo(1));

      fixture.staging.complete(_rejectedStaging());
      await turnFuture;
      await fixture.close();
    });

    test('foreground return never rearms an already active turn', () async {
      final fixture = _BindingFixture();
      fixture.binding.setOptIn(true);
      final turnFuture = fixture.binding.startVoiceTurn();
      await _waitFor(() => fixture.engine.startCalls == 1);
      await fixture.binding.stopCapture();
      await _waitFor(() => fixture.source.armCalls == 1);

      await fixture.binding.setForeground(false);
      await fixture.binding.setForeground(true);
      await _drainMicrotasks();

      expect(fixture.binding.state.optedIn, isTrue);
      expect(fixture.source.armCalls, 1);
      expect(fixture.source.state.isActive, isFalse);

      fixture.staging.complete(_rejectedStaging());
      await turnFuture;
      await fixture.close();
    });

    test('confirmed foreground event is forwarded once and invalidates turn', () async {
      final fixture = _BindingFixture();
      fixture.binding.setOptIn(true);
      final turnFuture = fixture.binding.startVoiceTurn();
      await _waitFor(() => fixture.engine.startCalls == 1);
      await fixture.binding.stopCapture();
      await _waitFor(() => fixture.source.armCalls == 1);

      await fixture.source.emit(
        const SpeechActivityEvent(
          eventId: 'speech-binding-1',
          confirmed: true,
          foreground: true,
        ),
      );
      await _waitFor(
        () =>
            fixture.binding.coordinator.state.lastSpeechOutcome ==
            IntegratedVoiceTurnSpeechOutcome.interrupted,
      );
      fixture.staging.complete(_rejectedStaging());

      expect(
        (await turnFuture)?.outcome,
        IntegratedVoiceTurnOutcome.invalidated,
      );
      expect(
        fixture.binding.coordinator.state.interruptionCount,
        1,
      );
      expect(fixture.localStopCalls, 1);
      expect(fixture.source.disarmCalls, greaterThanOrEqualTo(1));
      await fixture.close();
    });

    test('close is idempotent and owns all dedicated resources', () async {
      final fixture = _BindingFixture();

      await fixture.binding.close();
      await fixture.binding.close();

      expect(fixture.source.closeCalls, 1);
      expect(fixture.engine.disposeCalls, 1);
      expect(fixture.disposeOwnedCalls, 1);
      expect(
        fixture.binding.state.actionOutcome,
        IntegratedVoiceTurnHomeScreenActionOutcome.disposed,
      );
    });
  });
}

class _BindingFixture {
  _BindingFixture() {
    engine = FakeMicrophoneCaptureEngine();
    captureController = MicrophoneCaptureController(
      permissionGateway: FakeMicrophonePermissionGateway(
        initialStatus: MicrophonePermissionStatus.granted,
      ),
      engine: engine,
      maximumAllowedDuration: integratedVoiceTurnCaptureMaximumDuration,
    );
    captureSession = IntegratedVoiceTurnCaptureSession(
      controller: captureController,
    );
    source = _FakeSpeechActivitySource();
    queue = VoiceOutputQueueController(
      stopLocalPlayback: () async {
        localStopCalls += 1;
      },
    );
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
    coordinator = IntegratedVoiceTurnCoordinator(
      captureCompleted: captureSession.captureCompleted,
      stageCapture: (_) {
        stagingCalls += 1;
        return staging.future;
      },
      streamControllerFactory: () =>
          throw StateError('stream factory must remain unexecuted'),
      transcriptHandoffFactory: (_) =>
          throw StateError('transcript factory must remain unexecuted'),
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
  late final MicrophoneCaptureController captureController;
  late final IntegratedVoiceTurnCaptureSession captureSession;
  late final _FakeSpeechActivitySource source;
  late final VoiceOutputQueueController queue;
  late final RealtimeTerminalVoiceOutputOrchestrator voiceOutput;
  late final IntegratedVoiceTurnCoordinator coordinator;
  late final IntegratedVoiceTurnHomeScreenBinding binding;
  final Completer<HostAudioHandoffResult> staging =
      Completer<HostAudioHandoffResult>();

  int stagingCalls = 0;
  int synthesisCalls = 0;
  int playbackCalls = 0;
  int localStopCalls = 0;
  int disposeOwnedCalls = 0;

  Future<void> close() => binding.close();
}

class _FakeSpeechActivitySource extends SpeechActivitySource {
  SpeechActivitySourceState _state =
      const SpeechActivitySourceState.idle();
  SpeechActivityEventHandler? _handler;
  int armCalls = 0;
  int disarmCalls = 0;
  int closeCalls = 0;
  int? lastArmingGeneration;
  Completer<void>? nextDisarmBarrier;
  final List<bool> foregroundValues = <bool>[];

  @override
  SpeechActivitySourceState get state => _state;

  @override
  void setEventHandler(SpeechActivityEventHandler? handler) {
    _handler = handler;
  }

  @override
  Future<bool> arm({required int generation, required bool foreground}) async {
    armCalls += 1;
    lastArmingGeneration = generation;
    _state = SpeechActivitySourceState(
      phase: SpeechActivitySourcePhase.armed,
      armingGeneration: generation,
      emittedEventCount: _state.emittedEventCount,
      foreground: foreground,
    );
    notifyListeners();
    return true;
  }

  @override
  Future<void> setForeground(bool foreground) async {
    foregroundValues.add(foreground);
    _state = SpeechActivitySourceState(
      phase: _state.phase,
      armingGeneration: _state.armingGeneration,
      emittedEventCount: _state.emittedEventCount,
      foreground: foreground,
      technicalCode: _state.technicalCode,
    );
    notifyListeners();
  }

  @override
  Future<void> disarm() async {
    disarmCalls += 1;
    final barrier = nextDisarmBarrier;
    nextDisarmBarrier = null;
    await barrier?.future;
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

  Future<void> emit(SpeechActivityEvent event) async {
    final handler = _handler;
    if (handler != null) {
      await Future<void>.sync(() => handler(event));
    }
  }

  @override
  Future<void> close() async {
    closeCalls += 1;
    _handler = null;
    _state = SpeechActivitySourceState(
      phase: SpeechActivitySourcePhase.disposed,
      armingGeneration: _state.armingGeneration,
      emittedEventCount: _state.emittedEventCount,
      foreground: false,
    );
  }
}

HostAudioHandoffResult _rejectedStaging() {
  return HostAudioHandoffResult(
    outcome: HostAudioHandoffOutcome.failed,
    technicalCode: 'test_staging_rejected',
    safeMessage: 'staging rejected',
    privateArtifactDiscarded: true,
    cleanupSucceeded: true,
  );
}

Future<void> _waitFor(bool Function() predicate) async {
  for (var index = 0; index < 100; index += 1) {
    if (predicate()) {
      return;
    }
    await Future<void>.delayed(Duration.zero);
  }
  fail('condition not reached');
}

Future<void> _drainMicrotasks() async {
  await Future<void>.delayed(Duration.zero);
  await Future<void>.delayed(Duration.zero);
}
