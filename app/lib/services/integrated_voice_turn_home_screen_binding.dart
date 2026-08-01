import 'dart:async';

import 'package:flutter/widgets.dart';

import 'integrated_voice_turn_coordinator.dart';
import 'microphone_capture.dart';
import 'speech_activity_source.dart';

const Duration integratedVoiceTurnCaptureMaximumDuration = Duration(
  seconds: 15,
);

typedef IntegratedVoiceTurnHomeScreenBindingFactory =
    IntegratedVoiceTurnHomeScreenBinding Function();
typedef IntegratedVoiceTurnOwnedResourcesDisposer = FutureOr<void> Function();

enum IntegratedVoiceTurnHomeScreenActionOutcome {
  idle,
  optedIn,
  optedOut,
  started,
  captureStopped,
  completed,
  rejected,
  failed,
  disposed,
}

@immutable
class IntegratedVoiceTurnHomeScreenState {
  const IntegratedVoiceTurnHomeScreenState({
    required this.optedIn,
    required this.foreground,
    required this.actionOutcome,
  });

  const IntegratedVoiceTurnHomeScreenState.initial({
    required bool foreground,
  }) : this(
         optedIn: false,
         foreground: foreground,
         actionOutcome: IntegratedVoiceTurnHomeScreenActionOutcome.idle,
       );

  final bool optedIn;
  final bool foreground;
  final IntegratedVoiceTurnHomeScreenActionOutcome actionOutcome;
}

/// Bridges one explicit HomeScreen start/stop action to the existing bounded
/// microphone controller without exposing capture identity or private paths.
class IntegratedVoiceTurnCaptureSession {
  IntegratedVoiceTurnCaptureSession({
    required MicrophoneCaptureController controller,
    this.maximumDuration = integratedVoiceTurnCaptureMaximumDuration,
  }) : _controller = controller {
    _controller.addListener(_handleControllerChanged);
  }

  final MicrophoneCaptureController _controller;
  final Duration maximumDuration;

  Completer<MicrophoneCaptureResult>? _completion;
  bool _closed = false;

  MicrophoneCaptureState get state => _controller.state;
  bool get isActive => _completion != null || _controller.state.isActive;
  bool get canStop => _controller.state.canStop && _completion != null;

  Future<MicrophoneCaptureResult> captureCompleted() async {
    if (_closed) {
      return _failure(
        MicrophoneCaptureOutcome.failed,
        'integrated_capture_session_closed',
      );
    }
    if (_completion != null || _controller.state.isActive) {
      return _failure(
        MicrophoneCaptureOutcome.busy,
        'integrated_capture_session_busy',
      );
    }

    final started = await _controller.start(
      MicrophoneCaptureRequest(
        maxDuration: maximumDuration,
        publicMetadata: const <String, Object?>{
          'capture_owner': 'drc_integrated_voice_turn',
          'host_app': 'daily_rhythm_companion',
          'input_mode': 'microphone',
          'private_artifact_cleanup_required': true,
          'raw_audio_exposed': false,
        },
      ),
    );
    if (!started.isStarted || _closed) {
      if (_closed && _controller.state.isActive) {
        await _controller.cancel();
      }
      return started;
    }

    final completion = Completer<MicrophoneCaptureResult>();
    _completion = completion;
    _completeFromControllerIfTerminal();
    return completion.future;
  }

  Future<MicrophoneCaptureResult> stop() async {
    if (_closed || _completion == null || !_controller.state.canStop) {
      return _failure(
        MicrophoneCaptureOutcome.noActiveCapture,
        'integrated_capture_not_active',
      );
    }
    final result = await _controller.stop();
    _complete(result);
    return result;
  }

  Future<MicrophoneCaptureResult> cancel() async {
    if (_closed || _completion == null) {
      return _failure(
        MicrophoneCaptureOutcome.noActiveCapture,
        'integrated_capture_not_active',
      );
    }
    final result = await _controller.cancel();
    _complete(result);
    return result;
  }

  void _handleControllerChanged() {
    _completeFromControllerIfTerminal();
  }

  void _completeFromControllerIfTerminal() {
    final result = _controller.state.lastResult;
    if (result != null && result.isTerminal) {
      _complete(result);
    }
  }

  void _complete(MicrophoneCaptureResult result) {
    final completion = _completion;
    if (completion == null || completion.isCompleted) {
      return;
    }
    _completion = null;
    completion.complete(result);
  }

  MicrophoneCaptureResult _failure(
    MicrophoneCaptureOutcome outcome,
    String technicalCode,
  ) {
    return MicrophoneCaptureResult(
      outcome: outcome,
      safeMessage: 'The bounded voice capture could not continue safely.',
      technicalCode: technicalCode,
      publicMetadata: const <String, Object?>{
        'raw_audio_exposed': false,
      },
    );
  }

  Future<void> close() async {
    if (_closed) {
      return;
    }
    _closed = true;
    _controller.removeListener(_handleControllerChanged);
    if (_controller.state.isActive) {
      final result = await _controller.cancel();
      _complete(result);
    }
    final completion = _completion;
    _completion = null;
    if (completion != null && !completion.isCompleted) {
      completion.complete(
        _failure(
          MicrophoneCaptureOutcome.cancelled,
          'integrated_capture_session_closed',
        ),
      );
    }
    await _controller.close();
  }
}

/// HomeScreen-owned RT-5f3 session-local lifecycle and metadata binding.
///
/// The binding owns one dedicated coordinator dependency graph. It never shares
/// a stream controller, TTS queue, orchestrator, or local player with the
/// existing manual RT-4f4 / RT-5e controls.
class IntegratedVoiceTurnHomeScreenBinding extends ChangeNotifier
    with WidgetsBindingObserver {
  IntegratedVoiceTurnHomeScreenBinding({
    required this.coordinator,
    required this.captureSession,
    required this.speechActivitySource,
    IntegratedVoiceTurnOwnedResourcesDisposer? disposeOwnedResources,
    bool observeApplicationLifecycle = true,
    bool? initialForeground,
  }) : _disposeOwnedResources = disposeOwnedResources,
       _observeApplicationLifecycle = observeApplicationLifecycle,
       _state = IntegratedVoiceTurnHomeScreenState.initial(
         foreground:
             initialForeground ??
             (WidgetsBinding.instance.lifecycleState == null ||
                 WidgetsBinding.instance.lifecycleState ==
                     AppLifecycleState.resumed),
       ) {
    coordinator.addListener(_handleCoordinatorChanged);
    speechActivitySource.addListener(_handleSpeechActivitySourceChanged);
    speechActivitySource.setEventHandler(_handleSpeechActivity);
    if (_observeApplicationLifecycle) {
      WidgetsBinding.instance.addObserver(this);
    }
    unawaited(_initializeSpeechActivitySource());
  }

  final IntegratedVoiceTurnCoordinator coordinator;
  final IntegratedVoiceTurnCaptureSession captureSession;
  final SpeechActivitySource speechActivitySource;
  final IntegratedVoiceTurnOwnedResourcesDisposer? _disposeOwnedResources;
  final bool _observeApplicationLifecycle;

  IntegratedVoiceTurnHomeScreenState _state;
  int _speechSyncSequence = 0;
  int _authorizedTurnGeneration = 0;
  Future<void> _speechActivityTail = Future<void>.value();
  bool _handlingSpeechEvent = false;
  bool _closed = false;

  IntegratedVoiceTurnHomeScreenState get state => _state;

  bool get canToggleOptIn => !_closed;

  bool get canStartVoiceTurn =>
      !_closed &&
      _state.optedIn &&
      _state.foreground &&
      !coordinator.state.isBusy &&
      !captureSession.isActive &&
      !coordinator.state.localStopRetryRequired;

  bool get canStopCapture =>
      !_closed && _state.optedIn && captureSession.canStop;

  void setOptIn(bool value) {
    if (_closed || value == _state.optedIn || !canToggleOptIn) {
      return;
    }
    _setState(
      IntegratedVoiceTurnHomeScreenState(
        optedIn: value,
        foreground: _state.foreground,
        actionOutcome: value
            ? IntegratedVoiceTurnHomeScreenActionOutcome.optedIn
            : IntegratedVoiceTurnHomeScreenActionOutcome.optedOut,
      ),
    );
    if (!value) {
      _authorizedTurnGeneration = 0;
      unawaited(_handleOptOut());
    } else {
      _scheduleSpeechActivitySync();
    }
  }

  Future<void> _handleOptOut() async {
    ++_speechSyncSequence;
    await _enqueueSpeechActivityOperation(speechActivitySource.disarm);
    if (captureSession.isActive) {
      await captureSession.cancel();
    }
    _scheduleSpeechActivitySync();
  }

  Future<IntegratedVoiceTurnResult?> startVoiceTurn() async {
    if (!canStartVoiceTurn) {
      _setActionOutcome(IntegratedVoiceTurnHomeScreenActionOutcome.rejected);
      return null;
    }

    _authorizedTurnGeneration = coordinator.state.turnGeneration + 1;
    _setActionOutcome(IntegratedVoiceTurnHomeScreenActionOutcome.started);
    final result = await coordinator.startNextTurn();
    if (_closed) {
      return result;
    }
    _authorizedTurnGeneration = 0;
    _setActionOutcome(
      result.outcome == IntegratedVoiceTurnOutcome.completed
          ? IntegratedVoiceTurnHomeScreenActionOutcome.completed
          : result.outcome == IntegratedVoiceTurnOutcome.disposed
          ? IntegratedVoiceTurnHomeScreenActionOutcome.disposed
          : IntegratedVoiceTurnHomeScreenActionOutcome.failed,
    );
    _scheduleSpeechActivitySync();
    return result;
  }

  Future<MicrophoneCaptureResult?> stopCapture() async {
    if (!canStopCapture) {
      _setActionOutcome(IntegratedVoiceTurnHomeScreenActionOutcome.rejected);
      return null;
    }
    final result = await captureSession.stop();
    if (!_closed) {
      _setActionOutcome(
        result.isCompleted
            ? IntegratedVoiceTurnHomeScreenActionOutcome.captureStopped
            : IntegratedVoiceTurnHomeScreenActionOutcome.failed,
      );
    }
    return result;
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    unawaited(setForeground(state == AppLifecycleState.resumed));
  }

  Future<void> setForeground(bool foreground) async {
    if (_closed || foreground == _state.foreground) {
      return;
    }
    if (!foreground) {
      _authorizedTurnGeneration = 0;
    }
    _setState(
      IntegratedVoiceTurnHomeScreenState(
        optedIn: _state.optedIn,
        foreground: foreground,
        actionOutcome: _state.actionOutcome,
      ),
    );

    ++_speechSyncSequence;
    await _enqueueSpeechActivityOperation(
      () => speechActivitySource.setForeground(foreground),
    );
    if (!foreground && captureSession.isActive) {
      await captureSession.cancel();
    }
    _scheduleSpeechActivitySync();
  }

  void _handleCoordinatorChanged() {
    if (_closed) {
      return;
    }
    notifyListeners();
    _scheduleSpeechActivitySync();
  }

  void _handleSpeechActivitySourceChanged() {
    if (!_closed) {
      notifyListeners();
    }
  }

  Future<void> _handleSpeechActivity(SpeechActivityEvent event) async {
    if (_closed ||
        !_state.optedIn ||
        !_state.foreground ||
        !event.confirmed ||
        !event.foreground ||
        _handlingSpeechEvent) {
      return;
    }

    _handlingSpeechEvent = true;
    _authorizedTurnGeneration = 0;
    ++_speechSyncSequence;
    await _enqueueSpeechActivityOperation(speechActivitySource.disarm);
    try {
      await coordinator.handleSpeechActivity(
        IntegratedVoiceTurnSpeechActivity(
          eventId: event.eventId,
          confirmed: true,
          foreground: true,
        ),
      );
    } finally {
      _handlingSpeechEvent = false;
      _scheduleSpeechActivitySync();
    }
  }

  Future<void> _initializeSpeechActivitySource() async {
    await _enqueueSpeechActivityOperation(
      () => speechActivitySource.setForeground(_state.foreground),
    );
    _scheduleSpeechActivitySync();
  }

  Future<void> _enqueueSpeechActivityOperation(
    Future<void> Function() action,
  ) {
    final previous = _speechActivityTail;
    final next = () async {
      try {
        await previous;
      } catch (_) {
        // A later bounded source operation must still be allowed to clean up.
      }
      await action();
    }();
    _speechActivityTail = next;
    return next;
  }

  void _scheduleSpeechActivitySync() {
    if (_closed) {
      return;
    }
    final operation = ++_speechSyncSequence;
    final next = _enqueueSpeechActivityOperation(() async {
      if (_closed || operation != _speechSyncSequence) {
        return;
      }
      try {
        await _syncSpeechActivity(operation);
      } catch (_) {
        // Production source failures remain metadata-only on source.state.
      }
    });
    unawaited(next);
  }

  Future<void> _syncSpeechActivity(int operation) async {
    if (_closed || operation != _speechSyncSequence) {
      return;
    }
    final coordinatorState = coordinator.state;
    final shouldArm =
        !_handlingSpeechEvent &&
        _state.optedIn &&
        _state.foreground &&
        _authorizedTurnGeneration > 0 &&
        coordinatorState.turnGeneration == _authorizedTurnGeneration &&
        _phaseArmsSpeechActivity(coordinatorState.phase);

    if (!shouldArm) {
      await speechActivitySource.disarm();
      return;
    }

    if (speechActivitySource.state.isActive &&
        speechActivitySource.state.armingGeneration ==
            coordinatorState.turnGeneration) {
      return;
    }

    if (speechActivitySource.state.isActive) {
      await speechActivitySource.disarm();
    }
    if (_closed || operation != _speechSyncSequence) {
      return;
    }

    await speechActivitySource.arm(
      generation: coordinatorState.turnGeneration,
      foreground: true,
    );
  }

  bool _phaseArmsSpeechActivity(IntegratedVoiceTurnPhase phase) {
    return phase == IntegratedVoiceTurnPhase.staging ||
        phase == IntegratedVoiceTurnPhase.acquiringTranscript ||
        phase == IntegratedVoiceTurnPhase.streaming ||
        phase == IntegratedVoiceTurnPhase.voiceOutput;
  }

  void _setActionOutcome(IntegratedVoiceTurnHomeScreenActionOutcome outcome) {
    _setState(
      IntegratedVoiceTurnHomeScreenState(
        optedIn: _state.optedIn,
        foreground: _state.foreground,
        actionOutcome: outcome,
      ),
    );
  }

  void _setState(IntegratedVoiceTurnHomeScreenState state) {
    if (_closed) {
      return;
    }
    _state = state;
    notifyListeners();
  }

  Future<void> close() async {
    if (_closed) {
      return;
    }
    _closed = true;
    _authorizedTurnGeneration = 0;
    ++_speechSyncSequence;
    if (_observeApplicationLifecycle) {
      WidgetsBinding.instance.removeObserver(this);
    }
    coordinator.removeListener(_handleCoordinatorChanged);
    speechActivitySource.removeListener(_handleSpeechActivitySourceChanged);
    speechActivitySource.setEventHandler(null);
    try {
      await _speechActivityTail;
    } catch (_) {
      // Close continues through every dedicated resource owner.
    }
    await speechActivitySource.close();
    await captureSession.close();
    coordinator.dispose();
    final disposeOwnedResources = _disposeOwnedResources;
    if (disposeOwnedResources != null) {
      await Future<void>.sync(disposeOwnedResources);
    }
    _state = IntegratedVoiceTurnHomeScreenState(
      optedIn: false,
      foreground: false,
      actionOutcome: IntegratedVoiceTurnHomeScreenActionOutcome.disposed,
    );
  }

  @override
  void dispose() {
    unawaited(close());
    super.dispose();
  }
}
