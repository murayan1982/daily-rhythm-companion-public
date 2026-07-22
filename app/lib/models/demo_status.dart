class DemoCapabilityStatus {
  const DemoCapabilityStatus({
    required this.status,
    required this.source,
    required this.message,
  });

  final String status;
  final String source;
  final String message;

  factory DemoCapabilityStatus.fromJson(Map<String, dynamic> json) {
    return DemoCapabilityStatus(
      status: _stringFromJson(json['status'], fallback: 'unavailable'),
      source: _stringFromJson(json['source'], fallback: 'unknown'),
      message: _stringFromJson(json['message']),
    );
  }

  String get displayStatus {
    switch (status) {
      case 'available':
        return 'available';
      case 'unavailable':
        return 'unavailable';
      case 'skipped':
        return 'skipped';
      case 'fallback':
        return 'fallback';
      case 'unknown':
      case '':
        return 'unknown';
      default:
        return status;
    }
  }

  String get displaySource {
    switch (source) {
      case 'not_implemented':
        return 'not implemented';
      case 'not_configured':
        return 'not configured';
      case 'framework_config_missing':
        return 'framework config missing';
      case 'framework_config_invalid':
        return 'framework config invalid';
      case 'framework_adapter_unsupported':
        return 'framework adapter unsupported';
      case 'voice_input_adapter_unsupported':
        return 'voice input adapter unsupported';
      case 'framework_voice_input_public_boundary_missing':
        return 'framework voice input public boundary missing';
      case 'framework_voice_input_adapter_not_wired':
        return 'framework voice input adapter not wired';
      case 'framework_voice_input_boundary_missing':
        return 'framework voice input boundary missing';
      case 'voice_output_adapter_unsupported':
        return 'voice output adapter unsupported';
      case 'framework_voice_output_public_boundary_missing':
        return 'framework voice output public boundary missing';
      case 'framework_voice_output_adapter_not_wired':
        return 'framework voice output adapter not wired';
      case 'framework_voice_output_runtime_enabled':
        return 'framework voice output runtime enabled';
      case 'real_tts_runtime_disabled':
        return 'real TTS runtime disabled';
      case 'framework_voice_output_boundary_missing':
        return 'framework voice output boundary missing';
      case 'mock_sleep_provider':
        return 'mock sleep provider';
      case 'sleep_provider_not_google_health':
        return 'sleep provider not Google Health';
      case 'google_health_real_api_disabled':
        return 'Google Health real API disabled';
      case 'google_health_real_api_blocked':
        return 'Google Health real API blocked';
      case 'google_health_real_api_guarded':
        return 'Google Health real API guarded';
      case 'unsupported_engine':
        return 'unsupported engine';
      case 'mock':
      case 'framework':
      case 'unknown':
      case '':
        return source.isEmpty ? 'unknown' : source;
      default:
        return source;
    }
  }

  static String _stringFromJson(Object? value, {String fallback = ''}) {
    final text = value?.toString().trim();
    return text == null || text.isEmpty ? fallback : text;
  }
}

class DemoStatus {
  const DemoStatus({
    required this.engine,
    required this.mode,
    required this.capabilities,
  });

  final String engine;
  final String mode;
  final Map<String, DemoCapabilityStatus> capabilities;

  factory DemoStatus.fromJson(Map<String, dynamic> json) {
    return DemoStatus(
      engine: _stringFromJson(json['engine'], fallback: 'unknown'),
      mode: _stringFromJson(json['mode'], fallback: 'unknown'),
      capabilities: _capabilitiesFromJson(json['capabilities']),
    );
  }

  String get displayEngine {
    switch (engine) {
      case 'mock':
        return 'mock';
      case 'framework':
        return 'framework';
      case 'unsupported':
      case 'unknown':
      case '':
        return engine.isEmpty ? 'unknown' : engine;
      default:
        return engine;
    }
  }

  String get displayMode {
    switch (mode) {
      case 'mock_safe':
        return 'mock safe';
      case 'framework_local':
        return 'framework local';
      case 'mock':
      case 'unsupported':
      case 'unknown':
      case '':
        return mode.isEmpty ? 'unknown' : mode;
      default:
        return mode;
    }
  }

  DemoCapabilityStatus capability(String key) {
    return capabilities[key] ??
        const DemoCapabilityStatus(
          status: 'unknown',
          source: 'unknown',
          message: 'Capability status was not returned by the backend.',
        );
  }

  static String displayCapabilityName(String key) {
    switch (key) {
      case 'llm_response':
        return 'LLM response';
      case 'voice_input':
        return 'Voice input';
      case 'voice_output':
        return 'Voice output';
      case 'live2d_motion':
        return 'Live2D motion';
      case 'google_health_real_api':
        return 'Google Health real API';
      default:
        return key;
    }
  }

  static List<String> get orderedCapabilityKeys {
    return const [
      'llm_response',
      'voice_input',
      'voice_output',
      'live2d_motion',
      'google_health_real_api',
    ];
  }

  static Map<String, DemoCapabilityStatus> _capabilitiesFromJson(
    Object? value,
  ) {
    if (value is! Map) {
      return const <String, DemoCapabilityStatus>{};
    }

    final rawCapabilities = Map<Object?, Object?>.from(value);

    return rawCapabilities.map<String, DemoCapabilityStatus>((key, item) {
      final capabilityJson = item is Map
          ? Map<String, dynamic>.from(item)
          : const <String, dynamic>{};
      return MapEntry(
        key.toString(),
        DemoCapabilityStatus.fromJson(capabilityJson),
      );
    });
  }

  static String _stringFromJson(Object? value, {String fallback = ''}) {
    final text = value?.toString().trim();
    return text == null || text.isEmpty ? fallback : text;
  }
}
