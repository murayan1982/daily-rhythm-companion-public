import 'package:flutter/foundation.dart';

const int characterMotionPresentationMaxCommands = 3;
const int characterMotionPresentationMaxEventTypes = 12;
const int characterMotionPresentationMaxIdChars = 128;
const int characterMotionPresentationMaxExpressionChars = 64;
const int characterMotionPresentationMaxEnumChars = 64;
const int characterMotionPresentationMaxReasonCodeChars = 64;
const int characterMotionPresentationMaxSafeMessageChars = 256;

int _codePointCount(String value) => value.runes.length;

enum CharacterMotionPresentationPhase {
  idle,
  applying,
  completed,
  ignored,
  disabled,
  unavailable,
  failed,
  closed,
}

enum CharacterMotionLifecycleFact {
  idle('idle'),
  listening('listening'),
  transcribing('transcribing'),
  thinking('thinking'),
  responding('responding'),
  ttsPreparing('tts_preparing'),
  speaking('speaking'),
  motionActive('motion_active'),
  interrupted('interrupted'),
  completed('completed'),
  failed('failed'),
  closed('closed'),
  unavailable('unavailable'),
  unknown('unknown');

  const CharacterMotionLifecycleFact(this.wireName);

  final String wireName;

  static CharacterMotionLifecycleFact fromWire(String value) =>
      _enumFromWire<CharacterMotionLifecycleFact>(
        values: CharacterMotionLifecycleFact.values,
        value: value,
        wireName: (item) => item.wireName,
        code: 'invalid_motion_source_fact',
        message: 'The character-motion source fact was not recognized.',
      );
}

enum CharacterMotionCue {
  greeting('greeting'),
  thinking('thinking'),
  happy('happy'),
  tiredSupportive('tired_supportive'),
  speaking('speaking'),
  idle('idle');

  const CharacterMotionCue(this.wireName);

  final String wireName;

  static CharacterMotionCue fromWire(String value) =>
      _enumFromWire<CharacterMotionCue>(
        values: CharacterMotionCue.values,
        value: value,
        wireName: (item) => item.wireName,
        code: 'invalid_motion_cue',
        message: 'The character-motion cue was not recognized.',
      );
}

enum CharacterMotionCommandIntent {
  expression('expression'),
  speakingState('speaking_state'),
  idleMotion('idle_motion'),
  stopMotion('stop_motion'),
  resetExpression('reset_expression');

  const CharacterMotionCommandIntent(this.wireName);

  final String wireName;

  static CharacterMotionCommandIntent fromWire(String value) =>
      _enumFromWire<CharacterMotionCommandIntent>(
        values: CharacterMotionCommandIntent.values,
        value: value,
        wireName: (item) => item.wireName,
        code: 'invalid_motion_command_intent',
        message: 'The character-motion command intent was not recognized.',
      );
}

enum CharacterMotionExecutionStatus {
  completed('completed'),
  ignored('ignored'),
  disabled('disabled'),
  unavailable('unavailable'),
  failed('failed');

  const CharacterMotionExecutionStatus(this.wireName);

  final String wireName;

  static CharacterMotionExecutionStatus fromWire(String value) =>
      _enumFromWire<CharacterMotionExecutionStatus>(
        values: CharacterMotionExecutionStatus.values,
        value: value,
        wireName: (item) => item.wireName,
        code: 'invalid_motion_execution_status',
        message: 'The character-motion execution status was not recognized.',
      );

  CharacterMotionPresentationPhase get presentationPhase {
    switch (this) {
      case CharacterMotionExecutionStatus.completed:
        return CharacterMotionPresentationPhase.completed;
      case CharacterMotionExecutionStatus.ignored:
        return CharacterMotionPresentationPhase.ignored;
      case CharacterMotionExecutionStatus.disabled:
        return CharacterMotionPresentationPhase.disabled;
      case CharacterMotionExecutionStatus.unavailable:
        return CharacterMotionPresentationPhase.unavailable;
      case CharacterMotionExecutionStatus.failed:
        return CharacterMotionPresentationPhase.failed;
    }
  }
}

@immutable
class CharacterMotionPresentationProblem {
  const CharacterMotionPresentationProblem({
    required this.code,
    required this.message,
    required this.retryable,
  });

  final String code;
  final String message;
  final bool retryable;

  @override
  String toString() =>
      'CharacterMotionPresentationProblem(code: $code, retryable: $retryable)';
}

class CharacterMotionPresentationProblemException implements Exception {
  const CharacterMotionPresentationProblemException(this.problem);

  final CharacterMotionPresentationProblem problem;

  @override
  String toString() => problem.toString();
}

@immutable
class CharacterMotionPresentationRequest {
  factory CharacterMotionPresentationRequest({
    required CharacterMotionLifecycleFact sourceFact,
    String? sourceEventType,
    String? sourceSessionId,
    String? sourceTurnId,
    String? characterId,
    String schemaVersion = 'drc.v3.character-motion-presentation-request.1',
  }) {
    if (schemaVersion != 'drc.v3.character-motion-presentation-request.1') {
      _fail(
        'invalid_motion_request_schema',
        'The character-motion request schema was not recognized.',
      );
    }
    return CharacterMotionPresentationRequest._(
      schemaVersion: schemaVersion,
      sourceFact: sourceFact,
      sourceEventType: _optionalBoundedString(
        sourceEventType,
        characterMotionPresentationMaxIdChars,
        'invalid_motion_source_event_type',
      ),
      sourceSessionId: _optionalBoundedString(
        sourceSessionId,
        characterMotionPresentationMaxIdChars,
        'invalid_motion_source_session_id',
      ),
      sourceTurnId: _optionalBoundedString(
        sourceTurnId,
        characterMotionPresentationMaxIdChars,
        'invalid_motion_source_turn_id',
      ),
      characterId: _optionalBoundedString(
        characterId,
        characterMotionPresentationMaxIdChars,
        'invalid_motion_character_id',
      ),
    );
  }

  const CharacterMotionPresentationRequest._({
    required this.schemaVersion,
    required this.sourceFact,
    required this.sourceEventType,
    required this.sourceSessionId,
    required this.sourceTurnId,
    required this.characterId,
  });

  final String schemaVersion;
  final CharacterMotionLifecycleFact sourceFact;
  final String? sourceEventType;
  final String? sourceSessionId;
  final String? sourceTurnId;
  final String? characterId;

  Map<String, Object?> toJson() => <String, Object?>{
    'schema_version': schemaVersion,
    'source_fact': sourceFact.wireName,
    'source_event_type': sourceEventType,
    'source_session_id': sourceSessionId,
    'source_turn_id': sourceTurnId,
    'character_id': characterId,
  };

  @override
  String toString() =>
      'CharacterMotionPresentationRequest(sourceFact: ${sourceFact.wireName})';
}

@immutable
class CharacterMotionPresentationCommandResult {
  const CharacterMotionPresentationCommandResult({
    required this.order,
    required this.intent,
    required this.outcome,
    required this.state,
    required this.adapterStatus,
    required this.publicErrorCode,
    required this.retryable,
    required this.safeMessage,
  });

  final int order;
  final CharacterMotionCommandIntent intent;
  final String outcome;
  final String state;
  final String adapterStatus;
  final String publicErrorCode;
  final bool retryable;
  final String safeMessage;

  factory CharacterMotionPresentationCommandResult.fromJson(
    Map<String, Object?> json,
  ) {
    _rejectUnexpectedKeys(json, const <String>{
      'order',
      'intent',
      'outcome',
      'state',
      'adapter_status',
      'public_error_code',
      'retryable',
      'safe_message',
    }, 'invalid_motion_command_result_shape');
    return CharacterMotionPresentationCommandResult(
      order: _boundedInt(
        json['order'],
        minimum: 1,
        maximum: characterMotionPresentationMaxCommands,
        code: 'invalid_motion_command_order',
      ),
      intent: CharacterMotionCommandIntent.fromWire(
        _requiredBoundedString(
          json['intent'],
          characterMotionPresentationMaxEnumChars,
          'invalid_motion_command_intent',
        ),
      ),
      outcome: _requiredBoundedString(
        json['outcome'],
        characterMotionPresentationMaxEnumChars,
        'invalid_motion_command_outcome',
      ),
      state: _requiredBoundedString(
        json['state'],
        characterMotionPresentationMaxEnumChars,
        'invalid_motion_command_state',
      ),
      adapterStatus: _requiredBoundedString(
        json['adapter_status'],
        characterMotionPresentationMaxEnumChars,
        'invalid_motion_adapter_status',
      ),
      publicErrorCode: _requiredBoundedStringAllowEmpty(
        json['public_error_code'],
        characterMotionPresentationMaxEnumChars,
        'invalid_motion_public_error_code',
      ),
      retryable: _requiredBool(
        json['retryable'],
        'invalid_motion_command_retryable',
      ),
      safeMessage: _requiredBoundedStringAllowEmpty(
        json['safe_message'],
        characterMotionPresentationMaxSafeMessageChars,
        'invalid_motion_command_safe_message',
      ),
    );
  }

  @override
  String toString() =>
      'CharacterMotionPresentationCommandResult(order: $order, intent: ${intent.wireName})';
}

@immutable
class CharacterMotionPresentationResult {
  const CharacterMotionPresentationResult({
    required this.schemaVersion,
    required this.status,
    required this.sourceFact,
    required this.cue,
    required this.sourceEventType,
    required this.sourceSessionId,
    required this.sourceTurnId,
    required this.characterId,
    required this.commandsRequested,
    required this.commandsCompleted,
    required this.commandResults,
    required this.eventTypes,
    required this.frameworkImportAttempted,
    required this.sessionCreated,
    required this.sessionClosed,
    required this.adapter,
    required this.realAdapterEnabled,
    required this.providerExecutionAllowed,
    required this.providerExecutionAttempted,
    required this.networkExecution,
    required this.reasonCode,
    required this.safeMessage,
  });

  final String schemaVersion;
  final CharacterMotionExecutionStatus status;
  final CharacterMotionLifecycleFact sourceFact;
  final CharacterMotionCue? cue;
  final String? sourceEventType;
  final String? sourceSessionId;
  final String? sourceTurnId;
  final String? characterId;
  final int commandsRequested;
  final int commandsCompleted;
  final List<CharacterMotionPresentationCommandResult> commandResults;
  final List<String> eventTypes;
  final bool frameworkImportAttempted;
  final bool sessionCreated;
  final bool sessionClosed;
  final String adapter;
  final bool realAdapterEnabled;
  final bool providerExecutionAllowed;
  final bool providerExecutionAttempted;
  final bool networkExecution;
  final String reasonCode;
  final String safeMessage;

  CharacterMotionPresentationPhase get presentationPhase =>
      status.presentationPhase;

  factory CharacterMotionPresentationResult.fromJson(
    Map<String, Object?> json,
  ) {
    _rejectUnexpectedKeys(json, const <String>{
      'schema_version',
      'status',
      'source_fact',
      'cue',
      'source_event_type',
      'source_session_id',
      'source_turn_id',
      'character_id',
      'commands_requested',
      'commands_completed',
      'command_results',
      'event_types',
      'framework_import_attempted',
      'session_created',
      'session_closed',
      'adapter',
      'real_adapter_enabled',
      'provider_execution_allowed',
      'provider_execution_attempted',
      'network_execution',
      'reason_code',
      'safe_message',
    }, 'invalid_motion_result_shape');

    final schemaVersion = _requiredBoundedString(
      json['schema_version'],
      96,
      'invalid_motion_result_schema',
    );
    if (schemaVersion != 'drc.v3.framework-mock-motion-execution.1') {
      _fail(
        'invalid_motion_result_schema',
        'The character-motion result schema was not recognized.',
      );
    }

    final status = CharacterMotionExecutionStatus.fromWire(
      _requiredBoundedString(
        json['status'],
        characterMotionPresentationMaxEnumChars,
        'invalid_motion_execution_status',
      ),
    );
    final sourceFact = CharacterMotionLifecycleFact.fromWire(
      _requiredBoundedString(
        json['source_fact'],
        characterMotionPresentationMaxEnumChars,
        'invalid_motion_source_fact',
      ),
    );
    final cueText = _optionalBoundedString(
      json['cue'],
      characterMotionPresentationMaxEnumChars,
      'invalid_motion_cue',
    );
    final cue = cueText == null ? null : CharacterMotionCue.fromWire(cueText);
    final commandsRequested = _boundedInt(
      json['commands_requested'],
      minimum: 0,
      maximum: characterMotionPresentationMaxCommands,
      code: 'invalid_motion_commands_requested',
    );
    final commandsCompleted = _boundedInt(
      json['commands_completed'],
      minimum: 0,
      maximum: characterMotionPresentationMaxCommands,
      code: 'invalid_motion_commands_completed',
    );
    final commandResults = _commandResults(json['command_results']);
    final eventTypes = _eventTypes(json['event_types']);
    final frameworkImportAttempted = _requiredBool(
      json['framework_import_attempted'],
      'invalid_motion_framework_import_attempted',
    );
    final sessionCreated = _requiredBool(
      json['session_created'],
      'invalid_motion_session_created',
    );
    final sessionClosed = _requiredBool(
      json['session_closed'],
      'invalid_motion_session_closed',
    );
    final adapter = _requiredBoundedString(
      json['adapter'],
      characterMotionPresentationMaxEnumChars,
      'invalid_motion_adapter',
    );
    final realAdapterEnabled = _requiredBool(
      json['real_adapter_enabled'],
      'invalid_motion_real_adapter_enabled',
    );
    final providerExecutionAllowed = _requiredBool(
      json['provider_execution_allowed'],
      'invalid_motion_provider_execution_allowed',
    );
    final providerExecutionAttempted = _requiredBool(
      json['provider_execution_attempted'],
      'invalid_motion_provider_execution_attempted',
    );
    final networkExecution = _requiredBool(
      json['network_execution'],
      'invalid_motion_network_execution',
    );

    if (adapter != 'mock' ||
        realAdapterEnabled ||
        providerExecutionAllowed ||
        providerExecutionAttempted ||
        networkExecution) {
      _fail(
        'unsafe_motion_execution_flags',
        'The character-motion result did not satisfy the mock-only safety contract.',
      );
    }
    if (commandsCompleted > commandsRequested ||
        commandResults.length > commandsRequested ||
        commandsCompleted > commandResults.length) {
      _fail(
        'invalid_motion_command_counts',
        'The character-motion command counts were inconsistent.',
      );
    }
    final orders = commandResults.map((result) => result.order).toList();
    for (var index = 0; index < orders.length; index += 1) {
      if (orders[index] != index + 1) {
        _fail(
          'invalid_motion_command_order',
          'The character-motion command order was inconsistent.',
        );
      }
    }
    if (status == CharacterMotionExecutionStatus.completed) {
      if (commandsRequested == 0 ||
          commandsCompleted != commandsRequested ||
          commandResults.length != commandsRequested ||
          !frameworkImportAttempted ||
          !sessionCreated ||
          !sessionClosed) {
        _fail(
          'invalid_completed_motion_result',
          'The completed character-motion result was inconsistent.',
        );
      }
    }
    if (status == CharacterMotionExecutionStatus.ignored ||
        status == CharacterMotionExecutionStatus.disabled) {
      if (commandsCompleted != 0 ||
          commandResults.isNotEmpty ||
          frameworkImportAttempted ||
          sessionCreated ||
          sessionClosed) {
        _fail(
          'invalid_inactive_motion_result',
          'The inactive character-motion result was inconsistent.',
        );
      }
    }

    return CharacterMotionPresentationResult(
      schemaVersion: schemaVersion,
      status: status,
      sourceFact: sourceFact,
      cue: cue,
      sourceEventType: _optionalBoundedString(
        json['source_event_type'],
        characterMotionPresentationMaxIdChars,
        'invalid_motion_source_event_type',
      ),
      sourceSessionId: _optionalBoundedString(
        json['source_session_id'],
        characterMotionPresentationMaxIdChars,
        'invalid_motion_source_session_id',
      ),
      sourceTurnId: _optionalBoundedString(
        json['source_turn_id'],
        characterMotionPresentationMaxIdChars,
        'invalid_motion_source_turn_id',
      ),
      characterId: _optionalBoundedString(
        json['character_id'],
        characterMotionPresentationMaxIdChars,
        'invalid_motion_character_id',
      ),
      commandsRequested: commandsRequested,
      commandsCompleted: commandsCompleted,
      commandResults: List.unmodifiable(commandResults),
      eventTypes: List.unmodifiable(eventTypes),
      frameworkImportAttempted: frameworkImportAttempted,
      sessionCreated: sessionCreated,
      sessionClosed: sessionClosed,
      adapter: adapter,
      realAdapterEnabled: realAdapterEnabled,
      providerExecutionAllowed: providerExecutionAllowed,
      providerExecutionAttempted: providerExecutionAttempted,
      networkExecution: networkExecution,
      reasonCode: _requiredBoundedString(
        json['reason_code'],
        characterMotionPresentationMaxReasonCodeChars,
        'invalid_motion_reason_code',
      ),
      safeMessage: _requiredBoundedStringAllowEmpty(
        json['safe_message'],
        characterMotionPresentationMaxSafeMessageChars,
        'invalid_motion_safe_message',
      ),
    );
  }

  @override
  String toString() =>
      'CharacterMotionPresentationResult(status: ${status.wireName}, commandsCompleted: $commandsCompleted)';
}

@immutable
class CharacterMotionPresentationState {
  const CharacterMotionPresentationState({
    required this.phase,
    this.request,
    this.result,
    this.problem,
  });

  const CharacterMotionPresentationState.idle()
    : this(phase: CharacterMotionPresentationPhase.idle);

  final CharacterMotionPresentationPhase phase;
  final CharacterMotionPresentationRequest? request;
  final CharacterMotionPresentationResult? result;
  final CharacterMotionPresentationProblem? problem;

  bool get isApplying => phase == CharacterMotionPresentationPhase.applying;
  bool get isClosed => phase == CharacterMotionPresentationPhase.closed;
  bool get isTerminal =>
      phase == CharacterMotionPresentationPhase.completed ||
      phase == CharacterMotionPresentationPhase.ignored ||
      phase == CharacterMotionPresentationPhase.disabled ||
      phase == CharacterMotionPresentationPhase.unavailable ||
      phase == CharacterMotionPresentationPhase.failed ||
      phase == CharacterMotionPresentationPhase.closed;

  @override
  String toString() =>
      'CharacterMotionPresentationState(phase: ${phase.name}, problemCode: ${problem?.code})';
}

T _enumFromWire<T>({
  required List<T> values,
  required String value,
  required String Function(T value) wireName,
  required String code,
  required String message,
}) {
  for (final item in values) {
    if (wireName(item) == value) {
      return item;
    }
  }
  _fail(code, message);
}

Never _fail(String code, String message, {bool retryable = false}) {
  throw CharacterMotionPresentationProblemException(
    CharacterMotionPresentationProblem(
      code: code,
      message: message,
      retryable: retryable,
    ),
  );
}

void _rejectUnexpectedKeys(
  Map<String, Object?> json,
  Set<String> allowed,
  String code,
) {
  if (json.keys.any((key) => !allowed.contains(key))) {
    _fail(code, 'The character-motion response shape was invalid.');
  }
}

String _requiredBoundedString(Object? value, int maximum, String code) {
  if (value is! String || value.isEmpty || _codePointCount(value) > maximum) {
    _fail(code, 'A character-motion text field was invalid.');
  }
  return value;
}

String _requiredBoundedStringAllowEmpty(
  Object? value,
  int maximum,
  String code,
) {
  if (value is! String || _codePointCount(value) > maximum) {
    _fail(code, 'A character-motion text field was invalid.');
  }
  return value;
}

String? _optionalBoundedString(Object? value, int maximum, String code) {
  if (value == null) {
    return null;
  }
  if (value is! String || value.isEmpty || _codePointCount(value) > maximum) {
    _fail(code, 'A character-motion optional text field was invalid.');
  }
  return value;
}

bool _requiredBool(Object? value, String code) {
  if (value is! bool) {
    _fail(code, 'A character-motion boolean field was invalid.');
  }
  return value;
}

int _boundedInt(
  Object? value, {
  required int minimum,
  required int maximum,
  required String code,
}) {
  if (value is! int || value < minimum || value > maximum) {
    _fail(code, 'A character-motion numeric field was invalid.');
  }
  return value;
}

List<CharacterMotionPresentationCommandResult> _commandResults(Object? value) {
  if (value is! List || value.length > characterMotionPresentationMaxCommands) {
    _fail(
      'invalid_motion_command_results',
      'The character-motion command results were invalid.',
    );
  }
  return value.map((item) {
    if (item is! Map) {
      _fail(
        'invalid_motion_command_results',
        'The character-motion command results were invalid.',
      );
    }
    return CharacterMotionPresentationCommandResult.fromJson(
      Map<String, Object?>.from(item),
    );
  }).toList();
}

List<String> _eventTypes(Object? value) {
  if (value is! List ||
      value.length > characterMotionPresentationMaxEventTypes) {
    _fail(
      'invalid_motion_event_types',
      'The character-motion event types were invalid.',
    );
  }
  final result = <String>[];
  for (final item in value) {
    final text = _requiredBoundedString(
      item,
      characterMotionPresentationMaxEnumChars,
      'invalid_motion_event_type',
    );
    result.add(text);
  }
  return result;
}
