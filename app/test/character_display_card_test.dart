import 'package:app/models/advice_response.dart';
import 'package:app/models/character_display_presentation.dart';
import 'package:app/models/character_preset.dart';
import 'package:app/services/voice_output_audio_player.dart';
import 'package:app/ui/character_asset_catalog.dart';
import 'package:app/widgets/character_display_card.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('renders mood state with static character profile', (tester) async {
    await tester.pumpWidget(
      _app(
        presentation: _resolve(),
        imageAssetPath: CharacterAssetCatalog.imageForCharacter(
          _mina.characterId,
        ),
      ),
    );

    expect(find.byKey(const Key('character-display-card')), findsOneWidget);
    expect(find.text('気分: いつも通り'), findsOneWidget);
    expect(find.text('待機中'), findsOneWidget);
    expect(find.text('静的表示'), findsOneWidget);
    expect(find.text('ミナと今日の気分'), findsOneWidget);
    expect(find.text('gentle'), findsOneWidget);
    expect(find.text('casual'), findsOneWidget);
    expect(find.text('rest_focused'), findsOneWidget);

    final image = tester.widget<Image>(
      find.byKey(const ValueKey<String>('selected-character-image')),
    );
    expect(
      (image.image as AssetImage).assetName,
      CharacterAssetCatalog.characterImages['gentle_mina'],
    );
  });

  testWidgets('renders advice content without changing profile ownership', (
    tester,
  ) async {
    final presentation = _resolve(
      advice: const AdviceResponse(
        message: '少し早めに休憩しましょう。',
        characterName: 'ミナ',
      ),
    );

    await tester.pumpWidget(
      _app(
        presentation: presentation,
        imageAssetPath: CharacterAssetCatalog.imageForCharacter(
          _mina.characterId,
        ),
      ),
    );

    expect(find.text('アドバイス'), findsOneWidget);
    expect(find.text('ミナからのアドバイス'), findsOneWidget);
    expect(find.text('少し早めに休憩しましょう。'), findsOneWidget);
    expect(find.text('ミナ'), findsOneWidget);
  });

  testWidgets('shows deterministic loading and speaking activity', (
    tester,
  ) async {
    await tester.pumpWidget(
      _app(
        presentation: _resolve(isLoading: true),
        imageAssetPath: CharacterAssetCatalog.fallbackCharacter,
      ),
    );

    expect(find.text('準備中'), findsOneWidget);
    expect(find.byType(CircularProgressIndicator), findsOneWidget);

    await tester.pumpWidget(
      _app(
        presentation: _resolve(
          isLoading: true,
          playbackPhase: VoiceOutputPlaybackPhase.playing,
        ),
        imageAssetPath: CharacterAssetCatalog.fallbackCharacter,
      ),
    );
    await tester.pump();

    expect(find.text('音声再生中'), findsOneWidget);
    expect(find.byIcon(Icons.volume_up_outlined), findsOneWidget);
    expect(find.byType(CircularProgressIndicator), findsNothing);
  });

  testWidgets('fallback presentation uses safe static-runtime wording', (
    tester,
  ) async {
    final presentation = _resolve(
      character: null,
      hasRepositoryCharacterAsset: false,
    );

    await tester.pumpWidget(
      _app(
        character: null,
        presentation: presentation,
        imageAssetPath: CharacterAssetCatalog.fallbackCharacter,
      ),
    );

    expect(find.text('代替表示'), findsOneWidget);
    expect(find.text('未選択'), findsOneWidget);
    expect(
      find.byKey(const Key('character-display-fallback-note')),
      findsOneWidget,
    );
    expect(find.textContaining('Live2D / VTube Studio'), findsOneWidget);
    expect(find.textContaining('実行状態は表していません'), findsOneWidget);
  });
}

Widget _app({
  CharacterPreset? character = _mina,
  required CharacterDisplayPresentation presentation,
  required String imageAssetPath,
}) {
  return MaterialApp(
    home: Scaffold(
      body: SingleChildScrollView(
        child: CharacterDisplayCard(
          character: character,
          presentation: presentation,
          imageAssetPath: imageAssetPath,
        ),
      ),
    ),
  );
}

CharacterDisplayPresentation _resolve({
  CharacterPreset? character = _mina,
  AdviceResponse? advice,
  bool isLoading = false,
  VoiceOutputPlaybackPhase playbackPhase = VoiceOutputPlaybackPhase.idle,
  bool hasRepositoryCharacterAsset = true,
}) {
  return CharacterDisplayPresentation.resolve(
    character: character,
    moodLabel: 'いつも通り',
    moodSupportMessage: '今日は穏やかに整えます。',
    advice: advice,
    isLoading: isLoading,
    playbackPhase: playbackPhase,
    hasRepositoryCharacterAsset: hasRepositoryCharacterAsset,
  );
}

const CharacterPreset _mina = CharacterPreset(
  characterId: 'gentle_mina',
  displayName: 'ミナ',
  description: 'やさしい伴走役',
  personalityType: 'gentle',
  speakingStyle: 'casual',
  adviceStyle: 'rest_focused',
);
