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

class ChatLifecycle {
  const ChatLifecycle({
    required this.state,
    required this.turnCount,
    required this.turnLimit,
    required this.canSendMessage,
    required this.canRestart,
  });

  final String state;
  final int turnCount;
  final int turnLimit;
  final bool canSendMessage;
  final bool canRestart;

  factory ChatLifecycle.fromJson(Map<String, dynamic> json) {
    return ChatLifecycle(
      state: json['state']?.toString() ?? 'active',
      turnCount: _intValue(json['turn_count']),
      turnLimit: _intValue(json['turn_limit']),
      canSendMessage: _boolValue(json['can_send_message'], fallback: true),
      canRestart: _boolValue(json['can_restart']),
    );
  }

  factory ChatLifecycle.legacy({
    required String status,
    required List<ChatMessage> messages,
  }) {
    final normalizedStatus = status.trim().isEmpty ? 'active' : status.trim();
    final turnCount = messages.where((message) => message.role == 'user').length;
    final terminal = normalizedStatus == 'turn_limit_reached';

    return ChatLifecycle(
      state: normalizedStatus,
      turnCount: turnCount,
      turnLimit: 0,
      canSendMessage: !terminal,
      canRestart: terminal,
    );
  }

  bool get hasKnownTurnLimit => turnLimit > 0;

  bool get isTerminal => !canSendMessage || canRestart;

  String get displayState {
    switch (state) {
      case 'active':
        return '会話中';
      case 'turn_limit_reached':
        return '会話上限';
      case 'expired':
      case 'session_expired':
        return '期限切れ';
      case 'evicted':
      case 'session_evicted':
        return '終了済み';
      default:
        return state.isEmpty ? '未確認' : state;
    }
  }

  String get displayProgress {
    if (!hasKnownTurnLimit) {
      return '$turnCount / -';
    }
    return '$turnCount / $turnLimit';
  }
}

class ChatOutcome {
  const ChatOutcome({
    required this.kind,
    required this.canContinue,
    required this.canRestart,
    required this.userMessage,
    this.technicalCode,
  });

  final String kind;
  final bool canContinue;
  final bool canRestart;
  final String userMessage;
  final String? technicalCode;

  factory ChatOutcome.fromJson(Map<String, dynamic> json) {
    return ChatOutcome(
      kind: json['kind']?.toString() ?? 'pending',
      canContinue: _boolValue(json['can_continue'], fallback: true),
      canRestart: _boolValue(json['can_restart']),
      userMessage: json['user_message']?.toString() ?? '',
      technicalCode: _optionalString(json['technical_code']),
    );
  }

  factory ChatOutcome.legacy(ChatSource source) {
    if (source.engine == 'mock') {
      return const ChatOutcome(
        kind: 'mock',
        canContinue: true,
        canRestart: false,
        userMessage: 'デモ用の安全な会話を表示しています。',
        technicalCode: 'legacy_mock',
      );
    }

    return const ChatOutcome(
      kind: 'pending',
      canContinue: true,
      canRestart: false,
      userMessage: '会話を開始しました。',
      technicalCode: 'legacy_response',
    );
  }

  String get displayLabel {
    switch (kind) {
      case 'mock':
        return 'デモ応答';
      case 'configured':
        return '設定済みAI';
      case 'fallback':
        return '代替応答';
      case 'unavailable':
        return '利用不可';
      case 'blocked':
        return 'ブロック中';
      case 'skipped':
        return '現在オフ';
      case 'pending':
        return '開始済み';
      default:
        return kind.isEmpty ? '未確認' : kind;
    }
  }
}

class ChatSessionProblem {
  const ChatSessionProblem({
    required this.code,
    required this.message,
    required this.userMessage,
    this.canRestart = true,
  });

  final String code;
  final String message;
  final String userMessage;
  final bool canRestart;

  factory ChatSessionProblem.fromJson(Map<String, dynamic> json) {
    return ChatSessionProblem(
      code: json['code']?.toString() ?? 'session_not_found',
      message: json['message']?.toString() ?? 'Chat session not found',
      userMessage: json['user_message']?.toString() ??
          'この会話を続けられません。新しい会話を始めてください。',
      canRestart: _boolValue(json['can_restart'], fallback: true),
    );
  }

  String get displayLabel {
    switch (code) {
      case 'session_expired':
        return '期限切れ';
      case 'session_evicted':
        return '終了済み';
      case 'turn_limit_reached':
        return '会話上限';
      case 'session_not_found':
        return '会話を確認できません';
      default:
        return '会話を続けられません';
    }
  }
}

class PostAdviceChatApiException implements Exception {
  const PostAdviceChatApiException({
    required this.statusCode,
    required this.fallbackMessage,
    this.problem,
  });

  final int statusCode;
  final String fallbackMessage;
  final ChatSessionProblem? problem;

  String get userMessage => problem?.userMessage ?? fallbackMessage;

  @override
  String toString() {
    final code = problem?.code;
    if (code == null || code.isEmpty) {
      return fallbackMessage;
    }
    return '$fallbackMessage ($code)';
  }
}

class ChatSession {
  const ChatSession({
    required this.sessionId,
    required this.status,
    required this.source,
    required this.context,
    required this.messages,
    this.lifecycle = const ChatLifecycle(
      state: 'active',
      turnCount: 0,
      turnLimit: 0,
      canSendMessage: true,
      canRestart: false,
    ),
    this.outcome = const ChatOutcome(
      kind: 'pending',
      canContinue: true,
      canRestart: false,
      userMessage: '会話を開始しました。',
    ),
  });

  final String sessionId;
  final String status;
  final ChatSource source;
  final PostAdviceChatContext context;
  final List<ChatMessage> messages;
  final ChatLifecycle lifecycle;
  final ChatOutcome outcome;

  bool get canSendMessage =>
      lifecycle.canSendMessage && outcome.canContinue;

  bool get canRestart =>
      lifecycle.canRestart || outcome.canRestart;

  factory ChatSession.fromJson(Map<String, dynamic> json) {
    final status = json['status']?.toString() ?? '';
    final source = ChatSource.fromJson(
      json['source'] is Map
          ? Map<String, dynamic>.from(json['source'] as Map)
          : {},
    );
    final messages = _parseMessages(json['messages']);

    return ChatSession(
      sessionId: json['session_id']?.toString() ?? '',
      status: status,
      source: source,
      context: PostAdviceChatContext.fromJson(
        json['context'] is Map
            ? Map<String, dynamic>.from(json['context'] as Map)
            : {},
      ),
      messages: messages,
      lifecycle: json['lifecycle'] is Map
          ? ChatLifecycle.fromJson(
              Map<String, dynamic>.from(json['lifecycle'] as Map),
            )
          : ChatLifecycle.legacy(status: status, messages: messages),
      outcome: json['outcome'] is Map
          ? ChatOutcome.fromJson(
              Map<String, dynamic>.from(json['outcome'] as Map),
            )
          : ChatOutcome.legacy(source),
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
    this.lifecycle = const ChatLifecycle(
      state: 'active',
      turnCount: 0,
      turnLimit: 0,
      canSendMessage: true,
      canRestart: false,
    ),
    this.outcome = const ChatOutcome(
      kind: 'pending',
      canContinue: true,
      canRestart: false,
      userMessage: '会話を続けられます。',
    ),
  });

  final String sessionId;
  final ChatMessage reply;
  final ChatSource source;
  final List<ChatMessage> messages;
  final ChatLifecycle lifecycle;
  final ChatOutcome outcome;

  factory ChatMessageResponse.fromJson(Map<String, dynamic> json) {
    final source = ChatSource.fromJson(
      json['source'] is Map
          ? Map<String, dynamic>.from(json['source'] as Map)
          : {},
    );
    final messages = ChatSession._parseMessages(json['messages']);

    return ChatMessageResponse(
      sessionId: json['session_id']?.toString() ?? '',
      reply: ChatMessage.fromJson(
        json['reply'] is Map
            ? Map<String, dynamic>.from(json['reply'] as Map)
            : {},
      ),
      source: source,
      messages: messages,
      lifecycle: json['lifecycle'] is Map
          ? ChatLifecycle.fromJson(
              Map<String, dynamic>.from(json['lifecycle'] as Map),
            )
          : ChatLifecycle.legacy(status: 'active', messages: messages),
      outcome: json['outcome'] is Map
          ? ChatOutcome.fromJson(
              Map<String, dynamic>.from(json['outcome'] as Map),
            )
          : ChatOutcome.legacy(source),
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

int _intValue(dynamic value) {
  if (value is int) {
    return value;
  }
  return int.tryParse(value?.toString() ?? '') ?? 0;
}

bool _boolValue(dynamic value, {bool fallback = false}) {
  if (value is bool) {
    return value;
  }
  final normalized = value?.toString().trim().toLowerCase();
  if (normalized == 'true' || normalized == '1') {
    return true;
  }
  if (normalized == 'false' || normalized == '0') {
    return false;
  }
  return fallback;
}
