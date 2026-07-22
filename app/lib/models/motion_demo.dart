import 'demo_status.dart';

class MotionDemoBoundaryProbeSummary {
  const MotionDemoBoundaryProbeSummary({
    this.frameworkRoot,
    required this.frameworkRootExists,
    this.candidatePaths = const <String>[],
    this.publicApiCandidates = const <String>[],
    this.notes = const <String>[],
  });

  final String? frameworkRoot;
  final bool frameworkRootExists;
  final List<String> candidatePaths;
  final List<String> publicApiCandidates;
  final List<String> notes;

  factory MotionDemoBoundaryProbeSummary.fromJson(Map<String, dynamic> json) {
    return MotionDemoBoundaryProbeSummary(
      frameworkRoot: _nullableStringFromJson(json['framework_root']),
      frameworkRootExists: json['framework_root_exists'] == true,
      candidatePaths: _stringListFromJson(json['candidate_paths']),
      publicApiCandidates: _stringListFromJson(json['public_api_candidates']),
      notes: _stringListFromJson(json['notes']),
    );
  }

  String get displayFrameworkRoot => _displayOptional(frameworkRoot);
  String get displayFrameworkRootExists => frameworkRootExists ? 'yes' : 'no';

  static String _displayOptional(String? value) {
    final text = value?.trim();
    return text == null || text.isEmpty ? '-' : text;
  }

  static String? _nullableStringFromJson(Object? value) {
    final text = value?.toString().trim();
    return text == null || text.isEmpty ? null : text;
  }

  static List<String> _stringListFromJson(Object? value) {
    if (value is! List) {
      return const <String>[];
    }
    return value.map((item) => item.toString()).toList();
  }
}

class MotionDemoRequestResponse {
  const MotionDemoRequestResponse({
    required this.accepted,
    required this.requestState,
    required this.engine,
    required this.mode,
    required this.adapterMode,
    required this.motionEvent,
    this.clientEventId,
    this.characterId,
    this.expressionId,
    required this.triggerSource,
    this.requestedAdapterMode,
    required this.resolvedAdapterMode,
    required this.motionSent,
    required this.vtsConnectionUsed,
    this.requestWarnings = const <String>[],
    required this.message,
    required this.capability,
    this.supportedMotionEvents = const <String>[],
    this.supportedCharacterIds = const <String>[],
    this.supportedExpressionIds = const <String>[],
    this.frameworkProbe,
  });

  final bool accepted;
  final String requestState;
  final String engine;
  final String mode;
  final String adapterMode;
  final String motionEvent;
  final String? clientEventId;
  final String? characterId;
  final String? expressionId;
  final String triggerSource;
  final String? requestedAdapterMode;
  final String resolvedAdapterMode;
  final bool motionSent;
  final bool vtsConnectionUsed;
  final List<String> requestWarnings;
  final String message;
  final DemoCapabilityStatus capability;
  final List<String> supportedMotionEvents;
  final List<String> supportedCharacterIds;
  final List<String> supportedExpressionIds;
  final MotionDemoBoundaryProbeSummary? frameworkProbe;

  factory MotionDemoRequestResponse.fromJson(Map<String, dynamic> json) {
    final capabilityJson = json['capability'];
    final frameworkProbeJson = json['framework_probe'];

    return MotionDemoRequestResponse(
      accepted: json['accepted'] == true,
      requestState: _stringFromJson(json['request_state'], fallback: 'unknown'),
      engine: _stringFromJson(json['engine'], fallback: 'unknown'),
      mode: _stringFromJson(json['mode'], fallback: 'unknown'),
      adapterMode: _stringFromJson(json['adapter_mode'], fallback: 'unknown'),
      motionEvent: _stringFromJson(json['motion_event'], fallback: 'idle'),
      clientEventId: _nullableStringFromJson(json['client_event_id']),
      characterId: _nullableStringFromJson(json['character_id']),
      expressionId: _nullableStringFromJson(json['expression_id']),
      triggerSource: _stringFromJson(json['trigger_source'], fallback: 'manual'),
      requestedAdapterMode:
          _nullableStringFromJson(json['requested_adapter_mode']),
      resolvedAdapterMode:
          _stringFromJson(json['resolved_adapter_mode'], fallback: 'disabled'),
      motionSent: json['motion_sent'] == true,
      vtsConnectionUsed: json['vts_connection_used'] == true,
      requestWarnings: _stringListFromJson(json['request_warnings']),
      message: _stringFromJson(json['message']),
      capability: DemoCapabilityStatus.fromJson(
        capabilityJson is Map
            ? Map<String, dynamic>.from(capabilityJson)
            : const <String, dynamic>{},
      ),
      supportedMotionEvents: _stringListFromJson(json['supported_motion_events']),
      supportedCharacterIds: _stringListFromJson(json['supported_character_ids']),
      supportedExpressionIds: _stringListFromJson(json['supported_expression_ids']),
      frameworkProbe: frameworkProbeJson is Map
          ? MotionDemoBoundaryProbeSummary.fromJson(
              Map<String, dynamic>.from(frameworkProbeJson),
            )
          : null,
    );
  }

  String get displayAccepted => accepted ? 'accepted' : 'not accepted';
  String get displayRequestState => requestState.replaceAll('_', ' ');
  String get displayEngine => engine.replaceAll('_', ' ');
  String get displayMode => mode.replaceAll('_', ' ');
  String get displayAdapterMode => adapterMode.replaceAll('_', ' ');
  String get displayMotionEvent => motionEvent.replaceAll('_', ' ');
  String get displayCharacterId => _displayOptional(characterId);
  String get displayExpressionId => _displayOptional(expressionId);
  String get displayTriggerSource => triggerSource.replaceAll('_', ' ');
  String get displayRequestedAdapterMode => _displayOptional(requestedAdapterMode);
  String get displayResolvedAdapterMode => resolvedAdapterMode.replaceAll('_', ' ');
  String get displayMotionSent => motionSent ? 'yes' : 'no';
  String get displayVtsConnectionUsed => vtsConnectionUsed ? 'yes' : 'no';

  static String _displayOptional(String? value) {
    final text = value?.trim();
    return text == null || text.isEmpty ? '-' : text.replaceAll('_', ' ');
  }

  static String _stringFromJson(Object? value, {String fallback = ''}) {
    final text = value?.toString().trim();
    return text == null || text.isEmpty ? fallback : text;
  }

  static String? _nullableStringFromJson(Object? value) {
    final text = value?.toString().trim();
    return text == null || text.isEmpty ? null : text;
  }

  static List<String> _stringListFromJson(Object? value) {
    if (value is! List) {
      return const <String>[];
    }
    return value.map((item) => item.toString()).toList();
  }
}
