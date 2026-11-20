import 'package:drc_production/production_app.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

void main() => runApp(const ProductionApp(journeyHeader: _SleepCard()));

class _SleepCard extends StatefulWidget {
  const _SleepCard();

  @override
  State<_SleepCard> createState() => _SleepCardState();
}

class _SleepCardState extends State<_SleepCard> {
  static const _channel = MethodChannel('drc/sleep_debug');
  bool _loading = false;
  String _message = '睡眠を読み込まずにアドバイスへ進むこともできます。';

  Future<void> _readSleep() async {
    setState(() {
      _loading = true;
      _message = '睡眠を確認しています。';
    });

    String message;
    try {
      final result = await _channel.invokeMapMethod<String, Object?>('read');
      if (!mounted) return;
      message = switch (result?['status']) {
        'ok' => _formatSession(result!),
        'denied' => '睡眠の読み取りが許可されていません。',
        'empty' => '昨夜の対象になる睡眠記録が見つかりませんでした。',
        'unavailable' => 'この端末では Health Connect を利用できません。',
        _ => '睡眠を読み取れませんでした。時間をおいて再試行できます。',
      };
    } on PlatformException {
      message = '睡眠を読み取れませんでした。時間をおいて再試行できます。';
    } on MissingPluginException {
      message = 'このビルドでは Health Connect を利用できません。';
    }

    if (!mounted) return;
    setState(() {
      _message = message;
      _loading = false;
    });
  }

  String _formatSession(Map<String, Object?> result) {
    final localizations = MaterialLocalizations.of(context);
    String formatTime(String key) {
      final date = DateTime.fromMillisecondsSinceEpoch(result[key]! as int);
      final time = localizations.formatTimeOfDay(
        TimeOfDay.fromDateTime(date),
        alwaysUse24HourFormat: true,
      );
      return '${date.month}/${date.day} $time';
    }

    final minutes = result['minutes']! as int;
    return '${formatTime('start')} 〜 ${formatTime('end')}\n'
        '記録の長さ ${minutes ~/ 60}時間${minutes % 60}分';
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Semantics(
              header: true,
              child: Text(
                '昨夜の睡眠',
                style: Theme.of(context).textTheme.titleMedium,
              ),
            ),
            const SizedBox(height: 8),
            Semantics(liveRegion: true, child: Text(_message)),
            TextButton(
              onPressed: _loading ? null : _readSleep,
              child: const Text('Health Connect から読み込む'),
            ),
          ],
        ),
      ),
    );
  }
}
