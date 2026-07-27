import 'package:app/services/microphone_capture.dart';
import 'package:app/services/microphone_capture_host_audio_handoff.dart';
import 'package:app/services/record_microphone_capture_engine.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('HostAudioHandoffController', () {
    test('starts idle without a retained artifact', () {
      final fixture = _fixture();

      expect(fixture.controller.state.phase, HostAudioHandoffPhase.idle);
      expect(fixture.controller.state.hasRetainedArtifact, isFalse);
      expect(fixture.controller.isClosed, isFalse);
    });

    test('retains a completed opaque artifact without exposing id or path',
        () async {
      final fixture = _fixture();

      final result = await fixture.controller.retain(
        _completedCapture(),
        language: 'ja-JP',
        publicMetadata: const <String, Object?>{
          'host_app': 'DRC',
          'input_mode': 'microphone',
        },
      );

      expect(result.outcome, HostAudioHandoffOutcome.retained);
      expect(result.descriptor!.encoding, 'wav');
      expect(result.descriptor!.sampleRateHz, 16000);
      expect(result.descriptor!.channelCount, 1);
      expect(result.descriptor!.capturedDuration, const Duration(seconds: 3));
      expect(result.descriptor!.maximumDuration, const Duration(seconds: 15));
      expect(result.descriptor!.language, 'ja-JP');
      expect(result.publicMetadata['private_path_exposed'], isFalse);
      expect(result.publicMetadata['opaque_capture_id_exposed'], isFalse);
      expect(_publicText(result), isNot(contains('opaque-1')));
      expect(_publicText(result), isNot(contains('<private>/capture.wav')));
      expect(fixture.controller.state.phase, HostAudioHandoffPhase.retained);
    });

    test('rejects a capture result that is not completed', () async {
      final fixture = _fixture();
      final capture = MicrophoneCaptureResult(
        outcome: MicrophoneCaptureOutcome.cancelled,
        safeMessage: 'cancelled',
        technicalCode: 'capture_cancelled',
      );

      final result = await fixture.controller.retain(capture);

      expect(result.outcome, HostAudioHandoffOutcome.invalidCapture);
      expect(result.technicalCode, 'host_audio_capture_not_completed');
      expect(fixture.access.resolveCalls, 0);
    });

    test('rejects a completed capture without an engine artifact', () async {
      final fixture = _fixture();
      final capture = MicrophoneCaptureResult(
        outcome: MicrophoneCaptureOutcome.completed,
        safeMessage: 'completed',
        technicalCode: 'capture_completed',
      );

      final result = await fixture.controller.retain(capture);

      expect(result.outcome, HostAudioHandoffOutcome.invalidCapture);
      expect(result.technicalCode, 'host_audio_capture_not_completed');
      expect(fixture.access.resolveCalls, 0);
    });

    test('rejects zero and over-limit capture durations', () async {
      final fixture = _fixture();

      final zero = await fixture.controller.retain(
        _completedCapture(duration: Duration.zero),
      );
      final overLimit = await fixture.controller.retain(
        _completedCapture(duration: const Duration(seconds: 16)),
      );

      expect(zero.technicalCode, 'host_audio_capture_duration_invalid');
      expect(overLimit.technicalCode, 'host_audio_capture_duration_invalid');
      expect(fixture.access.resolveCalls, 0);
    });

    test('rejects audio outside the WAV 16 kHz mono contract', () async {
      final fixture = _fixture();

      final result = await fixture.controller.retain(
        _completedCapture(
          engineMetadata: const <String, Object?>{
            'encoding': 'mp3',
            'sample_rate_hz': 44100,
            'channels': 2,
            'private_artifact_registered': true,
          },
        ),
      );

      expect(result.outcome, HostAudioHandoffOutcome.invalidCapture);
      expect(result.technicalCode, 'host_audio_format_invalid');
      expect(fixture.access.resolveCalls, 0);
    });

    test('rejects an opaque id that has no private artifact', () async {
      final fixture = _fixture(
        access: _FakePrivateArtifactAccess(paths: const <String, String>{}),
      );

      final result = await fixture.controller.retain(_completedCapture());

      expect(result.outcome, HostAudioHandoffOutcome.artifactUnavailable);
      expect(result.technicalCode, 'host_audio_private_artifact_unavailable');
      expect(fixture.controller.state.phase, HostAudioHandoffPhase.failed);
    });

    test('single retained artifact is enforced', () async {
      final fixture = _fixture();
      await fixture.controller.retain(_completedCapture());

      final second = await fixture.controller.retain(
        _completedCapture(opaqueCaptureId: 'opaque-2'),
      );

      expect(second.outcome, HostAudioHandoffOutcome.busy);
      expect(second.retryable, isTrue);
      expect(fixture.access.resolveCalls, 1);
    });

    test('private path access is closed outside consumer execution', () async {
      final consumer = _LeaseCapturingConsumer();
      final fixture = _fixture(consumer: consumer);
      await fixture.controller.retain(_completedCapture());
      await fixture.controller.consume();

      await expectLater(
        consumer.lease!.withPrivateArtifactPath((_) async => true),
        throwsA(
          isA<HostAudioHandoffException>().having(
            (error) => error.code,
            'code',
            'host_audio_private_artifact_access_not_active',
          ),
        ),
      );
    });

    test('fake consumer completes and artifact is discarded exactly once',
        () async {
      final fixture = _fixture();
      await fixture.controller.retain(_completedCapture());

      final result = await fixture.controller.consume();

      expect(result.outcome, HostAudioHandoffOutcome.completed);
      expect(result.consumerInvoked, isTrue);
      expect(result.privateArtifactDiscarded, isTrue);
      expect(result.cleanupSucceeded, isTrue);
      expect(fixture.defaultConsumer.consumeCalls, 1);
      expect(fixture.access.discardedIds, <String>['opaque-1']);
      expect(fixture.access.paths, isEmpty);
      expect(result.publicMetadata['audio_uploaded'], isFalse);
      expect(result.publicMetadata['stt_executed'], isFalse);
    });

    test('scoped fake consumer can resolve a path only during consume',
        () async {
      final consumer = _PathUsingFakeConsumer();
      final fixture = _fixture(consumer: consumer);
      await fixture.controller.retain(_completedCapture());

      final result = await fixture.controller.consume();

      expect(consumer.pathSeen, '<private>/capture.wav');
      expect(result.isCompleted, isTrue);
      expect(_publicText(result), isNot(contains('<private>/capture.wav')));
      expect(_publicText(result), isNot(contains('opaque-1')));
    });

    test('consumer exception is normalized and cleanup still succeeds',
        () async {
      final fixture = _fixture(
        consumer: FakeHostAudioHandoffConsumer(
          consumeError: StateError('sensitive consumer payload'),
        ),
      );
      await fixture.controller.retain(_completedCapture());

      final result = await fixture.controller.consume();

      expect(result.outcome, HostAudioHandoffOutcome.failed);
      expect(result.technicalCode, 'host_audio_consumer_exception');
      expect(result.privateArtifactDiscarded, isTrue);
      expect(result.cleanupSucceeded, isTrue);
      expect(_publicText(result), isNot(contains('sensitive consumer payload')));
    });

    test('consumer-declared failure is returned after cleanup', () async {
      final fixture = _fixture(
        consumer: FakeHostAudioHandoffConsumer(
          result: HostAudioHandoffConsumerResult.failed(
            technicalCode: 'fake_staging_rejected',
            safeMessage: '<private>/capture.wav',
            retryable: true,
          ),
        ),
      );
      await fixture.controller.retain(_completedCapture());

      final result = await fixture.controller.consume();

      expect(result.outcome, HostAudioHandoffOutcome.failed);
      expect(result.technicalCode, 'fake_staging_rejected');
      expect(result.retryable, isTrue);
      expect(result.cleanupSucceeded, isTrue);
      expect(_publicText(result), isNot(contains('<private>/capture.wav')));
      expect(fixture.access.paths, isEmpty);
    });

    test('cleanup failure keeps the lease available for explicit retry',
        () async {
      final access = _FakePrivateArtifactAccess(
        discardResults: <bool>[false, true],
      );
      final fixture = _fixture(access: access);
      await fixture.controller.retain(_completedCapture());

      final failed = await fixture.controller.consume();

      expect(failed.outcome, HostAudioHandoffOutcome.cleanupFailed);
      expect(failed.retryable, isTrue);
      expect(access.paths, contains('opaque-1'));

      final retried = await fixture.controller.discard();

      expect(retried.outcome, HostAudioHandoffOutcome.discarded);
      expect(access.paths, isEmpty);
      expect(access.discardCalls, 2);
    });

    test('explicit discard removes a retained artifact without consuming',
        () async {
      final fixture = _fixture();
      await fixture.controller.retain(_completedCapture());

      final result = await fixture.controller.discard();

      expect(result.outcome, HostAudioHandoffOutcome.discarded);
      expect(result.consumerInvoked, isFalse);
      expect(result.privateArtifactDiscarded, isTrue);
      expect(fixture.defaultConsumer.consumeCalls, 0);
      expect(fixture.access.paths, isEmpty);
    });

    test('cancel invokes fake consumer cancellation and discards artifact',
        () async {
      final fixture = _fixture();
      await fixture.controller.retain(_completedCapture());

      final result = await fixture.controller.cancel();

      expect(result.outcome, HostAudioHandoffOutcome.cancelled);
      expect(result.cleanupSucceeded, isTrue);
      expect(fixture.defaultConsumer.cancelCalls, 1);
      expect(fixture.access.paths, isEmpty);
    });

    test('consumer cancel failure does not prevent artifact cleanup', () async {
      final fixture = _fixture(
        consumer: FakeHostAudioHandoffConsumer(
          cancelError: StateError('sensitive cancel payload'),
        ),
      );
      await fixture.controller.retain(_completedCapture());

      final result = await fixture.controller.cancel();

      expect(result.outcome, HostAudioHandoffOutcome.cancelled);
      expect(
        result.technicalCode,
        'host_audio_consumer_cancel_failed_artifact_discarded',
      );
      expect(result.cleanupSucceeded, isTrue);
      expect(fixture.access.paths, isEmpty);
      expect(_publicText(result), isNot(contains('sensitive cancel payload')));
    });

    test('close cleans a retained artifact and disposes the fake consumer',
        () async {
      final fixture = _fixture();
      await fixture.controller.retain(_completedCapture());

      await fixture.controller.close();

      expect(fixture.controller.isClosed, isTrue);
      expect(fixture.controller.state.phase, HostAudioHandoffPhase.closed);
      expect(fixture.defaultConsumer.cancelCalls, 1);
      expect(fixture.defaultConsumer.disposeCalls, 1);
      expect(fixture.access.paths, isEmpty);
    });

    test('close is idempotent', () async {
      final fixture = _fixture();

      await fixture.controller.close();
      await fixture.controller.close();

      expect(fixture.defaultConsumer.disposeCalls, 1);
      expect(fixture.controller.state.phase, HostAudioHandoffPhase.closed);
    });

    test('closed controller rejects new artifacts', () async {
      final fixture = _fixture();
      await fixture.controller.close();

      final result = await fixture.controller.retain(_completedCapture());

      expect(result.outcome, HostAudioHandoffOutcome.closed);
      expect(result.technicalCode, 'host_audio_handoff_closed');
      expect(fixture.access.resolveCalls, 0);
    });

    test('public metadata uses an allowlist and removes sensitive fields',
        () async {
      final fixture = _fixture();

      final result = await fixture.controller.retain(
        _completedCapture(),
        publicMetadata: const <String, Object?>{
          'host_app': 'DRC',
          'private_path': '<private>/capture.wav',
          'opaque_capture_id': 'opaque-1',
          'api_token': 'secret',
        },
      );

      expect(result.descriptor!.publicMetadata, <String, Object?>{
        'host_app': 'DRC',
      });
      expect(_publicText(result), isNot(contains('<private>/capture.wav')));
      expect(_publicText(result), isNot(contains('secret')));
      expect(_publicText(result), isNot(contains('opaque-1')));
    });
  });
}

class _Fixture {
  _Fixture({
    required this.access,
    required this.consumer,
    required this.controller,
  });

  final _FakePrivateArtifactAccess access;
  final HostAudioHandoffConsumer consumer;
  final HostAudioHandoffController controller;

  FakeHostAudioHandoffConsumer get defaultConsumer =>
      consumer as FakeHostAudioHandoffConsumer;
}

_Fixture _fixture({
  _FakePrivateArtifactAccess? access,
  HostAudioHandoffConsumer? consumer,
}) {
  final resolvedAccess = access ?? _FakePrivateArtifactAccess();
  final resolvedConsumer = consumer ?? FakeHostAudioHandoffConsumer();
  return _Fixture(
    access: resolvedAccess,
    consumer: resolvedConsumer,
    controller: HostAudioHandoffController(
      privateArtifactAccess: resolvedAccess,
      consumer: resolvedConsumer,
    ),
  );
}

MicrophoneCaptureResult _completedCapture({
  String opaqueCaptureId = 'opaque-1',
  Duration duration = const Duration(seconds: 3),
  Map<String, Object?> engineMetadata = const <String, Object?>{
    'encoding': 'wav',
    'sample_rate_hz': 16000,
    'channels': 1,
    'private_artifact_registered': true,
    'raw_audio_exposed': false,
  },
}) {
  return MicrophoneCaptureResult(
    outcome: MicrophoneCaptureOutcome.completed,
    safeMessage: 'completed',
    technicalCode: 'capture_completed',
    engineResult: MicrophoneCaptureEngineResult(
      opaqueCaptureId: opaqueCaptureId,
      capturedDuration: duration,
      publicMetadata: engineMetadata,
    ),
  );
}

String _publicText(HostAudioHandoffResult result) {
  return <Object?>[
    result.outcome.name,
    result.technicalCode,
    result.safeMessage,
    result.publicMetadata,
    result.descriptor?.encoding,
    result.descriptor?.language,
    result.descriptor?.publicMetadata,
  ].join('|');
}

class _FakePrivateArtifactAccess
    implements RecordMicrophoneCapturePrivateArtifactAccess {
  _FakePrivateArtifactAccess({
    Map<String, String>? paths,
    List<bool>? discardResults,
  })  : paths = Map<String, String>.from(
          paths ?? const <String, String>{'opaque-1': '<private>/capture.wav'},
        ),
        _discardResults = List<bool>.from(discardResults ?? const <bool>[]);

  final Map<String, String> paths;
  final List<bool> _discardResults;
  final List<String> discardedIds = <String>[];
  int resolveCalls = 0;
  int discardCalls = 0;

  @override
  String? resolvePrivateArtifactPath(String opaqueCaptureId) {
    resolveCalls += 1;
    return paths[opaqueCaptureId];
  }

  @override
  Future<bool> discardPrivateArtifact(String opaqueCaptureId) async {
    discardCalls += 1;
    discardedIds.add(opaqueCaptureId);
    final result = _discardResults.isEmpty ? true : _discardResults.removeAt(0);
    if (result) {
      paths.remove(opaqueCaptureId);
    }
    return result;
  }
}

class _PathUsingFakeConsumer implements HostAudioHandoffConsumer {
  String? pathSeen;

  @override
  Future<HostAudioHandoffConsumerResult> consume(
    HostAudioPrivateArtifactLease lease,
  ) {
    return lease.withPrivateArtifactPath((privatePath) async {
      pathSeen = privatePath;
      return HostAudioHandoffConsumerResult.completed();
    });
  }

  @override
  Future<void> cancel() async {}

  @override
  Future<void> dispose() async {}
}

class _LeaseCapturingConsumer implements HostAudioHandoffConsumer {
  HostAudioPrivateArtifactLease? lease;

  @override
  Future<HostAudioHandoffConsumerResult> consume(
    HostAudioPrivateArtifactLease lease,
  ) async {
    this.lease = lease;
    return HostAudioHandoffConsumerResult.completed();
  }

  @override
  Future<void> cancel() async {}

  @override
  Future<void> dispose() async {}
}
