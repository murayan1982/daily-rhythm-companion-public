import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:app/models/advice_response.dart';
import 'package:app/models/advice_source.dart';
import 'package:app/models/character_preset.dart';
import 'package:app/models/chat.dart';
import 'package:app/models/demo_status.dart';
import 'package:app/models/google_health_connection_ux.dart';
import 'package:app/models/google_health_diagnostics.dart';
import 'package:app/models/google_health_preflight.dart';
import 'package:app/models/google_health_self_check.dart';
import 'package:app/models/sleep_provider_selection.dart';
import 'package:app/models/sleep_summary.dart';
import 'package:app/screens/home_screen.dart';
import 'package:app/services/backend_api_client.dart';

void main() {
  testWidgets('turn-limit lifecycle disables sending and offers restart', (
    WidgetTester tester,
  ) async {
    final client = _LifecycleBackendApiClient(_ChatScenario.turnLimit);

    await _openPostAdviceChat(tester, client);

    expect(find.text('会話状態: 会話上限'), findsOneWidget);
    expect(find.text('会話回数: 8 / 8'), findsOneWidget);
    expect(find.byKey(const Key('post-advice-chat-message-field')), findsNothing);
    expect(
      find.byKey(const Key('post-advice-chat-restart-button')),
      findsOneWidget,
    );
  });

  testWidgets('expired session clears stale state and can restart directly', (
    WidgetTester tester,
  ) async {
    final client = _LifecycleBackendApiClient(_ChatScenario.expiredOnSend);

    await _openPostAdviceChat(tester, client);

    final field = find.byKey(const Key('post-advice-chat-message-field'));
    expect(field, findsOneWidget);
    await tester.enterText(field, '続けて話したい');

    final sendButton = find.byKey(const Key('post-advice-chat-send-button'));
    await tester.ensureVisible(sendButton);
    await tester.tap(sendButton);
    await tester.pumpAndSettle();

    expect(find.text('期限切れ'), findsOneWidget);
    expect(
      find.textContaining('時間が空いたため終了しました'),
      findsOneWidget,
    );
    expect(field, findsNothing);

    final restart = find.byKey(const Key('post-advice-chat-restart-button'));
    await tester.ensureVisible(restart);
    await tester.tap(restart);
    await tester.pumpAndSettle();

    expect(client.createCount, 2);
    expect(find.text('会話状態: 会話中'), findsOneWidget);
    expect(
      find.byKey(const Key('post-advice-chat-message-field')),
      findsOneWidget,
    );
  });

  testWidgets('unavailable outcome shows user copy and restart action', (
    WidgetTester tester,
  ) async {
    final client = _LifecycleBackendApiClient(_ChatScenario.unavailableOnSend);

    await _openPostAdviceChat(tester, client);

    final field = find.byKey(const Key('post-advice-chat-message-field'));
    await tester.enterText(field, 'AIチャットを確認');

    final sendButton = find.byKey(const Key('post-advice-chat-send-button'));
    await tester.ensureVisible(sendButton);
    await tester.tap(sendButton);
    await tester.pumpAndSettle();

    expect(find.text('応答状態: 利用不可'), findsOneWidget);
    expect(
      find.textContaining('現在AIチャットを利用できません'),
      findsOneWidget,
    );
    expect(
      find.byKey(const Key('post-advice-chat-restart-button')),
      findsOneWidget,
    );
    expect(field, findsNothing);
  });
}

Future<void> _openPostAdviceChat(
  WidgetTester tester,
  _LifecycleBackendApiClient client,
) async {
  await tester.pumpWidget(
    MaterialApp(home: HomeScreen(apiClient: client)),
  );
  await tester.pumpAndSettle();

  final adviceButton = find.widgetWithText(
    ElevatedButton,
    '今日のアドバイスを作る',
  );
  await tester.ensureVisible(adviceButton);
  await tester.tap(adviceButton);
  await tester.pumpAndSettle();

  final startButton = find.widgetWithText(ElevatedButton, '少し話す');
  await tester.ensureVisible(startButton);
  await tester.tap(startButton);
  await tester.pumpAndSettle();
}

enum _ChatScenario {
  turnLimit,
  expiredOnSend,
  unavailableOnSend,
}

class _LifecycleBackendApiClient extends BackendApiClient {
  _LifecycleBackendApiClient(this.scenario);

  final _ChatScenario scenario;
  int createCount = 0;

  static const _character = CharacterPreset(
    characterId: 'gentle_mina',
    displayName: 'ミナ',
    description: '落ち着いて寄り添うキャラクター',
    personalityType: 'gentle',
    speakingStyle: 'calm',
    adviceStyle: 'supportive',
  );

  @override
  Future<String> fetchHealthStatus() async => 'ok / API v2.0.1';

  @override
  Future<List<CharacterPreset>> fetchCharacters() async => const [_character];

  @override
  Future<SleepSummary> fetchSleepSummary() async {
    return const SleepSummary(
      date: '2026-07-24',
      totalSleepMinutes: 420,
      efficiency: 85,
      source: 'mock',
      available: true,
      isRealData: false,
    );
  }

  @override
  Future<SleepProviderSelectionStatus>
      fetchSleepProviderSelectionStatus() async {
    throw StateError('provider metadata is not needed in this focused test');
  }

  @override
  Future<DemoStatus> fetchDemoStatus() async {
    throw StateError('demo status is not needed in this focused test');
  }

  @override
  Future<GoogleHealthConnectionUx> fetchGoogleHealthConnectionUx() async {
    throw StateError('Google Health UX is not needed in this focused test');
  }

  @override
  Future<GoogleHealthDiagnostics> fetchGoogleHealthDiagnostics() async {
    throw StateError('Google Health diagnostics are not needed');
  }

  @override
  Future<GoogleHealthPreflight> fetchGoogleHealthPreflight() async {
    throw StateError('Google Health preflight is not needed');
  }

  @override
  Future<GoogleHealthSelfCheck> fetchGoogleHealthSelfCheck() async {
    throw StateError('Google Health self-check is not needed');
  }

  @override
  Future<AdviceResponse> createAdvice({
    required CharacterPreset character,
    required SleepSummary sleepSummary,
    required String mood,
  }) async {
    return AdviceResponse(
      message: '${character.displayName}です。今日は無理なく整えましょう。',
      characterName: character.displayName,
      source: AdviceSource(
        engine: 'mock',
        drcCharacterId: character.characterId,
        drcCharacterName: character.displayName,
      ),
    );
  }

  @override
  Future<ChatSession> createPostAdviceChatSession({
    required CharacterPreset character,
    required AdviceResponse adviceResponse,
    required String mood,
    String? initialUserMessage,
  }) async {
    createCount += 1;
    final isTurnLimit =
        scenario == _ChatScenario.turnLimit && createCount == 1;

    return ChatSession(
      sessionId: 'chat_${createCount.toString().padLeft(3, '0')}',
      status: isTurnLimit ? 'turn_limit_reached' : 'active',
      source: const ChatSource(
        engine: 'mock',
        mode: 'post_advice_chat',
        drcCharacterId: 'gentle_mina',
        drcCharacterName: 'ミナ',
      ),
      context: PostAdviceChatContext(
        character: character,
        adviceMessage: adviceResponse.message,
        mood: mood,
        adviceSource: adviceResponse.source,
      ),
      messages: const [
        ChatMessage(
          role: 'assistant',
          content: 'ミナです。もう少し話せるよ。',
        ),
      ],
      lifecycle: ChatLifecycle(
        state: isTurnLimit ? 'turn_limit_reached' : 'active',
        turnCount: isTurnLimit ? 8 : 0,
        turnLimit: 8,
        canSendMessage: !isTurnLimit,
        canRestart: isTurnLimit,
      ),
      outcome: const ChatOutcome(
        kind: 'mock',
        canContinue: true,
        canRestart: false,
        userMessage: 'デモ用の安全な会話を開始しました。',
        technicalCode: 'mock',
      ),
    );
  }

  @override
  Future<ChatMessageResponse> sendPostAdviceChatMessage({
    required String sessionId,
    required String message,
  }) async {
    if (scenario == _ChatScenario.expiredOnSend) {
      throw const PostAdviceChatApiException(
        statusCode: 404,
        fallbackMessage: 'Post-advice chat message API failed: HTTP 404',
        problem: ChatSessionProblem(
          code: 'session_expired',
          message: 'Chat session not found',
          userMessage:
              'この会話は時間が空いたため終了しました。新しい会話を始めてください。',
        ),
      );
    }

    final unavailable = scenario == _ChatScenario.unavailableOnSend;
    final reply = ChatMessage(
      role: 'assistant',
      content: unavailable
          ? '現在はAIチャットを利用できません。'
          : 'ミナです。ゆっくり続けよう。',
    );

    return ChatMessageResponse(
      sessionId: sessionId,
      reply: reply,
      source: ChatSource(
        engine: unavailable ? 'framework' : 'mock',
        mode: unavailable
            ? 'framework_text_chat_unavailable'
            : 'post_advice_chat',
        drcCharacterId: 'gentle_mina',
        drcCharacterName: 'ミナ',
      ),
      messages: [
        const ChatMessage(
          role: 'assistant',
          content: 'ミナです。もう少し話せるよ。',
        ),
        ChatMessage(role: 'user', content: message),
        reply,
      ],
      lifecycle: const ChatLifecycle(
        state: 'active',
        turnCount: 1,
        turnLimit: 8,
        canSendMessage: true,
        canRestart: false,
      ),
      outcome: ChatOutcome(
        kind: unavailable ? 'unavailable' : 'mock',
        canContinue: !unavailable,
        canRestart: unavailable,
        userMessage: unavailable
            ? '現在AIチャットを利用できません。時間をおいて新しい会話を始めてください。'
            : 'デモ用の安全な応答を表示しています。',
        technicalCode:
            unavailable ? 'framework_text_chat_unavailable' : 'mock',
      ),
    );
  }
}
