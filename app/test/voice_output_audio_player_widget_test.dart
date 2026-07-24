import 'dart:async';

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
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('in-app player supports play stop and replay', (tester) async {
    final apiClient = _AudioReadyBackendApiClient();
    final engine = _FakeVoiceOutputAudioEngine();

    await tester.pumpWidget(
      MaterialApp(
        home: HomeScreen(
          apiClient: apiClient,
          voiceOutputAudioEngine: engine,
        ),
      ),
    );
    await tester.pumpAndSettle();

    await _submitVoiceOutputRequest(tester);

    expect(find.text('アプリ内音声プレイヤー'), findsOneWidget);
    expect(find.text('音声を再生する'), findsOneWidget);
    expect(find.textContaining('/demo/voice-output/audio/'), findsNothing);

    final playButton = find.byKey(const Key('voice-output-play-button'));
    await tester.ensureVisible(playButton);
    await tester.tap(playButton);
    await tester.pumpAndSettle();

    expect(engine.loadedSources, hasLength(1));
    expect(engine.loadedSources.single.toString(),
        'http://203.0.113.20:8000/demo/voice-output/audio/opaque-test-id');
    expect(engine.playCalls, 1);
    expect(find.text('音声を再生しています。'), findsOneWidget);
    expect(find.text('停止する'), findsOneWidget);

    final stopButton = find.byKey(const Key('voice-output-stop-button'));
    await tester.tap(stopButton);
    await tester.pumpAndSettle();

    expect(engine.stopCalls, greaterThanOrEqualTo(1));
    expect(find.text('音声を停止しました。'), findsOneWidget);
    expect(find.text('もう一度再生する'), findsOneWidget);

    final replayButton = find.byKey(const Key('voice-output-replay-button'));
    await tester.tap(replayButton);
    await tester.pumpAndSettle();

    expect(engine.seekToStartCalls, 1);
    expect(engine.playCalls, 2);
    expect(find.text('音声を再生しています。'), findsOneWidget);
  });

  testWidgets('completion exposes replay without printing the source URL', (
    tester,
  ) async {
    final engine = _FakeVoiceOutputAudioEngine();

    await tester.pumpWidget(
      MaterialApp(
        home: HomeScreen(
          apiClient: _AudioReadyBackendApiClient(),
          voiceOutputAudioEngine: engine,
        ),
      ),
    );
    await tester.pumpAndSettle();
    await _submitVoiceOutputRequest(tester);

    final playButton = find.byKey(const Key('voice-output-play-button'));
    await tester.ensureVisible(playButton);
    await tester.tap(playButton);
    await tester.pumpAndSettle();

    engine.emit(const VoiceOutputAudioEngineEvent(
      type: VoiceOutputAudioEngineEventType.completed,
    ));
    await tester.pumpAndSettle();

    expect(find.text('音声の再生が完了しました。'), findsOneWidget);
    expect(find.text('もう一度再生する'), findsOneWidget);
    expect(find.textContaining('opaque-test-id'), findsNothing);
  });

  testWidgets('expired artifact offers direct regeneration', (tester) async {
    final apiClient = _AudioReadyBackendApiClient();
    final engine = _FakeVoiceOutputAudioEngine(
      loadError: const VoiceOutputAudioEngineException(
        code: 'audio_artifact_not_found',
        expired: true,
      ),
    );

    await tester.pumpWidget(
      MaterialApp(
        home: HomeScreen(
          apiClient: apiClient,
          voiceOutputAudioEngine: engine,
        ),
      ),
    );
    await tester.pumpAndSettle();
    await _submitVoiceOutputRequest(tester);

    final playButton = find.byKey(const Key('voice-output-play-button'));
    await tester.ensureVisible(playButton);
    await tester.tap(playButton);
    await tester.pumpAndSettle();

    expect(find.text('この音声は期限切れです。音声を作り直してください。'), findsOneWidget);
    expect(find.text('音声を作り直す'), findsOneWidget);
    expect(find.text('もう一度再生する'), findsNothing);

    final regenerate = find.byKey(const Key('voice-output-regenerate-button'));
    await tester.tap(regenerate);
    await tester.pumpAndSettle();

    expect(apiClient.voiceOutputRequestCalls, 2);
    expect(find.text('音声を再生する'), findsOneWidget);
  });
}

Future<void> _submitVoiceOutputRequest(WidgetTester tester) async {
  final button = find.widgetWithText(FilledButton, 'Voice output demoを試す');
  await tester.ensureVisible(button);
  await tester.pumpAndSettle();
  await tester.tap(button);
  await tester.pumpAndSettle();
}

class _FakeVoiceOutputAudioEngine implements VoiceOutputAudioEngine {
  _FakeVoiceOutputAudioEngine({this.loadError});

  final Object? loadError;
  final StreamController<VoiceOutputAudioEngineEvent> _events =
      StreamController<VoiceOutputAudioEngineEvent>.broadcast(sync: true);

  final List<Uri> loadedSources = <Uri>[];
  int playCalls = 0;
  int stopCalls = 0;
  int seekToStartCalls = 0;

  @override
  Stream<VoiceOutputAudioEngineEvent> get events => _events.stream;

  void emit(VoiceOutputAudioEngineEvent event) => _events.add(event);

  @override
  Future<void> load(Uri source) async {
    loadedSources.add(source);
    if (loadError != null) {
      throw loadError!;
    }
  }

  @override
  Future<void> play() async {
    playCalls += 1;
  }

  @override
  Future<void> stop() async {
    stopCalls += 1;
  }

  @override
  Future<void> seekToStart() async {
    seekToStartCalls += 1;
  }

  @override
  Future<void> dispose() async {
    await _events.close();
  }
}

class _AudioReadyBackendApiClient extends BackendApiClient {
  _AudioReadyBackendApiClient()
      : super(baseUrl: 'http://203.0.113.20:8000');

  int voiceOutputRequestCalls = 0;

  @override
  Future<String> fetchHealthStatus() async => 'ok / API v2.0.1';

  @override
  Future<List<CharacterPreset>> fetchCharacters() async {
    return const <CharacterPreset>[
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
  Future<GoogleHealthConnectionUx> fetchGoogleHealthConnectionUx() async {
    throw Exception('not used by the focused voice-output fixture');
  }

  @override
  Future<GoogleHealthDiagnostics> fetchGoogleHealthDiagnostics() async {
    throw Exception('not used by the focused voice-output fixture');
  }

  @override
  Future<GoogleHealthSelfCheck> fetchGoogleHealthSelfCheck() async {
    throw Exception('not used by the focused voice-output fixture');
  }

  @override
  Future<GoogleHealthPreflight> fetchGoogleHealthPreflight() async {
    throw Exception('not used by the focused voice-output fixture');
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
    voiceOutputRequestCalls += 1;
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
      audioUrl: '/demo/voice-output/audio/opaque-test-id',
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
}
