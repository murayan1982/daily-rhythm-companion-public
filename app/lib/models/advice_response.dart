import 'advice_source.dart';

class AdviceResponse {
  const AdviceResponse({
    required this.message,
    required this.characterName,
    this.source,
  });

  final String message;
  final String characterName;
  final AdviceSource? source;

  factory AdviceResponse.fromJson(Map<String, dynamic> json) {
    final sourceJson = json['source'];

    return AdviceResponse(
      message: json['message']?.toString() ?? '',
      characterName: json['character_name']?.toString() ?? '',
      source: sourceJson is Map
          ? AdviceSource.fromJson(Map<String, dynamic>.from(sourceJson))
          : null,
    );
  }
}
