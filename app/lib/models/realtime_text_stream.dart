import 'package:flutter/foundation.dart';

const int realtimeTextStreamMaxChunkChars = 512;
const int realtimeTextStreamMaxOutputChars = 4096;
const int realtimeTextStreamMaxProblemMessageChars = 240;

enum RealtimeTextStreamState {
  idle('idle'),
  streaming('streaming'),
  cancelRequested('cancel_requested'),
  completed('completed'),
  cancelled('cancelled'),
  failed('failed'),
  closed('closed');

  const RealtimeTextStreamState(this.wireName);

  final String wireName;

  static RealtimeTextStreamState fromWire(String value) {
    return RealtimeTextStreamState.values.firstWhere(
      (item) => item.wireName == value,
      orElse: () => throw const RealtimeTextStreamProblemException(
        RealtimeTextStreamProblem(
          code: 'invalid_stream_state',
          message: 'The stream state was not recognized.',
          retryable: false,
        ),
      ),
    );
  }
}

enum RealtimeTextStreamEventType {
  streamStarted('stream_started'),
  streamChunk('stream_chunk'),
  cancelRequested('cancel_requested'),
  streamCompleted('stream_completed'),
  streamCancelled('stream_cancelled'),
  streamFailed('stream_failed'),
  streamClosed('stream_closed');

  const RealtimeTextStreamEventType(this.wireName);

  final String wireName;

  static RealtimeTextStreamEventType fromWire(String value) {
    return RealtimeTextStreamEventType.values.firstWhere(
      (item) => item.wireName == value,
      orElse: () => throw const RealtimeTextStreamProblemException(
        RealtimeTextStreamProblem(
          code: 'invalid_stream_event_type',
          message: 'The stream event type was not recognized.',
          retryable: false,
        ),
      ),
    );
  }
}

enum RealtimeTextStreamTerminalOutcome {
  completed('completed'),
  cancelled('cancelled'),
  failed('failed'),
  closed('closed');

  const RealtimeTextStreamTerminalOutcome(this.wireName);

  final String wireName;

  static RealtimeTextStreamTerminalOutcome fromWire(String value) {
    return RealtimeTextStreamTerminalOutcome.values.firstWhere(
      (item) => item.wireName == value,
      orElse: () => throw const RealtimeTextStreamProblemException(
        RealtimeTextStreamProblem(
          code: 'invalid_terminal_outcome',
          message: 'The stream terminal outcome was not recognized.',
          retryable: false,
        ),
      ),
    );
  }
}

@immutable
class RealtimeTextStreamSession {
  const RealtimeTextStreamSession({
    required this.sessionId,
    required this.state,
    required this.activeTurnId,
    required this.lastSequence,
    required this.isClosed,
    required this.cancelMode,
    required this.hardCancelSupported,
    this.schemaVersion = 'drc.v3.realtime-text-stream-session.1',
  });

  final String schemaVersion;
  final String sessionId;
  final RealtimeTextStreamState state;
  final String? activeTurnId;
  final int lastSequence;
  final bool isClosed;
  final String cancelMode;
  final bool hardCancelSupported;

  factory RealtimeTextStreamSession.fromJson(Map<String, Object?> json) {
    final sessionId = _string(json['session_id'], 'missing_session_id');
    final lastSequence = _nonNegativeInt(
      json['last_sequence'],
      'invalid_last_sequence',
    );
    final cancelMode = _string(json['cancel_mode'], 'missing_cancel_mode');
    final hardCancelSupported = _bool(
      json['hard_cancel_supported'],
      'invalid_hard_cancel_supported',
    );
    if (cancelMode != 'cooperative' || hardCancelSupported) {
      throw const RealtimeTextStreamProblemException(
        RealtimeTextStreamProblem(
          code: 'unsupported_cancel_capability',
          message: 'The stream cancel capability is not supported.',
          retryable: false,
        ),
      );
    }
    return RealtimeTextStreamSession(
      schemaVersion:
          _optionalString(json['schema_version']) ??
          'drc.v3.realtime-text-stream-session.1',
      sessionId: sessionId,
      state: RealtimeTextStreamState.fromWire(
        _string(json['state'], 'missing_stream_state'),
      ),
      activeTurnId: _optionalString(json['active_turn_id']),
      lastSequence: lastSequence,
      isClosed: _bool(json['is_closed'], 'invalid_is_closed'),
      cancelMode: cancelMode,
      hardCancelSupported: hardCancelSupported,
    );
  }
}

@immutable
class RealtimeTextStreamTurn {
  const RealtimeTextStreamTurn({
    required this.sessionId,
    required this.turnId,
    required this.state,
    required this.chunkCount,
    required this.outputCharCount,
    required this.cancelRequested,
    required this.terminalOutcome,
    this.schemaVersion = 'drc.v3.realtime-text-stream-turn.1',
  });

  final String schemaVersion;
  final String sessionId;
  final String turnId;
  final RealtimeTextStreamState state;
  final int chunkCount;
  final int outputCharCount;
  final bool cancelRequested;
  final RealtimeTextStreamTerminalOutcome? terminalOutcome;

  factory RealtimeTextStreamTurn.fromJson(Map<String, Object?> json) {
    return RealtimeTextStreamTurn(
      schemaVersion:
          _optionalString(json['schema_version']) ??
          'drc.v3.realtime-text-stream-turn.1',
      sessionId: _string(json['session_id'], 'missing_session_id'),
      turnId: _string(json['turn_id'], 'missing_turn_id'),
      state: RealtimeTextStreamState.fromWire(
        _string(json['state'], 'missing_stream_state'),
      ),
      chunkCount: _nonNegativeInt(json['chunk_count'], 'invalid_chunk_count'),
      outputCharCount: _nonNegativeInt(
        json['output_char_count'],
        'invalid_output_char_count',
      ),
      cancelRequested: _bool(
        json['cancel_requested'],
        'invalid_cancel_requested',
      ),
      terminalOutcome: _optionalString(json['terminal_outcome']) == null
          ? null
          : RealtimeTextStreamTerminalOutcome.fromWire(
              _string(json['terminal_outcome'], 'invalid_terminal_outcome'),
            ),
    );
  }
}

@immutable
class RealtimeTextStreamChunk {
  const RealtimeTextStreamChunk({
    required this.sequence,
    required this.text,
    required this.outputCharCount,
    this.schemaVersion = 'drc.v3.realtime-text-stream-chunk.1',
  });

  final String schemaVersion;
  final int sequence;
  final String text;
  final int outputCharCount;

  factory RealtimeTextStreamChunk.fromJson(Map<String, Object?> json) {
    final text = _chunkText(json['text']);
    if (_codePointCount(text) > realtimeTextStreamMaxChunkChars) {
      throw const RealtimeTextStreamProblemException(
        RealtimeTextStreamProblem(
          code: 'chunk_limit_exceeded',
          message: 'The response chunk exceeded the configured text limit.',
          retryable: true,
        ),
      );
    }
    return RealtimeTextStreamChunk(
      schemaVersion:
          _optionalString(json['schema_version']) ??
          'drc.v3.realtime-text-stream-chunk.1',
      sequence: _positiveInt(json['sequence'], 'invalid_chunk_sequence'),
      text: text,
      outputCharCount: _nonNegativeInt(
        json['output_char_count'],
        'invalid_output_char_count',
      ),
    );
  }
}

@immutable
class RealtimeTextStreamTerminal {
  const RealtimeTextStreamTerminal({
    required this.sequence,
    required this.outcome,
    required this.finalText,
    required this.outputCharCount,
    required this.publicErrorCode,
    required this.safeMessage,
    required this.retryable,
    this.schemaVersion = 'drc.v3.realtime-text-stream-terminal.1',
  });

  final String schemaVersion;
  final int sequence;
  final RealtimeTextStreamTerminalOutcome outcome;
  final String finalText;
  final int outputCharCount;
  final String? publicErrorCode;
  final String safeMessage;
  final bool retryable;

  factory RealtimeTextStreamTerminal.fromJson(Map<String, Object?> json) {
    final finalText = _optionalPayloadString(json['final_text']) ?? '';
    final finalTextChars = _codePointCount(finalText);
    if (finalTextChars > realtimeTextStreamMaxOutputChars) {
      throw const RealtimeTextStreamProblemException(
        RealtimeTextStreamProblem(
          code: 'output_limit_exceeded',
          message:
              'The streamed response exceeded the configured output limit.',
          retryable: true,
        ),
      );
    }
    return RealtimeTextStreamTerminal(
      schemaVersion:
          _optionalString(json['schema_version']) ??
          'drc.v3.realtime-text-stream-terminal.1',
      sequence: _positiveInt(json['sequence'], 'invalid_terminal_sequence'),
      outcome: RealtimeTextStreamTerminalOutcome.fromWire(
        _string(json['outcome'], 'missing_terminal_outcome'),
      ),
      finalText: finalText,
      outputCharCount: _nonNegativeInt(
        json['output_char_count'],
        'invalid_output_char_count',
      ),
      publicErrorCode: _optionalString(json['public_error_code']),
      safeMessage: _boundedMessage(json['safe_message']),
      retryable: _bool(json['retryable'], 'invalid_retryable'),
    );
  }
}

@immutable
class RealtimeTextStreamEvent {
  const RealtimeTextStreamEvent({
    required this.eventType,
    required this.sessionId,
    required this.turnId,
    required this.sequence,
    required this.state,
    required this.chunk,
    required this.terminal,
    required this.safeMessage,
    this.schemaVersion = 'drc.v3.realtime-text-stream-event.1',
  });

  final String schemaVersion;
  final RealtimeTextStreamEventType eventType;
  final String sessionId;
  final String? turnId;
  final int sequence;
  final RealtimeTextStreamState state;
  final RealtimeTextStreamChunk? chunk;
  final RealtimeTextStreamTerminal? terminal;
  final String safeMessage;

  bool get isTerminal => terminal != null;

  void validateContract() {
    _validateEventPayload(this);
  }

  factory RealtimeTextStreamEvent.fromJson(Map<String, Object?> json) {
    final chunkJson = json['chunk'];
    final terminalJson = json['terminal'];
    final event = RealtimeTextStreamEvent(
      schemaVersion:
          _optionalString(json['schema_version']) ??
          'drc.v3.realtime-text-stream-event.1',
      eventType: RealtimeTextStreamEventType.fromWire(
        _string(json['event_type'], 'missing_event_type'),
      ),
      sessionId: _string(json['session_id'], 'missing_session_id'),
      turnId: _optionalString(json['turn_id']),
      sequence: _positiveInt(json['sequence'], 'invalid_event_sequence'),
      state: RealtimeTextStreamState.fromWire(
        _string(json['state'], 'missing_stream_state'),
      ),
      chunk: chunkJson == null
          ? null
          : RealtimeTextStreamChunk.fromJson(_map(chunkJson, 'invalid_chunk')),
      terminal: terminalJson == null
          ? null
          : RealtimeTextStreamTerminal.fromJson(
              _map(terminalJson, 'invalid_terminal'),
            ),
      safeMessage: _boundedMessage(json['safe_message']),
    );
    event.validateContract();
    return event;
  }
}

@immutable
class RealtimeTextStreamCreateResponse {
  const RealtimeTextStreamCreateResponse({
    required this.accepted,
    required this.session,
    required this.turn,
    required this.eventsPath,
    required this.cancelPath,
    required this.idleTtlSeconds,
    required this.maxDurationSeconds,
    required this.maxPendingEvents,
    required this.maxEventBytes,
    this.schemaVersion = 'drc.v3.realtime-text-stream-create.1',
  });

  final String schemaVersion;
  final bool accepted;
  final RealtimeTextStreamSession session;
  final RealtimeTextStreamTurn turn;
  final String eventsPath;
  final String cancelPath;
  final int idleTtlSeconds;
  final int maxDurationSeconds;
  final int maxPendingEvents;
  final int maxEventBytes;

  factory RealtimeTextStreamCreateResponse.fromJson(Map<String, Object?> json) {
    final accepted = _bool(json['accepted'], 'invalid_accepted');
    final session = RealtimeTextStreamSession.fromJson(
      _map(json['session'], 'invalid_session'),
    );
    final turn = RealtimeTextStreamTurn.fromJson(
      _map(json['turn'], 'invalid_turn'),
    );
    if (!accepted) {
      throw const RealtimeTextStreamProblemException(
        RealtimeTextStreamProblem(
          code: 'stream_create_not_accepted',
          message: 'The text stream create response was not accepted.',
          retryable: true,
        ),
      );
    }
    if (session.sessionId != turn.sessionId ||
        session.activeTurnId != turn.turnId) {
      throw const RealtimeTextStreamProblemException(
        RealtimeTextStreamProblem(
          code: 'mismatched_create_turn',
          message: 'The text stream create response was inconsistent.',
          retryable: true,
        ),
      );
    }
    return RealtimeTextStreamCreateResponse(
      schemaVersion:
          _optionalString(json['schema_version']) ??
          'drc.v3.realtime-text-stream-create.1',
      accepted: accepted,
      session: session,
      turn: turn,
      eventsPath: _relativePath(json['events_path'], 'invalid_events_path'),
      cancelPath: _relativePath(json['cancel_path'], 'invalid_cancel_path'),
      idleTtlSeconds: _positiveInt(
        json['idle_ttl_seconds'],
        'invalid_idle_ttl_seconds',
      ),
      maxDurationSeconds: _positiveInt(
        json['max_duration_seconds'],
        'invalid_max_duration_seconds',
      ),
      maxPendingEvents: _positiveInt(
        json['max_pending_events'],
        'invalid_max_pending_events',
      ),
      maxEventBytes: _positiveInt(
        json['max_event_bytes'],
        'invalid_max_event_bytes',
      ),
    );
  }
}

@immutable
class RealtimeTextStreamCancelResponse {
  const RealtimeTextStreamCancelResponse({
    required this.accepted,
    required this.sessionId,
    required this.turnId,
    required this.state,
    required this.cancelMode,
    required this.hardCancelSupported,
    required this.terminal,
    required this.safeMessage,
    this.schemaVersion = 'drc.v3.realtime-text-stream-cancel.1',
  });

  final String schemaVersion;
  final bool accepted;
  final String sessionId;
  final String? turnId;
  final RealtimeTextStreamState state;
  final String cancelMode;
  final bool hardCancelSupported;
  final bool terminal;
  final String safeMessage;

  factory RealtimeTextStreamCancelResponse.fromJson(Map<String, Object?> json) {
    final cancelMode = _string(json['cancel_mode'], 'missing_cancel_mode');
    final hardCancelSupported = _bool(
      json['hard_cancel_supported'],
      'invalid_hard_cancel_supported',
    );
    if (cancelMode != 'cooperative' || hardCancelSupported) {
      throw const RealtimeTextStreamProblemException(
        RealtimeTextStreamProblem(
          code: 'unsupported_cancel_capability',
          message: 'The stream cancel capability is not supported.',
          retryable: false,
        ),
      );
    }
    return RealtimeTextStreamCancelResponse(
      schemaVersion:
          _optionalString(json['schema_version']) ??
          'drc.v3.realtime-text-stream-cancel.1',
      accepted: _bool(json['accepted'], 'invalid_accepted'),
      sessionId: _string(json['session_id'], 'missing_session_id'),
      turnId: _optionalString(json['turn_id']),
      state: RealtimeTextStreamState.fromWire(
        _string(json['state'], 'missing_stream_state'),
      ),
      cancelMode: cancelMode,
      hardCancelSupported: hardCancelSupported,
      terminal: _bool(json['terminal'], 'invalid_terminal'),
      safeMessage: _boundedMessage(json['safe_message']),
    );
  }
}

@immutable
class RealtimeTextStreamProblem {
  const RealtimeTextStreamProblem({
    required this.code,
    required this.message,
    required this.retryable,
    this.schemaVersion = 'drc.v3.realtime-text-stream-problem.1',
  });

  final String schemaVersion;
  final String code;
  final String message;
  final bool retryable;

  factory RealtimeTextStreamProblem.fromJson(Map<String, Object?> json) {
    return RealtimeTextStreamProblem(
      schemaVersion:
          _optionalString(json['schema_version']) ??
          'drc.v3.realtime-text-stream-problem.1',
      code: _normalizeCode(_optionalString(json['code']) ?? 'stream_failed'),
      message: _boundedMessage(json['message']),
      retryable: _bool(json['retryable'], 'invalid_retryable'),
    );
  }
}

class RealtimeTextStreamProblemException implements Exception {
  const RealtimeTextStreamProblemException(this.problem);

  final RealtimeTextStreamProblem problem;

  @override
  String toString() => 'RealtimeTextStreamProblemException(${problem.code})';
}

Map<String, Object?> _map(Object? value, String code) {
  if (value is Map) {
    return Map<String, Object?>.from(value);
  }
  throw RealtimeTextStreamProblemException(
    RealtimeTextStreamProblem(
      code: code,
      message: 'The stream response shape was invalid.',
      retryable: true,
    ),
  );
}

String _chunkText(Object? value) {
  if (value is String && value.isNotEmpty) {
    return value;
  }
  throw const RealtimeTextStreamProblemException(
    RealtimeTextStreamProblem(
      code: 'missing_chunk_text',
      message: 'The stream response was missing a required value.',
      retryable: true,
    ),
  );
}

String _string(Object? value, String code) {
  if (value is String && value.trim().isNotEmpty) {
    return value.trim();
  }
  throw RealtimeTextStreamProblemException(
    RealtimeTextStreamProblem(
      code: code,
      message: 'The stream response was missing a required value.',
      retryable: true,
    ),
  );
}

String? _optionalString(Object? value) {
  if (value is String && value.trim().isNotEmpty) {
    return value.trim();
  }
  return null;
}

String? _optionalPayloadString(Object? value) {
  if (value is String) {
    return value;
  }
  return null;
}

String _relativePath(Object? value, String code) {
  final path = _string(value, code);
  final parsed = Uri.tryParse(path);
  if (parsed == null ||
      parsed.scheme.isNotEmpty ||
      parsed.hasAuthority ||
      parsed.host.isNotEmpty ||
      path.startsWith('//') ||
      !parsed.path.startsWith('/') ||
      parsed.hasFragment) {
    throw RealtimeTextStreamProblemException(
      RealtimeTextStreamProblem(
        code: code,
        message: 'The stream path was invalid.',
        retryable: true,
      ),
    );
  }
  return path;
}

bool _bool(Object? value, String code) {
  if (value is bool) {
    return value;
  }
  throw RealtimeTextStreamProblemException(
    RealtimeTextStreamProblem(
      code: code,
      message: 'The stream response contained an invalid flag.',
      retryable: true,
    ),
  );
}

int _positiveInt(Object? value, String code) {
  if (value is int && value > 0) {
    return value;
  }
  throw RealtimeTextStreamProblemException(
    RealtimeTextStreamProblem(
      code: code,
      message: 'The stream response contained an invalid sequence.',
      retryable: true,
    ),
  );
}

int _nonNegativeInt(Object? value, String code) {
  if (value is int && value >= 0) {
    return value;
  }
  throw RealtimeTextStreamProblemException(
    RealtimeTextStreamProblem(
      code: code,
      message: 'The stream response contained an invalid count.',
      retryable: true,
    ),
  );
}

String _boundedMessage(Object? value) {
  final raw = value is String ? value : 'The text stream failed safely.';
  final compact = raw
      .split(RegExp(r'\s+'))
      .where((part) => part.isNotEmpty)
      .join(' ');
  if (compact.isEmpty) {
    return 'The text stream failed safely.';
  }
  if (_codePointCount(compact) <= realtimeTextStreamMaxProblemMessageChars) {
    return compact;
  }
  return String.fromCharCodes(
    compact.runes.take(realtimeTextStreamMaxProblemMessageChars),
  );
}

String _normalizeCode(String value) {
  final buffer = StringBuffer();
  for (final codeUnit in value.trim().toLowerCase().codeUnits) {
    final isDigit = codeUnit >= 48 && codeUnit <= 57;
    final isLower = codeUnit >= 97 && codeUnit <= 122;
    final isSymbol = codeUnit == 45 || codeUnit == 46 || codeUnit == 95;
    if (isDigit || isLower || isSymbol) {
      buffer.writeCharCode(codeUnit);
    }
    if (buffer.length >= 64) {
      break;
    }
  }
  final normalized = buffer.toString();
  return normalized.isEmpty ? 'stream_failed' : normalized;
}

int _codePointCount(String value) => value.runes.length;

void _validateEventPayload(RealtimeTextStreamEvent event) {
  if (_codePointCount(event.safeMessage) >
      realtimeTextStreamMaxProblemMessageChars) {
    throw const RealtimeTextStreamProblemException(
      RealtimeTextStreamProblem(
        code: 'safe_message_limit_exceeded',
        message: 'The text-stream safe message exceeded the configured limit.',
        retryable: true,
      ),
    );
  }
  if (event.chunk != null && event.terminal != null) {
    throw const RealtimeTextStreamProblemException(
      RealtimeTextStreamProblem(
        code: 'invalid_stream_event_payload',
        message: 'The text-stream event payload was inconsistent.',
        retryable: true,
      ),
    );
  }
  if (event.turnId == null) {
    throw const RealtimeTextStreamProblemException(
      RealtimeTextStreamProblem(
        code: 'missing_turn_id',
        message: 'The text-stream event was missing a required value.',
        retryable: true,
      ),
    );
  }

  switch (event.eventType) {
    case RealtimeTextStreamEventType.streamStarted:
      _requireNoPayload(event);
      _requireState(event, RealtimeTextStreamState.streaming);
      break;
    case RealtimeTextStreamEventType.streamChunk:
      if (event.chunk == null || event.terminal != null) {
        _invalidEventShape();
      }
      _requireState(event, RealtimeTextStreamState.streaming);
      break;
    case RealtimeTextStreamEventType.cancelRequested:
      _requireNoPayload(event);
      _requireState(event, RealtimeTextStreamState.cancelRequested);
      break;
    case RealtimeTextStreamEventType.streamCompleted:
      _requireTerminal(event, RealtimeTextStreamTerminalOutcome.completed);
      break;
    case RealtimeTextStreamEventType.streamCancelled:
      _requireTerminal(event, RealtimeTextStreamTerminalOutcome.cancelled);
      break;
    case RealtimeTextStreamEventType.streamFailed:
      _requireTerminal(event, RealtimeTextStreamTerminalOutcome.failed);
      break;
    case RealtimeTextStreamEventType.streamClosed:
      _requireTerminal(event, RealtimeTextStreamTerminalOutcome.closed);
      break;
  }

  final chunk = event.chunk;
  if (chunk != null) {
    if (chunk.sequence != event.sequence) {
      throw const RealtimeTextStreamProblemException(
        RealtimeTextStreamProblem(
          code: 'mismatched_chunk_sequence',
          message: 'The text-stream chunk sequence was inconsistent.',
          retryable: true,
        ),
      );
    }
    if (_codePointCount(chunk.text) > realtimeTextStreamMaxChunkChars) {
      throw const RealtimeTextStreamProblemException(
        RealtimeTextStreamProblem(
          code: 'chunk_limit_exceeded',
          message: 'The response chunk exceeded the configured text limit.',
          retryable: true,
        ),
      );
    }
  }
  final terminal = event.terminal;
  if (terminal != null) {
    if (terminal.sequence != event.sequence) {
      throw const RealtimeTextStreamProblemException(
        RealtimeTextStreamProblem(
          code: 'mismatched_terminal_sequence',
          message: 'The text-stream terminal sequence was inconsistent.',
          retryable: true,
        ),
      );
    }
    if (_codePointCount(terminal.finalText) >
        realtimeTextStreamMaxOutputChars) {
      throw const RealtimeTextStreamProblemException(
        RealtimeTextStreamProblem(
          code: 'output_limit_exceeded',
          message:
              'The streamed response exceeded the configured output limit.',
          retryable: true,
        ),
      );
    }
    if (_codePointCount(terminal.safeMessage) >
        realtimeTextStreamMaxProblemMessageChars) {
      throw const RealtimeTextStreamProblemException(
        RealtimeTextStreamProblem(
          code: 'safe_message_limit_exceeded',
          message:
              'The text-stream safe message exceeded the configured limit.',
          retryable: true,
        ),
      );
    }
  }
}

void _requireNoPayload(RealtimeTextStreamEvent event) {
  if (event.chunk != null || event.terminal != null) {
    _invalidEventShape();
  }
}

void _requireState(
  RealtimeTextStreamEvent event,
  RealtimeTextStreamState expected,
) {
  if (event.state != expected) {
    _invalidEventShape();
  }
}

void _requireTerminal(
  RealtimeTextStreamEvent event,
  RealtimeTextStreamTerminalOutcome expected,
) {
  final terminal = event.terminal;
  if (event.chunk != null || terminal == null || terminal.outcome != expected) {
    _invalidEventShape();
  }
  _requireState(event, RealtimeTextStreamState.fromWire(expected.wireName));
}

Never _invalidEventShape() {
  throw const RealtimeTextStreamProblemException(
    RealtimeTextStreamProblem(
      code: 'invalid_stream_event_payload',
      message: 'The text-stream event payload was inconsistent.',
      retryable: true,
    ),
  );
}
