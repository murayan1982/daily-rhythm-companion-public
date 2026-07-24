import 'dart:async';

import 'package:app/services/audioplayers_voice_output_audio_engine.dart';
import 'package:app/services/voice_output_audio_player.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

void main() {
  group('AudioplayersVoiceOutputAudioEngine', () {
    test('loads MP3 bytes and drives play stop seek', () async {
      final driver = _FakePlatformAudioDriver();
      final engine = AudioplayersVoiceOutputAudioEngine(
        httpClient: MockClient((request) async {
          expect(request.headers['accept'], 'audio/mpeg');
          return http.Response.bytes(
            const <int>[0x49, 0x44, 0x33],
            200,
            headers: const {'content-type': 'audio/mpeg'},
          );
        }),
        driverFactory: () => driver,
      );

      await engine.load(Uri.parse('https://example.invalid/opaque-audio'));
      await engine.play();
      await engine.stop();
      await engine.seekToStart();

      expect(driver.configureCalls, 1);
      expect(driver.loadedBytes, const <int>[0x49, 0x44, 0x33]);
      expect(driver.loadedMimeType, 'audio/mpeg');
      expect(driver.resumeCalls, 1);
      expect(driver.stopCalls, 1);
      expect(driver.seekPositions, const <Duration>[Duration.zero]);

      await engine.dispose();
    });

    test('HTTP 404 becomes an expired artifact failure', () async {
      final engine = AudioplayersVoiceOutputAudioEngine(
        httpClient: MockClient((_) async => http.Response('missing', 404)),
        driverFactory: _FakePlatformAudioDriver.new,
      );

      await expectLater(
        engine.load(Uri.parse('https://example.invalid/missing')),
        throwsA(
          isA<VoiceOutputAudioEngineException>()
              .having((error) => error.expired, 'expired', isTrue)
              .having(
                (error) => error.code,
                'code',
                'audio_artifact_not_found',
              ),
        ),
      );

      await engine.dispose();
    });

    test('HTTP 410 becomes an expired artifact failure', () async {
      final engine = AudioplayersVoiceOutputAudioEngine(
        httpClient: MockClient((_) async => http.Response('gone', 410)),
        driverFactory: _FakePlatformAudioDriver.new,
      );

      await expectLater(
        engine.load(Uri.parse('https://example.invalid/gone')),
        throwsA(
          isA<VoiceOutputAudioEngineException>()
              .having((error) => error.expired, 'expired', isTrue),
        ),
      );

      await engine.dispose();
    });

    test('non-success HTTP status stays a retryable failure', () async {
      final engine = AudioplayersVoiceOutputAudioEngine(
        httpClient: MockClient((_) async => http.Response('busy', 503)),
        driverFactory: _FakePlatformAudioDriver.new,
      );

      await expectLater(
        engine.load(Uri.parse('https://example.invalid/busy')),
        throwsA(
          isA<VoiceOutputAudioEngineException>()
              .having((error) => error.expired, 'expired', isFalse)
              .having((error) => error.code, 'code', 'audio_http_503'),
        ),
      );

      await engine.dispose();
    });

    test('rejects a non-MP3 response without exposing its URL', () async {
      final engine = AudioplayersVoiceOutputAudioEngine(
        httpClient: MockClient((_) async {
          return http.Response.bytes(
            const <int>[1, 2, 3],
            200,
            headers: const {'content-type': 'text/html'},
          );
        }),
        driverFactory: _FakePlatformAudioDriver.new,
      );

      await expectLater(
        engine.load(Uri.parse('https://example.invalid/private-name')),
        throwsA(
          isA<VoiceOutputAudioEngineException>().having(
            (error) => error.code,
            'code',
            'unsupported_audio_content_type',
          ),
        ),
      );

      await engine.dispose();
    });

    test('forwards playing and completion events', () async {
      final driver = _FakePlatformAudioDriver();
      final engine = AudioplayersVoiceOutputAudioEngine(
        httpClient: MockClient((_) async {
          return http.Response.bytes(
            const <int>[0x49, 0x44, 0x33],
            200,
            headers: const {'content-type': 'audio/mpeg'},
          );
        }),
        driverFactory: () => driver,
      );
      final received = <VoiceOutputAudioEngineEventType>[];
      final subscription = engine.events.listen(
        (event) => received.add(event.type),
      );

      await engine.load(Uri.parse('https://example.invalid/opaque'));
      driver.emitState(VoiceOutputPlatformPlayerState.playing);
      driver.emitCompletion();

      expect(
        received,
        const <VoiceOutputAudioEngineEventType>[
          VoiceOutputAudioEngineEventType.playing,
          VoiceOutputAudioEngineEventType.completed,
        ],
      );

      await subscription.cancel();
      await engine.dispose();
    });

    test('platform not-found error is mapped to expired', () async {
      final driver = _FakePlatformAudioDriver(
        resumeError: Exception('HTTP 404 not found'),
      );
      final engine = AudioplayersVoiceOutputAudioEngine(
        httpClient: MockClient((_) async {
          return http.Response.bytes(
            const <int>[0x49, 0x44, 0x33],
            200,
            headers: const {'content-type': 'audio/mpeg'},
          );
        }),
        driverFactory: () => driver,
      );

      await engine.load(Uri.parse('https://example.invalid/opaque'));
      await expectLater(
        engine.play(),
        throwsA(
          isA<VoiceOutputAudioEngineException>()
              .having((error) => error.expired, 'expired', isTrue),
        ),
      );

      await engine.dispose();
    });
  });
}

class _FakePlatformAudioDriver implements VoiceOutputPlatformAudioDriver {
  _FakePlatformAudioDriver({this.resumeError});

  final Object? resumeError;
  final StreamController<VoiceOutputPlatformPlayerState> _states =
      StreamController<VoiceOutputPlatformPlayerState>.broadcast(sync: true);
  final StreamController<void> _completions =
      StreamController<void>.broadcast(sync: true);

  int configureCalls = 0;
  List<int> loadedBytes = const <int>[];
  String? loadedMimeType;
  int resumeCalls = 0;
  int stopCalls = 0;
  final List<Duration> seekPositions = <Duration>[];

  @override
  Stream<VoiceOutputPlatformPlayerState> get stateChanges => _states.stream;

  @override
  Stream<void> get completions => _completions.stream;

  void emitState(VoiceOutputPlatformPlayerState state) => _states.add(state);

  void emitCompletion() => _completions.add(null);

  @override
  Future<void> configure() async {
    configureCalls += 1;
  }

  @override
  Future<void> setSourceBytes(
    List<int> bytes, {
    required String mimeType,
  }) async {
    loadedBytes = List<int>.from(bytes);
    loadedMimeType = mimeType;
  }

  @override
  Future<void> resume() async {
    resumeCalls += 1;
    if (resumeError != null) {
      throw resumeError!;
    }
  }

  @override
  Future<void> stop() async {
    stopCalls += 1;
  }

  @override
  Future<void> seek(Duration position) async {
    seekPositions.add(position);
  }

  @override
  Future<void> dispose() async {
    await _states.close();
    await _completions.close();
  }
}
