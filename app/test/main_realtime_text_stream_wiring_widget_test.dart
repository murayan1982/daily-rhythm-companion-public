import 'package:app/main.dart';
import 'package:app/models/character_preset.dart';
import 'package:app/models/demo_status.dart';
import 'package:app/models/sleep_provider_selection.dart';
import 'package:app/models/sleep_summary.dart';
import 'package:app/services/backend_api_client.dart';
import 'package:app/services/realtime_text_stream_client.dart';
import 'package:app/services/realtime_text_stream_controller.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;

void main() {
  testWidgets('default app constructor remains valid', (tester) async {
    const app = DailyRhythmCompanionApp();

    expect(app, isA<DailyRhythmCompanionApp>());
  });

  testWidgets('without factory realtime stream remains unconfigured', (
    tester,
  ) async {
    await tester.pumpWidget(
      const DailyRhythmCompanionApp(apiClient: _FakeBackendApiClient()),
    );
    await tester.pumpAndSettle();

    expect(find.byKey(const Key('realtime-text-stream-section')), findsOne);
    expect(
      find.byKey(const Key('realtime-text-stream-unconfigured')),
      findsOne,
    );
    expect(find.text('Phase: unconfigured'), findsOne);
    expect(_button(tester, 'realtime-text-stream-start-button').enabled, false);
  });

  testWidgets('configured factory is used once and renders ready stream UI', (
    tester,
  ) async {
    final httpClient = _FailingHttpClient();
    var factoryCalls = 0;
    await tester.pumpWidget(
      DailyRhythmCompanionApp(
        apiClient: const _FakeBackendApiClient(),
        realtimeTextStreamControllerFactory: () {
          factoryCalls += 1;
          return _controller(httpClient);
        },
      ),
    );
    await tester.pumpAndSettle();

    expect(factoryCalls, 1);
    expect(find.byKey(const Key('realtime-text-stream-input')), findsOne);
    expect(find.text('Phase: idle'), findsOne);
    expect(find.text('Hard cancel supported: false'), findsOne);
    expect(
      find.byKey(const Key('realtime-text-stream-unconfigured')),
      findsNothing,
    );
    expect(httpClient.sendCalls, 0);
  });

  testWidgets('configured stream leaves transcript handoff unconfigured', (
    tester,
  ) async {
    final httpClient = _FailingHttpClient();
    await tester.pumpWidget(
      DailyRhythmCompanionApp(
        apiClient: const _FakeBackendApiClient(),
        realtimeTextStreamControllerFactory: () => _controller(httpClient),
      ),
    );
    await tester.pumpAndSettle();

    expect(
      find.byKey(const Key('realtime-text-stream-transcript-handoff')),
      findsOne,
    );
    expect(
      find.byKey(const Key('realtime-text-stream-transcript-unconfigured')),
      findsOne,
    );
    expect(find.text('Transcript handoff: unconfigured'), findsOne);
    expect(_visibleTextContains(tester, 'result-'), false);
    expect(_visibleTextContains(tester, 'transcript'), true);
    expect(httpClient.sendCalls, 0);
  });

  testWidgets('widget dispose disposes controller and closes HTTP client', (
    tester,
  ) async {
    final httpClient = _FailingHttpClient();
    late final RealtimeTextStreamController controller;
    await tester.pumpWidget(
      DailyRhythmCompanionApp(
        apiClient: const _FakeBackendApiClient(),
        realtimeTextStreamControllerFactory: () {
          controller = _controller(httpClient);
          return controller;
        },
      ),
    );
    await tester.pumpAndSettle();

    await tester.pumpWidget(const MaterialApp(home: SizedBox.shrink()));
    await tester.pump();

    expect(httpClient.closeCalls, 1);
    expect(httpClient.sendCalls, 0);
  });
}

RealtimeTextStreamController _controller(http.Client httpClient) {
  return RealtimeTextStreamController(
    client: RealtimeTextStreamClient(
      baseUrl: 'https://backend.test',
      client: httpClient,
    ),
  );
}

ElevatedButton _button(WidgetTester tester, String key) {
  return tester.widget<ElevatedButton>(find.byKey(Key(key)));
}

bool _visibleTextContains(WidgetTester tester, String needle) {
  return tester
      .widgetList<Text>(find.byType(Text))
      .map((widget) => widget.data ?? widget.textSpan?.toPlainText() ?? '')
      .any((text) => text.contains(needle));
}

class _FailingHttpClient extends http.BaseClient {
  var sendCalls = 0;
  var closeCalls = 0;

  @override
  Future<http.StreamedResponse> send(http.BaseRequest request) async {
    sendCalls += 1;
    fail('Main wiring widget tests must not execute stream HTTP requests.');
  }

  @override
  void close() {
    closeCalls += 1;
    super.close();
  }
}

class _FakeBackendApiClient extends BackendApiClient {
  const _FakeBackendApiClient() : super(baseUrl: 'https://backend.test');

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
      capabilities: <String, DemoCapabilityStatus>{
        'llm_response': DemoCapabilityStatus(
          status: 'unavailable',
          source: 'mock',
          message: 'LLM unavailable.',
        ),
        'voice_input': DemoCapabilityStatus(
          status: 'unavailable',
          source: 'not_implemented',
          message: 'Voice input unavailable.',
        ),
        'voice_output': DemoCapabilityStatus(
          status: 'unavailable',
          source: 'not_implemented',
          message: 'Voice output unavailable.',
        ),
        'live2d_motion': DemoCapabilityStatus(
          status: 'unavailable',
          source: 'not_implemented',
          message: 'Motion unavailable.',
        ),
      },
    );
  }
}
