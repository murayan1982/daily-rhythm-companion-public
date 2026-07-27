import 'dart:async';

import 'package:flutter/foundation.dart';

import 'microphone_permission.dart';

/// App-owned lifecycle phases for a bounded microphone capture request.
///
/// RT-2d provides only a deterministic fake engine. No implementation in this
/// file opens a microphone, captures audio, persists bytes, uploads content, or
/// invokes STT/provider/Framework runtime.
enum MicrophoneCapturePhase {
  idle,
  checkingPermission,
  starting,
  capturing,
  stopping,
  completed,
  cancelled,
  denied,
  permanentlyDenied,
  restricted,
  unsupported,
  timedOut,
  failed,
}

enum MicrophoneCaptureOutcome {
  started,
  completed,
  cancelled,
  denied,
  permanentlyDenied,
  restricted,
  unsupported,
  busy,
  timedOut,
  failed,
  noActiveCapture,
}

@immutable
class MicrophoneCaptureRequest {
  MicrophoneCaptureRequest({
    this.maxDuration = const Duration(seconds: 15),
    Map<String, Object?> publicMetadata = const <String, Object?>{},
  }) : publicMetadata = Map<String, Object?>.unmodifiable(publicMetadata);

  final Duration maxDuration;
  final Map<String, Object?> publicMetadata;
}

/// Opaque, provider-neutral completion data.
///
/// There is intentionally no byte buffer, filesystem path, platform handle, or
/// raw audio field. RT-2e may later supply an opaque artifact implementation.
@immutable
class MicrophoneCaptureEngineResult {
  MicrophoneCaptureEngineResult({
    required this.opaqueCaptureId,
    required this.capturedDuration,
    Map<String, Object?> publicMetadata = const <String, Object?>{},
  }) : publicMetadata = Map<String, Object?>.unmodifiable(publicMetadata);

  final String opaqueCaptureId;
  final Duration capturedDuration;
  final Map<String, Object?> publicMetadata;
}

@immutable
class MicrophoneCaptureResult {
  MicrophoneCaptureResult({
    required this.outcome,
    required this.safeMessage,
    required this.technicalCode,
    this.engineResult,
    Map<String, Object?> publicMetadata = const <String, Object?>{},
  }) : publicMetadata = Map<String, Object?>.unmodifiable(publicMetadata);

  final MicrophoneCaptureOutcome outcome;
  final String safeMessage;
  final String technicalCode;
  final MicrophoneCaptureEngineResult? engineResult;
  final Map<String, Object?> publicMetadata;

  bool get isStarted => outcome == MicrophoneCaptureOutcome.started;
  bool get isCompleted => outcome == MicrophoneCaptureOutcome.completed;
  bool get isTerminal => outcome != MicrophoneCaptureOutcome.started;
}

@immutable
class MicrophoneCaptureState {
  const MicrophoneCaptureState({
    required this.phase,
    required this.safeMessage,
    this.technicalCode,
    this.requestedMaxDuration,
    this.lastResult,
  });

  const MicrophoneCaptureState.idle()
      : this(
          phase: MicrophoneCapturePhase.idle,
          safeMessage: '音声入力は待機中です。',
        );

  final MicrophoneCapturePhase phase;
  final String safeMessage;
  final String? technicalCode;
  final Duration? requestedMaxDuration;
  final MicrophoneCaptureResult? lastResult;

  bool get isActive =>
      phase == MicrophoneCapturePhase.checkingPermission ||
      phase == MicrophoneCapturePhase.starting ||
      phase == MicrophoneCapturePhase.capturing ||
      phase == MicrophoneCapturePhase.stopping;

  bool get canStart => !isActive;
  bool get canStop => phase == MicrophoneCapturePhase.capturing;
  bool get canCancel =>
      phase == MicrophoneCapturePhase.checkingPermission ||
      phase == MicrophoneCapturePhase.starting ||
      phase == MicrophoneCapturePhase.capturing;

  String get displayPhase => phase.name.replaceAllMapped(
        RegExp(r'([A-Z])'),
        (match) => '_${match.group(1)!.toLowerCase()}',
      );
}

class MicrophoneCaptureEngineException implements Exception {
  const MicrophoneCaptureEngineException(this.code);

  final String code;

  @override
  String toString() => 'MicrophoneCaptureEngineException($code)';
}

abstract interface class MicrophoneCaptureEngine {
  bool get isCapturing;

  Future<void> start(MicrophoneCaptureRequest request);

  Future<MicrophoneCaptureEngineResult> stop();

  Future<void> cancel();

  Future<void> dispose();
}

/// Deterministic fake engine for state-machine tests.
///
/// This engine records calls only. Its public metadata always states that no
/// platform microphone was accessed and no audio was captured.
class FakeMicrophoneCaptureEngine implements MicrophoneCaptureEngine {
  FakeMicrophoneCaptureEngine({
    this.resultDuration = const Duration(seconds: 1),
    this.startError,
    this.stopError,
    this.cancelError,
    this.activateBeforeStartError = false,
  });

  final Duration resultDuration;
  final Object? startError;
  final Object? stopError;
  final Object? cancelError;
  final bool activateBeforeStartError;

  final List<MicrophoneCaptureRequest> requests = <MicrophoneCaptureRequest>[];
  int startCalls = 0;
  int stopCalls = 0;
  int cancelCalls = 0;
  int disposeCalls = 0;
  int _captureSequence = 0;
  bool _isCapturing = false;
  bool _isDisposed = false;

  @override
  bool get isCapturing => _isCapturing;

  @override
  Future<void> start(MicrophoneCaptureRequest request) async {
    startCalls += 1;
    if (_isDisposed) {
      throw const MicrophoneCaptureEngineException('fake_capture_disposed');
    }
    if (_isCapturing) {
      throw const MicrophoneCaptureEngineException('fake_capture_busy');
    }

    requests.add(request);
    if (activateBeforeStartError) {
      _isCapturing = true;
    }
    if (startError != null) {
      throw startError!;
    }
    _isCapturing = true;
  }

  @override
  Future<MicrophoneCaptureEngineResult> stop() async {
    stopCalls += 1;
    if (!_isCapturing) {
      throw const MicrophoneCaptureEngineException('fake_capture_not_active');
    }
    if (stopError != null) {
      throw stopError!;
    }

    _isCapturing = false;
    _captureSequence += 1;
    return MicrophoneCaptureEngineResult(
      opaqueCaptureId: 'fake-capture-$_captureSequence',
      capturedDuration: resultDuration,
      publicMetadata: const <String, Object?>{
        'engine': 'fake',
        'microphone_accessed': false,
        'audio_captured': false,
        'raw_audio_exposed': false,
      },
    );
  }

  @override
  Future<void> cancel() async {
    cancelCalls += 1;
    if (cancelError != null) {
      throw cancelError!;
    }
    _isCapturing = false;
  }

  @override
  Future<void> dispose() async {
    disposeCalls += 1;
    _isCapturing = false;
    _isDisposed = true;
  }
}

abstract interface class MicrophoneCaptureDeadline {
  void cancel();
}

abstract interface class MicrophoneCaptureDeadlineScheduler {
  MicrophoneCaptureDeadline schedule(
    Duration duration,
    void Function() onDeadline,
  );
}

class TimerMicrophoneCaptureDeadlineScheduler
    implements MicrophoneCaptureDeadlineScheduler {
  const TimerMicrophoneCaptureDeadlineScheduler();

  @override
  MicrophoneCaptureDeadline schedule(
    Duration duration,
    void Function() onDeadline,
  ) {
    return _TimerMicrophoneCaptureDeadline(Timer(duration, onDeadline));
  }
}

class _TimerMicrophoneCaptureDeadline implements MicrophoneCaptureDeadline {
  _TimerMicrophoneCaptureDeadline(this._timer);

  final Timer _timer;

  @override
  void cancel() => _timer.cancel();
}

class MicrophoneCaptureController extends ChangeNotifier {
  MicrophoneCaptureController({
    required MicrophonePermissionGateway permissionGateway,
    required MicrophoneCaptureEngine engine,
    MicrophoneCaptureDeadlineScheduler deadlineScheduler =
        const TimerMicrophoneCaptureDeadlineScheduler(),
    this.maximumAllowedDuration = const Duration(seconds: 60),
  })  : _permissionGateway = permissionGateway,
        _engine = engine,
        _deadlineScheduler = deadlineScheduler;

  final MicrophonePermissionGateway _permissionGateway;
  final MicrophoneCaptureEngine _engine;
  final MicrophoneCaptureDeadlineScheduler _deadlineScheduler;
  final Duration maximumAllowedDuration;

  MicrophoneCaptureState _state = const MicrophoneCaptureState.idle();
  MicrophoneCaptureDeadline? _deadline;
  int _operationSequence = 0;
  bool _isDisposed = false;
  bool _isClosed = false;

  MicrophoneCaptureState get state => _state;

  Future<MicrophoneCaptureResult> start(
    MicrophoneCaptureRequest request,
  ) async {
    if (_isClosed || _isDisposed) {
      return _result(
        MicrophoneCaptureOutcome.failed,
        '音声入力を開始できませんでした。',
        'capture_controller_closed',
      );
    }
    if (_state.isActive || _engine.isCapturing) {
      return _result(
        MicrophoneCaptureOutcome.busy,
        'すでに音声入力を実行しています。',
        'capture_busy',
      );
    }
    if (request.maxDuration <= Duration.zero) {
      final result = _result(
        MicrophoneCaptureOutcome.failed,
        '音声入力の制限時間が正しくありません。',
        'capture_duration_invalid',
      );
      _setTerminalState(MicrophoneCapturePhase.failed, result);
      return result;
    }
    if (request.maxDuration > maximumAllowedDuration) {
      final result = _result(
        MicrophoneCaptureOutcome.failed,
        '音声入力の制限時間が上限を超えています。',
        'capture_duration_exceeds_limit',
        publicMetadata: <String, Object?>{
          'maximum_duration_ms': maximumAllowedDuration.inMilliseconds,
        },
      );
      _setTerminalState(MicrophoneCapturePhase.failed, result);
      return result;
    }

    final operation = ++_operationSequence;
    _setState(
      MicrophoneCaptureState(
        phase: MicrophoneCapturePhase.checkingPermission,
        safeMessage: 'マイクの利用許可を確認しています。',
        requestedMaxDuration: request.maxDuration,
      ),
    );

    MicrophonePermissionResult permission;
    try {
      permission = await _permissionGateway.checkPermission();
    } catch (_) {
      if (!_isCurrent(operation)) {
        return _supersededResult();
      }
      final result = _result(
        MicrophoneCaptureOutcome.failed,
        'マイク権限の確認に失敗しました。',
        'capture_permission_check_failed',
      );
      _setTerminalState(MicrophoneCapturePhase.failed, result);
      return result;
    }

    if (!_isCurrent(operation)) {
      return _supersededResult();
    }

    final blocked = _permissionBlockedResult(permission);
    if (blocked != null) {
      _setTerminalState(_phaseForOutcome(blocked.outcome), blocked);
      return blocked;
    }

    _setState(
      MicrophoneCaptureState(
        phase: MicrophoneCapturePhase.starting,
        safeMessage: '音声入力を開始しています。',
        requestedMaxDuration: request.maxDuration,
      ),
    );

    try {
      await _engine.start(request);
    } catch (error) {
      final cleanupSucceeded = await _safeCancelEngine();
      if (!_isCurrent(operation)) {
        return _supersededResult();
      }
      final result = _result(
        MicrophoneCaptureOutcome.failed,
        '音声入力を開始できませんでした。',
        _engineCode(error, 'capture_start_failed'),
        publicMetadata: <String, Object?>{
          'cleanup_succeeded': cleanupSucceeded,
        },
      );
      _setTerminalState(MicrophoneCapturePhase.failed, result);
      return result;
    }

    if (!_isCurrent(operation)) {
      await _safeCancelEngine();
      return _supersededResult();
    }

    _deadline = _deadlineScheduler.schedule(
      request.maxDuration,
      () => unawaited(_handleDeadline(operation)),
    );
    final result = _result(
      MicrophoneCaptureOutcome.started,
      '音声入力を実行しています。',
      'capture_started',
      publicMetadata: <String, Object?>{
        'max_duration_ms': request.maxDuration.inMilliseconds,
      },
    );
    _setState(
      MicrophoneCaptureState(
        phase: MicrophoneCapturePhase.capturing,
        safeMessage: result.safeMessage,
        technicalCode: result.technicalCode,
        requestedMaxDuration: request.maxDuration,
        lastResult: result,
      ),
    );
    return result;
  }

  Future<MicrophoneCaptureResult> stop() async {
    if (_state.phase != MicrophoneCapturePhase.capturing) {
      return _result(
        MicrophoneCaptureOutcome.noActiveCapture,
        '停止できる音声入力はありません。',
        'capture_not_active',
      );
    }

    final operation = ++_operationSequence;
    _cancelDeadline();
    _setState(
      MicrophoneCaptureState(
        phase: MicrophoneCapturePhase.stopping,
        safeMessage: '音声入力を停止しています。',
        requestedMaxDuration: _state.requestedMaxDuration,
      ),
    );

    try {
      final engineResult = await _engine.stop();
      if (!_isCurrent(operation)) {
        return _supersededResult();
      }
      final result = _result(
        MicrophoneCaptureOutcome.completed,
        '音声入力を停止しました。',
        'capture_completed',
        engineResult: engineResult,
        publicMetadata: const <String, Object?>{
          'microphone_accessed': false,
          'audio_captured': false,
          'raw_audio_exposed': false,
        },
      );
      _setTerminalState(MicrophoneCapturePhase.completed, result);
      return result;
    } catch (error) {
      final cleanupSucceeded = await _safeCancelEngine();
      if (!_isCurrent(operation)) {
        return _supersededResult();
      }
      final result = _result(
        MicrophoneCaptureOutcome.failed,
        '音声入力の停止処理に失敗しました。',
        _engineCode(error, 'capture_stop_failed'),
        publicMetadata: <String, Object?>{
          'cleanup_succeeded': cleanupSucceeded,
        },
      );
      _setTerminalState(MicrophoneCapturePhase.failed, result);
      return result;
    }
  }

  Future<MicrophoneCaptureResult> cancel() async {
    if (!_state.isActive && !_engine.isCapturing) {
      return _result(
        MicrophoneCaptureOutcome.noActiveCapture,
        'キャンセルできる音声入力はありません。',
        'capture_not_active',
      );
    }

    ++_operationSequence;
    _cancelDeadline();
    final cleanupSucceeded = await _safeCancelEngine();
    final result = _result(
      cleanupSucceeded
          ? MicrophoneCaptureOutcome.cancelled
          : MicrophoneCaptureOutcome.failed,
      cleanupSucceeded
          ? '音声入力をキャンセルしました。'
          : '音声入力のキャンセル処理に失敗しました。',
      cleanupSucceeded ? 'capture_cancelled' : 'capture_cancel_cleanup_failed',
      publicMetadata: <String, Object?>{
        'cleanup_succeeded': cleanupSucceeded,
      },
    );
    _setTerminalState(
      cleanupSucceeded
          ? MicrophoneCapturePhase.cancelled
          : MicrophoneCapturePhase.failed,
      result,
    );
    return result;
  }

  Future<void> reset() async {
    if (_state.isActive || _engine.isCapturing) {
      await cancel();
    }
    if (_isClosed || _isDisposed) {
      return;
    }
    _setState(const MicrophoneCaptureState.idle());
  }

  Future<void> close() async {
    if (_isClosed) {
      return;
    }
    _isClosed = true;
    ++_operationSequence;
    _cancelDeadline();
    if (_state.isActive || _engine.isCapturing) {
      await _safeCancelEngine();
    }
    await _engine.dispose();
  }

  Future<void> _handleDeadline(int operation) async {
    if (!_isCurrent(operation) ||
        _state.phase != MicrophoneCapturePhase.capturing) {
      return;
    }

    ++_operationSequence;
    _cancelDeadline();
    final cleanupSucceeded = await _safeCancelEngine();
    if (_isDisposed) {
      return;
    }
    final result = _result(
      MicrophoneCaptureOutcome.timedOut,
      '音声入力は制限時間に達したため停止しました。',
      cleanupSucceeded ? 'capture_timed_out' : 'capture_timeout_cleanup_failed',
      publicMetadata: <String, Object?>{
        'cleanup_succeeded': cleanupSucceeded,
      },
    );
    _setTerminalState(MicrophoneCapturePhase.timedOut, result);
  }

  MicrophoneCaptureResult? _permissionBlockedResult(
    MicrophonePermissionResult permission,
  ) {
    switch (permission.status) {
      case MicrophonePermissionStatus.granted:
        return null;
      case MicrophonePermissionStatus.denied:
        return _result(
          MicrophoneCaptureOutcome.denied,
          'マイクの利用が許可されていません。',
          'capture_permission_denied',
        );
      case MicrophonePermissionStatus.permanentlyDenied:
        return _result(
          MicrophoneCaptureOutcome.permanentlyDenied,
          'マイクの利用が無効です。端末設定から許可してください。',
          'capture_permission_permanently_denied',
          publicMetadata: const <String, Object?>{'can_open_settings': true},
        );
      case MicrophonePermissionStatus.restricted:
        return _result(
          MicrophoneCaptureOutcome.restricted,
          'この端末ではマイクの利用が制限されています。',
          'capture_permission_restricted',
        );
      case MicrophonePermissionStatus.unsupported:
        return _result(
          MicrophoneCaptureOutcome.unsupported,
          'この環境では音声入力を利用できません。',
          'capture_permission_unsupported',
        );
      case MicrophonePermissionStatus.unknown:
        return _result(
          MicrophoneCaptureOutcome.failed,
          'マイクの利用許可を確認できませんでした。',
          'capture_permission_unknown',
        );
      case MicrophonePermissionStatus.failed:
        return _result(
          MicrophoneCaptureOutcome.failed,
          'マイク権限の確認に失敗しました。',
          'capture_permission_failed',
        );
    }
  }

  MicrophoneCapturePhase _phaseForOutcome(MicrophoneCaptureOutcome outcome) {
    switch (outcome) {
      case MicrophoneCaptureOutcome.denied:
        return MicrophoneCapturePhase.denied;
      case MicrophoneCaptureOutcome.permanentlyDenied:
        return MicrophoneCapturePhase.permanentlyDenied;
      case MicrophoneCaptureOutcome.restricted:
        return MicrophoneCapturePhase.restricted;
      case MicrophoneCaptureOutcome.unsupported:
        return MicrophoneCapturePhase.unsupported;
      case MicrophoneCaptureOutcome.timedOut:
        return MicrophoneCapturePhase.timedOut;
      case MicrophoneCaptureOutcome.cancelled:
        return MicrophoneCapturePhase.cancelled;
      case MicrophoneCaptureOutcome.completed:
        return MicrophoneCapturePhase.completed;
      case MicrophoneCaptureOutcome.started:
        return MicrophoneCapturePhase.capturing;
      case MicrophoneCaptureOutcome.busy:
      case MicrophoneCaptureOutcome.failed:
      case MicrophoneCaptureOutcome.noActiveCapture:
        return MicrophoneCapturePhase.failed;
    }
  }

  Future<bool> _safeCancelEngine() async {
    if (!_engine.isCapturing) {
      return true;
    }
    try {
      await _engine.cancel();
      return true;
    } catch (_) {
      return false;
    }
  }

  void _cancelDeadline() {
    _deadline?.cancel();
    _deadline = null;
  }

  bool _isCurrent(int operation) =>
      !_isDisposed && !_isClosed && operation == _operationSequence;

  String _engineCode(Object error, String fallback) {
    return error is MicrophoneCaptureEngineException ? error.code : fallback;
  }

  MicrophoneCaptureResult _supersededResult() {
    return _result(
      MicrophoneCaptureOutcome.cancelled,
      '音声入力の開始処理はキャンセルされました。',
      'capture_operation_superseded',
    );
  }

  MicrophoneCaptureResult _result(
    MicrophoneCaptureOutcome outcome,
    String safeMessage,
    String technicalCode, {
    MicrophoneCaptureEngineResult? engineResult,
    Map<String, Object?> publicMetadata = const <String, Object?>{},
  }) {
    return MicrophoneCaptureResult(
      outcome: outcome,
      safeMessage: safeMessage,
      technicalCode: technicalCode,
      engineResult: engineResult,
      publicMetadata: <String, Object?>{
        ...publicMetadata,
        'microphone_accessed': false,
        'audio_captured': false,
        'raw_audio_exposed': false,
      },
    );
  }

  void _setTerminalState(
    MicrophoneCapturePhase phase,
    MicrophoneCaptureResult result,
  ) {
    _setState(
      MicrophoneCaptureState(
        phase: phase,
        safeMessage: result.safeMessage,
        technicalCode: result.technicalCode,
        lastResult: result,
      ),
    );
  }

  void _setState(MicrophoneCaptureState nextState) {
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
    unawaited(close());
    super.dispose();
  }
}
