import 'dart:async';

import 'package:flutter/foundation.dart';

import '../models/realtime_text_stream.dart';
import 'microphone_capture.dart';
import 'microphone_capture_host_audio_handoff.dart';
import 'realtime_terminal_voice_output_orchestrator.dart';
import 'realtime_text_stream_controller.dart';
import 'realtime_text_stream_transcript_handoff.dart';
import 'voice_output_queue.dart';

const int integratedVoiceTurnMaxSpeechEventIdCodePoints = 128;
const int integratedVoiceTurnMaxRememberedSpeechEventIds = 32;
const int integratedVoiceTurnMaxTechnicalCodePoints = 128;

typedef IntegratedVoiceTurnCaptureCompletion =
    Future<MicrophoneCaptureResult> Function();
typedef IntegratedVoiceTurnStaging =
    Future<HostAudioHandoffResult> Function(
      MicrophoneCaptureResult captureResult,
    );
typedef IntegratedVoiceTurnStreamControllerFactory =
    RealtimeTextStreamController Function();
typedef IntegratedVoiceTurnTranscriptHandoffFactory =
    RealtimeTextStreamTranscriptHandoff Function(
      RealtimeTextStreamController controller,
    );

enum IntegratedVoiceTurnPhase {
  idle,
  capturing,
  staging,
  acquiringTranscript,
  streaming,
  voiceOutput,
  interrupting,
  ready,
  completed,
  failed,
  interruptionFailed,
  disposed,
}

enum IntegratedVoiceTurnOutcome {
  completed,
  captureRejected,
  stagingRejected,
  transcriptRejected,
  streamCancelled,
  streamFailed,
  streamClosed,
  terminalRejected,
  voiceOutputRejected,
  voiceOutputFailed,
  invalidated,
  busy,
  localStopRetryRequired,
  disposed,
}

enum IntegratedVoiceTurnSpeechOutcome {
  interrupted,
  coalesced,
  duplicate,
  invalid,
  noActiveWork,
  localStopFailed,
  disposed,
}

@immutable
class IntegratedVoiceTurnSpeechActivity {
  const IntegratedVoiceTurnSpeechActivity({
    required this.eventId,
    required this.confirmed,
    required this.foreground,
  });

  final String eventId;
  final bool confirmed;
  final bool foreground;
}

@immutable
class IntegratedVoiceTurnResult {
  const IntegratedVoiceTurnResult({
    required this.outcome,
    required this.technicalCode,
  });

  final IntegratedVoiceTurnOutcome outcome;
  final String technicalCode;
}

@immutable
class IntegratedVoiceTurnSpeechResult {
  const IntegratedVoiceTurnSpeechResult({
    required this.outcome,
    required this.technicalCode,
  });

  final IntegratedVoiceTurnSpeechOutcome outcome;
  final String technicalCode;
}

@immutable
class IntegratedVoiceTurnState {
  const IntegratedVoiceTurnState({
    required this.phase,
    required this.operationEpoch,
    required this.turnGeneration,
    required this.interruptionCount,
    required this.pendingVoiceOutputCount,
    required this.localStopRetryRequired,
    required this.lastTurnOutcome,
    required this.lastSpeechOutcome,
    required this.safeMessage,
    required this.technicalCode,
  });

  const IntegratedVoiceTurnState.idle()
    : this(
        phase: IntegratedVoiceTurnPhase.idle,
        operationEpoch: 0,
        turnGeneration: 0,
        interruptionCount: 0,
        pendingVoiceOutputCount: 0,
        localStopRetryRequired: false,
        lastTurnOutcome: null,
        lastSpeechOutcome: null,
        safeMessage: '',
        technicalCode: null,
      );

  final IntegratedVoiceTurnPhase phase;
  final int operationEpoch;
  final int turnGeneration;
  final int interruptionCount;
  final int pendingVoiceOutputCount;
  final bool localStopRetryRequired;
  final IntegratedVoiceTurnOutcome? lastTurnOutcome;
  final IntegratedVoiceTurnSpeechOutcome? lastSpeechOutcome;
  final String safeMessage;
  final String? technicalCode;

  bool get isBusy =>
      phase == IntegratedVoiceTurnPhase.capturing ||
      phase == IntegratedVoiceTurnPhase.staging ||
      phase == IntegratedVoiceTurnPhase.acquiringTranscript ||
      phase == IntegratedVoiceTurnPhase.streaming ||
      phase == IntegratedVoiceTurnPhase.voiceOutput ||
      phase == IntegratedVoiceTurnPhase.interrupting;
}

/// Fake-only RT-5f2 coordinator.
///
/// This class composes already accepted app-owned boundaries. It does not open a
/// microphone, read a private path, perform HTTP, import Framework code, execute
/// providers, play platform audio, or wire HomeScreen/main.dart.
class IntegratedVoiceTurnCoordinator extends ChangeNotifier {
  IntegratedVoiceTurnCoordinator({
    required IntegratedVoiceTurnCaptureCompletion captureCompleted,
    required IntegratedVoiceTurnStaging stageCapture,
    required IntegratedVoiceTurnStreamControllerFactory streamControllerFactory,
    required IntegratedVoiceTurnTranscriptHandoffFactory
    transcriptHandoffFactory,
    required RealtimeTerminalVoiceOutputOrchestrator voiceOutput,
    int maxRememberedSpeechEventIds =
        integratedVoiceTurnMaxRememberedSpeechEventIds,
  }) : _maxRememberedSpeechEventIds = maxRememberedSpeechEventIds <= 0
           ? 1
           : maxRememberedSpeechEventIds >
                 integratedVoiceTurnMaxRememberedSpeechEventIds
           ? integratedVoiceTurnMaxRememberedSpeechEventIds
           : maxRememberedSpeechEventIds,
       _captureCompleted = captureCompleted,
       _stageCapture = stageCapture,
       _streamControllerFactory = streamControllerFactory,
       _transcriptHandoffFactory = transcriptHandoffFactory,
       _voiceOutput = voiceOutput;

  final IntegratedVoiceTurnCaptureCompletion _captureCompleted;
  final IntegratedVoiceTurnStaging _stageCapture;
  final IntegratedVoiceTurnStreamControllerFactory _streamControllerFactory;
  final IntegratedVoiceTurnTranscriptHandoffFactory _transcriptHandoffFactory;
  final RealtimeTerminalVoiceOutputOrchestrator _voiceOutput;
  final int _maxRememberedSpeechEventIds;

  final List<String> _rememberedSpeechEventIds = <String>[];
  IntegratedVoiceTurnState _state = const IntegratedVoiceTurnState.idle();
  _IntegratedVoiceTurnOperation? _activeTurn;
  Completer<IntegratedVoiceTurnSpeechResult>? _interruptionCompleter;
  int _operationEpoch = 0;
  int _turnGeneration = 0;
  bool _isDisposed = false;

  IntegratedVoiceTurnState get state => _state;

  @visibleForTesting
  int get rememberedSpeechEventCount => _rememberedSpeechEventIds.length;

  Future<IntegratedVoiceTurnResult> startNextTurn() async {
    if (_isDisposed) {
      return const IntegratedVoiceTurnResult(
        outcome: IntegratedVoiceTurnOutcome.disposed,
        technicalCode: 'integrated_voice_turn_disposed',
      );
    }
    if (_state.localStopRetryRequired) {
      return const IntegratedVoiceTurnResult(
        outcome: IntegratedVoiceTurnOutcome.localStopRetryRequired,
        technicalCode: 'integrated_voice_turn_local_stop_retry_required',
      );
    }
    if (_activeTurn != null || _interruptionCompleter != null) {
      return const IntegratedVoiceTurnResult(
        outcome: IntegratedVoiceTurnOutcome.busy,
        technicalCode: 'integrated_voice_turn_busy',
      );
    }

    final operation = _IntegratedVoiceTurnOperation(
      token: Object(),
      epoch: ++_operationEpoch,
    );
    ++_turnGeneration;
    _activeTurn = operation;
    _setPhase(
      IntegratedVoiceTurnPhase.capturing,
      safeMessage: 'The next bounded voice turn is acquiring fake input.',
    );

    MicrophoneCaptureResult captureResult;
    try {
      captureResult = await _captureCompleted();
    } catch (_) {
      return _failCurrent(
        operation,
        IntegratedVoiceTurnOutcome.captureRejected,
        'integrated_voice_turn_capture_failed',
        'The fake capture completion could not be accepted safely.',
      );
    }
    if (!_isCurrent(operation)) {
      return _invalidatedResult();
    }
    if (!captureResult.isCompleted || captureResult.engineResult == null) {
      return _failCurrent(
        operation,
        IntegratedVoiceTurnOutcome.captureRejected,
        'integrated_voice_turn_capture_rejected',
        'A completed fake capture is required.',
      );
    }

    _setPhase(
      IntegratedVoiceTurnPhase.staging,
      safeMessage: 'The bounded fake capture is being staged.',
    );
    HostAudioHandoffResult stagingResult;
    try {
      stagingResult = await _stageCapture(captureResult);
    } catch (_) {
      return _failCurrent(
        operation,
        IntegratedVoiceTurnOutcome.stagingRejected,
        'integrated_voice_turn_staging_failed',
        'The fake staging handoff failed safely.',
      );
    }
    if (!_isCurrent(operation)) {
      return _invalidatedResult();
    }
    if (!stagingResult.isCompleted) {
      return _failCurrent(
        operation,
        IntegratedVoiceTurnOutcome.stagingRejected,
        'integrated_voice_turn_staging_rejected',
        'A completed fake staging handoff is required.',
      );
    }

    _setPhase(
      IntegratedVoiceTurnPhase.acquiringTranscript,
      safeMessage: 'A final provider-neutral transcript is being acquired.',
    );

    late final RealtimeTextStreamController controller;
    try {
      controller = _streamControllerFactory();
    } catch (_) {
      return _failCurrent(
        operation,
        IntegratedVoiceTurnOutcome.transcriptRejected,
        'integrated_voice_turn_stream_assembly_failed',
        'The fake transcript-to-stream assembly failed safely.',
      );
    }

    late final RealtimeTextStreamTranscriptHandoff handoff;
    try {
      handoff = _transcriptHandoffFactory(controller);
    } catch (_) {
      controller.dispose();
      return _failCurrent(
        operation,
        IntegratedVoiceTurnOutcome.transcriptRejected,
        'integrated_voice_turn_stream_assembly_failed',
        'The fake transcript-to-stream assembly failed safely.',
      );
    }
    operation.controller = controller;
    operation.handoff = handoff;
    operation.terminalCompleter =
        Completer<RealtimeTextStreamControllerState?>();
    _attachTerminalListener(operation);

    try {
      await handoff.startFromNextTranscript();
    } catch (_) {
      return _failCurrent(
        operation,
        IntegratedVoiceTurnOutcome.transcriptRejected,
        'integrated_voice_turn_transcript_handoff_failed',
        'The final transcript could not start the fake stream safely.',
      );
    }
    if (!_isCurrent(operation)) {
      return _invalidatedResult();
    }
    if (handoff.state.phase !=
        RealtimeTextStreamTranscriptHandoffPhase.accepted) {
      return _failCurrent(
        operation,
        IntegratedVoiceTurnOutcome.transcriptRejected,
        'integrated_voice_turn_transcript_rejected',
        'The final transcript was rejected by the fake stream handoff.',
      );
    }

    if (!controller.state.isTerminal) {
      _setPhase(
        IntegratedVoiceTurnPhase.streaming,
        safeMessage: 'The fake text stream is active.',
      );
    }

    final terminalState = await operation.terminalCompleter!.future;
    if (!_isCurrent(operation) || terminalState == null) {
      return _invalidatedResult();
    }

    switch (terminalState.phase) {
      case RealtimeTextStreamControllerPhase.completed:
        break;
      case RealtimeTextStreamControllerPhase.cancelled:
        return _failCurrent(
          operation,
          IntegratedVoiceTurnOutcome.streamCancelled,
          'integrated_voice_turn_stream_cancelled',
          'The fake text stream was cancelled.',
        );
      case RealtimeTextStreamControllerPhase.failed:
        return _failCurrent(
          operation,
          IntegratedVoiceTurnOutcome.streamFailed,
          'integrated_voice_turn_stream_failed',
          'The fake text stream failed safely.',
        );
      case RealtimeTextStreamControllerPhase.closed:
        return _failCurrent(
          operation,
          IntegratedVoiceTurnOutcome.streamClosed,
          'integrated_voice_turn_stream_closed',
          'The fake text stream closed without a completed response.',
        );
      case RealtimeTextStreamControllerPhase.idle:
      case RealtimeTextStreamControllerPhase.connecting:
      case RealtimeTextStreamControllerPhase.streaming:
      case RealtimeTextStreamControllerPhase.cancelRequested:
        return _failCurrent(
          operation,
          IntegratedVoiceTurnOutcome.terminalRejected,
          'integrated_voice_turn_terminal_invalid',
          'The fake text stream terminal was inconsistent.',
        );
    }

    final terminal = terminalState.terminal;
    if (terminal == null ||
        terminal.outcome != RealtimeTextStreamTerminalOutcome.completed) {
      return _failCurrent(
        operation,
        IntegratedVoiceTurnOutcome.terminalRejected,
        'integrated_voice_turn_terminal_rejected',
        'Only a completed fake terminal can reach voice output.',
      );
    }

    _setPhase(
      IntegratedVoiceTurnPhase.voiceOutput,
      safeMessage: 'The completed fake terminal is entering voice output.',
    );
    final enqueueResult = _voiceOutput.enqueueCompletedTerminal(terminalState);
    if (!enqueueResult.accepted) {
      return _failCurrent(
        operation,
        IntegratedVoiceTurnOutcome.voiceOutputRejected,
        'integrated_voice_turn_voice_output_enqueue_rejected',
        'The completed fake terminal was rejected by voice output.',
      );
    }

    final processResult = await _voiceOutput.processNext();
    if (!_isCurrent(operation)) {
      return _invalidatedResult();
    }
    if (processResult.outcome !=
        RealtimeTerminalVoiceOutputProcessOutcome.completed) {
      return _failCurrent(
        operation,
        IntegratedVoiceTurnOutcome.voiceOutputFailed,
        'integrated_voice_turn_voice_output_failed',
        'The fake voice-output lifecycle did not complete.',
      );
    }

    return _completeCurrent(operation);
  }

  Future<IntegratedVoiceTurnSpeechResult> handleSpeechActivity(
    IntegratedVoiceTurnSpeechActivity activity,
  ) {
    if (_isDisposed) {
      return Future<IntegratedVoiceTurnSpeechResult>.value(
        const IntegratedVoiceTurnSpeechResult(
          outcome: IntegratedVoiceTurnSpeechOutcome.disposed,
          technicalCode: 'integrated_voice_turn_disposed',
        ),
      );
    }

    final rawEventId = activity.eventId;
    final eventId = rawEventId.trim();
    if (!activity.confirmed ||
        !activity.foreground ||
        rawEventId != eventId ||
        !_isValidSpeechEventId(eventId)) {
      _recordSpeechOutcome(
        IntegratedVoiceTurnSpeechOutcome.invalid,
        technicalCode: 'integrated_voice_turn_speech_event_invalid',
      );
      return Future<IntegratedVoiceTurnSpeechResult>.value(
        const IntegratedVoiceTurnSpeechResult(
          outcome: IntegratedVoiceTurnSpeechOutcome.invalid,
          technicalCode: 'integrated_voice_turn_speech_event_invalid',
        ),
      );
    }
    if (_rememberedSpeechEventIds.contains(eventId)) {
      _recordSpeechOutcome(
        IntegratedVoiceTurnSpeechOutcome.duplicate,
        technicalCode: 'integrated_voice_turn_speech_event_duplicate',
      );
      return Future<IntegratedVoiceTurnSpeechResult>.value(
        const IntegratedVoiceTurnSpeechResult(
          outcome: IntegratedVoiceTurnSpeechOutcome.duplicate,
          technicalCode: 'integrated_voice_turn_speech_event_duplicate',
        ),
      );
    }
    _rememberSpeechEventId(eventId);

    final existing = _interruptionCompleter;
    if (existing != null) {
      return existing.future.then((result) {
        if (result.outcome == IntegratedVoiceTurnSpeechOutcome.disposed) {
          return result;
        }
        return const IntegratedVoiceTurnSpeechResult(
          outcome: IntegratedVoiceTurnSpeechOutcome.coalesced,
          technicalCode: 'integrated_voice_turn_interruption_coalesced',
        );
      });
    }

    final hasInterruptibleWork =
        _activeTurn != null ||
        _voiceOutput.state.isProcessing ||
        _voiceOutput.state.pendingCount > 0 ||
        _state.localStopRetryRequired;
    if (!hasInterruptibleWork) {
      _recordSpeechOutcome(
        IntegratedVoiceTurnSpeechOutcome.noActiveWork,
        technicalCode: 'integrated_voice_turn_no_active_work',
      );
      return Future<IntegratedVoiceTurnSpeechResult>.value(
        const IntegratedVoiceTurnSpeechResult(
          outcome: IntegratedVoiceTurnSpeechOutcome.noActiveWork,
          technicalCode: 'integrated_voice_turn_no_active_work',
        ),
      );
    }

    final completer = Completer<IntegratedVoiceTurnSpeechResult>();
    _interruptionCompleter = completer;
    _beginInterruption(completer);
    return completer.future;
  }

  void _beginInterruption(
    Completer<IntegratedVoiceTurnSpeechResult> completer,
  ) {
    final operation = _activeTurn;

    // The epoch and ownership changes happen before the first await. Every old
    // completion becomes stale immediately, including STT, stream, synthesis,
    // playback, and terminal callbacks.
    ++_operationEpoch;
    _activeTurn = null;
    _detachOperation(operation, requestCooperativeCancel: true);

    _setState(
      IntegratedVoiceTurnState(
        phase: IntegratedVoiceTurnPhase.interrupting,
        operationEpoch: _operationEpoch,
        turnGeneration: _turnGeneration,
        interruptionCount: _state.interruptionCount + 1,
        pendingVoiceOutputCount: _voiceOutput.state.pendingCount,
        localStopRetryRequired: _state.localStopRetryRequired,
        lastTurnOutcome: _state.lastTurnOutcome,
        lastSpeechOutcome: null,
        safeMessage:
            'Confirmed foreground speech is invalidating old fake voice work.',
        technicalCode: null,
      ),
    );

    final flushFuture = _voiceOutput.flush();
    unawaited(_completeInterruption(flushFuture, completer));
  }

  Future<void> _completeInterruption(
    Future<VoiceOutputQueueFlushResult> flushFuture,
    Completer<IntegratedVoiceTurnSpeechResult> completer,
  ) async {
    var result = const IntegratedVoiceTurnSpeechResult(
      outcome: IntegratedVoiceTurnSpeechOutcome.localStopFailed,
      technicalCode: 'integrated_voice_turn_local_stop_failed',
    );
    try {
      final flushResult = await flushFuture;
      if (_isDisposed) {
        result = const IntegratedVoiceTurnSpeechResult(
          outcome: IntegratedVoiceTurnSpeechOutcome.disposed,
          technicalCode: 'integrated_voice_turn_disposed',
        );
      } else if (!flushResult.localPlaybackStopRequested ||
          !flushResult.localPlaybackStopSucceeded ||
          flushResult.outcome != VoiceOutputQueueFlushOutcome.completed) {
        result = const IntegratedVoiceTurnSpeechResult(
          outcome: IntegratedVoiceTurnSpeechOutcome.localStopFailed,
          technicalCode: 'integrated_voice_turn_local_stop_failed',
        );
        _setState(
          IntegratedVoiceTurnState(
            phase: IntegratedVoiceTurnPhase.interruptionFailed,
            operationEpoch: _operationEpoch,
            turnGeneration: _turnGeneration,
            interruptionCount: _state.interruptionCount,
            pendingVoiceOutputCount: _voiceOutput.state.pendingCount,
            localStopRetryRequired: true,
            lastTurnOutcome: _state.lastTurnOutcome,
            lastSpeechOutcome: IntegratedVoiceTurnSpeechOutcome.localStopFailed,
            safeMessage:
                'Local playback stop failed; another confirmed speech event is required.',
            technicalCode: 'integrated_voice_turn_local_stop_failed',
          ),
        );
      } else {
        result = const IntegratedVoiceTurnSpeechResult(
          outcome: IntegratedVoiceTurnSpeechOutcome.interrupted,
          technicalCode: 'integrated_voice_turn_interrupted',
        );
        _setState(
          IntegratedVoiceTurnState(
            phase: IntegratedVoiceTurnPhase.ready,
            operationEpoch: _operationEpoch,
            turnGeneration: _turnGeneration,
            interruptionCount: _state.interruptionCount,
            pendingVoiceOutputCount: _voiceOutput.state.pendingCount,
            localStopRetryRequired: false,
            lastTurnOutcome: _state.lastTurnOutcome,
            lastSpeechOutcome: IntegratedVoiceTurnSpeechOutcome.interrupted,
            safeMessage:
                'Old fake voice work is inert and the next turn may start.',
            technicalCode: 'integrated_voice_turn_interrupted',
          ),
        );
      }
    } catch (_) {
      result = const IntegratedVoiceTurnSpeechResult(
        outcome: IntegratedVoiceTurnSpeechOutcome.localStopFailed,
        technicalCode: 'integrated_voice_turn_local_stop_failed',
      );
      if (!_isDisposed) {
        _setState(
          IntegratedVoiceTurnState(
            phase: IntegratedVoiceTurnPhase.interruptionFailed,
            operationEpoch: _operationEpoch,
            turnGeneration: _turnGeneration,
            interruptionCount: _state.interruptionCount,
            pendingVoiceOutputCount: _voiceOutput.state.pendingCount,
            localStopRetryRequired: true,
            lastTurnOutcome: _state.lastTurnOutcome,
            lastSpeechOutcome: IntegratedVoiceTurnSpeechOutcome.localStopFailed,
            safeMessage:
                'Local playback stop failed; another confirmed speech event is required.',
            technicalCode: 'integrated_voice_turn_local_stop_failed',
          ),
        );
      }
    } finally {
      if (identical(_interruptionCompleter, completer)) {
        _interruptionCompleter = null;
      }
      if (!completer.isCompleted) {
        completer.complete(result);
      }
    }
  }

  void _attachTerminalListener(_IntegratedVoiceTurnOperation operation) {
    final controller = operation.controller!;
    void listener() {
      final completer = operation.terminalCompleter;
      if (!_isCurrent(operation) ||
          completer == null ||
          completer.isCompleted) {
        return;
      }
      if (controller.state.isTerminal) {
        completer.complete(controller.state);
      }
    }

    operation.terminalListener = listener;
    controller.addListener(listener);
    listener();
  }

  IntegratedVoiceTurnResult _completeCurrent(
    _IntegratedVoiceTurnOperation operation,
  ) {
    if (!_isCurrent(operation)) {
      return _invalidatedResult();
    }
    _activeTurn = null;
    _detachOperation(operation, requestCooperativeCancel: false);
    const result = IntegratedVoiceTurnResult(
      outcome: IntegratedVoiceTurnOutcome.completed,
      technicalCode: 'integrated_voice_turn_completed',
    );
    _setState(
      IntegratedVoiceTurnState(
        phase: IntegratedVoiceTurnPhase.completed,
        operationEpoch: _operationEpoch,
        turnGeneration: _turnGeneration,
        interruptionCount: _state.interruptionCount,
        pendingVoiceOutputCount: _voiceOutput.state.pendingCount,
        localStopRetryRequired: false,
        lastTurnOutcome: result.outcome,
        lastSpeechOutcome: _state.lastSpeechOutcome,
        safeMessage: 'The fake integrated voice turn completed.',
        technicalCode: result.technicalCode,
      ),
    );
    return result;
  }

  IntegratedVoiceTurnResult _failCurrent(
    _IntegratedVoiceTurnOperation operation,
    IntegratedVoiceTurnOutcome outcome,
    String technicalCode,
    String safeMessage,
  ) {
    if (!_isCurrent(operation)) {
      return _invalidatedResult();
    }
    _activeTurn = null;
    _detachOperation(operation, requestCooperativeCancel: false);
    final result = IntegratedVoiceTurnResult(
      outcome: outcome,
      technicalCode: _safeTechnicalCode(technicalCode),
    );
    _setState(
      IntegratedVoiceTurnState(
        phase: IntegratedVoiceTurnPhase.failed,
        operationEpoch: _operationEpoch,
        turnGeneration: _turnGeneration,
        interruptionCount: _state.interruptionCount,
        pendingVoiceOutputCount: _voiceOutput.state.pendingCount,
        localStopRetryRequired: _state.localStopRetryRequired,
        lastTurnOutcome: outcome,
        lastSpeechOutcome: _state.lastSpeechOutcome,
        safeMessage: _safeMessage(safeMessage),
        technicalCode: result.technicalCode,
      ),
    );
    return result;
  }

  IntegratedVoiceTurnResult _invalidatedResult() {
    return const IntegratedVoiceTurnResult(
      outcome: IntegratedVoiceTurnOutcome.invalidated,
      technicalCode: 'integrated_voice_turn_invalidated',
    );
  }

  bool _isCurrent(_IntegratedVoiceTurnOperation operation) {
    return !_isDisposed &&
        identical(_activeTurn?.token, operation.token) &&
        operation.epoch == _operationEpoch;
  }

  void _detachOperation(
    _IntegratedVoiceTurnOperation? operation, {
    required bool requestCooperativeCancel,
  }) {
    if (operation == null || operation.detached) {
      return;
    }
    operation.detached = true;

    final controller = operation.controller;
    final listener = operation.terminalListener;
    if (controller != null && listener != null) {
      controller.removeListener(listener);
    }
    final terminalCompleter = operation.terminalCompleter;
    if (terminalCompleter != null && !terminalCompleter.isCompleted) {
      terminalCompleter.complete(null);
    }
    operation.handoff?.dispose();

    if (controller == null) {
      return;
    }
    if (requestCooperativeCancel && controller.state.isActive) {
      final cancelFuture = controller.cancel();
      unawaited(
        cancelFuture.then<void>(
          (_) {
            controller.dispose();
          },
          onError: (_, _) {
            controller.dispose();
          },
        ),
      );
      return;
    }
    controller.dispose();
  }

  void _rememberSpeechEventId(String eventId) {
    _rememberedSpeechEventIds.add(eventId);
    while (_rememberedSpeechEventIds.length > _maxRememberedSpeechEventIds) {
      _rememberedSpeechEventIds.removeAt(0);
    }
  }

  bool _isValidSpeechEventId(String value) {
    return value.isNotEmpty &&
        value.runes.length <= integratedVoiceTurnMaxSpeechEventIdCodePoints &&
        RegExp(r'^[A-Za-z0-9._-]+$').hasMatch(value);
  }

  void _recordSpeechOutcome(
    IntegratedVoiceTurnSpeechOutcome outcome, {
    required String technicalCode,
  }) {
    _setState(
      IntegratedVoiceTurnState(
        phase: _state.phase,
        operationEpoch: _operationEpoch,
        turnGeneration: _turnGeneration,
        interruptionCount: _state.interruptionCount,
        pendingVoiceOutputCount: _voiceOutput.state.pendingCount,
        localStopRetryRequired: _state.localStopRetryRequired,
        lastTurnOutcome: _state.lastTurnOutcome,
        lastSpeechOutcome: outcome,
        safeMessage: _state.safeMessage,
        technicalCode: _safeTechnicalCode(technicalCode),
      ),
    );
  }

  void _setPhase(
    IntegratedVoiceTurnPhase phase, {
    required String safeMessage,
  }) {
    _setState(
      IntegratedVoiceTurnState(
        phase: phase,
        operationEpoch: _operationEpoch,
        turnGeneration: _turnGeneration,
        interruptionCount: _state.interruptionCount,
        pendingVoiceOutputCount: _voiceOutput.state.pendingCount,
        localStopRetryRequired: _state.localStopRetryRequired,
        lastTurnOutcome: _state.lastTurnOutcome,
        lastSpeechOutcome: _state.lastSpeechOutcome,
        safeMessage: _safeMessage(safeMessage),
        technicalCode: null,
      ),
    );
  }

  void _setState(IntegratedVoiceTurnState next) {
    if (_isDisposed) {
      return;
    }
    _state = next;
    notifyListeners();
  }

  @override
  void dispose() {
    if (_isDisposed) {
      return;
    }
    _isDisposed = true;
    ++_operationEpoch;
    final operation = _activeTurn;
    _activeTurn = null;
    _detachOperation(operation, requestCooperativeCancel: true);
    final interruption = _interruptionCompleter;
    _interruptionCompleter = null;
    if (interruption != null && !interruption.isCompleted) {
      interruption.complete(
        const IntegratedVoiceTurnSpeechResult(
          outcome: IntegratedVoiceTurnSpeechOutcome.disposed,
          technicalCode: 'integrated_voice_turn_disposed',
        ),
      );
    }
    unawaited(_voiceOutput.flush().then<void>((_) {}, onError: (_, _) {}));
    _rememberedSpeechEventIds.clear();
    _state = IntegratedVoiceTurnState(
      phase: IntegratedVoiceTurnPhase.disposed,
      operationEpoch: _operationEpoch,
      turnGeneration: _turnGeneration,
      interruptionCount: _state.interruptionCount,
      pendingVoiceOutputCount: 0,
      localStopRetryRequired: false,
      lastTurnOutcome: _state.lastTurnOutcome,
      lastSpeechOutcome: _state.lastSpeechOutcome,
      safeMessage: '',
      technicalCode: null,
    );
    super.dispose();
  }
}

class _IntegratedVoiceTurnOperation {
  _IntegratedVoiceTurnOperation({required this.token, required this.epoch});

  final Object token;
  final int epoch;
  RealtimeTextStreamController? controller;
  RealtimeTextStreamTranscriptHandoff? handoff;
  Completer<RealtimeTextStreamControllerState?>? terminalCompleter;
  VoidCallback? terminalListener;
  bool detached = false;
}

String _safeMessage(String value) {
  final compact = value
      .trim()
      .split(RegExp(r'\s+'))
      .where((part) => part.isNotEmpty)
      .join(' ');
  if (compact.isEmpty) {
    return 'The fake integrated voice turn could not continue safely.';
  }
  if (compact.runes.length <= realtimeTextStreamMaxProblemMessageChars) {
    return compact;
  }
  return String.fromCharCodes(
    compact.runes.take(realtimeTextStreamMaxProblemMessageChars),
  );
}

String _safeTechnicalCode(String value) {
  final normalized = value.trim().toLowerCase();
  if (normalized.isEmpty || !RegExp(r'^[a-z0-9_.-]+$').hasMatch(normalized)) {
    return 'integrated_voice_turn_failed';
  }
  if (normalized.runes.length <= integratedVoiceTurnMaxTechnicalCodePoints) {
    return normalized;
  }
  return String.fromCharCodes(
    normalized.runes.take(integratedVoiceTurnMaxTechnicalCodePoints),
  );
}
