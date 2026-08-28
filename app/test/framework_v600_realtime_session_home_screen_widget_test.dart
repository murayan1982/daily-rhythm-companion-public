import 'dart:async';
import 'dart:convert';

import 'package:app/models/character_preset.dart';
import 'package:app/models/demo_status.dart';
import 'package:app/models/framework_v600_realtime_session.dart';
import 'package:app/models/sleep_provider_selection.dart';
import 'package:app/models/sleep_summary.dart';
import 'package:app/screens/home_screen.dart';
import 'package:app/services/backend_api_client.dart';
import 'package:app/services/framework_v600_realtime_session_client.dart';
import 'package:app/services/framework_v600_realtime_session_controller.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;

void main() {
  testWidgets('unconfigured HomeScreen keeps Open disabled and sends no FW-v6 request', (
    tester,
  ) async {
    await _pump(tester);

    expect(_textByKey(tester, 'framework-v600-realtime-configuration'), 'configuration: unconfigured');
    expect(_button(tester, 'framework-v600-realtime-open-button').enabled, false);
  });

  testWidgets('configured HomeScreen pump only does not call factory or FW-v6', (
    tester,
  ) async {
    final httpClient = _FakeFrameworkV600HttpClient();
    var factoryCalls = 0;

    await _pump(
      tester,
      factory: () {
        factoryCalls += 1;
        return _controller(httpClient);
      },
    );

    expect(_textByKey(tester, 'framework-v600-realtime-configuration'), 'configuration: configured');
    expect(factoryCalls, 0);
    expect(httpClient.requests, isEmpty);
  });

  testWidgets('explicit Open tap invokes factory exactly once', (tester) async {
    final httpClient = _FakeFrameworkV600HttpClient()..queueJson(201, _open());
    var factoryCalls = 0;
    await _pump(
      tester,
      factory: () {
        factoryCalls += 1;
        return _controller(httpClient);
      },
    );

    _pressButton(tester, 'framework-v600-realtime-open-button');
    await tester.pumpAndSettle();

    expect(factoryCalls, 1);
  });

  testWidgets('explicit Open sends session create POST exactly once', (tester) async {
    final httpClient = _FakeFrameworkV600HttpClient()..queueJson(201, _open());
    await _pump(tester, factory: () => _controller(httpClient));

    _pressButton(tester, 'framework-v600-realtime-open-button');
    await tester.pumpAndSettle();

    expect(_matching(httpClient, 'POST', '/realtime/framework-v6/provider-free/sessions'), 1);
  });

  testWidgets('Send disabled before ready', (tester) async {
    await _pump(
      tester,
      factory: () => _controller(_FakeFrameworkV600HttpClient()),
    );
    await tester.enterText(find.byKey(const ValueKey('framework-v600-realtime-input')), 'hello');
    await tester.pump();

    expect(_button(tester, 'framework-v600-realtime-send-button').enabled, false);
  });

  testWidgets('blank input cannot send', (tester) async {
    final httpClient = _FakeFrameworkV600HttpClient()..queueJson(201, _open());
    await _pump(tester, factory: () => _controller(httpClient));
    _pressButton(tester, 'framework-v600-realtime-open-button');
    await tester.pumpAndSettle();

    await tester.enterText(find.byKey(const ValueKey('framework-v600-realtime-input')), '   ');
    await tester.pump();

    expect(_button(tester, 'framework-v600-realtime-send-button').enabled, false);
    expect(_matching(httpClient, 'POST', '/realtime/framework-v6/provider-free/sessions/$_sessionId/turns'), 0);
  });

  testWidgets('ready explicit Send posts a turn exactly once', (tester) async {
    final httpClient = _FakeFrameworkV600HttpClient()
      ..queueJson(201, _open())
      ..queueJson(200, _turn(safeMessage: 'safe done'));
    await _pump(tester, factory: () => _controller(httpClient));
    _pressButton(tester, 'framework-v600-realtime-open-button');
    await tester.pumpAndSettle();
    await tester.enterText(find.byKey(const ValueKey('framework-v600-realtime-input')), '  keep exact  ');
    await tester.pump();

    _pressButton(tester, 'framework-v600-realtime-send-button');
    await tester.pumpAndSettle();

    expect(_matching(httpClient, 'POST', '/realtime/framework-v6/provider-free/sessions/$_sessionId/turns'), 1);
    final turnRequest = httpClient.requests.last as http.Request;
    expect(jsonDecode(turnRequest.body), <String, Object?>{'input_text': '  keep exact  '});
  });

  testWidgets('explicit Interrupt posts once and only after tap', (tester) async {
    final httpClient = _FakeFrameworkV600HttpClient()
      ..queueJson(201, _open())
      ..queueJson(200, _interrupt());
    await _pump(tester, factory: () => _controller(httpClient));
    _pressButton(tester, 'framework-v600-realtime-open-button');
    await tester.pumpAndSettle();
    expect(_matching(httpClient, 'POST', '/realtime/framework-v6/provider-free/sessions/$_sessionId/interrupt'), 0);

    _pressButton(tester, 'framework-v600-realtime-interrupt-button');
    await tester.pumpAndSettle();

    expect(_matching(httpClient, 'POST', '/realtime/framework-v6/provider-free/sessions/$_sessionId/interrupt'), 1);
  });

  testWidgets('explicit Diagnostics gets once and only after tap', (tester) async {
    final httpClient = _FakeFrameworkV600HttpClient()
      ..queueJson(201, _open())
      ..queueJson(200, _diagnostics());
    await _pump(tester, factory: () => _controller(httpClient));
    _pressButton(tester, 'framework-v600-realtime-open-button');
    await tester.pumpAndSettle();
    expect(_matching(httpClient, 'GET', '/realtime/framework-v6/provider-free/sessions/$_sessionId/diagnostics'), 0);

    _pressButton(tester, 'framework-v600-realtime-diagnostics-button');
    await tester.pumpAndSettle();

    expect(_matching(httpClient, 'GET', '/realtime/framework-v6/provider-free/sessions/$_sessionId/diagnostics'), 1);
  });

  testWidgets('explicit Close deletes once with no hidden extra DELETE', (tester) async {
    final httpClient = _FakeFrameworkV600HttpClient()
      ..queueJson(201, _open())
      ..queueText(204, '');
    await _pump(tester, factory: () => _controller(httpClient));
    _pressButton(tester, 'framework-v600-realtime-open-button');
    await tester.pumpAndSettle();

    _pressButton(tester, 'framework-v600-realtime-close-button');
    await tester.pumpAndSettle();
    await tester.pumpWidget(const MaterialApp(home: SizedBox.shrink()));
    await tester.pump();

    expect(_matching(httpClient, 'DELETE', '/realtime/framework-v6/provider-free/sessions/$_sessionId'), 1);
  });

  testWidgets('dispose before Open calls no factory and no FW-v6 request', (tester) async {
    final httpClient = _FakeFrameworkV600HttpClient();
    var factoryCalls = 0;
    await _pump(
      tester,
      factory: () {
        factoryCalls += 1;
        return _controller(httpClient);
      },
    );

    await tester.pumpWidget(const MaterialApp(home: SizedBox.shrink()));
    await tester.pump();

    expect(factoryCalls, 0);
    expect(httpClient.requests, isEmpty);
  });

  testWidgets('dispose after Open without explicit Close sends no hidden DELETE', (
    tester,
  ) async {
    final httpClient = _FakeFrameworkV600HttpClient()..queueJson(201, _open());
    await _pump(tester, factory: () => _controller(httpClient));
    _pressButton(tester, 'framework-v600-realtime-open-button');
    await tester.pumpAndSettle();

    await tester.pumpWidget(const MaterialApp(home: SizedBox.shrink()));
    await tester.pump();

    expect(_matching(httpClient, 'DELETE', '/realtime/framework-v6/provider-free/sessions/$_sessionId'), 0);
  });

  testWidgets('after explicit Close next explicit Open creates fresh controller', (
    tester,
  ) async {
    final firstHttpClient = _FakeFrameworkV600HttpClient()
      ..queueJson(201, _open())
      ..queueText(204, '');
    final secondHttpClient = _FakeFrameworkV600HttpClient()
      ..queueJson(201, _open());
    final clients = [firstHttpClient, secondHttpClient];
    var factoryCalls = 0;
    await _pump(
      tester,
      factory: () => _controller(clients[factoryCalls++]),
    );

    _pressButton(tester, 'framework-v600-realtime-open-button');
    await tester.pumpAndSettle();
    _pressButton(tester, 'framework-v600-realtime-close-button');
    await tester.pumpAndSettle();
    _pressButton(tester, 'framework-v600-realtime-open-button');
    await tester.pumpAndSettle();

    expect(factoryCalls, 2);
    expect(_matching(firstHttpClient, 'POST', '/realtime/framework-v6/provider-free/sessions'), 1);
    expect(_matching(secondHttpClient, 'POST', '/realtime/framework-v6/provider-free/sessions'), 1);
  });

  testWidgets('safe UI projection excludes raw exception JSON and private payload', (
    tester,
  ) async {
    final httpClient = _FakeFrameworkV600HttpClient()
      ..queueJson(201, _open())
      ..queueJson(200, _diagnostics())
      ..queueJson(200, _turn(safeMessage: 'safe turn message'))
      ..queueJson(200, _interrupt())
      ..queueJson(503, _problem('safe_problem'));
    await _pump(tester, factory: () => _controller(httpClient));
    _pressButton(tester, 'framework-v600-realtime-open-button');
    await tester.pumpAndSettle();
    _pressButton(tester, 'framework-v600-realtime-diagnostics-button');
    await tester.pumpAndSettle();
    await tester.enterText(find.byKey(const ValueKey('framework-v600-realtime-input')), 'safe input');
    await tester.pump();
    _pressButton(tester, 'framework-v600-realtime-send-button');
    await tester.pumpAndSettle();
    _pressButton(tester, 'framework-v600-realtime-interrupt-button');
    await tester.pumpAndSettle();
    await tester.enterText(find.byKey(const ValueKey('framework-v600-realtime-input')), 'safe input again');
    await tester.pump();
    _pressButton(tester, 'framework-v600-realtime-send-button');
    await tester.pumpAndSettle();

    expect(_textByKey(tester, 'framework-v600-realtime-turn-outcome'), 'turn outcome: completed');
    expect(_textByKey(tester, 'framework-v600-realtime-turn-safe-message'), 'turn safe message: safe turn message');
    expect(_textByKey(tester, 'framework-v600-realtime-interrupt-outcome'), 'interrupt outcome: accepted');
    expect(_textByKey(tester, 'framework-v600-realtime-diagnostics-state'), 'diagnostics state: ready');
    expect(_textByKey(tester, 'framework-v600-realtime-diagnostics-phase'), 'diagnostics phase: ready');
    expect(_textByKey(tester, 'framework-v600-realtime-problem-code'), 'problem code: safe_problem');
    expect(_textByKey(tester, 'framework-v600-realtime-problem-message'), 'problem message: safe problem message');
    expect(find.textContaining('RAW_PRIVATE_PROVIDER_PAYLOAD'), findsNothing);
    expect(find.textContaining('{'), findsNothing);
    expect(find.textContaining('StackTrace'), findsNothing);
  });
}

Future<void> _pump(
  WidgetTester tester, {
  FrameworkV600RealtimeSessionController Function()? factory,
}) async {
  await tester.pumpWidget(
    MaterialApp(
      home: HomeScreen(
        apiClient: const _FakeBackendApiClient(),
        frameworkV600RealtimeSessionControllerFactory: factory,
      ),
    ),
  );
  await tester.pumpAndSettle();
}

FrameworkV600RealtimeSessionController _controller(
  _FakeFrameworkV600HttpClient httpClient,
) {
  return FrameworkV600RealtimeSessionController(
    client: FrameworkV600RealtimeSessionClient(
      baseUrl: 'http://backend.test',
      client: httpClient,
    ),
  );
}

ButtonStyleButton _button(WidgetTester tester, String key) {
  return tester.widget<ButtonStyleButton>(find.byKey(ValueKey(key)));
}

void _pressButton(WidgetTester tester, String key) {
  final callback = _button(tester, key).onPressed;
  expect(callback, isNotNull);
  callback!();
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
    queueText(status, jsonEncode(body));
  }

  void queueText(int status, String body) {
    _responses.add(
      http.StreamedResponse(Stream<List<int>>.value(utf8.encode(body)), status),
    );
  }

  @override
  Future<http.StreamedResponse> send(http.BaseRequest request) async {
    requests.add(request);
    return _responses.removeAt(0);
  }
}

class _FakeBackendApiClient extends BackendApiClient {
  const _FakeBackendApiClient() : super(baseUrl: 'http://backend.test');

  @override
  Future<String> fetchHealthStatus() async => 'ok / API v2.1.0';

  @override
  Future<List<CharacterPreset>> fetchCharacters() async {
    return const <CharacterPreset>[
      CharacterPreset(
        characterId: 'default',
        displayName: 'Default',
        description: 'Default test character',
        personalityType: 'friendly',
        speakingStyle: 'casual',
        adviceStyle: 'light',
      ),
    ];
  }

  @override
  Future<SleepSummary> fetchSleepSummary() async {
    return const SleepSummary(
      date: '2026-07-30',
      totalSleepMinutes: 420,
      efficiency: 88,
      deepSleepMinutes: 80,
      remSleepMinutes: 90,
      awakeMinutes: 20,
      source: 'mock',
      available: true,
    );
  }

  @override
  Future<SleepProviderSelectionStatus>
  fetchSleepProviderSelectionStatus() async {
    return const SleepProviderSelectionStatus(
      configuredProvider: 'mock',
      configuredProviderLabel: 'Mock',
      configuredProviderRole: 'credential_free_default',
      configuredProviderSupported: true,
      selectionMode: 'backend_config',
      changeRequiresBackendRestart: true,
      availableProviders: <SleepProviderOption>[],
      message: 'Mock provider selected.',
    );
  }

  @override
  Future<DemoStatus> fetchDemoStatus() async {
    return const DemoStatus(
      engine: 'mock',
      mode: 'mock_safe',
      capabilities: <String, DemoCapabilityStatus>{},
    );
  }
}

const _sessionId = 'fw_session_0123456789abcdef0123456789abcdef';
const _turnId = 'fw_turn_0123456789abcdef0123456789abcdef';
const _generationId = 'fw_generation_0123456789abcdef0123456789abcdef';

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

Map<String, Object?> _turn({String safeMessage = ''}) => <String, Object?>{
  'schema_version': frameworkV600TurnSchema,
  'outcome': 'completed',
  'terminal': true,
  'session_id': _sessionId,
  'turn_id': _turnId,
  'generation_id': _generationId,
  'public_error_code': null,
  'safe_message': safeMessage,
  'retryable': false,
  'recovery_action': 'none',
  'events': const [],
  'capabilities': _capabilities(),
  'interrupt': null,
  'diagnostics': null,
  'raw_provider_payload': 'RAW_PRIVATE_PROVIDER_PAYLOAD',
};

Map<String, Object?> _interrupt() => <String, Object?>{
  'schema_version': frameworkV600InterruptSchema,
  'outcome': 'accepted',
  'scope': 'current_turn',
  'reason': 'host_app_request',
  'provider_cancel_supported': false,
  'provider_cancel_applied': false,
  'queue_flush_supported': true,
  'queue_flush_applied': true,
  'host_playback_stop_supported': false,
  'host_playback_stop_applied': false,
  'safe_message': 'safe interrupt',
  'retryable': false,
};

Map<String, Object?> _diagnostics() => <String, Object?>{
  'schema_version': frameworkV600DiagnosticsSchema,
  'session_id': _sessionId,
  'state': 'ready',
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

Map<String, Object?> _problem(String code) => <String, Object?>{
  'detail': <String, Object?>{
    'code': code,
    'message': 'safe problem message',
    'retryable': false,
  },
  'raw_provider_payload': 'RAW_PRIVATE_PROVIDER_PAYLOAD',
};
