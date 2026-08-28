import 'dart:async';
import 'dart:convert';

import 'package:app/models/framework_v600_realtime_session.dart';
import 'package:app/services/backend_api_client.dart';
import 'package:app/services/configured_framework_v600_realtime_session_runtime.dart';
import 'package:app/services/framework_v600_realtime_session_controller.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;

void main() {
  group('ConfiguredFrameworkV600RealtimeSessionRuntime', () {
    test('disabled runtime returns null factory', () {
      var httpClientFactoryCalls = 0;
      final runtime = ConfiguredFrameworkV600RealtimeSessionRuntime(
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

    test('enabled valid http URL returns factory', () {
      final runtime = ConfiguredFrameworkV600RealtimeSessionRuntime(
        enabled: true,
        baseUrl: 'http://backend.test',
        httpClientFactory: _FailingHttpClient.new,
      );

      expect(runtime.buildControllerFactory(), isNotNull);
    });

    test('enabled valid https URL returns factory', () {
      final runtime = ConfiguredFrameworkV600RealtimeSessionRuntime(
        enabled: true,
        baseUrl: 'https://backend.test',
        httpClientFactory: _FailingHttpClient.new,
      );

      expect(runtime.buildControllerFactory(), isNotNull);
    });

    test('invalid base URLs return null without creating clients', () {
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
        final runtime = ConfiguredFrameworkV600RealtimeSessionRuntime(
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

    test('runtime construction is lazy', () {
      var httpClientFactoryCalls = 0;
      ConfiguredFrameworkV600RealtimeSessionRuntime(
        enabled: true,
        baseUrl: 'https://backend.test',
        httpClientFactory: () {
          httpClientFactoryCalls += 1;
          return _FailingHttpClient();
        },
      );

      expect(httpClientFactoryCalls, 0);
    });

    test('buildControllerFactory lookup is lazy', () {
      var httpClientFactoryCalls = 0;
      final runtime = ConfiguredFrameworkV600RealtimeSessionRuntime(
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

    test('factory invocation creates independent ownership', () {
      final httpClients = <_FailingHttpClient>[];
      final runtime = ConfiguredFrameworkV600RealtimeSessionRuntime(
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

    test('newly created controller is idle and does not open automatically', () {
      final httpClient = _FailingHttpClient();
      final runtime = ConfiguredFrameworkV600RealtimeSessionRuntime(
        enabled: true,
        baseUrl: 'https://backend.test',
        httpClientFactory: () => httpClient,
      );

      final controller = runtime.buildControllerFactory()!();

      expect(controller.state.phase, FrameworkV600RealtimeSessionPhase.idle);
      expect(httpClient.sendCalls, 0);
      controller.dispose();
    });

    test('controller dispose closes owned HTTP client without DELETE', () {
      final httpClient = _FailingHttpClient();
      final runtime = ConfiguredFrameworkV600RealtimeSessionRuntime(
        enabled: true,
        baseUrl: 'https://backend.test',
        httpClientFactory: () => httpClient,
      );

      final controller = runtime.buildControllerFactory()!();
      controller.dispose();

      expect(httpClient.closeCalls, 1);
      expect(httpClient.sendCalls, 0);
    });

    test('explicit open uses trimmed base URL and preserves path prefix', () async {
      final httpClient = _RecordingHttpClient()..queueJson(201, _open());
      final runtime = ConfiguredFrameworkV600RealtimeSessionRuntime(
        enabled: true,
        baseUrl: '  https://example.invalid:8443/api/  ',
        httpClientFactory: () => httpClient,
      );

      final controller = runtime.buildControllerFactory()!();
      await controller.open();

      expect(httpClient.requests, hasLength(1));
      final request = httpClient.requests.single;
      expect(request.method, 'POST');
      expect(request.url.scheme, 'https');
      expect(request.url.host, 'example.invalid');
      expect(request.url.port, 8443);
      expect(
        request.url.path,
        '/api/realtime/framework-v6/provider-free/sessions',
      );
      expect(request.url.toString(), isNot(contains(' ')));

      controller.dispose();
    });

    test('environment factory uses BackendApiClient base URL', () async {
      final httpClient = _RecordingHttpClient()..queueJson(201, _open());
      final runtime =
          ConfiguredFrameworkV600RealtimeSessionRuntime.fromEnvironment(
            apiClient: const BackendApiClient(
              baseUrl: '  https://example.invalid/api/  ',
            ),
            httpClientFactory: () => httpClient,
          );

      expect(runtime.buildControllerFactory(), isNull);
      expect(httpClient.requests, isEmpty);
    });
  });
}

const _sessionId = 'fw_session_0123456789abcdef0123456789abcdef';

class _RecordingHttpClient extends http.BaseClient {
  final requests = <http.Request>[];
  final _responses = <http.StreamedResponse>[];

  void queueJson(int status, Map<String, Object?> body) {
    _responses.add(
      http.StreamedResponse(
        Stream<List<int>>.value(utf8.encode(jsonEncode(body))),
        status,
      ),
    );
  }

  @override
  Future<http.StreamedResponse> send(http.BaseRequest request) async {
    requests.add(request as http.Request);
    return _responses.removeAt(0);
  }
}

class _FailingHttpClient extends http.BaseClient {
  var sendCalls = 0;
  var closeCalls = 0;

  @override
  Future<http.StreamedResponse> send(http.BaseRequest request) async {
    sendCalls += 1;
    fail('Configured runtime tests must not execute implicit HTTP requests.');
  }

  @override
  void close() {
    closeCalls += 1;
    super.close();
  }
}

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
  'capabilities': <String, Object?>{
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
  },
};
