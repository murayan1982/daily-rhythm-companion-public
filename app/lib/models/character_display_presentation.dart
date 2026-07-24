import 'package:flutter/foundation.dart';

import '../services/voice_output_audio_player.dart';
import 'advice_response.dart';
import 'character_preset.dart';

enum CharacterDisplayContentState {
  mood,
  advice,
  fallback,
}

enum CharacterDisplayActivityState {
  idle,
  loading,
  speaking,
}

enum CharacterDisplayFallbackReason {
  characterUnavailable,
  assetUnavailable,
  frameworkFallback,
}

@immutable
class CharacterDisplayPresentation {
  const CharacterDisplayPresentation({
    required this.contentState,
    required this.activityState,
    required this.title,
    required this.message,
    required this.contentLabel,
    required this.activityLabel,
    required this.activityMessage,
    this.fallbackReason,
  });

  factory CharacterDisplayPresentation.resolve({
    required CharacterPreset? character,
    required String moodLabel,
    required String moodSupportMessage,
    required AdviceResponse? advice,
    required bool isLoading,
    required VoiceOutputPlaybackPhase playbackPhase,
    required bool hasRepositoryCharacterAsset,
  }) {
    final activityState = _resolveActivityState(
      isLoading: isLoading,
      playbackPhase: playbackPhase,
    );
    final activityCopy = _activityCopy(activityState);
    final fallbackReason = _resolveFallbackReason(
      character: character,
      advice: advice,
      hasRepositoryCharacterAsset: hasRepositoryCharacterAsset,
    );

    if (fallbackReason != null) {
      final fallbackCopy = _fallbackCopy(fallbackReason);
      return CharacterDisplayPresentation(
        contentState: CharacterDisplayContentState.fallback,
        activityState: activityState,
        title: fallbackCopy.title,
        message: fallbackCopy.message,
        contentLabel: '代替表示',
        activityLabel: activityCopy.label,
        activityMessage: activityCopy.message,
        fallbackReason: fallbackReason,
      );
    }

    final adviceMessage = advice?.message.trim() ?? '';
    if (adviceMessage.isNotEmpty) {
      return CharacterDisplayPresentation(
        contentState: CharacterDisplayContentState.advice,
        activityState: activityState,
        title: '${_characterName(character)}からのアドバイス',
        message: adviceMessage,
        contentLabel: 'アドバイス',
        activityLabel: activityCopy.label,
        activityMessage: activityCopy.message,
      );
    }

    final normalizedMoodLabel = moodLabel.trim();
    final normalizedMoodMessage = moodSupportMessage.trim();
    return CharacterDisplayPresentation(
      contentState: CharacterDisplayContentState.mood,
      activityState: activityState,
      title: '${_characterName(character)}と今日の気分',
      message: normalizedMoodMessage.isEmpty
          ? '今日の気分に合わせて、無理のない過ごし方を考えます。'
          : normalizedMoodMessage,
      contentLabel: normalizedMoodLabel.isEmpty
          ? '気分'
          : '気分: $normalizedMoodLabel',
      activityLabel: activityCopy.label,
      activityMessage: activityCopy.message,
    );
  }

  final CharacterDisplayContentState contentState;
  final CharacterDisplayActivityState activityState;
  final CharacterDisplayFallbackReason? fallbackReason;
  final String title;
  final String message;
  final String contentLabel;
  final String activityLabel;
  final String activityMessage;

  bool get isFallback => contentState == CharacterDisplayContentState.fallback;
  bool get isLoading => activityState == CharacterDisplayActivityState.loading;
  bool get isSpeaking => activityState == CharacterDisplayActivityState.speaking;

  static CharacterDisplayFallbackReason? _resolveFallbackReason({
    required CharacterPreset? character,
    required AdviceResponse? advice,
    required bool hasRepositoryCharacterAsset,
  }) {
    if (character == null) {
      return CharacterDisplayFallbackReason.characterUnavailable;
    }

    if (!hasRepositoryCharacterAsset) {
      return CharacterDisplayFallbackReason.assetUnavailable;
    }

    if (advice?.source?.engine.trim() == 'framework_fallback') {
      return CharacterDisplayFallbackReason.frameworkFallback;
    }

    return null;
  }

  static CharacterDisplayActivityState _resolveActivityState({
    required bool isLoading,
    required VoiceOutputPlaybackPhase playbackPhase,
  }) {
    if (playbackPhase == VoiceOutputPlaybackPhase.playing) {
      return CharacterDisplayActivityState.speaking;
    }

    if (isLoading || playbackPhase == VoiceOutputPlaybackPhase.loading) {
      return CharacterDisplayActivityState.loading;
    }

    return CharacterDisplayActivityState.idle;
  }

  static String _characterName(CharacterPreset? character) {
    final displayName = character?.displayName.trim() ?? '';
    return displayName.isEmpty ? 'キャラクター' : displayName;
  }

  static _CharacterDisplayCopy _fallbackCopy(
    CharacterDisplayFallbackReason reason,
  ) {
    switch (reason) {
      case CharacterDisplayFallbackReason.characterUnavailable:
        return const _CharacterDisplayCopy(
          title: 'キャラクターを準備しています',
          message: 'キャラクター情報を読み込めなかったため、共通の静的表示で案内します。',
        );
      case CharacterDisplayFallbackReason.assetUnavailable:
        return const _CharacterDisplayCopy(
          title: '共通のキャラクター表示',
          message: '選択した画像を確認できなかったため、リポジトリ内の代替表示を使用します。',
        );
      case CharacterDisplayFallbackReason.frameworkFallback:
        return const _CharacterDisplayCopy(
          title: '安全な代替アドバイス',
          message: 'AI応答を利用できなかったため、アプリの安全な代替アドバイスを表示しています。',
        );
    }
  }

  static _CharacterDisplayCopy _activityCopy(
    CharacterDisplayActivityState state,
  ) {
    switch (state) {
      case CharacterDisplayActivityState.idle:
        return const _CharacterDisplayCopy(
          title: '待機中',
          message: '次の操作を待っています。',
        );
      case CharacterDisplayActivityState.loading:
        return const _CharacterDisplayCopy(
          title: '準備中',
          message: '表示内容を準備しています。',
        );
      case CharacterDisplayActivityState.speaking:
        return const _CharacterDisplayCopy(
          title: '音声再生中',
          message: 'キャラクターの音声を再生しています。',
        );
    }
  }
}

class _CharacterDisplayCopy {
  const _CharacterDisplayCopy({
    required this.title,
    required this.message,
  });

  final String title;
  final String message;

  String get label => title;
}
