import 'dart:async';
import 'dart:io';
import 'dart:typed_data' show BytesBuilder;

import 'package:drc_production/core/production_character.dart';
import 'package:drc_production/core/production_mood.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import 'debug_ai_advice.dart';

typedef DebugMinaVoice = ({
  Future<Uint8List> Function(String message) fetch,
  Future<void> Function(Uint8List audio) play,
  Future<void> Function() stop,
});

typedef DebugMinaResponse = Future<DebugAdviceResult> Function();

Future<DebugAdviceResult> fixedMinaResponse() async =>
    (message: 'ひと息ついてから、できることを一つ選びましょう。', expressionTag: 'supportive');

DebugMinaVoice? minaVoiceFromEnvironment(DebugAiAdviceClient? client) {
  const profile = String.fromEnvironment('DRC_DEBUG_MINA_VOICE_PROFILE_ID');
  if (client == null || profile.trim().isEmpty) return null;
  const channel = MethodChannel('drc/debug_mina_audio');
  return (
    fetch: (message) async {
      final url = await client.requestMinaAudio(message, profile.trim());
      final http = HttpClient()..findProxy = (_) => 'DIRECT';
      try {
        return await _downloadAudio(
          http,
          url,
        ).timeout(const Duration(seconds: 15));
      } finally {
        http.close(force: true);
      }
    },
    play: (audio) => channel.invokeMethod<void>('play', audio),
    stop: () => channel.invokeMethod<void>('stop'),
  );
}

Future<Uint8List> _downloadAudio(HttpClient http, Uri url) async {
  final request = await http.getUrl(url);
  request.followRedirects = false;
  final response = await request.close();
  if (response.statusCode != HttpStatus.ok ||
      response.headers.contentType?.mimeType != 'audio/mpeg') {
    throw const FormatException('Invalid FW audio download');
  }
  final bytes = BytesBuilder(copy: false);
  await for (final chunk in response) {
    if (bytes.length + chunk.length > 2 * 1024 * 1024) {
      throw const FormatException('FW audio is too large');
    }
    bytes.add(chunk);
  }
  if (bytes.isEmpty) throw const FormatException('Empty FW audio');
  return bytes.takeBytes();
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
  final DebugMinaVoice? voice;

  @override
  State<DebugMinaDemo> createState() => _DebugMinaDemoState();
}

class _DebugMinaDemoState extends State<DebugMinaDemo> {
  int _generation = 0;
  int _playback = 0;
  DebugAdviceResult? _result;
  String? _status;
  bool _busy = false;

  @override
  void didUpdateWidget(covariant DebugMinaDemo oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.mood != widget.mood ||
        oldWidget.character != widget.character ||
        oldWidget.response != widget.response ||
        oldWidget.voice != widget.voice) {
      _reset(oldWidget.voice);
    }
  }

  @override
  void dispose() {
    _cancelPlayback(widget.voice);
    super.dispose();
  }

  void _reset(DebugMinaVoice? voice) {
    _generation++;
    _cancelPlayback(voice);
    _result = null;
    _status = null;
  }

  void _cancelPlayback(DebugMinaVoice? voice) {
    _playback++;
    final wasBusy = _busy;
    _busy = false;
    if (wasBusy && voice != null) {
      unawaited(_stopAudio(voice));
    }
  }

  Future<void> _stopAudio(DebugMinaVoice voice) async {
    try {
      await voice.stop();
    } catch (_) {
      // Cleanup also runs in the Android activity when its engine is destroyed.
    }
  }

  Future<void> _generate() async {
    setState(() => _reset(widget.voice));
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

  Future<void> _play() async {
    final voice = widget.voice;
    final result = _result;
    if (voice == null || result == null || _busy) return;
    final playback = ++_playback;
    setState(() {
      _busy = true;
      _status = '音声を準備しています。';
    });
    String? status;
    try {
      final audio = await voice.fetch(result.message);
      if (!mounted || playback != _playback) return;
      setState(() => _status = null);
      await voice.play(audio);
    } catch (_) {
      status = '音声を再生できませんでした。再試行できます。';
    }
    if (!mounted || playback != _playback) return;
    setState(() {
      _busy = false;
      _status = status;
    });
  }

  @override
  Widget build(BuildContext context) {
    final ready =
        widget.mood != null &&
        widget.character == ProductionCharacter.gentleMina;
    final supportive = _result?.expressionTag == 'supportive';
    final result = _result;
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Semantics(header: true, child: const Text('ミナの固定アドバイス（開発版）')),
            if (ready)
              Semantics(
                container: true,
                label: supportive ? 'ミナの表情：寄り添い' : 'ミナの表情：通常',
                liveRegion: true,
                excludeSemantics: true,
                child: CircleAvatar(child: Text(supportive ? '😌' : '🙂')),
              )
            else
              const Text('気分とミナを選ぶと固定アドバイスを表示できます。'),
            TextButton(
              onPressed: ready ? _generate : null,
              child: const Text('固定アドバイスを表示'),
            ),
            if (result != null) ...[
              Semantics(liveRegion: true, child: Text(result.message)),
              if (widget.voice == null) const Text('ミナの開発用音声設定が必要です。'),
              TextButton(
                onPressed: widget.voice != null && !_busy ? _play : null,
                child: const Text('再生'),
              ),
              if (_busy)
                TextButton(
                  onPressed: () => setState(() {
                    _cancelPlayback(widget.voice);
                    _status = null;
                  }),
                  child: const Text('停止'),
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
