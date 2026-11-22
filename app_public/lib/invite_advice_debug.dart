import 'dart:convert';
import 'dart:io';

import 'package:drc_production/core/production_character.dart';
import 'package:drc_production/core/production_mood.dart';
import 'package:flutter/material.dart';

typedef InviteAdviceHttpResponse = ({int status, String body});
typedef InviteAdviceTransport =
    Future<InviteAdviceHttpResponse> Function(
      Uri endpoint,
      Map<String, String> headers,
      String body,
    );

class InviteAdviceClient {
  const InviteAdviceClient({this.transport});

  static final _endpoint = Uri.http('127.0.0.1:8000', '/v1/advice');
  final InviteAdviceTransport? transport;

  Future<({int status, String? message})> generate({
    required ProductionMood mood,
    required ProductionCharacter character,
    required String token,
  }) async {
    final reply = await (transport ?? _post)(
      _endpoint,
      {
        HttpHeaders.authorizationHeader: 'Bearer $token',
        HttpHeaders.contentTypeHeader: 'application/json; charset=utf-8',
      },
      jsonEncode({
        'mood': productionMoodOptionFor(mood).code,
        'character_id': productionCharacterOptionFor(character).characterId,
      }),
    );
    if (reply.status != 200) return (status: reply.status, message: null);

    final value = jsonDecode(reply.body);
    if (value is Map<String, dynamic> &&
        value.length == 1 &&
        value['message'] is String) {
      final message = (value['message'] as String).trim();
      if (message.isNotEmpty && message.runes.length <= 240) {
        return (status: 200, message: message);
      }
    }
    throw const FormatException('Invalid invite advice response');
  }

  static Future<InviteAdviceHttpResponse> _post(
    Uri endpoint,
    Map<String, String> headers,
    String body,
  ) async {
    const timeout = Duration(seconds: 15);
    final client = HttpClient()
      ..connectionTimeout = timeout
      ..findProxy = (_) => 'DIRECT';
    try {
      return await _send(client, endpoint, headers, body).timeout(timeout);
    } finally {
      client.close(force: true);
    }
  }

  static Future<InviteAdviceHttpResponse> _send(
    HttpClient client,
    Uri endpoint,
    Map<String, String> headers,
    String body,
  ) async {
    final request = await client.postUrl(endpoint);
    request.followRedirects = false;
    request.persistentConnection = false;
    headers.forEach(request.headers.set);
    request.add(utf8.encode(body));
    final response = await request.close();
    if (response.statusCode != 200) {
      return (status: response.statusCode, body: '');
    }
    final bytes = <int>[];
    await for (final chunk in response) {
      if (bytes.length + chunk.length > 4096) {
        throw const FormatException('Invite advice response is too large');
      }
      bytes.addAll(chunk);
    }
    return (status: 200, body: utf8.decode(bytes));
  }
}

class InviteAdviceDebugCard extends StatefulWidget {
  const InviteAdviceDebugCard({
    super.key,
    this.mood,
    this.character,
    this.client = const InviteAdviceClient(),
  });

  final ProductionMood? mood;
  final ProductionCharacter? character;
  final InviteAdviceClient client;

  @override
  State<InviteAdviceDebugCard> createState() => _InviteAdviceDebugCardState();
}

class _InviteAdviceDebugCardState extends State<InviteAdviceDebugCard> {
  final _token = TextEditingController();
  static final _tokenSyntax = RegExp(r'^[a-zA-Z0-9_-]{1,128}$');
  int _generation = 0;
  bool _waiting = false;
  String? _result;

  @override
  void didUpdateWidget(InviteAdviceDebugCard oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.mood != widget.mood ||
        oldWidget.character != widget.character) {
      _clearResult();
    }
  }

  void _clearResult() {
    _generation++;
    _waiting = false;
    _result = null;
  }

  @override
  void dispose() {
    _token.dispose();
    super.dispose();
  }

  Future<void> _generate() async {
    final mood = widget.mood;
    final character = widget.character;
    final token = _token.text.trim();
    if (_waiting ||
        mood == null ||
        character == null ||
        !_tokenSyntax.hasMatch(token)) {
      return;
    }
    FocusScope.of(context).unfocus();
    final generation = ++_generation;
    setState(() {
      _waiting = true;
      _result = null;
    });
    String result;
    try {
      final reply = await widget.client.generate(
        mood: mood,
        character: character,
        token: token,
      );
      result = switch (reply.status) {
        200 => reply.message!,
        401 => '招待トークンを確認してください。端末内アドバイスは上に表示されています。',
        429 => '生成の上限に達しました。端末内アドバイスは上に表示されています。',
        502 || 503 => 'AIアドバイスを利用できません。端末内アドバイスは上に表示されています。',
        _ => _connectionError,
      };
    } on Exception {
      result = _connectionError;
    }
    if (!mounted || generation != _generation) return;
    setState(() {
      _waiting = false;
      _result = result;
    });
  }

  static const _connectionError = 'AIアドバイスを取得できませんでした。端末内アドバイスは上に表示されています。';

  @override
  Widget build(BuildContext context) {
    final canGenerate =
        !_waiting &&
        widget.mood != null &&
        widget.character != null &&
        _tokenSyntax.hasMatch(_token.text.trim());
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            TextField(
              controller: _token,
              decoration: const InputDecoration(labelText: '招待トークン（検証用）'),
              obscureText: true,
              autocorrect: false,
              enableSuggestions: false,
              enableIMEPersonalizedLearning: false,
              onChanged: (_) => setState(_clearResult),
            ),
            TextButton(
              onPressed: canGenerate ? _generate : null,
              child: const Text('AIアドバイスを生成'),
            ),
            if (_waiting) const Text('AIアドバイスを生成しています。'),
            if (_result case final message?)
              Semantics(liveRegion: true, child: Text(message)),
          ],
        ),
      ),
    );
  }
}
