import 'dart:async';
import 'dart:convert';

import 'package:app/services/backend_provider_neutral_transcript_provider.dart';
import 'package:app/services/backend_voice_input_staging_consumer.dart';
import 'package:app/services/realtime_text_stream_client.dart';
import 'package:app/services/realtime_text_stream_controller.dart';
import 'package:app/services/realtime_text_stream_transcript_handoff.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;

void main() {
  group('BackendProviderNeutralTranscriptProvider', () {
    test('valid response returns one provider-neutral final transcript', () async {
      var takeCalls = 0;
      final client = _RecordingTranscriptClient();
      final provider = BackendProviderNeutralTranscriptProvider(
        baseUrl: 'http://backend.test/',
        takeStagedArtifact: () {
          takeCalls += 1;
          return _artifact();
        },
        foregroundOptIn: () => true,
        client: client,
      );

      final result = await provider.acquireNextTranscript();

      expect(result, isNotNull);
      expect(result!.resultId, 'abcdef0123456789abcdef0123456789');
      expect(result.text, 'synthetic final transcript');
      expect(result.isFinal, isTrue);
      expect(takeCalls, 1);
      expect(client.sendCalls, 1);
      expect(client.method, 'POST');
      expect(client.uri.path, '/demo/voice-input/transcript');
      expect(client.uri.toString(), isNot(contains(_artifact().stagingId)));
      expect(client.followRedirects, isFalse);
      expect(client.body['staging_id'], _artifact().stagingId);
      expect(client.body['foreground_opt_in'], isTrue);
      expect(client.body['duration_ms'], 1000);
      expect(provider.toString(), isNot(contains(result.text)));

      provider.dispose();
    });

    test('opt-in false takes no artifact and sends no request', () async {
      var takeCalls = 0;
      final client = _RecordingTranscriptClient();
      final provider = BackendProviderNeutralTranscriptProvider(
        baseUrl: 'http://backend.test',
        takeStagedArtifact: () {
          takeCalls += 1;
          return _artifact();
        },
        foregroundOptIn: () => false,
        client: client,
      );

      await expectLater(
        provider.acquireNextTranscript(),
        throwsA(
          isA<BackendProviderNeutralTranscriptException>().having(
            (error) => error.code,
            'code',
            'backend_transcript_opt_in_required',
          ),
        ),
      );
      expect(takeCalls, 0);
      expect(client.sendCalls, 0);
    });

    test('no staged artifact returns null without HTTP', () async {
      final client = _RecordingTranscriptClient();
      final provider = BackendProviderNeutralTranscriptProvider(
        baseUrl: 'http://backend.test',
        takeStagedArtifact: () => null,
        foregroundOptIn: () => true,
        client: client,
      );

      expect(await provider.acquireNextTranscript(), isNull);
      expect(client.sendCalls, 0);
    });

    test('concurrent invocation takes and sends exactly once', () async {
      final responseCompleter = Completer<void>();
      final client = _RecordingTranscriptClient(
        beforeResponse: () => responseCompleter.future,
      );
      var takeCalls = 0;
      final provider = BackendProviderNeutralTranscriptProvider(
        baseUrl: 'http://backend.test',
        takeStagedArtifact: () {
          takeCalls += 1;
          return _artifact();
        },
        foregroundOptIn: () => true,
        client: client,
      );

      final first = provider.acquireNextTranscript();
      await Future<void>.delayed(Duration.zero);
      final second = provider.acquireNextTranscript();
      await expectLater(
        second,
        throwsA(
          isA<BackendProviderNeutralTranscriptException>().having(
            (error) => error.code,
            'code',
            'backend_transcript_request_in_progress',
          ),
        ),
      );
      expect(takeCalls, 1);
      expect(client.sendCalls, 1);
      responseCompleter.complete();
      expect(await first, isNotNull);
    });

    test('rejects redirect and does not retry', () async {
      final client = _RecordingTranscriptClient(statusCode: 307);
      final provider = _provider(client: client);

      await expectLater(
        provider.acquireNextTranscript(),
        throwsA(
          isA<BackendProviderNeutralTranscriptException>().having(
            (error) => error.code,
            'code',
            'backend_transcript_redirect_rejected',
          ),
        ),
      );
      expect(client.sendCalls, 1);
    });

    test('requires no-store success response header', () async {
      final client = _RecordingTranscriptClient(
        responseHeaders: const <String, String>{
          'content-type': 'application/json',
        },
      );
      final provider = _provider(client: client);

      await expectLater(
        provider.acquireNextTranscript(),
        throwsA(
          isA<BackendProviderNeutralTranscriptException>().having(
            (error) => error.code,
            'code',
            'backend_transcript_no_store_required',
          ),
        ),
      );
    });

    test('rejects forbidden or extra response keys', () async {
      final body = _successBody()..['provider'] = 'must-not-cross-boundary';
      final client = _RecordingTranscriptClient(responseBody: jsonEncode(body));
      final provider = _provider(client: client);

      await expectLater(
        provider.acquireNextTranscript(),
        throwsA(
          isA<BackendProviderNeutralTranscriptException>().having(
            (error) => error.code,
            'code',
            'backend_transcript_response_invalid',
          ),
        ),
      );
      expect(provider.toString(), isNot(contains('must-not-cross-boundary')));
    });

    test('rejects invalid id, nonfinal, empty, and overlong transcript', () async {
      Future<void> expectInvalid(Map<String, Object?> body) async {
        final provider = _provider(
          client: _RecordingTranscriptClient(responseBody: jsonEncode(body)),
        );
        await expectLater(
          provider.acquireNextTranscript(),
          throwsA(
            isA<BackendProviderNeutralTranscriptException>().having(
              (error) => error.code,
              'code',
              'backend_transcript_response_invalid',
            ),
          ),
        );
      }

      await expectInvalid(_successBody()..['result_id'] = '../private');
      await expectInvalid(_successBody()..['is_final'] = false);
      await expectInvalid(_successBody()..['text'] = '   ');
      await expectInvalid(
        _successBody()..['text'] = List<String>.filled(4097, 'あ').join(),
      );
    });

    test('rejects oversized response', () async {
      final provider = BackendProviderNeutralTranscriptProvider(
        baseUrl: 'http://backend.test',
        takeStagedArtifact: _artifact,
        foregroundOptIn: () => true,
        client: _RecordingTranscriptClient(),
        maximumResponseBytes: 16,
      );

      await expectLater(
        provider.acquireNextTranscript(),
        throwsA(
          isA<BackendProviderNeutralTranscriptException>().having(
            (error) => error.code,
            'code',
            'backend_transcript_response_invalid',
          ),
        ),
      );
    });

    test('normalizes problem body without exposing message or transcript', () async {
      const sensitive = 'private path credential transcript raw body';
      final client = _RecordingTranscriptClient(
        statusCode: 503,
        responseBody: jsonEncode(<String, Object?>{
          'detail': <String, Object?>{
            'code': 'voice_input_transcript_unavailable',
            'message': sensitive,
            'retryable': true,
          },
        }),
      );
      final provider = _provider(client: client);

      try {
        await provider.acquireNextTranscript();
        fail('expected failure');
      } on BackendProviderNeutralTranscriptException catch (error) {
        expect(error.code, 'voice_input_transcript_unavailable');
        expect(error.retryable, isTrue);
        expect(error.toString(), isNot(contains(sensitive)));
      }
    });

    test('dispose during pending request leaves completion inert', () async {
      final responseCompleter = Completer<void>();
      final client = _RecordingTranscriptClient(
        beforeResponse: () => responseCompleter.future,
      );
      final provider = _provider(client: client);

      final pending = provider.acquireNextTranscript();
      await Future<void>.delayed(Duration.zero);
      provider.dispose();
      responseCompleter.complete();

      expect(await pending, isNull);
    });

    test('existing handoff starts text stream exactly once', () async {
      final transcriptClient = _RecordingTranscriptClient();
      final provider = _provider(client: transcriptClient);
      final realtimeClient = _FakeRealtimeHttpClient();
      final controller = RealtimeTextStreamController(
        client: RealtimeTextStreamClient(
          baseUrl: 'http://backend.test',
          client: realtimeClient,
        ),
      );
      final handoff = RealtimeTextStreamTranscriptHandoff(
        controller: controller,
        transcriptProvider: provider.acquireNextTranscript,
      );

      await handoff.startFromNextTranscript();

      expect(transcriptClient.sendCalls, 1);
      expect(realtimeClient.createCalls, 1);
      expect(realtimeClient.lastInputText, 'synthetic final transcript');
      expect(
        handoff.state.phase,
        RealtimeTextStreamTranscriptHandoffPhase.accepted,
      );
      expect(
        handoff.state.safeMessage,
        isNot(contains('synthetic final transcript')),
      );

      handoff.dispose();
      controller.dispose();
      provider.dispose();
    });
  });
}

BackendProviderNeutralTranscriptProvider _provider({
  required http.Client client,
}) {
  return BackendProviderNeutralTranscriptProvider(
    baseUrl: 'http://backend.test',
    takeStagedArtifact: _artifact,
    foregroundOptIn: () => true,
    client: client,
  );
}

BackendVoiceInputStagedArtifact _artifact() {
  return const BackendVoiceInputStagedArtifact(
    stagingId: '0123456789abcdef0123456789abcdef',
    audioFormat: 'wav',
    mediaType: 'audio/wav',
    byteCount: 128,
    sampleRateHz: 16000,
    channelCount: 1,
    duration: Duration(seconds: 1),
    expiresIn: Duration(minutes: 5),
  );
}

Map<String, Object?> _successBody() {
  return <String, Object?>{
    'accepted': true,
    'request_state': 'final_transcript_ready',
    'result_id': 'abcdef0123456789abcdef0123456789',
    'text': 'synthetic final transcript',
    'is_final': true,
  };
}

class _RecordingTranscriptClient extends http.BaseClient {
  _RecordingTranscriptClient({
    this.statusCode = 200,
    String? responseBody,
    this.responseHeaders = const <String, String>{
      'content-type': 'application/json',
      'cache-control': 'no-store',
    },
    this.beforeResponse,
  }) : responseBody = responseBody ?? jsonEncode(_successBody());

  final int statusCode;
  final String responseBody;
  final Map<String, String> responseHeaders;
  final Future<void> Function()? beforeResponse;

  int sendCalls = 0;
  String? method;
  Uri uri = Uri();
  bool? followRedirects;
  Map<String, dynamic> body = <String, dynamic>{};

  @override
  Future<http.StreamedResponse> send(http.BaseRequest request) async {
    sendCalls += 1;
    method = request.method;
    uri = request.url;
    followRedirects = request.followRedirects;
    if (request is http.Request) {
      body = Map<String, dynamic>.from(
        jsonDecode(request.body) as Map<String, dynamic>,
      );
    }
    if (beforeResponse != null) {
      await beforeResponse!();
    }
    return http.StreamedResponse(
      Stream<List<int>>.value(utf8.encode(responseBody)),
      statusCode,
      headers: responseHeaders,
      isRedirect: statusCode >= 300 && statusCode < 400,
    );
  }
}

class _FakeRealtimeHttpClient extends http.BaseClient {
  var createCalls = 0;
  String? lastInputText;

  @override
  Future<http.StreamedResponse> send(http.BaseRequest request) async {
    if (request.method == 'POST' &&
        request.url.path == '/realtime/text/sessions') {
      createCalls += 1;
      if (request is http.Request) {
        final body = jsonDecode(request.body) as Map<String, Object?>;
        lastInputText = body['input_text'] as String?;
      }
      return _jsonResponse(201, <String, Object?>{
        'accepted': true,
        'session': <String, Object?>{
          'session_id': 'session-1',
          'state': 'streaming',
          'active_turn_id': 'turn-1',
          'last_sequence': 0,
          'is_closed': false,
          'cancel_mode': 'cooperative',
          'hard_cancel_supported': false,
        },
        'turn': <String, Object?>{
          'session_id': 'session-1',
          'turn_id': 'turn-1',
          'state': 'streaming',
          'chunk_count': 0,
          'output_char_count': 0,
          'cancel_requested': false,
          'terminal_outcome': null,
        },
        'events_path': '/realtime/text/sessions/session-1/events',
        'cancel_path': '/realtime/text/sessions/session-1/cancel',
        'idle_ttl_seconds': 30,
        'max_duration_seconds': 120,
        'max_pending_events': 64,
        'max_event_bytes': 32768,
      });
    }
    if (request.method == 'GET' &&
        request.url.path == '/realtime/text/sessions/session-1/events') {
      return http.StreamedResponse(const Stream<List<int>>.empty(), 200);
    }
    return _jsonResponse(404, <String, Object?>{
      'code': 'unexpected_request',
      'message': 'Unexpected fake request.',
      'retryable': false,
    });
  }
}

http.StreamedResponse _jsonResponse(int status, Map<String, Object?> body) {
  return http.StreamedResponse(
    Stream<List<int>>.value(utf8.encode(jsonEncode(body))),
    status,
    headers: const <String, String>{'content-type': 'application/json'},
  );
}
