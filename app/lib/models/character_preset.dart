class CharacterPreset {
  const CharacterPreset({
    required this.characterId,
    required this.displayName,
    required this.description,
    required this.personalityType,
    required this.speakingStyle,
    required this.adviceStyle,
  });

  final String characterId;
  final String displayName;
  final String description;
  final String personalityType;
  final String speakingStyle;
  final String adviceStyle;

  factory CharacterPreset.fromJson(Map<String, dynamic> json) {
    return CharacterPreset(
      characterId: json['character_id']?.toString() ?? '',
      displayName: json['display_name']?.toString() ?? '',
      description: json['description']?.toString() ?? '',
      personalityType: json['personality_type']?.toString() ?? '',
      speakingStyle: json['speaking_style']?.toString() ?? '',
      adviceStyle: json['advice_style']?.toString() ?? '',
    );
  }

  Map<String, dynamic> toAdviceJson() {
    return {
      'character_id': characterId,
      'display_name': displayName,
      'personality_type': personalityType,
      'speaking_style': speakingStyle,
      'advice_style': adviceStyle,
    };
  }
}