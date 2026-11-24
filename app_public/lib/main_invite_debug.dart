import 'package:drc_production/production_app.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

import 'debug_advice_playback.dart';
import 'debug_advice_conversation.dart';
import 'debug_ai_advice.dart';
import 'health_connect_sleep_card.dart';
import 'invite_advice.dart';

void main() {
  runApp(
    kDebugMode
        ? buildInviteDebugApp(
            enableVoice: const bool.fromEnvironment('DRC_DEBUG_INVITE_VOICE'),
            enableConversation: const bool.fromEnvironment(
              'DRC_DEBUG_INVITE_CHAT',
            ),
          )
        : const ProductionApp(journeyHeader: HealthConnectSleepCard()),
  );
}

final _loopbackEndpoint = Uri.http('127.0.0.1:8000', '/v1/advice');
final _debugAdviceEndpoint = _loopbackEndpoint.replace(
  path: '/debug/invite/advice',
);

Widget buildInviteDebugApp({
  required bool enableVoice,
  bool enableConversation = false,
  InviteAdviceTransport? transport,
  DebugAdviceTransport? conversationTransport,
  DebugCharacterVoice? characterVoice,
}) {
  final endpoint = enableConversation
      ? _debugAdviceEndpoint.replace(path: '/debug/invite/conversation/advice')
      : enableVoice
      ? _debugAdviceEndpoint
      : _loopbackEndpoint;
  final debugClient = DebugAiAdviceClient(
    endpoint: endpoint,
    transport: conversationTransport,
  );
  return InviteAdviceApp(
    client: InviteAdviceClient(
      endpoint: endpoint,
      transport: transport,
      sleepEndpoint: _debugAdviceEndpoint,
      conversationControls: !enableConversation
          ? null
          : (character, reference, audio) => _InviteConversationControls(
              key: UniqueKey(),
              conversation: (close) => DebugAdviceConversation(
                character: character,
                textOnly: true,
                start: () => debugClient.startConversation(reference),
                send: debugClient.sendChatTurn,
                end: debugClient.endConversation,
                onClose: close,
              ),
              audio: audio,
            ),
      audioControls: !enableVoice
          ? null
          : (character, ref) => _InvitePlayback(
              key: UniqueKey(),
              voice:
                  characterVoice?.call(character) ??
                  adviceVoiceFor(
                    (ref) => debugClient.requestGeneratedCharacterAudio(
                      character,
                      ref,
                    ),
                  ),
              reference: ref,
            ),
    ),
    tokenLabel: '招待トークン（検証用）',
    initiallyShowToken: true,
  );
}

class _InviteConversationControls extends StatefulWidget {
  const _InviteConversationControls({
    required super.key,
    required this.conversation,
    required this.audio,
  });

  final Widget Function(VoidCallback close) conversation;
  final Widget? audio;

  @override
  State<_InviteConversationControls> createState() =>
      _InviteConversationControlsState();
}

class _InviteConversationControlsState
    extends State<_InviteConversationControls> {
  bool _open = false;

  @override
  Widget build(BuildContext context) {
    if (_open) return widget.conversation(() => setState(() => _open = false));
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        ?widget.audio,
        TextButton(
          onPressed: () => setState(() => _open = true),
          child: const Text('会話を続ける'),
        ),
      ],
    );
  }
}

class _InvitePlayback extends StatefulWidget {
  const _InvitePlayback({
    required super.key,
    required this.voice,
    required this.reference,
  });

  final DebugAdviceVoice voice;
  final String reference;

  @override
  State<_InvitePlayback> createState() => _InvitePlaybackState();
}

class _InvitePlaybackState extends State<_InvitePlayback> {
  final _playback = DebugAdvicePlayback();

  @override
  void dispose() {
    _playback.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => DebugAdvicePlaybackControls(
    playback: _playback,
    voice: widget.voice,
    input: widget.reference,
    playLabel: '音声再生',
    replacePlayWithStop: true,
  );
}
