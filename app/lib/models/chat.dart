import 'advice_source.dart';
import 'character_preset.dart';

class PostAdviceChatContext {
  const PostAdviceChatContext({
    required this.character,
    required this.adviceMessage,
    this.mood,
    this.adviceBasis,
    this.adviceSource,
    this.reportHandoff,
    this.dailyRecordId,
  });

  final CharacterPreset character;
  final String adviceMessage;
  final String? mood;
  final String? adviceBasis;
  final AdviceSource? adviceSource;
  final Object? reportHandoff;
  final String? dailyRecordId;

  factory PostAdviceChatContext.fromJson(Map<String, dynamic> json) {
    return PostAdviceChatContext(
      character: CharacterPreset.fromJson(
        json['character'] is Map
            ? Map<String, dynamic>.from(json['character'] as Map)
            : {},
      ),
      adviceMessage: json['advice_message']?.toString() ?? '',
      mood: _optionalString(json['mood']),
      adviceBasis: _optionalString(json['advice_basis']),
      adviceSource: json['advice_source'] is Map
          ? AdviceSource.fromJson(
              Map<String, dynamic>.from(json['advice_source'] as Map),
            )
          : null,
      reportHandoff: json['report_handoff'],
      dailyRecordId: _optionalString(json['daily_record_id']),
    );
  }
}

class ChatMessage {
  const ChatMessage({
    required this.role,
    required this.content,
  });

  final String role;
  final String content;

  factory ChatMessage.fromJson(Map<String, dynamic> json) {
    return ChatMessage(
      role: json['role']?.toString() ?? '',
      content: json['content']?.toString() ?? '',
    );
  }

  String get displayRole {
    switch (role) {
      case 'assistant':
        return 'キャラクター';
      case 'user':
        return 'あなた';
      default:
        return role.isEmpty ? '-' : role;
    }
  }
}

class ChatSource {
  const ChatSource({
    required this.engine,
    required this.mode,
    required this.drcCharacterId,
    required this.drcCharacterName,
    this.frameworkPreset,
    this.frameworkCharacter,
    this.frameworkCharacterSource,
  });

  final String engine;
  final String mode;
  final String drcCharacterId;
  final String drcCharacterName;
  final String? frameworkPreset;
  final String? frameworkCharacter;
  final String? frameworkCharacterSource;

  factory ChatSource.fromJson(Map<String, dynamic> json) {
    return ChatSource(
      engine: json['engine']?.toString() ?? '',
      mode: json['mode']?.toString() ?? '',
      drcCharacterId: json['drc_character_id']?.toString() ?? '',
      drcCharacterName: json['drc_character_name']?.toString() ?? '',
      frameworkPreset: _optionalString(json['framework_preset']),
      frameworkCharacter: _optionalString(json['framework_character']),
      frameworkCharacterSource: _optionalString(
        json['framework_character_source'],
      ),
    );
  }

  String get displayLabel {
    final engineLabel = engine.isEmpty ? '-' : engine;
    final modeLabel = mode.isEmpty ? '-' : mode;
    return '$engineLabel / $modeLabel';
  }
}

class ChatSession {
  const ChatSession({
    required this.sessionId,
    required this.status,
    required this.source,
    required this.context,
    required this.messages,
  });

  final String sessionId;
  final String status;
  final ChatSource source;
  final PostAdviceChatContext context;
  final List<ChatMessage> messages;

  factory ChatSession.fromJson(Map<String, dynamic> json) {
    return ChatSession(
      sessionId: json['session_id']?.toString() ?? '',
      status: json['status']?.toString() ?? '',
      source: ChatSource.fromJson(
        json['source'] is Map
            ? Map<String, dynamic>.from(json['source'] as Map)
            : {},
      ),
      context: PostAdviceChatContext.fromJson(
        json['context'] is Map
            ? Map<String, dynamic>.from(json['context'] as Map)
            : {},
      ),
      messages: _parseMessages(json['messages']),
    );
  }

  static List<ChatMessage> _parseMessages(dynamic value) {
    if (value is! List) {
      return const [];
    }

    return value
        .whereType<Map>()
        .map((item) => ChatMessage.fromJson(Map<String, dynamic>.from(item)))
        .toList();
  }
}

class ChatMessageResponse {
  const ChatMessageResponse({
    required this.sessionId,
    required this.reply,
    required this.source,
    required this.messages,
  });

  final String sessionId;
  final ChatMessage reply;
  final ChatSource source;
  final List<ChatMessage> messages;

  factory ChatMessageResponse.fromJson(Map<String, dynamic> json) {
    return ChatMessageResponse(
      sessionId: json['session_id']?.toString() ?? '',
      reply: ChatMessage.fromJson(
        json['reply'] is Map
            ? Map<String, dynamic>.from(json['reply'] as Map)
            : {},
      ),
      source: ChatSource.fromJson(
        json['source'] is Map
            ? Map<String, dynamic>.from(json['source'] as Map)
            : {},
      ),
      messages: ChatSession._parseMessages(json['messages']),
    );
  }
}

String? _optionalString(dynamic value) {
  final text = value?.toString().trim();

  if (text == null || text.isEmpty) {
    return null;
  }

  return text;
}
