import 'dart:async';
import 'dart:convert';

import 'package:app/models/framework_v600_realtime_session.dart';
import 'package:app/services/framework_v600_realtime_session_client.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;

void main() {
  group('FrameworkV600RealtimeSessionClient', () {
    test('constructor makes zero requests', () {
      final httpClient = _FakeHttpClient();
      FrameworkV600RealtimeSessionClient(
        baseUrl: 'http://backend.local',
        client: httpClient,
      );

      expect(httpClient.requests, isEmpty);
    });

    test('create exact POST path and parses 201', () async {
      final httpClient = _FakeHttpClient()..queueJson(201, _open());
      final client = _client(httpClient);

      final result = await client.createSession();

      expect(httpClient.requests.single.method, 'POST');
      expect(
        httpClient.requests.single.url.path,
        '/realtime/framework-v6/provider-free/sessions',
      );
      expect(result.sessionId, _sessionId);
    });

    test(
      'turn sends only input_text and forwards valid input exactly',
      () async {
        const acceptedInput = '  keep spacing  ';
        final httpClient = _FakeHttpClient()..queueJson(200, _turn());
        final client = _client(httpClient);

        await client.runTurn(sessionId: _sessionId, inputText: acceptedInput);

        final body = jsonDecode(httpClient.requests.single.body) as Map;
        expect(body, <String, Object?>{'input_text': acceptedInput});
      },
    );

    test('blank and oversized turn rejected before HTTP', () async {
      for (final input in ['', '   ', List<String>.filled(4097, 'x').join()]) {
        final httpClient = _FakeHttpClient();
        final client = _client(httpClient);

        await expectLater(
          client.runTurn(sessionId: _sessionId, inputText: input),
          throwsA(_problemCode('invalid_input_text')),
        );
        expect(httpClient.requests, isEmpty);
      }
    });

    test('interrupt exact POST path defaults scopes and reasons', () async {
      final httpClient = _FakeHttpClient()..queueJson(200, _interrupt());
      final client = _client(httpClient);

      final result = await client.interrupt(sessionId: _sessionId);

      expect(httpClient.requests.single.method, 'POST');
      expect(
        httpClient.requests.single.url.path,
        '/realtime/framework-v6/provider-free/sessions/$_sessionId/interrupt',
      );
      expect(jsonDecode(httpClient.requests.single.body), {
        'scope': 'current_turn',
        'reason': 'host_app_request',
      });
      expect(result.scope, 'current_turn');
    });

    test('all accepted interrupt scopes and reasons are sent', () async {
      for (final scope in frameworkV600RealtimeInterruptScopes) {
        final httpClient = _FakeHttpClient()
          ..queueJson(200, _interrupt(scope: scope));
        await _client(
          httpClient,
        ).interrupt(sessionId: _sessionId, scope: scope);
        expect(jsonDecode(httpClient.requests.single.body)['scope'], scope);
      }
      for (final reason in frameworkV600RealtimeInterruptReasons) {
        final httpClient = _FakeHttpClient()
          ..queueJson(200, _interrupt(reason: reason));
        await _client(
          httpClient,
        ).interrupt(sessionId: _sessionId, reason: reason);
        expect(jsonDecode(httpClient.requests.single.body)['reason'], reason);
      }
    });

    test('invalid interrupt scope and reason rejected before HTTP', () async {
      final badScope = _FakeHttpClient();
      await expectLater(
        _client(badScope).interrupt(sessionId: _sessionId, scope: 'neutral'),
        throwsA(_problemCode('invalid_interrupt_scope')),
      );
      expect(badScope.requests, isEmpty);

      final badReason = _FakeHttpClient();
      await expectLater(
        _client(badReason).interrupt(sessionId: _sessionId, reason: 'neutral'),
        throwsA(_problemCode('invalid_interrupt_reason')),
      );
      expect(badReason.requests, isEmpty);
    });

    test('diagnostics exact GET path and close exact DELETE path', () async {
      final httpClient = _FakeHttpClient()
        ..queueJson(200, _diagnostics())
        ..queueText(204, '');
      final client = _client(httpClient);

      await client.diagnostics(sessionId: _sessionId);
      await client.closeSession(sessionId: _sessionId);

      expect(httpClient.requests[0].method, 'GET');
      expect(
        httpClient.requests[0].url.path,
        '/realtime/framework-v6/provider-free/sessions/$_sessionId/diagnostics',
      );
      expect(httpClient.requests[1].method, 'DELETE');
      expect(
        httpClient.requests[1].url.path,
        '/realtime/framework-v6/provider-free/sessions/$_sessionId',
      );
    });

    test('404 422 429 and 503 map to safe problems', () async {
      for (final status in [404, 422, 429, 503]) {
        final httpClient = _FakeHttpClient()
          ..queueJson(status, _problem('safe_$status'));

        await expectLater(
          _client(httpClient).createSession(),
          throwsA(_problemCode('safe_$status')),
        );
      }
    });

    test('malformed envelopes schema versions and ids fail safely', () async {
      final malformedProblem = _FakeHttpClient()..queueText(503, 'not json');
      await expectLater(
        _client(malformedProblem).createSession(),
        throwsA(_problemCode('invalid_response')),
      );

      final wrongSchema = _FakeHttpClient()
        ..queueJson(201, _open()..['schema_version'] = 'unexpected');
      await expectLater(
        _client(wrongSchema).createSession(),
        throwsA(_problemCode('invalid_schema_version')),
      );

      final invalidId = _FakeHttpClient()
        ..queueJson(201, _open()..['session_id'] = 'neutral-session');
      await expectLater(
        _client(invalidId).createSession(),
        throwsA(_problemCode('invalid_session_id')),
      );
    });

    test(
      'oversized response raw body and input text are not exposed',
      () async {
        final oversized = _FakeHttpClient()
          ..queueText(200, List<String>.filled(65537, 'x').join());

        await expectLater(
          _client(oversized).diagnostics(sessionId: _sessionId),
          throwsA(_problemCode('response_body_too_large')),
        );

        const privateInput = 'NEUTRAL_PRIVATE_INPUT_SENTINEL';
        final failed = _FakeHttpClient()..queueText(500, privateInput);
        try {
          await _client(
            failed,
          ).runTurn(sessionId: _sessionId, inputText: privateInput);
          fail('expected safe exception');
        } on FrameworkV600RealtimeProblemException catch (error) {
          expect(error.toString(), isNot(contains(privateInput)));
          expect(error.problem.message, isNot(contains(privateInput)));
        }
      },
    );

    test('exact 64 KiB boundary is not response_body_too_large', () async {
      final exactBody = List<String>.filled(65536, 'x').join();
      final httpClient = _FakeHttpClient()..queueText(200, exactBody);

      await expectLater(
        _client(httpClient).diagnostics(sessionId: _sessionId),
        throwsA(
          isA<FrameworkV600RealtimeProblemException>().having(
            (error) => error.problem.code,
            'code',
            isNot('response_body_too_large'),
          ),
        ),
      );
    });

    test(
      'pre-append oversized body guard rejects before later chunks',
      () async {
        final httpClient = _FakeHttpClient()
          ..queueChunks(200, [
            List<int>.filled(65530, 120),
            List<int>.filled(7, 121),
            List<int>.filled(1, 122),
          ]);

        await expectLater(
          _client(httpClient).diagnostics(sessionId: _sessionId),
          throwsA(_problemCode('response_body_too_large')),
        );
        expect(httpClient.consumedChunkCount, 2);
      },
    );

    test(
      'transport failures do not echo the session id unnecessarily',
      () async {
        final httpClient = _FakeHttpClient(failSend: true);

        await expectLater(
          _client(httpClient).diagnostics(sessionId: _sessionId),
          throwsA(
            isA<FrameworkV600RealtimeProblemException>()
                .having((error) => error.problem.code, 'code', 'request_failed')
                .having(
                  (error) => error.problem.message,
                  'message',
                  isNot(contains(_sessionId)),
                ),
          ),
        );
      },
    );
  });
}

const _sessionId = 'fw_session_0123456789abcdef0123456789abcdef';
const _turnId = 'fw_turn_0123456789abcdef0123456789abcdef';
const _generationId = 'fw_generation_0123456789abcdef0123456789abcdef';

FrameworkV600RealtimeSessionClient _client(_FakeHttpClient httpClient) {
  return FrameworkV600RealtimeSessionClient(
    baseUrl: 'http://backend.local',
    client: httpClient,
  );
}

Matcher _problemCode(String code) =>
    isA<FrameworkV600RealtimeProblemException>().having(
      (error) => error.problem.code,
      'code',
      code,
    );

class _FakeHttpClient extends http.BaseClient {
  _FakeHttpClient({this.failSend = false});

  final bool failSend;
  final requests = <http.Request>[];
  final _responses = <http.StreamedResponse>[];
  int consumedChunkCount = 0;

  void queueJson(int status, Map<String, Object?> body) {
    queueText(status, jsonEncode(body));
  }

  void queueText(int status, String body) {
    _responses.add(
      http.StreamedResponse(Stream<List<int>>.value(utf8.encode(body)), status),
    );
  }

  void queueChunks(int status, List<List<int>> chunks) {
    _responses.add(
      http.StreamedResponse(
        Stream<List<int>>.fromIterable(chunks).map((chunk) {
          consumedChunkCount++;
          return chunk;
        }),
        status,
      ),
    );
  }

  @override
  Future<http.StreamedResponse> send(http.BaseRequest request) async {
    if (failSend) {
      throw StateError('neutral transport failure');
    }
    final captured = request as http.Request;
    requests.add(captured);
    return _responses.removeAt(0);
  }
}

Map<String, Object?> _problem(String code) => <String, Object?>{
  'detail': <String, Object?>{
    'code': code,
    'message': 'safe problem',
    'retryable': false,
  },
};

Map<String, Object?> _open() => <String, Object?>{
  'schema_version': frameworkV600OpenSchema,
  'status': 'open',
  'available': true,
  'session_id': _sessionId,
  'public_error_code': null,
  'safe_message': '',
  'retryable': false,
  'real_runtime_requested': false,
  'real_runtime_enabled': false,
  'runtime_executable': true,
  'capabilities': _capabilities(),
};

Map<String, Object?> _capabilities() => <String, Object?>{
  'schema_version': frameworkV600CapabilitySchema,
  'session_id': _sessionId,
  'supports_text_chat': true,
  'supports_voice_input': true,
  'supports_voice_output': true,
  'supports_motion': false,
  'real_runtime_enabled': false,
  'hard_cancel_supported': false,
  'tts_queue_flush_supported': true,
  'runtime_available': true,
  'fake_runtime': 'provider_free',
  'real_runtime': 'unavailable',
  'guarded': true,
  'cooperative_cancel_supported': true,
  'provider_hard_cancel_supported': false,
  'pending_flush_supported': true,
  'host_playback_owned_by_drc': true,
  'real_unified_runtime_available': false,
  'unified_real_pipeline_claimed': false,
};

Map<String, Object?> _turn({String outcome = 'completed'}) => <String, Object?>{
  'schema_version': frameworkV600TurnSchema,
  'outcome': outcome,
  'terminal': true,
  'session_id': _sessionId,
  'turn_id': _turnId,
  'generation_id': _generationId,
  'public_error_code': null,
  'safe_message': '',
  'retryable': false,
  'recovery_action': 'none',
  'events': const [],
  'capabilities': _capabilities(),
  'interrupt': null,
  'diagnostics': null,
};

Map<String, Object?> _interrupt({
  String scope = 'current_turn',
  String reason = 'host_app_request',
}) => <String, Object?>{
  'schema_version': frameworkV600InterruptSchema,
  'outcome': 'accepted',
  'scope': scope,
  'reason': reason,
  'provider_cancel_supported': false,
  'provider_cancel_applied': false,
  'queue_flush_supported': true,
  'queue_flush_applied': true,
  'host_playback_stop_supported': false,
  'host_playback_stop_applied': false,
  'safe_message': 'safe',
  'retryable': false,
};

Map<String, Object?> _diagnostics() => <String, Object?>{
  'schema_version': frameworkV600DiagnosticsSchema,
  'session_id': _sessionId,
  'state': 'idle',
  'phase': 'ready',
  'is_closed': false,
  'active_turn_id': null,
  'active_generation_id': null,
  'queue_depth': 0,
  'active_generation_count': 0,
  'last_terminal_event_type': null,
  'last_terminal_turn_id': null,
  'last_terminal_generation_id': null,
  'last_terminal_outcome': null,
  'last_terminal_public_error_code': null,
  'last_terminal_retryable': false,
  'last_terminal_recovery_action': null,
  'last_safe_error_code': null,
  'stale_completion_count': 0,
  'duplicate_terminal_count': 0,
  'overflow_count': 0,
};
