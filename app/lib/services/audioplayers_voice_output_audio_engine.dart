import 'dart:async';
import 'dart:typed_data';

import 'package:audioplayers/audioplayers.dart';
import 'package:http/http.dart' as http;

import 'voice_output_audio_player.dart';

enum VoiceOutputPlatformPlayerState {
  stopped,
  playing,
  paused,
  completed,
  disposed,
}

abstract interface class VoiceOutputPlatformAudioDriver {
  Stream<VoiceOutputPlatformPlayerState> get stateChanges;

  Stream<void> get completions;

  Future<void> configure();

  Future<void> setSourceBytes(List<int> bytes, {required String mimeType});

  Future<void> resume();

  Future<void> stop();

  Future<void> seek(Duration position);

  Future<void> dispose();
}

typedef VoiceOutputPlatformAudioDriverFactory =
    VoiceOutputPlatformAudioDriver Function();

class AudioplayersVoiceOutputAudioEngine implements VoiceOutputAudioEngine {
  AudioplayersVoiceOutputAudioEngine({
    http.Client? httpClient,
    VoiceOutputPlatformAudioDriverFactory? driverFactory,
  })  : _httpClient = httpClient ?? http.Client(),
        _ownsHttpClient = httpClient == null,
        _driverFactory =
            driverFactory ?? _AudioplayersVoiceOutputPlatformDriver.new;

  final http.Client _httpClient;
  final bool _ownsHttpClient;
  final VoiceOutputPlatformAudioDriverFactory _driverFactory;
  final StreamController<VoiceOutputAudioEngineEvent> _events =
      StreamController<VoiceOutputAudioEngineEvent>.broadcast(sync: true);

  VoiceOutputPlatformAudioDriver? _driver;
  StreamSubscription<VoiceOutputPlatformPlayerState>? _stateSubscription;
  StreamSubscription<void>? _completionSubscription;
  bool _configured = false;
  bool _disposed = false;

  @override
  Stream<VoiceOutputAudioEngineEvent> get events => _events.stream;

  @override
  Future<void> load(Uri source) async {
    _ensureUsable();

    final response = await _fetchAudio(source);
    if (response.statusCode == 404 || response.statusCode == 410) {
      throw const VoiceOutputAudioEngineException(
        code: 'audio_artifact_not_found',
        expired: true,
      );
    }
    if (response.statusCode != 200 && response.statusCode != 206) {
      throw VoiceOutputAudioEngineException(
        code: 'audio_http_${response.statusCode}',
      );
    }

    final contentType = response.headers['content-type']?.toLowerCase() ?? '';
    if (contentType.isNotEmpty && !contentType.contains('audio/mpeg')) {
      throw const VoiceOutputAudioEngineException(
        code: 'unsupported_audio_content_type',
      );
    }
    if (response.bodyBytes.isEmpty) {
      throw const VoiceOutputAudioEngineException(code: 'empty_audio_artifact');
    }

    final driver = _ensureDriver();
    if (!_configured) {
      await _mapDriverOperation(driver.configure);
      _configured = true;
    }
    await _mapDriverOperation(
      () => driver.setSourceBytes(
        response.bodyBytes,
        mimeType: 'audio/mpeg',
      ),
    );
  }

  @override
  Future<void> play() async {
    _ensureUsable();
    await _mapDriverOperation(_ensureDriver().resume);
  }

  @override
  Future<void> stop() async {
    if (_disposed || _driver == null) {
      return;
    }
    await _mapDriverOperation(_driver!.stop);
  }

  @override
  Future<void> seekToStart() async {
    _ensureUsable();
    await _mapDriverOperation(() => _ensureDriver().seek(Duration.zero));
  }

  @override
  Future<void> dispose() async {
    if (_disposed) {
      return;
    }
    _disposed = true;

    await _stateSubscription?.cancel();
    await _completionSubscription?.cancel();
    await _driver?.dispose();
    if (_ownsHttpClient) {
      _httpClient.close();
    }
    await _events.close();
  }

  Future<http.Response> _fetchAudio(Uri source) async {
    try {
      return await _httpClient.get(
        source,
        headers: const {
          'Accept': 'audio/mpeg',
          'Cache-Control': 'no-cache',
        },
      );
    } catch (_) {
      throw const VoiceOutputAudioEngineException(
        code: 'audio_http_request_failed',
      );
    }
  }

  VoiceOutputPlatformAudioDriver _ensureDriver() {
    final existing = _driver;
    if (existing != null) {
      return existing;
    }

    final created = _driverFactory();
    _driver = created;
    _stateSubscription = created.stateChanges.listen((state) {
      if (_disposed) {
        return;
      }
      switch (state) {
        case VoiceOutputPlatformPlayerState.playing:
          _events.add(const VoiceOutputAudioEngineEvent(
            type: VoiceOutputAudioEngineEventType.playing,
          ));
          break;
        case VoiceOutputPlatformPlayerState.completed:
        case VoiceOutputPlatformPlayerState.stopped:
        case VoiceOutputPlatformPlayerState.paused:
        case VoiceOutputPlatformPlayerState.disposed:
          break;
      }
    });
    _completionSubscription = created.completions.listen((_) {
      if (!_disposed) {
        _events.add(const VoiceOutputAudioEngineEvent(
          type: VoiceOutputAudioEngineEventType.completed,
        ));
      }
    });
    return created;
  }

  Future<void> _mapDriverOperation(
    Future<void> Function() operation,
  ) async {
    try {
      await operation();
    } catch (error) {
      final normalized = error.toString().toLowerCase();
      if (normalized.contains('404') ||
          normalized.contains('410') ||
          normalized.contains('not found')) {
        throw const VoiceOutputAudioEngineException(
          code: 'audio_artifact_not_found',
          expired: true,
        );
      }
      throw const VoiceOutputAudioEngineException(
        code: 'audio_platform_playback_failed',
      );
    }
  }

  void _ensureUsable() {
    if (_disposed) {
      throw const VoiceOutputAudioEngineException(
        code: 'audio_engine_disposed',
      );
    }
  }
}

class _AudioplayersVoiceOutputPlatformDriver
    implements VoiceOutputPlatformAudioDriver {
  _AudioplayersVoiceOutputPlatformDriver() : _player = AudioPlayer() {
    _stateChanges = _player.onPlayerStateChanged.map(_mapPlayerState);
    _completions = _player.onPlayerComplete;
  }

  final AudioPlayer _player;
  late final Stream<VoiceOutputPlatformPlayerState> _stateChanges;
  late final Stream<void> _completions;

  @override
  Stream<VoiceOutputPlatformPlayerState> get stateChanges => _stateChanges;

  @override
  Stream<void> get completions => _completions;

  @override
  Future<void> configure() async {
    await _player.setPlayerMode(PlayerMode.mediaPlayer);
    await _player.setReleaseMode(ReleaseMode.stop);
  }

  @override
  Future<void> setSourceBytes(
    List<int> bytes, {
    required String mimeType,
  }) async {
    await _player.setSourceBytes(
      Uint8List.fromList(bytes),
      mimeType: mimeType,
    );
  }

  @override
  Future<void> resume() => _player.resume();

  @override
  Future<void> stop() => _player.stop();

  @override
  Future<void> seek(Duration position) => _player.seek(position);

  @override
  Future<void> dispose() => _player.dispose();

  static VoiceOutputPlatformPlayerState _mapPlayerState(PlayerState state) {
    return switch (state) {
      PlayerState.stopped => VoiceOutputPlatformPlayerState.stopped,
      PlayerState.playing => VoiceOutputPlatformPlayerState.playing,
      PlayerState.paused => VoiceOutputPlatformPlayerState.paused,
      PlayerState.completed => VoiceOutputPlatformPlayerState.completed,
      PlayerState.disposed => VoiceOutputPlatformPlayerState.disposed,
    };
  }
}
