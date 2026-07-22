import 'demo_status.dart';

class VoiceInputDemoProbeCheck {
  const VoiceInputDemoProbeCheck({
    required this.name,
    required this.status,
    required this.message,
  });

  final String name;
  final String status;
  final String message;

  factory VoiceInputDemoProbeCheck.fromJson(Map<String, dynamic> json) {
    return VoiceInputDemoProbeCheck(
      name: _stringFromJson(json['name'], fallback: 'unknown'),
      status: _stringFromJson(json['status'], fallback: 'unknown'),
      message: _stringFromJson(json['message']),
    );
  }

  String get displayName => name.replaceAll('_', ' ');
  String get displayStatus => status.replaceAll('_', ' ');

  static String _stringFromJson(Object? value, {String fallback = ''}) {
    final text = value?.toString().trim();
    return text == null || text.isEmpty ? fallback : text;
  }
}

class VoiceInputDemoRequestResponse {
  const VoiceInputDemoRequestResponse({
    required this.accepted,
    required this.requestState,
    required this.engine,
    required this.mode,
    required this.adapterMode,
    required this.inputMode,
    required this.capability,
    required this.message,
    this.clientEventId,
    this.transcript,
    this.checks = const <VoiceInputDemoProbeCheck>[],
    this.candidatePaths = const <String>[],
    this.publicApiCandidates = const <String>[],
  });

  final bool accepted;
  final String requestState;
  final String engine;
  final String mode;
  final String adapterMode;
  final String inputMode;
  final String? clientEventId;
  final DemoCapabilityStatus capability;
  final String? transcript;
  final String message;
  final List<VoiceInputDemoProbeCheck> checks;
  final List<String> candidatePaths;
  final List<String> publicApiCandidates;

  factory VoiceInputDemoRequestResponse.fromJson(Map<String, dynamic> json) {
    final checksJson = json['checks'];
    final candidatePathsJson = json['candidate_paths'];
    final publicApiCandidatesJson = json['public_api_candidates'];
    final capabilityJson = json['capability'];

    return VoiceInputDemoRequestResponse(
      accepted: json['accepted'] == true,
      requestState: _stringFromJson(json['request_state'], fallback: 'unknown'),
      engine: _stringFromJson(json['engine'], fallback: 'unknown'),
      mode: _stringFromJson(json['mode'], fallback: 'unknown'),
      adapterMode: _stringFromJson(json['adapter_mode'], fallback: 'unknown'),
      inputMode: _stringFromJson(json['input_mode'], fallback: 'unknown'),
      clientEventId: _nullableStringFromJson(json['client_event_id']),
      capability: DemoCapabilityStatus.fromJson(
        capabilityJson is Map
            ? Map<String, dynamic>.from(capabilityJson)
            : const <String, dynamic>{},
      ),
      transcript: _nullableStringFromJson(json['transcript']),
      message: _stringFromJson(json['message']),
      checks: checksJson is List
          ? checksJson
              .whereType<Map>()
              .map((item) => VoiceInputDemoProbeCheck.fromJson(
                    Map<String, dynamic>.from(item),
                  ))
              .toList()
          : const <VoiceInputDemoProbeCheck>[],
      candidatePaths: candidatePathsJson is List
          ? candidatePathsJson.map((item) => item.toString()).toList()
          : const <String>[],
      publicApiCandidates: publicApiCandidatesJson is List
          ? publicApiCandidatesJson.map((item) => item.toString()).toList()
          : const <String>[],
    );
  }

  String get displayAccepted => accepted ? 'accepted' : 'not accepted';
  String get displayRequestState => requestState.replaceAll('_', ' ');
  String get displayEngine => engine.replaceAll('_', ' ');
  String get displayMode => mode.replaceAll('_', ' ');
  String get displayAdapterMode => adapterMode.replaceAll('_', ' ');
  String get displayInputMode => inputMode.replaceAll('_', ' ');
  String get displayTranscript {
    final text = transcript?.trim();
    return text == null || text.isEmpty ? '-' : text;
  }

  static String _stringFromJson(Object? value, {String fallback = ''}) {
    final text = value?.toString().trim();
    return text == null || text.isEmpty ? fallback : text;
  }

  static String? _nullableStringFromJson(Object? value) {
    final text = value?.toString().trim();
    return text == null || text.isEmpty ? null : text;
  }
}
