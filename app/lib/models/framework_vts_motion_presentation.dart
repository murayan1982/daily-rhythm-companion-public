import 'package:flutter/foundation.dart';

const int frameworkVtsMotionMaxIdChars = 128;
const int frameworkVtsMotionMaxEnumChars = 64;
const int frameworkVtsMotionMaxMessageChars = 256;
const int frameworkVtsMotionMaxEventTypes = 16;

int _runes(String value) => value.runes.length;

enum FrameworkVtsMotionPresentationPhase {
  idle,
  applying,
  completed,
  disabled,
  providerExecutionNotAllowed,
  unavailable,
  unsupported,
  failed,
  closed,
}

enum FrameworkVtsMotionIntent {
  expression('expression'),
  emotion('emotion'),
  gesture('gesture'),
  resetExpression('reset_expression'),
  stopMotion('stop_motion');

  const FrameworkVtsMotionIntent(this.wireName);
  final String wireName;

  bool get requiresSelector =>
      this == FrameworkVtsMotionIntent.expression ||
      this == FrameworkVtsMotionIntent.emotion ||
      this == FrameworkVtsMotionIntent.gesture;

  static FrameworkVtsMotionIntent fromWire(String value) {
    for (final item in values) {
      if (item.wireName == value) {
        return item;
      }
    }
    throw const FrameworkVtsMotionPresentationProblemException(
      FrameworkVtsMotionPresentationProblem(
        code: 'invalid_vts_motion_intent',
        message: 'The VTS motion intent was not recognized.',
        retryable: false,
      ),
    );
  }
}

enum FrameworkVtsMotionExecutionStatus {
  completed('completed'),
  completedWithOptionalSkip('completed_with_optional_skip'),
  disabled('disabled'),
  providerExecutionNotAllowed('provider_execution_not_allowed'),
  unavailable('unavailable'),
  unsupported('unsupported'),
  failed('failed');

  const FrameworkVtsMotionExecutionStatus(this.wireName);
  final String wireName;

  static FrameworkVtsMotionExecutionStatus fromWire(String value) {
    for (final item in values) {
      if (item.wireName == value) {
        return item;
      }
    }
    _fail(
      'invalid_vts_execution_status',
      'The VTS execution status was not recognized.',
    );
  }

  FrameworkVtsMotionPresentationPhase get presentationPhase {
    switch (this) {
      case FrameworkVtsMotionExecutionStatus.completed:
      case FrameworkVtsMotionExecutionStatus.completedWithOptionalSkip:
        return FrameworkVtsMotionPresentationPhase.completed;
      case FrameworkVtsMotionExecutionStatus.disabled:
        return FrameworkVtsMotionPresentationPhase.disabled;
      case FrameworkVtsMotionExecutionStatus.providerExecutionNotAllowed:
        return FrameworkVtsMotionPresentationPhase.providerExecutionNotAllowed;
      case FrameworkVtsMotionExecutionStatus.unavailable:
        return FrameworkVtsMotionPresentationPhase.unavailable;
      case FrameworkVtsMotionExecutionStatus.unsupported:
        return FrameworkVtsMotionPresentationPhase.unsupported;
      case FrameworkVtsMotionExecutionStatus.failed:
        return FrameworkVtsMotionPresentationPhase.failed;
    }
  }
}

@immutable
class FrameworkVtsMotionPresentationProblem {
  const FrameworkVtsMotionPresentationProblem({
    required this.code,
    required this.message,
    required this.retryable,
  });
  final String code;
  final String message;
  final bool retryable;
  @override
  String toString() =>
      'FrameworkVtsMotionPresentationProblem(code: $code, retryable: $retryable)';
}

class FrameworkVtsMotionPresentationProblemException implements Exception {
  const FrameworkVtsMotionPresentationProblemException(this.problem);
  final FrameworkVtsMotionPresentationProblem problem;
  @override
  String toString() => problem.toString();
}

@immutable
class FrameworkVtsMotionPresentationRequest {
  factory FrameworkVtsMotionPresentationRequest({
    required FrameworkVtsMotionIntent intent,
    String? selectorValue,
    String? characterId,
    String schemaVersion = 'drc.v3.framework-vts-motion-presentation-request.1',
  }) {
    if (schemaVersion != 'drc.v3.framework-vts-motion-presentation-request.1') {
      _fail(
        'invalid_vts_request_schema',
        'The VTS request schema was not recognized.',
      );
    }
    final selector = _optional(selectorValue, 'invalid_vts_selector');
    if (intent.requiresSelector && selector == null) {
      _fail(
        'missing_vts_selector',
        'The selected VTS intent requires a value.',
      );
    }
    if (!intent.requiresSelector && selector != null) {
      _fail(
        'unexpected_vts_selector',
        'The selected VTS intent does not accept a value.',
      );
    }
    return FrameworkVtsMotionPresentationRequest._(
      schemaVersion: schemaVersion,
      intent: intent,
      selectorValue: selector,
      characterId: _optional(characterId, 'invalid_vts_character_id'),
    );
  }

  const FrameworkVtsMotionPresentationRequest._({
    required this.schemaVersion,
    required this.intent,
    required this.selectorValue,
    required this.characterId,
  });

  final String schemaVersion;
  final FrameworkVtsMotionIntent intent;
  final String? selectorValue;
  final String? characterId;

  Map<String, Object?> toJson() => <String, Object?>{
    'schema_version': schemaVersion,
    'command': <String, Object?>{
      'order': 1,
      'intent': intent.wireName,
      'expression': intent == FrameworkVtsMotionIntent.expression
          ? selectorValue
          : null,
      'emotion': intent == FrameworkVtsMotionIntent.emotion
          ? selectorValue
          : null,
      'gesture': intent == FrameworkVtsMotionIntent.gesture
          ? selectorValue
          : null,
      'character_id': characterId,
    },
  };

  @override
  String toString() =>
      'FrameworkVtsMotionPresentationRequest(intent: ${intent.wireName})';
}

@immutable
class FrameworkVtsMotionCommandResult {
  const FrameworkVtsMotionCommandResult({
    required this.order,
    required this.intent,
    required this.outcome,
    required this.state,
    required this.adapterStatus,
    required this.publicErrorCode,
    required this.retryable,
    required this.skipped,
    required this.safeMessage,
  });
  final int order;
  final FrameworkVtsMotionIntent intent;
  final String outcome;
  final String state;
  final String adapterStatus;
  final String publicErrorCode;
  final bool retryable;
  final bool skipped;
  final String safeMessage;

  factory FrameworkVtsMotionCommandResult.fromJson(Map<String, Object?> json) {
    _rejectUnexpected(json, const <String>{
      'order',
      'intent',
      'outcome',
      'state',
      'adapter_status',
      'public_error_code',
      'retryable',
      'skipped',
      'safe_message',
    }, 'invalid_vts_command_result_shape');
    return FrameworkVtsMotionCommandResult(
      order: _int(json['order'], 1, 1, 'invalid_vts_command_order'),
      intent: FrameworkVtsMotionIntent.fromWire(
        _string(
          json['intent'],
          frameworkVtsMotionMaxEnumChars,
          'invalid_vts_command_intent',
        ),
      ),
      outcome: _string(
        json['outcome'],
        frameworkVtsMotionMaxEnumChars,
        'invalid_vts_command_outcome',
      ),
      state: _string(
        json['state'],
        frameworkVtsMotionMaxEnumChars,
        'invalid_vts_command_state',
      ),
      adapterStatus: _string(
        json['adapter_status'],
        frameworkVtsMotionMaxEnumChars,
        'invalid_vts_adapter_status',
      ),
      publicErrorCode: _string(
        json['public_error_code'],
        frameworkVtsMotionMaxEnumChars,
        'invalid_vts_public_error',
        allowEmpty: true,
      ),
      retryable: _bool(json['retryable'], 'invalid_vts_retryable'),
      skipped: _bool(json['skipped'], 'invalid_vts_skipped'),
      safeMessage: _string(
        json['safe_message'],
        frameworkVtsMotionMaxMessageChars,
        'invalid_vts_command_message',
        allowEmpty: true,
      ),
    );
  }
}

@immutable
class FrameworkVtsMotionPresentationResult {
  const FrameworkVtsMotionPresentationResult({
    required this.schemaVersion,
    required this.status,
    required this.commandsRequested,
    required this.commandsApplied,
    required this.commandsCompleted,
    required this.optionalCommandsSkipped,
    required this.commandResults,
    required this.eventTypes,
    required this.frameworkImportAttempted,
    required this.sessionCreated,
    required this.sessionClosed,
    required this.adapter,
    required this.realAdapterEnabled,
    required this.providerExecutionAllowed,
    required this.providerExecutionAttempted,
    required this.networkExecutionAttempted,
    required this.realMotionExecuted,
    required this.reasonCode,
    required this.safeMessage,
  });

  final String schemaVersion;
  final FrameworkVtsMotionExecutionStatus status;
  final int commandsRequested;
  final int commandsApplied;
  final int commandsCompleted;
  final int optionalCommandsSkipped;
  final List<FrameworkVtsMotionCommandResult> commandResults;
  final List<String> eventTypes;
  final bool frameworkImportAttempted;
  final bool sessionCreated;
  final bool sessionClosed;
  final String adapter;
  final bool realAdapterEnabled;
  final bool providerExecutionAllowed;
  final bool providerExecutionAttempted;
  final bool networkExecutionAttempted;
  final bool realMotionExecuted;
  final String reasonCode;
  final String safeMessage;

  FrameworkVtsMotionPresentationPhase get presentationPhase =>
      status.presentationPhase;

  factory FrameworkVtsMotionPresentationResult.fromJson(
    Map<String, Object?> json,
  ) {
    _rejectUnexpected(json, const <String>{
      'schema_version',
      'status',
      'commands_requested',
      'commands_applied',
      'commands_completed',
      'optional_commands_skipped',
      'command_results',
      'event_types',
      'framework_import_attempted',
      'session_created',
      'session_closed',
      'adapter',
      'real_adapter_enabled',
      'provider_execution_allowed',
      'provider_execution_attempted',
      'network_execution_attempted',
      'real_motion_executed',
      'reason_code',
      'safe_message',
    }, 'invalid_vts_result_shape');
    final schema = _string(
      json['schema_version'],
      80,
      'invalid_vts_result_schema',
    );
    if (schema != 'drc.v3.framework-vts-motion-execution.1') {
      _fail(
        'invalid_vts_result_schema',
        'The VTS result schema was not recognized.',
      );
    }
    final rawCommands = json['command_results'];
    final rawEvents = json['event_types'];
    if (rawCommands is! List ||
        rawCommands.length > 1 ||
        rawEvents is! List ||
        rawEvents.length > frameworkVtsMotionMaxEventTypes) {
      _fail('invalid_vts_result_shape', 'The VTS result shape was invalid.');
    }
    final commands = rawCommands
        .map((item) {
          if (item is! Map) {
            _fail(
              'invalid_vts_command_result',
              'The VTS command result was invalid.',
            );
          }
          return FrameworkVtsMotionCommandResult.fromJson(
            Map<String, Object?>.from(item),
          );
        })
        .toList(growable: false);
    final events = rawEvents
        .map(
          (item) => _string(
            item,
            frameworkVtsMotionMaxEnumChars,
            'invalid_vts_event_type',
          ),
        )
        .toList(growable: false);
    final adapter = _string(
      json['adapter'],
      frameworkVtsMotionMaxEnumChars,
      'invalid_vts_adapter',
    );
    if (adapter != 'vts') {
      _fail('invalid_vts_adapter', 'The VTS adapter value was invalid.');
    }
    return FrameworkVtsMotionPresentationResult(
      schemaVersion: schema,
      status: FrameworkVtsMotionExecutionStatus.fromWire(
        _string(
          json['status'],
          frameworkVtsMotionMaxEnumChars,
          'invalid_vts_status',
        ),
      ),
      commandsRequested: _int(
        json['commands_requested'],
        0,
        1,
        'invalid_vts_commands_requested',
      ),
      commandsApplied: _int(
        json['commands_applied'],
        0,
        1,
        'invalid_vts_commands_applied',
      ),
      commandsCompleted: _int(
        json['commands_completed'],
        0,
        1,
        'invalid_vts_commands_completed',
      ),
      optionalCommandsSkipped: _int(
        json['optional_commands_skipped'],
        0,
        1,
        'invalid_vts_optional_skips',
      ),
      commandResults: commands,
      eventTypes: events,
      frameworkImportAttempted: _bool(
        json['framework_import_attempted'],
        'invalid_vts_framework_import',
      ),
      sessionCreated: _bool(
        json['session_created'],
        'invalid_vts_session_created',
      ),
      sessionClosed: _bool(
        json['session_closed'],
        'invalid_vts_session_closed',
      ),
      adapter: adapter,
      realAdapterEnabled: _bool(
        json['real_adapter_enabled'],
        'invalid_vts_real_adapter',
      ),
      providerExecutionAllowed: _bool(
        json['provider_execution_allowed'],
        'invalid_vts_provider_allowed',
      ),
      providerExecutionAttempted: _bool(
        json['provider_execution_attempted'],
        'invalid_vts_provider_attempted',
      ),
      networkExecutionAttempted: _bool(
        json['network_execution_attempted'],
        'invalid_vts_network_attempted',
      ),
      realMotionExecuted: _bool(
        json['real_motion_executed'],
        'invalid_vts_real_motion',
      ),
      reasonCode: _string(
        json['reason_code'],
        frameworkVtsMotionMaxEnumChars,
        'invalid_vts_reason',
      ),
      safeMessage: _string(
        json['safe_message'],
        frameworkVtsMotionMaxMessageChars,
        'invalid_vts_message',
        allowEmpty: true,
      ),
    );
  }
}

@immutable
class FrameworkVtsMotionPresentationState {
  const FrameworkVtsMotionPresentationState({
    required this.phase,
    this.request,
    this.result,
    this.problem,
  });
  const FrameworkVtsMotionPresentationState.idle()
    : phase = FrameworkVtsMotionPresentationPhase.idle,
      request = null,
      result = null,
      problem = null;
  final FrameworkVtsMotionPresentationPhase phase;
  final FrameworkVtsMotionPresentationRequest? request;
  final FrameworkVtsMotionPresentationResult? result;
  final FrameworkVtsMotionPresentationProblem? problem;
  bool get isApplying => phase == FrameworkVtsMotionPresentationPhase.applying;
  bool get isClosed => phase == FrameworkVtsMotionPresentationPhase.closed;
}

Never _fail(String code, String message) =>
    throw FrameworkVtsMotionPresentationProblemException(
      FrameworkVtsMotionPresentationProblem(
        code: code,
        message: message,
        retryable: false,
      ),
    );

String? _optional(String? value, String code) {
  if (value == null) {
    return null;
  }
  final trimmed = value.trim();
  if (trimmed.isEmpty || _runes(trimmed) > frameworkVtsMotionMaxIdChars) {
    _fail(code, 'A VTS request value was invalid.');
  }
  return trimmed;
}

String _string(Object? value, int max, String code, {bool allowEmpty = false}) {
  if (value is! String ||
      (!allowEmpty && value.isEmpty) ||
      _runes(value) > max) {
    _fail(code, 'A VTS response value was invalid.');
  }
  return value;
}

bool _bool(Object? value, String code) {
  if (value is! bool) {
    _fail(code, 'A VTS response boolean was invalid.');
  }
  return value;
}

int _int(Object? value, int min, int max, String code) {
  if (value is! int || value < min || value > max) {
    _fail(code, 'A VTS response count was invalid.');
  }
  return value;
}

void _rejectUnexpected(
  Map<String, Object?> json,
  Set<String> allowed,
  String code,
) {
  if (json.keys.any((key) => !allowed.contains(key))) {
    _fail(code, 'The VTS response contained an unexpected field.');
  }
}
