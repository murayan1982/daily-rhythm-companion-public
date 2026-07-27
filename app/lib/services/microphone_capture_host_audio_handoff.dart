import 'package:flutter/foundation.dart';

import 'microphone_capture.dart';
import 'record_microphone_capture_engine.dart';

/// App-owned lifecycle phases for a completed microphone artifact handoff.
///
/// RT-3b is a fake-only contract. This file does not upload audio, import the
/// Framework, execute a provider, or perform STT.
enum HostAudioHandoffPhase {
  idle,
  retained,
  consuming,
  completed,
  cancelled,
  discarded,
  failed,
  closed,
}

enum HostAudioHandoffOutcome {
  retained,
  completed,
  cancelled,
  discarded,
  invalidCapture,
  artifactUnavailable,
  noRetainedArtifact,
  busy,
  cleanupFailed,
  failed,
  closed,
}

@immutable
class HostAudioHandoffDescriptor {
  HostAudioHandoffDescriptor({
    required this.capturedDuration,
    required this.maximumDuration,
    required this.encoding,
    required this.sampleRateHz,
    required this.channelCount,
    this.language,
    Map<String, Object?> publicMetadata = const <String, Object?>{},
  }) : publicMetadata = Map<String, Object?>.unmodifiable(publicMetadata);

  final Duration capturedDuration;
  final Duration maximumDuration;
  final String encoding;
  final int sampleRateHz;
  final int channelCount;
  final String? language;
  final Map<String, Object?> publicMetadata;
}

@immutable
class HostAudioHandoffConsumerResult {
  HostAudioHandoffConsumerResult({
    required this.completed,
    required this.technicalCode,
    required this.safeMessage,
    this.retryable = false,
    Map<String, Object?> publicMetadata = const <String, Object?>{},
  }) : publicMetadata = Map<String, Object?>.unmodifiable(publicMetadata);

  factory HostAudioHandoffConsumerResult.completed({
    String technicalCode = 'host_audio_consumer_completed',
    String safeMessage = '音声データの受け渡し処理が完了しました。',
    Map<String, Object?> publicMetadata = const <String, Object?>{},
  }) {
    return HostAudioHandoffConsumerResult(
      completed: true,
      technicalCode: technicalCode,
      safeMessage: safeMessage,
      publicMetadata: publicMetadata,
    );
  }

  factory HostAudioHandoffConsumerResult.failed({
    String technicalCode = 'host_audio_consumer_failed',
    String safeMessage = '音声データの受け渡し処理に失敗しました。',
    bool retryable = false,
    Map<String, Object?> publicMetadata = const <String, Object?>{},
  }) {
    return HostAudioHandoffConsumerResult(
      completed: false,
      technicalCode: technicalCode,
      safeMessage: safeMessage,
      retryable: retryable,
      publicMetadata: publicMetadata,
    );
  }

  final bool completed;
  final String technicalCode;
  final String safeMessage;
  final bool retryable;
  final Map<String, Object?> publicMetadata;
}

@immutable
class HostAudioHandoffResult {
  HostAudioHandoffResult({
    required this.outcome,
    required this.technicalCode,
    required this.safeMessage,
    this.descriptor,
    this.consumerInvoked = false,
    this.privateArtifactDiscarded = false,
    this.cleanupSucceeded = false,
    this.retryable = false,
    Map<String, Object?> publicMetadata = const <String, Object?>{},
  }) : publicMetadata = Map<String, Object?>.unmodifiable(publicMetadata);

  final HostAudioHandoffOutcome outcome;
  final String technicalCode;
  final String safeMessage;
  final HostAudioHandoffDescriptor? descriptor;
  final bool consumerInvoked;
  final bool privateArtifactDiscarded;
  final bool cleanupSucceeded;
  final bool retryable;
  final Map<String, Object?> publicMetadata;

  bool get isCompleted => outcome == HostAudioHandoffOutcome.completed;
  bool get isRetained => outcome == HostAudioHandoffOutcome.retained;
}

@immutable
class HostAudioHandoffState {
  const HostAudioHandoffState({
    required this.phase,
    required this.safeMessage,
    this.technicalCode,
    this.lastResult,
  });

  const HostAudioHandoffState.idle()
      : this(
          phase: HostAudioHandoffPhase.idle,
          safeMessage: '音声データの受け渡しは待機中です。',
        );

  final HostAudioHandoffPhase phase;
  final String safeMessage;
  final String? technicalCode;
  final HostAudioHandoffResult? lastResult;

  bool get hasRetainedArtifact => phase == HostAudioHandoffPhase.retained;
  bool get isActive => phase == HostAudioHandoffPhase.consuming;
}

class HostAudioHandoffException implements Exception {
  const HostAudioHandoffException(this.code);

  final String code;

  @override
  String toString() => 'HostAudioHandoffException($code)';
}

/// Scoped app-internal access to one retained private capture artifact.
///
/// The private path has no getter and is never copied into a public result,
/// metadata, log, UI state, or API payload. A future app-owned staging consumer
/// may use [withPrivateArtifactPath] only while [HostAudioHandoffConsumer.consume]
/// is active. RT-3b fake tests do not read audio or perform network I/O.
class HostAudioPrivateArtifactLease {
  HostAudioPrivateArtifactLease._({
    required String opaqueCaptureId,
    required RecordMicrophoneCapturePrivateArtifactAccess privateArtifactAccess,
    required this.descriptor,
  })  : _opaqueCaptureId = opaqueCaptureId,
        _privateArtifactAccess = privateArtifactAccess;

  final String _opaqueCaptureId;
  final RecordMicrophoneCapturePrivateArtifactAccess _privateArtifactAccess;
  final HostAudioHandoffDescriptor descriptor;

  bool _consumerAccessOpen = false;
  bool _discarded = false;

  bool get isDiscarded => _discarded;

  Future<T> withPrivateArtifactPath<T>(
    Future<T> Function(String privatePath) action,
  ) async {
    if (!_consumerAccessOpen || _discarded) {
      throw const HostAudioHandoffException(
        'host_audio_private_artifact_access_not_active',
      );
    }

    final privatePath =
        _privateArtifactAccess.resolvePrivateArtifactPath(_opaqueCaptureId);
    if (privatePath == null || privatePath.isEmpty) {
      throw const HostAudioHandoffException(
        'host_audio_private_artifact_unavailable',
      );
    }
    return action(privatePath);
  }

  bool _isAvailable() {
    final privatePath =
        _privateArtifactAccess.resolvePrivateArtifactPath(_opaqueCaptureId);
    return !_discarded && privatePath != null && privatePath.isNotEmpty;
  }

  void _openConsumerAccess() {
    if (_discarded) {
      throw const HostAudioHandoffException(
        'host_audio_private_artifact_discarded',
      );
    }
    _consumerAccessOpen = true;
  }

  void _closeConsumerAccess() {
    _consumerAccessOpen = false;
  }

  Future<bool> _discard() async {
    _consumerAccessOpen = false;
    if (_discarded) {
      return true;
    }
    bool discarded;
    try {
      discarded = await _privateArtifactAccess.discardPrivateArtifact(
        _opaqueCaptureId,
      );
    } catch (_) {
      return false;
    }
    if (discarded) {
      _discarded = true;
    }
    return discarded;
  }
}

abstract interface class HostAudioHandoffConsumer {
  Future<HostAudioHandoffConsumerResult> consume(
    HostAudioPrivateArtifactLease lease,
  );

  Future<void> cancel();

  Future<void> dispose();
}

/// Deterministic fake consumer used by RT-3b tests.
///
/// It records only public descriptors. It does not resolve a private path, read
/// audio, upload data, import Framework code, execute a provider, or run STT.
class FakeHostAudioHandoffConsumer implements HostAudioHandoffConsumer {
  FakeHostAudioHandoffConsumer({
    HostAudioHandoffConsumerResult? result,
    this.consumeError,
    this.cancelError,
    this.disposeError,
  }) : result = result ?? HostAudioHandoffConsumerResult.completed();

  final HostAudioHandoffConsumerResult result;
  final Object? consumeError;
  final Object? cancelError;
  final Object? disposeError;

  final List<HostAudioHandoffDescriptor> descriptors =
      <HostAudioHandoffDescriptor>[];
  int consumeCalls = 0;
  int cancelCalls = 0;
  int disposeCalls = 0;

  @override
  Future<HostAudioHandoffConsumerResult> consume(
    HostAudioPrivateArtifactLease lease,
  ) async {
    consumeCalls += 1;
    descriptors.add(lease.descriptor);
    if (consumeError != null) {
      throw consumeError!;
    }
    return result;
  }

  @override
  Future<void> cancel() async {
    cancelCalls += 1;
    if (cancelError != null) {
      throw cancelError!;
    }
  }

  @override
  Future<void> dispose() async {
    disposeCalls += 1;
    if (disposeError != null) {
      throw disposeError!;
    }
  }
}

/// Coordinates retain, consume, cancel, discard, and close semantics for one
/// completed app-owned microphone artifact.
///
/// The controller retains only the opaque capture identity internally. It never
/// returns the opaque ID or private path through [HostAudioHandoffResult].
class HostAudioHandoffController extends ChangeNotifier {
  HostAudioHandoffController({
    required RecordMicrophoneCapturePrivateArtifactAccess privateArtifactAccess,
    required HostAudioHandoffConsumer consumer,
    this.maximumAllowedDuration = const Duration(seconds: 15),
  })  : _privateArtifactAccess = privateArtifactAccess,
        _consumer = consumer;

  static const Set<String> _allowedPublicMetadataKeys = <String>{
    'capture_owner',
    'host_app',
    'input_mode',
    'operator_target',
    'private_artifact_cleanup_required',
    'raw_audio_exposed',
  };

  final RecordMicrophoneCapturePrivateArtifactAccess _privateArtifactAccess;
  final HostAudioHandoffConsumer _consumer;
  final Duration maximumAllowedDuration;

  HostAudioHandoffState _state = const HostAudioHandoffState.idle();
  HostAudioPrivateArtifactLease? _lease;
  bool _operationInFlight = false;
  bool _closed = false;
  int _operationSequence = 0;

  HostAudioHandoffState get state => _state;
  bool get isClosed => _closed;

  Future<HostAudioHandoffResult> retain(
    MicrophoneCaptureResult captureResult, {
    String? language,
    Duration? maximumDuration,
    Map<String, Object?> publicMetadata = const <String, Object?>{},
  }) async {
    if (_closed) {
      return _setResult(_closedResult());
    }
    if (_operationInFlight || _lease != null) {
      return _setResult(_busyResult());
    }

    final engineResult = captureResult.engineResult;
    if (!captureResult.isCompleted || engineResult == null) {
      return _setResult(
        _failureResult(
          HostAudioHandoffOutcome.invalidCapture,
          'host_audio_capture_not_completed',
          '完了した音声データがありません。',
        ),
      );
    }

    final requestedMaximumDuration = maximumDuration ?? maximumAllowedDuration;
    if (requestedMaximumDuration <= Duration.zero ||
        requestedMaximumDuration > maximumAllowedDuration ||
        engineResult.capturedDuration <= Duration.zero ||
        engineResult.capturedDuration > requestedMaximumDuration) {
      return _setResult(
        _failureResult(
          HostAudioHandoffOutcome.invalidCapture,
          'host_audio_capture_duration_invalid',
          '音声データの時間情報が無効です。',
        ),
      );
    }

    final opaqueCaptureId = engineResult.opaqueCaptureId.trim();
    if (opaqueCaptureId.isEmpty) {
      return _setResult(
        _failureResult(
          HostAudioHandoffOutcome.invalidCapture,
          'host_audio_capture_id_invalid',
          '音声データを識別できません。',
        ),
      );
    }

    final engineMetadata = engineResult.publicMetadata;
    final encoding = engineMetadata['encoding'];
    final sampleRateHz = engineMetadata['sample_rate_hz'];
    final channelCount = engineMetadata['channels'];
    if (encoding is! String ||
        encoding.trim().toLowerCase() != 'wav' ||
        sampleRateHz is! int ||
        sampleRateHz != 16000 ||
        channelCount is! int ||
        channelCount != 1) {
      return _setResult(
        _failureResult(
          HostAudioHandoffOutcome.invalidCapture,
          'host_audio_format_invalid',
          '音声データの形式情報が無効です。',
        ),
      );
    }

    final descriptor = HostAudioHandoffDescriptor(
      capturedDuration: engineResult.capturedDuration,
      maximumDuration: requestedMaximumDuration,
      encoding: encoding.trim().toLowerCase(),
      sampleRateHz: sampleRateHz,
      channelCount: channelCount,
      language: language,
      publicMetadata: _safePublicMetadata(publicMetadata),
    );
    final lease = HostAudioPrivateArtifactLease._(
      opaqueCaptureId: opaqueCaptureId,
      privateArtifactAccess: _privateArtifactAccess,
      descriptor: descriptor,
    );
    if (!lease._isAvailable()) {
      return _setResult(
        _failureResult(
          HostAudioHandoffOutcome.artifactUnavailable,
          'host_audio_private_artifact_unavailable',
          '音声データを利用できません。',
          descriptor: descriptor,
        ),
      );
    }

    _lease = lease;
    return _setResult(
      HostAudioHandoffResult(
        outcome: HostAudioHandoffOutcome.retained,
        technicalCode: 'host_audio_artifact_retained',
        safeMessage: '音声データを一時的に保持しました。',
        descriptor: descriptor,
        publicMetadata: const <String, Object?>{
          'private_artifact_retained': true,
          'private_path_exposed': false,
          'opaque_capture_id_exposed': false,
          'audio_uploaded': false,
          'stt_executed': false,
        },
      ),
      phase: HostAudioHandoffPhase.retained,
    );
  }

  Future<HostAudioHandoffResult> consume() async {
    if (_closed) {
      return _setResult(_closedResult());
    }
    if (_operationInFlight) {
      return _setResult(_busyResult());
    }
    final lease = _lease;
    if (lease == null) {
      return _setResult(_noArtifactResult());
    }

    _operationInFlight = true;
    final operation = ++_operationSequence;
    _setPhase(
      HostAudioHandoffPhase.consuming,
      '音声データの受け渡し処理中です。',
      'host_audio_consumer_in_progress',
    );

    HostAudioHandoffConsumerResult consumerResult;
    try {
      lease._openConsumerAccess();
      consumerResult = await _consumer.consume(lease);
    } catch (_) {
      consumerResult = HostAudioHandoffConsumerResult.failed(
        technicalCode: 'host_audio_consumer_exception',
      );
    } finally {
      lease._closeConsumerAccess();
    }

    final discarded = await _discardLease(lease);
    _operationInFlight = false;
    if (!_isCurrent(operation)) {
      return _closedResult();
    }
    if (!discarded) {
      return _setResult(
        HostAudioHandoffResult(
          outcome: HostAudioHandoffOutcome.cleanupFailed,
          technicalCode: 'host_audio_private_artifact_discard_failed',
          safeMessage: '音声データの削除に失敗しました。',
          descriptor: lease.descriptor,
          consumerInvoked: true,
          privateArtifactDiscarded: false,
          cleanupSucceeded: false,
          retryable: true,
          publicMetadata: const <String, Object?>{
            'private_path_exposed': false,
            'opaque_capture_id_exposed': false,
            'audio_uploaded': false,
            'stt_executed': false,
          },
        ),
        phase: HostAudioHandoffPhase.failed,
      );
    }

    if (!consumerResult.completed) {
      return _setResult(
        HostAudioHandoffResult(
          outcome: HostAudioHandoffOutcome.failed,
          technicalCode: _safeTechnicalCode(
            consumerResult.technicalCode,
            fallback: 'host_audio_consumer_failed',
          ),
          safeMessage: '音声データの受け渡し処理に失敗しました。',
          descriptor: lease.descriptor,
          consumerInvoked: true,
          privateArtifactDiscarded: true,
          cleanupSucceeded: true,
          retryable: consumerResult.retryable,
          publicMetadata: <String, Object?>{
            ..._safePublicMetadata(consumerResult.publicMetadata),
            'private_path_exposed': false,
            'opaque_capture_id_exposed': false,
            'audio_uploaded': false,
            'stt_executed': false,
          },
        ),
        phase: HostAudioHandoffPhase.failed,
      );
    }

    return _setResult(
      HostAudioHandoffResult(
        outcome: HostAudioHandoffOutcome.completed,
        technicalCode: _safeTechnicalCode(
          consumerResult.technicalCode,
          fallback: 'host_audio_consumer_completed',
        ),
        safeMessage: '音声データの受け渡し処理が完了しました。',
        descriptor: lease.descriptor,
        consumerInvoked: true,
        privateArtifactDiscarded: true,
        cleanupSucceeded: true,
        publicMetadata: <String, Object?>{
          ..._safePublicMetadata(consumerResult.publicMetadata),
          'private_path_exposed': false,
          'opaque_capture_id_exposed': false,
          'audio_uploaded': false,
          'stt_executed': false,
        },
      ),
      phase: HostAudioHandoffPhase.completed,
    );
  }

  Future<HostAudioHandoffResult> discard() async {
    if (_closed) {
      return _setResult(_closedResult());
    }
    if (_operationInFlight) {
      return _setResult(_busyResult());
    }
    final lease = _lease;
    if (lease == null) {
      return _setResult(_noArtifactResult());
    }

    final discarded = await _discardLease(lease);
    if (!discarded) {
      return _setResult(
        _failureResult(
          HostAudioHandoffOutcome.cleanupFailed,
          'host_audio_private_artifact_discard_failed',
          '音声データの削除に失敗しました。',
          descriptor: lease.descriptor,
          retryable: true,
        ),
        phase: HostAudioHandoffPhase.failed,
      );
    }

    return _setResult(
      HostAudioHandoffResult(
        outcome: HostAudioHandoffOutcome.discarded,
        technicalCode: 'host_audio_private_artifact_discarded',
        safeMessage: '音声データを削除しました。',
        descriptor: lease.descriptor,
        privateArtifactDiscarded: true,
        cleanupSucceeded: true,
        publicMetadata: const <String, Object?>{
          'private_path_exposed': false,
          'opaque_capture_id_exposed': false,
          'audio_uploaded': false,
          'stt_executed': false,
        },
      ),
      phase: HostAudioHandoffPhase.discarded,
    );
  }

  Future<HostAudioHandoffResult> cancel() async {
    if (_closed) {
      return _setResult(_closedResult());
    }
    if (_operationInFlight) {
      return _setResult(_busyResult());
    }
    final lease = _lease;
    if (lease == null) {
      return _setResult(_noArtifactResult());
    }

    var consumerCancelled = true;
    try {
      await _consumer.cancel();
    } catch (_) {
      consumerCancelled = false;
    }
    final discarded = await _discardLease(lease);
    if (!discarded) {
      return _setResult(
        _failureResult(
          HostAudioHandoffOutcome.cleanupFailed,
          'host_audio_cancel_cleanup_failed',
          '音声データのキャンセル処理に失敗しました。',
          descriptor: lease.descriptor,
          retryable: true,
          publicMetadata: <String, Object?>{
            'consumer_cancelled': consumerCancelled,
          },
        ),
        phase: HostAudioHandoffPhase.failed,
      );
    }

    return _setResult(
      HostAudioHandoffResult(
        outcome: HostAudioHandoffOutcome.cancelled,
        technicalCode: consumerCancelled
            ? 'host_audio_handoff_cancelled'
            : 'host_audio_consumer_cancel_failed_artifact_discarded',
        safeMessage: '音声データの受け渡しをキャンセルしました。',
        descriptor: lease.descriptor,
        privateArtifactDiscarded: true,
        cleanupSucceeded: true,
        publicMetadata: <String, Object?>{
          'consumer_cancelled': consumerCancelled,
          'private_path_exposed': false,
          'opaque_capture_id_exposed': false,
          'audio_uploaded': false,
          'stt_executed': false,
        },
      ),
      phase: HostAudioHandoffPhase.cancelled,
    );
  }

  Future<void> close() async {
    if (_closed) {
      return;
    }

    _closed = true;
    ++_operationSequence;
    final lease = _lease;
    try {
      await _consumer.cancel();
    } catch (_) {
      // Close continues to private-artifact cleanup.
    }
    if (lease != null) {
      await _discardLease(lease);
    }
    try {
      await _consumer.dispose();
    } catch (_) {
      // Public close remains idempotent and does not expose consumer payloads.
    }
    _operationInFlight = false;
    _lease = null;
    _setPhase(
      HostAudioHandoffPhase.closed,
      '音声データの受け渡しを終了しました。',
      'host_audio_handoff_closed',
    );
  }

  Future<void> disposeAsync() => close();

  Future<bool> _discardLease(HostAudioPrivateArtifactLease lease) async {
    final discarded = await lease._discard();
    if (discarded && identical(_lease, lease)) {
      _lease = null;
    }
    return discarded;
  }

  HostAudioHandoffResult _setResult(
    HostAudioHandoffResult result, {
    HostAudioHandoffPhase? phase,
  }) {
    _state = HostAudioHandoffState(
      phase: phase ?? _phaseForOutcome(result.outcome),
      safeMessage: result.safeMessage,
      technicalCode: result.technicalCode,
      lastResult: result,
    );
    notifyListeners();
    return result;
  }

  void _setPhase(
    HostAudioHandoffPhase phase,
    String safeMessage,
    String technicalCode,
  ) {
    _state = HostAudioHandoffState(
      phase: phase,
      safeMessage: safeMessage,
      technicalCode: technicalCode,
      lastResult: _state.lastResult,
    );
    notifyListeners();
  }

  HostAudioHandoffResult _failureResult(
    HostAudioHandoffOutcome outcome,
    String technicalCode,
    String safeMessage, {
    HostAudioHandoffDescriptor? descriptor,
    bool retryable = false,
    Map<String, Object?> publicMetadata = const <String, Object?>{},
  }) {
    return HostAudioHandoffResult(
      outcome: outcome,
      technicalCode: technicalCode,
      safeMessage: safeMessage,
      descriptor: descriptor,
      retryable: retryable,
      publicMetadata: <String, Object?>{
        ..._safePublicMetadata(publicMetadata),
        'private_path_exposed': false,
        'opaque_capture_id_exposed': false,
        'audio_uploaded': false,
        'stt_executed': false,
      },
    );
  }

  HostAudioHandoffResult _busyResult() => _failureResult(
        HostAudioHandoffOutcome.busy,
        'host_audio_handoff_busy',
        '別の音声データを処理中です。',
        descriptor: _lease?.descriptor,
        retryable: true,
      );

  HostAudioHandoffResult _noArtifactResult() => _failureResult(
        HostAudioHandoffOutcome.noRetainedArtifact,
        'host_audio_no_retained_artifact',
        '保持中の音声データがありません。',
      );

  HostAudioHandoffResult _closedResult() => _failureResult(
        HostAudioHandoffOutcome.closed,
        'host_audio_handoff_closed',
        '音声データの受け渡しは終了しています。',
      );

  HostAudioHandoffPhase _phaseForOutcome(HostAudioHandoffOutcome outcome) {
    return switch (outcome) {
      HostAudioHandoffOutcome.retained => HostAudioHandoffPhase.retained,
      HostAudioHandoffOutcome.completed => HostAudioHandoffPhase.completed,
      HostAudioHandoffOutcome.cancelled => HostAudioHandoffPhase.cancelled,
      HostAudioHandoffOutcome.discarded => HostAudioHandoffPhase.discarded,
      HostAudioHandoffOutcome.closed => HostAudioHandoffPhase.closed,
      _ => HostAudioHandoffPhase.failed,
    };
  }

  String _safeTechnicalCode(
    String value, {
    required String fallback,
  }) {
    final normalized = value.trim().toLowerCase();
    if (normalized.isEmpty ||
        normalized.length > 80 ||
        !RegExp(r'^[a-z0-9_]+$').hasMatch(normalized)) {
      return fallback;
    }
    return normalized;
  }

  bool _isCurrent(int operation) =>
      !_closed && operation == _operationSequence;

  Map<String, Object?> _safePublicMetadata(Map<String, Object?> values) {
    final safe = <String, Object?>{};
    for (final entry in values.entries) {
      if (_allowedPublicMetadataKeys.contains(entry.key)) {
        safe[entry.key] = entry.value;
      }
    }
    return Map<String, Object?>.unmodifiable(safe);
  }
}
