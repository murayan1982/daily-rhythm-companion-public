import 'dart:async';

import 'package:app/models/character_preset.dart';
import 'package:app/models/demo_status.dart';
import 'package:app/models/realtime_text_stream.dart';
import 'package:app/models/sleep_provider_selection.dart';
import 'package:app/models/sleep_summary.dart';
import 'package:app/screens/home_screen.dart';
import 'package:app/services/backend_api_client.dart';
import 'package:app/services/realtime_terminal_voice_output_home_screen_binding.dart';
import 'package:app/services/realtime_terminal_voice_output_orchestrator.dart';
import 'package:app/services/realtime_text_stream_client.dart';
import 'package:app/services/realtime_text_stream_controller.dart';
import 'package:app/services/voice_output_audio_player.dart';
import 'package:app/services/voice_output_queue.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;

void main() {
  testWidgets('unconfigured binding keeps manual voice controls disabled', (
    tester,
  ) async {
    final controller = _FakeRealtimeTextStreamController();
    final engine = _FakeVoiceOutputAudioEngine();

    await _pumpHome(
      tester,
      controller: controller,
      engine: engine,
      includeBinding: false,
    );

    expect(
      find.byKey(const Key('realtime-terminal-voice-output-section')),
      findsOne,
    );
    expect(find.text('Configuration: unconfigured'), findsOne);
    expect(_switch(tester).value, false);
    expect(_switch(tester).onChanged, isNull);
    expect(_button(tester, _enqueueKey).enabled, false);
    expect(_button(tester, _processKey).enabled, false);
    expect(_button(tester, _flushKey).enabled, false);
  });

  testWidgets('binding factory runs once and opt-in defaults off', (
    tester,
  ) async {
    final controller = _FakeRealtimeTextStreamController();
    final fixture = _VoiceFixture();
    final engine = _FakeVoiceOutputAudioEngine();
    var factoryCalls = 0;

    await _pumpHome(
      tester,
      controller: controller,
      fixture: fixture,
      engine: engine,
      onBindingFactoryCalled: () {
        factoryCalls += 1;
      },
    );

    expect(factoryCalls, 1);
    expect(find.text('Configuration: configured'), findsOne);
    expect(find.text('Opt-in: off'), findsOne);
    expect(fixture.synthesisCalls, 0);
    expect(fixture.playbackCalls, 0);
    expect(fixture.localStopCalls, 0);
  });

  testWidgets('stream completion and opt-in alone do not start voice output', (
    tester,
  ) async {
    final controller = _FakeRealtimeTextStreamController();
    final fixture = _VoiceFixture();
    final engine = _FakeVoiceOutputAudioEngine();

    await _pumpHome(
      tester,
      controller: controller,
      fixture: fixture,
      engine: engine,
    );
    controller.complete(text: 'completed but not enqueued');
    await tester.pump();

    expect(find.text('RT-5 phase: idle'), findsOne);
    expect(find.text('Pending: 0'), findsOne);
    expect(fixture.synthesisCalls, 0);
    expect(fixture.playbackCalls, 0);
    expect(fixture.localStopCalls, 0);

    _switch(tester).onChanged!(true);
    await tester.pump();

    expect(find.text('Opt-in: on'), findsOne);
    expect(fixture.synthesisCalls, 0);
    expect(fixture.playbackCalls, 0);
    expect(fixture.localStopCalls, 0);
  });

  testWidgets('explicit enqueue does not automatically process', (
    tester,
  ) async {
    final controller = _FakeRealtimeTextStreamController();
    final fixture = _VoiceFixture();
    final engine = _FakeVoiceOutputAudioEngine();

    await _pumpHome(
      tester,
      controller: controller,
      fixture: fixture,
      engine: engine,
    );
    _enableOptIn(tester);
    controller.complete(text: 'manual queue item');
    await tester.pump();

    _pressButton(tester, _enqueueKey);
    await tester.pump();

    expect(find.text('Last enqueue: accepted'), findsOne);
    expect(find.text('Pending: 1'), findsOne);
    expect(fixture.synthesisCalls, 0);
    expect(fixture.playbackCalls, 0);
    expect(_button(tester, _processKey).enabled, true);
    expect(_switch(tester).onChanged, isNull);
  });

  testWidgets('duplicate completed terminal is visibly rejected', (
    tester,
  ) async {
    final controller = _FakeRealtimeTextStreamController();
    final fixture = _VoiceFixture();
    final engine = _FakeVoiceOutputAudioEngine();

    await _pumpHome(
      tester,
      controller: controller,
      fixture: fixture,
      engine: engine,
    );
    _enableOptIn(tester);
    controller.complete(text: 'deduplicated terminal');
    await tester.pump();

    _pressButton(tester, _enqueueKey);
    await tester.pump();
    _pressButton(tester, _enqueueKey);
    await tester.pump();

    expect(find.text('Last enqueue: duplicateCompletedTerminal'), findsOne);
    expect(find.text('Pending: 1'), findsOne);
    expect(fixture.synthesisCalls, 0);
  });

  testWidgets('one process click completes one fake queued item', (
    tester,
  ) async {
    final controller = _FakeRealtimeTextStreamController();
    final fixture = _VoiceFixture();
    final engine = _FakeVoiceOutputAudioEngine();

    await _pumpHome(
      tester,
      controller: controller,
      fixture: fixture,
      engine: engine,
    );
    _enableOptIn(tester);
    controller.complete(text: 'first spoken item');
    await tester.pump();
    _pressButton(tester, _enqueueKey);
    await tester.pump();

    _pressButton(tester, _processKey);
    await tester.pumpAndSettle();

    expect(fixture.synthesisCalls, 1);
    expect(fixture.playbackCalls, 1);
    expect(fixture.utterances, <String>['first spoken item']);
    expect(find.text('Last process: completed'), findsOne);
    expect(find.text('Pending: 0'), findsOne);
    expect(find.text('Active: no'), findsOne);
    expect(engine.loadCalls, 0);
    expect(engine.playCalls, 0);
    expect(engine.stopCalls, 0);
  });

  testWidgets('duplicate process tap is guarded synchronously', (tester) async {
    final synthesisCompleter =
        Completer<RealtimeTerminalVoiceSynthesisResult>();
    final controller = _FakeRealtimeTextStreamController();
    final fixture = _VoiceFixture(synthesisCompleter: synthesisCompleter);
    final engine = _FakeVoiceOutputAudioEngine();

    await _pumpHome(
      tester,
      controller: controller,
      fixture: fixture,
      engine: engine,
    );
    _enableOptIn(tester);
    controller.complete(text: 'single process invocation');
    await tester.pump();
    _pressButton(tester, _enqueueKey);
    await tester.pump();

    final callback = _button(tester, _processKey).onPressed!;
    callback();
    callback();
    await tester.pump();

    expect(fixture.synthesisCalls, 1);
    expect(fixture.playbackCalls, 0);

    synthesisCompleter.complete(
      const RealtimeTerminalVoiceSynthesisResult.audioReady(
        'https://audio.example.invalid/single.mp3',
      ),
    );
    await tester.pumpAndSettle();
    expect(fixture.playbackCalls, 1);
  });

  testWidgets('queued items remain manual one by one', (tester) async {
    final controller = _FakeRealtimeTextStreamController();
    final fixture = _VoiceFixture();
    final engine = _FakeVoiceOutputAudioEngine();

    await _pumpHome(
      tester,
      controller: controller,
      fixture: fixture,
      engine: engine,
    );
    _enableOptIn(tester);

    controller.complete(
      text: 'first',
      sessionId: 'session-one',
      turnId: 'turn-one',
      sequence: 1,
    );
    await tester.pump();
    _pressButton(tester, _enqueueKey);
    await tester.pump();

    controller.complete(
      text: 'second',
      sessionId: 'session-two',
      turnId: 'turn-two',
      sequence: 2,
    );
    await tester.pump();
    _pressButton(tester, _enqueueKey);
    await tester.pump();

    expect(find.text('Pending: 2'), findsOne);

    _pressButton(tester, _processKey);
    await tester.pumpAndSettle();

    expect(fixture.synthesisCalls, 1);
    expect(find.text('Pending: 1'), findsOne);

    _pressButton(tester, _processKey);
    await tester.pumpAndSettle();

    expect(fixture.synthesisCalls, 2);
    expect(fixture.utterances, <String>['first', 'second']);
    expect(find.text('Pending: 0'), findsOne);
  });

  testWidgets('manual flush clears pending and requests only local fake stop', (
    tester,
  ) async {
    final controller = _FakeRealtimeTextStreamController();
    final fixture = _VoiceFixture();
    final engine = _FakeVoiceOutputAudioEngine();

    await _pumpHome(
      tester,
      controller: controller,
      fixture: fixture,
      engine: engine,
    );
    _enableOptIn(tester);
    controller.complete(text: 'flush pending');
    await tester.pump();
    _pressButton(tester, _enqueueKey);
    await tester.pump();

    _pressButton(tester, _flushKey);
    await tester.pumpAndSettle();

    expect(fixture.localStopCalls, 1);
    expect(find.text('Last flush: completed'), findsOne);
    expect(find.text('Cleared pending: 1'), findsOne);
    expect(find.text('Local fake stop requested: true'), findsOne);
    expect(find.text('Local fake stop succeeded: true'), findsOne);
    expect(find.text('Pending: 0'), findsOne);
    expect(engine.stopCalls, 0);
  });

  testWidgets('duplicate flush tap shares one local fake stop', (tester) async {
    final stopCompleter = Completer<void>();
    final controller = _FakeRealtimeTextStreamController();
    final fixture = _VoiceFixture(localStopCompleter: stopCompleter);
    final engine = _FakeVoiceOutputAudioEngine();

    await _pumpHome(
      tester,
      controller: controller,
      fixture: fixture,
      engine: engine,
    );
    _enableOptIn(tester);
    controller.complete(text: 'single flush');
    await tester.pump();
    _pressButton(tester, _enqueueKey);
    await tester.pump();

    final callback = _button(tester, _flushKey).onPressed!;
    callback();
    callback();
    await tester.pump();

    expect(fixture.localStopCalls, 1);
    expect(find.text('RT-5 phase: flushing'), findsOne);

    stopCompleter.complete();
    await tester.pumpAndSettle();

    expect(fixture.localStopCalls, 1);
    expect(find.text('Last flush: completed'), findsOne);
  });

  testWidgets('flush during synthesis prevents late playback and stale UI', (
    tester,
  ) async {
    final synthesisCompleter =
        Completer<RealtimeTerminalVoiceSynthesisResult>();
    final controller = _FakeRealtimeTextStreamController();
    final fixture = _VoiceFixture(synthesisCompleter: synthesisCompleter);
    final engine = _FakeVoiceOutputAudioEngine();

    await _pumpHome(
      tester,
      controller: controller,
      fixture: fixture,
      engine: engine,
    );
    _enableOptIn(tester);
    controller.complete(text: 'late synthesis');
    await tester.pump();
    _pressButton(tester, _enqueueKey);
    await tester.pump();

    _pressButton(tester, _processKey);
    await tester.pump();
    expect(find.text('RT-5 phase: synthesizing'), findsOne);

    _pressButton(tester, _flushKey);
    await tester.pumpAndSettle();
    expect(fixture.localStopCalls, 1);
    expect(find.text('Last flush: completed'), findsOne);
    expect(find.text('RT-5 phase: idle'), findsOne);

    synthesisCompleter.complete(
      const RealtimeTerminalVoiceSynthesisResult.audioReady(
        'https://audio.example.invalid/late.mp3',
      ),
    );
    await tester.pump();
    await tester.pump();

    expect(fixture.playbackCalls, 0);
    expect(find.text('Last flush: completed'), findsOne);
    expect(find.text('Pending: 0'), findsOne);
  });

  testWidgets('flush during playback ignores late playback terminal', (
    tester,
  ) async {
    final playbackCompleter = Completer<RealtimeTerminalVoicePlaybackResult>();
    final controller = _FakeRealtimeTextStreamController();
    final fixture = _VoiceFixture(playbackCompleter: playbackCompleter);
    final engine = _FakeVoiceOutputAudioEngine();

    await _pumpHome(
      tester,
      controller: controller,
      fixture: fixture,
      engine: engine,
    );
    _enableOptIn(tester);
    controller.complete(text: 'late playback');
    await tester.pump();
    _pressButton(tester, _enqueueKey);
    await tester.pump();

    _pressButton(tester, _processKey);
    await tester.pump();
    await tester.pump();
    expect(find.text('RT-5 phase: playing'), findsOne);

    _pressButton(tester, _flushKey);
    await tester.pumpAndSettle();
    expect(fixture.localStopCalls, 1);
    expect(find.text('Active: no'), findsOne);

    playbackCompleter.complete(
      const RealtimeTerminalVoicePlaybackResult.completed(),
    );
    await tester.pump();
    await tester.pump();

    expect(find.text('Last flush: completed'), findsOne);
    expect(find.text('Active: no'), findsOne);
    expect(engine.stopCalls, 0);
  });

  testWidgets('flush releases UI for a new generation while old future waits', (
    tester,
  ) async {
    final oldSynthesis = Completer<RealtimeTerminalVoiceSynthesisResult>();
    final controller = _FakeRealtimeTextStreamController();
    final fixture = _VoiceFixture(synthesisCompleter: oldSynthesis);
    final engine = _FakeVoiceOutputAudioEngine();

    await _pumpHome(
      tester,
      controller: controller,
      fixture: fixture,
      engine: engine,
    );
    _enableOptIn(tester);
    controller.complete(
      text: 'old generation',
      sessionId: 'old-session',
      turnId: 'old-turn',
    );
    await tester.pump();
    _pressButton(tester, _enqueueKey);
    await tester.pump();
    _pressButton(tester, _processKey);
    await tester.pump();

    _pressButton(tester, _flushKey);
    await tester.pumpAndSettle();

    fixture.synthesisCompleter = null;
    controller.complete(
      text: 'new generation',
      sessionId: 'new-session',
      turnId: 'new-turn',
      sequence: 2,
    );
    await tester.pump();
    _pressButton(tester, _enqueueKey);
    await tester.pump();

    expect(_button(tester, _processKey).enabled, true);
    _pressButton(tester, _processKey);
    await tester.pumpAndSettle();

    expect(fixture.synthesisCalls, 2);
    expect(fixture.playbackCalls, 1);
    expect(fixture.utterances.last, 'new generation');
    expect(find.text('Last process: completed'), findsOne);

    oldSynthesis.complete(
      const RealtimeTerminalVoiceSynthesisResult.audioReady(
        'https://audio.example.invalid/old.mp3',
      ),
    );
    await tester.pump();
    expect(fixture.playbackCalls, 1);
    expect(find.text('Last process: completed'), findsOne);
  });

  testWidgets('binding disposal is exactly once and late work is inert', (
    tester,
  ) async {
    final synthesisCompleter =
        Completer<RealtimeTerminalVoiceSynthesisResult>();
    final controller = _FakeRealtimeTextStreamController();
    final fixture = _VoiceFixture(synthesisCompleter: synthesisCompleter);
    final engine = _FakeVoiceOutputAudioEngine();

    await _pumpHome(
      tester,
      controller: controller,
      fixture: fixture,
      engine: engine,
    );
    _enableOptIn(tester);
    controller.complete(text: 'dispose pending operation');
    await tester.pump();
    _pressButton(tester, _enqueueKey);
    await tester.pump();
    _pressButton(tester, _processKey);
    await tester.pump();

    await tester.pumpWidget(const MaterialApp(home: SizedBox.shrink()));
    await tester.pump();

    expect(fixture.disposeOwnedCalls, 1);
    expect(fixture.binding.isDisposed, true);
    expect(fixture.localStopCalls, 1);
    expect(controller.disposed, true);

    synthesisCompleter.complete(
      const RealtimeTerminalVoiceSynthesisResult.audioReady(
        'https://audio.example.invalid/disposed.mp3',
      ),
    );
    await tester.pump();
    await tester.pump();

    expect(fixture.playbackCalls, 0);

    fixture.binding.dispose();
    expect(fixture.disposeOwnedCalls, 1);
  });

  testWidgets('configuration failure is bounded and hides raw exception', (
    tester,
  ) async {
    final controller = _FakeRealtimeTextStreamController();
    final engine = _FakeVoiceOutputAudioEngine();

    await tester.pumpWidget(
      MaterialApp(
        home: HomeScreen(
          apiClient: const _FakeBackendApiClient(),
          voiceOutputAudioEngine: engine,
          realtimeTextStreamControllerFactory: () => controller,
          realtimeTerminalVoiceOutputBindingFactory: () {
            throw StateError('raw binding failure details');
          },
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Configuration: configuration_failed'), findsOne);
    expect(find.textContaining('raw binding failure details'), findsNothing);
    expect(_switch(tester).onChanged, isNull);
  });

  testWidgets('voice section never displays text IDs URI or raw errors', (
    tester,
  ) async {
    const secretText = 'terminal-private-content';
    const audioUri = 'https://audio.example.invalid/private-object.mp3';
    final controller = _FakeRealtimeTextStreamController();
    final fixture = _VoiceFixture(
      synthesisResult: const RealtimeTerminalVoiceSynthesisResult.audioReady(
        audioUri,
      ),
    );
    final engine = _FakeVoiceOutputAudioEngine();

    await _pumpHome(
      tester,
      controller: controller,
      fixture: fixture,
      engine: engine,
    );
    _enableOptIn(tester);
    controller.complete(
      text: secretText,
      sessionId: 'session-private-id',
      turnId: 'turn-private-id',
    );
    await tester.pump();
    _pressButton(tester, _enqueueKey);
    await tester.pump();
    _pressButton(tester, _processKey);
    await tester.pumpAndSettle();

    final section = find.byKey(
      const Key('realtime-terminal-voice-output-section'),
    );
    final visibleText = tester
        .widgetList<Text>(
          find.descendant(of: section, matching: find.byType(Text)),
        )
        .map((widget) => widget.data ?? '')
        .join('\n');

    expect(visibleText, isNot(contains(secretText)));
    expect(visibleText, isNot(contains('session-private-id')));
    expect(visibleText, isNot(contains('turn-private-id')));
    expect(visibleText, isNot(contains(audioUri)));
    expect(visibleText, isNot(contains('tts-')));
    expect(
      find.byKey(
        const Key('realtime-terminal-voice-output-player-separation-note'),
      ),
      findsOne,
    );
    expect(engine.loadCalls, 0);
    expect(engine.playCalls, 0);
    expect(engine.stopCalls, 0);
  });
}

const String _enqueueKey = 'realtime-terminal-voice-output-enqueue-button';
const String _processKey = 'realtime-terminal-voice-output-process-button';
const String _flushKey = 'realtime-terminal-voice-output-flush-button';

Future<void> _pumpHome(
  WidgetTester tester, {
  required _FakeRealtimeTextStreamController controller,
  required _FakeVoiceOutputAudioEngine engine,
  _VoiceFixture? fixture,
  bool includeBinding = true,
  VoidCallback? onBindingFactoryCalled,
}) async {
  await tester.pumpWidget(
    MaterialApp(
      home: HomeScreen(
        apiClient: const _FakeBackendApiClient(),
        voiceOutputAudioEngine: engine,
        realtimeTextStreamControllerFactory: () => controller,
        realtimeTerminalVoiceOutputBindingFactory: includeBinding
            ? () {
                onBindingFactoryCalled?.call();
                return fixture!.binding;
              }
            : null,
      ),
    ),
  );
  await tester.pumpAndSettle();
}

SwitchListTile _switch(WidgetTester tester) {
  return tester.widget<SwitchListTile>(
    find.byKey(const Key('realtime-terminal-voice-output-opt-in')),
  );
}

void _enableOptIn(WidgetTester tester) {
  final callback = _switch(tester).onChanged;
  expect(callback, isNotNull);
  callback!(true);
}

ButtonStyleButton _button(WidgetTester tester, String key) {
  return tester.widget<ButtonStyleButton>(find.byKey(Key(key)));
}

void _pressButton(WidgetTester tester, String key) {
  final callback = _button(tester, key).onPressed;
  expect(callback, isNotNull);
  callback!();
}

class _VoiceFixture {
  _VoiceFixture({
    RealtimeTerminalVoiceSynthesisResult synthesisResult =
        const RealtimeTerminalVoiceSynthesisResult.audioReady(
          'https://audio.example.invalid/fake.mp3',
        ),
    RealtimeTerminalVoicePlaybackResult playbackResult =
        const RealtimeTerminalVoicePlaybackResult.completed(),
    this.synthesisCompleter,
    this.playbackCompleter,
    this.localStopCompleter,
  }) : _synthesisResult = synthesisResult,
       _playbackResult = playbackResult {
    queue = VoiceOutputQueueController(
      stopLocalPlayback: () async {
        localStopCalls += 1;
        final completer = localStopCompleter;
        if (completer != null) {
          await completer.future;
        }
      },
    );
    orchestrator = RealtimeTerminalVoiceOutputOrchestrator(
      queue: queue,
      synthesize: (request) async {
        synthesisCalls += 1;
        utterances.add(request.utterance);
        final completer = synthesisCompleter;
        if (completer != null) {
          return completer.future;
        }
        return _synthesisResult;
      },
      playToTerminal: (source) async {
        playbackCalls += 1;
        playbackSources.add(source);
        final completer = playbackCompleter;
        if (completer != null) {
          return completer.future;
        }
        return _playbackResult;
      },
    );
    binding = OwnedRealtimeTerminalVoiceOutputHomeScreenBinding(
      orchestrator: orchestrator,
      disposeOwnedResources: () {
        disposeOwnedCalls += 1;
        queue.dispose();
      },
    );
  }

  final RealtimeTerminalVoiceSynthesisResult _synthesisResult;
  final RealtimeTerminalVoicePlaybackResult _playbackResult;

  Completer<RealtimeTerminalVoiceSynthesisResult>? synthesisCompleter;
  Completer<RealtimeTerminalVoicePlaybackResult>? playbackCompleter;
  Completer<void>? localStopCompleter;

  late final VoiceOutputQueueController queue;
  late final RealtimeTerminalVoiceOutputOrchestrator orchestrator;
  late final OwnedRealtimeTerminalVoiceOutputHomeScreenBinding binding;

  int synthesisCalls = 0;
  int playbackCalls = 0;
  int localStopCalls = 0;
  int disposeOwnedCalls = 0;
  final List<String> utterances = <String>[];
  final List<Uri> playbackSources = <Uri>[];
}

class _FakeRealtimeTextStreamController extends RealtimeTextStreamController {
  _FakeRealtimeTextStreamController()
    : super(
        client: RealtimeTextStreamClient(
          baseUrl: 'http://unused.invalid',
          client: _NoopHttpClient(),
        ),
      );

  RealtimeTextStreamControllerState _fakeState =
      const RealtimeTextStreamControllerState.idle();
  bool disposed = false;

  @override
  RealtimeTextStreamControllerState get state => _fakeState;

  void complete({
    required String text,
    String sessionId = 'session-one',
    String turnId = 'turn-one',
    int sequence = 1,
  }) {
    _fakeState = RealtimeTextStreamControllerState(
      phase: RealtimeTextStreamControllerPhase.completed,
      outputText: text,
      lastSequence: sequence,
      cancelMode: 'cooperative',
      hardCancelSupported: false,
      createResponse: RealtimeTextStreamCreateResponse(
        accepted: true,
        session: RealtimeTextStreamSession(
          sessionId: sessionId,
          state: RealtimeTextStreamState.streaming,
          activeTurnId: turnId,
          lastSequence: 0,
          isClosed: false,
          cancelMode: 'cooperative',
          hardCancelSupported: false,
        ),
        turn: RealtimeTextStreamTurn(
          sessionId: sessionId,
          turnId: turnId,
          state: RealtimeTextStreamState.streaming,
          chunkCount: 1,
          outputCharCount: text.runes.length,
          cancelRequested: false,
          terminalOutcome: null,
        ),
        eventsPath: '/realtime/text/sessions/$sessionId/events',
        cancelPath: '/realtime/text/sessions/$sessionId/cancel',
        idleTtlSeconds: 30,
        maxDurationSeconds: 120,
        maxPendingEvents: 64,
        maxEventBytes: 32768,
      ),
      terminal: RealtimeTextStreamTerminal(
        sequence: sequence,
        outcome: RealtimeTextStreamTerminalOutcome.completed,
        finalText: text,
        outputCharCount: text.runes.length,
        publicErrorCode: null,
        safeMessage: '',
        retryable: false,
      ),
    );
    notifyListeners();
  }

  @override
  Future<void> start({required String inputText}) async {}

  @override
  Future<void> cancel() async {}

  @override
  void dispose() {
    if (disposed) {
      return;
    }
    disposed = true;
    super.dispose();
  }
}

class _NoopHttpClient extends http.BaseClient {
  @override
  Future<http.StreamedResponse> send(http.BaseRequest request) async {
    return http.StreamedResponse(Stream<List<int>>.value(const <int>[]), 500);
  }
}

class _FakeVoiceOutputAudioEngine implements VoiceOutputAudioEngine {
  final StreamController<VoiceOutputAudioEngineEvent> _events =
      StreamController<VoiceOutputAudioEngineEvent>.broadcast();

  int loadCalls = 0;
  int playCalls = 0;
  int stopCalls = 0;
  int seekCalls = 0;
  int disposeCalls = 0;

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
  Future<void> stop() async {
    stopCalls += 1;
  }

  @override
  Future<void> seekToStart() async {
    seekCalls += 1;
  }

  @override
  Future<void> dispose() async {
    disposeCalls += 1;
    await _events.close();
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
      date: '2026-07-31',
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
