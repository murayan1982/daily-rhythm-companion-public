import 'dart:io';
import 'dart:math';

import 'package:path_provider/path_provider.dart';
import 'package:record/record.dart';

import 'microphone_capture.dart';

/// App-owned request passed to the package-specific recorder driver.
///
/// [privatePath] is intentionally confined to this adapter boundary. It must
/// never be copied into public result metadata, logs, UI state, or API payloads.
class RecordMicrophoneCaptureDriverRequest {
  const RecordMicrophoneCaptureDriverRequest({
    required this.privatePath,
    this.sampleRate = 16000,
    this.numChannels = 1,
  });

  final String privatePath;
  final int sampleRate;
  final int numChannels;
}

/// Injectable boundary around package:record.
///
/// RT-2e-b tests use only a fake implementation. The production implementation
/// is compiled but is not connected to UI/startup and is not executed here.
abstract interface class RecordMicrophoneCaptureDriver {
  bool get accessesRealMicrophone;

  Future<void> start(RecordMicrophoneCaptureDriverRequest request);

  Future<String?> stop();

  Future<void> cancel();

  Future<void> dispose();
}

/// package:record 6.2.1 implementation.
///
/// Permission checks remain owned by [MicrophoneCaptureController] through the
/// app-owned permission gateway. This driver deliberately does not call
/// the package permission helper.
class RecordPackageMicrophoneCaptureDriver
    implements RecordMicrophoneCaptureDriver {
  RecordPackageMicrophoneCaptureDriver({AudioRecorder? recorder})
      : _recorder = recorder ?? AudioRecorder();

  final AudioRecorder _recorder;

  @override
  bool get accessesRealMicrophone => true;

  @override
  Future<void> start(RecordMicrophoneCaptureDriverRequest request) {
    return _recorder.start(
      RecordConfig(
        encoder: AudioEncoder.wav,
        sampleRate: request.sampleRate,
        numChannels: request.numChannels,
      ),
      path: request.privatePath,
    );
  }

  @override
  Future<String?> stop() => _recorder.stop();

  @override
  Future<void> cancel() => _recorder.cancel();

  @override
  Future<void> dispose() => _recorder.dispose();
}

/// Private temporary file boundary used by the record adapter.
abstract interface class RecordMicrophoneCapturePrivateFileSystem {
  Future<String> allocatePrivatePath();

  bool ownsPrivatePath(String path);

  Future<void> deletePrivatePath(String path);
}

typedef RecordTemporaryDirectoryLoader = Future<Directory> Function();

/// Mobile-oriented private temporary path allocator.
///
/// It allocates only a path under the app temporary directory. The audio file
/// itself is created by package:record only if the production driver is later
/// explicitly executed.
class PathProviderRecordMicrophoneCapturePrivateFileSystem
    implements RecordMicrophoneCapturePrivateFileSystem {
  PathProviderRecordMicrophoneCapturePrivateFileSystem({
    RecordTemporaryDirectoryLoader? temporaryDirectoryLoader,
    Random? random,
  })  : _temporaryDirectoryLoader =
            temporaryDirectoryLoader ?? getTemporaryDirectory,
        _random = random ?? Random.secure();

  final RecordTemporaryDirectoryLoader _temporaryDirectoryLoader;
  final Random _random;
  final Set<String> _ownedPaths = <String>{};

  @override
  Future<String> allocatePrivatePath() async {
    final temporaryDirectory = await _temporaryDirectoryLoader();
    final captureDirectory = Directory(
      '${temporaryDirectory.path}${Platform.pathSeparator}'
      'drc_microphone_capture',
    );
    await captureDirectory.create(recursive: true);

    for (var attempt = 0; attempt < 8; attempt += 1) {
      final token = List<int>.generate(
        16,
        (_) => _random.nextInt(256),
        growable: false,
      ).map((value) => value.toRadixString(16).padLeft(2, '0')).join();
      final path = '${captureDirectory.path}${Platform.pathSeparator}'
          'capture_$token.wav';
      if (!_ownedPaths.contains(path) && !await File(path).exists()) {
        _ownedPaths.add(path);
        return path;
      }
    }

    throw const MicrophoneCaptureEngineException(
      'record_private_path_allocation_failed',
    );
  }

  @override
  bool ownsPrivatePath(String path) => _ownedPaths.contains(path);

  @override
  Future<void> deletePrivatePath(String path) async {
    if (!_ownedPaths.remove(path)) {
      return;
    }

    final file = File(path);
    if (await file.exists()) {
      await file.delete();
    }
  }
}

typedef RecordMicrophoneCaptureOpaqueIdGenerator = String Function();
typedef RecordMicrophoneCaptureNow = DateTime Function();

/// App-internal access to a private completed capture artifact.
///
/// The path is never present in [MicrophoneCaptureEngineResult]. A future
/// upload/STT boundary may resolve the path by opaque id, then must explicitly
/// discard it. RT-2e-b does not add that consumer.
abstract interface class RecordMicrophoneCapturePrivateArtifactAccess {
  String? resolvePrivateArtifactPath(String opaqueCaptureId);

  Future<bool> discardPrivateArtifact(String opaqueCaptureId);
}

/// package:record-backed engine with injectable driver and private filesystem.
///
/// RT-2e-b compiles this real-capable adapter but tests it only with fake
/// dependencies. No UI or startup wiring instantiates the production driver.
class RecordMicrophoneCaptureEngine
    implements
        MicrophoneCaptureEngine,
        RecordMicrophoneCapturePrivateArtifactAccess {
  RecordMicrophoneCaptureEngine({
    required RecordMicrophoneCaptureDriver driver,
    required RecordMicrophoneCapturePrivateFileSystem privateFileSystem,
    RecordMicrophoneCaptureOpaqueIdGenerator? opaqueIdGenerator,
    RecordMicrophoneCaptureNow? now,
  })  : _driver = driver,
        _privateFileSystem = privateFileSystem,
        _opaqueIdGenerator = opaqueIdGenerator ?? _defaultOpaqueId,
        _now = now ?? DateTime.now;

  factory RecordMicrophoneCaptureEngine.mobile() {
    return RecordMicrophoneCaptureEngine(
      driver: RecordPackageMicrophoneCaptureDriver(),
      privateFileSystem:
          PathProviderRecordMicrophoneCapturePrivateFileSystem(),
    );
  }

  static final Random _opaqueRandom = Random.secure();

  final RecordMicrophoneCaptureDriver _driver;
  final RecordMicrophoneCapturePrivateFileSystem _privateFileSystem;
  final RecordMicrophoneCaptureOpaqueIdGenerator _opaqueIdGenerator;
  final RecordMicrophoneCaptureNow _now;
  final Map<String, String> _privateArtifacts = <String, String>{};

  bool _isCapturing = false;
  bool _isDisposed = false;
  String? _activePrivatePath;
  DateTime? _startedAt;

  @override
  bool get isCapturing => _isCapturing;

  @override
  Future<void> start(MicrophoneCaptureRequest request) async {
    if (_isDisposed) {
      throw const MicrophoneCaptureEngineException(
        'record_capture_engine_disposed',
      );
    }
    if (_isCapturing || _activePrivatePath != null) {
      throw const MicrophoneCaptureEngineException('record_capture_busy');
    }

    String privatePath;
    try {
      privatePath = await _privateFileSystem.allocatePrivatePath();
    } on MicrophoneCaptureEngineException {
      rethrow;
    } catch (_) {
      throw const MicrophoneCaptureEngineException(
        'record_private_path_allocation_failed',
      );
    }

    _activePrivatePath = privatePath;
    _startedAt = _now();

    try {
      await _driver.start(
        RecordMicrophoneCaptureDriverRequest(privatePath: privatePath),
      );
      _isCapturing = true;
    } catch (_) {
      await _bestEffortCancelDriver();
      await _bestEffortDelete(privatePath);
      _clearActiveCapture();
      throw const MicrophoneCaptureEngineException(
        'record_capture_start_failed',
      );
    }
  }

  @override
  Future<MicrophoneCaptureEngineResult> stop() async {
    final expectedPath = _activePrivatePath;
    final startedAt = _startedAt;
    if (!_isCapturing || expectedPath == null || startedAt == null) {
      throw const MicrophoneCaptureEngineException(
        'record_capture_not_active',
      );
    }

    String? stoppedPath;
    try {
      stoppedPath = await _driver.stop();
    } catch (_) {
      throw const MicrophoneCaptureEngineException(
        'record_capture_stop_failed',
      );
    }

    _isCapturing = false;
    if (stoppedPath == null || stoppedPath.isEmpty) {
      await _bestEffortDelete(expectedPath);
      _clearActiveCapture();
      throw const MicrophoneCaptureEngineException(
        'record_capture_artifact_missing',
      );
    }
    if (stoppedPath != expectedPath ||
        !_privateFileSystem.ownsPrivatePath(expectedPath)) {
      await _bestEffortDelete(expectedPath);
      _clearActiveCapture();
      throw const MicrophoneCaptureEngineException(
        'record_capture_artifact_path_mismatch',
      );
    }

    final opaqueCaptureId = _nextUniqueOpaqueId();
    if (opaqueCaptureId == null) {
      await _bestEffortDelete(expectedPath);
      _clearActiveCapture();
      throw const MicrophoneCaptureEngineException(
        'record_capture_opaque_id_failed',
      );
    }

    _privateArtifacts[opaqueCaptureId] = expectedPath;
    final capturedDuration = _nonNegativeDuration(_now().difference(startedAt));
    _clearActiveCapture();

    return MicrophoneCaptureEngineResult(
      opaqueCaptureId: opaqueCaptureId,
      capturedDuration: capturedDuration,
      publicMetadata: <String, Object?>{
        'engine': 'record',
        'record_version': '6.2.1',
        'encoding': 'wav',
        'sample_rate_hz': 16000,
        'channels': 1,
        'microphone_accessed': _driver.accessesRealMicrophone,
        'audio_captured': _driver.accessesRealMicrophone,
        'raw_audio_exposed': false,
        'private_artifact_registered': true,
      },
    );
  }

  @override
  Future<void> cancel() async {
    if (_isDisposed) {
      return;
    }

    final privatePath = _activePrivatePath;
    Object? failure;
    if (_isCapturing || privatePath != null) {
      try {
        await _driver.cancel();
      } catch (error) {
        failure = error;
      }
    }
    if (privatePath != null) {
      try {
        await _privateFileSystem.deletePrivatePath(privatePath);
      } catch (error) {
        failure ??= error;
      }
    }
    _clearActiveCapture();

    if (failure != null) {
      throw const MicrophoneCaptureEngineException(
        'record_capture_cancel_failed',
      );
    }
  }

  @override
  String? resolvePrivateArtifactPath(String opaqueCaptureId) {
    return _privateArtifacts[opaqueCaptureId];
  }

  @override
  Future<bool> discardPrivateArtifact(String opaqueCaptureId) async {
    final privatePath = _privateArtifacts.remove(opaqueCaptureId);
    if (privatePath == null) {
      return false;
    }
    try {
      await _privateFileSystem.deletePrivatePath(privatePath);
      return true;
    } catch (_) {
      _privateArtifacts[opaqueCaptureId] = privatePath;
      return false;
    }
  }

  @override
  Future<void> dispose() async {
    if (_isDisposed) {
      return;
    }

    Object? failure;
    try {
      await cancel();
    } catch (error) {
      failure = error;
    }

    final artifactIds = _privateArtifacts.keys.toList(growable: false);
    for (final artifactId in artifactIds) {
      final deleted = await discardPrivateArtifact(artifactId);
      if (!deleted) {
        failure ??= StateError('private artifact cleanup failed');
      }
    }

    try {
      await _driver.dispose();
    } catch (error) {
      failure ??= error;
    }
    _isDisposed = true;

    if (failure != null) {
      throw const MicrophoneCaptureEngineException(
        'record_capture_dispose_failed',
      );
    }
  }

  static String _defaultOpaqueId() {
    final token = List<int>.generate(
      16,
      (_) => _opaqueRandom.nextInt(256),
      growable: false,
    ).map((value) => value.toRadixString(16).padLeft(2, '0')).join();
    return 'record-capture-$token';
  }

  String? _nextUniqueOpaqueId() {
    for (var attempt = 0; attempt < 8; attempt += 1) {
      final candidate = _opaqueIdGenerator().trim();
      if (candidate.isNotEmpty && !_privateArtifacts.containsKey(candidate)) {
        return candidate;
      }
    }
    return null;
  }

  Duration _nonNegativeDuration(Duration value) {
    return value.isNegative ? Duration.zero : value;
  }

  Future<void> _bestEffortCancelDriver() async {
    try {
      await _driver.cancel();
    } catch (_) {
      // The original typed start failure remains authoritative.
    }
  }

  Future<void> _bestEffortDelete(String privatePath) async {
    try {
      await _privateFileSystem.deletePrivatePath(privatePath);
    } catch (_) {
      // The original typed failure remains authoritative.
    }
  }

  void _clearActiveCapture() {
    _isCapturing = false;
    _activePrivatePath = null;
    _startedAt = null;
  }
}
