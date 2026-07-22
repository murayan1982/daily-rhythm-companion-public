import 'demo_status.dart';

class VoiceOutputDemoProbeCheck {
  const VoiceOutputDemoProbeCheck({
    required this.name,
    required this.status,
    required this.message,
  });

  final String name;
  final String status;
  final String message;

  factory VoiceOutputDemoProbeCheck.fromJson(Map<String, dynamic> json) {
    return VoiceOutputDemoProbeCheck(
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

class VoiceOutputDemoRequestResponse {
  const VoiceOutputDemoRequestResponse({
    required this.accepted,
    required this.requestState,
    required this.engine,
    required this.mode,
    required this.adapterMode,
    required this.realTtsEnabled,
    required this.outputMode,
    required this.capability,
    required this.message,
    required this.frameworkCallState,
    required this.audioPlaybackStatus,
    required this.evidenceStatus,
    this.clientEventId,
    this.textContent,
    this.characterId,
    this.voiceProfileId,
    this.requestedAudioFormat,
    this.utterancePurpose,
    this.frameworkApiName,
    this.audioUrl,
    this.audioArtifactRef,
    this.audioFormat,
    this.audioReady = false,
    this.audioHandoffKind = 'none',
    this.hasAudioHandoff = false,
    this.isGenerated = false,
    this.requestWarnings = const <String>[],
    this.runtimeNotes = const <String>[],
    this.checks = const <VoiceOutputDemoProbeCheck>[],
    this.candidatePaths = const <String>[],
    this.publicApiCandidates = const <String>[],
  });

  final bool accepted;
  final String requestState;
  final String engine;
  final String mode;
  final String adapterMode;
  final bool realTtsEnabled;
  final String outputMode;
  final String? clientEventId;
  final String? textContent;
  final String? characterId;
  final String? voiceProfileId;
  final String? requestedAudioFormat;
  final String? utterancePurpose;
  final String frameworkCallState;
  final String? frameworkApiName;
  final String? audioUrl;
  final String? audioArtifactRef;
  final String? audioFormat;
  final bool audioReady;
  final String audioHandoffKind;
  final bool hasAudioHandoff;
  final bool isGenerated;
  final String audioPlaybackStatus;
  final String evidenceStatus;
  final List<String> requestWarnings;
  final List<String> runtimeNotes;
  final DemoCapabilityStatus capability;
  final String message;
  final List<VoiceOutputDemoProbeCheck> checks;
  final List<String> candidatePaths;
  final List<String> publicApiCandidates;

  factory VoiceOutputDemoRequestResponse.fromJson(Map<String, dynamic> json) {
    final checksJson = json['checks'];
    final candidatePathsJson = json['candidate_paths'];
    final publicApiCandidatesJson = json['public_api_candidates'];
    final requestWarningsJson = json['request_warnings'];
    final runtimeNotesJson = json['runtime_notes'];
    final capabilityJson = json['capability'];

    return VoiceOutputDemoRequestResponse(
      accepted: json['accepted'] == true,
      requestState: _stringFromJson(json['request_state'], fallback: 'unknown'),
      engine: _stringFromJson(json['engine'], fallback: 'unknown'),
      mode: _stringFromJson(json['mode'], fallback: 'unknown'),
      adapterMode: _stringFromJson(json['adapter_mode'], fallback: 'unknown'),
      realTtsEnabled: json['real_tts_enabled'] == true,
      outputMode: _stringFromJson(json['output_mode'], fallback: 'unknown'),
      clientEventId: _nullableStringFromJson(json['client_event_id']),
      textContent: _nullableStringFromJson(json['text_content']),
      characterId: _nullableStringFromJson(json['character_id']),
      voiceProfileId: _nullableStringFromJson(json['voice_profile_id']),
      requestedAudioFormat:
          _nullableStringFromJson(json['requested_audio_format']),
      utterancePurpose: _nullableStringFromJson(json['utterance_purpose']),
      frameworkCallState: _stringFromJson(
        json['framework_call_state'],
        fallback: 'not_called',
      ),
      frameworkApiName: _nullableStringFromJson(json['framework_api_name']),
      audioUrl: _nullableStringFromJson(json['audio_url']),
      audioArtifactRef: _nullableStringFromJson(json['audio_artifact_ref']),
      audioFormat: _nullableStringFromJson(json['audio_format']),
      audioReady: json['audio_ready'] == true,
      audioHandoffKind: _stringFromJson(
        json['audio_handoff_kind'],
        fallback: 'none',
      ),
      hasAudioHandoff: json['has_audio_handoff'] == true,
      isGenerated: json['is_generated'] == true,
      audioPlaybackStatus: _stringFromJson(
        json['audio_playback_status'],
        fallback: 'not_started',
      ),
      evidenceStatus: _stringFromJson(
        json['evidence_status'],
        fallback: 'not_evidence',
      ),
      requestWarnings: requestWarningsJson is List
          ? requestWarningsJson.map((item) => item.toString()).toList()
          : const <String>[],
      runtimeNotes: runtimeNotesJson is List
          ? runtimeNotesJson.map((item) => item.toString()).toList()
          : const <String>[],
      capability: DemoCapabilityStatus.fromJson(
        capabilityJson is Map
            ? Map<String, dynamic>.from(capabilityJson)
            : const <String, dynamic>{},
      ),
      message: _stringFromJson(json['message']),
      checks: checksJson is List
          ? checksJson
              .whereType<Map>()
              .map((item) => VoiceOutputDemoProbeCheck.fromJson(
                    Map<String, dynamic>.from(item),
                  ))
              .toList()
          : const <VoiceOutputDemoProbeCheck>[],
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
  String get displayRealTtsGate => realTtsEnabled ? 'enabled' : 'disabled';
  String get displayOutputMode => outputMode.replaceAll('_', ' ');
  String get displayCharacterId => _displayOptional(characterId);
  String get displayVoiceProfileId => _displayOptional(voiceProfileId);
  String get displayRequestedAudioFormat => _displayOptional(requestedAudioFormat);
  String get displayUtterancePurpose => _displayOptional(utterancePurpose);
  String get displayFrameworkCallState => frameworkCallState.replaceAll('_', ' ');
  String get displayFrameworkApiName => _displayOptional(frameworkApiName);
  String get displayAudioFormat => _displayOptional(audioFormat);
  String get displayAudioReady => audioReady ? 'ready' : 'not ready';
  String get displayAudioHandoffKind => audioHandoffKind.replaceAll('_', ' ');
  String get displayHasAudioHandoff => hasAudioHandoff ? 'yes' : 'no';
  String get displayIsGenerated => isGenerated ? 'generated' : 'not generated';
  String get displayAudioUrl => _displayHandoffPresence(
        audioUrl,
        presentLabel: 'available (URL hidden)',
      );
  String get displayAudioArtifactRef => _displayHandoffPresence(
        audioArtifactRef,
        presentLabel: 'available (ref hidden)',
      );
  String get displayAudioPlaybackStatus => audioPlaybackStatus.replaceAll('_', ' ');
  String get displayEvidenceStatus => evidenceStatus.replaceAll('_', ' ');

  String get displayTextContent {
    final text = textContent?.trim();
    if (text == null || text.isEmpty) {
      return '-';
    }

    if (text.length <= 120) {
      return text;
    }

    return '${text.substring(0, 120)}...';
  }

  static String _displayOptional(String? value) {
    final text = value?.trim();
    return text == null || text.isEmpty ? '-' : text;
  }

  static String _displayHandoffPresence(
    String? value, {
    required String presentLabel,
  }) {
    final text = value?.trim();
    return text == null || text.isEmpty ? 'not present' : presentLabel;
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
