import 'package:drc_production/production_app.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import 'debug_ai_advice.dart';
import 'debug_advice_playback.dart';
import 'debug_mina_demo.dart';
import 'health_connect_sleep_card.dart';

void main() {
  final client = kDebugMode ? DebugAiAdviceClient.fromEnvironment() : null;
  const minaDemo = kDebugMode && bool.fromEnvironment('DRC_DEBUG_MINA_STAGE3');
  const adviceChat =
      kDebugMode && bool.fromEnvironment('DRC_DEBUG_ADVICE_CHAT');
  const characterAiVoice =
      kDebugMode &&
      (adviceChat ||
          bool.fromEnvironment('DRC_DEBUG_CHARACTER_AI_VOICE') ||
          bool.fromEnvironment('DRC_DEBUG_MINA_AI_VOICE'));
  runApp(
    SleepDebugApp(
      adviceClient: client,
      minaResponse: minaDemo ? fixedMinaResponse : null,
      minaVoice: minaDemo ? minaVoiceFromEnvironment(client) : null,
      adviceChat: adviceChat,
      characterAiVoice: characterAiVoice && client != null
          ? (character) => adviceVoiceFor(
              (ref) => client.requestGeneratedCharacterAudio(character, ref),
            )
          : null,
    ),
  );
}

class SleepDebugApp extends StatefulWidget {
  const SleepDebugApp({
    super.key,
    this.adviceClient,
    this.minaResponse,
    this.minaVoice,
    this.characterAiVoice,
    this.adviceChat = false,
  });

  final DebugAiAdviceClient? adviceClient;
  final DebugMinaResponse? minaResponse;
  final DebugAdviceVoice? minaVoice;
  final DebugCharacterVoice? characterAiVoice;
  final bool adviceChat;

  @override
  State<SleepDebugApp> createState() => _SleepDebugAppState();
}

class _SleepDebugAppState extends State<SleepDebugApp> {
  static const _portraitChannel = MethodChannel('drc/debug_character_images');
  late final _portraits = _portraitChannel.invokeMapMethod<String, Uint8List>(
    'load',
  );

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<Map<String, Uint8List>?>(
      future: _portraits,
      builder: (context, snapshot) => ProductionApp(
        journeyHeader: const HealthConnectSleepCard(),
        adviceExtension: kDebugMode
            ? (mood, character) {
                final response = widget.minaResponse;
                return response == null
                    ? DebugAiAdviceCard(
                        client: widget.adviceClient,
                        mood: mood,
                        character: character,
                        characterVoice: widget.characterAiVoice,
                        conversationEnabled: widget.adviceChat,
                      )
                    : DebugMinaDemo(
                        mood: mood,
                        character: character,
                        response: response,
                        voice: widget.minaVoice,
                      );
              }
            : null,
        characterPortrait: (option, fallback) {
          final bytes = snapshot.data?[option.characterId];
          if (bytes == null || bytes.isEmpty) return null;
          const size = 56.0;
          return Image.memory(
            bytes,
            width: size,
            height: size,
            cacheWidth: (size * MediaQuery.devicePixelRatioOf(context)).round(),
            fit: BoxFit.contain,
            errorBuilder: (context, error, stackTrace) => fallback,
          );
        },
      ),
    );
  }
}
