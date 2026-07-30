import 'dart:async';

import 'package:flutter/foundation.dart';

const int voiceOutputQueueMaxPendingItems = 8;
const int voiceOutputQueueMaxUtteranceCodePoints = 4096;
const int voiceOutputQueueMaxRetainedCodePoints = 16384;
const int voiceOutputQueueMaxTechnicalCodePoints = 128;

typedef VoiceOutputLocalPlaybackStop = Future<void> Function();

enum VoiceOutputQueuePhase { idle, ready, active, flushing, disposed }

enum VoiceOutputQueueRejection {
  invalidUtterance,
  utteranceTooLong,
  pendingLimitReached,
  retainedTextLimitReached,
  activeItemExists,
  noPendingItem,
  flushInProgress,
  staleGeneration,
  staleItem,
  noActiveItem,
  disposed,
}

enum VoiceOutputQueueItemOutcome { completed, failed }

enum VoiceOutputQueueFlushOutcome {
  completed,
  completedWithLocalPlaybackStopFailure,
  disposed,
}

@immutable
class VoiceOutputQueueItemMetadata {
  const VoiceOutputQueueItemMetadata({
    required this.itemId,
    required this.generation,
    required this.characterCount,
  });

  final String itemId;
  final int generation;
  final int characterCount;
}

@immutable
class VoiceOutputQueueClaim {
  const VoiceOutputQueueClaim({required this.item, required this.utterance});

  final VoiceOutputQueueItemMetadata item;
  final String utterance;
}

@immutable
class VoiceOutputQueueActionResult {
  const VoiceOutputQueueActionResult({
    required this.accepted,
    this.rejection,
    this.item,
    this.technicalCode,
  });

  final bool accepted;
  final VoiceOutputQueueRejection? rejection;
  final VoiceOutputQueueItemMetadata? item;
  final String? technicalCode;
}

@immutable
class VoiceOutputQueueClaimResult {
  const VoiceOutputQueueClaimResult({
    required this.accepted,
    this.rejection,
    this.claim,
  });

  final bool accepted;
  final VoiceOutputQueueRejection? rejection;
  final VoiceOutputQueueClaim? claim;
}

@immutable
class VoiceOutputQueueFlushResult {
  const VoiceOutputQueueFlushResult({
    required this.outcome,
    required this.clearedPendingCount,
    required this.invalidatedActiveItem,
    required this.localPlaybackStopRequested,
    required this.localPlaybackStopSucceeded,
    this.technicalCode,
  });

  final VoiceOutputQueueFlushOutcome outcome;
  final int clearedPendingCount;
  final bool invalidatedActiveItem;
  final bool localPlaybackStopRequested;
  final bool localPlaybackStopSucceeded;
  final String? technicalCode;
}

@immutable
class VoiceOutputQueueState {
  const VoiceOutputQueueState({
    required this.phase,
    required this.generation,
    required this.pendingCount,
    required this.retainedCodePoints,
    required this.activeItem,
    required this.lastOutcome,
    required this.lastTechnicalCode,
  });

  final VoiceOutputQueuePhase phase;
  final int generation;
  final int pendingCount;
  final int retainedCodePoints;
  final VoiceOutputQueueItemMetadata? activeItem;
  final VoiceOutputQueueItemOutcome? lastOutcome;
  final String? lastTechnicalCode;

  bool get hasActiveItem => activeItem != null;
  bool get canClaim =>
      phase == VoiceOutputQueuePhase.ready &&
      !hasActiveItem &&
      pendingCount > 0;
}

class VoiceOutputQueueController extends ChangeNotifier {
  VoiceOutputQueueController({
    required VoiceOutputLocalPlaybackStop stopLocalPlayback,
    this.maxPendingItems = voiceOutputQueueMaxPendingItems,
    this.maxUtteranceCodePoints = voiceOutputQueueMaxUtteranceCodePoints,
    this.maxRetainedCodePoints = voiceOutputQueueMaxRetainedCodePoints,
  }) : assert(maxPendingItems > 0),
       assert(maxUtteranceCodePoints > 0),
       assert(maxRetainedCodePoints > 0),
       _stopLocalPlayback = stopLocalPlayback;

  final VoiceOutputLocalPlaybackStop _stopLocalPlayback;
  final int maxPendingItems;
  final int maxUtteranceCodePoints;
  final int maxRetainedCodePoints;

  final List<_QueuedUtterance> _pending = <_QueuedUtterance>[];
  _QueuedUtterance? _active;
  int _generation = 1;
  int _nextItemSequence = 0;
  int _retainedCodePoints = 0;
  VoiceOutputQueuePhase _phase = VoiceOutputQueuePhase.idle;
  VoiceOutputQueueItemOutcome? _lastOutcome;
  String? _lastTechnicalCode;
  Future<VoiceOutputQueueFlushResult>? _flushInFlight;
  bool _isDisposed = false;

  VoiceOutputQueueState get state => VoiceOutputQueueState(
    phase: _phase,
    generation: _generation,
    pendingCount: _pending.length,
    retainedCodePoints: _retainedCodePoints,
    activeItem: _active?.item,
    lastOutcome: _lastOutcome,
    lastTechnicalCode: _lastTechnicalCode,
  );

  VoiceOutputQueueActionResult enqueue(String utterance) {
    if (_isDisposed) {
      return _rejectedAction(VoiceOutputQueueRejection.disposed);
    }
    if (_phase == VoiceOutputQueuePhase.flushing) {
      return _rejectedAction(VoiceOutputQueueRejection.flushInProgress);
    }

    final normalized = utterance.trim();
    if (normalized.isEmpty) {
      return _rejectedAction(VoiceOutputQueueRejection.invalidUtterance);
    }

    final characterCount = normalized.runes.length;
    if (characterCount > maxUtteranceCodePoints) {
      return _rejectedAction(VoiceOutputQueueRejection.utteranceTooLong);
    }
    if (_pending.length >= maxPendingItems) {
      return _rejectedAction(VoiceOutputQueueRejection.pendingLimitReached);
    }
    if (_retainedCodePoints + characterCount > maxRetainedCodePoints) {
      return _rejectedAction(
        VoiceOutputQueueRejection.retainedTextLimitReached,
      );
    }

    final item = VoiceOutputQueueItemMetadata(
      itemId: 'tts-${++_nextItemSequence}',
      generation: _generation,
      characterCount: characterCount,
    );
    _pending.add(_QueuedUtterance(item: item, utterance: normalized));
    _retainedCodePoints += characterCount;
    _lastOutcome = null;
    _lastTechnicalCode = null;
    _phase = _active == null
        ? VoiceOutputQueuePhase.ready
        : VoiceOutputQueuePhase.active;
    _notify();

    return VoiceOutputQueueActionResult(accepted: true, item: item);
  }

  VoiceOutputQueueClaimResult claimNext() {
    if (_isDisposed) {
      return const VoiceOutputQueueClaimResult(
        accepted: false,
        rejection: VoiceOutputQueueRejection.disposed,
      );
    }
    if (_phase == VoiceOutputQueuePhase.flushing) {
      return const VoiceOutputQueueClaimResult(
        accepted: false,
        rejection: VoiceOutputQueueRejection.flushInProgress,
      );
    }
    if (_active != null) {
      return const VoiceOutputQueueClaimResult(
        accepted: false,
        rejection: VoiceOutputQueueRejection.activeItemExists,
      );
    }
    if (_pending.isEmpty) {
      return const VoiceOutputQueueClaimResult(
        accepted: false,
        rejection: VoiceOutputQueueRejection.noPendingItem,
      );
    }

    final next = _pending.removeAt(0);
    _active = next;
    _phase = VoiceOutputQueuePhase.active;
    _lastOutcome = null;
    _lastTechnicalCode = null;
    _notify();

    return VoiceOutputQueueClaimResult(
      accepted: true,
      claim: VoiceOutputQueueClaim(item: next.item, utterance: next.utterance),
    );
  }

  VoiceOutputQueueActionResult complete(VoiceOutputQueueClaim claim) {
    final rejection = _validateClaim(claim);
    if (rejection != null) {
      return _rejectedAction(rejection);
    }

    final item = _active!.item;
    _releaseActive();
    _lastOutcome = VoiceOutputQueueItemOutcome.completed;
    _lastTechnicalCode = null;
    _notify();

    return VoiceOutputQueueActionResult(accepted: true, item: item);
  }

  VoiceOutputQueueActionResult fail(
    VoiceOutputQueueClaim claim, {
    String technicalCode = 'voice_output_queue_item_failed',
  }) {
    final rejection = _validateClaim(claim);
    if (rejection != null) {
      return _rejectedAction(rejection);
    }

    final item = _active!.item;
    _releaseActive();
    _lastOutcome = VoiceOutputQueueItemOutcome.failed;
    _lastTechnicalCode = _safeTechnicalCode(
      technicalCode,
      fallback: 'voice_output_queue_item_failed',
    );
    _notify();

    return VoiceOutputQueueActionResult(
      accepted: true,
      item: item,
      technicalCode: _lastTechnicalCode,
    );
  }

  Future<VoiceOutputQueueFlushResult> flush() {
    if (_isDisposed) {
      return Future<VoiceOutputQueueFlushResult>.value(
        const VoiceOutputQueueFlushResult(
          outcome: VoiceOutputQueueFlushOutcome.disposed,
          clearedPendingCount: 0,
          invalidatedActiveItem: false,
          localPlaybackStopRequested: false,
          localPlaybackStopSucceeded: false,
          technicalCode: 'voice_output_queue_disposed',
        ),
      );
    }

    final existing = _flushInFlight;
    if (existing != null) {
      return existing;
    }

    final completer = Completer<VoiceOutputQueueFlushResult>();
    _flushInFlight = completer.future;
    unawaited(_completeFlush(completer));
    return completer.future;
  }

  Future<void> _completeFlush(
    Completer<VoiceOutputQueueFlushResult> completer,
  ) async {
    try {
      completer.complete(await _performFlush());
    } catch (error, stackTrace) {
      completer.completeError(error, stackTrace);
    } finally {
      if (identical(_flushInFlight, completer.future)) {
        _flushInFlight = null;
      }
    }
  }

  Future<VoiceOutputQueueFlushResult> _performFlush() async {
    final clearedPendingCount = _pending.length;
    final invalidatedActiveItem = _active != null;

    _generation += 1;
    _pending.clear();
    _active = null;
    _retainedCodePoints = 0;
    _lastOutcome = null;
    _lastTechnicalCode = null;
    _phase = VoiceOutputQueuePhase.flushing;
    _notify();

    try {
      await _stopLocalPlayback();
    } catch (_) {
      if (_isDisposed) {
        return VoiceOutputQueueFlushResult(
          outcome: VoiceOutputQueueFlushOutcome.disposed,
          clearedPendingCount: clearedPendingCount,
          invalidatedActiveItem: invalidatedActiveItem,
          localPlaybackStopRequested: true,
          localPlaybackStopSucceeded: false,
          technicalCode: 'voice_output_queue_disposed',
        );
      }

      _phase = VoiceOutputQueuePhase.idle;
      _lastTechnicalCode = 'local_playback_stop_failed';
      _notify();
      return VoiceOutputQueueFlushResult(
        outcome:
            VoiceOutputQueueFlushOutcome.completedWithLocalPlaybackStopFailure,
        clearedPendingCount: clearedPendingCount,
        invalidatedActiveItem: invalidatedActiveItem,
        localPlaybackStopRequested: true,
        localPlaybackStopSucceeded: false,
        technicalCode: _lastTechnicalCode,
      );
    }

    if (_isDisposed) {
      return VoiceOutputQueueFlushResult(
        outcome: VoiceOutputQueueFlushOutcome.disposed,
        clearedPendingCount: clearedPendingCount,
        invalidatedActiveItem: invalidatedActiveItem,
        localPlaybackStopRequested: true,
        localPlaybackStopSucceeded: true,
        technicalCode: 'voice_output_queue_disposed',
      );
    }

    _phase = VoiceOutputQueuePhase.idle;
    _notify();
    return VoiceOutputQueueFlushResult(
      outcome: VoiceOutputQueueFlushOutcome.completed,
      clearedPendingCount: clearedPendingCount,
      invalidatedActiveItem: invalidatedActiveItem,
      localPlaybackStopRequested: true,
      localPlaybackStopSucceeded: true,
    );
  }

  VoiceOutputQueueRejection? _validateClaim(VoiceOutputQueueClaim claim) {
    if (_isDisposed) {
      return VoiceOutputQueueRejection.disposed;
    }
    if (_phase == VoiceOutputQueuePhase.flushing) {
      return VoiceOutputQueueRejection.flushInProgress;
    }
    if (claim.item.generation != _generation) {
      return VoiceOutputQueueRejection.staleGeneration;
    }
    final active = _active;
    if (active == null) {
      return VoiceOutputQueueRejection.noActiveItem;
    }
    if (active.item.itemId != claim.item.itemId) {
      return VoiceOutputQueueRejection.staleItem;
    }
    return null;
  }

  void _releaseActive() {
    final active = _active!;
    _active = null;
    _retainedCodePoints -= active.item.characterCount;
    if (_retainedCodePoints < 0) {
      _retainedCodePoints = 0;
    }
    _phase = _pending.isEmpty
        ? VoiceOutputQueuePhase.idle
        : VoiceOutputQueuePhase.ready;
  }

  VoiceOutputQueueActionResult _rejectedAction(
    VoiceOutputQueueRejection rejection,
  ) {
    return VoiceOutputQueueActionResult(accepted: false, rejection: rejection);
  }

  void _notify() {
    if (!_isDisposed) {
      notifyListeners();
    }
  }

  @override
  void dispose() {
    if (_isDisposed) {
      return;
    }
    _isDisposed = true;
    _generation += 1;
    _pending.clear();
    _active = null;
    _retainedCodePoints = 0;
    _lastOutcome = null;
    _lastTechnicalCode = null;
    _phase = VoiceOutputQueuePhase.disposed;
    super.dispose();
  }
}

class _QueuedUtterance {
  const _QueuedUtterance({required this.item, required this.utterance});

  final VoiceOutputQueueItemMetadata item;
  final String utterance;
}

String _safeTechnicalCode(String value, {required String fallback}) {
  final normalized = value.trim();
  if (normalized.isEmpty || !RegExp(r'^[a-z0-9_.-]+$').hasMatch(normalized)) {
    return fallback;
  }
  if (normalized.runes.length <= voiceOutputQueueMaxTechnicalCodePoints) {
    return normalized;
  }
  return String.fromCharCodes(
    normalized.runes.take(voiceOutputQueueMaxTechnicalCodePoints),
  );
}
