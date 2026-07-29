import 'dart:async';

import 'package:app/models/realtime_text_stream.dart';
import 'package:app/services/realtime_text_stream_client.dart';
import 'package:app/services/realtime_text_stream_controller.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;

void main() {
  group('RealtimeTextStreamController', () {
    test('starts, appends chunks, and completes from terminal event', () async {
      final client = _FakeRealtimeTextStreamClient();
      final controller = RealtimeTextStreamController(client: client);
      final phases = <RealtimeTextStreamControllerPhase>[];
      controller.addListener(() => phases.add(controller.state.phase));

      await controller.start(inputText: 'private input');
      client.emit(_chunk(1, 'hello '));
      client.emit(_chunk(2, 'world', outputCharCount: 11));
      client.emit(
        _terminal(
          3,
          RealtimeTextStreamTerminalOutcome.completed,
          finalText: 'hello world',
        ),
      );
      await Future<void>.delayed(Duration.zero);

      expect(phases, contains(RealtimeTextStreamControllerPhase.connecting));
      expect(phases, contains(RealtimeTextStreamControllerPhase.streaming));
      expect(
        controller.state.phase,
        RealtimeTextStreamControllerPhase.completed,
      );
      expect(controller.state.outputText, 'hello world');
      expect(controller.state.lastSequence, 3);
      expect(controller.state.hardCancelSupported, isFalse);
      expect(controller.state.toString(), isNot(contains('private input')));

      controller.dispose();
    });

    test('rejects active stream replacement', () async {
      final client = _FakeRealtimeTextStreamClient();
      final controller = RealtimeTextStreamController(client: client);

      await controller.start(inputText: 'first');

      await expectLater(
        controller.start(inputText: 'second'),
        throwsA(
          isA<RealtimeTextStreamProblemException>().having(
            (error) => error.problem.code,
            'code',
            'active_stream_replacement_rejected',
          ),
        ),
      );

      controller.dispose();
    });

    test('rejects concurrent start before first create completes', () async {
      const privateInput = 'private concurrent input';
      final client = _FakeRealtimeTextStreamClient();
      final controller = RealtimeTextStreamController(client: client);

      final firstStart = controller.start(inputText: privateInput);

      await expectLater(
        controller.start(inputText: 'second input'),
        throwsA(
          isA<RealtimeTextStreamProblemException>().having(
            (error) => error.problem.code,
            'code',
            'active_stream_replacement_rejected',
          ),
        ),
      );
      await firstStart;

      expect(client.createCalls, 1);
      expect(controller.state.isActive, isTrue);
      expect(controller.state.toString(), isNot(contains(privateInput)));
      expect(controller.state.problem?.message, isNot(contains(privateInput)));

      controller.dispose();
    });

    test('requests cooperative cancel and remains idempotent', () async {
      final client = _FakeRealtimeTextStreamClient();
      final controller = RealtimeTextStreamController(client: client);

      await controller.start(inputText: 'cancel me');
      await controller.cancel();
      await controller.cancel();
      client.emit(_terminal(1, RealtimeTextStreamTerminalOutcome.cancelled));
      await Future<void>.delayed(Duration.zero);

      expect(client.cancelCalls, 1);
      expect(
        controller.state.phase,
        RealtimeTextStreamControllerPhase.cancelled,
      );
      expect(controller.state.cancelMode, 'cooperative');
      expect(controller.state.hardCancelSupported, isFalse);
      expect(client.streamCancelCalls, 1);

      controller.dispose();
    });

    test('cancel HTTP failure releases subscription safely', () async {
      final client = _FakeRealtimeTextStreamClient(
        cancelError: const RealtimeTextStreamProblemException(
          RealtimeTextStreamProblem(
            code: 'cancel_failed',
            message: 'safe cancel failure',
            retryable: true,
          ),
        ),
      );
      final controller = RealtimeTextStreamController(client: client);

      await controller.start(inputText: 'input');
      await controller.cancel();
      await controller.cancel();
      await Future<void>.delayed(Duration.zero);

      expect(client.cancelCalls, 1);
      expect(client.streamCancelCalls, 1);
      expect(controller.state.phase, RealtimeTextStreamControllerPhase.failed);
      expect(controller.state.problem!.code, 'cancel_failed');

      controller.dispose();
      controller.dispose();
      expect(client.closeCalls, 1);
    });

    test('keeps local cancelRequested after delayed streamStarted', () async {
      final client = _FakeRealtimeTextStreamClient();
      final controller = RealtimeTextStreamController(client: client);

      await controller.start(inputText: 'cancel before start event');
      await controller.cancel();

      expect(
        controller.state.phase,
        RealtimeTextStreamControllerPhase.cancelRequested,
      );

      client.emit(_started(1));
      await Future<void>.delayed(Duration.zero);

      expect(
        controller.state.phase,
        RealtimeTextStreamControllerPhase.cancelRequested,
      );
      expect(controller.state.outputText, isEmpty);
      expect(controller.state.lastSequence, 1);

      await controller.cancel();
      expect(client.cancelCalls, 1);

      client.emit(_cancelRequested(2));
      client.emit(_terminal(3, RealtimeTextStreamTerminalOutcome.cancelled));
      await Future<void>.delayed(Duration.zero);

      expect(
        controller.state.phase,
        RealtimeTextStreamControllerPhase.cancelled,
      );
      expect(controller.state.lastSequence, 3);
      expect(client.cancelCalls, 1);

      controller.dispose();
    });

    test('failed terminal exposes bounded safe problem', () async {
      final client = _FakeRealtimeTextStreamClient();
      final controller = RealtimeTextStreamController(client: client);

      await controller.start(inputText: 'input');
      client.emit(
        _terminal(
          1,
          RealtimeTextStreamTerminalOutcome.failed,
          publicErrorCode: 'stream_failed',
          safeMessage: 'bounded safe failure',
        ),
      );
      await Future<void>.delayed(Duration.zero);

      expect(controller.state.phase, RealtimeTextStreamControllerPhase.failed);
      expect(controller.state.problem!.code, 'stream_failed');
      expect(controller.state.problem!.message, 'bounded safe failure');

      controller.dispose();
    });

    test(
      'rejects invalid sequence session and turn without state mutation',
      () async {
        for (final event in <RealtimeTextStreamEvent>[
          _chunk(2, 'skip'),
          _chunk(1, 'other session', sessionId: 'session-2'),
          _chunk(1, 'other turn', turnId: 'turn-2'),
        ]) {
          final client = _FakeRealtimeTextStreamClient();
          final controller = RealtimeTextStreamController(client: client);

          await controller.start(inputText: 'input');
          client.emit(event);
          await Future<void>.delayed(Duration.zero);

          expect(
            controller.state.phase,
            RealtimeTextStreamControllerPhase.failed,
          );
          expect(controller.state.outputText, isEmpty);
          expect(controller.state.lastSequence, 0);
          expect(client.streamCancelCalls, 1);

          controller.dispose();
        }
      },
    );

    test('rejects directly generated invalid event contracts', () async {
      final longChunk = List<String>.filled(513, 'x').join();
      final longFinalText = List<String>.filled(4097, 'x').join();
      final invalidEvents = <RealtimeTextStreamEvent>[
        _started(
          1,
          chunk: RealtimeTextStreamChunk(
            sequence: 1,
            text: 'unexpected',
            outputCharCount: 10,
          ),
        ),
        _eventWithoutPayload(
          1,
          RealtimeTextStreamEventType.streamChunk,
          RealtimeTextStreamState.streaming,
        ),
        _chunkWithTerminal(1),
        _eventWithTerminal(
          1,
          RealtimeTextStreamEventType.streamCompleted,
          RealtimeTextStreamState.completed,
          RealtimeTextStreamTerminalOutcome.failed,
        ),
        _eventWithoutPayload(
          1,
          RealtimeTextStreamEventType.cancelRequested,
          RealtimeTextStreamState.streaming,
        ),
        _chunk(1, longChunk),
        _terminal(
          1,
          RealtimeTextStreamTerminalOutcome.completed,
          finalText: longFinalText,
        ),
      ];

      for (final event in invalidEvents) {
        final client = _FakeRealtimeTextStreamClient();
        final controller = RealtimeTextStreamController(client: client);

        await controller.start(inputText: 'input');
        client.emit(event);
        await Future<void>.delayed(Duration.zero);

        expect(
          controller.state.phase,
          RealtimeTextStreamControllerPhase.failed,
        );
        expect(controller.state.outputText, isEmpty);
        expect(controller.state.lastSequence, 0);
        expect(client.streamCancelCalls, 1);

        controller.dispose();
      }
    });

    test('reflects server cancelRequested without changing output', () async {
      final client = _FakeRealtimeTextStreamClient();
      final controller = RealtimeTextStreamController(client: client);

      await controller.start(inputText: 'input');
      client.emit(_started(1));
      client.emit(_chunk(2, 'hello', outputCharCount: 5));
      client.emit(_cancelRequested(3));
      await Future<void>.delayed(Duration.zero);

      expect(
        controller.state.phase,
        RealtimeTextStreamControllerPhase.cancelRequested,
      );
      expect(controller.state.outputText, 'hello');
      expect(controller.state.lastSequence, 3);

      controller.dispose();
    });

    test('rejects inconsistent terminal without changing output', () async {
      final client = _FakeRealtimeTextStreamClient();
      final controller = RealtimeTextStreamController(client: client);

      await controller.start(inputText: 'input');
      client.emit(_chunk(1, 'hello'));
      client.emit(
        _terminal(
          2,
          RealtimeTextStreamTerminalOutcome.completed,
          finalText: 'different',
          outputCharCount: 5,
        ),
      );
      await Future<void>.delayed(Duration.zero);

      expect(controller.state.phase, RealtimeTextStreamControllerPhase.failed);
      expect(controller.state.outputText, 'hello');
      expect(controller.state.lastSequence, 1);
      expect(controller.state.problem!.code, 'mismatched_terminal_final_text');
      expect(client.streamCancelCalls, 1);

      controller.dispose();
    });

    test('rejects terminal final text mismatches for all outcomes', () async {
      for (final outcome in <RealtimeTextStreamTerminalOutcome>[
        RealtimeTextStreamTerminalOutcome.cancelled,
        RealtimeTextStreamTerminalOutcome.failed,
        RealtimeTextStreamTerminalOutcome.closed,
      ]) {
        final client = _FakeRealtimeTextStreamClient();
        final controller = RealtimeTextStreamController(client: client);

        await controller.start(inputText: 'input');
        client.emit(_chunk(1, 'hello'));
        client.emit(
          _terminal(2, outcome, finalText: 'different', outputCharCount: 5),
        );
        await Future<void>.delayed(Duration.zero);

        expect(
          controller.state.phase,
          RealtimeTextStreamControllerPhase.failed,
        );
        expect(controller.state.outputText, 'hello');
        expect(controller.state.lastSequence, 1);
        expect(
          controller.state.problem!.code,
          'mismatched_terminal_final_text',
        );
        expect(client.streamCancelCalls, 1);

        controller.dispose();
      }
    });

    test(
      'rejects terminal empty final text and output count mismatch',
      () async {
        for (final terminal in <RealtimeTextStreamEvent>[
          _terminal(
            2,
            RealtimeTextStreamTerminalOutcome.completed,
            finalText: '',
            outputCharCount: 5,
          ),
          _terminal(
            2,
            RealtimeTextStreamTerminalOutcome.completed,
            finalText: 'hello',
            outputCharCount: 4,
          ),
        ]) {
          final client = _FakeRealtimeTextStreamClient();
          final controller = RealtimeTextStreamController(client: client);

          await controller.start(inputText: 'input');
          client.emit(_chunk(1, 'hello'));
          client.emit(terminal);
          await Future<void>.delayed(Duration.zero);

          expect(
            controller.state.phase,
            RealtimeTextStreamControllerPhase.failed,
          );
          expect(controller.state.outputText, 'hello');
          expect(controller.state.lastSequence, 1);
          expect(client.streamCancelCalls, 1);

          controller.dispose();
        }
      },
    );

    test('rejects oversized accumulated output', () async {
      final client = _FakeRealtimeTextStreamClient();
      final controller = RealtimeTextStreamController(client: client);

      await controller.start(inputText: 'input');
      for (var sequence = 1; sequence <= 9; sequence += 1) {
        client.emit(
          _chunk(
            sequence,
            List<String>.filled(512, 'x').join(),
            outputCharCount: sequence * 512,
          ),
        );
      }
      await Future<void>.delayed(Duration.zero);

      expect(controller.state.phase, RealtimeTextStreamControllerPhase.failed);
      expect(controller.state.problem!.code, 'output_limit_exceeded');
      expect(controller.state.outputText.runes.length, 4096);
      expect(client.streamCancelCalls, 1);

      controller.dispose();
    });

    test('ignores late events after terminal and dispose', () async {
      final client = _FakeRealtimeTextStreamClient();
      final controller = RealtimeTextStreamController(client: client);

      await controller.start(inputText: 'input');
      client.emit(_chunk(1, 'done'));
      client.emit(
        _terminal(
          2,
          RealtimeTextStreamTerminalOutcome.completed,
          finalText: 'done',
        ),
      );
      client.emit(_chunk(3, 'late'));
      await Future<void>.delayed(Duration.zero);

      expect(controller.state.outputText, 'done');
      expect(
        controller.state.phase,
        RealtimeTextStreamControllerPhase.completed,
      );

      controller.dispose();
      expect(client.streamCancelCalls, 1);
      client.emit(_chunk(3, 'after dispose'));
      await Future<void>.delayed(Duration.zero);

      expect(controller.state.outputText, 'done');
    });

    test('keeps input text out of public state after start failure', () async {
      const privateInput = 'private transcript-like input';
      final client = _FakeRealtimeTextStreamClient(
        createError: const RealtimeTextStreamProblemException(
          RealtimeTextStreamProblem(
            code: 'create_failed',
            message: 'safe create failure',
            retryable: true,
          ),
        ),
      );
      final controller = RealtimeTextStreamController(client: client);

      await controller.start(inputText: privateInput);

      expect(controller.state.phase, RealtimeTextStreamControllerPhase.failed);
      expect(controller.state.problem!.message, isNot(contains(privateInput)));
      expect(controller.state.outputText, isEmpty);

      controller.dispose();
    });
  });
}

class _FakeRealtimeTextStreamClient extends RealtimeTextStreamClient {
  _FakeRealtimeTextStreamClient({this.createError, this.cancelError})
    : super(baseUrl: 'http://backend.local', client: _NoopHttpClient()) {
    _events = StreamController<RealtimeTextStreamEvent>.broadcast(
      sync: true,
      onCancel: () {
        streamCancelCalls += 1;
        isClosed = true;
      },
    );
  }

  final Object? createError;
  final Object? cancelError;
  late final StreamController<RealtimeTextStreamEvent> _events;
  int cancelCalls = 0;
  int createCalls = 0;
  int closeCalls = 0;
  int streamCancelCalls = 0;
  bool isClosed = false;
  bool clientClosed = false;
  RealtimeTextStreamCreateResponse? created;

  @override
  Future<RealtimeTextStreamCreateResponse> createSession({
    required String inputText,
  }) async {
    createCalls += 1;
    if (createError != null) {
      throw createError!;
    }
    created = _createResponse();
    return created!;
  }

  @override
  Stream<RealtimeTextStreamEvent> streamEvents(
    RealtimeTextStreamCreateResponse createResponse,
  ) {
    return _events.stream;
  }

  @override
  Future<RealtimeTextStreamCancelResponse> cancel(
    RealtimeTextStreamCreateResponse createResponse,
  ) async {
    cancelCalls += 1;
    if (cancelError != null) {
      throw cancelError!;
    }
    return RealtimeTextStreamCancelResponse(
      accepted: true,
      sessionId: createResponse.session.sessionId,
      turnId: createResponse.turn.turnId,
      state: RealtimeTextStreamState.cancelled,
      cancelMode: 'cooperative',
      hardCancelSupported: false,
      terminal: true,
      safeMessage: 'cancelled',
    );
  }

  void emit(RealtimeTextStreamEvent event) {
    if (isClosed) {
      return;
    }
    _events.add(event);
  }

  @override
  void close() {
    if (clientClosed) {
      return;
    }
    clientClosed = true;
    closeCalls += 1;
    isClosed = true;
    unawaited(_events.close());
  }
}

class _NoopHttpClient extends http.BaseClient {
  @override
  Future<http.StreamedResponse> send(http.BaseRequest request) async {
    return http.StreamedResponse(Stream<List<int>>.empty(), 404);
  }
}

RealtimeTextStreamCreateResponse _createResponse() {
  return const RealtimeTextStreamCreateResponse(
    accepted: true,
    session: RealtimeTextStreamSession(
      sessionId: 'session-1',
      state: RealtimeTextStreamState.streaming,
      activeTurnId: 'turn-1',
      lastSequence: 1,
      isClosed: false,
      cancelMode: 'cooperative',
      hardCancelSupported: false,
    ),
    turn: RealtimeTextStreamTurn(
      sessionId: 'session-1',
      turnId: 'turn-1',
      state: RealtimeTextStreamState.streaming,
      chunkCount: 0,
      outputCharCount: 0,
      cancelRequested: false,
      terminalOutcome: null,
    ),
    eventsPath: '/realtime/text/sessions/session-1/events',
    cancelPath: '/realtime/text/sessions/session-1/cancel',
    idleTtlSeconds: 120,
    maxDurationSeconds: 60,
    maxPendingEvents: 32,
    maxEventBytes: 32768,
  );
}

RealtimeTextStreamEvent _chunk(
  int sequence,
  String text, {
  String sessionId = 'session-1',
  String? turnId = 'turn-1',
  int? outputCharCount,
}) {
  return RealtimeTextStreamEvent(
    eventType: RealtimeTextStreamEventType.streamChunk,
    sessionId: sessionId,
    turnId: turnId,
    sequence: sequence,
    state: RealtimeTextStreamState.streaming,
    chunk: RealtimeTextStreamChunk(
      sequence: sequence,
      text: text,
      outputCharCount: outputCharCount ?? text.runes.length,
    ),
    terminal: null,
    safeMessage: '',
  );
}

RealtimeTextStreamEvent _started(
  int sequence, {
  RealtimeTextStreamChunk? chunk,
}) {
  return RealtimeTextStreamEvent(
    eventType: RealtimeTextStreamEventType.streamStarted,
    sessionId: 'session-1',
    turnId: 'turn-1',
    sequence: sequence,
    state: RealtimeTextStreamState.streaming,
    chunk: chunk,
    terminal: null,
    safeMessage: '',
  );
}

RealtimeTextStreamEvent _cancelRequested(int sequence) {
  return RealtimeTextStreamEvent(
    eventType: RealtimeTextStreamEventType.cancelRequested,
    sessionId: 'session-1',
    turnId: 'turn-1',
    sequence: sequence,
    state: RealtimeTextStreamState.cancelRequested,
    chunk: null,
    terminal: null,
    safeMessage: '',
  );
}

RealtimeTextStreamEvent _eventWithoutPayload(
  int sequence,
  RealtimeTextStreamEventType eventType,
  RealtimeTextStreamState state,
) {
  return RealtimeTextStreamEvent(
    eventType: eventType,
    sessionId: 'session-1',
    turnId: 'turn-1',
    sequence: sequence,
    state: state,
    chunk: null,
    terminal: null,
    safeMessage: '',
  );
}

RealtimeTextStreamEvent _chunkWithTerminal(int sequence) {
  return RealtimeTextStreamEvent(
    eventType: RealtimeTextStreamEventType.streamChunk,
    sessionId: 'session-1',
    turnId: 'turn-1',
    sequence: sequence,
    state: RealtimeTextStreamState.streaming,
    chunk: RealtimeTextStreamChunk(
      sequence: sequence,
      text: 'x',
      outputCharCount: 1,
    ),
    terminal: RealtimeTextStreamTerminal(
      sequence: sequence,
      outcome: RealtimeTextStreamTerminalOutcome.failed,
      finalText: '',
      outputCharCount: 0,
      publicErrorCode: 'stream_failed',
      safeMessage: 'safe',
      retryable: true,
    ),
    safeMessage: '',
  );
}

RealtimeTextStreamEvent _eventWithTerminal(
  int sequence,
  RealtimeTextStreamEventType eventType,
  RealtimeTextStreamState state,
  RealtimeTextStreamTerminalOutcome terminalOutcome,
) {
  return RealtimeTextStreamEvent(
    eventType: eventType,
    sessionId: 'session-1',
    turnId: 'turn-1',
    sequence: sequence,
    state: state,
    chunk: null,
    terminal: RealtimeTextStreamTerminal(
      sequence: sequence,
      outcome: terminalOutcome,
      finalText: '',
      outputCharCount: 0,
      publicErrorCode:
          terminalOutcome == RealtimeTextStreamTerminalOutcome.failed
          ? 'stream_failed'
          : null,
      safeMessage: '',
      retryable: terminalOutcome == RealtimeTextStreamTerminalOutcome.failed,
    ),
    safeMessage: '',
  );
}

RealtimeTextStreamEvent _terminal(
  int sequence,
  RealtimeTextStreamTerminalOutcome outcome, {
  String finalText = '',
  int? outputCharCount,
  String safeMessage = '',
  String? publicErrorCode,
}) {
  return RealtimeTextStreamEvent(
    eventType: switch (outcome) {
      RealtimeTextStreamTerminalOutcome.completed =>
        RealtimeTextStreamEventType.streamCompleted,
      RealtimeTextStreamTerminalOutcome.cancelled =>
        RealtimeTextStreamEventType.streamCancelled,
      RealtimeTextStreamTerminalOutcome.failed =>
        RealtimeTextStreamEventType.streamFailed,
      RealtimeTextStreamTerminalOutcome.closed =>
        RealtimeTextStreamEventType.streamClosed,
    },
    sessionId: 'session-1',
    turnId: 'turn-1',
    sequence: sequence,
    state: switch (outcome) {
      RealtimeTextStreamTerminalOutcome.completed =>
        RealtimeTextStreamState.completed,
      RealtimeTextStreamTerminalOutcome.cancelled =>
        RealtimeTextStreamState.cancelled,
      RealtimeTextStreamTerminalOutcome.failed =>
        RealtimeTextStreamState.failed,
      RealtimeTextStreamTerminalOutcome.closed =>
        RealtimeTextStreamState.closed,
    },
    chunk: null,
    terminal: RealtimeTextStreamTerminal(
      sequence: sequence,
      outcome: outcome,
      finalText: finalText,
      outputCharCount: outputCharCount ?? finalText.runes.length,
      publicErrorCode: publicErrorCode,
      safeMessage: safeMessage,
      retryable: outcome == RealtimeTextStreamTerminalOutcome.failed,
    ),
    safeMessage: safeMessage,
  );
}
