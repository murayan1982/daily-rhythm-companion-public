import 'dart:async';

import 'package:drc_production/core/production_character.dart';
import 'package:flutter/material.dart';

import 'debug_advice_playback.dart';

typedef DebugChatSession = ({String id, int turnLimit});
typedef DebugChatReply = ({
  String message,
  String expressionTag,
  String? voiceRef,
});

class DebugAdviceConversation extends StatefulWidget {
  const DebugAdviceConversation({
    required this.character,
    required this.adviceTag,
    required this.playback,
    required this.start,
    required this.send,
    required this.end,
    required this.voice,
    required this.onClose,
    super.key,
  });

  final ProductionCharacter character;
  final String adviceTag;
  final DebugAdvicePlayback playback;
  final Future<DebugChatSession> Function() start;
  final Future<DebugChatReply> Function(
    String sessionId,
    int turn,
    String message,
  )
  send;
  final Future<void> Function(String sessionId) end;
  final DebugAdviceVoice Function(String sessionId) voice;
  final VoidCallback onClose;

  @override
  State<DebugAdviceConversation> createState() =>
      _DebugAdviceConversationState();
}

class _DebugAdviceConversationState extends State<DebugAdviceConversation> {
  final _input = TextEditingController();
  final _turns = <({String question, DebugChatReply reply})>[];
  DebugChatSession? _session;
  String? _pendingQuestion;
  String? _error;
  bool _busy = true;

  @override
  void initState() {
    super.initState();
    unawaited(_start());
  }

  Future<void> _start() async {
    final end = widget.end;
    try {
      final session = await widget.start();
      if (!mounted) {
        unawaited(_end(end, session.id));
        return;
      }
      setState(() {
        _session = session;
        _busy = false;
      });
    } catch (_) {
      if (!mounted) return;
      setState(() {
        _busy = false;
        _error = '会話を開始できませんでした。再試行するか、アドバイスを生成し直してください。';
      });
    }
  }

  Future<void> _send() async {
    final session = _session;
    final question = _input.text.trim();
    if (session == null ||
        _busy ||
        _turns.length >= session.turnLimit ||
        question.isEmpty) {
      return;
    }
    widget.playback.stop();
    setState(() {
      _pendingQuestion = question;
      _busy = true;
      _error = null;
    });
    try {
      final reply = await widget.send(session.id, _turns.length + 1, question);
      if (!mounted) return;
      setState(() {
        _turns.add((question: question, reply: reply));
        _pendingQuestion = null;
        _input.clear();
        _busy = false;
      });
    } catch (_) {
      if (!mounted) return;
      setState(() {
        _busy = false;
        _error = '返信を取得できませんでした。入力を残しました。再試行できます。';
      });
    }
  }

  static Future<void> _end(
    Future<void> Function(String) end,
    String session,
  ) async {
    try {
      await end(session);
    } catch (_) {
      // The Backend also expires idle conversations.
    }
  }

  @override
  void dispose() {
    if (_session case final session?) unawaited(_end(widget.end, session.id));
    _input.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final session = _session;
    final latest = _turns.lastOrNull?.reply;
    final full = session != null && _turns.length >= session.turnLimit;
    final name = productionCharacterOptionFor(widget.character).displayName;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        OutlinedButton(onPressed: widget.onClose, child: const Text('会話を終了')),
        DebugAdviceExpression(
          widget.character,
          latest?.expressionTag ?? widget.adviceTag,
        ),
        for (final turn in _turns) ...[
          Text('あなた：${turn.question}'),
          Semantics(
            liveRegion: true,
            child: Text('$name：${turn.reply.message}'),
          ),
        ],
        if (session != null && latest != null && !_busy)
          if (latest.voiceRef case final ref?)
            DebugAdvicePlaybackControls(
              playback: widget.playback,
              voice: widget.voice(session.id),
              input: ref,
            )
          else
            Text('$nameの読み上げは利用できません。'),
        if (session != null && !full) ...[
          TextField(
            controller: _input,
            readOnly: _pendingQuestion != null,
            maxLength: 400,
            minLines: 1,
            maxLines: 3,
            decoration: const InputDecoration(labelText: '質問'),
            onChanged: (_) => setState(() {}),
          ),
          TextButton(
            onPressed: !_busy && _input.text.trim().isNotEmpty ? _send : null,
            child: Text(_error == null ? '質問を送る' : '質問を再試行'),
          ),
        ],
        if (full) const Text('この会話の上限に達しました。'),
        if (_busy)
          Semantics(
            liveRegion: true,
            child: Text(session == null ? '会話を開始しています。' : '返信を待っています。'),
          ),
        if (_error case final error?)
          Semantics(liveRegion: true, child: Text(error)),
        if (_error != null && session == null)
          TextButton(
            onPressed: () {
              setState(() {
                _busy = true;
                _error = null;
              });
              unawaited(_start());
            },
            child: const Text('会話の開始を再試行'),
          ),
      ],
    );
  }
}
