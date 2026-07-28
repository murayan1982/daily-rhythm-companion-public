import 'dart:convert';
import 'dart:io';

import 'package:app/services/backend_voice_input_staging_consumer.dart';
import 'package:app/services/microphone_capture.dart';
import 'package:app/services/microphone_capture_host_audio_handoff.dart';
import 'package:app/services/record_microphone_capture_engine.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;

void main() {
  group('BackendVoiceInputStagingConsumer', () {
    late Directory temporaryDirectory;

    setUp(() async {
      temporaryDirectory = await Directory.systemTemp.createTemp(
        'drc_rt3c3_staging_consumer_',
      );
    });

    tearDown(() async {
      if (await temporaryDirectory.exists()) {
        await temporaryDirectory.delete(recursive: true);
      }
    });

    test('streams scoped WAV bytes and keeps path out of request metadata',
        () async {
      final wav = _wavBytes();
      final privateFile = File('${temporaryDirectory.path}/capture.wav');
      await privateFile.writeAsBytes(wav, flush: true);
      final client = _RecordingClient(
        responseBody: _successResponse(byteCount: wav.length),
      );
      final access = _PrivateArtifactAccess(privateFile.path);
      final consumer = BackendVoiceInputStagingConsumer(
        baseUrl: 'http://127.0.0.1:8000/',
        client: client,
      );
      final controller = HostAudioHandoffController(
        privateArtifactAccess: access,
        consumer: consumer,
      );

      final retained = await controller.retain(_completedCapture());
      final result = await controller.consume();

      expect(retained.isRetained, isTrue);
      expect(result.isCompleted, isTrue);
      expect(result.technicalCode, 'host_audio_backend_staging_completed');
      expect(result.publicMetadata['audio_uploaded'], isTrue);
      expect(result.publicMetadata['backend_staging_created'], isTrue);
      expect(result.publicMetadata['backend_staging_id_available'], isTrue);
      expect(result.publicMetadata['stt_executed'], isFalse);
      expect(client.method, 'POST');
      expect(client.uri.path, '/demo/voice-input/staging');
      expect(client.headers['content-type'], 'audio/wav');
      expect(client.headers['x-drc-audio-format'], 'wav');
      expect(client.headers['x-drc-sample-rate-hz'], '16000');
      expect(client.headers['x-drc-channel-count'], '1');
      expect(client.headers['x-drc-duration-ms'], '3000');
      expect(client.bodyBytes, wav);
      expect(client.contentLength, wav.length);
      expect(access.discardCalls, 1);
      expect(await privateFile.exists(), isFalse);

      final staged = consumer.stagedArtifact;
      expect(staged, isNotNull);
      expect(staged!.stagingId, '0123456789abcdef0123456789abcdef');
      expect(staged.byteCount, wav.length);
      expect(staged.duration, const Duration(seconds: 3));
      final publicText = <Object?>[
        result.technicalCode,
        result.safeMessage,
        result.publicMetadata,
        staged.stagingId,
      ].join('|');
      expect(publicText, isNot(contains(privateFile.path)));
      expect(client.uri.toString(), isNot(contains(privateFile.path)));
      expect(client.headers.toString(), isNot(contains(privateFile.path)));
    });

    test('takeStagedArtifact transfers the path-free handle once', () async {
      final wav = _wavBytes();
      final privateFile = File('${temporaryDirectory.path}/capture.wav');
      await privateFile.writeAsBytes(wav);
      final consumer = BackendVoiceInputStagingConsumer(
        baseUrl: 'http://backend.local',
        client: _RecordingClient(
          responseBody: _successResponse(byteCount: wav.length),
        ),
      );
      final controller = HostAudioHandoffController(
        privateArtifactAccess: _PrivateArtifactAccess(privateFile.path),
        consumer: consumer,
      );

      await controller.retain(_completedCapture());
      await controller.consume();
      final staged = consumer.takeStagedArtifact();

      expect(staged, isNotNull);
      expect(consumer.stagedArtifact, isNull);
      expect(consumer.takeStagedArtifact(), isNull);
      expect(staged!.stagingId, hasLength(32));
    });

    test('rejects local artifact above the client byte bound before sending',
        () async {
      final wav = _wavBytes(payloadSize: 64);
      final privateFile = File('${temporaryDirectory.path}/capture.wav');
      await privateFile.writeAsBytes(wav);
      final client = _RecordingClient(
        responseBody: _successResponse(byteCount: wav.length),
      );
      final access = _PrivateArtifactAccess(privateFile.path);
      final consumer = BackendVoiceInputStagingConsumer(
        baseUrl: 'http://backend.local',
        client: client,
        maximumBodyBytes: 32,
      );
      final controller = HostAudioHandoffController(
        privateArtifactAccess: access,
        consumer: consumer,
      );

      await controller.retain(_completedCapture());
      final result = await controller.consume();

      expect(result.outcome, HostAudioHandoffOutcome.failed);
      expect(
        result.technicalCode,
        'backend_staging_private_artifact_too_large',
      );
      expect(result.publicMetadata['audio_uploaded'], isFalse);
      expect(client.sendCalls, 0);
      expect(access.discardCalls, 1);
      expect(await privateFile.exists(), isFalse);
    });

    test('normalizes Backend problem without exposing the response message',
        () async {
      final wav = _wavBytes();
      final privateFile = File('${temporaryDirectory.path}/capture.wav');
      await privateFile.writeAsBytes(wav);
      final client = _RecordingClient(
        statusCode: 413,
        responseBody: jsonEncode(<String, Object?>{
          'detail': <String, Object?>{
            'code': 'artifact_too_large',
            'message': 'private server detail must not escape',
            'retryable': false,
          },
        }),
      );
      final consumer = BackendVoiceInputStagingConsumer(
        baseUrl: 'http://backend.local',
        client: client,
      );
      final controller = HostAudioHandoffController(
        privateArtifactAccess: _PrivateArtifactAccess(privateFile.path),
        consumer: consumer,
      );

      await controller.retain(_completedCapture());
      final result = await controller.consume();

      expect(result.outcome, HostAudioHandoffOutcome.failed);
      expect(result.technicalCode, 'artifact_too_large');
      expect(result.retryable, isFalse);
      expect(result.safeMessage, isNot(contains('private server detail')));
      expect(result.publicMetadata['audio_uploaded'], isFalse);
      expect(consumer.stagedArtifact, isNull);
    });

    test('marks server failure retryable while local source is still discarded',
        () async {
      final wav = _wavBytes();
      final privateFile = File('${temporaryDirectory.path}/capture.wav');
      await privateFile.writeAsBytes(wav);
      final access = _PrivateArtifactAccess(privateFile.path);
      final consumer = BackendVoiceInputStagingConsumer(
        baseUrl: 'http://backend.local',
        client: _RecordingClient(
          statusCode: 503,
          responseBody: jsonEncode(<String, Object?>{
            'detail': <String, Object?>{
              'code': 'staging_failed',
              'message': 'safe',
              'retryable': true,
            },
          }),
        ),
      );
      final controller = HostAudioHandoffController(
        privateArtifactAccess: access,
        consumer: consumer,
      );

      await controller.retain(_completedCapture());
      final result = await controller.consume();

      expect(result.technicalCode, 'staging_failed');
      expect(result.retryable, isTrue);
      expect(result.privateArtifactDiscarded, isTrue);
      expect(access.discardCalls, 1);
      expect(await privateFile.exists(), isFalse);
    });

    test('rejects malformed success response as a safe contract failure',
        () async {
      final wav = _wavBytes();
      final privateFile = File('${temporaryDirectory.path}/capture.wav');
      await privateFile.writeAsBytes(wav);
      final consumer = BackendVoiceInputStagingConsumer(
        baseUrl: 'http://backend.local',
        client: _RecordingClient(
          responseBody: jsonEncode(<String, Object?>{
            'accepted': true,
            'request_state': 'staged',
            'staging_id': '../private.wav',
          }),
        ),
      );
      final controller = HostAudioHandoffController(
        privateArtifactAccess: _PrivateArtifactAccess(privateFile.path),
        consumer: consumer,
      );

      await controller.retain(_completedCapture());
      final result = await controller.consume();

      expect(result.technicalCode, 'backend_staging_response_invalid');
      expect(result.retryable, isTrue);
      expect(consumer.stagedArtifact, isNull);
      expect(result.toString(), isNot(contains(privateFile.path)));
    });

    test('does not allow a second upload while a staging handle is pending',
        () async {
      final firstFile = File('${temporaryDirectory.path}/first.wav');
      final secondFile = File('${temporaryDirectory.path}/second.wav');
      final wav = _wavBytes();
      await firstFile.writeAsBytes(wav);
      await secondFile.writeAsBytes(wav);
      final client = _RecordingClient(
        responseBody: _successResponse(byteCount: wav.length),
      );
      final consumer = BackendVoiceInputStagingConsumer(
        baseUrl: 'http://backend.local',
        client: client,
      );
      final firstController = HostAudioHandoffController(
        privateArtifactAccess: _PrivateArtifactAccess(firstFile.path),
        consumer: consumer,
      );
      final secondController = HostAudioHandoffController(
        privateArtifactAccess: _PrivateArtifactAccess(
          secondFile.path,
          opaqueCaptureId: 'opaque-2',
        ),
        consumer: consumer,
      );

      await firstController.retain(_completedCapture());
      expect((await firstController.consume()).isCompleted, isTrue);
      await secondController.retain(
        _completedCapture(opaqueCaptureId: 'opaque-2'),
      );
      final second = await secondController.consume();

      expect(second.technicalCode, 'backend_staging_artifact_pending');
      expect(client.sendCalls, 1);
      expect(await secondFile.exists(), isFalse);
    });

    test('dispose fast-fails future consume and remains idempotent', () async {
      final wav = _wavBytes();
      final privateFile = File('${temporaryDirectory.path}/capture.wav');
      await privateFile.writeAsBytes(wav);
      final client = _RecordingClient(responseBody: '{}');
      final consumer = BackendVoiceInputStagingConsumer(
        baseUrl: 'http://backend.local',
        client: client,
      );
      final access = _PrivateArtifactAccess(privateFile.path);
      final controller = HostAudioHandoffController(
        privateArtifactAccess: access,
        consumer: consumer,
      );

      await consumer.dispose();
      await consumer.dispose();
      await controller.retain(_completedCapture());
      final result = await controller.consume();

      expect(client.closeCalls, 0);
      expect(result.technicalCode, 'backend_staging_consumer_closed');
      expect(client.sendCalls, 0);
      expect(access.discardCalls, 1);
      expect(await privateFile.exists(), isFalse);
    });
  });
}

List<int> _wavBytes({int payloadSize = 24}) {
  return <int>[
    ...ascii.encode('RIFF'),
    payloadSize + 4,
    0,
    0,
    0,
    ...ascii.encode('WAVE'),
    ...List<int>.filled(payloadSize, 0),
  ];
}

String _successResponse({required int byteCount}) {
  return jsonEncode(<String, Object?>{
    'accepted': true,
    'request_state': 'staged',
    'staging_id': '0123456789abcdef0123456789abcdef',
    'audio_format': 'wav',
    'media_type': 'audio/wav',
    'byte_count': byteCount,
    'sample_rate_hz': 16000,
    'channel_count': 1,
    'duration_ms': 3000,
    'expires_in_seconds': 300,
  });
}

MicrophoneCaptureResult _completedCapture({
  String opaqueCaptureId = 'opaque-1',
}) {
  return MicrophoneCaptureResult(
    outcome: MicrophoneCaptureOutcome.completed,
    safeMessage: 'completed',
    technicalCode: 'capture_completed',
    engineResult: MicrophoneCaptureEngineResult(
      opaqueCaptureId: opaqueCaptureId,
      capturedDuration: const Duration(seconds: 3),
      publicMetadata: const <String, Object?>{
        'encoding': 'wav',
        'sample_rate_hz': 16000,
        'channels': 1,
        'private_artifact_registered': true,
      },
    ),
  );
}

class _PrivateArtifactAccess
    implements RecordMicrophoneCapturePrivateArtifactAccess {
  _PrivateArtifactAccess(
    this.privatePath, {
    this.opaqueCaptureId = 'opaque-1',
  });

  final String privatePath;
  final String opaqueCaptureId;
  int discardCalls = 0;

  @override
  String? resolvePrivateArtifactPath(String opaqueCaptureId) {
    if (opaqueCaptureId != this.opaqueCaptureId) {
      return null;
    }
    return privatePath;
  }

  @override
  Future<bool> discardPrivateArtifact(String opaqueCaptureId) async {
    if (opaqueCaptureId != this.opaqueCaptureId) {
      return false;
    }
    discardCalls += 1;
    final file = File(privatePath);
    if (await file.exists()) {
      await file.delete();
    }
    return true;
  }
}

class _RecordingClient extends http.BaseClient {
  _RecordingClient({
    required this.responseBody,
    this.statusCode = 201,
  });

  final String responseBody;
  final int statusCode;
  int sendCalls = 0;
  int closeCalls = 0;
  String? method;
  Uri uri = Uri();
  Map<String, String> headers = <String, String>{};
  List<int> bodyBytes = <int>[];
  int? contentLength;

  @override
  Future<http.StreamedResponse> send(http.BaseRequest request) async {
    sendCalls += 1;
    method = request.method;
    uri = request.url;
    headers = <String, String>{
      for (final entry in request.headers.entries)
        entry.key.toLowerCase(): entry.value,
    };
    contentLength = request.contentLength;
    bodyBytes = await request.finalize().fold<List<int>>(
      <int>[],
      (bytes, chunk) => bytes..addAll(chunk),
    );
    return http.StreamedResponse(
      Stream<List<int>>.value(utf8.encode(responseBody)),
      statusCode,
      headers: const <String, String>{'content-type': 'application/json'},
    );
  }

  @override
  void close() {
    closeCalls += 1;
  }
}
