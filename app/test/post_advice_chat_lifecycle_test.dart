import 'package:flutter_test/flutter_test.dart';

import 'package:app/models/chat.dart';

void main() {
  const source = ChatSource(
    engine: 'framework',
    mode: 'framework_text_chat_boundary',
    drcCharacterId: 'gentle_mina',
    drcCharacterName: 'ミナ',
  );

  test('ChatSession parses structured lifecycle and outcome fields', () {
    final session = ChatSession.fromJson({
      'session_id': 'chat_001',
      'status': 'turn_limit_reached',
      'source': {
        'engine': 'framework',
        'mode': 'framework_text_chat_boundary',
        'drc_character_id': 'gentle_mina',
        'drc_character_name': 'ミナ',
      },
      'context': {
        'character': {
          'character_id': 'gentle_mina',
          'display_name': 'ミナ',
          'description': 'gentle',
          'personality_type': 'gentle',
          'speaking_style': 'calm',
          'advice_style': 'supportive',
        },
        'advice_message': '今日は休みましょう。',
      },
      'messages': [
        {'role': 'assistant', 'content': '開始'},
        {'role': 'user', 'content': '質問'},
        {'role': 'assistant', 'content': '返答'},
      ],
      'lifecycle': {
        'state': 'turn_limit_reached',
        'turn_count': 8,
        'turn_limit': 8,
        'can_send_message': false,
        'can_restart': true,
      },
      'outcome': {
        'kind': 'configured',
        'can_continue': true,
        'can_restart': false,
        'user_message': '設定済みAIから返答しました。',
        'technical_code': 'configured_success',
      },
    });

    expect(session.lifecycle.displayState, '会話上限');
    expect(session.lifecycle.displayProgress, '8 / 8');
    expect(session.canSendMessage, isFalse);
    expect(session.canRestart, isTrue);
    expect(session.outcome.displayLabel, '設定済みAI');
  });

  test('legacy chat payload remains parseable without lifecycle fields', () {
    final session = ChatSession.fromJson({
      'session_id': 'chat_legacy',
      'status': 'active',
      'source': {
        'engine': 'mock',
        'mode': 'post_advice_chat',
        'drc_character_id': 'gentle_mina',
        'drc_character_name': 'ミナ',
      },
      'context': {
        'character': {
          'character_id': 'gentle_mina',
          'display_name': 'ミナ',
          'description': 'gentle',
          'personality_type': 'gentle',
          'speaking_style': 'calm',
          'advice_style': 'supportive',
        },
        'advice_message': '今日は休みましょう。',
      },
      'messages': [
        {'role': 'assistant', 'content': '開始'},
        {'role': 'user', 'content': '質問'},
        {'role': 'assistant', 'content': '返答'},
      ],
    });

    expect(session.lifecycle.turnCount, 1);
    expect(session.lifecycle.hasKnownTurnLimit, isFalse);
    expect(session.canSendMessage, isTrue);
    expect(session.outcome.kind, 'mock');
  });

  test('ChatSessionProblem exposes restartable user-facing reason', () {
    final problem = ChatSessionProblem.fromJson({
      'code': 'session_expired',
      'message': 'Chat session not found',
      'user_message': 'この会話は時間が空いたため終了しました。新しい会話を始めてください。',
      'can_restart': true,
    });

    expect(problem.displayLabel, '期限切れ');
    expect(problem.canRestart, isTrue);
    expect(problem.userMessage, contains('新しい会話'));
  });

  test('PostAdviceChatApiException prefers structured problem copy', () {
    const problem = ChatSessionProblem(
      code: 'turn_limit_reached',
      message: 'Chat turn limit reached',
      userMessage: 'この会話は上限まで進みました。',
    );
    const error = PostAdviceChatApiException(
      statusCode: 409,
      fallbackMessage: 'Chat API failed',
      problem: problem,
    );

    expect(error.userMessage, 'この会話は上限まで進みました。');
    expect(error.toString(), contains('turn_limit_reached'));
    expect(source.displayLabel, 'framework / framework_text_chat_boundary');
  });
}
