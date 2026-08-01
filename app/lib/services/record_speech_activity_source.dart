import 'dart:async';
import 'dart:typed_data';

import 'package:record/record.dart';

import 'speech_activity_source.dart';

const RecordConfig recordSpeechActivityRecordConfig = RecordConfig(
  encoder: AudioEncoder.pcm16bits,
  sampleRate: 16000,
  numChannels: 1,
  autoGain: true,
  echoCancel: true,
  noiseSuppress: true,
  audioInterruption: AudioInterruptionMode.none,
);

abstract interface class RecordSpeechActivityDriver {
  Stream<double> get amplitudeDbfs;

  Future<void> start({required Duration sampleInterval});

  Future<void> stop();

  Future<void> dispose();
}

/// package:record 6.2.1 production driver.
///
/// PCM16 bytes are drained immediately and are never retained, logged, exposed,
/// or persisted. Only package-provided dBFS amplitude samples cross into the
/// bounded speech-activity state machine.
class RecordPackageSpeechActivityDriver
    implements RecordSpeechActivityDriver {
  RecordPackageSpeechActivityDriver({AudioRecorder? recorder})
    : _recorder = recorder ?? AudioRecorder();

  final AudioRecorder _recorder;
  final StreamController<double> _amplitudes =
      StreamController<double>.broadcast(sync: true);

  StreamSubscription<Uint8List>? _pcmSubscription;
  StreamSubscription<Amplitude>? _amplitudeSubscription;
  bool _started = false;
  bool _disposed = false;

  @override
  Stream<double> get amplitudeDbfs => _amplitudes.stream;

  @override
  Future<void> start({required Duration sampleInterval}) async {
    if (_disposed) {
      throw StateError('record_speech_activity_driver_disposed');
    }
    if (_started) {
      throw StateError('record_speech_activity_driver_busy');
    }

    try {
      final pcmStream = await _recorder.startStream(
        recordSpeechActivityRecordConfig,
      );
      _pcmSubscription = pcmStream.listen(
        (_) {
          // Intentionally drain and drop every chunk.
        },
        onError: _forwardError,
      );
      _amplitudeSubscription = _recorder
          .onAmplitudeChanged(sampleInterval)
          .listen(
            (amplitude) => _amplitudes.add(amplitude.current),
            onError: _forwardError,
          );
      _started = true;
    } catch (_) {
      await _cancelSubscriptions();
      try {
        await _recorder.cancel();
      } catch (_) {
        // Fail closed without exposing a package/platform exception.
      }
      rethrow;
    }
  }

  void _forwardError(Object error, StackTrace stackTrace) {
    if (!_amplitudes.isClosed) {
      _amplitudes.addError(error, stackTrace);
    }
  }

  @override
  Future<void> stop() async {
    if (!_started) {
      return;
    }
    _started = false;
    await _cancelSubscriptions();
    await _recorder.stop();
  }

  Future<void> _cancelSubscriptions() async {
    final pcmSubscription = _pcmSubscription;
    _pcmSubscription = null;
    await pcmSubscription?.cancel();

    final amplitudeSubscription = _amplitudeSubscription;
    _amplitudeSubscription = null;
    await amplitudeSubscription?.cancel();
  }

  @override
  Future<void> dispose() async {
    if (_disposed) {
      return;
    }
    _disposed = true;
    try {
      await stop();
    } catch (_) {
      // Continue to recorder disposal.
    }
    await _recorder.dispose();
    await _amplitudes.close();
  }
}

/// Bounded production speech detector using package-provided dBFS samples.
class RecordSpeechActivitySource extends SpeechActivitySource {
  RecordSpeechActivitySource({
    RecordSpeechActivityDriver? driver,
    this.config = const SpeechActivitySourceConfig(),
    SpeechActivityDeadlineScheduler deadlineScheduler =
        const TimerSpeechActivityDeadlineScheduler(),
  }) : _driver = driver ?? RecordPackageSpeechActivityDriver(),
       _deadlineScheduler = deadlineScheduler;

  final RecordSpeechActivityDriver _driver;
  final SpeechActivitySourceConfig config;
  final SpeechActivityDeadlineScheduler _deadlineScheduler;

  SpeechActivitySourceState _state =
      const SpeechActivitySourceState.idle();
  SpeechActivityEventHandler? _eventHandler;
  StreamSubscription<double>? _amplitudeSubscription;
  Future<void>? _driverStartOperation;
  SpeechActivityDeadline? _maximumLifetimeDeadline;
  SpeechActivityDeadline? _cooldownDeadline;
  int _operationSequence = 0;
  int _eventSequence = 0;
  int _consecutiveSamples = 0;
  bool _closed = false;

  @override
  SpeechActivitySourceState get state => _state;

  @override
  void setEventHandler(SpeechActivityEventHandler? handler) {
    if (_closed) {
      return;
    }
    _eventHandler = handler;
  }

  @override
  Future<bool> arm({required int generation, required bool foreground}) async {
    if (_closed || !config.isValid || generation <= 0 || !foreground) {
      if (!_closed) {
        _setState(
          SpeechActivitySourceState(
            phase: SpeechActivitySourcePhase.failed,
            armingGeneration: generation < 0 ? 0 : generation,
            emittedEventCount: _state.emittedEventCount,
            foreground: foreground,
            technicalCode: !config.isValid
                ? 'speech_activity_config_invalid'
                : 'speech_activity_arm_rejected',
          ),
        );
      }
      return false;
    }
    if (_state.isActive) {
      return false;
    }

    final operation = ++_operationSequence;
    _resetDetectionState();
    _setState(
      SpeechActivitySourceState(
        phase: SpeechActivitySourcePhase.starting,
        armingGeneration: generation,
        emittedEventCount: _state.emittedEventCount,
        foreground: true,
      ),
    );

    _amplitudeSubscription = _driver.amplitudeDbfs.listen(
      (sample) => _handleAmplitude(operation, sample),
      onError: (_, _) => unawaited(_fail(operation)),
    );

    final driverStartOperation = _driver.start(
      sampleInterval: config.sampleInterval,
    );
    _driverStartOperation = driverStartOperation;
    try {
      await driverStartOperation;
    } catch (_) {
      await _cancelAmplitudeSubscription();
      if (_isCurrent(operation)) {
        _setState(
          SpeechActivitySourceState(
            phase: SpeechActivitySourcePhase.failed,
            armingGeneration: generation,
            emittedEventCount: _state.emittedEventCount,
            foreground: true,
            technicalCode: 'speech_activity_driver_start_failed',
          ),
        );
      }
      return false;
    } finally {
      if (identical(_driverStartOperation, driverStartOperation)) {
        _driverStartOperation = null;
      }
    }

    if (!_isCurrent(operation) || !_state.foreground) {
      await _stopDriverSafely();
      return false;
    }

    _maximumLifetimeDeadline = _deadlineScheduler.schedule(
      config.maximumLifetime,
      () => _expire(operation),
    );
    _setState(
      SpeechActivitySourceState(
        phase: SpeechActivitySourcePhase.armed,
        armingGeneration: generation,
        emittedEventCount: _state.emittedEventCount,
        foreground: true,
      ),
    );
    return true;
  }

  void _handleAmplitude(int operation, double sampleDbfs) {
    if (!_isCurrent(operation) || !sampleDbfs.isFinite) {
      return;
    }
    if (_state.phase == SpeechActivitySourcePhase.cooldown) {
      return;
    }
    if (_state.phase != SpeechActivitySourcePhase.armed) {
      return;
    }

    if (sampleDbfs < config.thresholdDbfs) {
      _consecutiveSamples = 0;
      return;
    }

    _consecutiveSamples += 1;
    if (_consecutiveSamples < config.requiredConsecutiveSamples) {
      return;
    }

    _consecutiveSamples = 0;
    _setState(
      SpeechActivitySourceState(
        phase: SpeechActivitySourcePhase.cooldown,
        armingGeneration: _state.armingGeneration,
        emittedEventCount: _state.emittedEventCount + 1,
        foreground: true,
      ),
    );

    final event = SpeechActivityEvent(
      eventId:
          'speech-${_state.armingGeneration}-${++_eventSequence}',
      confirmed: true,
      foreground: true,
    );
    final handler = _eventHandler;
    if (handler != null) {
      unawaited(
        Future<void>.sync(() => handler(event)).catchError((_) {
          // Event consumers are isolated from the production driver stream.
        }),
      );
    }

    _cooldownDeadline?.cancel();
    _cooldownDeadline = _deadlineScheduler.schedule(config.cooldown, () {
      if (!_isCurrent(operation)) {
        return;
      }
      // One confirmed event is permitted per arming generation. The source
      // remains latched until the binding disarms it and a later turn arms a
      // new generation.
    });
  }

  Future<void> _expire(int operation) async {
    if (!_isCurrent(operation)) {
      return;
    }
    await _disarmWithCode('speech_activity_maximum_lifetime_reached');
  }

  Future<void> _fail(int operation) async {
    if (!_isCurrent(operation)) {
      return;
    }
    ++_operationSequence;
    _cancelDeadlines();
    await _cancelAmplitudeSubscription();
    await _stopDriverSafely();
    if (_closed) {
      return;
    }
    _setState(
      SpeechActivitySourceState(
        phase: SpeechActivitySourcePhase.failed,
        armingGeneration: _state.armingGeneration,
        emittedEventCount: _state.emittedEventCount,
        foreground: _state.foreground,
        technicalCode: 'speech_activity_driver_stream_failed',
      ),
    );
  }

  @override
  Future<void> setForeground(bool foreground) async {
    if (_closed || foreground == _state.foreground) {
      return;
    }
    if (!foreground && _state.isActive) {
      _setState(
        SpeechActivitySourceState(
          phase: _state.phase,
          armingGeneration: _state.armingGeneration,
          emittedEventCount: _state.emittedEventCount,
          foreground: false,
          technicalCode: _state.technicalCode,
        ),
      );
      await _disarmWithCode('speech_activity_background_disarmed');
      return;
    }
    _setState(
      SpeechActivitySourceState(
        phase: _state.phase,
        armingGeneration: _state.armingGeneration,
        emittedEventCount: _state.emittedEventCount,
        foreground: foreground,
        technicalCode: _state.technicalCode,
      ),
    );
  }

  @override
  Future<void> disarm() => _disarmWithCode(null);

  Future<void> _disarmWithCode(String? technicalCode) async {
    if (_closed || !_state.isActive) {
      return;
    }
    ++_operationSequence;
    _setState(
      SpeechActivitySourceState(
        phase: SpeechActivitySourcePhase.stopping,
        armingGeneration: _state.armingGeneration,
        emittedEventCount: _state.emittedEventCount,
        foreground: _state.foreground,
      ),
    );
    _cancelDeadlines();
    await _cancelAmplitudeSubscription();
    final stopped = await _stopDriverSafely();
    if (_closed) {
      return;
    }
    _resetDetectionState();
    _setState(
      SpeechActivitySourceState(
        phase: stopped
            ? SpeechActivitySourcePhase.stopped
            : SpeechActivitySourcePhase.failed,
        armingGeneration: _state.armingGeneration,
        emittedEventCount: _state.emittedEventCount,
        foreground: _state.foreground,
        technicalCode: stopped
            ? technicalCode
            : 'speech_activity_driver_stop_failed',
      ),
    );
  }

  Future<bool> _stopDriverSafely() async {
    final driverStartOperation = _driverStartOperation;
    if (driverStartOperation != null) {
      try {
        await driverStartOperation;
      } catch (_) {
        // Stop still runs after a failed or cancelled driver start.
      }
    }
    try {
      await _driver.stop();
      return true;
    } catch (_) {
      return false;
    }
  }

  Future<void> _cancelAmplitudeSubscription() async {
    final subscription = _amplitudeSubscription;
    _amplitudeSubscription = null;
    await subscription?.cancel();
  }

  void _cancelDeadlines() {
    _maximumLifetimeDeadline?.cancel();
    _maximumLifetimeDeadline = null;
    _cooldownDeadline?.cancel();
    _cooldownDeadline = null;
  }

  void _resetDetectionState() {
    _consecutiveSamples = 0;
  }

  bool _isCurrent(int operation) =>
      !_closed && operation == _operationSequence;

  void _setState(SpeechActivitySourceState state) {
    if (_closed) {
      return;
    }
    _state = state;
    notifyListeners();
  }

  @override
  Future<void> close() async {
    if (_closed) {
      return;
    }
    _closed = true;
    ++_operationSequence;
    _eventHandler = null;
    _cancelDeadlines();
    await _cancelAmplitudeSubscription();
    await _stopDriverSafely();
    try {
      await _driver.dispose();
    } catch (_) {
      // Close remains metadata-only even if the platform driver rejects dispose.
    }
    _state = SpeechActivitySourceState(
      phase: SpeechActivitySourcePhase.disposed,
      armingGeneration: _state.armingGeneration,
      emittedEventCount: _state.emittedEventCount,
      foreground: _state.foreground,
    );
  }

  @override
  void dispose() {
    unawaited(close());
    super.dispose();
  }
}
