import 'dart:async';
import 'dart:convert';

import 'package:app/services/configured_realtime_text_stream_runtime.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;

void main() {
  group('ConfiguredRealtimeTextStreamRuntime', () {
    test('disabled runtime returns null and does not create HTTP client', () {
      var httpClientFactoryCalls = 0;
      final runtime = ConfiguredRealtimeTextStreamRuntime(
        enabled: false,
        baseUrl: 'http://backend.test',
        httpClientFactory: () {
          httpClientFactoryCalls += 1;
          return _FailingHttpClient();
        },
      );

      expect(runtime.buildControllerFactory(), isNull);
      expect(httpClientFactoryCalls, 0);
    });

    test('enabled runtime accepts valid HTTP and HTTPS URLs', () {
      final httpRuntime = ConfiguredRealtimeTextStreamRuntime(
        enabled: true,
        baseUrl: 'http://backend.test',
        httpClientFactory: _FailingHttpClient.new,
      );
      final httpsRuntime = ConfiguredRealtimeTextStreamRuntime(
        enabled: true,
        baseUrl: 'https://backend.test',
        httpClientFactory: _FailingHttpClient.new,
      );

      expect(httpRuntime.buildControllerFactory(), isNotNull);
      expect(httpsRuntime.buildControllerFactory(), isNotNull);
    });

    test('runtime construction and factory lookup are lazy', () {
      var httpClientFactoryCalls = 0;
      final runtime = ConfiguredRealtimeTextStreamRuntime(
        enabled: true,
        baseUrl: 'https://backend.test',
        httpClientFactory: () {
          httpClientFactoryCalls += 1;
          return _FailingHttpClient();
        },
      );

      final controllerFactory = runtime.buildControllerFactory();

      expect(controllerFactory, isNotNull);
      expect(httpClientFactoryCalls, 0);
    });

    test('controller factory creates independent controllers and clients', () {
      final httpClients = <_FailingHttpClient>[];
      final runtime = ConfiguredRealtimeTextStreamRuntime(
        enabled: true,
        baseUrl: 'https://backend.test',
        httpClientFactory: () {
          final client = _FailingHttpClient();
          httpClients.add(client);
          return client;
        },
      );
      final controllerFactory = runtime.buildControllerFactory()!;

      final first = controllerFactory();
      final second = controllerFactory();

      expect(identical(first, second), false);
      expect(httpClients, hasLength(2));
      expect(httpClients.first.sendCalls, 0);
      expect(httpClients.last.sendCalls, 0);

      first.dispose();
      second.dispose();
      expect(httpClients.first.closeCalls, 1);
      expect(httpClients.last.closeCalls, 1);
    });

    test('controller creation alone sends no request', () {
      final httpClient = _FailingHttpClient();
      final runtime = ConfiguredRealtimeTextStreamRuntime(
        enabled: true,
        baseUrl: 'https://backend.test',
        httpClientFactory: () => httpClient,
      );

      final controller = runtime.buildControllerFactory()!();

      expect(httpClient.sendCalls, 0);
      controller.dispose();
      expect(httpClient.closeCalls, 1);
    });

    test('trimmed base URL is used at the client request boundary', () async {
      final httpClient = _RecordingHttpClient();
      final runtime = ConfiguredRealtimeTextStreamRuntime(
        enabled: true,
        baseUrl: '  https://example.invalid:8443/api/  ',
        httpClientFactory: () => httpClient,
      );

      final controller = runtime.buildControllerFactory()!();
      await controller.start(inputText: 'public input');

      expect(httpClient.requests, hasLength(1));
      final uri = httpClient.requests.single.url;
      expect(uri.scheme, 'https');
      expect(uri.host, 'example.invalid');
      expect(uri.port, 8443);
      expect(uri.path, '/api/realtime/text/sessions');
      expect(uri.toString(), isNot(contains(' ')));

      controller.dispose();
    });

    test('invalid URLs return null without creating clients or throwing', () {
      const invalidBaseUrls = <String>[
        '',
        'not a uri',
        '/relative',
        'ftp://backend.test',
        'http:///missing-host',
        'https://user:pass@backend.test',
        'https://backend.test/#fragment',
      ];

      for (final baseUrl in invalidBaseUrls) {
        var httpClientFactoryCalls = 0;
        final runtime = ConfiguredRealtimeTextStreamRuntime(
          enabled: true,
          baseUrl: baseUrl,
          httpClientFactory: () {
            httpClientFactoryCalls += 1;
            return _FailingHttpClient();
          },
        );

        expect(runtime.buildControllerFactory(), isNull);
        expect(httpClientFactoryCalls, 0);
      }
    });
  });
}

class _RecordingHttpClient extends http.BaseClient {
  final requests = <http.BaseRequest>[];

  @override
  Future<http.StreamedResponse> send(http.BaseRequest request) async {
    requests.add(request);
    final body = jsonEncode(<String, Object?>{
      'accepted': true,
      'session': <String, Object?>{
        'session_id': 'session-1',
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
        'started_at_ms': 1,
        'expires_at_ms': 2,
      },
      'events_path': '/api/realtime/text/sessions/session-1/events',
      'cancel_path': '/api/realtime/text/sessions/session-1/cancel',
      'idle_ttl_seconds': 30,
      'max_duration_seconds': 60,
      'max_pending_events': 16,
      'max_event_bytes': 32768,
    });
    return http.StreamedResponse(
      Stream<List<int>>.value(utf8.encode(body)),
      201,
      request: request,
    );
  }
}

class _FailingHttpClient extends http.BaseClient {
  var sendCalls = 0;
  var closeCalls = 0;

  @override
  Future<http.StreamedResponse> send(http.BaseRequest request) async {
    sendCalls += 1;
    fail('Configured runtime tests must not execute HTTP requests.');
  }

  @override
  void close() {
    closeCalls += 1;
    super.close();
  }
}
