import 'dart:async';
import 'dart:convert';

import 'package:app/models/character_preset.dart';
import 'package:app/models/demo_status.dart';
import 'package:app/models/realtime_text_stream.dart';
import 'package:app/models/sleep_provider_selection.dart';
import 'package:app/models/sleep_summary.dart';
import 'package:app/screens/home_screen.dart';
import 'package:app/services/backend_api_client.dart';
import 'package:app/services/realtime_text_stream_client.dart';
import 'package:app/services/realtime_text_stream_controller.dart';
import 'package:app/services/voice_output_audio_player.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;

void main() {
  testWidgets('no factory shows unconfigured stream section', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(home: HomeScreen(apiClient: _FakeBackendApiClient())),
    );
    await tester.pumpAndSettle();

    expect(find.byKey(const Key('realtime-text-stream-section')), findsOne);
    expect(
      find.byKey(const Key('realtime-text-stream-unconfigured')),
      findsOne,
    );
    expect(find.text('Phase: unconfigured'), findsOne);
    expect(_button(tester, 'realtime-text-stream-start-button').enabled, false);
    expect(
      _button(tester, 'realtime-text-stream-cancel-button').enabled,
      false,
    );
  });

  testWidgets('factory owns controller listener and disposal', (tester) async {
    final httpClient = _FakeRealtimeHttpClient();
    var factoryCalls = 0;

    await tester.pumpWidget(
      MaterialApp(
        home: HomeScreen(
          apiClient: const _FakeBackendApiClient(),
          realtimeTextStreamControllerFactory: () {
            factoryCalls += 1;
            return RealtimeTextStreamController(
              client: RealtimeTextStreamClient(
                baseUrl: 'http://backend.test',
                client: httpClient,
              ),
            );
          },
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(factoryCalls, 1);
    await _enterInputAndStart(tester, 'hello');
    httpClient.emitStarted(1);
    await tester.pump();
    expect(find.text('Phase: streaming'), findsOne);

    await tester.pumpWidget(const MaterialApp(home: SizedBox.shrink()));
    await tester.pump();
    expect(httpClient.closed, true);
    httpClient.emitChunk(2, 'late');
    await tester.pump();
  });

  testWidgets('bounded manual input rejects invalid text', (tester) async {
    final httpClient = _FakeRealtimeHttpClient();
    await _pumpConfigured(tester, httpClient);

    await _enterInputAndStart(tester, '   ');
    expect(find.byKey(const Key('realtime-text-stream-error')), findsOne);
    expect(httpClient.createCalls, 0);

    await _enterInputAndStart(tester, List<String>.filled(4097, 'x').join());
    expect(
      find.text('The text stream input must be 4096 characters or fewer.'),
      findsOne,
    );
    expect(httpClient.createCalls, 0);
  });

  testWidgets('start shows incremental completion without input echo', (
    tester,
  ) async {
    final httpClient = _FakeRealtimeHttpClient();
    await _pumpConfigured(tester, httpClient);

    await _enterInputAndStart(tester, 'private manual input');
    expect(httpClient.createCalls, 1);
    expect(find.text('Phase: streaming'), findsOne);

    httpClient.emitStarted(1);
    httpClient.emitChunk(2, 'hello ');
    await tester.pump();
    expect(find.text('hello '), findsOne);

    httpClient.emitChunk(3, 'world', outputCharCount: 11);
    await tester.pump();
    expect(find.text('hello world'), findsOne);

    httpClient.emitTerminal(
      4,
      'stream_completed',
      'completed',
      finalText: 'hello world',
      outputCharCount: 11,
    );
    await tester.pump();
    expect(find.text('Phase: completed'), findsOne);
    expect(find.text('hello world'), findsOne);

    final inputFinder = find.byKey(const Key('realtime-text-stream-input'));
    final editableFinder = find.descendant(
      of: inputFinder,
      matching: find.byType(EditableText),
    );

    final editable = tester.widget<EditableText>(editableFinder);
    expect(editable.controller.text, 'private manual input');

    final visibleTextWidgets = tester.widgetList<Text>(find.byType(Text));
    expect(
      visibleTextWidgets.any(
        (widget) => (widget.data ?? '').contains('private manual input'),
      ),
      false,
    );

    final output = tester.widget<Text>(
      find.byKey(const Key('realtime-text-stream-output')),
    );
    expect(output.data, 'hello world');
  });

  testWidgets('duplicate start is prevented while active', (tester) async {
    final httpClient = _FakeRealtimeHttpClient(holdCreate: true);
    await _pumpConfigured(tester, httpClient);

    await _enterInputAndStart(tester, 'first input');
    expect(_button(tester, 'realtime-text-stream-start-button').enabled, false);
    await tester.pump();

    expect(httpClient.createCalls, 1);
    httpClient.completeCreate();
    await tester.pump();
  });

  testWidgets('cooperative cancellation is visible and idempotent', (
    tester,
  ) async {
    final httpClient = _FakeRealtimeHttpClient(holdCreate: true);
    await _pumpConfigured(tester, httpClient);

    await tester.enterText(
      find.byKey(const Key('realtime-text-stream-input')),
      'cancel input',
    );
    await tester.ensureVisible(
      find.byKey(const Key('realtime-text-stream-start-button')),
    );
    await tester.pump();
    _pressButton(tester, 'realtime-text-stream-start-button');
    await tester.pump();
    await tester.pump();
    await tester.pump();
    expect(
      _button(tester, 'realtime-text-stream-cancel-button').enabled,
      false,
    );
    httpClient.completeCreate();
    await tester.pump();
    await tester.pump();
    expect(_button(tester, 'realtime-text-stream-cancel-button').enabled, true);

    await tester.ensureVisible(
      find.byKey(const Key('realtime-text-stream-cancel-button')),
    );
    await tester.pump();
    _pressButton(tester, 'realtime-text-stream-cancel-button');
    await tester.pump();
    expect(httpClient.cancelCalls, 1);
    expect(find.text('Phase: cancel_requested'), findsOne);
    expect(find.text('Hard cancel supported: false'), findsOne);

    await tester.ensureVisible(
      find.byKey(const Key('realtime-text-stream-cancel-button')),
    );
    await tester.pump();
    _button(tester, 'realtime-text-stream-cancel-button').onPressed?.call();
    await tester.pump();
    expect(httpClient.cancelCalls, 1);

    httpClient.emitTerminal(1, 'stream_cancelled', 'cancelled');
    await tester.pump();
    expect(find.text('Phase: cancelled'), findsOne);
  });

  testWidgets('safe failure exposes bounded message only', (tester) async {
    final httpClient = _FakeRealtimeHttpClient();
    await _pumpConfigured(tester, httpClient);
    final longSafeMessage =
        'safe  safe  ${List<String>.filled(300, 'x').join()}';

    await _enterInputAndStart(tester, 'failure input');
    httpClient.emitTerminal(
      1,
      'stream_failed',
      'failed',
      publicErrorCode: 'stream_failed',
      safeMessage: longSafeMessage,
      responseBody: 'raw response body',
    );
    await tester.pump();

    expect(find.text('Phase: failed'), findsOne);
    final displayedError = tester.widget<Text>(
      find.byKey(const Key('realtime-text-stream-error')),
    );
    expect(
      displayedError.data!.runes.length,
      realtimeTextStreamMaxProblemMessageChars,
    );
    expect(displayedError.data, startsWith('safe safe'));
    expect(find.textContaining('raw response body'), findsNothing);
    expect(find.textContaining('session-1'), findsNothing);
    expect(find.textContaining('turn-1'), findsNothing);
    expect(find.textContaining('/realtime/text'), findsNothing);
  });

  testWidgets('closed terminal retains output and allows restart', (
    tester,
  ) async {
    final httpClient = _FakeRealtimeHttpClient();
    await _pumpConfigured(tester, httpClient);

    await _enterInputAndStart(tester, 'closed input');
    httpClient.emitChunk(1, 'partial');
    httpClient.emitTerminal(
      2,
      'stream_closed',
      'closed',
      finalText: 'partial',
      outputCharCount: 7,
    );
    await tester.pump();

    expect(find.text('Phase: closed'), findsOne);
    expect(find.text('partial'), findsOne);
    expect(_button(tester, 'realtime-text-stream-start-button').enabled, true);
  });

  testWidgets('stream completion does not start voice output', (tester) async {
    final httpClient = _FakeRealtimeHttpClient();
    final engine = _FakeVoiceOutputAudioEngine();
    await _pumpConfigured(tester, httpClient, voiceOutputAudioEngine: engine);

    await _enterInputAndStart(tester, 'no tts input');
    httpClient.emitTerminal(1, 'stream_completed', 'completed');
    await tester.pump();

    expect(find.text('Phase: completed'), findsOne);
    expect(engine.loadCalls, 0);
    expect(engine.playCalls, 0);
  });
}

Future<void> _pumpConfigured(
  WidgetTester tester,
  _FakeRealtimeHttpClient httpClient, {
  VoiceOutputAudioEngine? voiceOutputAudioEngine,
}) async {
  await tester.pumpWidget(
    MaterialApp(
      home: HomeScreen(
        apiClient: const _FakeBackendApiClient(),
        voiceOutputAudioEngine: voiceOutputAudioEngine,
        realtimeTextStreamControllerFactory: () => RealtimeTextStreamController(
          client: RealtimeTextStreamClient(
            baseUrl: 'http://backend.test',
            client: httpClient,
          ),
        ),
      ),
    ),
  );
  await tester.pumpAndSettle();
}

Future<void> _enterInputAndStart(WidgetTester tester, String input) async {
  await tester.ensureVisible(
    find.byKey(const Key('realtime-text-stream-input')),
  );
  await tester.pump();
  await tester.enterText(
    find.byKey(const Key('realtime-text-stream-input')),
    input,
  );
  await tester.ensureVisible(
    find.byKey(const Key('realtime-text-stream-start-button')),
  );
  await tester.pump();
  _pressButton(tester, 'realtime-text-stream-start-button');
  await tester.pump();
  await tester.pump();
  await tester.pump();
}

ButtonStyleButton _button(WidgetTester tester, String key) {
  return tester.widget<ButtonStyleButton>(find.byKey(Key(key)));
}

void _pressButton(WidgetTester tester, String key) {
  final callback = _button(tester, key).onPressed;
  expect(callback, isNotNull);
  callback!();
}

class _FakeRealtimeHttpClient extends http.BaseClient {
  _FakeRealtimeHttpClient({this.holdCreate = false});

  final bool holdCreate;
  final List<http.BaseRequest> requests = <http.BaseRequest>[];
  final Completer<void> _createCompleter = Completer<void>();
  StreamController<List<int>>? _events;
  var createCalls = 0;
  var cancelCalls = 0;
  var closed = false;

  @override
  Future<http.StreamedResponse> send(http.BaseRequest request) async {
    requests.add(request);
    if (request.method == 'POST' &&
        request.url.path == '/realtime/text/sessions') {
      createCalls += 1;
      if (holdCreate) {
        await _createCompleter.future;
      }
      return _jsonResponse(201, _createResponse());
    }
    if (request.method == 'GET' &&
        request.url.path == '/realtime/text/sessions/session-1/events') {
      _events = StreamController<List<int>>();
      return http.StreamedResponse(_events!.stream, 200);
    }
    if (request.method == 'POST' &&
        request.url.path == '/realtime/text/sessions/session-1/cancel') {
      cancelCalls += 1;
      return _jsonResponse(200, <String, Object?>{
        'accepted': true,
        'session_id': 'session-1',
        'turn_id': 'turn-1',
        'state': 'cancel_requested',
        'cancel_mode': 'cooperative',
        'hard_cancel_supported': false,
        'terminal': false,
        'safe_message': 'Cooperative cancel requested.',
      });
    }
    return _jsonResponse(404, <String, Object?>{
      'code': 'unexpected_request',
      'message': 'Unexpected fake request.',
      'retryable': false,
    });
  }

  void completeCreate() {
    if (!_createCompleter.isCompleted) {
      _createCompleter.complete();
    }
  }

  void emitStarted(int sequence) {
    _emit(sequence, 'stream_started', _event(sequence, 'stream_started'));
  }

  void emitChunk(int sequence, String text, {int? outputCharCount}) {
    _emit(
      sequence,
      'stream_chunk',
      _event(
        sequence,
        'stream_chunk',
        chunkText: text,
        outputCharCount: outputCharCount ?? text.runes.length,
      ),
    );
  }

  void emitTerminal(
    int sequence,
    String eventType,
    String outcome, {
    String finalText = '',
    int outputCharCount = 0,
    String safeMessage = '',
    String? publicErrorCode,
    String? responseBody,
  }) {
    _emit(
      sequence,
      eventType,
      _event(
        sequence,
        eventType,
        terminalOutcome: outcome,
        finalText: finalText,
        outputCharCount: outputCharCount,
        safeMessage: safeMessage,
        publicErrorCode: publicErrorCode,
        responseBody: responseBody,
      ),
    );
  }

  void _emit(int id, String eventName, Map<String, Object?> payload) {
    final controller = _events;
    if (controller == null || controller.isClosed) {
      return;
    }
    controller.add(utf8.encode(_sseFrame(id, eventName, payload)));
  }

  @override
  void close() {
    closed = true;
    _events?.close();
    super.close();
  }
}

http.StreamedResponse _jsonResponse(int status, Map<String, Object?> body) {
  return http.StreamedResponse(
    Stream<List<int>>.value(utf8.encode(jsonEncode(body))),
    status,
    headers: const {'content-type': 'application/json'},
  );
}

Map<String, Object?> _createResponse() {
  return <String, Object?>{
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
  };
}

Map<String, Object?> _event(
  int sequence,
  String eventType, {
  String? chunkText,
  int outputCharCount = 0,
  String? terminalOutcome,
  String finalText = '',
  String safeMessage = '',
  String? publicErrorCode,
  String? responseBody,
}) {
  final isChunk = chunkText != null;
  final state = switch (eventType) {
    'cancel_requested' => 'cancel_requested',
    'stream_completed' => 'completed',
    'stream_cancelled' => 'cancelled',
    'stream_failed' => 'failed',
    'stream_closed' => 'closed',
    _ => 'streaming',
  };
  return <String, Object?>{
    'event_type': eventType,
    'session_id': 'session-1',
    'turn_id': 'turn-1',
    'sequence': sequence,
    'state': state,
    'chunk': isChunk
        ? <String, Object?>{
            'sequence': sequence,
            'text': chunkText,
            'output_char_count': outputCharCount,
          }
        : null,
    'terminal': terminalOutcome == null
        ? null
        : <String, Object?>{
            'sequence': sequence,
            'outcome': terminalOutcome,
            'final_text': finalText,
            'output_char_count': outputCharCount,
            'public_error_code': publicErrorCode,
            'safe_message': safeMessage,
            'retryable': terminalOutcome == 'failed',
            'response_body': responseBody,
          },
    'safe_message': safeMessage,
  };
}

String _sseFrame(int id, String eventName, Map<String, Object?> payload) {
  return 'id: $id\n'
      'event: $eventName\n'
      'data: ${jsonEncode(payload)}\n\n';
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

class _FakeVoiceOutputAudioEngine implements VoiceOutputAudioEngine {
  final StreamController<VoiceOutputAudioEngineEvent> _events =
      StreamController<VoiceOutputAudioEngineEvent>.broadcast();
  var loadCalls = 0;
  var playCalls = 0;

  @override
  Stream<VoiceOutputAudioEngineEvent> get events => _events.stream;

  @override
  Future<void> load(Uri source) async {
    loadCalls += 1;
  }

  @override
  Future<void> play() async {
    playCalls += 1;
  }

  @override
  Future<void> stop() async {}

  @override
  Future<void> seekToStart() async {}

  @override
  Future<void> dispose() async {
    await _events.close();
  }
}
