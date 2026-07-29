import 'dart:async';

import 'package:flutter/foundation.dart';

import '../models/realtime_text_stream.dart';
import 'realtime_text_stream_client.dart';

enum RealtimeTextStreamControllerPhase {
  idle,
  connecting,
  streaming,
  cancelRequested,
  completed,
  cancelled,
  failed,
  closed,
}

@immutable
class RealtimeTextStreamControllerState {
  const RealtimeTextStreamControllerState({
    required this.phase,
    required this.outputText,
    required this.lastSequence,
    required this.cancelMode,
    required this.hardCancelSupported,
    this.createResponse,
    this.terminal,
    this.problem,
  });

  const RealtimeTextStreamControllerState.idle()
    : this(
        phase: RealtimeTextStreamControllerPhase.idle,
        outputText: '',
        lastSequence: 0,
        cancelMode: 'cooperative',
        hardCancelSupported: false,
      );

  final RealtimeTextStreamControllerPhase phase;
  final String outputText;
  final int lastSequence;
  final String cancelMode;
  final bool hardCancelSupported;
  final RealtimeTextStreamCreateResponse? createResponse;
  final RealtimeTextStreamTerminal? terminal;
  final RealtimeTextStreamProblem? problem;

  bool get isActive =>
      phase == RealtimeTextStreamControllerPhase.connecting ||
      phase == RealtimeTextStreamControllerPhase.streaming ||
      phase == RealtimeTextStreamControllerPhase.cancelRequested;

  bool get isTerminal =>
      phase == RealtimeTextStreamControllerPhase.completed ||
      phase == RealtimeTextStreamControllerPhase.cancelled ||
      phase == RealtimeTextStreamControllerPhase.failed ||
      phase == RealtimeTextStreamControllerPhase.closed;

  RealtimeTextStreamControllerState copyWith({
    RealtimeTextStreamControllerPhase? phase,
    String? outputText,
    int? lastSequence,
    String? cancelMode,
    bool? hardCancelSupported,
    RealtimeTextStreamCreateResponse? createResponse,
    RealtimeTextStreamTerminal? terminal,
    RealtimeTextStreamProblem? problem,
  }) {
    return RealtimeTextStreamControllerState(
      phase: phase ?? this.phase,
      outputText: outputText ?? this.outputText,
      lastSequence: lastSequence ?? this.lastSequence,
      cancelMode: cancelMode ?? this.cancelMode,
      hardCancelSupported: hardCancelSupported ?? this.hardCancelSupported,
      createResponse: createResponse ?? this.createResponse,
      terminal: terminal ?? this.terminal,
      problem: problem ?? this.problem,
    );
  }
}

class RealtimeTextStreamController extends ChangeNotifier {
  RealtimeTextStreamController({required RealtimeTextStreamClient client})
    : _client = client;

  final RealtimeTextStreamClient _client;
  RealtimeTextStreamControllerState _state =
      const RealtimeTextStreamControllerState.idle();
  StreamSubscription<RealtimeTextStreamEvent>? _subscription;
  int _operation = 0;
  bool _isDisposed = false;
  bool _cancelInFlight = false;

  RealtimeTextStreamControllerState get state => _state;

  Future<void> start({required String inputText}) async {
    if (_isDisposed) {
      return;
    }
    if (_state.isActive) {
      throw const RealtimeTextStreamProblemException(
        RealtimeTextStreamProblem(
          code: 'active_stream_replacement_rejected',
          message: 'A text stream is already active.',
          retryable: false,
        ),
      );
    }

    final operation = ++_operation;
    final previousSubscription = _subscription;
    _subscription = null;
    _cancelInFlight = false;
    _setState(
      const RealtimeTextStreamControllerState.idle().copyWith(
        phase: RealtimeTextStreamControllerPhase.connecting,
      ),
    );

    try {
      await previousSubscription?.cancel();
      if (!_isCurrent(operation)) {
        return;
      }
      final created = await _client.createSession(inputText: inputText);
      if (!_isCurrent(operation)) {
        return;
      }
      _setState(
        _state.copyWith(
          phase: RealtimeTextStreamControllerPhase.streaming,
          createResponse: created,
          cancelMode: created.session.cancelMode,
          hardCancelSupported: false,
        ),
      );
      _subscription = _client
          .streamEvents(created)
          .listen(
            (event) => _handleEvent(operation, event),
            onError: (Object error) => _handleError(operation, error),
            onDone: () => _handleDone(operation),
            cancelOnError: true,
          );
    } on RealtimeTextStreamProblemException catch (error) {
      if (_isCurrent(operation)) {
        _fail(error.problem);
      }
    } catch (_) {
      if (_isCurrent(operation)) {
        _fail(
          const RealtimeTextStreamProblem(
            code: 'stream_start_failed',
            message: 'The text stream could not be started.',
            retryable: true,
          ),
        );
      }
    }
  }

  Future<void> cancel() async {
    if (_isDisposed ||
        !_state.isActive ||
        _cancelInFlight ||
        _state.phase == RealtimeTextStreamControllerPhase.cancelRequested) {
      return;
    }
    final createResponse = _state.createResponse;
    if (createResponse == null) {
      return;
    }
    _cancelInFlight = true;
    _setState(
      _state.copyWith(phase: RealtimeTextStreamControllerPhase.cancelRequested),
    );
    final operation = _operation;
    try {
      await _client.cancel(createResponse);
    } on RealtimeTextStreamProblemException catch (error) {
      if (_isCurrent(operation) && !_state.isTerminal) {
        _fail(error.problem);
      }
    } catch (_) {
      if (_isCurrent(operation) && !_state.isTerminal) {
        _fail(
          const RealtimeTextStreamProblem(
            code: 'stream_cancel_failed',
            message: 'The text stream cancel request failed.',
            retryable: true,
          ),
        );
      }
    } finally {
      _cancelInFlight = false;
    }
  }

  void _handleEvent(int operation, RealtimeTextStreamEvent event) {
    if (!_isCurrent(operation) || _state.isTerminal) {
      return;
    }

    final problem = _validateControllerEvent(event);
    if (problem != null) {
      _fail(problem);
      return;
    }

    if (event.eventType == RealtimeTextStreamEventType.streamStarted) {
      _setState(
        _state.copyWith(
          phase:
              _state.phase == RealtimeTextStreamControllerPhase.cancelRequested
              ? RealtimeTextStreamControllerPhase.cancelRequested
              : RealtimeTextStreamControllerPhase.streaming,
          lastSequence: event.sequence,
        ),
      );
      return;
    }

    if (event.eventType == RealtimeTextStreamEventType.cancelRequested) {
      _setState(
        _state.copyWith(
          phase: RealtimeTextStreamControllerPhase.cancelRequested,
          lastSequence: event.sequence,
        ),
      );
      return;
    }

    final chunk = event.chunk;
    if (chunk != null) {
      final nextOutput = _state.outputText + chunk.text;
      if (_codePointCount(nextOutput) > realtimeTextStreamMaxOutputChars) {
        _fail(
          const RealtimeTextStreamProblem(
            code: 'output_limit_exceeded',
            message:
                'The streamed response exceeded the configured output limit.',
            retryable: true,
          ),
        );
        return;
      }
      _setState(
        _state.copyWith(
          phase:
              _state.phase == RealtimeTextStreamControllerPhase.cancelRequested
              ? RealtimeTextStreamControllerPhase.cancelRequested
              : RealtimeTextStreamControllerPhase.streaming,
          outputText: nextOutput,
          lastSequence: event.sequence,
        ),
      );
      return;
    }

    final terminal = event.terminal;
    if (terminal != null) {
      _setState(
        _state.copyWith(
          phase: _phaseForTerminal(terminal.outcome),
          outputText: terminal.finalText,
          lastSequence: event.sequence,
          terminal: terminal,
          problem: terminal.outcome == RealtimeTextStreamTerminalOutcome.failed
              ? RealtimeTextStreamProblem(
                  code: terminal.publicErrorCode ?? 'stream_failed',
                  message: terminal.safeMessage.isNotEmpty
                      ? terminal.safeMessage
                      : 'The text stream failed safely.',
                  retryable: terminal.retryable,
                )
              : null,
        ),
      );
      _cancelSubscription();
      return;
    }
  }

  void _handleError(int operation, Object error) {
    if (!_isCurrent(operation) || _state.isTerminal) {
      return;
    }
    if (error is RealtimeTextStreamProblemException) {
      _fail(error.problem);
      return;
    }
    _fail(
      const RealtimeTextStreamProblem(
        code: 'stream_event_failed',
        message: 'The text stream event failed safely.',
        retryable: true,
      ),
    );
  }

  void _handleDone(int operation) {
    if (!_isCurrent(operation) || _state.isTerminal || _isDisposed) {
      return;
    }
    _fail(
      const RealtimeTextStreamProblem(
        code: 'stream_closed_without_terminal',
        message: 'The text stream ended before a terminal event.',
        retryable: true,
      ),
    );
  }

  void _fail(RealtimeTextStreamProblem problem) {
    _setState(
      _state.copyWith(
        phase: RealtimeTextStreamControllerPhase.failed,
        problem: problem,
        hardCancelSupported: false,
      ),
    );
    _cancelSubscription();
  }

  RealtimeTextStreamProblem? _validateControllerEvent(
    RealtimeTextStreamEvent event,
  ) {
    final createResponse = _state.createResponse;
    try {
      event.validateContract();
    } on RealtimeTextStreamProblemException catch (error) {
      return error.problem;
    }
    if (createResponse == null) {
      return const RealtimeTextStreamProblem(
        code: 'missing_create_response',
        message: 'The text stream controller state was inconsistent.',
        retryable: true,
      );
    }
    if (event.sequence != _state.lastSequence + 1) {
      return const RealtimeTextStreamProblem(
        code: 'out_of_order_stream_event',
        message: 'The text-stream event sequence was out of order.',
        retryable: true,
      );
    }
    if (event.sessionId != createResponse.session.sessionId) {
      return const RealtimeTextStreamProblem(
        code: 'mismatched_stream_session',
        message: 'The text-stream event belonged to another session.',
        retryable: false,
      );
    }
    if (event.turnId != createResponse.turn.turnId) {
      return const RealtimeTextStreamProblem(
        code: 'stale_stream_turn',
        message: 'The text-stream event belonged to an obsolete turn.',
        retryable: false,
      );
    }

    final chunk = event.chunk;
    if (chunk != null) {
      final nextOutputCount =
          _codePointCount(_state.outputText) + _codePointCount(chunk.text);
      if (chunk.sequence != event.sequence ||
          chunk.outputCharCount != nextOutputCount) {
        return const RealtimeTextStreamProblem(
          code: 'mismatched_chunk_output_count',
          message: 'The text-stream chunk output count was inconsistent.',
          retryable: true,
        );
      }
    }

    final terminal = event.terminal;
    if (terminal != null) {
      if (terminal.sequence != event.sequence ||
          terminal.outputCharCount != _codePointCount(_state.outputText)) {
        return const RealtimeTextStreamProblem(
          code: 'mismatched_terminal_output_count',
          message: 'The text-stream terminal output count was inconsistent.',
          retryable: true,
        );
      }
      if (terminal.finalText != _state.outputText) {
        return const RealtimeTextStreamProblem(
          code: 'mismatched_terminal_final_text',
          message: 'The text-stream terminal final text was inconsistent.',
          retryable: true,
        );
      }
    }
    return null;
  }

  RealtimeTextStreamControllerPhase _phaseForTerminal(
    RealtimeTextStreamTerminalOutcome outcome,
  ) {
    switch (outcome) {
      case RealtimeTextStreamTerminalOutcome.completed:
        return RealtimeTextStreamControllerPhase.completed;
      case RealtimeTextStreamTerminalOutcome.cancelled:
        return RealtimeTextStreamControllerPhase.cancelled;
      case RealtimeTextStreamTerminalOutcome.failed:
        return RealtimeTextStreamControllerPhase.failed;
      case RealtimeTextStreamTerminalOutcome.closed:
        return RealtimeTextStreamControllerPhase.closed;
    }
  }

  bool _isCurrent(int operation) => !_isDisposed && operation == _operation;

  void _cancelSubscription() {
    unawaited(_subscription?.cancel());
    _subscription = null;
  }

  void _setState(RealtimeTextStreamControllerState nextState) {
    if (_isDisposed) {
      return;
    }
    _state = nextState.copyWith(hardCancelSupported: false);
    notifyListeners();
  }

  @override
  void dispose() {
    if (_isDisposed) {
      return;
    }
    _isDisposed = true;
    ++_operation;
    _cancelSubscription();
    _client.close();
    super.dispose();
  }
}

int _codePointCount(String value) => value.runes.length;
