import 'dart:async';

import 'package:flutter/foundation.dart';

import '../models/framework_v600_realtime_session.dart';
import 'framework_v600_realtime_session_client.dart';

enum FrameworkV600RealtimeSessionPhase {
  idle,
  opening,
  ready,
  turnRunning,
  closing,
  closed,
  failed,
}

@immutable
class FrameworkV600RealtimeSessionControllerState {
  const FrameworkV600RealtimeSessionControllerState({
    required this.phase,
    required this.interruptInFlight,
    required this.diagnosticsInFlight,
    this.sessionId,
    this.openResult,
    this.latestTurnResult,
    this.latestInterruptResult,
    this.latestDiagnostics,
    this.problem,
  });

  const FrameworkV600RealtimeSessionControllerState.idle()
    : this(
        phase: FrameworkV600RealtimeSessionPhase.idle,
        interruptInFlight: false,
        diagnosticsInFlight: false,
      );

  final FrameworkV600RealtimeSessionPhase phase;
  final bool interruptInFlight;
  final bool diagnosticsInFlight;
  final String? sessionId;
  final FrameworkV600RealtimeOpenResult? openResult;
  final FrameworkV600RealtimeTurnResult? latestTurnResult;
  final FrameworkV600RealtimeInterruptResult? latestInterruptResult;
  final FrameworkV600RealtimeDiagnosticsSnapshot? latestDiagnostics;
  final FrameworkV600RealtimeProblem? problem;

  FrameworkV600RealtimeSessionControllerState copyWith({
    FrameworkV600RealtimeSessionPhase? phase,
    bool? interruptInFlight,
    bool? diagnosticsInFlight,
    String? sessionId,
    FrameworkV600RealtimeOpenResult? openResult,
    FrameworkV600RealtimeTurnResult? latestTurnResult,
    FrameworkV600RealtimeInterruptResult? latestInterruptResult,
    FrameworkV600RealtimeDiagnosticsSnapshot? latestDiagnostics,
    FrameworkV600RealtimeProblem? problem,
    bool clearProblem = false,
  }) {
    return FrameworkV600RealtimeSessionControllerState(
      phase: phase ?? this.phase,
      interruptInFlight: interruptInFlight ?? this.interruptInFlight,
      diagnosticsInFlight: diagnosticsInFlight ?? this.diagnosticsInFlight,
      sessionId: sessionId ?? this.sessionId,
      openResult: openResult ?? this.openResult,
      latestTurnResult: latestTurnResult ?? this.latestTurnResult,
      latestInterruptResult:
          latestInterruptResult ?? this.latestInterruptResult,
      latestDiagnostics: latestDiagnostics ?? this.latestDiagnostics,
      problem: clearProblem ? null : problem ?? this.problem,
    );
  }
}

class FrameworkV600RealtimeSessionController extends ChangeNotifier {
  FrameworkV600RealtimeSessionController({
    required FrameworkV600RealtimeSessionClient client,
  }) : _client = client;

  final FrameworkV600RealtimeSessionClient _client;
  FrameworkV600RealtimeSessionControllerState _state =
      const FrameworkV600RealtimeSessionControllerState.idle();
  int _generation = 0;
  int? _openGeneration;
  Future<FrameworkV600RealtimeOpenResult>? _openInFlight;
  Future<void>? _closeInFlight;
  bool _disposed = false;

  FrameworkV600RealtimeSessionControllerState get state => _state;

  Future<void> open() async {
    if (_disposed || _state.phase == FrameworkV600RealtimeSessionPhase.closed) {
      return;
    }
    if (_state.phase != FrameworkV600RealtimeSessionPhase.idle) {
      throw _localProblem(
        'session_open_not_allowed',
        'The session cannot be opened in the current state.',
      );
    }
    final generation = ++_generation;
    _setState(
      const FrameworkV600RealtimeSessionControllerState.idle().copyWith(
        phase: FrameworkV600RealtimeSessionPhase.opening,
        clearProblem: true,
      ),
    );
    final openFuture = _client.createSession();
    _openGeneration = generation;
    _openInFlight = openFuture;
    try {
      final result = await openFuture;
      if (!_isCurrent(generation)) {
        return;
      }
      _setState(
        _state.copyWith(
          phase: FrameworkV600RealtimeSessionPhase.ready,
          sessionId: result.sessionId,
          openResult: result,
          clearProblem: true,
        ),
      );
    } on FrameworkV600RealtimeProblemException catch (error) {
      if (_isCurrent(generation)) {
        _fail(error.problem);
      }
    } catch (_) {
      if (_isCurrent(generation)) {
        _fail(
          const FrameworkV600RealtimeProblem(
            code: 'request_failed',
            message: 'The request failed safely.',
            retryable: false,
          ),
        );
      }
    } finally {
      if (_openGeneration == generation) {
        _openGeneration = null;
        _openInFlight = null;
      }
    }
  }

  Future<void> runTurn({required String inputText}) async {
    final sessionId = _state.sessionId;
    if (_state.phase == FrameworkV600RealtimeSessionPhase.turnRunning) {
      throw _localProblem('turn_already_active', 'A turn is already active.');
    }
    if (_disposed ||
        sessionId == null ||
        _state.phase != FrameworkV600RealtimeSessionPhase.ready) {
      throw _localProblem('session_not_ready', 'The session is not ready.');
    }
    final generation = _generation;
    _setState(
      _state.copyWith(
        phase: FrameworkV600RealtimeSessionPhase.turnRunning,
        clearProblem: true,
      ),
    );
    try {
      final result = await _client.runTurn(
        sessionId: sessionId,
        inputText: inputText,
      );
      if (!_isCurrent(generation)) {
        return;
      }
      _setState(
        _state.copyWith(
          phase: FrameworkV600RealtimeSessionPhase.ready,
          latestTurnResult: result,
          clearProblem: true,
        ),
      );
    } on FrameworkV600RealtimeProblemException catch (error) {
      if (_isCurrent(generation)) {
        _fail(error.problem);
      }
    }
  }

  Future<void> interrupt({
    String scope = 'current_turn',
    String reason = 'host_app_request',
  }) async {
    final sessionId = _state.sessionId;
    if (_disposed ||
        sessionId == null ||
        _state.phase == FrameworkV600RealtimeSessionPhase.closed ||
        _state.phase == FrameworkV600RealtimeSessionPhase.closing) {
      return;
    }
    final generation = _generation;
    _setState(_state.copyWith(interruptInFlight: true));
    try {
      final result = await _client.interrupt(
        sessionId: sessionId,
        scope: scope,
        reason: reason,
      );
      if (_isCurrent(generation)) {
        _setState(
          _state.copyWith(
            interruptInFlight: false,
            latestInterruptResult: result,
          ),
        );
      }
    } on FrameworkV600RealtimeProblemException catch (error) {
      if (_isCurrent(generation)) {
        _setState(
          _state.copyWith(interruptInFlight: false, problem: error.problem),
        );
      }
    } finally {
      if (_isCurrent(generation) && _state.interruptInFlight) {
        _setState(_state.copyWith(interruptInFlight: false));
      }
    }
  }

  Future<void> diagnostics() async {
    final sessionId = _state.sessionId;
    if (_disposed ||
        sessionId == null ||
        _state.phase == FrameworkV600RealtimeSessionPhase.closed ||
        _state.phase == FrameworkV600RealtimeSessionPhase.closing) {
      return;
    }
    final generation = _generation;
    _setState(_state.copyWith(diagnosticsInFlight: true));
    try {
      final result = await _client.diagnostics(sessionId: sessionId);
      if (_isCurrent(generation)) {
        _setState(
          _state.copyWith(
            diagnosticsInFlight: false,
            latestDiagnostics: result,
          ),
        );
      }
    } on FrameworkV600RealtimeProblemException catch (error) {
      if (_isCurrent(generation)) {
        _setState(
          _state.copyWith(diagnosticsInFlight: false, problem: error.problem),
        );
      }
    } finally {
      if (_isCurrent(generation) && _state.diagnosticsInFlight) {
        _setState(_state.copyWith(diagnosticsInFlight: false));
      }
    }
  }

  Future<void> close() {
    if (_disposed || _state.phase == FrameworkV600RealtimeSessionPhase.closed) {
      return Future<void>.value();
    }
    final existing = _closeInFlight;
    if (existing != null) {
      return existing;
    }
    final completer = Completer<void>();
    final sharedFuture = completer.future;
    _closeInFlight = sharedFuture;
    Future<void>(() async {
      try {
        await _performClose();
        if (!completer.isCompleted) {
          completer.complete();
        }
      } catch (error, stackTrace) {
        if (!completer.isCompleted) {
          completer.completeError(error, stackTrace);
        }
      } finally {
        if (identical(_closeInFlight, sharedFuture)) {
          _closeInFlight = null;
        }
      }
    });
    return sharedFuture;
  }

  Future<void> _performClose() async {
    final sessionId = _state.sessionId;
    final openInFlight = _openInFlight;
    _generation++;
    _setState(
      _state.copyWith(
        phase: FrameworkV600RealtimeSessionPhase.closing,
        interruptInFlight: false,
        diagnosticsInFlight: false,
      ),
    );
    if (sessionId != null) {
      try {
        await _client.closeSession(sessionId: sessionId);
      } on FrameworkV600RealtimeProblemException catch (error) {
        _setState(
          _state.copyWith(
            phase: FrameworkV600RealtimeSessionPhase.closed,
            problem: error.problem,
          ),
        );
        return;
      }
    }
    if (sessionId == null && openInFlight != null) {
      try {
        final opened = await openInFlight;
        await _client.closeSession(sessionId: opened.sessionId);
      } on FrameworkV600RealtimeProblemException catch (error) {
        _setState(
          _state.copyWith(
            phase: FrameworkV600RealtimeSessionPhase.closed,
            problem: error.problem,
          ),
        );
        return;
      }
    }
    _setState(
      _state.copyWith(
        phase: FrameworkV600RealtimeSessionPhase.closed,
        interruptInFlight: false,
        diagnosticsInFlight: false,
      ),
    );
  }

  @override
  void dispose() {
    _disposed = true;
    _generation++;
    _client.close();
    super.dispose();
  }

  bool _isCurrent(int generation) =>
      !_disposed &&
      generation == _generation &&
      _state.phase != FrameworkV600RealtimeSessionPhase.closed &&
      _state.phase != FrameworkV600RealtimeSessionPhase.closing;

  void _fail(FrameworkV600RealtimeProblem problem) {
    _setState(
      _state.copyWith(
        phase: FrameworkV600RealtimeSessionPhase.failed,
        problem: problem,
      ),
    );
  }

  void _setState(FrameworkV600RealtimeSessionControllerState state) {
    _state = state;
    notifyListeners();
  }

  FrameworkV600RealtimeProblemException _localProblem(
    String code,
    String message,
  ) {
    return FrameworkV600RealtimeProblemException(
      FrameworkV600RealtimeProblem(
        code: code,
        message: message,
        retryable: false,
      ),
    );
  }
}
