import 'dart:async';

import 'package:app/models/advice_response.dart';
import 'package:app/models/advice_source.dart';
import 'package:app/models/character_preset.dart';
import 'package:app/models/demo_status.dart';
import 'package:app/models/google_health_connection_ux.dart';
import 'package:app/models/google_health_diagnostics.dart';
import 'package:app/models/google_health_preflight.dart';
import 'package:app/models/google_health_self_check.dart';
import 'package:app/models/sleep_provider_selection.dart';
import 'package:app/models/sleep_summary.dart';
import 'package:app/models/voice_output_demo.dart';
import 'package:app/screens/home_screen.dart';
import 'package:app/services/backend_api_client.dart';
import 'package:app/services/voice_output_audio_player.dart';
import 'package:app/ui/character_asset_catalog.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('HomeScreen shows deterministic loading before mood state', (
    tester,
  ) async {
    final healthStatus = Completer<String>();
    final apiClient = _CharacterDisplayBackendApiClient(
      healthStatusFuture: healthStatus.future,
    );

    await tester.pumpWidget(
      MaterialApp(
        home: HomeScreen(
          apiClient: apiClient,
          voiceOutputAudioEngine: _FakeVoiceOutputAudioEngine(),
        ),
      ),
    );
    await tester.pump();

    final card = find.byKey(const Key('character-display-card'));
    expect(card, findsOneWidget);
    expect(
      find.descendant(of: card, matching: find.text('準備中')),
      findsOneWidget,
    );
    expect(
      find.descendant(
        of: card,
        matching: find.text('キャラクターを準備しています'),
      ),
      findsOneWidget,
    );

    healthStatus.complete('ok / API v2.0.1');
    await tester.pumpAndSettle();

    expect(
      find.descendant(of: card, matching: find.text('気分: いつも通り')),
      findsOneWidget,
    );
    expect(
      find.descendant(of: card, matching: find.text('待機中')),
      findsOneWidget,
    );
  });

  testWidgets('mood and advice loading resolve into advice presentation', (
    tester,
  ) async {
    final advice = Completer<AdviceResponse>();
    final apiClient = _CharacterDisplayBackendApiClient(
      adviceFuture: advice.future,
    );

    await _pumpHome(tester, apiClient: apiClient);

    final card = find.byKey(const Key('character-display-card'));
    final tiredMood = find.widgetWithText(ChoiceChip, '😪 ちょっと休みたい');
    await tester.ensureVisible(tiredMood);
    await tester.tap(tiredMood);
    await tester.pumpAndSettle();

    expect(
      find.descendant(
        of: card,
        matching: find.text('気分: ちょっと休みたい'),
      ),
      findsOneWidget,
    );

    final adviceButton = find.widgetWithText(
      ElevatedButton,
      '今日のアドバイスを作る',
    );
    await tester.ensureVisible(adviceButton);
    await tester.tap(adviceButton);
    await tester.pump();

    expect(
      find.descendant(of: card, matching: find.text('準備中')),
      findsOneWidget,
    );

    advice.complete(
      const AdviceResponse(
        message: '今日は早めに休憩を入れましょう。',
        characterName: 'ミナ',
        source: AdviceSource(
          engine: 'mock',
          drcCharacterId: 'gentle_mina',
          drcCharacterName: 'ミナ',
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(
      find.descendant(of: card, matching: find.text('アドバイス')),
      findsOneWidget,
    );
    expect(
      find.descendant(
        of: card,
        matching: find.text('今日は早めに休憩を入れましょう。'),
      ),
      findsOneWidget,
    );
  });

  testWidgets('framework fallback uses safe copy inside character card', (
    tester,
  ) async {
    const privateProviderMessage = 'provider-private-message';
    final apiClient = _CharacterDisplayBackendApiClient(
      adviceResponse: const AdviceResponse(
        message: privateProviderMessage,
        characterName: 'ミナ',
        source: AdviceSource(
          engine: 'framework_fallback',
          drcCharacterId: 'gentle_mina',
          drcCharacterName: 'ミナ',
        ),
      ),
    );

    await _pumpHome(tester, apiClient: apiClient);
    await _createAdvice(tester);

    final card = find.byKey(const Key('character-display-card'));
    expect(
      find.descendant(of: card, matching: find.text('代替表示')),
      findsOneWidget,
    );
    expect(
      find.descendant(
        of: card,
        matching: find.text('安全な代替アドバイス'),
      ),
      findsOneWidget,
    );
    expect(
      find.descendant(
        of: card,
        matching: find.textContaining(privateProviderMessage),
      ),
      findsNothing,
    );
  });

  testWidgets('in-app audio playback drives speaking presentation', (
    tester,
  ) async {
    final engine = _FakeVoiceOutputAudioEngine();
    final apiClient = _CharacterDisplayBackendApiClient();

    await _pumpHome(
      tester,
      apiClient: apiClient,
      voiceOutputAudioEngine: engine,
    );

    final submitButton = find.widgetWithText(
      FilledButton,
      'Voice output demoを試す',
    );
    await tester.ensureVisible(submitButton);
    await tester.tap(submitButton);
    await tester.pumpAndSettle();

    final playButton = find.byKey(const Key('voice-output-play-button'));
    await tester.ensureVisible(playButton);
    await tester.tap(playButton);
    await tester.pumpAndSettle();

    final card = find.byKey(const Key('character-display-card'));
    expect(
      find.descendant(of: card, matching: find.text('音声再生中')),
      findsOneWidget,
    );
    expect(engine.playCalls, 1);
  });

  testWidgets('unknown character ID uses repository fallback presentation', (
    tester,
  ) async {
    final apiClient = _CharacterDisplayBackendApiClient(
      characters: const <CharacterPreset>[
        CharacterPreset(
          characterId: 'repository_unknown_character',
          displayName: 'Unknown',
          description: 'Unknown test character',
          personalityType: 'unknown',
          speakingStyle: 'unknown',
          adviceStyle: 'unknown',
        ),
      ],
    );

    await _pumpHome(tester, apiClient: apiClient);

    final card = find.byKey(const Key('character-display-card'));
    expect(
      find.descendant(of: card, matching: find.text('代替表示')),
      findsOneWidget,
    );
    expect(
      find.descendant(
        of: card,
        matching: find.text('共通のキャラクター表示'),
      ),
      findsOneWidget,
    );

    final image = tester.widget<Image>(
      find.byKey(const ValueKey<String>('selected-character-image')),
    );
    expect(
      (image.image as AssetImage).assetName,
      CharacterAssetCatalog.fallbackCharacter,
    );
  });
}

Future<void> _pumpHome(
  WidgetTester tester, {
  required _CharacterDisplayBackendApiClient apiClient,
  VoiceOutputAudioEngine? voiceOutputAudioEngine,
}) async {
  await tester.pumpWidget(
    MaterialApp(
      home: HomeScreen(
        apiClient: apiClient,
        voiceOutputAudioEngine:
            voiceOutputAudioEngine ?? _FakeVoiceOutputAudioEngine(),
      ),
    ),
  );
  await tester.pumpAndSettle();
}

Future<void> _createAdvice(WidgetTester tester) async {
  final adviceButton = find.widgetWithText(
    ElevatedButton,
    '今日のアドバイスを作る',
  );
  await tester.ensureVisible(adviceButton);
  await tester.tap(adviceButton);
  await tester.pumpAndSettle();
}

class _FakeVoiceOutputAudioEngine implements VoiceOutputAudioEngine {
  final StreamController<VoiceOutputAudioEngineEvent> _events =
      StreamController<VoiceOutputAudioEngineEvent>.broadcast(sync: true);

  int playCalls = 0;

  @override
  Stream<VoiceOutputAudioEngineEvent> get events => _events.stream;

  @override
  Future<void> load(Uri source) async {}

  @override
  Future<void> play() async {
    playCalls += 1;
  }

  @override
  Future<void> stop() async {}

  @override
  Future<void> seekToStart() async {}

  @override
  Future<void> dispose() async {
    await _events.close();
  }
}

class _CharacterDisplayBackendApiClient extends BackendApiClient {
  _CharacterDisplayBackendApiClient({
    this.healthStatusFuture,
    this.adviceFuture,
    this.adviceResponse = const AdviceResponse(
      message: '今日は無理なく過ごしましょう。',
      characterName: 'ミナ',
      source: AdviceSource(
        engine: 'mock',
        drcCharacterId: 'gentle_mina',
        drcCharacterName: 'ミナ',
      ),
    ),
    this.characters = const <CharacterPreset>[
      CharacterPreset(
        characterId: 'gentle_mina',
        displayName: 'ミナ',
        description: 'やさしい伴走役',
        personalityType: 'gentle',
        speakingStyle: 'casual',
        adviceStyle: 'rest_focused',
      ),
    ],
  }) : super(baseUrl: 'http://203.0.113.20:8000');

  final Future<String>? healthStatusFuture;
  final Future<AdviceResponse>? adviceFuture;
  final AdviceResponse adviceResponse;
  final List<CharacterPreset> characters;

  @override
  Future<String> fetchHealthStatus() async {
    return healthStatusFuture ?? 'ok / API v2.0.1';
  }

  @override
  Future<List<CharacterPreset>> fetchCharacters() async => characters;

  @override
  Future<SleepSummary> fetchSleepSummary() async {
    return const SleepSummary(
      date: '2026-07-24',
      totalSleepMinutes: 420,
      efficiency: 88,
      deepSleepMinutes: 80,
      remSleepMinutes: 90,
      awakeMinutes: 20,
      source: 'mock',
      available: true,
      isRealData: false,
    );
  }

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
      availableProviders: <SleepProviderOption>[
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
  Future<AdviceResponse> createAdvice({
    required CharacterPreset character,
    required SleepSummary sleepSummary,
    required String mood,
  }) async {
    return adviceFuture ?? adviceResponse;
  }

  @override
  Future<DemoStatus> fetchDemoStatus() async {
    return const DemoStatus(
      engine: 'mock',
      mode: 'mock_safe',
      capabilities: <String, DemoCapabilityStatus>{
        'voice_output': DemoCapabilityStatus(
          status: 'available',
          source: 'framework_public_boundary',
          message: 'Voice output is available for this fixture.',
        ),
      },
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
      audioUrl: '/demo/voice-output/audio/opaque-character-display-id',
      audioArtifactRef: null,
      audioFormat: 'mp3',
      audioReady: true,
      audioHandoffKind: 'url',
      hasAudioHandoff: true,
      isGenerated: true,
      audioPlaybackStatus: 'ready_for_in_app_playback',
      evidenceStatus: 'not_evidence',
      capability: const DemoCapabilityStatus(
        status: 'available',
        source: 'framework_public_boundary',
        message: 'Framework voice output boundary is available.',
      ),
      message: 'Generated audio is ready for in-app playback.',
    );
  }

  @override
  Future<GoogleHealthConnectionUx> fetchGoogleHealthConnectionUx() async {
    throw StateError('not used by character-display integration tests');
  }

  @override
  Future<GoogleHealthDiagnostics> fetchGoogleHealthDiagnostics() async {
    throw StateError('not used by character-display integration tests');
  }

  @override
  Future<GoogleHealthSelfCheck> fetchGoogleHealthSelfCheck() async {
    throw StateError('not used by character-display integration tests');
  }

  @override
  Future<GoogleHealthPreflight> fetchGoogleHealthPreflight() async {
    throw StateError('not used by character-display integration tests');
  }
}
