import 'package:app/operators/rt2ec_microphone_capture_operator.dart';
import 'package:app/services/microphone_capture.dart';
import 'package:app/services/microphone_permission.dart';
import 'package:app/services/record_microphone_capture_engine.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('disabled target renders blocked screen without dependencies', (
    tester,
  ) async {
    var factoryCalls = 0;

    await tester.pumpWidget(
      Rt2ecOperatorCaptureApp(
        operatorTargetEnabled: false,
        dependenciesFactory: () {
          factoryCalls += 1;
          throw StateError('must not construct dependencies');
        },
      ),
    );

    expect(find.text('operator target enabled: false'), findsOneWidget);
    expect(find.byKey(rt2ecOperatorAcknowledgementKey), findsNothing);
    expect(factoryCalls, 0);
  });

  testWidgets('compile-time opt-in still requires in-app acknowledgement', (
    tester,
  ) async {
    final fixture = _Fixture();

    await _pumpBootstrap(tester, fixture);

    expect(find.byKey(rt2ecOperatorAcknowledgementKey), findsOneWidget);
    expect(_filledButton(tester, rt2ecOperatorActivateKey).onPressed, isNull);
    expect(fixture.factoryCalls, 0);
    expect(fixture.permission.checkCalls, 0);
    expect(fixture.permission.requestCalls, 0);
    expect(fixture.engine.startCalls, 0);
  });

  testWidgets('acknowledgement constructs fakes but performs no startup action', (
    tester,
  ) async {
    final fixture = _Fixture();

    await _activateHarness(tester, fixture);

    expect(fixture.factoryCalls, 1);
    expect(fixture.permission.checkCalls, 0);
    expect(fixture.permission.requestCalls, 0);
    expect(fixture.engine.startCalls, 0);
    expect(find.text('acknowledgement completed: true'), findsOneWidget);
    expect(_filledButton(tester, rt2ecOperatorCaptureStartKey).onPressed, isNull);
  });

  testWidgets('permission check is explicit and enables start only when granted', (
    tester,
  ) async {
    final fixture = _Fixture(
      initialPermission: MicrophonePermissionStatus.granted,
    );
    await _activateHarness(tester, fixture);

    await tester.tap(find.byKey(rt2ecOperatorPermissionCheckKey));
    await tester.pumpAndSettle();

    expect(fixture.permission.checkCalls, 1);
    expect(fixture.permission.requestCalls, 0);
    expect(find.text('permission status: granted'), findsOneWidget);
    expect(
      _filledButton(tester, rt2ecOperatorCaptureStartKey).onPressed,
      isNotNull,
    );
  });

  testWidgets('permission request remains a separate explicit action', (
    tester,
  ) async {
    final fixture = _Fixture(
      initialPermission: MicrophonePermissionStatus.denied,
      requestSequence: const <MicrophonePermissionStatus>[
        MicrophonePermissionStatus.granted,
      ],
    );
    await _activateHarness(tester, fixture);

    await tester.tap(find.byKey(rt2ecOperatorPermissionRequestKey));
    await tester.pumpAndSettle();

    expect(fixture.permission.checkCalls, 0);
    expect(fixture.permission.requestCalls, 1);
    expect(find.text('permission request attempted: true'), findsOneWidget);
    expect(find.text('permission status: granted'), findsOneWidget);
  });

  testWidgets('start uses exactly the bounded 15-second fake request', (
    tester,
  ) async {
    final fixture = _Fixture(
      initialPermission: MicrophonePermissionStatus.granted,
    );
    await _activateHarness(tester, fixture);
    await _checkPermissionAndStart(tester);

    expect(fixture.engine.startCalls, 1);
    expect(fixture.engine.requests, hasLength(1));
    expect(
      fixture.engine.requests.single.maxDuration,
      rt2ecOperatorMaximumCaptureDuration,
    );
    expect(fixture.controller.maximumAllowedDuration,
        rt2ecOperatorMaximumCaptureDuration);
    expect(find.text('capture phase: capturing'), findsOneWidget);
    expect(find.text('microphone accessed: false'), findsOneWidget);
    expect(find.text('audio captured: false'), findsOneWidget);
  });

  testWidgets('completed stop immediately discards by opaque id', (
    tester,
  ) async {
    final fixture = _Fixture(
      initialPermission: MicrophonePermissionStatus.granted,
    );
    await _activateHarness(tester, fixture);
    await _checkPermissionAndStart(tester);

    await tester.tap(find.byKey(rt2ecOperatorCaptureStopKey));
    await tester.pumpAndSettle();

    expect(fixture.engine.stopCalls, 1);
    expect(fixture.artifacts.discardedIds, <String>['opaque-internal-1']);
    expect(find.text('capture outcome: completed'), findsOneWidget);
    expect(find.text('private artifact registered: true'), findsOneWidget);
    expect(find.text('private artifact discarded: true'), findsOneWidget);
    expect(find.text('cleanup succeeded: true'), findsOneWidget);
    expect(find.textContaining('opaque-internal-1'), findsNothing);
    expect(find.textContaining('forbidden-private-path'), findsNothing);
  });

  testWidgets('cancel is explicit and creates no completed artifact', (
    tester,
  ) async {
    final fixture = _Fixture(
      initialPermission: MicrophonePermissionStatus.granted,
    );
    await _activateHarness(tester, fixture);
    await _checkPermissionAndStart(tester);

    await tester.tap(find.byKey(rt2ecOperatorCaptureCancelKey));
    await tester.pumpAndSettle();

    expect(fixture.engine.cancelCalls, 1);
    expect(fixture.artifacts.discardedIds, isEmpty);
    expect(find.text('capture outcome: cancelled'), findsOneWidget);
    expect(find.text('private artifact discarded: false'), findsOneWidget);
  });

  testWidgets('denied permission never starts capture', (tester) async {
    final fixture = _Fixture(
      initialPermission: MicrophonePermissionStatus.denied,
    );
    await _activateHarness(tester, fixture);

    await tester.tap(find.byKey(rt2ecOperatorPermissionCheckKey));
    await tester.pumpAndSettle();

    expect(find.text('permission status: denied'), findsOneWidget);
    expect(_filledButton(tester, rt2ecOperatorCaptureStartKey).onPressed, isNull);
    expect(fixture.engine.startCalls, 0);
  });

  test('safe evidence map contains only the accepted allowlist', () {
    const evidence = Rt2ecOperatorCaptureEvidence(
      operatorTargetEnabled: true,
      acknowledgementCompleted: true,
      permissionStatus: 'granted',
      permissionRequestAttempted: true,
      capturePhase: 'completed',
      captureOutcome: 'completed',
      technicalCode: 'capture_completed',
      requestedMaximumDurationMilliseconds: 15000,
      capturedDurationMilliseconds: 1200,
      microphoneAccessed: false,
      audioCaptured: false,
      rawAudioExposed: false,
      privateArtifactRegistered: true,
      privateArtifactDiscarded: true,
      cleanupSucceeded: true,
    );

    expect(
      evidence.toSafeMap().keys,
      <String>[
        'operator target enabled',
        'acknowledgement completed',
        'permission status',
        'permission request attempted',
        'capture phase',
        'capture outcome',
        'technical code',
        'requested maximum duration',
        'captured duration',
        'microphone accessed',
        'audio captured',
        'raw audio exposed',
        'private artifact registered',
        'private artifact discarded',
        'cleanup succeeded',
      ],
    );
    expect(evidence.toSafeMap(), isNot(contains('opaque capture id')));
    expect(evidence.toSafeMap(), isNot(contains('private path')));
    expect(evidence.toSafeMap(), isNot(contains('raw audio bytes')));
  });
}

Future<void> _pumpBootstrap(WidgetTester tester, _Fixture fixture) async {
  await tester.pumpWidget(
    Rt2ecOperatorCaptureApp(
      operatorTargetEnabled: true,
      dependenciesFactory: fixture.createDependencies,
    ),
  );
  await tester.pumpAndSettle();
}

Future<void> _activateHarness(WidgetTester tester, _Fixture fixture) async {
  await _pumpBootstrap(tester, fixture);
  await tester.tap(find.byKey(rt2ecOperatorAcknowledgementKey));
  await tester.pumpAndSettle();
  await tester.tap(find.byKey(rt2ecOperatorActivateKey));
  await tester.pumpAndSettle();
}

Future<void> _checkPermissionAndStart(WidgetTester tester) async {
  await tester.tap(find.byKey(rt2ecOperatorPermissionCheckKey));
  await tester.pumpAndSettle();
  await tester.tap(find.byKey(rt2ecOperatorCaptureStartKey));
  await tester.pumpAndSettle();
}

FilledButton _filledButton(WidgetTester tester, Key key) {
  return tester.widget<FilledButton>(find.byKey(key));
}

class _Fixture {
  _Fixture({
    MicrophonePermissionStatus initialPermission =
        MicrophonePermissionStatus.unknown,
    Iterable<MicrophonePermissionStatus> requestSequence =
        const <MicrophonePermissionStatus>[],
  }) : permission = FakeMicrophonePermissionGateway(
          initialStatus: initialPermission,
          requestSequence: requestSequence,
        ) {
    controller = MicrophoneCaptureController(
      permissionGateway: permission,
      engine: engine,
      maximumAllowedDuration: rt2ecOperatorMaximumCaptureDuration,
    );
  }

  final FakeMicrophonePermissionGateway permission;
  final _OperatorFakeCaptureEngine engine = _OperatorFakeCaptureEngine();
  final _FakePrivateArtifactAccess artifacts = _FakePrivateArtifactAccess();
  late final MicrophoneCaptureController controller;
  int factoryCalls = 0;

  Rt2ecOperatorCaptureDependencies createDependencies() {
    factoryCalls += 1;
    return Rt2ecOperatorCaptureDependencies(
      permissionGateway: permission,
      captureController: controller,
      privateArtifactAccess: artifacts,
    );
  }
}

class _OperatorFakeCaptureEngine implements MicrophoneCaptureEngine {
  final List<MicrophoneCaptureRequest> requests = <MicrophoneCaptureRequest>[];
  int startCalls = 0;
  int stopCalls = 0;
  int cancelCalls = 0;
  int disposeCalls = 0;
  int _sequence = 0;
  bool _isCapturing = false;

  @override
  bool get isCapturing => _isCapturing;

  @override
  Future<void> start(MicrophoneCaptureRequest request) async {
    startCalls += 1;
    requests.add(request);
    _isCapturing = true;
  }

  @override
  Future<MicrophoneCaptureEngineResult> stop() async {
    stopCalls += 1;
    _isCapturing = false;
    _sequence += 1;
    return MicrophoneCaptureEngineResult(
      opaqueCaptureId: 'opaque-internal-$_sequence',
      capturedDuration: const Duration(milliseconds: 1200),
      publicMetadata: const <String, Object?>{
        'engine': 'operator-fake',
        'encoding': 'wav',
        'sample_rate_hz': 16000,
        'channels': 1,
        'microphone_accessed': false,
        'audio_captured': false,
        'raw_audio_exposed': false,
        'private_artifact_registered': true,
      },
    );
  }

  @override
  Future<void> cancel() async {
    cancelCalls += 1;
    _isCapturing = false;
  }

  @override
  Future<void> dispose() async {
    disposeCalls += 1;
    _isCapturing = false;
  }
}

class _FakePrivateArtifactAccess
    implements RecordMicrophoneCapturePrivateArtifactAccess {
  final List<String> discardedIds = <String>[];

  @override
  String? resolvePrivateArtifactPath(String opaqueCaptureId) {
    return 'forbidden-private-path.wav';
  }

  @override
  Future<bool> discardPrivateArtifact(String opaqueCaptureId) async {
    discardedIds.add(opaqueCaptureId);
    return true;
  }
}
