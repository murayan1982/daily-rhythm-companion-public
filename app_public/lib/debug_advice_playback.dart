import 'dart:async';
import 'dart:io';
import 'dart:typed_data' show BytesBuilder;

import 'package:drc_production/core/production_character.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

typedef DebugAdviceVoice = ({
  Future<Uint8List> Function(String input) fetch,
  Future<void> Function(Uint8List audio) play,
  Future<void> Function() stop,
});

typedef DebugCharacterVoice = DebugAdviceVoice Function(ProductionCharacter);

DebugAdviceVoice adviceVoiceFor(Future<Uri> Function(String) requestAudio) {
  return adviceVoiceWithFetch((input) async {
    final url = await requestAudio(input);
    final http = HttpClient()..findProxy = (_) => 'DIRECT';
    try {
      return await _downloadAudio(
        http,
        url,
      ).timeout(const Duration(seconds: 15));
    } finally {
      http.close(force: true);
    }
  });
}

DebugAdviceVoice adviceVoiceWithFetch(
  Future<Uint8List> Function(String) fetch,
) {
  const channel = MethodChannel('drc/debug_mina_audio');
  return (
    fetch: fetch,
    play: (audio) => channel.invokeMethod<void>('play', audio),
    stop: () => channel.invokeMethod<void>('stop'),
  );
}

Future<Uint8List> _downloadAudio(HttpClient http, Uri url) async {
  final request = await http.getUrl(url);
  request.followRedirects = false;
  final response = await request.close();
  return readAdviceAudio(response);
}

Future<Uint8List> readAdviceAudio(HttpClientResponse response) async {
  if (response.statusCode != HttpStatus.ok ||
      response.headers.contentType?.mimeType != 'audio/mpeg') {
    throw const FormatException('Invalid audio download');
  }
  final bytes = BytesBuilder(copy: false);
  await for (final chunk in response) {
    if (bytes.length + chunk.length > 2 * 1024 * 1024) {
      throw const FormatException('Audio is too large');
    }
    bytes.add(chunk);
  }
  if (bytes.isEmpty) throw const FormatException('Empty audio');
  return bytes.takeBytes();
}

class DebugAdvicePlayback extends ChangeNotifier {
  int _operation = 0;
  DebugAdviceVoice? _activeVoice;
  String? _status;

  bool get busy => _activeVoice != null;
  String? get status => _status;

  void stop() {
    final changed = busy || _status != null;
    _invalidate();
    if (changed) notifyListeners();
  }

  void _invalidate() {
    _operation++;
    final voice = _activeVoice;
    _activeVoice = null;
    _status = null;
    if (voice != null) unawaited(_stopAudio(voice));
  }

  Future<void> _stopAudio(DebugAdviceVoice voice) async {
    try {
      await voice.stop();
    } catch (_) {
      // The Android activity also releases playback when it is destroyed.
    }
  }

  Future<void> play(DebugAdviceVoice voice, String input) async {
    if (busy) return;
    final operation = ++_operation;
    _activeVoice = voice;
    _status = '音声を準備しています。';
    notifyListeners();
    String? failure;
    try {
      final audio = await voice.fetch(input);
      if (operation != _operation) return;
      _status = null;
      notifyListeners();
      await voice.play(audio);
    } catch (_) {
      failure = '音声を再生できませんでした。再試行できます。';
    }
    if (operation != _operation) return;
    _activeVoice = null;
    _status = failure;
    notifyListeners();
  }

  @override
  void dispose() {
    _invalidate();
    super.dispose();
  }
}

class DebugAdvicePlaybackControls extends StatelessWidget {
  const DebugAdvicePlaybackControls({
    required this.playback,
    required this.voice,
    required this.input,
    this.unavailableMessage = 'ミナの開発用音声設定が必要です。',
    this.playLabel = '再生',
    this.replacePlayWithStop = false,
    super.key,
  });

  final DebugAdvicePlayback playback;
  final DebugAdviceVoice? voice;
  final String input;
  final String unavailableMessage;
  final String playLabel;
  final bool replacePlayWithStop;

  @override
  Widget build(BuildContext context) => ListenableBuilder(
    listenable: playback,
    builder: (context, child) {
      final output = voice;
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (output == null) Text(unavailableMessage),
          if (!playback.busy || !replacePlayWithStop)
            TextButton(
              onPressed: output == null || playback.busy
                  ? null
                  : () => playback.play(output, input),
              child: Text(playLabel),
            ),
          if (playback.busy)
            TextButton(onPressed: playback.stop, child: const Text('停止')),
          if (playback.status case final status?)
            Semantics(liveRegion: true, child: Text(status)),
        ],
      );
    },
  );
}

class DebugAdviceExpression extends StatelessWidget {
  const DebugAdviceExpression(this.character, this.tag, {super.key});

  final ProductionCharacter character;
  final String? tag;

  @override
  Widget build(BuildContext context) {
    final name = productionCharacterOptionFor(character).displayName;
    final (label, emoji) = switch ((character, tag)) {
      (ProductionCharacter.gentleMina, 'supportive') => ('寄り添い', '😌'),
      (ProductionCharacter.cheerfulSora, 'happy') => ('笑顔', '😄'),
      (ProductionCharacter.coolRei, 'thinking') => ('考え中', '🤔'),
      _ => ('通常', '🙂'),
    };
    return Semantics(
      container: true,
      label: '$nameの表情：$label',
      liveRegion: true,
      excludeSemantics: true,
      child: CircleAvatar(child: Text(emoji)),
    );
  }
}
