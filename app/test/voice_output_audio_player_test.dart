import 'dart:async';

import 'package:app/services/voice_output_audio_player.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('VoiceOutputAudioPlayerController', () {
    test('starts idle without a retained source', () {
      final engine = _FakeVoiceOutputAudioEngine();
      final controller = VoiceOutputAudioPlayerController(engine: engine);

      expect(controller.state.phase, VoiceOutputPlaybackPhase.idle);
      expect(controller.state.hasSource, isFalse);
      expect(controller.state.canStop, isFalse);
      expect(controller.state.canReplay, isFalse);

      controller.dispose();
    });

    test('play exposes loading before becoming playing', () async {
      final engine = _FakeVoiceOutputAudioEngine()..holdLoad();
      final controller = VoiceOutputAudioPlayerController(engine: engine);
      final source = Uri.parse('http://127.0.0.1:8000/demo/voice-output/audio/opaque');

      final playFuture = controller.play(source);

      expect(controller.state.phase, VoiceOutputPlaybackPhase.loading);
      expect(controller.state.hasSource, isTrue);
      expect(controller.state.canStop, isTrue);
      expect(engine.loadedSources, [source]);

      engine.completeLoad();
      await playFuture;

      expect(controller.state.phase, VoiceOutputPlaybackPhase.playing);
      expect(engine.playCalls, 1);

      controller.dispose();
    });

    test('stop produces a replayable stopped state', () async {
      final engine = _FakeVoiceOutputAudioEngine();
      final controller = VoiceOutputAudioPlayerController(engine: engine);

      await controller.play(Uri.parse('https://example.invalid/audio.mp3'));
      await controller.stop();

      expect(controller.state.phase, VoiceOutputPlaybackPhase.stopped);
      expect(controller.state.canReplay, isTrue);
      expect(engine.stopCalls, 1);

      controller.dispose();
    });

    test('completion event produces replay-ready state', () async {
      final engine = _FakeVoiceOutputAudioEngine();
      final controller = VoiceOutputAudioPlayerController(engine: engine);

      await controller.play(Uri.parse('https://example.invalid/audio.mp3'));
      engine.emit(const VoiceOutputAudioEngineEvent(
        type: VoiceOutputAudioEngineEventType.completed,
      ));

      expect(controller.state.phase, VoiceOutputPlaybackPhase.completed);
      expect(controller.state.canReplay, isTrue);

      controller.dispose();
    });

    test('replay seeks to the beginning and starts again', () async {
      final engine = _FakeVoiceOutputAudioEngine();
      final controller = VoiceOutputAudioPlayerController(engine: engine);

      await controller.play(Uri.parse('https://example.invalid/audio.mp3'));
      engine.emit(const VoiceOutputAudioEngineEvent(
        type: VoiceOutputAudioEngineEventType.completed,
      ));
      await controller.replay();

      expect(engine.seekToStartCalls, 1);
      expect(engine.playCalls, 2);
      expect(controller.state.phase, VoiceOutputPlaybackPhase.playing);

      controller.dispose();
    });

    test('expired engine failure clears the source and blocks replay', () async {
      final engine = _FakeVoiceOutputAudioEngine(
        loadError: const VoiceOutputAudioEngineException(
          code: 'audio_artifact_not_found',
          expired: true,
        ),
      );
      final controller = VoiceOutputAudioPlayerController(engine: engine);

      await controller.play(Uri.parse('https://example.invalid/expired.mp3'));

      expect(controller.state.phase, VoiceOutputPlaybackPhase.expired);
      expect(controller.state.hasSource, isFalse);
      expect(controller.state.canReplay, isFalse);
      expect(controller.state.technicalCode, 'audio_artifact_not_found');
      expect(controller.state.userMessage, isNot(contains('example.invalid')));

      controller.dispose();
    });

    test('ordinary engine failure stays retryable without exposing URL', () async {
      final engine = _FakeVoiceOutputAudioEngine(
        playError: const VoiceOutputAudioEngineException(
          code: 'decoder_failed',
        ),
      );
      final controller = VoiceOutputAudioPlayerController(engine: engine);

      await controller.play(Uri.parse('https://example.invalid/private-path.mp3'));

      expect(controller.state.phase, VoiceOutputPlaybackPhase.failed);
      expect(controller.state.canReplay, isTrue);
      expect(controller.state.technicalCode, 'decoder_failed');
      expect(controller.state.userMessage, isNot(contains('private-path')));

      controller.dispose();
    });

    test('unsupported URI fails before the engine sees it', () async {
      final engine = _FakeVoiceOutputAudioEngine();
      final controller = VoiceOutputAudioPlayerController(engine: engine);

      await controller.play(Uri.parse('file:///private/audio.mp3'));

      expect(controller.state.phase, VoiceOutputPlaybackPhase.failed);
      expect(controller.state.technicalCode, 'unsupported_audio_uri');
      expect(engine.loadedSources, isEmpty);

      controller.dispose();
    });

    test('reset invalidates a pending load result', () async {
      final engine = _FakeVoiceOutputAudioEngine()..holdLoad();
      final controller = VoiceOutputAudioPlayerController(engine: engine);

      final playFuture = controller.play(
        Uri.parse('https://example.invalid/audio.mp3'),
      );
      await controller.reset();
      engine.completeLoad();
      await playFuture;
      engine.emit(const VoiceOutputAudioEngineEvent(
        type: VoiceOutputAudioEngineEventType.completed,
      ));

      expect(controller.state.phase, VoiceOutputPlaybackPhase.idle);
      expect(engine.playCalls, 0);

      controller.dispose();
    });

    test('dispose closes the engine', () async {
      final engine = _FakeVoiceOutputAudioEngine();
      final controller = VoiceOutputAudioPlayerController(engine: engine);

      controller.dispose();
      await Future<void>.delayed(Duration.zero);

      expect(engine.disposeCalls, 1);
    });
  });
}

class _FakeVoiceOutputAudioEngine implements VoiceOutputAudioEngine {
  _FakeVoiceOutputAudioEngine({this.loadError, this.playError});

  final Object? loadError;
  final Object? playError;
  final StreamController<VoiceOutputAudioEngineEvent> _events =
      StreamController<VoiceOutputAudioEngineEvent>.broadcast(sync: true);

  final List<Uri> loadedSources = [];
  int playCalls = 0;
  int stopCalls = 0;
  int seekToStartCalls = 0;
  int disposeCalls = 0;
  Completer<void>? _loadCompleter;

  @override
  Stream<VoiceOutputAudioEngineEvent> get events => _events.stream;

  void holdLoad() {
    _loadCompleter = Completer<void>();
  }

  void completeLoad() {
    _loadCompleter?.complete();
  }

  void emit(VoiceOutputAudioEngineEvent event) {
    _events.add(event);
  }

  @override
  Future<void> load(Uri source) async {
    loadedSources.add(source);
    if (loadError != null) {
      throw loadError!;
    }
    await _loadCompleter?.future;
  }

  @override
  Future<void> play() async {
    playCalls += 1;
    if (playError != null) {
      throw playError!;
    }
  }

  @override
  Future<void> stop() async {
    stopCalls += 1;
  }

  @override
  Future<void> seekToStart() async {
    seekToStartCalls += 1;
  }

  @override
  Future<void> dispose() async {
    disposeCalls += 1;
    await _events.close();
  }
}
