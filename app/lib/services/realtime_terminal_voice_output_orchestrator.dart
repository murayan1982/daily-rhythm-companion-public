import 'dart:async';

import 'package:flutter/foundation.dart';

import '../models/realtime_text_stream.dart';
import 'realtime_text_stream_controller.dart';
import 'voice_output_queue.dart';

const int realtimeTerminalVoiceOutputMaxAudioUriCodePoints = 2048;
const int realtimeTerminalVoiceOutputMaxRememberedTerminals = 32;

const String _synthesisRejectedCode = 'synthesis_rejected';
const String _synthesisRequestFailedCode = 'synthesis_request_failed';
const String _invalidAudioUriCode = 'invalid_audio_uri';
const String _playbackFailedCode = 'playback_failed';
const String _playbackExpiredCode = 'playback_expired';
const String _playbackStoppedCode = 'playback_stopped';
const String _playbackLifecycleFailedCode = 'playback_lifecycle_failed';
const String _operationInvalidatedCode = 'voice_output_operation_invalidated';

/// Injected fake/in-memory synthesis boundary for RT-5c.
typedef RealtimeTerminalVoiceSynthesis =
    Future<RealtimeTerminalVoiceSynthesisResult> Function(
      RealtimeTerminalVoiceSynthesisRequest request,
    );

/// Injected fake/in-memory playback lifecycle boundary for RT-5c.
///
/// The returned future must complete only when playback reaches a terminal
/// lifecycle result. Starting playback is not completion.
typedef RealtimeTerminalVoicePlayback =
    Future<RealtimeTerminalVoicePlaybackResult> Function(Uri source);

enum RealtimeTerminalVoiceOutputPhase {
  idle,
  ready,
  synthesizing,
  playing,
  flushing,
  disposed,
}

enum RealtimeTerminalVoiceOutputEnqueueRejection {
  invalidCompletedTerminal,
  duplicateCompletedTerminal,
  queueRejected,
  disposed,
}

enum RealtimeTerminalVoiceSynthesisOutcome { audioReady, rejected, failed }

enum RealtimeTerminalVoicePlaybackOutcome {
  completed,
  failed,
  expired,
  stopped,
}

enum RealtimeTerminalVoiceOutputProcessOutcome {
  completed,
  synthesisRejected,
  synthesisFailed,
  invalidAudioUri,
  playbackFailed,
  playbackExpired,
  playbackStopped,
  playbackLifecycleFailed,
  invalidated,
  queueRejected,
  noPendingItem,
  processInProgress,
  disposed,
}

@immutable
class RealtimeTerminalVoiceSynthesisRequest {
  const RealtimeTerminalVoiceSynthesisRequest({
    required this.item,
    required this.utterance,
  });

  final VoiceOutputQueueItemMetadata item;
  final String utterance;
}

@immutable
class RealtimeTerminalVoiceSynthesisResult {
  const RealtimeTerminalVoiceSynthesisResult._({
    required this.outcome,
    this.opaqueAudioUri,
  });

  const RealtimeTerminalVoiceSynthesisResult.audioReady(String opaqueAudioUri)
    : this._(
        outcome: RealtimeTerminalVoiceSynthesisOutcome.audioReady,
        opaqueAudioUri: opaqueAudioUri,
      );

  const RealtimeTerminalVoiceSynthesisResult.rejected()
    : this._(outcome: RealtimeTerminalVoiceSynthesisOutcome.rejected);

  const RealtimeTerminalVoiceSynthesisResult.failed()
    : this._(outcome: RealtimeTerminalVoiceSynthesisOutcome.failed);

  final RealtimeTerminalVoiceSynthesisOutcome outcome;
  final String? opaqueAudioUri;
}

@immutable
class RealtimeTerminalVoicePlaybackResult {
  const RealtimeTerminalVoicePlaybackResult(this.outcome);

  const RealtimeTerminalVoicePlaybackResult.completed()
    : this(RealtimeTerminalVoicePlaybackOutcome.completed);

  const RealtimeTerminalVoicePlaybackResult.failed()
    : this(RealtimeTerminalVoicePlaybackOutcome.failed);

  const RealtimeTerminalVoicePlaybackResult.expired()
    : this(RealtimeTerminalVoicePlaybackOutcome.expired);

  const RealtimeTerminalVoicePlaybackResult.stopped()
    : this(RealtimeTerminalVoicePlaybackOutcome.stopped);

  final RealtimeTerminalVoicePlaybackOutcome outcome;
}

@immutable
class RealtimeTerminalVoiceOutputEnqueueResult {
  const RealtimeTerminalVoiceOutputEnqueueResult({
    required this.accepted,
    this.rejection,
    this.queueRejection,
    this.item,
  });

  final bool accepted;
  final RealtimeTerminalVoiceOutputEnqueueRejection? rejection;
  final VoiceOutputQueueRejection? queueRejection;
  final VoiceOutputQueueItemMetadata? item;
}

@immutable
class RealtimeTerminalVoiceOutputProcessResult {
  const RealtimeTerminalVoiceOutputProcessResult({
    required this.outcome,
    this.item,
    this.queueRejection,
    this.technicalCode,
  });

  final RealtimeTerminalVoiceOutputProcessOutcome outcome;
  final VoiceOutputQueueItemMetadata? item;
  final VoiceOutputQueueRejection? queueRejection;
  final String? technicalCode;
}

@immutable
class RealtimeTerminalVoiceOutputState {
  const RealtimeTerminalVoiceOutputState({
    required this.phase,
    required this.pendingCount,
    required this.activeItem,
    required this.lastProcessOutcome,
    required this.lastEnqueueRejection,
    required this.lastQueueRejection,
    required this.lastTechnicalCode,
  });

  final RealtimeTerminalVoiceOutputPhase phase;
  final int pendingCount;
  final VoiceOutputQueueItemMetadata? activeItem;
  final RealtimeTerminalVoiceOutputProcessOutcome? lastProcessOutcome;
  final RealtimeTerminalVoiceOutputEnqueueRejection? lastEnqueueRejection;
  final VoiceOutputQueueRejection? lastQueueRejection;
  final String? lastTechnicalCode;

  bool get isProcessing =>
      phase == RealtimeTerminalVoiceOutputPhase.synthesizing ||
      phase == RealtimeTerminalVoiceOutputPhase.playing;
}

class RealtimeTerminalVoiceOutputOrchestrator extends ChangeNotifier {
  RealtimeTerminalVoiceOutputOrchestrator({
    required VoiceOutputQueueController queue,
    required RealtimeTerminalVoiceSynthesis synthesize,
    required RealtimeTerminalVoicePlayback playToTerminal,
    this.maxRememberedTerminals =
        realtimeTerminalVoiceOutputMaxRememberedTerminals,
  }) : assert(maxRememberedTerminals > 0),
       _queue = queue,
       _synthesize = synthesize,
       _playToTerminal = playToTerminal,
       _state = RealtimeTerminalVoiceOutputState(
         phase: _phaseForQueue(queue.state.phase),
         pendingCount: queue.state.pendingCount,
         activeItem: queue.state.activeItem,
         lastProcessOutcome: null,
         lastEnqueueRejection: null,
         lastQueueRejection: null,
         lastTechnicalCode: null,
       );

  final VoiceOutputQueueController _queue;
  final RealtimeTerminalVoiceSynthesis _synthesize;
  final RealtimeTerminalVoicePlayback _playToTerminal;
  final int maxRememberedTerminals;

  final Set<_CompletedTerminalKey> _rememberedTerminals =
      <_CompletedTerminalKey>{};

  RealtimeTerminalVoiceOutputState _state;
  Object? _activeProcessToken;
  Future<VoiceOutputQueueFlushResult>? _flushInFlight;
  int _operationEpoch = 0;
  bool _isDisposed = false;

  RealtimeTerminalVoiceOutputState get state => _state;

  /// Explicitly enqueues one validated completed realtime terminal.
  ///
  /// This method does not subscribe to the realtime controller and does not
  /// start synthesis or playback. A separate explicit [processNext] call is
  /// required for each queued item.
  RealtimeTerminalVoiceOutputEnqueueResult enqueueCompletedTerminal(
    RealtimeTextStreamControllerState terminalState,
  ) {
    if (_isDisposed) {
      return const RealtimeTerminalVoiceOutputEnqueueResult(
        accepted: false,
        rejection: RealtimeTerminalVoiceOutputEnqueueRejection.disposed,
      );
    }

    final validated = _validateCompletedTerminal(terminalState);
    if (validated == null) {
      _recordEnqueueRejection(
        RealtimeTerminalVoiceOutputEnqueueRejection.invalidCompletedTerminal,
      );
      return const RealtimeTerminalVoiceOutputEnqueueResult(
        accepted: false,
        rejection: RealtimeTerminalVoiceOutputEnqueueRejection
            .invalidCompletedTerminal,
      );
    }

    if (_rememberedTerminals.contains(validated.key)) {
      _recordEnqueueRejection(
        RealtimeTerminalVoiceOutputEnqueueRejection.duplicateCompletedTerminal,
      );
      return const RealtimeTerminalVoiceOutputEnqueueResult(
        accepted: false,
        rejection: RealtimeTerminalVoiceOutputEnqueueRejection
            .duplicateCompletedTerminal,
      );
    }

    final queueResult = _queue.enqueue(validated.utterance);
    if (!queueResult.accepted) {
      _recordEnqueueRejection(
        RealtimeTerminalVoiceOutputEnqueueRejection.queueRejected,
        queueRejection: queueResult.rejection,
      );
      return RealtimeTerminalVoiceOutputEnqueueResult(
        accepted: false,
        rejection: RealtimeTerminalVoiceOutputEnqueueRejection.queueRejected,
        queueRejection: queueResult.rejection,
      );
    }

    _remember(validated.key);
    _setState(
      RealtimeTerminalVoiceOutputState(
        phase: _phaseAfterQueueMutation(),
        pendingCount: _queue.state.pendingCount,
        activeItem: _queue.state.activeItem,
        lastProcessOutcome: _state.lastProcessOutcome,
        lastEnqueueRejection: null,
        lastQueueRejection: null,
        lastTechnicalCode: _state.lastTechnicalCode,
      ),
    );

    return RealtimeTerminalVoiceOutputEnqueueResult(
      accepted: true,
      item: queueResult.item,
    );
  }

  /// Claims and processes at most one queued item.
  ///
  /// Pending items are never drained automatically. Concurrent processing is
  /// rejected rather than sharing or replacing the active operation.
  Future<RealtimeTerminalVoiceOutputProcessResult> processNext() {
    if (_isDisposed) {
      return Future<RealtimeTerminalVoiceOutputProcessResult>.value(
        const RealtimeTerminalVoiceOutputProcessResult(
          outcome: RealtimeTerminalVoiceOutputProcessOutcome.disposed,
          technicalCode: 'voice_output_orchestrator_disposed',
        ),
      );
    }
    if (_activeProcessToken != null) {
      return Future<RealtimeTerminalVoiceOutputProcessResult>.value(
        const RealtimeTerminalVoiceOutputProcessResult(
          outcome: RealtimeTerminalVoiceOutputProcessOutcome.processInProgress,
          technicalCode: 'voice_output_process_in_progress',
        ),
      );
    }

    final claimResult = _queue.claimNext();
    if (!claimResult.accepted) {
      return Future<RealtimeTerminalVoiceOutputProcessResult>.value(
        _recordClaimRejection(claimResult.rejection),
      );
    }

    final claim = claimResult.claim!;
    final token = Object();
    final epoch = ++_operationEpoch;
    _activeProcessToken = token;
    _setState(
      RealtimeTerminalVoiceOutputState(
        phase: RealtimeTerminalVoiceOutputPhase.synthesizing,
        pendingCount: _queue.state.pendingCount,
        activeItem: claim.item,
        lastProcessOutcome: null,
        lastEnqueueRejection: _state.lastEnqueueRejection,
        lastQueueRejection: null,
        lastTechnicalCode: null,
      ),
    );

    return _runClaim(claim, token: token, epoch: epoch);
  }

  Future<RealtimeTerminalVoiceOutputProcessResult> _runClaim(
    VoiceOutputQueueClaim claim, {
    required Object token,
    required int epoch,
  }) async {
    try {
      if (!_isCurrentClaim(claim, token: token, epoch: epoch)) {
        return _invalidated(claim.item);
      }

      RealtimeTerminalVoiceSynthesisResult synthesisResult;
      try {
        synthesisResult = await _synthesize(
          RealtimeTerminalVoiceSynthesisRequest(
            item: claim.item,
            utterance: claim.utterance,
          ),
        );
      } catch (_) {
        return _failCurrentClaim(
          claim,
          token: token,
          epoch: epoch,
          outcome: RealtimeTerminalVoiceOutputProcessOutcome.synthesisFailed,
          technicalCode: _synthesisRequestFailedCode,
        );
      }

      if (!_isCurrentClaim(claim, token: token, epoch: epoch)) {
        return _invalidated(claim.item);
      }

      switch (synthesisResult.outcome) {
        case RealtimeTerminalVoiceSynthesisOutcome.rejected:
          return _failCurrentClaim(
            claim,
            token: token,
            epoch: epoch,
            outcome:
                RealtimeTerminalVoiceOutputProcessOutcome.synthesisRejected,
            technicalCode: _synthesisRejectedCode,
          );
        case RealtimeTerminalVoiceSynthesisOutcome.failed:
          return _failCurrentClaim(
            claim,
            token: token,
            epoch: epoch,
            outcome: RealtimeTerminalVoiceOutputProcessOutcome.synthesisFailed,
            technicalCode: _synthesisRequestFailedCode,
          );
        case RealtimeTerminalVoiceSynthesisOutcome.audioReady:
          break;
      }

      final source = _validatedAudioUri(synthesisResult.opaqueAudioUri);
      if (source == null) {
        return _failCurrentClaim(
          claim,
          token: token,
          epoch: epoch,
          outcome: RealtimeTerminalVoiceOutputProcessOutcome.invalidAudioUri,
          technicalCode: _invalidAudioUriCode,
        );
      }

      if (!_isCurrentClaim(claim, token: token, epoch: epoch)) {
        return _invalidated(claim.item);
      }

      Future<RealtimeTerminalVoicePlaybackResult> playbackFuture;
      try {
        playbackFuture = _playToTerminal(source);
      } catch (_) {
        return _failCurrentClaim(
          claim,
          token: token,
          epoch: epoch,
          outcome:
              RealtimeTerminalVoiceOutputProcessOutcome.playbackLifecycleFailed,
          technicalCode: _playbackLifecycleFailedCode,
        );
      }

      if (!_isCurrentClaim(claim, token: token, epoch: epoch)) {
        return _invalidated(claim.item);
      }

      _setState(
        RealtimeTerminalVoiceOutputState(
          phase: RealtimeTerminalVoiceOutputPhase.playing,
          pendingCount: _queue.state.pendingCount,
          activeItem: claim.item,
          lastProcessOutcome: null,
          lastEnqueueRejection: _state.lastEnqueueRejection,
          lastQueueRejection: null,
          lastTechnicalCode: null,
        ),
      );

      RealtimeTerminalVoicePlaybackResult playbackResult;
      try {
        playbackResult = await playbackFuture;
      } catch (_) {
        return _failCurrentClaim(
          claim,
          token: token,
          epoch: epoch,
          outcome:
              RealtimeTerminalVoiceOutputProcessOutcome.playbackLifecycleFailed,
          technicalCode: _playbackLifecycleFailedCode,
        );
      }

      if (!_isCurrentClaim(claim, token: token, epoch: epoch)) {
        return _invalidated(claim.item);
      }

      switch (playbackResult.outcome) {
        case RealtimeTerminalVoicePlaybackOutcome.completed:
          return _completeCurrentClaim(claim, token: token, epoch: epoch);
        case RealtimeTerminalVoicePlaybackOutcome.failed:
          return _failCurrentClaim(
            claim,
            token: token,
            epoch: epoch,
            outcome: RealtimeTerminalVoiceOutputProcessOutcome.playbackFailed,
            technicalCode: _playbackFailedCode,
          );
        case RealtimeTerminalVoicePlaybackOutcome.expired:
          return _failCurrentClaim(
            claim,
            token: token,
            epoch: epoch,
            outcome: RealtimeTerminalVoiceOutputProcessOutcome.playbackExpired,
            technicalCode: _playbackExpiredCode,
          );
        case RealtimeTerminalVoicePlaybackOutcome.stopped:
          return _failCurrentClaim(
            claim,
            token: token,
            epoch: epoch,
            outcome: RealtimeTerminalVoiceOutputProcessOutcome.playbackStopped,
            technicalCode: _playbackStoppedCode,
          );
      }
    } finally {
      if (identical(_activeProcessToken, token)) {
        _activeProcessToken = null;
      }
    }
  }

  /// Invalidates active work, clears the app-owned queue, and requests only the
  /// queue's injected local playback stop boundary.
  Future<VoiceOutputQueueFlushResult> flush() {
    if (_isDisposed) {
      return Future<VoiceOutputQueueFlushResult>.value(
        const VoiceOutputQueueFlushResult(
          outcome: VoiceOutputQueueFlushOutcome.disposed,
          clearedPendingCount: 0,
          invalidatedActiveItem: false,
          localPlaybackStopRequested: false,
          localPlaybackStopSucceeded: false,
          technicalCode: 'voice_output_orchestrator_disposed',
        ),
      );
    }

    final existing = _flushInFlight;
    if (existing != null) {
      return existing;
    }

    final completer = Completer<VoiceOutputQueueFlushResult>();
    _flushInFlight = completer.future;

    ++_operationEpoch;
    _activeProcessToken = null;

    final queueFuture = _queue.flush();
    _syncFlushingQueueState();
    unawaited(_completeFlush(queueFuture, completer));
    return completer.future;
  }

  Future<void> _completeFlush(
    Future<VoiceOutputQueueFlushResult> queueFuture,
    Completer<VoiceOutputQueueFlushResult> completer,
  ) async {
    try {
      final result = await queueFuture;
      if (!_isDisposed && identical(_flushInFlight, completer.future)) {
        _setState(
          RealtimeTerminalVoiceOutputState(
            phase: _phaseForQueue(_queue.state.phase),
            pendingCount: _queue.state.pendingCount,
            activeItem: _queue.state.activeItem,
            lastProcessOutcome: null,
            lastEnqueueRejection: _state.lastEnqueueRejection,
            lastQueueRejection: null,
            lastTechnicalCode: result.technicalCode,
          ),
        );
      }
      completer.complete(result);
    } catch (_) {
      const result = VoiceOutputQueueFlushResult(
        outcome:
            VoiceOutputQueueFlushOutcome.completedWithLocalPlaybackStopFailure,
        clearedPendingCount: 0,
        invalidatedActiveItem: false,
        localPlaybackStopRequested: false,
        localPlaybackStopSucceeded: false,
        technicalCode: 'voice_output_queue_flush_failed',
      );
      if (!_isDisposed && identical(_flushInFlight, completer.future)) {
        _setState(
          RealtimeTerminalVoiceOutputState(
            phase: _phaseForQueue(_queue.state.phase),
            pendingCount: _queue.state.pendingCount,
            activeItem: _queue.state.activeItem,
            lastProcessOutcome: null,
            lastEnqueueRejection: _state.lastEnqueueRejection,
            lastQueueRejection: null,
            lastTechnicalCode: result.technicalCode,
          ),
        );
      }
      completer.complete(result);
    } finally {
      if (identical(_flushInFlight, completer.future)) {
        _flushInFlight = null;
      }
    }
  }

  RealtimeTerminalVoiceOutputProcessResult _completeCurrentClaim(
    VoiceOutputQueueClaim claim, {
    required Object token,
    required int epoch,
  }) {
    if (!_isCurrentClaim(claim, token: token, epoch: epoch)) {
      return _invalidated(claim.item);
    }

    final queueResult = _queue.complete(claim);
    if (!queueResult.accepted) {
      return _recordQueueProcessRejection(claim.item, queueResult.rejection);
    }

    const outcome = RealtimeTerminalVoiceOutputProcessOutcome.completed;
    if (_isCurrentOperation(token: token, epoch: epoch)) {
      _recordProcessOutcome(outcome);
    }
    return RealtimeTerminalVoiceOutputProcessResult(
      outcome: outcome,
      item: claim.item,
    );
  }

  RealtimeTerminalVoiceOutputProcessResult _failCurrentClaim(
    VoiceOutputQueueClaim claim, {
    required Object token,
    required int epoch,
    required RealtimeTerminalVoiceOutputProcessOutcome outcome,
    required String technicalCode,
  }) {
    if (!_isCurrentClaim(claim, token: token, epoch: epoch)) {
      return _invalidated(claim.item);
    }

    final queueResult = _queue.fail(claim, technicalCode: technicalCode);
    if (!queueResult.accepted) {
      return _recordQueueProcessRejection(claim.item, queueResult.rejection);
    }

    if (_isCurrentOperation(token: token, epoch: epoch)) {
      _recordProcessOutcome(outcome, technicalCode: technicalCode);
    }
    return RealtimeTerminalVoiceOutputProcessResult(
      outcome: outcome,
      item: claim.item,
      technicalCode: technicalCode,
    );
  }

  bool _isCurrentClaim(
    VoiceOutputQueueClaim claim, {
    required Object token,
    required int epoch,
  }) {
    if (!_isCurrentOperation(token: token, epoch: epoch)) {
      return false;
    }
    final queueState = _queue.state;
    return queueState.generation == claim.item.generation &&
        queueState.activeItem?.itemId == claim.item.itemId;
  }

  bool _isCurrentOperation({required Object token, required int epoch}) {
    return !_isDisposed &&
        identical(_activeProcessToken, token) &&
        epoch == _operationEpoch;
  }

  RealtimeTerminalVoiceOutputProcessResult _invalidated(
    VoiceOutputQueueItemMetadata item,
  ) {
    return RealtimeTerminalVoiceOutputProcessResult(
      outcome: RealtimeTerminalVoiceOutputProcessOutcome.invalidated,
      item: item,
      technicalCode: _operationInvalidatedCode,
    );
  }

  RealtimeTerminalVoiceOutputProcessResult _recordClaimRejection(
    VoiceOutputQueueRejection? rejection,
  ) {
    if (rejection == VoiceOutputQueueRejection.noPendingItem) {
      const outcome = RealtimeTerminalVoiceOutputProcessOutcome.noPendingItem;
      _recordProcessOutcome(
        outcome,
        queueRejection: rejection,
        technicalCode: 'voice_output_queue_empty',
      );
      return RealtimeTerminalVoiceOutputProcessResult(
        outcome: outcome,
        queueRejection: rejection,
        technicalCode: 'voice_output_queue_empty',
      );
    }
    if (rejection == VoiceOutputQueueRejection.disposed) {
      const outcome = RealtimeTerminalVoiceOutputProcessOutcome.disposed;
      _recordProcessOutcome(
        outcome,
        queueRejection: rejection,
        technicalCode: 'voice_output_queue_disposed',
      );
      return RealtimeTerminalVoiceOutputProcessResult(
        outcome: outcome,
        queueRejection: rejection,
        technicalCode: 'voice_output_queue_disposed',
      );
    }
    return _recordQueueProcessRejection(null, rejection);
  }

  RealtimeTerminalVoiceOutputProcessResult _recordQueueProcessRejection(
    VoiceOutputQueueItemMetadata? item,
    VoiceOutputQueueRejection? rejection,
  ) {
    const outcome = RealtimeTerminalVoiceOutputProcessOutcome.queueRejected;
    _recordProcessOutcome(
      outcome,
      queueRejection: rejection,
      technicalCode: 'voice_output_queue_rejected',
    );
    return RealtimeTerminalVoiceOutputProcessResult(
      outcome: outcome,
      item: item,
      queueRejection: rejection,
      technicalCode: 'voice_output_queue_rejected',
    );
  }

  void _recordProcessOutcome(
    RealtimeTerminalVoiceOutputProcessOutcome outcome, {
    VoiceOutputQueueRejection? queueRejection,
    String? technicalCode,
  }) {
    _setState(
      RealtimeTerminalVoiceOutputState(
        phase: _phaseForQueue(_queue.state.phase),
        pendingCount: _queue.state.pendingCount,
        activeItem: _queue.state.activeItem,
        lastProcessOutcome: outcome,
        lastEnqueueRejection: _state.lastEnqueueRejection,
        lastQueueRejection: queueRejection,
        lastTechnicalCode: technicalCode,
      ),
    );
  }

  void _recordEnqueueRejection(
    RealtimeTerminalVoiceOutputEnqueueRejection rejection, {
    VoiceOutputQueueRejection? queueRejection,
  }) {
    _setState(
      RealtimeTerminalVoiceOutputState(
        phase: _phaseAfterQueueMutation(),
        pendingCount: _queue.state.pendingCount,
        activeItem: _queue.state.activeItem,
        lastProcessOutcome: _state.lastProcessOutcome,
        lastEnqueueRejection: rejection,
        lastQueueRejection: queueRejection,
        lastTechnicalCode: _state.lastTechnicalCode,
      ),
    );
  }

  void _syncFlushingQueueState() {
    if (_isDisposed) {
      return;
    }
    _setState(
      RealtimeTerminalVoiceOutputState(
        phase: RealtimeTerminalVoiceOutputPhase.flushing,
        pendingCount: _queue.state.pendingCount,
        activeItem: _queue.state.activeItem,
        lastProcessOutcome: null,
        lastEnqueueRejection: _state.lastEnqueueRejection,
        lastQueueRejection: null,
        lastTechnicalCode: null,
      ),
    );
  }

  RealtimeTerminalVoiceOutputPhase _phaseAfterQueueMutation() {
    if (_activeProcessToken != null && _state.isProcessing) {
      return _state.phase;
    }
    return _phaseForQueue(_queue.state.phase);
  }

  void _remember(_CompletedTerminalKey key) {
    if (_rememberedTerminals.length >= maxRememberedTerminals) {
      _rememberedTerminals.remove(_rememberedTerminals.first);
    }
    _rememberedTerminals.add(key);
  }

  void _setState(RealtimeTerminalVoiceOutputState nextState) {
    if (_isDisposed) {
      return;
    }
    _state = nextState;
    notifyListeners();
  }

  @override
  void dispose() {
    if (_isDisposed) {
      return;
    }
    _isDisposed = true;
    ++_operationEpoch;
    _activeProcessToken = null;
    _rememberedTerminals.clear();
    _state = const RealtimeTerminalVoiceOutputState(
      phase: RealtimeTerminalVoiceOutputPhase.disposed,
      pendingCount: 0,
      activeItem: null,
      lastProcessOutcome: null,
      lastEnqueueRejection: null,
      lastQueueRejection: null,
      lastTechnicalCode: null,
    );
    unawaited(_queue.flush().then<void>((_) {}, onError: (_, _) {}));
    super.dispose();
  }
}

class _ValidatedCompletedTerminal {
  const _ValidatedCompletedTerminal({
    required this.key,
    required this.utterance,
  });

  final _CompletedTerminalKey key;
  final String utterance;
}

@immutable
class _CompletedTerminalKey {
  const _CompletedTerminalKey({
    required this.sessionId,
    required this.turnId,
    required this.sequence,
  });

  final String sessionId;
  final String turnId;
  final int sequence;

  @override
  bool operator ==(Object other) {
    return other is _CompletedTerminalKey &&
        other.sessionId == sessionId &&
        other.turnId == turnId &&
        other.sequence == sequence;
  }

  @override
  int get hashCode => Object.hash(sessionId, turnId, sequence);
}

_ValidatedCompletedTerminal? _validateCompletedTerminal(
  RealtimeTextStreamControllerState state,
) {
  final createResponse = state.createResponse;
  final terminal = state.terminal;
  if (state.phase != RealtimeTextStreamControllerPhase.completed ||
      createResponse == null ||
      !createResponse.accepted ||
      terminal == null ||
      terminal.outcome != RealtimeTextStreamTerminalOutcome.completed ||
      state.problem != null ||
      state.outputText.trim().isEmpty ||
      terminal.sequence <= 0 ||
      terminal.sequence != state.lastSequence ||
      terminal.finalText != state.outputText ||
      terminal.outputCharCount != state.outputText.runes.length) {
    return null;
  }

  final rawSessionId = createResponse.session.sessionId;
  final rawTurnId = createResponse.turn.turnId;
  final sessionId = rawSessionId.trim();
  final turnId = rawTurnId.trim();
  if (sessionId.isEmpty ||
      turnId.isEmpty ||
      sessionId != rawSessionId ||
      turnId != rawTurnId ||
      createResponse.turn.sessionId != createResponse.session.sessionId ||
      createResponse.session.activeTurnId != createResponse.turn.turnId) {
    return null;
  }

  return _ValidatedCompletedTerminal(
    key: _CompletedTerminalKey(
      sessionId: sessionId,
      turnId: turnId,
      sequence: terminal.sequence,
    ),
    utterance: state.outputText,
  );
}

Uri? _validatedAudioUri(String? value) {
  if (value == null ||
      value.runes.length > realtimeTerminalVoiceOutputMaxAudioUriCodePoints) {
    return null;
  }

  final normalized = value.trim();
  if (normalized.isEmpty ||
      normalized != value ||
      normalized.contains('\\') ||
      normalized.runes.any(
        (codePoint) => codePoint <= 0x20 || codePoint == 0x7f,
      )) {
    return null;
  }

  final uri = Uri.tryParse(normalized);
  if (uri == null ||
      !uri.isAbsolute ||
      (uri.scheme != 'http' && uri.scheme != 'https') ||
      uri.host.isEmpty ||
      uri.userInfo.isNotEmpty ||
      uri.fragment.isNotEmpty) {
    return null;
  }
  return uri;
}

RealtimeTerminalVoiceOutputPhase _phaseForQueue(VoiceOutputQueuePhase phase) {
  switch (phase) {
    case VoiceOutputQueuePhase.idle:
      return RealtimeTerminalVoiceOutputPhase.idle;
    case VoiceOutputQueuePhase.ready:
    case VoiceOutputQueuePhase.active:
      return RealtimeTerminalVoiceOutputPhase.ready;
    case VoiceOutputQueuePhase.flushing:
      return RealtimeTerminalVoiceOutputPhase.flushing;
    case VoiceOutputQueuePhase.disposed:
      return RealtimeTerminalVoiceOutputPhase.disposed;
  }
}
