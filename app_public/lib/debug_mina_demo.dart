import 'package:drc_production/core/production_character.dart';
import 'package:drc_production/core/production_mood.dart';
import 'package:flutter/material.dart';

import 'debug_ai_advice.dart';
import 'debug_advice_playback.dart';

typedef DebugMinaResponse = Future<DebugAdviceResult> Function();

Future<DebugAdviceResult> fixedMinaResponse() async =>
    (message: 'ひと息ついてから、できることを一つ選びましょう。', expressionTag: 'supportive');

DebugAdviceVoice? minaVoiceFromEnvironment(DebugAiAdviceClient? client) {
  const profile = String.fromEnvironment('DRC_DEBUG_MINA_VOICE_PROFILE_ID');
  if (client == null || profile.trim().isEmpty) return null;
  return adviceVoiceFor(
    (message) => client.requestMinaAudio(message, profile.trim()),
  );
}

class DebugMinaDemo extends StatefulWidget {
  const DebugMinaDemo({
    required this.mood,
    required this.character,
    required this.response,
    required this.voice,
    super.key,
  });

  final ProductionMood? mood;
  final ProductionCharacter? character;
  final DebugMinaResponse response;
  final DebugAdviceVoice? voice;

  @override
  State<DebugMinaDemo> createState() => _DebugMinaDemoState();
}

class _DebugMinaDemoState extends State<DebugMinaDemo> {
  final _playback = DebugAdvicePlayback();
  int _generation = 0;
  DebugAdviceResult? _result;
  String? _status;

  @override
  void didUpdateWidget(covariant DebugMinaDemo oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.mood != widget.mood ||
        oldWidget.character != widget.character ||
        oldWidget.response != widget.response ||
        oldWidget.voice != widget.voice) {
      _reset();
    }
  }

  @override
  void dispose() {
    _playback.dispose();
    super.dispose();
  }

  void _reset() {
    _generation++;
    _playback.stop();
    _result = null;
    _status = null;
  }

  Future<void> _generate() async {
    setState(_reset);
    final generation = _generation;
    try {
      final result = await widget.response();
      if (!mounted || generation != _generation) return;
      setState(() => _result = result);
    } catch (_) {
      if (!mounted || generation != _generation) return;
      setState(() => _status = '固定アドバイスを表示できませんでした。');
    }
  }

  @override
  Widget build(BuildContext context) {
    final ready =
        widget.mood != null &&
        widget.character == ProductionCharacter.gentleMina;
    final result = _result;
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Semantics(header: true, child: const Text('ミナの固定アドバイス（開発版）')),
            if (ready)
              DebugAdviceExpression(
                ProductionCharacter.gentleMina,
                result?.expressionTag,
              )
            else
              const Text('気分とミナを選ぶと固定アドバイスを表示できます。'),
            TextButton(
              onPressed: ready ? _generate : null,
              child: const Text('固定アドバイスを表示'),
            ),
            if (result != null) ...[
              Semantics(liveRegion: true, child: Text(result.message)),
              DebugAdvicePlaybackControls(
                playback: _playback,
                voice: widget.voice,
                input: result.message,
              ),
            ],
            if (_status case final status?)
              Semantics(liveRegion: true, child: Text(status)),
          ],
        ),
      ),
    );
  }
}
