import 'report_handoff_context.dart';

class AdviceSource {
  const AdviceSource({
    required this.engine,
    required this.drcCharacterId,
    required this.drcCharacterName,
    this.frameworkPreset,
    this.frameworkCharacter,
    this.frameworkCharacterSource,
    this.reportHandoff,
  });

  final String engine;
  final String drcCharacterId;
  final String drcCharacterName;
  final String? frameworkPreset;
  final String? frameworkCharacter;
  final String? frameworkCharacterSource;
  final ReportHandoffContext? reportHandoff;

  factory AdviceSource.fromJson(Map<String, dynamic> json) {
    return AdviceSource(
      engine: json['engine']?.toString() ?? '',
      drcCharacterId: json['drc_character_id']?.toString() ?? '',
      drcCharacterName: json['drc_character_name']?.toString() ?? '',
      frameworkPreset: _optionalString(json['framework_preset']),
      frameworkCharacter: _optionalString(json['framework_character']),
      frameworkCharacterSource: _optionalString(
        json['framework_character_source'],
      ),
      reportHandoff: _parseReportHandoff(json['report_handoff']),
    );
  }


  Map<String, dynamic> toJson() {
    return {
      'engine': engine,
      'drc_character_id': drcCharacterId,
      'drc_character_name': drcCharacterName,
      'framework_preset': frameworkPreset,
      'framework_character': frameworkCharacter,
      'framework_character_source': frameworkCharacterSource,
      'report_handoff': reportHandoff?.toJson(),
    };
  }

  String get displayEngine {
    switch (engine) {
      case 'mock':
        return 'mock';
      case 'framework':
        return 'framework';
      case 'framework_fallback':
        return 'framework fallback';
      case '':
        return '-';
      default:
        return engine;
    }
  }

  String get displayDrcCharacter {
    final name = drcCharacterName.trim();
    final id = drcCharacterId.trim();

    if (name.isNotEmpty && id.isNotEmpty) {
      return '$name ($id)';
    }

    if (name.isNotEmpty) {
      return name;
    }

    if (id.isNotEmpty) {
      return id;
    }

    return '-';
  }

  String get displayFrameworkPreset {
    return _displayNullable(frameworkPreset);
  }

  String get displayFrameworkCharacter {
    return _displayNullable(frameworkCharacter);
  }

  String get displayFrameworkCharacterSource {
    return _displayNullable(frameworkCharacterSource);
  }

  bool get hasFrameworkMetadata {
    return frameworkPreset != null ||
        frameworkCharacter != null ||
        frameworkCharacterSource != null;
  }

  bool get hasReportHandoff {
    return reportHandoff?.shouldShowAsAdviceContext ?? false;
  }

  String get displayReportHandoffLabel {
    return reportHandoff?.displayAdviceContextLabel ?? '-';
  }

  String get displayReportHandoffSummary {
    return reportHandoff?.displayUserFacingSummary ?? '-';
  }

  String get displayReportHandoffQuality {
    return reportHandoff?.displayQuality ?? '-';
  }

  String get displayReportHandoffSource {
    return reportHandoff?.displaySource ?? '-';
  }

  static ReportHandoffContext? _parseReportHandoff(dynamic value) {
    if (value is Map) {
      return ReportHandoffContext.fromJson(Map<String, dynamic>.from(value));
    }

    return null;
  }

  static String? _optionalString(dynamic value) {
    final text = value?.toString().trim();

    if (text == null || text.isEmpty) {
      return null;
    }

    return text;
  }

  static String _displayNullable(String? value) {
    final text = value?.trim();

    if (text == null || text.isEmpty) {
      return '-';
    }

    return text;
  }
}
