import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';

import 'package:drc_production/core/production_character.dart';
import 'package:drc_production/core/production_mood.dart';
import 'package:flutter/material.dart';

import 'debug_advice_playback.dart';
import 'debug_advice_conversation.dart';

typedef DebugAdviceHttpResponse = ({int statusCode, String body});
typedef DebugAdviceTransport =
    Future<DebugAdviceHttpResponse> Function(Uri endpoint, String jsonBody);
typedef DebugAdviceResult = ({String message, String expressionTag});
typedef DebugCharacterAdviceResult = ({
  DebugAdviceResult advice,
  String? voiceRef,
  String? adviceRef,
});

class DebugAiAdviceClient {
  const DebugAiAdviceClient({
    required this.endpoint,
    this.timeout = const Duration(seconds: 15),
    DebugAdviceTransport? transport,
  }) : _transport = transport;

  static DebugAiAdviceClient? fromEnvironment() {
    const url = String.fromEnvironment('DRC_DEBUG_AI_ADVICE_BASE_URL');
    final origin = Uri.tryParse(url);
    if (origin == null ||
        origin.scheme != 'http' ||
        origin.host != '127.0.0.1' ||
        origin.userInfo.isNotEmpty ||
        origin.hasQuery ||
        origin.hasFragment ||
        (origin.path.isNotEmpty && origin.path != '/') ||
        origin.port < 1 ||
        origin.port > 65535) {
      return null;
    }
    return DebugAiAdviceClient(
      endpoint: origin.replace(path: '/debug/ai-advice'),
    );
  }

  final Uri endpoint;
  final Duration timeout;
  final DebugAdviceTransport? _transport;
  static const _expressionTags = {
    'idle',
    'happy',
    'thinking',
    'supportive',
    'speaking',
  };
  static final _opaqueRef = RegExp(r'^[A-Za-z0-9_-]{32}$');

  Future<DebugAdviceResult> generate({
    required ProductionMood mood,
    required ProductionCharacter character,
    int? syntheticSleepMinutes,
  }) async {
    final json = await _generateJson(
      endpoint,
      mood,
      character,
      syntheticSleepMinutes,
    );
    if (json.length != 2) {
      throw const FormatException('Invalid advice response');
    }
    return _decodeAdvice(json);
  }

  Future<DebugCharacterAdviceResult> generateCharacterAdvice({
    required ProductionMood mood,
    required ProductionCharacter character,
    int? syntheticSleepMinutes,
    bool withConversation = false,
  }) async {
    final json = await _generateJson(
      endpoint.replace(
        path: withConversation
            ? '/debug/conversation/advice'
            : '/debug/character/ai-advice',
      ),
      mood,
      character,
      syntheticSleepMinutes,
    );
    final adviceRef = json['advice_ref'];
    if (json.length != (withConversation ? 4 : 3) ||
        (withConversation &&
            (adviceRef is! String || !_opaqueRef.hasMatch(adviceRef)))) {
      throw const FormatException('Invalid advice response');
    }
    return (
      advice: _decodeAdvice(json),
      voiceRef: _decodeVoiceRef(json),
      adviceRef: withConversation ? adviceRef as String : null,
    );
  }

  String? _decodeVoiceRef(Map<String, dynamic> json) {
    final ref = json['voice_ref'];
    if (!json.containsKey('voice_ref') ||
        (ref != null && (ref is! String || !_opaqueRef.hasMatch(ref)))) {
      throw const FormatException('Invalid character audio reference');
    }
    return ref as String?;
  }

  Future<Map<String, dynamic>> _conversationJson(
    String action,
    Map<String, Object> body,
  ) => _requestJson(
    endpoint.replace(path: '/debug/conversation/$action'),
    jsonEncode(body),
  );

  Future<DebugChatSession> startConversation(String adviceRef) async {
    final json = await _conversationJson('start', {'advice_ref': adviceRef});
    final id = json['session_id'];
    final limit = json['turn_limit'];
    if (id is! String ||
        !_opaqueRef.hasMatch(id) ||
        limit is! int ||
        limit < 1) {
      throw const FormatException('Invalid conversation session');
    }
    return (id: id, turnLimit: limit);
  }

  Future<DebugChatReply> sendChatTurn(
    String id,
    int turn,
    String message,
  ) async {
    final json = await _conversationJson('turn', {
      'session_id': id,
      'turn': turn,
      'message': message,
    });
    if (json.length != 3) {
      throw const FormatException('Invalid conversation reply');
    }
    final advice = _decodeAdvice(json);
    return (
      message: advice.message,
      expressionTag: advice.expressionTag,
      voiceRef: _decodeVoiceRef(json),
    );
  }

  Future<void> endConversation(String id) async {
    await _conversationJson('end', {'session_id': id});
  }

  Future<Uint8List> fetchConversationAudio(String id, String ref) async {
    final http = HttpClient()..findProxy = (_) => 'DIRECT';
    try {
      final response = _sendRequest(
        http,
        endpoint.replace(path: '/debug/conversation/voice'),
        jsonEncode({'session_id': id, 'voice_ref': ref}),
        'audio/mpeg',
      ).then(readAdviceAudio);
      return await response.timeout(timeout);
    } finally {
      http.close(force: true);
    }
  }

  Future<Map<String, dynamic>> _generateJson(
    Uri url,
    ProductionMood mood,
    ProductionCharacter character,
    int? syntheticSleepMinutes,
  ) {
    final body = jsonEncode({
      'mood': productionMoodOptionFor(mood).code,
      'character_id': productionCharacterOptionFor(character).characterId,
      if (syntheticSleepMinutes != null)
        'sleep_summary': {'total_sleep_minutes': syntheticSleepMinutes},
    });
    return _requestJson(url, body);
  }

  DebugAdviceResult _decodeAdvice(Map<String, dynamic> json) {
    final message = json['message'];
    final tag = json['expression_tag'];
    if (message is! String ||
        message.trim().isEmpty ||
        message.trim().runes.length > 240 ||
        tag is! String ||
        !_expressionTags.contains(tag)) {
      throw const FormatException('Invalid advice response');
    }
    return (message: message.trim(), expressionTag: tag);
  }

  Future<Uri> requestMinaAudio(String message, String voiceProfileId) =>
      _requestAudio('/demo/voice-output', {
        'output_mode': 'tts',
        'text_content': message,
        'character_id': 'gentle_mina',
        'voice_profile_id': voiceProfileId,
        'audio_format': 'mp3',
      });

  Future<Uri> requestGeneratedCharacterAudio(
    ProductionCharacter character,
    String ref,
  ) => _requestAudio('/debug/character/voice', {
    'voice_ref': ref,
    'character_id': productionCharacterOptionFor(character).characterId,
  });

  Future<Uri> _requestAudio(String path, Map<String, String> data) async {
    final json = await _requestJson(
      endpoint.replace(path: path),
      jsonEncode(data),
    );
    final audioPath = json['audio_url'];
    if (json['accepted'] != true ||
        json['audio_ready'] != true ||
        json['audio_format'] != 'mp3' ||
        audioPath is! String ||
        !RegExp(
          r'^/demo/voice-output/audio/[0-9a-f]{32}$',
        ).hasMatch(audioPath)) {
      throw const FormatException('Invalid audio response');
    }
    return endpoint.replace(path: audioPath);
  }

  Future<Map<String, dynamic>> _requestJson(Uri url, String body) async {
    final transport = _transport;
    final client = transport == null
        ? (HttpClient()..findProxy = (_) => 'DIRECT')
        : null;
    try {
      final pending = transport != null
          ? transport(url, body)
          : _post(client!, url, body);
      final response = await pending.timeout(timeout);
      if (response.statusCode != HttpStatus.ok) {
        throw HttpException('Unexpected status ${response.statusCode}');
      }
      final json = jsonDecode(response.body);
      if (json is! Map<String, dynamic>) {
        throw const FormatException('Invalid JSON response');
      }
      return json;
    } finally {
      client?.close(force: true);
    }
  }

  Future<DebugAdviceHttpResponse> _post(
    HttpClient client,
    Uri url,
    String body,
  ) async {
    final response = await _sendRequest(client, url, body, 'application/json');
    if (response.statusCode != HttpStatus.ok) {
      return (statusCode: response.statusCode, body: '');
    }
    if (response.headers.contentType?.mimeType != 'application/json') {
      throw const FormatException('Advice response must be JSON');
    }
    final bytes = <int>[];
    await for (final chunk in response) {
      if (bytes.length + chunk.length > 4096) {
        throw const FormatException('Advice response is too large');
      }
      bytes.addAll(chunk);
    }
    return (statusCode: response.statusCode, body: utf8.decode(bytes));
  }

  Future<HttpClientResponse> _sendRequest(
    HttpClient client,
    Uri url,
    String body,
    String accept,
  ) async {
    final request = await client.postUrl(url);
    request.followRedirects = false;
    request.headers.contentType = ContentType.json;
    request.headers.set(HttpHeaders.acceptHeader, accept);
    request.add(utf8.encode(body));
    return request.close();
  }
}

class DebugAiAdviceCard extends StatefulWidget {
  const DebugAiAdviceCard({
    required this.client,
    required this.mood,
    required this.character,
    this.characterVoice,
    this.conversationEnabled = false,
    super.key,
  });

  final DebugAiAdviceClient? client;
  final ProductionMood? mood;
  final ProductionCharacter? character;
  final DebugCharacterVoice? characterVoice;
  final bool conversationEnabled;

  @override
  State<DebugAiAdviceCard> createState() => _DebugAiAdviceCardState();
}

class _DebugAiAdviceCardState extends State<DebugAiAdviceCard> {
  static const _syntheticSleepMinutes = 385;
  final _playback = DebugAdvicePlayback();
  bool _includeSyntheticSleep = false;
  bool _loading = false;
  bool _failed = false;
  int _requestId = 0;
  DebugAdviceResult? _result;
  String? _voiceRef;
  String? _adviceRef;
  bool _chatOpen = false;

  @override
  void didUpdateWidget(covariant DebugAiAdviceCard oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.mood != widget.mood ||
        oldWidget.character != widget.character ||
        oldWidget.client != widget.client ||
        oldWidget.characterVoice != widget.characterVoice ||
        oldWidget.conversationEnabled != widget.conversationEnabled) {
      _requestId++;
      _loading = false;
      _failed = false;
      _clearResult();
    }
  }

  @override
  void dispose() {
    _playback.dispose();
    super.dispose();
  }

  void _clearResult() {
    _playback.stop();
    _result = null;
    _voiceRef = null;
    _adviceRef = null;
    _chatOpen = false;
  }

  Future<void> _generate() async {
    final client = widget.client;
    final mood = widget.mood;
    final character = widget.character;
    if (client == null || mood == null || character == null || _loading) return;
    final id = ++_requestId;
    setState(() {
      _loading = true;
      _failed = false;
      _clearResult();
    });

    DebugAdviceResult? result;
    String? voiceRef;
    String? adviceRef;
    try {
      final sleep = _includeSyntheticSleep ? _syntheticSleepMinutes : null;
      if (widget.characterVoice != null || widget.conversationEnabled) {
        final generated = await client.generateCharacterAdvice(
          mood: mood,
          character: character,
          syntheticSleepMinutes: sleep,
          withConversation: widget.conversationEnabled,
        );
        result = generated.advice;
        voiceRef = generated.voiceRef;
        adviceRef = generated.adviceRef;
      } else {
        result = await client.generate(
          mood: mood,
          character: character,
          syntheticSleepMinutes: sleep,
        );
      }
    } catch (_) {
      // The shared journey already displays the current on-device advice.
    }
    if (!mounted || id != _requestId) return;
    setState(() {
      _result = result;
      _voiceRef = voiceRef;
      _adviceRef = adviceRef;
      _failed = result == null;
      _loading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    final configured = widget.client != null;
    final character = widget.character;
    final ready = widget.mood != null && character != null;
    final characterVoice = widget.characterVoice;
    final client = widget.client;
    final adviceRef = _adviceRef;
    final result = _result;
    final status = !configured
        ? '開発用の接続先を指定すると利用できます。'
        : !ready
        ? '気分とキャラクターを選ぶと生成できます。'
        : _loading
        ? 'AIアドバイスを生成しています。'
        : _failed
        ? 'AIアドバイスを取得できませんでした。上の端末内アドバイスを利用できます。時間をおいて再試行してください。'
        : _result?.message;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Semantics(header: true, child: const Text('AIアドバイス（開発版）')),
            const Text(
              '生成を押すと、気分とキャラクターを開発用サーバーに送ります。Health Connectの睡眠記録は送信しません。',
            ),
            CheckboxListTile(
              contentPadding: EdgeInsets.zero,
              title: const Text('合成睡眠要約（$_syntheticSleepMinutes分）を含める'),
              value: _includeSyntheticSleep,
              onChanged: !configured || _loading
                  ? null
                  : (checked) {
                      setState(() {
                        _includeSyntheticSleep = checked ?? false;
                        _clearResult();
                        _failed = false;
                      });
                    },
            ),
            TextButton(
              onPressed: configured && ready && !_loading ? _generate : null,
              child: const Text('AIアドバイスを生成'),
            ),
            if ((characterVoice != null || widget.conversationEnabled) &&
                ready &&
                !_chatOpen)
              DebugAdviceExpression(character, result?.expressionTag),
            if (status != null)
              Semantics(liveRegion: true, child: Text(status)),
            if (characterVoice != null &&
                character != null &&
                result != null &&
                !_chatOpen)
              if (_voiceRef case final ref?)
                DebugAdvicePlaybackControls(
                  playback: _playback,
                  voice: characterVoice(character),
                  input: ref,
                )
              else
                Semantics(
                  liveRegion: true,
                  child: Text(
                    '${productionCharacterOptionFor(character).displayName}の読み上げは利用できません。',
                  ),
                ),
            if (client != null &&
                character != null &&
                result != null &&
                adviceRef != null)
              if (_chatOpen)
                DebugAdviceConversation(
                  key: ValueKey(adviceRef),
                  character: character,
                  adviceTag: result.expressionTag,
                  playback: _playback,
                  start: () => client.startConversation(adviceRef),
                  send: client.sendChatTurn,
                  end: client.endConversation,
                  voice: (id) => adviceVoiceWithFetch(
                    (ref) => client.fetchConversationAudio(id, ref),
                  ),
                  onClose: () => setState(() {
                    _playback.stop();
                    _chatOpen = false;
                  }),
                )
              else
                TextButton(
                  onPressed: () => setState(() {
                    _playback.stop();
                    _chatOpen = true;
                  }),
                  child: const Text('会話を続ける'),
                ),
          ],
        ),
      ),
    );
  }
}
