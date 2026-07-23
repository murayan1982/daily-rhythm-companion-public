import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:app/main.dart';
import 'package:app/models/advice_response.dart';
import 'package:app/models/advice_source.dart';
import 'package:app/models/character_preset.dart';
import 'package:app/models/chat.dart';
import 'package:app/models/fitbit_connect_response.dart';
import 'package:app/models/fitbit_status.dart';
import 'package:app/models/google_health_connection_ux.dart';
import 'package:app/models/google_health_diagnostics.dart';
import 'package:app/models/google_health_preflight.dart';
import 'package:app/models/google_health_self_check.dart';
import 'package:app/models/sleep_provider_selection.dart';
import 'package:app/models/sleep_summary.dart';
import 'package:app/screens/home_screen.dart';
import 'package:app/services/backend_api_client.dart';
import 'package:app/models/daily_record.dart';
import 'package:app/models/recent_sleep_trend.dart';
import 'package:app/models/weekly_sleep_summary.dart';
import 'package:app/models/rhythm_report.dart';
import 'package:app/models/report_handoff_context.dart';
import 'package:app/models/demo_status.dart';
import 'package:app/models/voice_input_demo.dart';
import 'package:app/models/voice_output_demo.dart';
import 'package:app/models/motion_demo.dart';
import 'package:app/screens/history_screen.dart';
import 'package:app/ui/character_asset_catalog.dart';

void main() {
  testWidgets('App renders title', (WidgetTester tester) async {
    await tester.pumpWidget(const DailyRhythmCompanionApp());

    expect(find.text('Daily Rhythm Companion'), findsWidgets);
  });

  test('BackendApiClient exposes dart-define friendly default base URL', () {
    const apiClient = BackendApiClient();

    expect(BackendApiClient.defaultBaseUrl, 'http://127.0.0.1:8000');
    expect(apiClient.baseUrl, BackendApiClient.defaultBaseUrl);
    expect(apiClient.usesLocalhostBackend, isTrue);
    expect(
      apiClient.smartphoneWebAccessHint,
      contains('DRC_BACKEND_API_BASE_URL'),
    );
  });

  test('BackendApiClient formats versioned and legacy health payloads', () {
    expect(
      BackendApiClient.formatHealthStatus({
        'status': 'ok',
        'version': '2.0.1',
      }),
      'ok / API v2.0.1',
    );
    expect(
      BackendApiClient.formatHealthStatus({'status': 'ok'}),
      'ok',
    );
  });

  testWidgets('Backend connection section shows configured API base URL', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: HomeScreen(
          apiClient: _FakeBackendApiClient(
            baseUrl: 'http://203.0.113.20:8000',
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Backend status: ok / API v2.0.1'), findsOneWidget);
    expect(find.text('API base URL: http://203.0.113.20:8000'), findsOneWidget);
    expect(
      find.text('スマホWeb実演向けのbackend API URLが指定されています。'),
      findsOneWidget,
    );
  });



  testWidgets('Daily loop overview explains core app flow', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: HomeScreen(apiClient: _FakeBackendApiClient()),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text("Today's Loop"), findsOneWidget);
    expect(
      find.textContaining('まず今日の睡眠と気分を確認して'),
      findsOneWidget,
    );
    expect(find.text('7時間0分 / Google Health'), findsOneWidget);
    expect(find.text('ふつう'), findsWidgets);
    expect(find.text('Default'), findsWidgets);
    expect(find.text('未作成'), findsOneWidget);
    expect(
      find.textContaining('作成後は DailyRecord として履歴で確認できます'),
      findsOneWidget,
    );
  });




  testWidgets('Daily loop status gives recovery guidance after backend error', (
    WidgetTester tester,
  ) async {
    final apiClient = _RecoveringInitialLoadBackendApiClient();

    await tester.pumpWidget(
      MaterialApp(
        home: HomeScreen(apiClient: apiClient),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Daily Loop Status'), findsOneWidget);
    expect(find.text('状態: 確認が必要です'), findsOneWidget);
    expect(find.text('次の操作: 内容を確認して再読み込みする'), findsOneWidget);
    expect(find.text('Daily loop error'), findsOneWidget);
    expect(find.textContaining('temporary backend outage'), findsOneWidget);

    final reloadButton = find.widgetWithText(
      OutlinedButton,
      'Reload backend data',
    );
    expect(reloadButton, findsOneWidget);

    await tester.ensureVisible(reloadButton);
    await tester.pumpAndSettle();
    await tester.tap(reloadButton);
    await tester.pumpAndSettle();

    expect(find.text('状態: 準備できています'), findsOneWidget);
    expect(find.text('次の操作: 今日のアドバイスを作る'), findsOneWidget);
    expect(find.text('Daily loop error'), findsNothing);
  });




  testWidgets('Daily loop demo context separates capability status from core flow', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: HomeScreen(apiClient: _FakeBackendApiClient()),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Demo Context'), findsOneWidget);
    expect(find.text('Daily loop demo visibility'), findsOneWidget);
    expect(find.text('Loop engine: mock'), findsOneWidget);
    expect(find.text('Loop mode: mock safe'), findsOneWidget);
    expect(find.text('LLM for advice: unavailable / mock'), findsOneWidget);
    expect(
      find.text('Voice input demo: unavailable / not implemented'),
      findsOneWidget,
    );
    expect(
      find.text('Voice output demo: unavailable / not implemented'),
      findsOneWidget,
    );
    expect(
      find.text('Motion demo: unavailable / not implemented'),
      findsOneWidget,
    );
    expect(find.text('Advanced Demo Tools'), findsOneWidget);
    expect(find.textContaining('通常の日次ループは上の sleep / mood / character / advice flow'), findsOneWidget);
  });



  testWidgets('Mood check updates advice focus and readiness summary', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: HomeScreen(apiClient: _FakeBackendApiClient()),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('選択中: ふつう'), findsOneWidget);
    expect(find.text('Advice focus: 無理なく維持する'), findsWidgets);

    final tiredMoodChip = find.widgetWithText(ChoiceChip, '😪 だるい');
    expect(tiredMoodChip, findsOneWidget);

    await tester.ensureVisible(tiredMoodChip);
    await tester.pumpAndSettle();
    await tester.tap(tiredMoodChip);
    await tester.pumpAndSettle();

    expect(find.text('選択中: だるい'), findsOneWidget);
    expect(find.text('Advice focus: 回復優先で整える'), findsWidgets);
    expect(find.text('Mood: だるい'), findsOneWidget);
  });



  testWidgets('Character choice updates daily loop and advice context', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: HomeScreen(apiClient: _MultiCharacterBackendApiClient()),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Character Choice'), findsOneWidget);
    expect(find.text('選択中のキャラクター'), findsOneWidget);
    expect(find.text('Name: ミナ'), findsOneWidget);
    expect(find.text('Personality: gentle'), findsOneWidget);
    expect(find.text('Speaking: calm'), findsOneWidget);
    expect(find.text('Advice style: supportive'), findsOneWidget);
    expect(find.byKey(const ValueKey<String>('selected-character-image')), findsOneWidget);
    final selectedImage = tester.widget<Image>(
      find.byKey(const ValueKey<String>('selected-character-image')),
    );
    expect(
      (selectedImage.image as AssetImage).assetName,
      CharacterAssetCatalog.characterImages['gentle_mina'],
    );
    expect(
      find.byKey(const ValueKey<String>('character-option-image-gentle_mina')),
      findsOneWidget,
    );
    expect(
      find.textContaining('このキャラクターの話し方で、今日の気分と睡眠コンテキスト'),
      findsOneWidget,
    );

    final soraOption = find.text('ソラ');
    expect(soraOption, findsOneWidget);

    await tester.ensureVisible(soraOption);
    await tester.pumpAndSettle();
    await tester.tap(soraOption);
    await tester.pumpAndSettle();

    expect(find.text('Name: ソラ'), findsOneWidget);
    expect(find.text('Personality: cheerful'), findsOneWidget);
    expect(find.text('Speaking: bright'), findsOneWidget);
    expect(find.text('Advice style: upbeat'), findsOneWidget);
    final soraSelectedImage = tester.widget<Image>(
      find.byKey(const ValueKey<String>('selected-character-image')),
    );
    expect(
      (soraSelectedImage.image as AssetImage).assetName,
      CharacterAssetCatalog.characterImages['cheerful_sora'],
    );
    expect(find.text('Character: ソラ / upbeat'), findsOneWidget);
    expect(find.text('Character: ソラ'), findsOneWidget);

    final adviceButton = find.widgetWithText(
      ElevatedButton,
      '今日のアドバイスを作る',
    );
    expect(adviceButton, findsOneWidget);

    await tester.ensureVisible(adviceButton);
    await tester.pumpAndSettle();
    await tester.tap(adviceButton);
    await tester.pumpAndSettle();

    expect(find.textContaining('ソラです。'), findsOneWidget);
    expect(find.text('Character: ソラ'), findsWidgets);
  });





  testWidgets('Post-advice chat starts after advice and shows mock response', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: HomeScreen(apiClient: _FakeBackendApiClient()),
      ),
    );
    await tester.pumpAndSettle();

    final adviceButton = find.widgetWithText(
      ElevatedButton,
      '今日のアドバイスを作る',
    );
    await tester.ensureVisible(adviceButton);
    await tester.pumpAndSettle();
    await tester.tap(adviceButton);
    await tester.pumpAndSettle();

    expect(find.text('Post-advice Chat'), findsOneWidget);
    expect(find.text('少し話す'), findsOneWidget);
    expect(find.text('今日はここまで'), findsOneWidget);

    final startChatButton = find.widgetWithText(ElevatedButton, '少し話す');
    await tester.ensureVisible(startChatButton);
    await tester.pumpAndSettle();
    await tester.tap(startChatButton);
    await tester.pumpAndSettle();

    expect(find.textContaining('Chat source'), findsOneWidget);
    expect(find.textContaining('mock / post_advice_chat'), findsOneWidget);
    expect(find.textContaining('もう少し話せるよ'), findsOneWidget);

    await tester.enterText(
      find.byType(TextField),
      'もう少しゆるく過ごすには？',
    );

    final sendButton = find.widgetWithText(OutlinedButton, '送信');
    await tester.ensureVisible(sendButton);
    await tester.pumpAndSettle();
    await tester.tap(sendButton);
    await tester.pumpAndSettle();

    expect(find.text('あなた'), findsOneWidget);
    expect(find.textContaining('もう少しゆるく過ごすには？'), findsWidgets);
    expect(find.text('キャラクター'), findsWidgets);
  });


  testWidgets('Framework text chat unavailable state is visible in post-advice chat', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: HomeScreen(apiClient: _FrameworkUnavailableChatBackendApiClient()),
      ),
    );
    await tester.pumpAndSettle();

    final adviceButton = find.widgetWithText(
      ElevatedButton,
      '今日のアドバイスを作る',
    );
    await tester.ensureVisible(adviceButton);
    await tester.pumpAndSettle();
    await tester.tap(adviceButton);
    await tester.pumpAndSettle();

    final startChatButton = find.widgetWithText(ElevatedButton, '少し話す');
    await tester.ensureVisible(startChatButton);
    await tester.pumpAndSettle();
    await tester.tap(startChatButton);
    await tester.pumpAndSettle();

    expect(find.textContaining('Chat source'), findsOneWidget);
    expect(
      find.textContaining('framework / framework_text_chat_boundary'),
      findsOneWidget,
    );

    await tester.enterText(
      find.byType(TextField),
      'FWチャットの状態を確認したい',
    );

    final sendButton = find.widgetWithText(OutlinedButton, '送信');
    await tester.ensureVisible(sendButton);
    await tester.pumpAndSettle();
    await tester.tap(sendButton);
    await tester.pumpAndSettle();

    expect(
      find.textContaining('framework / framework_text_chat_unavailable'),
      findsOneWidget,
    );
    expect(find.textContaining('FWテキストチャットは有効化されていますが'), findsOneWidget);
    expect(find.text('あなた'), findsOneWidget);
    expect(find.text('キャラクター'), findsWidgets);
  });


  testWidgets('Post-advice chat can be skipped and daily record flow remains visible', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: HomeScreen(apiClient: _FakeBackendApiClient()),
      ),
    );
    await tester.pumpAndSettle();

    final adviceButton = find.widgetWithText(
      ElevatedButton,
      '今日のアドバイスを作る',
    );
    await tester.ensureVisible(adviceButton);
    await tester.pumpAndSettle();
    await tester.tap(adviceButton);
    await tester.pumpAndSettle();

    final skipButton = find.widgetWithText(OutlinedButton, '今日はここまで');
    await tester.ensureVisible(skipButton);
    await tester.pumpAndSettle();
    await tester.tap(skipButton);
    await tester.pumpAndSettle();

    expect(find.textContaining('今日はここまでを選びました'), findsOneWidget);
    expect(find.text('DailyRecord / History'), findsOneWidget);
  });


  testWidgets('Character-aware mood labels stay presentation-only while advice uses stable mood IDs', (
    WidgetTester tester,
  ) async {
    final apiClient = _MoodCopyTrackingBackendApiClient();

    await tester.pumpWidget(
      MaterialApp(
        home: HomeScreen(apiClient: apiClient),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Name: ミナ'), findsOneWidget);
    expect(find.widgetWithText(ChoiceChip, '☀️ いい感じ'), findsOneWidget);
    expect(find.widgetWithText(ChoiceChip, '🌿 いつも通り'), findsOneWidget);
    expect(find.widgetWithText(ChoiceChip, '😪 ちょっと休みたい'), findsOneWidget);
    expect(find.text('選択中: いつも通り'), findsOneWidget);
    expect(find.text('Advice focus: 穏やかに整える'), findsWidgets);
    expect(find.widgetWithText(ChoiceChip, '🌿 ふつう'), findsNothing);

    final soraOption = find.text('ソラ');
    expect(soraOption, findsOneWidget);

    await tester.ensureVisible(soraOption);
    await tester.pumpAndSettle();
    await tester.tap(soraOption);
    await tester.pumpAndSettle();

    expect(find.text('Name: ソラ'), findsOneWidget);
    expect(find.widgetWithText(ChoiceChip, '☀️ いけそう！'), findsOneWidget);
    expect(find.widgetWithText(ChoiceChip, '🌿 ぼちぼち'), findsOneWidget);
    expect(find.widgetWithText(ChoiceChip, '😪 省エネで'), findsOneWidget);
    expect(find.text('選択中: ぼちぼち'), findsOneWidget);
    expect(find.text('Advice focus: 小さく進める'), findsWidgets);

    final reiOption = find.text('レイ');
    expect(reiOption, findsOneWidget);

    await tester.ensureVisible(reiOption);
    await tester.pumpAndSettle();
    await tester.tap(reiOption);
    await tester.pumpAndSettle();

    expect(find.text('Name: レイ'), findsOneWidget);
    expect(find.widgetWithText(ChoiceChip, '☀️ 高め'), findsOneWidget);
    expect(find.widgetWithText(ChoiceChip, '🌿 標準'), findsOneWidget);
    expect(find.widgetWithText(ChoiceChip, '😪 低め'), findsOneWidget);
    expect(find.text('選択中: 標準'), findsOneWidget);
    expect(find.text('Advice focus: リズムを維持する'), findsWidgets);

    final tiredReiMoodChip = find.widgetWithText(ChoiceChip, '😪 低め');
    await tester.ensureVisible(tiredReiMoodChip);
    await tester.pumpAndSettle();
    await tester.tap(tiredReiMoodChip);
    await tester.pumpAndSettle();

    expect(find.text('選択中: 低め'), findsOneWidget);
    expect(find.text('Advice focus: 負荷を抑える'), findsWidgets);
    expect(find.text('Mood: 低め'), findsOneWidget);

    final adviceButton = find.widgetWithText(
      ElevatedButton,
      '今日のアドバイスを作る',
    );
    expect(adviceButton, findsOneWidget);

    await tester.ensureVisible(adviceButton);
    await tester.pumpAndSettle();
    await tester.tap(adviceButton);
    await tester.pumpAndSettle();

    expect(apiClient.lastMood, 'tired');
    expect(apiClient.lastCharacterId, 'cool_rei');
    expect(find.textContaining('mood=tired'), findsOneWidget);
    expect(find.textContaining('character=cool_rei'), findsOneWidget);
    expect(find.text('Character: レイ'), findsWidgets);
  });



  testWidgets('Accepted visual assets are exposed in the Web UI', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: HomeScreen(apiClient: _MultiCharacterBackendApiClient()),
      ),
    );
    await tester.pumpAndSettle();

    final previewTitle = find.text('Visual Asset Preview');
    await tester.ensureVisible(previewTitle);
    await tester.pumpAndSettle();

    expect(previewTitle, findsOneWidget);
    expect(
      find.byKey(const ValueKey<String>('morning-background-preview')),
      findsOneWidget,
    );
    expect(
      find.byKey(const ValueKey<String>('night-background-preview')),
      findsOneWidget,
    );
    expect(
      find.byKey(const ValueKey<String>('fallback-character-preview')),
      findsOneWidget,
    );
  });

  testWidgets('Daily loop completion summarizes next actions after advice', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: HomeScreen(apiClient: _FakeBackendApiClient()),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Daily Loop Complete'), findsNothing);

    final adviceButton = find.widgetWithText(
      ElevatedButton,
      '今日のアドバイスを作る',
    );
    expect(adviceButton, findsOneWidget);

    await tester.ensureVisible(adviceButton);
    await tester.pumpAndSettle();
    await tester.tap(adviceButton);
    await tester.pumpAndSettle();

    expect(find.text('Daily Loop Complete'), findsOneWidget);
    expect(find.text('完了サマリー'), findsOneWidget);
    expect(find.text('完了ステップ: 4 / 4'), findsOneWidget);
    expect(find.text('次のおすすめ: History で今日の記録を振り返る'), findsOneWidget);
    expect(find.text('明日の入口: 睡眠と気分を確認してもう一度作る'), findsOneWidget);
    expect(
      find.textContaining('今日の睡眠・気分・キャラクター・アドバイス確認まで完了'),
      findsOneWidget,
    );
  });



  testWidgets('Demo status renders capability availability', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: HomeScreen(apiClient: _FakeBackendApiClient()),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Demo Status'), findsOneWidget);
    expect(
      find.text('AI Character Framework demo capability visibility.'),
      findsOneWidget,
    );
    expect(find.text('Engine: mock'), findsWidgets);
    expect(find.text('Mode: mock safe'), findsOneWidget);
    expect(find.text('LLM response: unavailable / mock'), findsOneWidget);
    expect(
      find.text('Voice input: unavailable / not implemented'),
      findsOneWidget,
    );
    expect(
      find.text('Voice output: unavailable / not implemented'),
      findsOneWidget,
    );
    expect(
      find.text('Live2D motion: unavailable / not implemented'),
      findsOneWidget,
    );
    expect(
      find.text('Google Health real API: skipped / mock sleep provider'),
      findsOneWidget,
    );
    expect(
      find.text('LLM response is unavailable in mock mode.'),
      findsOneWidget,
    );
  });



  testWidgets('Voice input demo button submits metadata-only request', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: HomeScreen(apiClient: _FakeBackendApiClient()),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Voice Input Demo'), findsOneWidget);
    expect(
      find.textContaining('backend の voice input demo request contract'),
      findsOneWidget,
    );
    expect(find.text('まだ voice input demo request は送信していません。'), findsOneWidget);

    final voiceInputButton = find.widgetWithText(
      FilledButton,
      'Voice input demoを試す',
    );
    expect(voiceInputButton, findsOneWidget);

    await tester.ensureVisible(voiceInputButton);
    await tester.pumpAndSettle();
    await tester.tap(voiceInputButton);
    await tester.pumpAndSettle();

    expect(find.text('Request: not accepted'), findsOneWidget);
    expect(find.text('State: not started'), findsOneWidget);
    expect(find.text('Adapter: disabled'), findsOneWidget);
    expect(
      find.text('Capability: unavailable / not configured'),
      findsOneWidget,
    );
    expect(find.text('Transcript: -'), findsOneWidget);
    expect(find.text('Voice input checks'), findsOneWidget);
    expect(find.textContaining('Voice input demo request was received'), findsOneWidget);
  });


  testWidgets('Voice output demo button submits metadata-only request', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: HomeScreen(apiClient: _FakeBackendApiClient()),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Voice Output / TTS Demo'), findsOneWidget);
    expect(
      find.textContaining('backend の guarded voice output contract'),
      findsOneWidget,
    );
    expect(
      find.textContaining('Web UI の音声再生確認導線'),
      findsOneWidget,
    );
    expect(find.text('まだ voice output demo request は送信していません。'), findsOneWidget);

    final voiceOutputButton = find.widgetWithText(
      FilledButton,
      'Voice output demoを試す',
    );
    expect(voiceOutputButton, findsOneWidget);

    await tester.ensureVisible(voiceOutputButton);
    await tester.pumpAndSettle();
    await tester.tap(voiceOutputButton);
    await tester.pumpAndSettle();

    expect(find.text('Request: not accepted'), findsOneWidget);
    expect(find.text('State: not started'), findsOneWidget);
    expect(find.text('Adapter: disabled'), findsOneWidget);
    expect(
      find.text('Capability: unavailable / not configured'),
      findsOneWidget,
    );
    expect(find.text('Output mode: tts'), findsOneWidget);
    expect(find.text('Requested audio: mp3'), findsOneWidget);
    expect(find.text('Generated audio: -'), findsOneWidget);
    expect(find.text('Audio ready: not ready'), findsOneWidget);
    expect(find.text('Handoff kind: none'), findsOneWidget);
    expect(find.text('Has handoff: no'), findsOneWidget);
    expect(find.text('Generated state: not generated'), findsOneWidget);
    expect(find.text('Audio URL: not present'), findsOneWidget);
    expect(find.text('Audio artifact ref: not present'), findsOneWidget);
    expect(
      find.text('Playback candidate: non-playable (not generated: not started)'),
      findsOneWidget,
    );
    expect(find.text('音声を開いて再生確認する'), findsNothing);
    expect(
      find.textContaining('Public UI does not print raw audio URLs or artifact refs'),
      findsOneWidget,
    );
    expect(find.text('Voice output checks'), findsOneWidget);
    expect(find.textContaining('Voice output demo request was received'), findsOneWidget);
  });




  testWidgets('Voice output demo shows playback handoff when audio is ready', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: HomeScreen(apiClient: _AudioReadyVoiceOutputBackendApiClient()),
      ),
    );
    await tester.pumpAndSettle();

    final voiceOutputButton = find.widgetWithText(
      FilledButton,
      'Voice output demoを試す',
    );
    await tester.ensureVisible(voiceOutputButton);
    await tester.pumpAndSettle();
    await tester.tap(voiceOutputButton);
    await tester.pumpAndSettle();

    expect(find.text('Request: accepted'), findsOneWidget);
    expect(find.text('State: generated'), findsOneWidget);
    expect(find.text('Real TTS: enabled'), findsOneWidget);
    expect(find.text('Generated audio: mp3'), findsOneWidget);
    expect(find.text('Audio ready: ready'), findsOneWidget);
    expect(find.text('Handoff kind: url'), findsOneWidget);
    expect(find.text('Has handoff: yes'), findsOneWidget);
    expect(find.text('Generated state: generated'), findsOneWidget);
    expect(find.text('Audio URL: available (URL hidden)'), findsOneWidget);
    expect(find.text('Audio artifact ref: not present'), findsOneWidget);
    expect(
      find.text('Playback candidate: playable URL handoff (operator confirmation required)'),
      findsOneWidget,
    );
    expect(
      find.text('Playback: requires operator confirmation'),
      findsOneWidget,
    );
    expect(find.text('Evidence: not evidence'), findsOneWidget);
    expect(find.text('音声を開いて再生確認する'), findsOneWidget);
    expect(find.textContaining('/__test__/voice-output-audio.mp3'), findsNothing);
  });






  testWidgets('Voice output demo keeps legacy audio URL non-playable', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: HomeScreen(apiClient: _LegacyUrlVoiceOutputBackendApiClient()),
      ),
    );
    await tester.pumpAndSettle();

    final voiceOutputButton = find.widgetWithText(
      FilledButton,
      'Voice output demoを試す',
    );
    await tester.ensureVisible(voiceOutputButton);
    await tester.pumpAndSettle();
    await tester.tap(voiceOutputButton);
    await tester.pumpAndSettle();

    expect(find.text('Request: not accepted'), findsOneWidget);
    expect(find.text('State: legacy audio ready'), findsOneWidget);
    expect(find.text('Audio ready: ready'), findsOneWidget);
    expect(find.text('Handoff kind: url'), findsOneWidget);
    expect(find.text('Has handoff: yes'), findsOneWidget);
    expect(find.text('Generated state: not generated'), findsOneWidget);
    expect(find.text('Audio URL: available (URL hidden)'), findsOneWidget);
    expect(
      find.text('Playback candidate: non-playable (not generated: legacy audio ready)'),
      findsOneWidget,
    );
    expect(find.text('音声を開いて再生確認する'), findsNothing);
    expect(find.textContaining('/__test__/legacy-voice-output.mp3'), findsNothing);
  });


  testWidgets('Motion demo button submits lightweight avatar request', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: HomeScreen(apiClient: _FakeBackendApiClient()),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Motion Demo'), findsOneWidget);
    expect(find.textContaining('軽量なペラ絵/表情差分 simulator'), findsOneWidget);
    expect(find.text('Lightweight avatar simulator: happy'), findsOneWidget);
    expect(find.text('Motion event: greeting'), findsOneWidget);
    expect(find.text('まだ motion demo request は送信していません。'), findsOneWidget);

    final motionButton = find.widgetWithText(
      FilledButton,
      'Motion demoを試す',
    );
    expect(motionButton, findsOneWidget);

    await tester.ensureVisible(motionButton);
    await tester.pumpAndSettle();
    await tester.tap(motionButton);
    await tester.pumpAndSettle();

    expect(find.text('Request: not accepted'), findsOneWidget);
    expect(find.text('State: not started'), findsOneWidget);
    expect(find.text('Adapter: disabled'), findsOneWidget);
    expect(
      find.text('Capability: unavailable / not configured'),
      findsOneWidget,
    );
    expect(find.text('Motion: greeting'), findsOneWidget);
    expect(find.text('Expression: happy'), findsOneWidget);
    expect(find.text('Requested adapter: simulator'), findsOneWidget);
    expect(find.text('Resolved adapter: disabled'), findsOneWidget);
    expect(find.text('Motion sent: no'), findsOneWidget);
    expect(find.text('VTS connection: no'), findsOneWidget);
    expect(find.text('Supported motions'), findsOneWidget);
    expect(find.text('Supported expressions'), findsOneWidget);
    expect(find.textContaining('Motion demo request was received'), findsOneWidget);
  });


  testWidgets('Sleep summary renders normalized real data fields', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: HomeScreen(apiClient: _FakeBackendApiClient()),
      ),
    );
    await tester.pumpAndSettle();

    final sourceSection = find.byKey(const Key('sleep-data-source-section'));
    expect(sourceSection, findsOneWidget);
    expect(
      find.descendant(
        of: sourceSection,
        matching: find.text('設定中のprovider: Google Health'),
      ),
      findsOneWidget,
    );
    expect(
      find.descendant(
        of: sourceSection,
        matching: find.text('今回のデータ元: Google Health'),
      ),
      findsOneWidget,
    );
    expect(
      find.descendant(
        of: sourceSection,
        matching: find.text('データ種別: 実データ'),
      ),
      findsOneWidget,
    );
    expect(find.text('Sleep Summary'), findsOneWidget);
    expect(find.text('実データ'), findsOneWidget);
    expect(find.text('睡眠時間: 7時間0分'), findsOneWidget);
    expect(find.textContaining('睡眠評価:'), findsNothing);
    expect(find.textContaining('信頼度:'), findsNothing);
    });


  testWidgets('Advice section shows real sleep data context', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: HomeScreen(apiClient: _FakeBackendApiClient()),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('作成前の確認'), findsOneWidget);
    expect(find.text('Sleep: 7時間0分 / Google Health'), findsWidgets);
    expect(find.text('Mood: ふつう'), findsOneWidget);
    expect(find.text('Advice focus: 無理なく維持する'), findsWidgets);
    expect(find.text('Character: Default'), findsOneWidget);

    final adviceButton = find.widgetWithText(
      ElevatedButton,
      '今日のアドバイスを作る',
    );
    expect(adviceButton, findsOneWidget);

    await tester.ensureVisible(adviceButton);
    await tester.pumpAndSettle();
    await tester.tap(adviceButton);
    await tester.pumpAndSettle();

    expect(find.text('Advice'), findsOneWidget);
    expect(find.text('作成結果です。必要なら気分やキャラクターを変えて、もう一度作り直せます。'), findsOneWidget);
    expect(find.text('DailyRecord: 保存対象'), findsOneWidget);
    expect(find.text('実睡眠データを反映'), findsOneWidget);
    expect(find.text('睡眠時間 7時間0分'), findsOneWidget);
    expect(find.textContaining('/ 評価'), findsNothing);
    expect(find.textContaining('Google Healthの実データ'), findsOneWidget);
    expect(find.text('Advice Source'), findsOneWidget);
    expect(find.text('Engine: mock'), findsWidgets);
    expect(find.text('DRC: Default (default)'), findsOneWidget);
  });


  testWidgets('DailyRecord handoff explains history review path', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: HomeScreen(apiClient: _FakeBackendApiClient()),
      ),
    );
    await tester.pumpAndSettle();

    final adviceButton = find.widgetWithText(
      ElevatedButton,
      '今日のアドバイスを作る',
    );
    expect(adviceButton, findsOneWidget);

    await tester.ensureVisible(adviceButton);
    await tester.pumpAndSettle();
    await tester.tap(adviceButton);
    await tester.pumpAndSettle();

    expect(find.text('DailyRecord / History'), findsOneWidget);
    expect(find.text('保存と振り返り'), findsOneWidget);
    expect(find.text('保存ステータス: DailyRecord 保存対象'), findsOneWidget);
    expect(find.text('Sleep context: 7時間0分 / Google Health'), findsOneWidget);

    final historyButton = find.widgetWithText(
      OutlinedButton,
      '履歴で確認する',
    );
    expect(historyButton, findsOneWidget);

    await tester.ensureVisible(historyButton);
    await tester.pumpAndSettle();
    await tester.tap(historyButton);
    await tester.pumpAndSettle();

    expect(find.text('Daily History'), findsOneWidget);
    expect(find.text('History / DailyRecord'), findsOneWidget);
    expect(find.textContaining('過去の記録を振り返ります'), findsOneWidget);
  });


  testWidgets('Unavailable sleep data still allows mood-based advice', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: HomeScreen(apiClient: _UnavailableSleepBackendApiClient()),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('未取得'), findsWidgets);
    expect(find.text('状態: 未取得'), findsOneWidget);
    expect(find.text('理由: 対象日の睡眠データが見つかりません'), findsOneWidget);
    expect(
      find.text('睡眠データがない場合でも、今の気分をもとにアドバイスできます。'),
      findsOneWidget,
    );

    final adviceButton = find.widgetWithText(
      ElevatedButton,
      '今日のアドバイスを作る',
    );
    expect(adviceButton, findsOneWidget);

    await tester.ensureVisible(adviceButton);
    await tester.pumpAndSettle();
    await tester.tap(adviceButton);
    await tester.pumpAndSettle();

    expect(find.text('Advice'), findsOneWidget);
    expect(find.text('睡眠データ未取得のため気分を中心に反映'), findsOneWidget);
    expect(find.text('睡眠データ未取得 / 対象日の睡眠データが見つかりません'), findsOneWidget);
    expect(find.textContaining('睡眠データを確認できなかった'), findsOneWidget);
    expect(find.text('Advice Source'), findsOneWidget);
    expect(find.text('Engine: framework fallback'), findsOneWidget);
    expect(find.textContaining('0時間0分'), findsNothing);
  });


  testWidgets('Google Health user UX stays concise in sleep data source card', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: HomeScreen(apiClient: _FakeBackendApiClient()),
      ),
    );
    await tester.pumpAndSettle();

    final sourceSection = find.byKey(const Key('sleep-data-source-section'));
    expect(sourceSection, findsOneWidget);
    expect(
      find.descendant(
        of: sourceSection,
        matching: find.text('モック睡眠データで動作中'),
      ),
      findsOneWidget,
    );
    expect(
      find.descendant(
        of: sourceSection,
        matching: find.textContaining('開発用のモック睡眠データ'),
      ),
      findsOneWidget,
    );
    expect(
      find.descendant(
        of: sourceSection,
        matching: find.textContaining('次の操作:'),
      ),
      findsOneWidget,
    );
    expect(
      find.descendant(
        of: sourceSection,
        matching: find.text('状態の理由'),
      ),
      findsNothing,
    );
    expect(
      find.descendant(
        of: sourceSection,
        matching: find.text('開発者向け詳細'),
      ),
      findsNothing,
    );
    expect(
      find.descendant(
        of: sourceSection,
        matching: find.text('接続 / 継続'),
      ),
      findsNothing,
    );
  });

  testWidgets('Google Health operator details remain under advanced tools', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: HomeScreen(apiClient: _FakeBackendApiClient()),
      ),
    );
    await tester.pumpAndSettle();

    final operatorDetails =
        find.byKey(const Key('google-health-operator-details'));
    expect(operatorDetails, findsOneWidget);
    expect(
      find.descendant(
        of: operatorDetails,
        matching: find.text('状態の理由'),
      ),
      findsOneWidget,
    );
    expect(
      find.descendant(
        of: operatorDetails,
        matching: find.text('開発者向け詳細'),
      ),
      findsOneWidget,
    );
    expect(
      find.descendant(
        of: operatorDetails,
        matching: find.text('接続 / 継続'),
      ),
      findsOneWidget,
    );
    expect(find.text('Google Health Operator Connection Details'), findsOneWidget);
    expect(find.text('Checklist status: mock_mode'), findsOneWidget);
  });

  testWidgets('Mock provider stays credential-free and skips Fitbit status', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: HomeScreen(apiClient: _MockProviderBackendApiClient()),
      ),
    );
    await tester.pumpAndSettle();

    final sourceSection = find.byKey(const Key('sleep-data-source-section'));
    expect(sourceSection, findsOneWidget);
    expect(
      find.descendant(
        of: sourceSection,
        matching: find.text('設定中のprovider: サンプルデータ'),
      ),
      findsOneWidget,
    );
    expect(
      find.descendant(
        of: sourceSection,
        matching: find.text('今回のデータ元: サンプルデータ'),
      ),
      findsOneWidget,
    );
    expect(
      find.descendant(
        of: sourceSection,
        matching: find.textContaining('外部サービスへの接続は不要'),
      ),
      findsOneWidget,
    );
    expect(find.text('Fitbit Operator Status'), findsNothing);
  });

  testWidgets('Fitbit UI retires legacy OAuth guidance', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: HomeScreen(apiClient: _FitbitProviderBackendApiClient()),
      ),
    );
    await tester.pumpAndSettle();

    final sourceSection = find.byKey(const Key('sleep-data-source-section'));
    expect(sourceSection, findsOneWidget);
    expect(
      find.descendant(
        of: sourceSection,
        matching: find.text('設定中のprovider: Fitbit（旧Web API・移行参照）'),
      ),
      findsOneWidget,
    );
    expect(
      find.descendant(
        of: sourceSection,
        matching: find.text('Fitbit状態: ローカルトークン検出'),
      ),
      findsOneWidget,
    );
    expect(
      find.descendant(
        of: sourceSection,
        matching: find.textContaining('新しい実利用経路にはGoogle Health'),
      ),
      findsOneWidget,
    );
    expect(
      find.descendant(
        of: sourceSection,
        matching: find.text('Fitbit状態: 連携済み'),
      ),
      findsNothing,
    );
    expect(find.text('Fitbit Operator Status'), findsOneWidget);
  });

  testWidgets('Google Health developer check renders safe status fields', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: HomeScreen(apiClient: _FakeBackendApiClient()),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Google Health Developer Check'), findsOneWidget);
    expect(find.text('Refresh'), findsWidgets);
    expect(find.textContaining('Diagnostics: credentials不足'), findsOneWidget);
    expect(find.textContaining('Preflight: credentials不足'), findsOneWidget);
    expect(find.textContaining('Self Check: guard blocked'), findsOneWidget);
    expect(find.text('OAuth configured: ready'), findsOneWidget);
    expect(find.text('Credentials file configured: not ready'), findsOneWidget);
    expect(find.text('Guard allows real API: not ready'), findsOneWidget);
    expect(find.text('Preflight ready for OAuth: not ready'), findsOneWidget);
    expect(find.text('OAuth scopes configured: ready'), findsOneWidget);
    expect(find.text('OAuth scope count: 2'), findsOneWidget);
    expect(find.text('OAuth URL ready: not ready'), findsOneWidget);
    expect(find.text('Client secret configured: ready'), findsOneWidget);
    expect(find.text('Preflight real API allowed: not ready'), findsOneWidget);
    expect(find.text('Self-check HTTP status: -'), findsOneWidget);
    expect(find.text('Real HTTP attempted: not ready'), findsOneWidget);
    expect(find.text('Safe for /sleep/summary: ready'), findsOneWidget);
  });

  testWidgets('Google Health developer check does not render raw secrets', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: HomeScreen(apiClient: _FakeBackendApiClient()),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.textContaining('super-secret-client-secret'), findsNothing);
    expect(find.textContaining('raw-access-token-value'), findsNothing);
    expect(find.textContaining('raw-refresh-token-value'), findsNothing);
    expect(find.textContaining('raw-health-payload'), findsNothing);
  });
  testWidgets('History screen renders daily records', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: HistoryScreen(apiClient: _FakeBackendApiClient()),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Daily History'), findsOneWidget);
    expect(find.text('History / DailyRecord'), findsOneWidget);
    expect(find.text('過去の記録を振り返ります。'), findsOneWidget);
    expect(
      find.textContaining('過去の睡眠記録や傾向は参考情報です'),
      findsOneWidget,
    );
    expect(find.textContaining('今日の睡眠としては扱いません'), findsOneWidget);
    expect(find.text('表示件数: 1'), findsOneWidget);
    expect(find.text('Recent Sleep Trend'), findsOneWidget);
    expect(find.text('履歴から見た直近傾向ラベルです。'), findsOneWidget);
    expect(
      find.textContaining('今日の睡眠データや健康状態の断定には使いません'),
      findsWidgets,
    );
    expect(find.text('最近は短め傾向'), findsOneWidget);
    expect(find.text('平均: 5時間40分'), findsOneWidget);
    expect(find.text('対象: 直近7日 / 使用記録: 3件'), findsOneWidget);
    expect(find.text('Simple Weekly Summary'), findsOneWidget);
    expect(find.text('週対象: 対象: 直近7日 / 使用記録: 3件'), findsOneWidget);
    expect(find.text('過去のDailyRecordから作る軽い週次まとめです。'), findsOneWidget);
    expect(find.textContaining('今日の睡眠や健康状態の診断には使いません'), findsWidgets);
    expect(find.text('今週は短め寄り'), findsOneWidget);
    expect(find.text('週平均: 5時間40分'), findsOneWidget);
    expect(
      find.textContaining('予定や休憩を軽く見直す参考にできます'),
      findsOneWidget,
    );
    expect(
      find.text('メモ: 短めの日が続く時は、無理な予定を詰めすぎない参考にしてください。'),
      findsOneWidget,
    );

    await tester.scrollUntilVisible(find.text('Weekly Rhythm Report'), 200.0);
    await tester.pumpAndSettle();

    expect(find.text('Weekly Rhythm Report'), findsOneWidget);
    expect(find.text('週次リズムは短め寄り'), findsOneWidget);
    expect(find.text('記録状態: 参考にしやすい記録数です'), findsOneWidget);
    expect(find.text('レポート範囲: 2026-05-11 〜 2026-05-17'), findsOneWidget);
    expect(find.text('保存記録: 3件 / 睡眠つき記録: 3件'), findsWidgets);
    expect(
      find.text('データ元: 保存済みDailyRecord（デモ睡眠データ）'),
      findsNWidgets(2),
    );
    expect(find.text('集計範囲: 週次の保存履歴'), findsOneWidget);

    await tester.scrollUntilVisible(find.text('Monthly Rhythm Report'), 200.0);
    await tester.pumpAndSettle();

    expect(find.text('Monthly Rhythm Report'), findsOneWidget);
    expect(find.text('月次リズムは参考程度'), findsOneWidget);
    expect(find.text('記録状態: 記録が少なめなので参考程度です'), findsOneWidget);
    expect(find.text('レポート範囲: 2026-04-18 〜 2026-05-17'), findsOneWidget);
    expect(find.text('集計範囲: 月次の保存履歴'), findsOneWidget);

    await tester.scrollUntilVisible(find.text('2026-05-08'), 200.0);
    await tester.pumpAndSettle();

    expect(find.text('2026-05-08'), findsOneWidget);
    expect(find.text('ミナ'), findsOneWidget);
    expect(find.text('気分: だるい'), findsOneWidget);
    expect(find.text('記録種別: 過去の記録'), findsOneWidget);
    expect(find.text('睡眠時間: 5時間30分'), findsOneWidget);
    expect(find.text('データ種別: デモデータ / サンプルデータ'), findsOneWidget);
    expect(
      find.textContaining('今日の睡眠状態の断定には使いません'),
      findsOneWidget,
    );
    expect(find.textContaining('今日は回復優先'), findsOneWidget);
    expect(find.text('Advice basis: この日の睡眠・気分・キャラクター'), findsOneWidget);
    expect(find.text('Source: mock'), findsOneWidget);
  });



  testWidgets('Advice section displays report handoff context without raw labels', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: HomeScreen(apiClient: _ReportHandoffAdviceBackendApiClient()),
      ),
    );
    await tester.pumpAndSettle();

    final adviceButton = find.widgetWithText(
      ElevatedButton,
      '今日のアドバイスを作る',
    );
    expect(adviceButton, findsOneWidget);

    await tester.ensureVisible(adviceButton);
    await tester.pumpAndSettle();
    await tester.tap(adviceButton);
    await tester.pumpAndSettle();

    expect(find.text('Report context'), findsOneWidget);
    expect(find.text('Report context: 週次レポートも参考'), findsOneWidget);
    expect(find.text('週次レポートも参考'), findsOneWidget);
    expect(
      find.textContaining('過去の保存記録から見た軽い参考情報です'),
      findsOneWidget,
    );
    expect(find.text('記録状態: 参考にしやすい保存記録があります'), findsOneWidget);
    expect(find.text('範囲: 2026-05-11 〜 2026-05-17'), findsOneWidget);
    expect(find.text('保存記録: 3件 / 睡眠つき記録: 3件'), findsOneWidget);
    expect(
      find.text('データ元: 保存済みDailyRecord（デモ睡眠データ）からの振り返り'),
      findsOneWidget,
    );
    expect(find.text('集計範囲: 週次の保存履歴'), findsOneWidget);
    expect(find.textContaining('source_label'), findsNothing);
    expect(find.textContaining('data_quality'), findsNothing);
    expect(find.textContaining('weekly_history'), findsNothing);
  });

  testWidgets('History screen displays report-informed DailyRecord reflection', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: HistoryScreen(apiClient: _ReportHandoffHistoryBackendApiClient()),
      ),
    );
    await tester.pumpAndSettle();

    await tester.scrollUntilVisible(find.text('2026-05-17'), 200.0);
    await tester.pumpAndSettle();

    expect(
      find.text('Advice basis: リズムレポートも参考にしたアドバイス'),
      findsOneWidget,
    );
    expect(
      find.text('Report reflection: 週次レポートも参考にした振り返り'),
      findsOneWidget,
    );
    expect(
      find.text('Report quality: 参考にしやすい保存記録があります'),
      findsOneWidget,
    );
    expect(
      find.text('Report source: 保存済みDailyRecord（デモ睡眠データ）からの振り返り'),
      findsOneWidget,
    );
    expect(find.textContaining('source_label'), findsNothing);
    expect(find.textContaining('rhythm_report+mood+character+mock'), findsNothing);
  });

  testWidgets('History screen explains rhythm report fallback without raw labels', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: HistoryScreen(apiClient: _RhythmReportUnavailableBackendApiClient()),
      ),
    );
    await tester.pumpAndSettle();

    await tester.scrollUntilVisible(find.text('Weekly Rhythm Report'), 200.0);
    await tester.pumpAndSettle();

    expect(find.text('Weekly Rhythm Report'), findsOneWidget);
    expect(find.text('週次リズムレポート: 読み込み未完了'), findsOneWidget);
    expect(find.text('リズムレポートはまだ読み込めていません。'), findsWidgets);
    expect(
      find.text('履歴一覧と既存の週次まとめはそのまま確認できます。'),
      findsWidgets,
    );

    await tester.scrollUntilVisible(find.text('Monthly Rhythm Report'), 200.0);
    await tester.pumpAndSettle();

    expect(find.text('Monthly Rhythm Report'), findsOneWidget);
    expect(find.text('月次リズムレポート: 読み込み未完了'), findsOneWidget);
    expect(find.textContaining('Quality:'), findsNothing);
    expect(find.textContaining('Source: saved_daily_record_history'), findsNothing);
    expect(find.textContaining('Scope:'), findsNothing);
    expect(find.textContaining('weekly_history'), findsNothing);
    expect(find.textContaining('monthly_history'), findsNothing);
  });
}


const ReportHandoffContext _weeklyReportHandoffContext = ReportHandoffContext(
  period: 'weekly',
  rangeStart: '2026-05-11',
  rangeEnd: '2026-05-17',
  label: 'weekly_balanced',
  reportSummary: '保存済み記録から見ると、平均睡眠は6h 30mです。',
  actionHint: '今日は予定を詰めすぎず、休憩を先に置いておくとよさそうです。',
  sourceLabel: 'saved_daily_record_history_with_mock_sleep',
  dataScope: 'weekly_history',
  dataQuality: 'usable',
  totalRecordCount: 3,
  usableSleepRecordCount: 3,
  isMedicalAdvice: false,
  shouldInformAdvice: true,
  adviceBasisPrefix: 'rhythm_report',
  userFacingSourceLabel: '保存済みDailyRecord（デモ睡眠データ）からの振り返り',
  userFacingScopeLabel: '週次の保存履歴',
  userFacingQualityLabel: '参考にしやすい保存記録があります',
  userFacingSummary: '過去の保存記録から見た軽い振り返りとして扱います。',
  promptGuidance: 'Use this report as lightweight historical context only.',
);

class _ReportHandoffAdviceBackendApiClient extends _FakeBackendApiClient {
  const _ReportHandoffAdviceBackendApiClient();

  @override
  Future<AdviceResponse> createAdvice({
    required CharacterPreset character,
    required SleepSummary sleepSummary,
    required String mood,
  }) async {
    return AdviceResponse(
      message:
          '${character.displayName}です。週次レポートは過去の保存記録として軽く参考にしつつ、今日は無理なく整えましょう。',
      characterName: character.displayName,
      source: AdviceSource(
        engine: 'mock',
        drcCharacterId: character.characterId,
        drcCharacterName: character.displayName,
        reportHandoff: _weeklyReportHandoffContext,
      ),
    );
  }
}

class _ReportHandoffHistoryBackendApiClient extends _FakeBackendApiClient {
  const _ReportHandoffHistoryBackendApiClient();

  @override
  Future<List<DailyRecord>> fetchDailyRecords({int limit = 30}) async {
    return [
      DailyRecord(
        date: '2026-05-17',
        characterId: 'gentle_mina',
        characterName: 'ミナ',
        mood: 'normal',
        sleepSummary: const SleepSummary(
          date: '2026-05-17',
          totalSleepMinutes: 390,
          efficiency: 88,
          source: 'mock',
          available: true,
          message: 'Mock sleep summary is available.',
          qualityLabel: 'fair',
          confidence: 'mock',
          isRealData: false,
        ),
        adviceMessage: '週次レポートも参考にしながら、今日は無理なく整えましょう。',
        adviceBasis: 'rhythm_report+mood+character+mock',
        adviceSource: const AdviceSource(
          engine: 'mock',
          drcCharacterId: 'gentle_mina',
          drcCharacterName: 'ミナ',
          reportHandoff: _weeklyReportHandoffContext,
        ),
        createdAt: '2026-05-17T00:00:00Z',
        updatedAt: '2026-05-17T00:00:00Z',
      ),
    ];
  }
}


class _RhythmReportUnavailableBackendApiClient extends _FakeBackendApiClient {
  const _RhythmReportUnavailableBackendApiClient();

  @override
  Future<RhythmReport> fetchRhythmReport({
    String period = 'weekly',
    String? referenceDate,
  }) async {
    throw Exception('rhythm report unavailable for fallback test');
  }
}

class _AudioReadyVoiceOutputBackendApiClient extends _FakeBackendApiClient {
  const _AudioReadyVoiceOutputBackendApiClient()
      : super(baseUrl: 'http://203.0.113.20:8000');

  @override
  Future<VoiceOutputDemoRequestResponse> submitVoiceOutputDemoRequest({
    required String clientEventId,
    String outputMode = 'tts',
    String? textContent,
    String? characterId,
    String? voiceProfileId,
    String? audioFormat,
    String utterancePurpose = 'daily_advice',
  }) async {
    return VoiceOutputDemoRequestResponse(
      accepted: true,
      requestState: 'generated',
      engine: 'framework',
      mode: 'framework_local',
      adapterMode: 'framework',
      realTtsEnabled: true,
      outputMode: outputMode,
      clientEventId: clientEventId,
      textContent: textContent,
      characterId: characterId,
      voiceProfileId: voiceProfileId,
      requestedAudioFormat: audioFormat,
      utterancePurpose: utterancePurpose,
      frameworkCallState: 'generated',
      frameworkApiName: 'create_voice_output_session',
      audioUrl: '/__test__/voice-output-audio.mp3',
      audioArtifactRef: null,
      audioFormat: 'mp3',
      audioReady: true,
      audioHandoffKind: 'url',
      hasAudioHandoff: true,
      isGenerated: true,
      audioPlaybackStatus: 'requires_operator_confirmation',
      evidenceStatus: 'not_evidence',
      requestWarnings: const [],
      runtimeNotes: const [
        'Web UI audible playback and screenshot evidence must be privately recorded.',
      ],
      capability: const DemoCapabilityStatus(
        status: 'available',
        source: 'framework_public_boundary',
        message: 'Framework voice output boundary is available.',
      ),
      message:
          'Real TTS candidate audio is ready; operator playback confirmation is still required.',
      checks: const [
        VoiceOutputDemoProbeCheck(
          name: 'voice_output_real_tts_enabled',
          status: 'pass',
          message: 'Private real TTS gate is enabled for this fake widget test.',
        ),
      ],
      candidatePaths: const [],
      publicApiCandidates: const ['create_voice_output_session'],
    );
  }
}


class _LegacyUrlVoiceOutputBackendApiClient extends _FakeBackendApiClient {
  const _LegacyUrlVoiceOutputBackendApiClient()
      : super(baseUrl: 'http://203.0.113.20:8000');

  @override
  Future<VoiceOutputDemoRequestResponse> submitVoiceOutputDemoRequest({
    required String clientEventId,
    String outputMode = 'tts',
    String? textContent,
    String? characterId,
    String? voiceProfileId,
    String? audioFormat,
    String utterancePurpose = 'daily_advice',
  }) async {
    return VoiceOutputDemoRequestResponse(
      accepted: false,
      requestState: 'legacy_audio_ready',
      engine: 'framework',
      mode: 'framework_local',
      adapterMode: 'framework',
      realTtsEnabled: true,
      outputMode: outputMode,
      clientEventId: clientEventId,
      textContent: textContent,
      characterId: characterId,
      voiceProfileId: voiceProfileId,
      requestedAudioFormat: audioFormat,
      utterancePurpose: utterancePurpose,
      frameworkCallState: 'legacy_audio_ready',
      frameworkApiName: 'create_voice_output_session',
      audioUrl: '/__test__/legacy-voice-output.mp3',
      audioArtifactRef: null,
      audioFormat: 'mp3',
      audioReady: true,
      audioHandoffKind: 'url',
      hasAudioHandoff: true,
      isGenerated: false,
      audioPlaybackStatus: 'not_started',
      evidenceStatus: 'not_evidence',
      requestWarnings: const [],
      runtimeNotes: const [
        'Legacy URL responses are not FW v5 generated evidence by themselves.',
      ],
      capability: const DemoCapabilityStatus(
        status: 'available',
        source: 'framework_public_boundary',
        message: 'Framework voice output boundary is available.',
      ),
      message: 'Legacy audio URL must stay non-playable in the Web UI.',
      checks: const [],
      candidatePaths: const [],
      publicApiCandidates: const ['create_voice_output_session'],
    );
  }
}


class _FakeBackendApiClient extends BackendApiClient {
  const _FakeBackendApiClient({super.baseUrl = BackendApiClient.defaultBaseUrl});

  @override
  Future<String> fetchHealthStatus() async {
    return 'ok / API v2.0.1';
  }


  @override
  Future<DemoStatus> fetchDemoStatus() async {
    return const DemoStatus(
      engine: 'mock',
      mode: 'mock_safe',
      capabilities: {
        'llm_response': DemoCapabilityStatus(
          status: 'unavailable',
          source: 'mock',
          message: 'LLM response is unavailable in mock mode.',
        ),
        'voice_input': DemoCapabilityStatus(
          status: 'unavailable',
          source: 'not_implemented',
          message: 'Voice input demo is planned for a later version.',
        ),
        'voice_output': DemoCapabilityStatus(
          status: 'unavailable',
          source: 'not_implemented',
          message: 'Voice output/TTS demo is planned for a later version.',
        ),
        'live2d_motion': DemoCapabilityStatus(
          status: 'unavailable',
          source: 'not_implemented',
          message: 'Live2D/VTS motion demo is planned for a later version.',
        ),
        'google_health_real_api': DemoCapabilityStatus(
          status: 'skipped',
          source: 'mock_sleep_provider',
          message: 'Google Health real API is skipped in mock-safe mode.',
        ),
      },
    );
  }


  @override
  Future<VoiceInputDemoRequestResponse> submitVoiceInputDemoRequest({
    required String clientEventId,
    String inputMode = 'demo_button',
    String? textHint,
  }) async {
    return VoiceInputDemoRequestResponse(
      accepted: false,
      requestState: 'not_started',
      engine: 'mock',
      mode: 'mock_safe',
      adapterMode: 'disabled',
      inputMode: inputMode,
      clientEventId: clientEventId,
      capability: const DemoCapabilityStatus(
        status: 'unavailable',
        source: 'not_configured',
        message: 'Voice input demo is disabled.',
      ),
      transcript: null,
      message:
          'Voice input demo request was received, but no audio was processed because voice input is unavailable / not_configured.',
      checks: const [
        VoiceInputDemoProbeCheck(
          name: 'voice_input_demo_enabled',
          status: 'skip',
          message: 'Voice input demo is disabled.',
        ),
      ],
      candidatePaths: const [],
    );
  }

  @override
  Future<VoiceOutputDemoRequestResponse> submitVoiceOutputDemoRequest({
    required String clientEventId,
    String outputMode = 'tts',
    String? textContent,
    String? characterId,
    String? voiceProfileId,
    String? audioFormat,
    String utterancePurpose = 'daily_advice',
  }) async {
    return VoiceOutputDemoRequestResponse(
      accepted: false,
      requestState: 'not_started',
      engine: 'mock',
      mode: 'mock_safe',
      adapterMode: 'disabled',
      realTtsEnabled: false,
      outputMode: outputMode,
      clientEventId: clientEventId,
      textContent: textContent,
      characterId: characterId,
      voiceProfileId: voiceProfileId,
      requestedAudioFormat: audioFormat,
      utterancePurpose: utterancePurpose,
      frameworkCallState: 'not_called',
      audioUrl: null,
      audioFormat: null,
      audioPlaybackStatus: 'not_started',
      evidenceStatus: 'not_evidence',
      requestWarnings: const [],
      runtimeNotes: const [],
      capability: const DemoCapabilityStatus(
        status: 'unavailable',
        source: 'not_configured',
        message: 'Voice output demo is disabled.',
      ),
      message:
          'Voice output demo request was received, but no audio was generated because voice output is unavailable / not_configured.',
      checks: const [
        VoiceOutputDemoProbeCheck(
          name: 'voice_output_demo_enabled',
          status: 'skip',
          message: 'Voice output demo is disabled.',
        ),
      ],
      candidatePaths: const [],
      publicApiCandidates: const [],
    );
  }



  @override
  Future<MotionDemoRequestResponse> submitMotionDemoRequest({
    required String clientEventId,
    String motionEvent = 'idle',
    String? characterId,
    String? expressionId,
    String triggerSource = 'manual',
    String requestedAdapterMode = 'simulator',
  }) async {
    return MotionDemoRequestResponse(
      accepted: false,
      requestState: 'not_started',
      engine: 'mock',
      mode: 'mock_safe',
      adapterMode: 'disabled',
      motionEvent: motionEvent,
      clientEventId: clientEventId,
      characterId: characterId,
      expressionId: expressionId,
      triggerSource: triggerSource,
      requestedAdapterMode: requestedAdapterMode,
      resolvedAdapterMode: 'disabled',
      motionSent: false,
      vtsConnectionUsed: false,
      requestWarnings: const [],
      capability: const DemoCapabilityStatus(
        status: 'unavailable',
        source: 'not_configured',
        message: 'Motion demo is disabled.',
      ),
      message:
          'Motion demo request was received, but no Live2D/VTS motion was sent because motion is unavailable / not_configured.',
      supportedMotionEvents: const [
        'greeting',
        'thinking',
        'happy',
        'tired_supportive',
        'speaking',
        'idle',
      ],
      supportedCharacterIds: const [
        'gentle_mina',
        'cheerful_sora',
        'cool_rei',
      ],
      supportedExpressionIds: const [
        'idle',
        'happy',
        'thinking',
        'supportive',
        'speaking',
      ],
    );
  }


  @override
  Future<ChatSession> createPostAdviceChatSession({
    required CharacterPreset character,
    required AdviceResponse adviceResponse,
    required String mood,
    String? initialUserMessage,
  }) async {
    return ChatSession(
      sessionId: 'chat_test_001',
      status: 'active',
      source: ChatSource(
        engine: 'mock',
        mode: 'post_advice_chat',
        drcCharacterId: character.characterId,
        drcCharacterName: character.displayName,
      ),
      context: PostAdviceChatContext(
        character: character,
        adviceMessage: adviceResponse.message,
        mood: mood,
        adviceSource: adviceResponse.source,
      ),
      messages: [
        ChatMessage(
          role: 'assistant',
          content: '${character.displayName}です。さっきのアドバイスについて、もう少し話せるよ。',
        ),
      ],
    );
  }

  @override
  Future<ChatMessageResponse> sendPostAdviceChatMessage({
    required String sessionId,
    required String message,
  }) async {
    return ChatMessageResponse(
      sessionId: sessionId,
      reply: ChatMessage(
        role: 'assistant',
        content: 'Defaultです。$message について、今日は小さく試してみましょう。',
      ),
      source: const ChatSource(
        engine: 'mock',
        mode: 'post_advice_chat',
        drcCharacterId: 'default',
        drcCharacterName: 'Default',
      ),
      messages: [
        const ChatMessage(
          role: 'assistant',
          content: 'Defaultです。さっきのアドバイスについて、もう少し話せるよ。',
        ),
        ChatMessage(role: 'user', content: message),
        ChatMessage(
          role: 'assistant',
          content: 'Defaultです。$message について、今日は小さく試してみましょう。',
        ),
      ],
    );
  }

  @override
  Future<List<CharacterPreset>> fetchCharacters() async {
    return const [
      CharacterPreset(
        characterId: 'default',
        displayName: 'Default',
        description: 'Default test character',
        personalityType: 'friendly',
        speakingStyle: 'casual',
        adviceStyle: 'light',
      ),
    ];
  }

  @override
  Future<SleepSummary> fetchSleepSummary() async {
    return const SleepSummary(
      date: '2026-05-04',
      totalSleepMinutes: 420,
      efficiency: 88,
      deepSleepMinutes: 80,
      remSleepMinutes: 90,
      awakeMinutes: 20,
      source: 'google_health',
      available: true,
      sleepStart: '2026-05-03T15:00:00Z',
      sleepEnd: '2026-05-03T22:00:00Z',
      qualityLabel: 'good',
      confidence: 'medium',
      isRealData: true,
    );
  }

  @override
  Future<SleepProviderSelectionStatus>
      fetchSleepProviderSelectionStatus() async {
    return const SleepProviderSelectionStatus(
      configuredProvider: 'google_health',
      configuredProviderLabel: 'Google Health',
      configuredProviderRole: 'configured_real_provider',
      configuredProviderSupported: true,
      selectionMode: 'backend_config',
      changeRequiresBackendRestart: true,
      availableProviders: [
        SleepProviderOption(
          provider: 'mock',
          displayLabel: 'サンプルデータ',
          role: 'credential_free_default',
        ),
        SleepProviderOption(
          provider: 'google_health',
          displayLabel: 'Google Health',
          role: 'configured_real_provider',
        ),
        SleepProviderOption(
          provider: 'fitbit',
          displayLabel: 'Fitbit（旧Web API・移行参照）',
          role: 'legacy_migration_reference',
          realOperatorVerificationRequired: false,
        ),
      ],
      message: 'Selected by backend configuration.',
    );
  }

  @override
  Future<FitbitStatus> fetchFitbitStatus() async {
    return const FitbitStatus(
      connected: false,
      provider: 'google_health',
      message: 'Google Health is not connected yet.',
    );
  }

  @override
  Future<FitbitConnectResponse> fetchFitbitConnect() async {
    return const FitbitConnectResponse(
      ready: false,
      connectUrl: null,
      message: 'Connect URL is not ready.',
    );
  }

  @override
  Future<AdviceResponse> createAdvice({
    required CharacterPreset character,
    required SleepSummary sleepSummary,
    required String mood,
  }) async {
    return AdviceResponse(
      message: '${character.displayName}です。Google Healthの実データでは、昨夜の睡眠は${sleepSummary.formattedTotalSleep}くらいですね。今の気分をふまえて、今日は無理なく整えていきましょう。',
      characterName: character.displayName,
      source: AdviceSource(
        engine: 'mock',
        drcCharacterId: character.characterId,
        drcCharacterName: character.displayName,
      ),
    );
  }


  @override
  Future<GoogleHealthConnectionUx> fetchGoogleHealthConnectionUx() async {
    return const GoogleHealthConnectionUx(
      provider: 'google_health',
      state: 'mock_mode',
      severity: 'info',
      title: 'モック睡眠データで動作中',
      message: '現在はGoogle Health連携ではなく、開発用のモック睡眠データを使っています。',
      statusSummary: '通常のローカル開発では安全なモック睡眠データを使います。',
      userGuidance: '通常の確認はこのままでOKです。外部の健康データ取得は使わず、安全なモック睡眠データで日次ループを確認します。',
      safeGuardSummary: 'real API requests は通常OFFです。mock-safeまたはsafe previewで確認します。',
      stateStage: 'Mock-safe development',
      stateReason: 'SLEEP_PROVIDER is not google_health, so the daily loop is using mock sleep data.',
      stateDetails: [
        GoogleHealthConnectionUxStateDetail(
          key: 'safe_default',
          label: 'Safe default',
          value: 'mock sleep',
          tone: 'ready',
          guidance: 'This is the expected state for ordinary local UI and daily loop checks.',
        ),
      ],
      nextAction: '通常のローカル開発ではこの状態でOKです。',
      recoverySteps: [
        '日次ループやUI確認は、このままモック睡眠データで続ける。',
        'Google Healthを試す時だけ、sleep providerをgoogle_healthに切り替える。',
      ],
      safeModeNote: 'mock-safe が既定です。Google Health の実APIは、明示的な guarded real request 用フラグが揃うまで呼び出しません。',
      primaryAction: GoogleHealthConnectionUxAction(
        key: 'keep_mock_mode',
        label: 'このまま使う',
        description: '通常の開発・UI確認はモックモードで安全に続けられます。',
        enabled: true,
      ),
      secondaryActions: [
        GoogleHealthConnectionUxAction(
          key: 'review_google_health_setup_later',
          label: 'Google Health設定は後で確認',
          description: '実データ連携の検証時だけ、接続設定とOAuth状態を確認します。',
          enabled: true,
          actionType: 'review',
          guidance: '必要になった時だけ接続状態を確認します。',
          expectedResult: 'mock-safeのまま接続作業を先送りできます。',
        ),
      ],
      connectionActions: [
        GoogleHealthConnectionUxAction(
          key: 'keep_mock_mode',
          label: 'このまま使う',
          description: '通常の開発・UI確認はモックモードで安全に続けられます。',
          enabled: true,
          actionType: 'continue',
          guidance: '日次ループ確認を優先する場合の安全な継続アクションです。',
          expectedResult: 'Google Health実APIを呼ばずにHome画面を確認できます。',
        ),
        GoogleHealthConnectionUxAction(
          key: 'review_google_health_setup_later',
          label: 'Google Health設定は後で確認',
          description: '実データ連携の検証時だけ、接続設定とOAuth状態を確認します。',
          enabled: true,
          actionType: 'review',
          guidance: '必要になった時だけ接続状態を確認します。',
          expectedResult: 'mock-safeのまま接続作業を先送りできます。',
        ),
      ],
      retryActions: [
        GoogleHealthConnectionUxAction(
          key: 'refresh_google_health_connection_status',
          label: '状態を再読み込み',
          description: '設定や認証状態を変えた後に、Google Health接続状態を再取得します。',
          enabled: true,
          actionType: 'retry',
          guidance: '設定変更・OAuth完了・token reset後に使う再確認アクションです。',
          expectedResult: '最新の接続状態を再表示します。',
        ),
      ],
      sleepProvider: 'mock',
      tokenStored: false,
      reconnectRecommended: false,
      realApiRequested: false,
      realApiAllowed: false,
      canStartOauth: false,
      canResetLocalToken: false,
      canUseSafePreview: false,
      canUseGuardedRealRequest: false,
      developerStatus: 'mock_mode',
      developerNote: 'このUXレスポンスは token / secret / local path / raw command / raw health payload を含めないユーザー向けサマリーです。詳細確認は developer check 側に寄せます。',
      developerSummary: 'SLEEP_PROVIDER is not google_health; Google Health connection work is intentionally inactive.',
      developerDetails: [
        GoogleHealthConnectionUxStateDetail(
          key: 'developer_status',
          label: 'Checklist status',
          value: 'mock_mode',
          tone: 'warning',
          guidance: 'Developer-only readiness summary. It does not include token values or local file paths.',
        ),
      ],
      userVisibleDetailsLimited: true,
      error: null,
    );
  }

  @override
  Future<GoogleHealthDiagnostics> fetchGoogleHealthDiagnostics() async {
    return const GoogleHealthDiagnostics(
      provider: 'google_health',
      overallStatus: 'needs_credentials',
      readyForOauth: true,
      readyForSleepProvider: true,
      readyForRealApiRequest: false,
      config: GoogleHealthDiagnosticConfig(
        sleepProvider: 'google_health',
        provider: 'google_health',
        oauthConfigured: true,
        credentialsFileConfigured: false,
        credentialsLoaded: false,
        redirectUriConfigured: true,
        realTokenExchangeEnabled: false,
        realTokenRefreshEnabled: false,
        realApiRequestsEnabled: false,
        endpointVerified: false,
      ),
      runtimeGuard: GoogleHealthDiagnosticRuntimeGuard(
        realApiRequested: false,
        realApiAllowed: false,
        apiBaseUrlPlaceholder: true,
        endpointVerified: false,
        sleepApiPathConfigured: true,
        apiTimeoutValid: true,
        message: 'Real Google Health API calls are blocked by guard.',
        nextAction: 'Verify endpoint and scope before enabling real API requests.',
      ),
      token: GoogleHealthDiagnosticToken(
        stored: false,
        hasRefreshToken: false,
        accessTokenExpired: null,
        refreshRecommended: null,
        expiresAt: null,
        tokenType: null,
        scopeConfigured: true,
      ),
      message: 'Credentials are not loaded yet.',
    );
  }

  @override
  Future<GoogleHealthPreflight> fetchGoogleHealthPreflight() async {
    return const GoogleHealthPreflight(
      provider: 'google_health',
      status: 'needs_credentials',
      readyForOauth: false,
      readyForAuthCallback: false,
      readyForTokenRefresh: false,
      readyForRealApiRequest: false,
      credentials: GoogleHealthPreflightCredentials(
        credentialsFileConfigured: true,
        credentialsFileExists: false,
        credentialsLoaded: false,
        clientIdConfigured: true,
        clientSecretConfigured: true,
        redirectUriConfigured: true,
        redirectUriRegistered: null,
        message: 'Credentials file is not available.',
      ),
      oauth: GoogleHealthPreflightOAuth(
        scopesConfigured: true,
        scopeCount: 2,
        authUrlReady: false,
        stateReady: false,
        message: 'OAuth URL was not prepared.',
      ),
      token: GoogleHealthPreflightToken(
        stored: false,
        hasRefreshToken: false,
        accessTokenExpired: null,
        refreshRecommended: null,
        scopeConfigured: false,
      ),
      api: GoogleHealthPreflightApi(
        realTokenExchangeEnabled: false,
        realTokenRefreshEnabled: false,
        realApiRequestsEnabled: false,
        realApiRequestsAllowed: false,
        endpointVerified: false,
        apiBaseUrlPlaceholder: true,
        sleepApiPathConfigured: true,
        apiTimeoutValid: true,
        message: 'Real API calls are blocked by guard.',
      ),
      message: 'Google Health credentials are not ready.',
      nextAction: 'Set credentials.json before real API testing.',
    );
  }

  @override
  Future<GoogleHealthSelfCheck> fetchGoogleHealthSelfCheck() async {
    return const GoogleHealthSelfCheck(
      provider: 'google_health',
      targetDate: '2026-05-04',
      diagnosticsStatus: 'needs_credentials',
      sourceStatus: 'blocked',
      safeToUseSleepSummary: true,
      realHttpAttempted: false,
      session: GoogleHealthSelfCheckSession(
        tokenAvailable: false,
        refreshChecked: false,
        apiRequested: false,
        succeeded: false,
        endpoint: null,
        refresh: GoogleHealthSelfCheckRefresh(
          checked: false,
          attempted: false,
          requestPrepared: false,
          realRefreshEnabled: false,
          refreshed: false,
          saved: false,
          message: 'Refresh was not attempted.',
        ),
        api: GoogleHealthSelfCheckApi(
          requested: false,
          attempted: false,
          requestPrepared: false,
          realApiEnabled: false,
          succeeded: false,
          statusCode: null,
          message: 'Real API request was not attempted.',
        ),
        message: 'Guard blocked real API access.',
      ),
      message: 'Self-check completed without raw HTTP access.',
    );
  }

  @override
  Future<RecentSleepTrend> fetchRecentSleepTrend({
    String? referenceDate,
    int days = 7,
  }) async {
    return const RecentSleepTrend(
      referenceDate: '2026-05-17',
      days: 7,
      label: 'recently_short',
      usableRecordCount: 3,
      averageTotalSleepMinutes: 340,
      recentDates: ['2026-05-08', '2026-05-07', '2026-05-06'],
      message: 'Recent usable records suggest shorter sleep than ideal.',
      displayLabel: '最近は短め傾向',
      displaySummary: '直近の使える記録では、平均睡眠が5時間40分で短めの傾向です。',
      displayNote: '履歴から見た参考情報です。今日の睡眠データや健康状態の断定には使いません。',
    );
  }

  @override
  Future<WeeklySleepSummary> fetchWeeklySleepSummary({
    String? referenceDate,
    int days = 7,
  }) async {
    return const WeeklySleepSummary(
      referenceDate: '2026-05-17',
      days: 7,
      label: 'weekly_short',
      usableRecordCount: 3,
      averageTotalSleepMinutes: 340,
      recentDates: ['2026-05-08', '2026-05-07', '2026-05-06'],
      displayLabel: '今週は短め寄り',
      displaySummary: '直近の使える記録では、平均睡眠が5時間40分で短め寄りです。予定や休憩を軽く見直す参考にできます。',
      displayCoverage: '対象: 直近7日 / 使用記録: 3件',
      displayNote: '過去のDailyRecordから作る軽い振り返りです。今日の睡眠や健康状態の診断には使いません。',
      actionHint: '短めの日が続く時は、無理な予定を詰めすぎない参考にしてください。',
    );
  }



  @override
  Future<RhythmReport> fetchRhythmReport({
    String period = 'weekly',
    String? referenceDate,
  }) async {
    if (period == 'monthly') {
      return const RhythmReport(
        period: 'monthly',
        referenceDate: '2026-05-17',
        rangeStart: '2026-04-18',
        rangeEnd: '2026-05-17',
        days: 30,
        label: 'monthly_sparse',
        totalRecordCount: 3,
        usableSleepRecordCount: 3,
        averageTotalSleepMinutes: 340,
        recordDates: ['2026-05-08', '2026-05-07', '2026-05-06'],
        displayTitle: 'Monthly Rhythm Report',
        displayLabel: '月次リズムは参考程度',
        displaySummary: '月次としては記録が少ないので、今は参考メモとして見てください。',
        displayCoverage: '対象: 直近30日 / 保存記録: 3件 / 使用記録: 3件',
        displayNote: '過去のDailyRecordから作る軽い振り返りです。今日の睡眠や健康状態の診断には使いません。',
        actionHint: 'まずはDailyRecordをためて、あとで月の流れを見返します。',
        sourceLabel: 'saved_daily_record_history_with_mock_sleep',
        dataScope: 'monthly_history',
        dataQuality: 'partial',
        isMedicalAdvice: false,
      );
    }

    return const RhythmReport(
      period: 'weekly',
      referenceDate: '2026-05-17',
      rangeStart: '2026-05-11',
      rangeEnd: '2026-05-17',
      days: 7,
      label: 'weekly_short',
      totalRecordCount: 3,
      usableSleepRecordCount: 3,
      averageTotalSleepMinutes: 340,
      recordDates: ['2026-05-08', '2026-05-07', '2026-05-06'],
      displayTitle: 'Weekly Rhythm Report',
      displayLabel: '週次リズムは短め寄り',
      displaySummary: '保存済み記録から見ると、平均睡眠は5時間40分で短め寄りです。予定や休憩を軽く見直す参考にできます。',
      displayCoverage: '対象: 直近7日 / 保存記録: 3件 / 使用記録: 3件',
      displayNote: '過去のDailyRecordから作る軽い振り返りです。今日の睡眠や健康状態の診断には使いません。',
      actionHint: '短めの日が続く時は、無理な予定を詰めすぎない参考にしてください。',
      sourceLabel: 'saved_daily_record_history_with_mock_sleep',
      dataScope: 'weekly_history',
      dataQuality: 'usable',
      isMedicalAdvice: false,
    );
  }

  @override
  Future<List<DailyRecord>> fetchDailyRecords({int limit = 30}) async {
    return [
      DailyRecord(
        date: '2026-05-08',
        characterId: 'gentle_mina',
        characterName: 'ミナ',
        mood: 'tired',
        sleepSummary: SleepSummary(
          date: '2026-05-08',
          totalSleepMinutes: 330,
          efficiency: 82,
          source: 'mock',
          available: true,
          message: 'Mock sleep summary is available.',
          qualityLabel: 'short',
          confidence: 'mock',
          isRealData: false,
        ),
        adviceMessage: '今日は回復優先でいきましょう。',
        adviceBasis: 'sleep+mood+character',
        adviceSource: AdviceSource(
          engine: 'mock',
          drcCharacterId: 'gentle_mina',
          drcCharacterName: 'ミナ',
        ),
        createdAt: '2026-05-08T13:59:04.157697+00:00',
        updatedAt: '2026-05-08T13:59:04.157697+00:00',
      ),
    ];
  }
}


class _MockProviderBackendApiClient extends _FakeBackendApiClient {
  const _MockProviderBackendApiClient();

  @override
  Future<SleepProviderSelectionStatus>
      fetchSleepProviderSelectionStatus() async {
    return const SleepProviderSelectionStatus(
      configuredProvider: 'mock',
      configuredProviderLabel: 'サンプルデータ',
      configuredProviderRole: 'credential_free_default',
      configuredProviderSupported: true,
      selectionMode: 'backend_config',
      changeRequiresBackendRestart: true,
      availableProviders: [
        SleepProviderOption(
          provider: 'mock',
          displayLabel: 'サンプルデータ',
          role: 'credential_free_default',
        ),
      ],
      message: 'Selected by backend configuration.',
    );
  }

  @override
  Future<SleepSummary> fetchSleepSummary() async {
    return const SleepSummary(
      date: '2026-05-04',
      totalSleepMinutes: 390,
      efficiency: 84,
      source: 'mock',
      available: true,
      isRealData: false,
    );
  }

  @override
  Future<FitbitStatus> fetchFitbitStatus() async {
    throw StateError('Mock provider must not query Fitbit status.');
  }
}


class _FitbitProviderBackendApiClient extends _FakeBackendApiClient {
  const _FitbitProviderBackendApiClient();

  @override
  Future<SleepProviderSelectionStatus>
      fetchSleepProviderSelectionStatus() async {
    return const SleepProviderSelectionStatus(
      configuredProvider: 'fitbit',
      configuredProviderLabel: 'Fitbit（旧Web API・移行参照）',
      configuredProviderRole: 'legacy_migration_reference',
      configuredProviderSupported: true,
      selectionMode: 'backend_config',
      changeRequiresBackendRestart: true,
      availableProviders: [
        SleepProviderOption(
          provider: 'fitbit',
          displayLabel: 'Fitbit（旧Web API・移行参照）',
          role: 'legacy_migration_reference',
          realOperatorVerificationRequired: false,
        ),
      ],
      message: 'Selected by backend configuration.',
    );
  }

  @override
  Future<SleepSummary> fetchSleepSummary() async {
    return const SleepSummary(
      date: '2026-05-04',
      totalSleepMinutes: 0,
      source: 'fitbit',
      available: false,
      isRealData: false,
      unavailableReason: 'refresh_required',
    );
  }

  @override
  Future<FitbitStatus> fetchFitbitStatus() async {
    return const FitbitStatus(
      connected: false,
      provider: 'fitbit',
      message: 'Local token-like fields were detected.',
      connectionState: 'token_present_unverified',
      verified: false,
    );
  }
}




class _MultiCharacterBackendApiClient extends _FakeBackendApiClient {
  const _MultiCharacterBackendApiClient();

  @override
  Future<List<CharacterPreset>> fetchCharacters() async {
    return const [
      CharacterPreset(
        characterId: 'gentle_mina',
        displayName: 'ミナ',
        description: '落ち着いて寄り添うキャラクター',
        personalityType: 'gentle',
        speakingStyle: 'calm',
        adviceStyle: 'supportive',
      ),
      CharacterPreset(
        characterId: 'cheerful_sora',
        displayName: 'ソラ',
        description: '明るく背中を押すキャラクター',
        personalityType: 'cheerful',
        speakingStyle: 'bright',
        adviceStyle: 'upbeat',
      ),
    ];
  }

  @override
  Future<AdviceResponse> createAdvice({
    required CharacterPreset character,
    required SleepSummary sleepSummary,
    required String mood,
  }) async {
    return AdviceResponse(
      message:
          '${character.displayName}です。${character.adviceStyle}な雰囲気で、今日の睡眠と気分に合わせて軽く整えていきましょう。',
      characterName: character.displayName,
      source: AdviceSource(
        engine: 'mock',
        drcCharacterId: character.characterId,
        drcCharacterName: character.displayName,
      ),
    );
  }
}


class _MoodCopyTrackingBackendApiClient extends _FakeBackendApiClient {
  String? lastMood;
  String? lastCharacterId;

  @override
  Future<List<CharacterPreset>> fetchCharacters() async {
    return const [
      CharacterPreset(
        characterId: 'gentle_mina',
        displayName: 'ミナ',
        description: '落ち着いて寄り添うキャラクター',
        personalityType: 'gentle',
        speakingStyle: 'calm',
        adviceStyle: 'supportive',
      ),
      CharacterPreset(
        characterId: 'cheerful_sora',
        displayName: 'ソラ',
        description: '明るく背中を押すキャラクター',
        personalityType: 'cheerful',
        speakingStyle: 'bright',
        adviceStyle: 'upbeat',
      ),
      CharacterPreset(
        characterId: 'cool_rei',
        displayName: 'レイ',
        description: '落ち着いて実用的に整理するキャラクター',
        personalityType: 'cool',
        speakingStyle: 'concise',
        adviceStyle: 'practical',
      ),
    ];
  }

  @override
  Future<AdviceResponse> createAdvice({
    required CharacterPreset character,
    required SleepSummary sleepSummary,
    required String mood,
  }) async {
    lastMood = mood;
    lastCharacterId = character.characterId;

    return AdviceResponse(
      message:
          '${character.displayName}です。mood=$mood / character=${character.characterId} の安定IDで受け取りました。',
      characterName: character.displayName,
      source: AdviceSource(
        engine: 'mock',
        drcCharacterId: character.characterId,
        drcCharacterName: character.displayName,
      ),
    );
  }
}


class _RecoveringInitialLoadBackendApiClient extends _FakeBackendApiClient {
  int _healthStatusCallCount = 0;

  @override
  Future<String> fetchHealthStatus() async {
    _healthStatusCallCount += 1;

    if (_healthStatusCallCount == 1) {
      throw Exception('temporary backend outage');
    }

    return 'ok / API v2.0.1';
  }
}


class _UnavailableSleepBackendApiClient extends _FakeBackendApiClient {
  const _UnavailableSleepBackendApiClient();

  @override
  Future<SleepSummary> fetchSleepSummary() async {
    return const SleepSummary(
      date: '2026-05-04',
      totalSleepMinutes: 0,
      source: 'google_health',
      available: false,
      message: 'Google Health returned no sleep dataPoints for the target date.',
      qualityLabel: 'unavailable',
      confidence: 'none',
      isRealData: false,
      unavailableReason: 'no_sleep_data_points',
    );
  }

  @override
  Future<AdviceResponse> createAdvice({
    required CharacterPreset character,
    required SleepSummary sleepSummary,
    required String mood,
  }) async {
    return AdviceResponse(
      message: '${character.displayName}です。今日は睡眠データを確認できなかったので、今の気分を中心に軽めに整えていきましょう。',
      characterName: character.displayName,
      source: AdviceSource(
        engine: 'framework_fallback',
        drcCharacterId: character.characterId,
        drcCharacterName: character.displayName,
      ),
    );
  }
}

class _FrameworkUnavailableChatBackendApiClient extends _FakeBackendApiClient {
  const _FrameworkUnavailableChatBackendApiClient();

  @override
  Future<ChatSession> createPostAdviceChatSession({
    required CharacterPreset character,
    required AdviceResponse adviceResponse,
    required String mood,
    String? initialUserMessage,
  }) async {
    return ChatSession(
      sessionId: 'chat_fw_unavailable_001',
      status: 'active',
      source: ChatSource(
        engine: 'framework',
        mode: 'framework_text_chat_boundary',
        drcCharacterId: character.characterId,
        drcCharacterName: character.displayName,
        frameworkPreset: 'text_chat',
        frameworkCharacter: 'default',
        frameworkCharacterSource: 'configured_env',
      ),
      context: PostAdviceChatContext(
        character: character,
        adviceMessage: adviceResponse.message,
        mood: mood,
        adviceSource: adviceResponse.source,
      ),
      messages: [
        ChatMessage(
          role: 'assistant',
          content:
              '${character.displayName}です。FWテキストチャット境界は有効化されています。まだ実FW呼び出しは行わず、未接続状態を安全に表示します。',
        ),
      ],
    );
  }

  @override
  Future<ChatMessageResponse> sendPostAdviceChatMessage({
    required String sessionId,
    required String message,
  }) async {
    return ChatMessageResponse(
      sessionId: sessionId,
      reply: const ChatMessage(
        role: 'assistant',
        content:
            'FWテキストチャットは有効化されていますが、FRAMEWORK_ROOT または FRAMEWORK_PROJECT_ROOT が未設定のため実行できません。',
      ),
      source: const ChatSource(
        engine: 'framework',
        mode: 'framework_text_chat_unavailable',
        drcCharacterId: 'default',
        drcCharacterName: 'Default',
        frameworkPreset: 'text_chat',
        frameworkCharacter: 'default',
        frameworkCharacterSource: 'configured_env',
      ),
      messages: [
        const ChatMessage(
          role: 'assistant',
          content:
              'Defaultです。FWテキストチャット境界は有効化されています。まだ実FW呼び出しは行わず、未接続状態を安全に表示します。',
        ),
        ChatMessage(role: 'user', content: message),
        const ChatMessage(
          role: 'assistant',
          content:
              'FWテキストチャットは有効化されていますが、FRAMEWORK_ROOT または FRAMEWORK_PROJECT_ROOT が未設定のため実行できません。',
        ),
      ],
    );
  }
}



