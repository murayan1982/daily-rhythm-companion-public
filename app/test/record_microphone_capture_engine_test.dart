import 'package:app/services/microphone_capture.dart';
import 'package:app/services/record_microphone_capture_engine.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('RecordMicrophoneCaptureEngine', () {
    test('start allocates a private mono WAV path through the fake driver',
        () async {
      final fixture = _fixture();

      await fixture.engine.start(MicrophoneCaptureRequest());

      expect(fixture.engine.isCapturing, isTrue);
      expect(fixture.driver.startCalls, 1);
      expect(fixture.driver.requests.single.privatePath, fixture.paths.firstPath);
      expect(fixture.driver.requests.single.sampleRate, 16000);
      expect(fixture.driver.requests.single.numChannels, 1);
      expect(fixture.paths.allocateCalls, 1);

      await fixture.engine.dispose();
    });

    test('second start is rejected without allocating another private path',
        () async {
      final fixture = _fixture();
      await fixture.engine.start(MicrophoneCaptureRequest());

      await expectLater(
        fixture.engine.start(MicrophoneCaptureRequest()),
        throwsA(
          isA<MicrophoneCaptureEngineException>().having(
            (error) => error.code,
            'code',
            'record_capture_busy',
          ),
        ),
      );

      expect(fixture.driver.startCalls, 1);
      expect(fixture.paths.allocateCalls, 1);
      await fixture.engine.dispose();
    });

    test('private path allocation failure is typed before driver start',
        () async {
      final fixture = _fixture(
        paths: _FakePrivateFileSystem(
          allocateError: StateError('sensitive allocation detail'),
        ),
      );

      await expectLater(
        fixture.engine.start(MicrophoneCaptureRequest()),
        throwsA(
          isA<MicrophoneCaptureEngineException>().having(
            (error) => error.code,
            'code',
            'record_private_path_allocation_failed',
          ),
        ),
      );

      expect(fixture.paths.allocateCalls, 1);
      expect(fixture.driver.startCalls, 0);
      expect(fixture.engine.isCapturing, isFalse);
    });

    test('start failure cancels the fake driver and removes the private path',
        () async {
      final fixture = _fixture(
        driver: _FakeRecordDriver(
          startError: StateError('sensitive native start payload'),
          activateBeforeStartError: true,
        ),
      );

      await expectLater(
        fixture.engine.start(MicrophoneCaptureRequest()),
        throwsA(
          isA<MicrophoneCaptureEngineException>().having(
            (error) => error.code,
            'code',
            'record_capture_start_failed',
          ),
        ),
      );

      expect(fixture.driver.cancelCalls, 1);
      expect(fixture.paths.deletedPaths, <String>[fixture.paths.firstPath]);
      expect(fixture.engine.isCapturing, isFalse);
      await fixture.engine.dispose();
    });

    test('stop returns an opaque id while the private path stays internal',
        () async {
      final start = DateTime.utc(2026, 7, 27, 12);
      final fixture = _fixture(
        nowValues: <DateTime>[start, start.add(const Duration(seconds: 3))],
      );
      await fixture.engine.start(MicrophoneCaptureRequest());

      final result = await fixture.engine.stop();

      expect(result.opaqueCaptureId, 'opaque-1');
      expect(result.capturedDuration, const Duration(seconds: 3));
      expect(result.publicMetadata['engine'], 'record');
      expect(result.publicMetadata['record_version'], '6.2.1');
      expect(result.publicMetadata['encoding'], 'wav');
      expect(result.publicMetadata['microphone_accessed'], isFalse);
      expect(result.publicMetadata['audio_captured'], isFalse);
      expect(result.publicMetadata['raw_audio_exposed'], isFalse);
      expect(result.publicMetadata['private_artifact_registered'], isTrue);
      expect(result.publicMetadata.values, isNot(contains(fixture.paths.firstPath)));
      expect(
        fixture.engine.resolvePrivateArtifactPath(result.opaqueCaptureId),
        fixture.paths.firstPath,
      );

      await fixture.engine.dispose();
    });

    test('driver capability controls safe microphone and audio metadata',
        () async {
      final fixture = _fixture(
        driver: _FakeRecordDriver(accessesRealMicrophone: true),
      );
      await fixture.engine.start(MicrophoneCaptureRequest());

      final result = await fixture.engine.stop();

      expect(result.publicMetadata['microphone_accessed'], isTrue);
      expect(result.publicMetadata['audio_captured'], isTrue);
      expect(result.publicMetadata['raw_audio_exposed'], isFalse);
      expect(result.publicMetadata, isNot(contains('private_path')));
      await fixture.engine.dispose();
    });

    test('missing stop artifact is typed and deletes the expected path',
        () async {
      final fixture = _fixture(
        driver: _FakeRecordDriver(stopPath: null),
        defaultStopPath: false,
      );
      await fixture.engine.start(MicrophoneCaptureRequest());

      await expectLater(
        fixture.engine.stop(),
        throwsA(
          isA<MicrophoneCaptureEngineException>().having(
            (error) => error.code,
            'code',
            'record_capture_artifact_missing',
          ),
        ),
      );

      expect(fixture.paths.deletedPaths, <String>[fixture.paths.firstPath]);
      expect(fixture.engine.isCapturing, isFalse);
      await fixture.engine.dispose();
    });

    test('unexpected stop path is rejected without registering it', () async {
      final fixture = _fixture(
        driver: _FakeRecordDriver(stopPath: '<outside>/unexpected.wav'),
      );
      await fixture.engine.start(MicrophoneCaptureRequest());

      await expectLater(
        fixture.engine.stop(),
        throwsA(
          isA<MicrophoneCaptureEngineException>().having(
            (error) => error.code,
            'code',
            'record_capture_artifact_path_mismatch',
          ),
        ),
      );

      expect(fixture.paths.deletedPaths, <String>[fixture.paths.firstPath]);
      expect(fixture.engine.resolvePrivateArtifactPath('opaque-1'), isNull);
      await fixture.engine.dispose();
    });

    test('stop failure remains active so controller cleanup can cancel',
        () async {
      final fixture = _fixture(
        driver: _FakeRecordDriver(
          stopError: StateError('sensitive native stop payload'),
        ),
      );
      await fixture.engine.start(MicrophoneCaptureRequest());

      await expectLater(
        fixture.engine.stop(),
        throwsA(
          isA<MicrophoneCaptureEngineException>().having(
            (error) => error.code,
            'code',
            'record_capture_stop_failed',
          ),
        ),
      );

      expect(fixture.engine.isCapturing, isTrue);
      await fixture.engine.cancel();
      expect(fixture.driver.cancelCalls, 1);
      expect(fixture.paths.deletedPaths, <String>[fixture.paths.firstPath]);
      expect(fixture.engine.isCapturing, isFalse);
      await fixture.engine.dispose();
    });

    test('cancel removes the partial artifact and returns no public result',
        () async {
      final fixture = _fixture();
      await fixture.engine.start(MicrophoneCaptureRequest());

      await fixture.engine.cancel();

      expect(fixture.driver.cancelCalls, 1);
      expect(fixture.paths.deletedPaths, <String>[fixture.paths.firstPath]);
      expect(fixture.engine.resolvePrivateArtifactPath('opaque-1'), isNull);
      expect(fixture.engine.isCapturing, isFalse);
      await fixture.engine.dispose();
    });

    test('cancel failure is typed after best-effort private path cleanup',
        () async {
      final fixture = _fixture(
        driver: _FakeRecordDriver(
          cancelError: StateError('sensitive native cancel payload'),
        ),
      );
      await fixture.engine.start(MicrophoneCaptureRequest());

      await expectLater(
        fixture.engine.cancel(),
        throwsA(
          isA<MicrophoneCaptureEngineException>().having(
            (error) => error.code,
            'code',
            'record_capture_cancel_failed',
          ),
        ),
      );

      expect(fixture.paths.deletedPaths, <String>[fixture.paths.firstPath]);
      expect(fixture.engine.isCapturing, isFalse);
      await fixture.engine.dispose();
    });

    test('discard deletes a registered private artifact exactly once',
        () async {
      final fixture = _fixture();
      await fixture.engine.start(MicrophoneCaptureRequest());
      final result = await fixture.engine.stop();

      final first = await fixture.engine.discardPrivateArtifact(
        result.opaqueCaptureId,
      );
      final second = await fixture.engine.discardPrivateArtifact(
        result.opaqueCaptureId,
      );

      expect(first, isTrue);
      expect(second, isFalse);
      expect(fixture.paths.deletedPaths, <String>[fixture.paths.firstPath]);
      expect(
        fixture.engine.resolvePrivateArtifactPath(result.opaqueCaptureId),
        isNull,
      );
      await fixture.engine.dispose();
    });

    test('discard delete failure keeps the opaque artifact retriable',
        () async {
      final paths = _FakePrivateFileSystem(
        deleteError: StateError('sensitive delete detail'),
      );
      final fixture = _fixture(paths: paths);
      await fixture.engine.start(MicrophoneCaptureRequest());
      final result = await fixture.engine.stop();

      final deleted = await fixture.engine.discardPrivateArtifact(
        result.opaqueCaptureId,
      );

      expect(deleted, isFalse);
      expect(
        fixture.engine.resolvePrivateArtifactPath(result.opaqueCaptureId),
        fixture.paths.firstPath,
      );
      expect(fixture.paths.deletedPaths, isEmpty);
    });

    test('dispose cancels active capture and disposes the fake driver',
        () async {
      final fixture = _fixture();
      await fixture.engine.start(MicrophoneCaptureRequest());

      await fixture.engine.dispose();

      expect(fixture.driver.cancelCalls, 1);
      expect(fixture.driver.disposeCalls, 1);
      expect(fixture.paths.deletedPaths, <String>[fixture.paths.firstPath]);
      expect(fixture.engine.isCapturing, isFalse);
    });

    test('driver dispose failure is converted to a typed engine error',
        () async {
      final fixture = _fixture(
        driver: _FakeRecordDriver(
          disposeError: StateError('sensitive dispose detail'),
        ),
      );

      await expectLater(
        fixture.engine.dispose(),
        throwsA(
          isA<MicrophoneCaptureEngineException>().having(
            (error) => error.code,
            'code',
            'record_capture_dispose_failed',
          ),
        ),
      );

      expect(fixture.driver.disposeCalls, 1);
      expect(fixture.engine.isCapturing, isFalse);
    });

    test('dispose deletes completed artifacts that were not consumed',
        () async {
      final fixture = _fixture();
      await fixture.engine.start(MicrophoneCaptureRequest());
      final result = await fixture.engine.stop();
      expect(
        fixture.engine.resolvePrivateArtifactPath(result.opaqueCaptureId),
        fixture.paths.firstPath,
      );

      await fixture.engine.dispose();

      expect(fixture.paths.deletedPaths, <String>[fixture.paths.firstPath]);
      expect(
        fixture.engine.resolvePrivateArtifactPath(result.opaqueCaptureId),
        isNull,
      );
      expect(fixture.driver.disposeCalls, 1);
    });

    test('opaque id collision fails closed and removes the second artifact',
        () async {
      final paths = _FakePrivateFileSystem(
        paths: <String>['<private>/one.wav', '<private>/two.wav'],
      );
      final fixture = _fixture(
        paths: paths,
        opaqueIds: List<String>.filled(10, 'opaque-duplicate'),
      );
      await fixture.engine.start(MicrophoneCaptureRequest());
      final first = await fixture.engine.stop();
      expect(first.opaqueCaptureId, 'opaque-duplicate');

      fixture.driver.stopPath = '<private>/two.wav';
      await fixture.engine.start(MicrophoneCaptureRequest());
      await expectLater(
        fixture.engine.stop(),
        throwsA(
          isA<MicrophoneCaptureEngineException>().having(
            (error) => error.code,
            'code',
            'record_capture_opaque_id_failed',
          ),
        ),
      );

      expect(paths.deletedPaths, <String>['<private>/two.wav']);
      expect(
        fixture.engine.resolvePrivateArtifactPath(first.opaqueCaptureId),
        '<private>/one.wav',
      );
      await fixture.engine.dispose();
    });

    test('disposed engine rejects later starts without invoking the driver',
        () async {
      final fixture = _fixture();
      await fixture.engine.dispose();

      await expectLater(
        fixture.engine.start(MicrophoneCaptureRequest()),
        throwsA(
          isA<MicrophoneCaptureEngineException>().having(
            (error) => error.code,
            'code',
            'record_capture_engine_disposed',
          ),
        ),
      );

      expect(fixture.driver.startCalls, 0);
    });
  });
}

_Fixture _fixture({
  _FakeRecordDriver? driver,
  _FakePrivateFileSystem? paths,
  List<String> opaqueIds = const <String>['opaque-1'],
  List<DateTime>? nowValues,
  bool defaultStopPath = true,
}) {
  final captureDriver = driver ?? _FakeRecordDriver();
  final privatePaths = paths ?? _FakePrivateFileSystem();
  if (defaultStopPath) {
    captureDriver.stopPath ??= privatePaths.firstPath;
  }

  var idIndex = 0;
  String nextOpaqueId() {
    final safeIndex = idIndex < opaqueIds.length ? idIndex : opaqueIds.length - 1;
    idIndex += 1;
    return opaqueIds[safeIndex];
  }

  final times = nowValues ??
      <DateTime>[
        DateTime.utc(2026, 7, 27, 12),
        DateTime.utc(2026, 7, 27, 12, 0, 1),
      ];
  var timeIndex = 0;
  DateTime now() {
    final safeIndex = timeIndex < times.length ? timeIndex : times.length - 1;
    timeIndex += 1;
    return times[safeIndex];
  }

  final engine = RecordMicrophoneCaptureEngine(
    driver: captureDriver,
    privateFileSystem: privatePaths,
    opaqueIdGenerator: nextOpaqueId,
    now: now,
  );
  return _Fixture(engine, captureDriver, privatePaths);
}

class _Fixture {
  const _Fixture(this.engine, this.driver, this.paths);

  final RecordMicrophoneCaptureEngine engine;
  final _FakeRecordDriver driver;
  final _FakePrivateFileSystem paths;
}

class _FakeRecordDriver implements RecordMicrophoneCaptureDriver {
  _FakeRecordDriver({
    this.accessesRealMicrophone = false,
    this.stopPath,
    this.startError,
    this.stopError,
    this.cancelError,
    this.disposeError,
    this.activateBeforeStartError = false,
  });

  @override
  final bool accessesRealMicrophone;
  String? stopPath;
  final Object? startError;
  final Object? stopError;
  final Object? cancelError;
  final Object? disposeError;
  final bool activateBeforeStartError;

  final List<RecordMicrophoneCaptureDriverRequest> requests =
      <RecordMicrophoneCaptureDriverRequest>[];
  int startCalls = 0;
  int stopCalls = 0;
  int cancelCalls = 0;
  int disposeCalls = 0;
  bool active = false;

  @override
  Future<void> start(RecordMicrophoneCaptureDriverRequest request) async {
    startCalls += 1;
    requests.add(request);
    if (activateBeforeStartError) {
      active = true;
    }
    if (startError != null) {
      throw startError!;
    }
    active = true;
  }

  @override
  Future<String?> stop() async {
    stopCalls += 1;
    if (stopError != null) {
      throw stopError!;
    }
    active = false;
    return stopPath;
  }

  @override
  Future<void> cancel() async {
    cancelCalls += 1;
    active = false;
    if (cancelError != null) {
      throw cancelError!;
    }
  }

  @override
  Future<void> dispose() async {
    disposeCalls += 1;
    active = false;
    if (disposeError != null) {
      throw disposeError!;
    }
  }
}

class _FakePrivateFileSystem
    implements RecordMicrophoneCapturePrivateFileSystem {
  _FakePrivateFileSystem({
    List<String> paths = const <String>['<private>/capture.wav'],
    this.allocateError,
    this.deleteError,
  }) : _paths = List<String>.from(paths);

  final List<String> _paths;
  final Object? allocateError;
  final Object? deleteError;
  final Set<String> _ownedPaths = <String>{};
  final List<String> deletedPaths = <String>[];
  int allocateCalls = 0;

  String get firstPath => _paths.first;

  @override
  Future<String> allocatePrivatePath() async {
    allocateCalls += 1;
    if (allocateError != null) {
      throw allocateError!;
    }
    final index = allocateCalls - 1;
    final path = index < _paths.length ? _paths[index] : _paths.last;
    _ownedPaths.add(path);
    return path;
  }

  @override
  bool ownsPrivatePath(String path) => _ownedPaths.contains(path);

  @override
  Future<void> deletePrivatePath(String path) async {
    if (deleteError != null) {
      throw deleteError!;
    }
    if (_ownedPaths.remove(path)) {
      deletedPaths.add(path);
    }
  }
}
