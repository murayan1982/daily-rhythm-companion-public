import 'dart:async';
import 'dart:convert';

import 'package:app/models/character_preset.dart';
import 'package:app/models/demo_status.dart';
import 'package:app/models/provider_neutral_transcript.dart';
import 'package:app/models/realtime_text_stream.dart';
import 'package:app/models/sleep_provider_selection.dart';
import 'package:app/models/sleep_summary.dart';
import 'package:app/models/voice_input_demo.dart';
import 'package:app/screens/home_screen.dart';
import 'package:app/services/backend_api_client.dart';
import 'package:app/services/realtime_text_stream_client.dart';
import 'package:app/services/realtime_text_stream_controller.dart';
import 'package:app/services/realtime_text_stream_transcript_handoff.dart';
import 'package:app/services/voice_output_audio_player.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;

void main() {
  testWidgets('default app shows transcript handoff unconfigured', (
    tester,
  ) async {
    await tester.pumpWidget(
      const MaterialApp(home: HomeScreen(apiClient: _FakeBackendApiClient())),
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
    expect(
      _button(tester, 'realtime-text-stream-transcript-start-button').enabled,
      false,
    );
  });

  testWidgets(
    'factory lifecycle passes owned controller and disposes handoff',
    (tester) async {
      final fakeHttp = _FakeRealtimeHttpClient();
      final providerCompleter = Completer<ProviderNeutralTranscriptResult>();
      RealtimeTextStreamController? ownedController;
      _SpyHandoff? spyHandoff;
      var handoffFactoryCalls = 0;

      await tester.pumpWidget(
        MaterialApp(
          home: HomeScreen(
            apiClient: const _FakeBackendApiClient(),
            realtimeTextStreamControllerFactory: () {
              ownedController = _controller(fakeHttp);
              return ownedController!;
            },
            realtimeTextStreamTranscriptHandoffFactory: (controller) {
              handoffFactoryCalls += 1;
              expect(identical(controller, ownedController), true);
              spyHandoff = _SpyHandoff(
                controller: controller,
                transcriptProvider: () => providerCompleter.future,
              );
              return spyHandoff!;
            },
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(handoffFactoryCalls, 1);
      _pressButton(tester, 'realtime-text-stream-transcript-start-button');
      await tester.pump();
      expect(find.text('Transcript handoff: acquiring'), findsOne);

      await tester.pumpWidget(const MaterialApp(home: SizedBox.shrink()));
      await tester.pump();
      expect(spyHandoff!.disposed, true);
      expect(fakeHttp.closed, true);
      providerCompleter.complete(_result('result-1', 'late injected text'));
      await tester.pump();
      expect(fakeHttp.createCalls, 0);
    },
  );

  testWidgets('successful handoff starts stream without transcript display', (
    tester,
  ) async {
    final fakeHttp = _FakeRealtimeHttpClient();
    final providerCompleter = Completer<ProviderNeutralTranscriptResult>();
    var providerCalls = 0;
    await _pumpConfigured(
      tester,
      fakeHttp,
      transcriptProvider: () {
        providerCalls += 1;
        return providerCompleter.future;
      },
    );

    _pressButton(tester, 'realtime-text-stream-transcript-start-button');
    await tester.pump();
    expect(find.text('Transcript handoff: acquiring'), findsOne);

    providerCompleter.complete(_result('result-1', 'injected final text'));
    await tester.pump();
    await tester.pump();
    await tester.pump();

    expect(providerCalls, 1);
    expect(fakeHttp.createCalls, 1);
    expect(find.text('Transcript handoff: accepted'), findsOne);
    expect(_visibleTextContains(tester, 'injected final text'), false);
    expect(_visibleTextContains(tester, 'result-1'), false);
    final editable = tester.widget<EditableText>(
      find.descendant(
        of: find.byKey(const Key('realtime-text-stream-input')),
        matching: find.byType(EditableText),
      ),
    );
    expect(editable.controller.text, '');

    fakeHttp.emitChunk(1, 'generated output', outputCharCount: 16);
    fakeHttp.emitTerminal(
      2,
      'stream_completed',
      'completed',
      finalText: 'generated output',
      outputCharCount: 16,
    );
    await tester.pump();

    expect(find.text('generated output'), findsOne);
    expect(_visibleTextContains(tester, 'injected final text'), false);
  });

  testWidgets('rapid duplicate tap cannot create duplicate handoff or start', (
    tester,
  ) async {
    final fakeHttp = _FakeRealtimeHttpClient();
    final providerCompleter = Completer<ProviderNeutralTranscriptResult>();
    var providerCalls = 0;
    await _pumpConfigured(
      tester,
      fakeHttp,
      transcriptProvider: () {
        providerCalls += 1;
        return providerCompleter.future;
      },
    );

    _pressButton(tester, 'realtime-text-stream-transcript-start-button');
    await tester.pump();
    expect(
      _button(tester, 'realtime-text-stream-transcript-start-button').enabled,
      false,
    );
    _button(
      tester,
      'realtime-text-stream-transcript-start-button',
    ).onPressed?.call();
    await tester.pump();
    expect(find.text('Transcript handoff: acquiring'), findsOne);
    expect(providerCalls, 1);
    expect(fakeHttp.createCalls, 0);

    providerCompleter.complete(_result('result-1', 'injected final text'));
    await tester.pump();
    await tester.pump();

    expect(providerCalls, 1);
    expect(fakeHttp.createCalls, 1);
  });

  testWidgets('invalid transcript is rejected without display or create', (
    tester,
  ) async {
    final fakeHttp = _FakeRealtimeHttpClient();
    await _pumpConfigured(
      tester,
      fakeHttp,
      transcriptProvider: () async => _result('result-1', '   '),
    );

    _pressButton(tester, 'realtime-text-stream-transcript-start-button');
    await tester.pump();
    await tester.pump();

    expect(fakeHttp.createCalls, 0);
    expect(find.text('Transcript handoff: rejected'), findsOne);
    expect(_visibleTextContains(tester, 'result-1'), false);
  });

  testWidgets('active stream disables transcript handoff and avoids provider', (
    tester,
  ) async {
    final fakeHttp = _FakeRealtimeHttpClient(holdCreate: true);
    var providerCalls = 0;
    await _pumpConfigured(
      tester,
      fakeHttp,
      transcriptProvider: () async {
        providerCalls += 1;
        return _result('result-1', 'unused injected text');
      },
    );

    await tester.enterText(
      find.byKey(const Key('realtime-text-stream-input')),
      'manual stream text',
    );
    _pressButton(tester, 'realtime-text-stream-start-button');
    await tester.pump();

    expect(
      _button(tester, 'realtime-text-stream-transcript-start-button').enabled,
      false,
    );
    _button(
      tester,
      'realtime-text-stream-transcript-start-button',
    ).onPressed?.call();
    await tester.pump();

    expect(providerCalls, 0);
    expect(fakeHttp.createCalls, 1);
  });

  testWidgets('safe failure is bounded and omits raw details', (tester) async {
    final fakeHttp = _FakeRealtimeHttpClient();
    await tester.pumpWidget(
      MaterialApp(
        home: HomeScreen(
          apiClient: const _FakeBackendApiClient(),
          realtimeTextStreamControllerFactory: () =>
              _FailingRealtimeTextStreamController(fakeHttp),
          realtimeTextStreamTranscriptHandoffFactory: (controller) =>
              RealtimeTextStreamTranscriptHandoff(
                controller: controller,
                transcriptProvider: () async =>
                    _result('result-1', 'injected final text'),
              ),
        ),
      ),
    );
    await tester.pumpAndSettle();

    _pressButton(tester, 'realtime-text-stream-transcript-start-button');
    await tester.pump();
    await tester.pump();

    final error = tester.widget<Text>(
      find.byKey(const Key('realtime-text-stream-transcript-error')),
    );
    expect(error.data!.runes.length, realtimeTextStreamMaxProblemMessageChars);
    expect(error.data, startsWith('safe safe'));
    expect(_visibleTextContains(tester, 'create_failed'), false);
    expect(_visibleTextContains(tester, 'result-1'), false);
    expect(_visibleTextContains(tester, 'injected final text'), false);
    expect(_visibleTextContains(tester, '/realtime/text'), false);
    expect(_visibleTextContains(tester, 'raw response body'), false);
  });

  testWidgets('VoiceInputDemo transcript does not trigger stream handoff', (
    tester,
  ) async {
    final fakeHttp = _FakeRealtimeHttpClient();
    var providerCalls = 0;
    await _pumpConfigured(
      tester,
      fakeHttp,
      apiClient: const _FakeBackendApiClient(
        voiceInputTranscript: 'demo response text',
      ),
      transcriptProvider: () async {
        providerCalls += 1;
        return _result('result-1', 'injected final text');
      },
    );

    await tester.ensureVisible(find.byIcon(Icons.mic_none));
    await tester.tap(find.byIcon(Icons.mic_none));
    await tester.pump();
    await tester.pump();

    expect(providerCalls, 0);
    expect(fakeHttp.createCalls, 0);
    expect(find.textContaining('demo response text'), findsWidgets);
  });

  testWidgets('completed stream from transcript does not start TTS playback', (
    tester,
  ) async {
    final fakeHttp = _FakeRealtimeHttpClient();
    final engine = _FakeVoiceOutputAudioEngine();
    await _pumpConfigured(
      tester,
      fakeHttp,
      voiceOutputAudioEngine: engine,
      transcriptProvider: () async =>
          _result('result-1', 'injected final text'),
    );

    _pressButton(tester, 'realtime-text-stream-transcript-start-button');
    await tester.pump();
    await tester.pump();
    fakeHttp.emitTerminal(1, 'stream_completed', 'completed');
    await tester.pump();

    expect(find.text('Phase: completed'), findsOne);
    expect(engine.loadCalls, 0);
    expect(engine.playCalls, 0);
  });
}

Future<void> _pumpConfigured(
  WidgetTester tester,
  _FakeRealtimeHttpClient fakeHttp, {
  BackendApiClient apiClient = const _FakeBackendApiClient(),
  VoiceOutputAudioEngine? voiceOutputAudioEngine,
  required ProviderNeutralTranscriptProvider transcriptProvider,
}) async {
  await tester.pumpWidget(
    MaterialApp(
      home: HomeScreen(
        apiClient: apiClient,
        voiceOutputAudioEngine: voiceOutputAudioEngine,
        realtimeTextStreamControllerFactory: () => _controller(fakeHttp),
        realtimeTextStreamTranscriptHandoffFactory: (controller) =>
            RealtimeTextStreamTranscriptHandoff(
              controller: controller,
              transcriptProvider: transcriptProvider,
            ),
      ),
    ),
  );
  await tester.pumpAndSettle();
}

RealtimeTextStreamController _controller(_FakeRealtimeHttpClient fakeHttp) {
  return RealtimeTextStreamController(
    client: RealtimeTextStreamClient(
      baseUrl: 'http://backend.test',
      client: fakeHttp,
    ),
  );
}

ProviderNeutralTranscriptResult _result(String resultId, String text) {
  return ProviderNeutralTranscriptResult(
    resultId: resultId,
    text: text,
    isFinal: true,
  );
}

ButtonStyleButton _button(WidgetTester tester, String key) {
  return tester.widget<ButtonStyleButton>(find.byKey(Key(key)));
}

void _pressButton(WidgetTester tester, String key) {
  final callback = _button(tester, key).onPressed;
  expect(callback, isNotNull);
  callback!();
}

bool _visibleTextContains(WidgetTester tester, String value) {
  return tester
      .widgetList<Text>(find.byType(Text))
      .any((widget) => (widget.data ?? '').contains(value));
}

class _SpyHandoff extends RealtimeTextStreamTranscriptHandoff {
  _SpyHandoff({required super.controller, required super.transcriptProvider});

  var disposed = false;

  @override
  void dispose() {
    disposed = true;
    super.dispose();
  }
}

class _FailingRealtimeTextStreamController
    extends RealtimeTextStreamController {
  _FailingRealtimeTextStreamController(_FakeRealtimeHttpClient fakeHttp)
    : super(
        client: RealtimeTextStreamClient(
          baseUrl: 'http://backend.test',
          client: fakeHttp,
        ),
      );

  RealtimeTextStreamControllerState _fakeState =
      const RealtimeTextStreamControllerState.idle();

  @override
  RealtimeTextStreamControllerState get state => _fakeState;

  @override
  Future<void> start({required String inputText}) async {
    _fakeState = RealtimeTextStreamControllerState(
      phase: RealtimeTextStreamControllerPhase.failed,
      outputText: '',
      lastSequence: 0,
      cancelMode: 'cooperative',
      hardCancelSupported: false,
      problem: RealtimeTextStreamProblem(
        code: 'fake_failed',
        message: 'safe  safe  ${List<String>.filled(300, 'x').join()}',
        retryable: true,
      ),
    );
    notifyListeners();
  }
}

class _FakeRealtimeHttpClient extends http.BaseClient {
  _FakeRealtimeHttpClient({this.holdCreate = false});

  final bool holdCreate;
  final Completer<void> _createCompleter = Completer<void>();
  StreamController<List<int>>? _events;
  var createCalls = 0;
  var closed = false;

  @override
  Future<http.StreamedResponse> send(http.BaseRequest request) async {
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
    return _jsonResponse(404, <String, Object?>{
      'code': 'unexpected_request',
      'message': 'Unexpected fake request.',
      'retryable': false,
    });
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
}) {
  final isChunk = chunkText != null;
  final state = switch (eventType) {
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
            'public_error_code': null,
            'safe_message': '',
            'retryable': false,
          },
    'safe_message': '',
  };
}

String _sseFrame(int id, String eventName, Map<String, Object?> payload) {
  return 'id: $id\n'
      'event: $eventName\n'
      'data: ${jsonEncode(payload)}\n\n';
}

class _FakeBackendApiClient extends BackendApiClient {
  const _FakeBackendApiClient({this.voiceInputTranscript})
    : super(baseUrl: 'http://backend.test');

  final String? voiceInputTranscript;

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
  Future<VoiceInputDemoRequestResponse> submitVoiceInputDemoRequest({
    required String clientEventId,
    String inputMode = 'demo_button',
    String? textHint,
  }) async {
    return VoiceInputDemoRequestResponse(
      accepted: false,
      requestState: 'not_started',
      engine: 'mock',
      mode: 'mock_safe',
      adapterMode: 'not_configured',
      inputMode: 'metadata_only',
      capability: const DemoCapabilityStatus(
        status: 'unavailable',
        source: 'not_implemented',
        message: 'Voice input unavailable.',
      ),
      transcript: voiceInputTranscript,
      message: 'Voice input demo is metadata only.',
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
