import 'package:app/models/advice_response.dart';
import 'package:app/models/advice_source.dart';
import 'package:app/models/character_display_presentation.dart';
import 'package:app/models/character_preset.dart';
import 'package:app/services/voice_output_audio_player.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('CharacterDisplayPresentation', () {
    test('uses mood content before advice exists', () {
      final presentation = _resolve();

      expect(presentation.contentState, CharacterDisplayContentState.mood);
      expect(presentation.contentLabel, '気分: いつも通り');
      expect(presentation.title, 'ミナと今日の気分');
      expect(presentation.message, contains('穏やか'));
      expect(presentation.fallbackReason, isNull);
    });

    test('uses non-empty advice ahead of mood content', () {
      final presentation = _resolve(
        advice: const AdviceResponse(
          message: '今日は小さく休憩を入れましょう。',
          characterName: 'ミナ',
        ),
      );

      expect(presentation.contentState, CharacterDisplayContentState.advice);
      expect(presentation.contentLabel, 'アドバイス');
      expect(presentation.message, '今日は小さく休憩を入れましょう。');
    });

    test('empty advice remains mood content', () {
      final presentation = _resolve(
        advice: const AdviceResponse(
          message: '   ',
          characterName: 'ミナ',
        ),
      );

      expect(presentation.contentState, CharacterDisplayContentState.mood);
    });

    test('framework fallback uses safe app copy instead of provider text', () {
      final presentation = _resolve(
        advice: const AdviceResponse(
          message: 'provider-private-message',
          characterName: 'ミナ',
          source: AdviceSource(
            engine: 'framework_fallback',
            drcCharacterId: 'gentle_mina',
            drcCharacterName: 'ミナ',
          ),
        ),
      );

      expect(presentation.contentState, CharacterDisplayContentState.fallback);
      expect(
        presentation.fallbackReason,
        CharacterDisplayFallbackReason.frameworkFallback,
      );
      expect(presentation.message, isNot(contains('provider-private-message')));
      expect(presentation.message, contains('安全な代替アドバイス'));
    });

    test('missing character wins before other content', () {
      final presentation = _resolve(
        character: null,
        advice: const AdviceResponse(
          message: '通常アドバイス',
          characterName: '不明',
        ),
      );

      expect(presentation.contentState, CharacterDisplayContentState.fallback);
      expect(
        presentation.fallbackReason,
        CharacterDisplayFallbackReason.characterUnavailable,
      );
    });

    test('missing repository asset produces asset fallback', () {
      final presentation = _resolve(hasRepositoryCharacterAsset: false);

      expect(presentation.contentState, CharacterDisplayContentState.fallback);
      expect(
        presentation.fallbackReason,
        CharacterDisplayFallbackReason.assetUnavailable,
      );
      expect(presentation.message, contains('リポジトリ内の代替表示'));
    });

    test('speaking wins over simultaneous loading', () {
      final presentation = _resolve(
        isLoading: true,
        playbackPhase: VoiceOutputPlaybackPhase.playing,
      );

      expect(
        presentation.activityState,
        CharacterDisplayActivityState.speaking,
      );
      expect(presentation.activityLabel, '音声再生中');
    });

    test('app or player loading resolves to loading', () {
      final appLoading = _resolve(isLoading: true);
      final playerLoading = _resolve(
        playbackPhase: VoiceOutputPlaybackPhase.loading,
      );

      expect(appLoading.activityState, CharacterDisplayActivityState.loading);
      expect(playerLoading.activityState, CharacterDisplayActivityState.loading);
      expect(playerLoading.activityMessage, '表示内容を準備しています。');
    });

    test('terminal playback phases return to idle presentation', () {
      for (final phase in <VoiceOutputPlaybackPhase>[
        VoiceOutputPlaybackPhase.stopped,
        VoiceOutputPlaybackPhase.completed,
        VoiceOutputPlaybackPhase.failed,
        VoiceOutputPlaybackPhase.expired,
      ]) {
        final presentation = _resolve(playbackPhase: phase);
        expect(
          presentation.activityState,
          CharacterDisplayActivityState.idle,
          reason: 'phase=$phase',
        );
      }
    });
  });
}

CharacterDisplayPresentation _resolve({
  CharacterPreset? character = _mina,
  String moodLabel = 'いつも通り',
  String moodSupportMessage = '今日は穏やかに整えます。',
  AdviceResponse? advice,
  bool isLoading = false,
  VoiceOutputPlaybackPhase playbackPhase = VoiceOutputPlaybackPhase.idle,
  bool hasRepositoryCharacterAsset = true,
}) {
  return CharacterDisplayPresentation.resolve(
    character: character,
    moodLabel: moodLabel,
    moodSupportMessage: moodSupportMessage,
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
