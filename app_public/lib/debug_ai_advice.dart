import 'dart:convert';
import 'dart:io';

import 'package:drc_production/core/production_character.dart';
import 'package:drc_production/core/production_mood.dart';
import 'package:flutter/material.dart';

typedef DebugAdviceHttpResponse = ({int statusCode, String body});
typedef DebugAdviceTransport =
    Future<DebugAdviceHttpResponse> Function(Uri endpoint, String jsonBody);
typedef DebugAdviceResult = ({String message, String expressionTag});

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

  Future<DebugAdviceResult> generate({
    required ProductionMood mood,
    required ProductionCharacter character,
    int? syntheticSleepMinutes,
  }) async {
    final body = jsonEncode({
      'mood': productionMoodOptionFor(mood).code,
      'character_id': productionCharacterOptionFor(character).characterId,
      if (syntheticSleepMinutes != null)
        'sleep_summary': {'total_sleep_minutes': syntheticSleepMinutes},
    });
    final transport = _transport;
    final client = transport == null
        ? (HttpClient()..findProxy = (_) => 'DIRECT')
        : null;
    try {
      final pending = transport != null
          ? transport(endpoint, body)
          : _post(client!, body);
      final response = await pending.timeout(timeout);
      if (response.statusCode != HttpStatus.ok) {
        throw HttpException('Unexpected status ${response.statusCode}');
      }
      final json = jsonDecode(response.body);
      if (json is! Map<String, dynamic> || json.length != 2) {
        throw const FormatException('Invalid advice response');
      }
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
    } finally {
      client?.close(force: true);
    }
  }

  Future<DebugAdviceHttpResponse> _post(HttpClient client, String body) async {
    final request = await client.postUrl(endpoint);
    request.followRedirects = false;
    request.headers.contentType = ContentType.json;
    request.headers.set(HttpHeaders.acceptHeader, 'application/json');
    request.add(utf8.encode(body));
    final response = await request.close();
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
}

class DebugAiAdviceCard extends StatefulWidget {
  const DebugAiAdviceCard({
    required this.client,
    required this.mood,
    required this.character,
    super.key,
  });

  final DebugAiAdviceClient? client;
  final ProductionMood? mood;
  final ProductionCharacter? character;

  @override
  State<DebugAiAdviceCard> createState() => _DebugAiAdviceCardState();
}

class _DebugAiAdviceCardState extends State<DebugAiAdviceCard> {
  static const _syntheticSleepMinutes = 385;
  bool _includeSyntheticSleep = false;
  bool _loading = false;
  bool _failed = false;
  int _requestId = 0;
  DebugAdviceResult? _result;

  @override
  void didUpdateWidget(covariant DebugAiAdviceCard oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.mood != widget.mood ||
        oldWidget.character != widget.character ||
        oldWidget.client != widget.client) {
      _requestId++;
      _loading = false;
      _failed = false;
      _result = null;
    }
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
      _result = null;
    });

    DebugAdviceResult? result;
    try {
      result = await client.generate(
        mood: mood,
        character: character,
        syntheticSleepMinutes: _includeSyntheticSleep
            ? _syntheticSleepMinutes
            : null,
      );
    } catch (_) {
      // The shared journey already displays the current on-device advice.
    }
    if (!mounted || id != _requestId) return;
    setState(() {
      _result = result;
      _failed = result == null;
      _loading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    final configured = widget.client != null;
    final ready = widget.mood != null && widget.character != null;
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
                        _result = null;
                        _failed = false;
                      });
                    },
            ),
            TextButton(
              onPressed: configured && ready && !_loading ? _generate : null,
              child: const Text('AIアドバイスを生成'),
            ),
            if (status != null)
              Semantics(liveRegion: true, child: Text(status)),
          ],
        ),
      ),
    );
  }
}
