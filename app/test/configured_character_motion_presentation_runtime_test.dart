import 'dart:convert';

import 'package:app/models/character_motion_presentation.dart';
import 'package:app/services/backend_api_client.dart';
import 'package:app/services/configured_character_motion_presentation_runtime.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;

void main() {
  group('ConfiguredCharacterMotionPresentationRuntime', () {
    test('disabled runtime returns null without creating HTTP client', () {
      var factoryCalls = 0;
      final runtime = ConfiguredCharacterMotionPresentationRuntime(
        enabled: false,
        apiClient: const BackendApiClient(baseUrl: 'https://backend.test'),
        httpClientFactory: () {
          factoryCalls += 1;
          return _ScriptedHttpClient();
        },
      );

      expect(runtime.buildControllerFactory(), isNull);
      expect(factoryCalls, 0);
    });

    test('enabled runtime accepts valid HTTP and HTTPS base URLs', () {
      for (final baseUrl in <String>[
        'http://backend.test',
        'https://backend.test/api/',
      ]) {
        final runtime = ConfiguredCharacterMotionPresentationRuntime(
          enabled: true,
          apiClient: BackendApiClient(baseUrl: baseUrl),
          httpClientFactory: _ScriptedHttpClient.new,
        );
        expect(runtime.buildControllerFactory(), isNotNull);
      }
    });

    test('invalid base URLs fail closed without creating clients', () {
      const invalid = <String>[
        '',
        'not a uri',
        '/relative',
        'ftp://backend.test',
        'http:///missing-host',
        'https://user:pass@backend.test',
        'https://backend.test/#fragment',
      ];

      for (final baseUrl in invalid) {
        var factoryCalls = 0;
        final runtime = ConfiguredCharacterMotionPresentationRuntime(
          enabled: true,
          apiClient: BackendApiClient(baseUrl: baseUrl),
          httpClientFactory: () {
            factoryCalls += 1;
            return _ScriptedHttpClient();
          },
        );
        expect(runtime.buildControllerFactory(), isNull);
        expect(factoryCalls, 0);
      }
    });

    test('factory lookup is lazy and controller creation sends no request', () {
      final clients = <_ScriptedHttpClient>[];
      final runtime = ConfiguredCharacterMotionPresentationRuntime(
        enabled: true,
        apiClient: const BackendApiClient(baseUrl: 'https://backend.test'),
        httpClientFactory: () {
          final client = _ScriptedHttpClient();
          clients.add(client);
          return client;
        },
      );

      final factory = runtime.buildControllerFactory();
      expect(factory, isNotNull);
      expect(clients, isEmpty);

      final controller = factory!();
      expect(clients, hasLength(1));
      expect(clients.single.requests, isEmpty);

      controller.dispose();
      controller.dispose();
      expect(clients.single.closeCalls, 1);
    });

    test(
      'one explicit apply sends one strict POST and parses result',
      () async {
        final httpClient = _ScriptedHttpClient(responseBody: _result());
        final runtime = ConfiguredCharacterMotionPresentationRuntime(
          enabled: true,
          apiClient: const BackendApiClient(
            baseUrl: '  https://backend.test/api/  ',
          ),
          httpClientFactory: () => httpClient,
        );
        final controller = runtime.buildControllerFactory()!();
        final request = CharacterMotionPresentationRequest(
          sourceFact: CharacterMotionLifecycleFact.speaking,
          sourceEventType: 'home_screen_manual_motion',
          sourceSessionId: null,
          sourceTurnId: null,
          characterId: 'gentle_mina',
        );

        await controller.apply(request);

        expect(httpClient.requests, hasLength(1));
        final recorded = httpClient.requests.single;
        expect(recorded.method, 'POST');
        expect(
          recorded.uri.toString(),
          'https://backend.test/api/demo/character-motion/presentation',
        );
        expect(recorded.followRedirects, isFalse);
        expect(recorded.maxRedirects, 0);
        expect(recorded.headers['accept'], 'application/json');
        expect(recorded.body, <String, Object?>{
          'schema_version': 'drc.v3.character-motion-presentation-request.1',
          'source_fact': 'speaking',
          'source_event_type': 'home_screen_manual_motion',
          'source_session_id': null,
          'source_turn_id': null,
          'character_id': 'gentle_mina',
        });
        expect(
          controller.state.phase,
          CharacterMotionPresentationPhase.completed,
        );
        expect(
          controller.state.result?.status,
          CharacterMotionExecutionStatus.completed,
        );
        expect(controller.state.result?.networkExecution, isFalse);

        controller.dispose();
        expect(httpClient.closeCalls, 1);
      },
    );

    for (final response in <_ResponseScript>[
      const _ResponseScript(statusCode: 302),
      const _ResponseScript(statusCode: 500),
      const _ResponseScript(contentType: 'text/plain'),
      const _ResponseScript(contentType: 'application/jsonp'),
      const _ResponseScript(body: '[]'),
      const _ResponseScript(body: '{not-json'),
      _ResponseScript(
        body: jsonEncode(<String, Object?>{
          'private': List<String>.filled(70000, 'x').join(),
        }),
      ),
    ]) {
      test(
        'unsafe or malformed response becomes generic transport failure',
        () async {
          final httpClient = _ScriptedHttpClient(
            statusCode: response.statusCode,
            contentType: response.contentType,
            rawResponseBody: response.body,
          );
          final controller = ConfiguredCharacterMotionPresentationRuntime(
            enabled: true,
            apiClient: const BackendApiClient(baseUrl: 'https://backend.test'),
            httpClientFactory: () => httpClient,
          ).buildControllerFactory()!();

          await controller.apply(
            CharacterMotionPresentationRequest(
              sourceFact: CharacterMotionLifecycleFact.idle,
              sourceEventType: 'home_screen_manual_motion',
            ),
          );

          expect(
            controller.state.phase,
            CharacterMotionPresentationPhase.failed,
          );
          expect(controller.state.problem?.code, 'motion_transport_failed');
          expect(
            controller.state.problem?.message,
            'The character-motion presentation request failed.',
          );
          expect(
            controller.state.problem.toString(),
            isNot(contains('private')),
          );
          controller.dispose();
        },
      );
    }

    test('timeout bounds the complete streamed response', () async {
      final httpClient = _ScriptedHttpClient(
        responseBody: _result(),
        streamChunkDelay: const Duration(milliseconds: 15),
        splitResponseAt: 1,
      );
      final controller = ConfiguredCharacterMotionPresentationRuntime(
        enabled: true,
        apiClient: const BackendApiClient(baseUrl: 'https://backend.test'),
        httpClientFactory: () => httpClient,
        requestTimeout: const Duration(milliseconds: 20),
      ).buildControllerFactory()!();

      await controller.apply(
        CharacterMotionPresentationRequest(
          sourceFact: CharacterMotionLifecycleFact.idle,
          sourceEventType: 'home_screen_manual_motion',
        ),
      );

      expect(controller.state.phase, CharacterMotionPresentationPhase.failed);
      expect(controller.state.problem?.code, 'motion_transport_failed');
      controller.dispose();
    });
  });
}

class _ResponseScript {
  const _ResponseScript({
    this.statusCode = 200,
    this.contentType = 'application/json; charset=utf-8',
    this.body = '{}',
  });

  final int statusCode;
  final String contentType;
  final String body;
}

class _RecordedRequest {
  const _RecordedRequest({
    required this.method,
    required this.uri,
    required this.headers,
    required this.body,
    required this.followRedirects,
    required this.maxRedirects,
  });

  final String method;
  final Uri uri;
  final Map<String, String> headers;
  final Map<String, Object?> body;
  final bool followRedirects;
  final int maxRedirects;
}

class _ScriptedHttpClient extends http.BaseClient {
  _ScriptedHttpClient({
    Map<String, Object?>? responseBody,
    this.statusCode = 200,
    this.contentType = 'application/json; charset=utf-8',
    String? rawResponseBody,
    this.streamChunkDelay = Duration.zero,
    this.splitResponseAt,
  }) : responseBody = rawResponseBody ?? jsonEncode(responseBody ?? _result());

  final int statusCode;
  final String contentType;
  final String responseBody;
  final Duration streamChunkDelay;
  final int? splitResponseAt;
  final List<_RecordedRequest> requests = <_RecordedRequest>[];
  int closeCalls = 0;

  @override
  Future<http.StreamedResponse> send(http.BaseRequest request) async {
    final bodyBytes = await request.finalize().toBytes();
    final decodedBody = jsonDecode(utf8.decode(bodyBytes));
    requests.add(
      _RecordedRequest(
        method: request.method,
        uri: request.url,
        headers: Map<String, String>.from(request.headers),
        body: Map<String, Object?>.from(decodedBody as Map<String, dynamic>),
        followRedirects: request.followRedirects,
        maxRedirects: request.maxRedirects,
      ),
    );
    final bytes = utf8.encode(responseBody);
    final split = splitResponseAt;
    final chunks = split != null && split > 0 && split < bytes.length
        ? <List<int>>[bytes.sublist(0, split), bytes.sublist(split)]
        : <List<int>>[bytes];
    var stream = Stream<List<int>>.fromIterable(chunks);
    if (streamChunkDelay != Duration.zero) {
      stream = stream.asyncMap((chunk) async {
        await Future<void>.delayed(streamChunkDelay);
        return chunk;
      });
    }
    return http.StreamedResponse(
      stream,
      statusCode,
      headers: <String, String>{'content-type': contentType},
      contentLength: bytes.length,
      request: request,
    );
  }

  @override
  void close() {
    closeCalls += 1;
    super.close();
  }
}

Map<String, Object?> _result() => <String, Object?>{
  'schema_version': 'drc.v3.framework-mock-motion-execution.1',
  'status': 'completed',
  'source_fact': 'speaking',
  'cue': 'speaking',
  'source_event_type': 'home_screen_manual_motion',
  'source_session_id': null,
  'source_turn_id': null,
  'character_id': 'gentle_mina',
  'commands_requested': 1,
  'commands_completed': 1,
  'command_results': <Object?>[
    <String, Object?>{
      'order': 1,
      'intent': 'speaking_state',
      'outcome': 'completed',
      'state': 'speaking',
      'adapter_status': 'mock_available',
      'public_error_code': 'none',
      'retryable': false,
      'safe_message': '',
    },
  ],
  'event_types': <String>['motion.completed'],
  'framework_import_attempted': true,
  'session_created': true,
  'session_closed': true,
  'adapter': 'mock',
  'real_adapter_enabled': false,
  'provider_execution_allowed': false,
  'provider_execution_attempted': false,
  'network_execution': false,
  'reason_code': 'framework_mock_motion_completed',
  'safe_message': 'Framework mock motion commands completed locally.',
};
