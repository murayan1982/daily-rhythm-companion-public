import 'dart:async';
import 'dart:convert';

import 'package:app/main.dart';
import 'package:app/models/character_preset.dart';
import 'package:app/models/demo_status.dart';
import 'package:app/models/framework_v600_realtime_session.dart';
import 'package:app/models/sleep_provider_selection.dart';
import 'package:app/models/sleep_summary.dart';
import 'package:app/services/backend_api_client.dart';
import 'package:app/services/configured_framework_v600_realtime_session_runtime.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;

void main() {
  testWidgets('default app leaves FW-v6 session unconfigured', (tester) async {
    await tester.pumpWidget(
      const DailyRhythmCompanionApp(apiClient: _FakeBackendApiClient()),
    );
    await tester.pumpAndSettle();

    expect(
      _textByKey(tester, 'framework-v600-realtime-configuration'),
      'configuration: unconfigured',
    );
    expect(
      _button(tester, 'framework-v600-realtime-open-button').enabled,
      isFalse,
    );
  });

  testWidgets('configured factory composition is lazy', (tester) async {
    final httpClient = _FakeFrameworkV600HttpClient();
    var factoryCalls = 0;
    var httpClientCalls = 0;
    final runtime = ConfiguredFrameworkV600RealtimeSessionRuntime(
      enabled: true,
      baseUrl: 'https://backend.test',
      httpClientFactory: () {
        httpClientCalls += 1;
        return httpClient;
      },
    );
    final runtimeFactory = runtime.buildControllerFactory()!;

    await tester.pumpWidget(
      DailyRhythmCompanionApp(
        apiClient: const _FakeBackendApiClient(),
        frameworkV600RealtimeSessionControllerFactory: () {
          factoryCalls += 1;
          return runtimeFactory();
        },
      ),
    );
    await tester.pumpAndSettle();

    expect(
      _textByKey(tester, 'framework-v600-realtime-configuration'),
      'configuration: configured',
    );
    expect(factoryCalls, 0);
    expect(httpClientCalls, 0);
    expect(httpClient.requests, isEmpty);
  });

  testWidgets('pump build and settle do not activate FW-v6 factory', (
    tester,
  ) async {
    final httpClient = _FakeFrameworkV600HttpClient();
    var factoryCalls = 0;
    var httpClientCalls = 0;
    final runtime = ConfiguredFrameworkV600RealtimeSessionRuntime(
      enabled: true,
      baseUrl: 'https://backend.test',
      httpClientFactory: () {
        httpClientCalls += 1;
        return httpClient;
      },
    );
    final runtimeFactory = runtime.buildControllerFactory()!;

    await tester.pumpWidget(
      DailyRhythmCompanionApp(
        apiClient: const _FakeBackendApiClient(),
        frameworkV600RealtimeSessionControllerFactory: () {
          factoryCalls += 1;
          return runtimeFactory();
        },
      ),
    );
    await tester.pump();
    await tester.pumpAndSettle();

    expect(factoryCalls, 0);
    expect(httpClientCalls, 0);
    expect(httpClient.requests, isEmpty);
  });

  testWidgets('explicit Open activates factory and create-session once', (
    tester,
  ) async {
    final httpClient = _FakeFrameworkV600HttpClient()..queueJson(201, _open());
    var factoryCalls = 0;
    var httpClientCalls = 0;
    final runtime = ConfiguredFrameworkV600RealtimeSessionRuntime(
      enabled: true,
      baseUrl: 'https://backend.test',
      httpClientFactory: () {
        httpClientCalls += 1;
        return httpClient;
      },
    );
    final runtimeFactory = runtime.buildControllerFactory()!;

    await tester.pumpWidget(
      DailyRhythmCompanionApp(
        apiClient: const _FakeBackendApiClient(),
        frameworkV600RealtimeSessionControllerFactory: () {
          factoryCalls += 1;
          return runtimeFactory();
        },
      ),
    );
    await tester.pumpAndSettle();

    await tester.ensureVisible(
      find.byKey(const ValueKey('framework-v600-realtime-open-button')),
    );
    await tester.tap(
      find.byKey(const ValueKey('framework-v600-realtime-open-button')),
    );
    await tester.pumpAndSettle();

    expect(factoryCalls, 1);
    expect(httpClientCalls, 1);
    expect(
      _matching(
        httpClient,
        'POST',
        '/realtime/framework-v6/provider-free/sessions',
      ),
      1,
    );
  });

  testWidgets('dispose before Open does not create FW-v6 request or DELETE', (
    tester,
  ) async {
    final httpClient = _FakeFrameworkV600HttpClient();
    var factoryCalls = 0;
    var httpClientCalls = 0;
    final runtime = ConfiguredFrameworkV600RealtimeSessionRuntime(
      enabled: true,
      baseUrl: 'https://backend.test',
      httpClientFactory: () {
        httpClientCalls += 1;
        return httpClient;
      },
    );
    final runtimeFactory = runtime.buildControllerFactory()!;

    await tester.pumpWidget(
      DailyRhythmCompanionApp(
        apiClient: const _FakeBackendApiClient(),
        frameworkV600RealtimeSessionControllerFactory: () {
          factoryCalls += 1;
          return runtimeFactory();
        },
      ),
    );
    await tester.pumpAndSettle();
    await tester.pumpWidget(const MaterialApp(home: SizedBox.shrink()));
    await tester.pump();

    expect(factoryCalls, 0);
    expect(httpClientCalls, 0);
    expect(httpClient.requests, isEmpty);
    expect(
      _matching(
        httpClient,
        'DELETE',
        '/realtime/framework-v6/provider-free/sessions/$_sessionId',
      ),
      0,
    );
  });
}

ButtonStyleButton _button(WidgetTester tester, String key) {
  return tester.widget<ButtonStyleButton>(find.byKey(ValueKey(key)));
}

String _textByKey(WidgetTester tester, String key) {
  return tester.widget<Text>(find.byKey(ValueKey(key))).data!;
}

int _matching(_FakeFrameworkV600HttpClient client, String method, String path) {
  return client.requests
      .where((request) => request.method == method && request.url.path == path)
      .length;
}

class _FakeFrameworkV600HttpClient extends http.BaseClient {
  final requests = <http.BaseRequest>[];
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
    requests.add(request);
    return _responses.removeAt(0);
  }
}

class _FakeBackendApiClient extends BackendApiClient {
  const _FakeBackendApiClient() : super(baseUrl: 'https://backend.test');

  @override
  Future<String> fetchHealthStatus() async => 'ok / API v2.1.0';

  @override
  Future<List<CharacterPreset>> fetchCharacters() async =>
      const <CharacterPreset>[
        CharacterPreset(
          characterId: 'default',
          displayName: 'Default',
          description: 'Default test character',
          personalityType: 'friendly',
          speakingStyle: 'casual',
          adviceStyle: 'light',
        ),
      ];

  @override
  Future<SleepSummary> fetchSleepSummary() async => const SleepSummary(
    date: '2026-07-30',
    totalSleepMinutes: 420,
    efficiency: 88,
    deepSleepMinutes: 80,
    remSleepMinutes: 90,
    awakeMinutes: 20,
    source: 'mock',
    available: true,
  );

  @override
  Future<SleepProviderSelectionStatus>
  fetchSleepProviderSelectionStatus() async =>
      const SleepProviderSelectionStatus(
        configuredProvider: 'mock',
        configuredProviderLabel: 'Mock',
        configuredProviderRole: 'credential_free_default',
        configuredProviderSupported: true,
        selectionMode: 'backend_config',
        changeRequiresBackendRestart: true,
        availableProviders: <SleepProviderOption>[],
        message: 'Mock provider selected.',
      );

  @override
  Future<DemoStatus> fetchDemoStatus() async => const DemoStatus(
    engine: 'mock',
    mode: 'mock_safe',
    capabilities: <String, DemoCapabilityStatus>{},
  );
}

const _sessionId = 'fw_session_0123456789abcdef0123456789abcdef';

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
