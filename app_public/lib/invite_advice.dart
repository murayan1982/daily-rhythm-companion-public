import 'dart:convert';
import 'dart:io';

import 'package:drc_production/components/production_daily_advice.dart';
import 'package:drc_production/core/production_character.dart';
import 'package:drc_production/core/production_mood.dart';
import 'package:drc_production/production_app.dart';
import 'package:flutter/material.dart';

import 'bundled_character_portrait.dart';
import 'health_connect_sleep_card.dart';

typedef InviteAdviceHttpResponse = ({int status, String body});
typedef InviteAdviceTransport =
    Future<InviteAdviceHttpResponse> Function(
      Uri endpoint,
      Map<String, String> headers,
      String body,
    );
typedef InviteAdviceAudioControls =
    Widget Function(ProductionCharacter character, String voiceRef);
typedef InviteAdviceConversationControls =
    Widget Function(
      ProductionCharacter character,
      String adviceRef,
      Widget? audioControls,
    );

class InviteAdviceClient {
  const InviteAdviceClient({
    required this.endpoint,
    this.transport,
    this.audioControls,
    this.conversationControls,
    this.sleepEndpoint,
  });

  final Uri endpoint;
  final InviteAdviceTransport? transport;
  final InviteAdviceAudioControls? audioControls;
  final InviteAdviceConversationControls? conversationControls;
  final Uri? sleepEndpoint;
  static final _voiceRefPattern = RegExp(r'^[A-Za-z0-9_-]{32}$');

  Future<ProductionGeneratedAdvice> generate({
    required ProductionMood mood,
    required ProductionCharacter character,
    required String token,
    int? totalSleepMinutes,
  }) async {
    final useSleep = sleepEndpoint != null && totalSleepMinutes != null;
    final reply = await (transport ?? _post)(
      useSleep && conversationControls == null ? sleepEndpoint! : endpoint,
      {
        HttpHeaders.authorizationHeader: 'Bearer $token',
        HttpHeaders.contentTypeHeader: 'application/json; charset=utf-8',
      },
      jsonEncode({
        'mood': productionMoodOptionFor(mood).code,
        'character_id': productionCharacterOptionFor(character).characterId,
        if (useSleep) 'total_sleep_minutes': totalSleepMinutes,
      }),
    );
    if (reply.status != 200) {
      throw const HttpException('Invite advice request failed');
    }

    final value = jsonDecode(reply.body);
    final voice = audioControls;
    final conversation = conversationControls;
    final fields = conversation != null
        ? 3
        : voice != null || useSleep
        ? 2
        : 1;
    if (value is Map<String, dynamic> &&
        value.length == fields &&
        value['message'] is String) {
      final message = (value['message'] as String).trim();
      final ref = value['voice_ref'];
      final adviceRef = value['advice_ref'];
      final validReference =
          fields == 1 ||
          (value.containsKey('voice_ref') &&
              (ref == null || ref is String && _voiceRefPattern.hasMatch(ref)));
      final validAdviceRef =
          conversation == null ||
          adviceRef is String && _voiceRefPattern.hasMatch(adviceRef);
      if (message.isNotEmpty &&
          message.runes.length <= 240 &&
          validReference &&
          validAdviceRef) {
        final audio = ref is String ? voice?.call(character, ref) : null;
        return (
          message: message,
          resultControls: conversation == null
              ? audio
              : conversation(character, adviceRef as String, audio),
        );
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

class InviteAdviceApp extends StatefulWidget {
  const InviteAdviceApp({
    super.key,
    required this.client,
    this.tokenLabel = '招待トークン',
    this.initiallyShowToken = false,
  });

  final InviteAdviceClient client;
  final String tokenLabel;
  final bool initiallyShowToken;

  @override
  State<InviteAdviceApp> createState() => _InviteAdviceAppState();
}

class _InviteAdviceAppState extends State<InviteAdviceApp> {
  final _token = TextEditingController();
  late bool _showToken = widget.initiallyShowToken;
  static final _tokenSyntax = RegExp(r'^[a-zA-Z0-9_-]{1,128}$');
  ProductionAdviceGenerator? _generateOnline;
  int? _actualSleepMinutes;
  bool _includeSleep = false;

  void _updateToken(String value) {
    final token = value.trim();
    setState(() {
      _generateOnline = _tokenSyntax.hasMatch(token)
          ? (mood, character) => widget.client.generate(
              mood: mood,
              character: character,
              token: token,
              totalSleepMinutes: _includeSleep ? _actualSleepMinutes : null,
            )
          : null;
    });
  }

  void _updateSleepMinutes(int? minutes) {
    if (_actualSleepMinutes == minutes) return;
    _actualSleepMinutes = minutes;
    if (_includeSleep) _updateToken(_token.text);
  }

  @override
  void dispose() {
    _token.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return ProductionApp(
      journeyHeader: HealthConnectSleepCard(
        onActualSleepMinutesChanged: widget.client.sleepEndpoint == null
            ? null
            : _updateSleepMinutes,
      ),
      characterPortrait: buildBundledCharacterPortrait,
      onlineAdvice: (
        generate: _generateOnline,
        settings: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('招待トークンを入力すると、生成時に気分とキャラクターを送信します。'),
            if (!widget.initiallyShowToken)
              TextButton(
                onPressed: () => setState(() => _showToken = !_showToken),
                child: Text(_showToken ? '招待トークン欄を閉じる' : '招待トークンを入力'),
              ),
            if (_showToken)
              TextField(
                controller: _token,
                decoration: InputDecoration(labelText: widget.tokenLabel),
                obscureText: true,
                autocorrect: false,
                enableSuggestions: false,
                enableIMEPersonalizedLearning: false,
                onChanged: _updateToken,
              ),
            if (widget.client.sleepEndpoint != null)
              SwitchListTile(
                contentPadding: EdgeInsets.zero,
                title: const Text('睡眠時間をアドバイスに使う'),
                subtitle: const Text('オンにすると、取得済みの実睡眠時間（分）をアドバイス生成先に送信します。'),
                value: _includeSleep,
                onChanged: (value) {
                  _includeSleep = value;
                  _updateToken(_token.text);
                },
              ),
          ],
        ),
      ),
    );
  }
}
