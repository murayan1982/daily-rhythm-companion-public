import 'package:flutter/foundation.dart';

const int frameworkV600RealtimeMaxInputChars = 4096;
const int frameworkV600RealtimeMaxBodyBytes = 64 * 1024;

const String frameworkV600OpenSchema =
    'drc.v4.framework-v600-open-result.1';
const String frameworkV600TurnSchema =
    'drc.v4.framework-v600-turn-result.1';
const String frameworkV600InterruptSchema =
    'drc.v4.framework-v600-interrupt-result.1';
const String frameworkV600DiagnosticsSchema =
    'drc.v4.framework-v600-diagnostics.1';
const String frameworkV600CapabilitySchema =
    'drc.v4.framework-v600-capability-snapshot.1';
const String frameworkV600EventSchema =
    'drc.v4.framework-v600-realtime-event.1';

final RegExp _sessionIdPattern = RegExp(r'^fw_session_[0-9a-f]{32}$');
final RegExp _turnIdPattern = RegExp(r'^fw_turn_[0-9a-f]{32}$');
final RegExp _generationIdPattern = RegExp(
  r'^fw_generation_[0-9a-f]{32}$',
);

@immutable
class FrameworkV600RealtimeProblem {
  const FrameworkV600RealtimeProblem({
    required this.code,
    required this.message,
    required this.retryable,
  });

  final String code;
  final String message;
  final bool retryable;

  factory FrameworkV600RealtimeProblem.fromJson(Map<String, Object?> json) {
    return FrameworkV600RealtimeProblem(
      code: _boundedString(json['code'], 'invalid_problem'),
      message: _boundedString(json['message'], 'invalid_problem'),
      retryable: _bool(json['retryable'], 'invalid_problem'),
    );
  }

  @override
  String toString() =>
      'FrameworkV600RealtimeProblem(code: $code, retryable: $retryable)';
}

class FrameworkV600RealtimeProblemException implements Exception {
  const FrameworkV600RealtimeProblemException(this.problem);

  final FrameworkV600RealtimeProblem problem;

  @override
  String toString() => 'FrameworkV600RealtimeProblemException(${problem.code})';
}

@immutable
class FrameworkV600RealtimeCapabilitySnapshot {
  const FrameworkV600RealtimeCapabilitySnapshot({
    required this.sessionId,
    required this.supportsTextChat,
    required this.supportsVoiceInput,
    required this.supportsVoiceOutput,
    required this.supportsMotion,
    required this.realRuntimeEnabled,
    required this.hardCancelSupported,
    required this.ttsQueueFlushSupported,
    required this.runtimeAvailable,
    required this.fakeRuntime,
    required this.realRuntime,
    required this.guarded,
    required this.cooperativeCancelSupported,
    required this.providerHardCancelSupported,
    required this.pendingFlushSupported,
    required this.hostPlaybackOwnedByDrc,
    required this.realUnifiedRuntimeAvailable,
    required this.unifiedRealPipelineClaimed,
    this.schemaVersion = frameworkV600CapabilitySchema,
  });

  final String schemaVersion;
  final String sessionId;
  final bool supportsTextChat;
  final bool supportsVoiceInput;
  final bool supportsVoiceOutput;
  final bool supportsMotion;
  final bool realRuntimeEnabled;
  final bool hardCancelSupported;
  final bool ttsQueueFlushSupported;
  final bool runtimeAvailable;
  final String fakeRuntime;
  final String realRuntime;
  final bool guarded;
  final bool cooperativeCancelSupported;
  final bool providerHardCancelSupported;
  final bool pendingFlushSupported;
  final bool hostPlaybackOwnedByDrc;
  final bool realUnifiedRuntimeAvailable;
  final bool unifiedRealPipelineClaimed;

  factory FrameworkV600RealtimeCapabilitySnapshot.fromJson(
    Map<String, Object?> json,
  ) {
    _requireSchema(json, frameworkV600CapabilitySchema);
    final sessionId = _sessionId(json['session_id']);
    return FrameworkV600RealtimeCapabilitySnapshot(
      sessionId: sessionId,
      supportsTextChat: _bool(json['supports_text_chat'], 'invalid_capability'),
      supportsVoiceInput: _bool(
        json['supports_voice_input'],
        'invalid_capability',
      ),
      supportsVoiceOutput: _bool(
        json['supports_voice_output'],
        'invalid_capability',
      ),
      supportsMotion: _bool(json['supports_motion'], 'invalid_capability'),
      realRuntimeEnabled: _bool(
        json['real_runtime_enabled'],
        'invalid_capability',
      ),
      hardCancelSupported: _bool(
        json['hard_cancel_supported'],
        'invalid_capability',
      ),
      ttsQueueFlushSupported: _bool(
        json['tts_queue_flush_supported'],
        'invalid_capability',
      ),
      runtimeAvailable: _bool(
        json['runtime_available'],
        'invalid_capability',
      ),
      fakeRuntime: _boundedString(json['fake_runtime'], 'invalid_capability'),
      realRuntime: _boundedString(json['real_runtime'], 'invalid_capability'),
      guarded: _bool(json['guarded'], 'invalid_capability'),
      cooperativeCancelSupported: _bool(
        json['cooperative_cancel_supported'],
        'invalid_capability',
      ),
      providerHardCancelSupported: _bool(
        json['provider_hard_cancel_supported'],
        'invalid_capability',
      ),
      pendingFlushSupported: _bool(
        json['pending_flush_supported'],
        'invalid_capability',
      ),
      hostPlaybackOwnedByDrc: _bool(
        json['host_playback_owned_by_drc'],
        'invalid_capability',
      ),
      realUnifiedRuntimeAvailable: _bool(
        json['real_unified_runtime_available'],
        'invalid_capability',
      ),
      unifiedRealPipelineClaimed: _bool(
        json['unified_real_pipeline_claimed'],
        'invalid_capability',
      ),
    );
  }
}

@immutable
class FrameworkV600RealtimeOpenResult {
  const FrameworkV600RealtimeOpenResult({
    required this.status,
    required this.available,
    required this.sessionId,
    required this.retryable,
    required this.realRuntimeRequested,
    required this.realRuntimeEnabled,
    required this.runtimeExecutable,
    required this.capabilities,
    this.publicErrorCode,
    this.safeMessage = '',
    this.schemaVersion = frameworkV600OpenSchema,
  });

  final String schemaVersion;
  final String status;
  final bool available;
  final String sessionId;
  final String? publicErrorCode;
  final String safeMessage;
  final bool retryable;
  final bool realRuntimeRequested;
  final bool realRuntimeEnabled;
  final bool runtimeExecutable;
  final FrameworkV600RealtimeCapabilitySnapshot capabilities;

  factory FrameworkV600RealtimeOpenResult.fromJson(Map<String, Object?> json) {
    _requireSchema(json, frameworkV600OpenSchema);
    final sessionId = _sessionId(json['session_id']);
    final capabilities = FrameworkV600RealtimeCapabilitySnapshot.fromJson(
      _map(json['capabilities'], 'invalid_capability'),
    );
    if (capabilities.sessionId != sessionId ||
        _bool(json['available'], 'invalid_open_result') != true ||
        _bool(json['real_runtime_requested'], 'invalid_open_result') ||
        _bool(json['real_runtime_enabled'], 'invalid_open_result') ||
        _bool(json['runtime_executable'], 'invalid_open_result') != true ||
        capabilities.realRuntimeEnabled ||
        capabilities.realUnifiedRuntimeAvailable ||
        capabilities.unifiedRealPipelineClaimed) {
      throw _problem('invalid_open_invariant', 'The open response was invalid.');
    }
    return FrameworkV600RealtimeOpenResult(
      status: _boundedString(json['status'], 'invalid_open_result'),
      available: true,
      sessionId: sessionId,
      publicErrorCode: _optionalBoundedString(json['public_error_code']),
      safeMessage: _optionalBoundedString(json['safe_message']) ?? '',
      retryable: _bool(json['retryable'], 'invalid_open_result'),
      realRuntimeRequested: false,
      realRuntimeEnabled: false,
      runtimeExecutable: true,
      capabilities: capabilities,
    );
  }
}

@immutable
class FrameworkV600RealtimeEventSummary {
  const FrameworkV600RealtimeEventSummary({
    required this.eventType,
    required this.sessionId,
    required this.sequence,
    required this.phase,
    required this.terminal,
    required this.retryable,
    this.turnId,
    this.generationId,
    this.publicErrorCode,
    this.safeMessage = '',
    this.schemaVersion = frameworkV600EventSchema,
  });

  final String schemaVersion;
  final String eventType;
  final String sessionId;
  final String? turnId;
  final String? generationId;
  final int sequence;
  final String phase;
  final bool terminal;
  final String? publicErrorCode;
  final String safeMessage;
  final bool retryable;

  factory FrameworkV600RealtimeEventSummary.fromJson(
    Map<String, Object?> json,
  ) {
    _requireSchema(json, frameworkV600EventSchema);
    final sequence = _int(json['sequence'], 'invalid_event');
    if (sequence < 1) {
      throw _problem('invalid_event', 'The realtime event was invalid.');
    }
    return FrameworkV600RealtimeEventSummary(
      eventType: _boundedString(json['event_type'], 'invalid_event'),
      sessionId: _sessionId(json['session_id']),
      turnId: _optionalTurnId(json['turn_id']),
      generationId: _optionalGenerationId(json['generation_id']),
      sequence: sequence,
      phase: _boundedString(json['phase'], 'invalid_event'),
      terminal: _bool(json['terminal'], 'invalid_event'),
      publicErrorCode: _optionalBoundedString(json['public_error_code']),
      safeMessage: _optionalBoundedString(json['safe_message']) ?? '',
      retryable: _bool(json['retryable'], 'invalid_event'),
    );
  }
}

@immutable
class FrameworkV600RealtimeTurnResult {
  const FrameworkV600RealtimeTurnResult({
    required this.outcome,
    required this.terminal,
    required this.retryable,
    required this.recoveryAction,
    required this.events,
    this.sessionId,
    this.turnId,
    this.generationId,
    this.publicErrorCode,
    this.safeMessage = '',
    this.capabilities,
    this.diagnostics,
    this.interrupt,
    this.schemaVersion = frameworkV600TurnSchema,
  });

  final String schemaVersion;
  final String outcome;
  final bool terminal;
  final String? sessionId;
  final String? turnId;
  final String? generationId;
  final String? publicErrorCode;
  final String safeMessage;
  final bool retryable;
  final String recoveryAction;
  final List<FrameworkV600RealtimeEventSummary> events;
  final FrameworkV600RealtimeCapabilitySnapshot? capabilities;
  final FrameworkV600RealtimeDiagnosticsSnapshot? diagnostics;
  final FrameworkV600RealtimeInterruptResult? interrupt;

  factory FrameworkV600RealtimeTurnResult.fromJson(Map<String, Object?> json) {
    _requireSchema(json, frameworkV600TurnSchema);
    final outcome = _boundedString(json['outcome'], 'invalid_turn_result');
    if (!{'completed', 'failed', 'unavailable', 'closed'}.contains(outcome)) {
      throw _problem('invalid_turn_result', 'The turn response was invalid.');
    }
    return FrameworkV600RealtimeTurnResult(
      outcome: outcome,
      terminal: _bool(json['terminal'], 'invalid_turn_result'),
      sessionId: _optionalSessionId(json['session_id']),
      turnId: _optionalTurnId(json['turn_id']),
      generationId: _optionalGenerationId(json['generation_id']),
      publicErrorCode: _optionalBoundedString(json['public_error_code']),
      safeMessage: _optionalBoundedString(json['safe_message']) ?? '',
      retryable: _bool(json['retryable'], 'invalid_turn_result'),
      recoveryAction:
          _optionalBoundedString(json['recovery_action']) ?? 'none',
      events: [
        for (final item in _optionalList(json['events']))
          FrameworkV600RealtimeEventSummary.fromJson(
            _map(item, 'invalid_event'),
          ),
      ],
      capabilities: json['capabilities'] == null
          ? null
          : FrameworkV600RealtimeCapabilitySnapshot.fromJson(
              _map(json['capabilities'], 'invalid_capability'),
            ),
      diagnostics: json['diagnostics'] == null
          ? null
          : FrameworkV600RealtimeDiagnosticsSnapshot.fromJson(
              _map(json['diagnostics'], 'invalid_diagnostics'),
            ),
      interrupt: json['interrupt'] == null
          ? null
          : FrameworkV600RealtimeInterruptResult.fromJson(
              _map(json['interrupt'], 'invalid_interrupt_result'),
            ),
    );
  }
}

@immutable
class FrameworkV600RealtimeInterruptResult {
  const FrameworkV600RealtimeInterruptResult({
    required this.outcome,
    required this.scope,
    required this.reason,
    required this.providerCancelSupported,
    required this.providerCancelApplied,
    required this.queueFlushSupported,
    required this.queueFlushApplied,
    required this.hostPlaybackStopSupported,
    required this.hostPlaybackStopApplied,
    required this.safeMessage,
    required this.retryable,
    this.schemaVersion = frameworkV600InterruptSchema,
  });

  final String schemaVersion;
  final String outcome;
  final String scope;
  final String reason;
  final bool providerCancelSupported;
  final bool providerCancelApplied;
  final bool queueFlushSupported;
  final bool queueFlushApplied;
  final bool hostPlaybackStopSupported;
  final bool hostPlaybackStopApplied;
  final String safeMessage;
  final bool retryable;

  factory FrameworkV600RealtimeInterruptResult.fromJson(
    Map<String, Object?> json,
  ) {
    _requireSchema(json, frameworkV600InterruptSchema);
    return FrameworkV600RealtimeInterruptResult(
      outcome: _boundedString(json['outcome'], 'invalid_interrupt_result'),
      scope: _boundedString(json['scope'], 'invalid_interrupt_result'),
      reason:
          _optionalBoundedString(json['reason']) ?? 'host_app_request',
      providerCancelSupported: _bool(
        json['provider_cancel_supported'],
        'invalid_interrupt_result',
      ),
      providerCancelApplied: _bool(
        json['provider_cancel_applied'],
        'invalid_interrupt_result',
      ),
      queueFlushSupported: _bool(
        json['queue_flush_supported'],
        'invalid_interrupt_result',
      ),
      queueFlushApplied: _bool(
        json['queue_flush_applied'],
        'invalid_interrupt_result',
      ),
      hostPlaybackStopSupported: _bool(
        json['host_playback_stop_supported'],
        'invalid_interrupt_result',
      ),
      hostPlaybackStopApplied: _bool(
        json['host_playback_stop_applied'],
        'invalid_interrupt_result',
      ),
      safeMessage: _optionalBoundedString(json['safe_message']) ?? '',
      retryable: _bool(json['retryable'], 'invalid_interrupt_result'),
    );
  }
}

@immutable
class FrameworkV600RealtimeDiagnosticsSnapshot {
  const FrameworkV600RealtimeDiagnosticsSnapshot({
    required this.sessionId,
    required this.state,
    required this.phase,
    required this.isClosed,
    required this.queueDepth,
    required this.activeGenerationCount,
    required this.staleCompletionCount,
    required this.duplicateTerminalCount,
    required this.overflowCount,
    this.activeTurnId,
    this.activeGenerationId,
    this.lastTerminalEventType,
    this.lastTerminalTurnId,
    this.lastTerminalGenerationId,
    this.lastTerminalOutcome,
    this.lastTerminalPublicErrorCode,
    this.lastTerminalRetryable = false,
    this.lastTerminalRecoveryAction,
    this.lastSafeErrorCode,
    this.schemaVersion = frameworkV600DiagnosticsSchema,
  });

  final String schemaVersion;
  final String sessionId;
  final String state;
  final String phase;
  final bool isClosed;
  final String? activeTurnId;
  final String? activeGenerationId;
  final int queueDepth;
  final int activeGenerationCount;
  final String? lastTerminalEventType;
  final String? lastTerminalTurnId;
  final String? lastTerminalGenerationId;
  final String? lastTerminalOutcome;
  final String? lastTerminalPublicErrorCode;
  final bool lastTerminalRetryable;
  final String? lastTerminalRecoveryAction;
  final String? lastSafeErrorCode;
  final int staleCompletionCount;
  final int duplicateTerminalCount;
  final int overflowCount;

  factory FrameworkV600RealtimeDiagnosticsSnapshot.fromJson(
    Map<String, Object?> json,
  ) {
    _requireSchema(json, frameworkV600DiagnosticsSchema);
    return FrameworkV600RealtimeDiagnosticsSnapshot(
      sessionId: _sessionId(json['session_id']),
      state: _boundedString(json['state'], 'invalid_diagnostics'),
      phase: _boundedString(json['phase'], 'invalid_diagnostics'),
      isClosed: _bool(json['is_closed'], 'invalid_diagnostics'),
      activeTurnId: _optionalTurnId(json['active_turn_id']),
      activeGenerationId: _optionalGenerationId(json['active_generation_id']),
      queueDepth: _nonNegativeInt(json['queue_depth'], 'invalid_diagnostics'),
      activeGenerationCount: _nonNegativeInt(
        json['active_generation_count'],
        'invalid_diagnostics',
      ),
      lastTerminalEventType: _optionalBoundedString(
        json['last_terminal_event_type'],
      ),
      lastTerminalTurnId: _optionalTurnId(json['last_terminal_turn_id']),
      lastTerminalGenerationId: _optionalGenerationId(
        json['last_terminal_generation_id'],
      ),
      lastTerminalOutcome: _optionalBoundedString(
        json['last_terminal_outcome'],
      ),
      lastTerminalPublicErrorCode: _optionalBoundedString(
        json['last_terminal_public_error_code'],
      ),
      lastTerminalRetryable: _bool(
        json['last_terminal_retryable'],
        'invalid_diagnostics',
      ),
      lastTerminalRecoveryAction: _optionalBoundedString(
        json['last_terminal_recovery_action'],
      ),
      lastSafeErrorCode: _optionalBoundedString(json['last_safe_error_code']),
      staleCompletionCount: _nonNegativeInt(
        json['stale_completion_count'],
        'invalid_diagnostics',
      ),
      duplicateTerminalCount: _nonNegativeInt(
        json['duplicate_terminal_count'],
        'invalid_diagnostics',
      ),
      overflowCount: _nonNegativeInt(
        json['overflow_count'],
        'invalid_diagnostics',
      ),
    );
  }
}

Map<String, Object?> _map(Object? value, String code) {
  if (value is Map<String, Object?>) {
    return value;
  }
  if (value is Map) {
    return value.map((key, value) => MapEntry(key.toString(), value));
  }
  throw _problem(code, 'The response was invalid.');
}

List<Object?> _optionalList(Object? value) {
  if (value == null) {
    return const [];
  }
  if (value is List<Object?>) {
    return value;
  }
  if (value is List) {
    return List<Object?>.from(value);
  }
  throw _problem('invalid_response', 'The response was invalid.');
}

bool _bool(Object? value, String code) {
  if (value is bool) {
    return value;
  }
  throw _problem(code, 'The response was invalid.');
}

int _int(Object? value, String code) {
  if (value is int) {
    return value;
  }
  throw _problem(code, 'The response was invalid.');
}

int _nonNegativeInt(Object? value, String code) {
  final parsed = _int(value, code);
  if (parsed < 0) {
    throw _problem(code, 'The response was invalid.');
  }
  return parsed;
}

String _boundedString(Object? value, String code) {
  if (value is String && value.runes.length <= 240) {
    return value;
  }
  throw _problem(code, 'The response was invalid.');
}

String? _optionalBoundedString(Object? value) {
  if (value == null) {
    return null;
  }
  return _boundedString(value, 'invalid_response');
}

String _sessionId(Object? value) {
  final parsed = _boundedString(value, 'invalid_session_id');
  if (!_sessionIdPattern.hasMatch(parsed)) {
    throw _problem('invalid_session_id', 'The session id was invalid.');
  }
  return parsed;
}

String? _optionalSessionId(Object? value) => value == null ? null : _sessionId(value);

String? _optionalTurnId(Object? value) {
  if (value == null) {
    return null;
  }
  final parsed = _boundedString(value, 'invalid_turn_id');
  if (!_turnIdPattern.hasMatch(parsed)) {
    throw _problem('invalid_turn_id', 'The turn id was invalid.');
  }
  return parsed;
}

String? _optionalGenerationId(Object? value) {
  if (value == null) {
    return null;
  }
  final parsed = _boundedString(value, 'invalid_generation_id');
  if (!_generationIdPattern.hasMatch(parsed)) {
    throw _problem('invalid_generation_id', 'The generation id was invalid.');
  }
  return parsed;
}

void _requireSchema(Map<String, Object?> json, String expected) {
  if (json['schema_version'] != expected) {
    throw _problem(
      'invalid_schema_version',
      'The response schema version was invalid.',
    );
  }
}

FrameworkV600RealtimeProblemException _problem(String code, String message) {
  return FrameworkV600RealtimeProblemException(
    FrameworkV600RealtimeProblem(
      code: code,
      message: message,
      retryable: false,
    ),
  );
}
