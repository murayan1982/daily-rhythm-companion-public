import 'dart:async';

import 'package:flutter/foundation.dart';

enum VoiceOutputPlaybackPhase {
  idle,
  loading,
  playing,
  stopped,
  completed,
  failed,
  expired,
}

enum VoiceOutputAudioEngineEventType {
  playing,
  completed,
  failed,
  expired,
}

class VoiceOutputAudioEngineEvent {
  const VoiceOutputAudioEngineEvent({
    required this.type,
    this.technicalCode,
  });

  final VoiceOutputAudioEngineEventType type;
  final String? technicalCode;
}

class VoiceOutputAudioEngineException implements Exception {
  const VoiceOutputAudioEngineException({
    required this.code,
    this.expired = false,
  });

  final String code;
  final bool expired;

  @override
  String toString() => 'VoiceOutputAudioEngineException($code)';
}

abstract interface class VoiceOutputAudioEngine {
  Stream<VoiceOutputAudioEngineEvent> get events;

  Future<void> load(Uri source);

  Future<void> play();

  Future<void> stop();

  Future<void> seekToStart();

  Future<void> dispose();
}

@immutable
class VoiceOutputPlaybackState {
  const VoiceOutputPlaybackState({
    required this.phase,
    required this.hasSource,
    required this.userMessage,
    this.technicalCode,
  });

  const VoiceOutputPlaybackState.idle()
      : this(
          phase: VoiceOutputPlaybackPhase.idle,
          hasSource: false,
          userMessage: '再生できる音声はまだありません。',
        );

  final VoiceOutputPlaybackPhase phase;
  final bool hasSource;
  final String userMessage;
  final String? technicalCode;

  bool get isLoading => phase == VoiceOutputPlaybackPhase.loading;
  bool get isPlaying => phase == VoiceOutputPlaybackPhase.playing;
  bool get isCompleted => phase == VoiceOutputPlaybackPhase.completed;
  bool get isFailed => phase == VoiceOutputPlaybackPhase.failed;
  bool get isExpired => phase == VoiceOutputPlaybackPhase.expired;

  bool get canStop => isLoading || isPlaying;

  bool get canReplay =>
      hasSource &&
      (phase == VoiceOutputPlaybackPhase.stopped ||
          phase == VoiceOutputPlaybackPhase.completed ||
          phase == VoiceOutputPlaybackPhase.failed);

  String get displayPhase => phase.name.replaceAll('_', ' ');
}

class VoiceOutputAudioPlayerController extends ChangeNotifier {
  VoiceOutputAudioPlayerController({required VoiceOutputAudioEngine engine})
      : _engine = engine {
    _eventSubscription = _engine.events.listen(_handleEngineEvent);
  }

  final VoiceOutputAudioEngine _engine;
  late final StreamSubscription<VoiceOutputAudioEngineEvent> _eventSubscription;

  VoiceOutputPlaybackState _state = const VoiceOutputPlaybackState.idle();
  Uri? _source;
  int _operationSequence = 0;
  bool _isDisposed = false;

  VoiceOutputPlaybackState get state => _state;

  Future<void> play(Uri source) async {
    if (!_isSupportedSource(source)) {
      _setState(
        const VoiceOutputPlaybackState(
          phase: VoiceOutputPlaybackPhase.failed,
          hasSource: false,
          userMessage: 'この音声URLは再生できません。',
          technicalCode: 'unsupported_audio_uri',
        ),
      );
      return;
    }

    final operation = ++_operationSequence;
    _source = source;
    _setState(
      const VoiceOutputPlaybackState(
        phase: VoiceOutputPlaybackPhase.loading,
        hasSource: true,
        userMessage: '音声を読み込んでいます。',
      ),
    );

    try {
      await _engine.load(source);
      if (!_isCurrent(operation)) {
        return;
      }

      await _engine.play();
      if (!_isCurrent(operation)) {
        return;
      }

      _setState(
        const VoiceOutputPlaybackState(
          phase: VoiceOutputPlaybackPhase.playing,
          hasSource: true,
          userMessage: '音声を再生しています。',
        ),
      );
    } catch (error) {
      if (_isCurrent(operation)) {
        _handleOperationError(error);
      }
    }
  }

  Future<void> stop() async {
    if (_source == null) {
      return;
    }

    final operation = ++_operationSequence;
    try {
      await _engine.stop();
      if (!_isCurrent(operation)) {
        return;
      }
      _setState(
        const VoiceOutputPlaybackState(
          phase: VoiceOutputPlaybackPhase.stopped,
          hasSource: true,
          userMessage: '音声を停止しました。',
        ),
      );
    } catch (error) {
      if (_isCurrent(operation)) {
        _handleOperationError(error);
      }
    }
  }

  Future<void> replay() async {
    final source = _source;
    if (source == null || !state.canReplay) {
      return;
    }

    if (state.isFailed) {
      await play(source);
      return;
    }

    final operation = ++_operationSequence;
    _setState(
      const VoiceOutputPlaybackState(
        phase: VoiceOutputPlaybackPhase.loading,
        hasSource: true,
        userMessage: '音声をもう一度読み込んでいます。',
      ),
    );

    try {
      await _engine.seekToStart();
      if (!_isCurrent(operation)) {
        return;
      }
      await _engine.play();
      if (!_isCurrent(operation)) {
        return;
      }
      _setState(
        const VoiceOutputPlaybackState(
          phase: VoiceOutputPlaybackPhase.playing,
          hasSource: true,
          userMessage: '音声を再生しています。',
        ),
      );
    } catch (error) {
      if (_isCurrent(operation)) {
        _handleOperationError(error);
      }
    }
  }

  Future<void> markExpired({String technicalCode = 'audio_artifact_expired'}) async {
    ++_operationSequence;
    _source = null;

    try {
      await _engine.stop();
    } catch (_) {
      // Expiry remains the user-facing terminal state even when stop also fails.
    }

    _setState(
      VoiceOutputPlaybackState(
        phase: VoiceOutputPlaybackPhase.expired,
        hasSource: false,
        userMessage: 'この音声は期限切れです。音声を作り直してください。',
        technicalCode: technicalCode,
      ),
    );
  }

  Future<void> reset() async {
    ++_operationSequence;
    _source = null;

    try {
      await _engine.stop();
    } catch (_) {
      // Reset must leave the controller idle even if the platform is already gone.
    }

    _setState(const VoiceOutputPlaybackState.idle());
  }

  void _handleEngineEvent(VoiceOutputAudioEngineEvent event) {
    if (_isDisposed || _source == null || !(state.isLoading || state.isPlaying)) {
      return;
    }

    switch (event.type) {
      case VoiceOutputAudioEngineEventType.playing:
        if (_source != null) {
          _setState(
            VoiceOutputPlaybackState(
              phase: VoiceOutputPlaybackPhase.playing,
              hasSource: true,
              userMessage: '音声を再生しています。',
              technicalCode: event.technicalCode,
            ),
          );
        }
        break;
      case VoiceOutputAudioEngineEventType.completed:
        if (_source != null) {
          _setState(
            VoiceOutputPlaybackState(
              phase: VoiceOutputPlaybackPhase.completed,
              hasSource: true,
              userMessage: '音声の再生が完了しました。',
              technicalCode: event.technicalCode,
            ),
          );
        }
        break;
      case VoiceOutputAudioEngineEventType.failed:
        _setState(
          VoiceOutputPlaybackState(
            phase: VoiceOutputPlaybackPhase.failed,
            hasSource: _source != null,
            userMessage: '音声を再生できませんでした。もう一度試してください。',
            technicalCode: event.technicalCode ?? 'audio_playback_failed',
          ),
        );
        break;
      case VoiceOutputAudioEngineEventType.expired:
        _source = null;
        _setState(
          VoiceOutputPlaybackState(
            phase: VoiceOutputPlaybackPhase.expired,
            hasSource: false,
            userMessage: 'この音声は期限切れです。音声を作り直してください。',
            technicalCode: event.technicalCode ?? 'audio_artifact_expired',
          ),
        );
        break;
    }
  }

  void _handleOperationError(Object error) {
    if (error is VoiceOutputAudioEngineException && error.expired) {
      _source = null;
      _setState(
        VoiceOutputPlaybackState(
          phase: VoiceOutputPlaybackPhase.expired,
          hasSource: false,
          userMessage: 'この音声は期限切れです。音声を作り直してください。',
          technicalCode: error.code,
        ),
      );
      return;
    }

    final technicalCode = error is VoiceOutputAudioEngineException
        ? error.code
        : 'audio_playback_failed';
    _setState(
      VoiceOutputPlaybackState(
        phase: VoiceOutputPlaybackPhase.failed,
        hasSource: _source != null,
        userMessage: '音声を再生できませんでした。もう一度試してください。',
        technicalCode: technicalCode,
      ),
    );
  }

  bool _isSupportedSource(Uri source) =>
      source.hasScheme && (source.scheme == 'http' || source.scheme == 'https');

  bool _isCurrent(int operation) =>
      !_isDisposed && operation == _operationSequence;

  void _setState(VoiceOutputPlaybackState nextState) {
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
    ++_operationSequence;
    unawaited(_eventSubscription.cancel());
    unawaited(_engine.dispose());
    super.dispose();
  }
}
