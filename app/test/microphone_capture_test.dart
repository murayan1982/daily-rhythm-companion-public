import 'package:app/services/microphone_capture.dart';
import 'package:app/services/microphone_permission.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('MicrophoneCaptureController', () {
    test('starts idle with no active capture', () {
      final fixture = _fixture();

      expect(fixture.controller.state.phase, MicrophoneCapturePhase.idle);
      expect(fixture.controller.state.isActive, isFalse);
      expect(fixture.controller.state.canStart, isTrue);
      expect(fixture.engine.isCapturing, isFalse);

      fixture.controller.dispose();
    });

    test('granted permission starts only the fake engine', () async {
      final fixture = _fixture();

      final result = await fixture.controller.start(
        MicrophoneCaptureRequest(maxDuration: const Duration(seconds: 10)),
      );

      expect(result.outcome, MicrophoneCaptureOutcome.started);
      expect(fixture.controller.state.phase, MicrophoneCapturePhase.capturing);
      expect(fixture.permission.checkCalls, 1);
      expect(fixture.permission.requestCalls, 0);
      expect(fixture.engine.startCalls, 1);
      expect(fixture.engine.isCapturing, isTrue);
      expect(result.publicMetadata['microphone_accessed'], isFalse);
      expect(result.publicMetadata['audio_captured'], isFalse);

      await fixture.controller.close();
    });

    test('denied permission stays typed and never starts the engine', () async {
      final fixture = _fixture(status: MicrophonePermissionStatus.denied);

      final result = await fixture.controller.start(MicrophoneCaptureRequest());

      expect(result.outcome, MicrophoneCaptureOutcome.denied);
      expect(fixture.controller.state.phase, MicrophoneCapturePhase.denied);
      expect(fixture.engine.startCalls, 0);
      expect(fixture.permission.requestCalls, 0);

      await fixture.controller.close();
    });

    test('permanently denied remains distinct and points to settings', () async {
      final fixture = _fixture(
        status: MicrophonePermissionStatus.permanentlyDenied,
      );

      final result = await fixture.controller.start(MicrophoneCaptureRequest());

      expect(result.outcome, MicrophoneCaptureOutcome.permanentlyDenied);
      expect(
        fixture.controller.state.phase,
        MicrophoneCapturePhase.permanentlyDenied,
      );
      expect(result.publicMetadata['can_open_settings'], isTrue);
      expect(fixture.permission.openSettingsCalls, 0);
      expect(fixture.engine.startCalls, 0);

      await fixture.controller.close();
    });

    test('restricted permission remains distinct', () async {
      final fixture = _fixture(status: MicrophonePermissionStatus.restricted);

      final result = await fixture.controller.start(MicrophoneCaptureRequest());

      expect(result.outcome, MicrophoneCaptureOutcome.restricted);
      expect(fixture.controller.state.phase, MicrophoneCapturePhase.restricted);
      expect(fixture.engine.startCalls, 0);

      await fixture.controller.close();
    });

    test('unsupported permission fails closed', () async {
      final fixture = _fixture(status: MicrophonePermissionStatus.unsupported);

      final result = await fixture.controller.start(MicrophoneCaptureRequest());

      expect(result.outcome, MicrophoneCaptureOutcome.unsupported);
      expect(fixture.controller.state.phase, MicrophoneCapturePhase.unsupported);
      expect(fixture.engine.startCalls, 0);

      await fixture.controller.close();
    });

    test('a second start is busy and preserves the active capture', () async {
      final fixture = _fixture();
      await fixture.controller.start(MicrophoneCaptureRequest());

      final result = await fixture.controller.start(MicrophoneCaptureRequest());

      expect(result.outcome, MicrophoneCaptureOutcome.busy);
      expect(fixture.controller.state.phase, MicrophoneCapturePhase.capturing);
      expect(fixture.engine.startCalls, 1);
      expect(fixture.permission.checkCalls, 1);

      await fixture.controller.close();
    });

    test('duration must be positive and within the hard maximum', () async {
      final fixture = _fixture(maximumDuration: const Duration(seconds: 20));

      final invalid = await fixture.controller.start(
        MicrophoneCaptureRequest(maxDuration: Duration.zero),
      );
      final excessive = await fixture.controller.start(
        MicrophoneCaptureRequest(maxDuration: const Duration(seconds: 21)),
      );

      expect(invalid.technicalCode, 'capture_duration_invalid');
      expect(excessive.technicalCode, 'capture_duration_exceeds_limit');
      expect(fixture.permission.checkCalls, 0);
      expect(fixture.engine.startCalls, 0);

      await fixture.controller.close();
    });

    test('stop returns only opaque fake completion data', () async {
      final fixture = _fixture();
      await fixture.controller.start(MicrophoneCaptureRequest());

      final result = await fixture.controller.stop();

      expect(result.outcome, MicrophoneCaptureOutcome.completed);
      expect(fixture.controller.state.phase, MicrophoneCapturePhase.completed);
      expect(result.engineResult?.opaqueCaptureId, 'fake-capture-1');
      expect(result.engineResult?.capturedDuration, const Duration(seconds: 1));
      expect(result.engineResult?.publicMetadata['microphone_accessed'], isFalse);
      expect(result.engineResult?.publicMetadata['audio_captured'], isFalse);
      expect(result.engineResult?.publicMetadata['raw_audio_exposed'], isFalse);
      expect(fixture.engine.stopCalls, 1);
      expect(fixture.scheduler.lastDeadline?.cancelled, isTrue);

      await fixture.controller.close();
    });

    test('cancel stops the fake lifecycle without producing an artifact', () async {
      final fixture = _fixture();
      await fixture.controller.start(MicrophoneCaptureRequest());

      final result = await fixture.controller.cancel();

      expect(result.outcome, MicrophoneCaptureOutcome.cancelled);
      expect(fixture.controller.state.phase, MicrophoneCapturePhase.cancelled);
      expect(result.engineResult, isNull);
      expect(fixture.engine.cancelCalls, 1);
      expect(fixture.engine.isCapturing, isFalse);
      expect(fixture.scheduler.lastDeadline?.cancelled, isTrue);

      await fixture.controller.close();
    });

    test('deadline produces a typed timeout and cleanup', () async {
      final fixture = _fixture();
      await fixture.controller.start(
        MicrophoneCaptureRequest(maxDuration: const Duration(seconds: 7)),
      );

      expect(fixture.scheduler.lastDuration, const Duration(seconds: 7));
      fixture.scheduler.fire();
      await Future<void>.delayed(Duration.zero);

      expect(fixture.controller.state.phase, MicrophoneCapturePhase.timedOut);
      expect(
        fixture.controller.state.lastResult?.outcome,
        MicrophoneCaptureOutcome.timedOut,
      );
      expect(fixture.engine.cancelCalls, 1);
      expect(fixture.engine.isCapturing, isFalse);

      await fixture.controller.close();
    });

    test('start failure cleans a partially active fake engine', () async {
      final engine = FakeMicrophoneCaptureEngine(
        activateBeforeStartError: true,
        startError: const MicrophoneCaptureEngineException(
          'fake_partial_start_failed',
        ),
      );
      final fixture = _fixture(engine: engine);

      final result = await fixture.controller.start(MicrophoneCaptureRequest());

      expect(result.outcome, MicrophoneCaptureOutcome.failed);
      expect(result.technicalCode, 'fake_partial_start_failed');
      expect(result.publicMetadata['cleanup_succeeded'], isTrue);
      expect(engine.cancelCalls, 1);
      expect(engine.isCapturing, isFalse);

      await fixture.controller.close();
    });

    test('stop failure attempts cancellation cleanup', () async {
      final engine = FakeMicrophoneCaptureEngine(
        stopError: const MicrophoneCaptureEngineException('fake_stop_failed'),
      );
      final fixture = _fixture(engine: engine);
      await fixture.controller.start(MicrophoneCaptureRequest());

      final result = await fixture.controller.stop();

      expect(result.outcome, MicrophoneCaptureOutcome.failed);
      expect(result.technicalCode, 'fake_stop_failed');
      expect(result.publicMetadata['cleanup_succeeded'], isTrue);
      expect(engine.cancelCalls, 1);
      expect(engine.isCapturing, isFalse);

      await fixture.controller.close();
    });

    test('cancel cleanup failure stays typed and safe', () async {
      final engine = FakeMicrophoneCaptureEngine(
        cancelError: StateError('private native payload'),
      );
      final fixture = _fixture(engine: engine);
      await fixture.controller.start(MicrophoneCaptureRequest());

      final result = await fixture.controller.cancel();

      expect(result.outcome, MicrophoneCaptureOutcome.failed);
      expect(result.technicalCode, 'capture_cancel_cleanup_failed');
      expect(result.publicMetadata['cleanup_succeeded'], isFalse);
      expect(result.publicMetadata.values, isNot(contains('private native payload')));

      await fixture.controller.close();
    });

    test('permission check exception is converted without raw details', () async {
      final engine = FakeMicrophoneCaptureEngine();
      final controller = MicrophoneCaptureController(
        permissionGateway: _ThrowingPermissionGateway(),
        engine: engine,
        deadlineScheduler: _FakeDeadlineScheduler(),
      );

      final result = await controller.start(MicrophoneCaptureRequest());

      expect(result.outcome, MicrophoneCaptureOutcome.failed);
      expect(result.technicalCode, 'capture_permission_check_failed');
      expect(result.publicMetadata.values, isNot(contains('private permission payload')));
      expect(engine.startCalls, 0);

      await controller.close();
    });

    test('close cancels an active fake capture and disposes the engine', () async {
      final fixture = _fixture();
      await fixture.controller.start(MicrophoneCaptureRequest());

      await fixture.controller.close();

      expect(fixture.engine.cancelCalls, 1);
      expect(fixture.engine.disposeCalls, 1);
      expect(fixture.engine.isCapturing, isFalse);
      expect(fixture.scheduler.lastDeadline?.cancelled, isTrue);

      final closedResult = await fixture.controller.start(
        MicrophoneCaptureRequest(),
      );
      expect(closedResult.technicalCode, 'capture_controller_closed');
    });

    test('request and result metadata are immutable', () {
      final requestMetadata = <String, Object?>{'source': 'test'};
      final request = MicrophoneCaptureRequest(publicMetadata: requestMetadata);
      requestMetadata['source'] = 'changed';

      final resultMetadata = <String, Object?>{'engine': 'fake'};
      final result = MicrophoneCaptureEngineResult(
        opaqueCaptureId: 'opaque',
        capturedDuration: Duration.zero,
        publicMetadata: resultMetadata,
      );
      resultMetadata['engine'] = 'changed';

      expect(request.publicMetadata['source'], 'test');
      expect(result.publicMetadata['engine'], 'fake');
      expect(
        () => request.publicMetadata['extra'] = true,
        throwsUnsupportedError,
      );
      expect(
        () => result.publicMetadata['extra'] = true,
        throwsUnsupportedError,
      );
    });
  });
}

_Fixture _fixture({
  MicrophonePermissionStatus status = MicrophonePermissionStatus.granted,
  FakeMicrophoneCaptureEngine? engine,
  Duration maximumDuration = const Duration(seconds: 60),
}) {
  final permission = FakeMicrophonePermissionGateway(initialStatus: status);
  final captureEngine = engine ?? FakeMicrophoneCaptureEngine();
  final scheduler = _FakeDeadlineScheduler();
  final controller = MicrophoneCaptureController(
    permissionGateway: permission,
    engine: captureEngine,
    deadlineScheduler: scheduler,
    maximumAllowedDuration: maximumDuration,
  );
  return _Fixture(controller, permission, captureEngine, scheduler);
}

class _Fixture {
  const _Fixture(
    this.controller,
    this.permission,
    this.engine,
    this.scheduler,
  );

  final MicrophoneCaptureController controller;
  final FakeMicrophonePermissionGateway permission;
  final FakeMicrophoneCaptureEngine engine;
  final _FakeDeadlineScheduler scheduler;
}

class _FakeDeadlineScheduler implements MicrophoneCaptureDeadlineScheduler {
  Duration? lastDuration;
  _FakeDeadline? lastDeadline;
  void Function()? _callback;

  @override
  MicrophoneCaptureDeadline schedule(
    Duration duration,
    void Function() onDeadline,
  ) {
    lastDuration = duration;
    _callback = onDeadline;
    final deadline = _FakeDeadline();
    lastDeadline = deadline;
    return deadline;
  }

  void fire() {
    if (lastDeadline?.cancelled ?? true) {
      return;
    }
    _callback?.call();
  }
}

class _FakeDeadline implements MicrophoneCaptureDeadline {
  bool cancelled = false;

  @override
  void cancel() {
    cancelled = true;
  }
}

class _ThrowingPermissionGateway implements MicrophonePermissionGateway {
  @override
  Future<MicrophonePermissionResult> checkPermission() {
    throw StateError('private permission payload');
  }

  @override
  Future<MicrophonePermissionResult> requestPermission() {
    throw UnimplementedError();
  }

  @override
  Future<MicrophonePermissionResult> openAppSettings() {
    throw UnimplementedError();
  }
}
