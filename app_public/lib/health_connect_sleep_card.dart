import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

class HealthConnectSleepCard extends StatefulWidget {
  const HealthConnectSleepCard({super.key, this.onActualSleepMinutesChanged});

  final ValueChanged<int?>? onActualSleepMinutesChanged;

  @override
  State<HealthConnectSleepCard> createState() => _HealthConnectSleepCardState();
}

class _HealthConnectSleepCardState extends State<HealthConnectSleepCard>
    with WidgetsBindingObserver {
  static const _channel = MethodChannel('drc/health_connect_sleep');
  static const _initial = '読み込まなくても気分を選べます。';
  static const _error = '睡眠を読み取れませんでした。時間をおいて再試行できます。';
  bool _loading = false;
  bool _showingRecord = false;
  String _message = _initial;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (_showingRecord && _isBackgrounded(state)) {
      // Leaving for Android settings can revoke access. Clear the display
      // without reading records or checking permissions on resume.
      setState(() {
        _showingRecord = false;
        _message = _initial;
      });
      widget.onActualSleepMinutesChanged?.call(null);
    }
  }

  bool _isBackgrounded(AppLifecycleState? state) =>
      state == AppLifecycleState.hidden ||
      state == AppLifecycleState.paused ||
      state == AppLifecycleState.detached;

  Future<void> _readSleep() async {
    if (_loading) return;
    final onActualSleep = widget.onActualSleepMinutesChanged;
    onActualSleep?.call(null);
    setState(() {
      _loading = true;
      _showingRecord = false;
      _message = '睡眠を確認しています。';
    });

    var showingRecord = false;
    int? actualSleepMinutes;
    String message;
    try {
      final result = await _channel.invokeMapMethod<String, Object?>(
        'read',
        onActualSleep == null ? null : {'includeActualSleep': true},
      );
      if (!mounted) return;
      message = switch (result?['status']) {
        'denied' => '睡眠の読み取りが許可されていません。',
        'empty' => '昨夜の対象になる睡眠記録が見つかりませんでした。',
        'unavailable' => 'この端末では Health Connect を利用できません。',
        _ => _error,
      };
      if (result case {
        'status': 'ok',
        'start': final int start,
        'end': final int end,
        'minutes': final int minutes,
      } when end >= start && minutes >= 0) {
        showingRecord = !_isBackgrounded(
          WidgetsBinding.instance.lifecycleState,
        );
        message = showingRecord
            ? _formatSession(start, end, minutes)
            : _initial;
        final actual = result['actualSleepMinutes'];
        if (showingRecord &&
            onActualSleep != null &&
            actual is int &&
            actual > 0 &&
            actual <= minutes &&
            actual <= 1440) {
          actualSleepMinutes = actual;
          message = '$message\n実睡眠時間 $actual 分';
        }
      }
    } on PlatformException {
      message = _error;
    } on MissingPluginException {
      message = 'このビルドでは Health Connect を利用できません。';
    }

    if (!mounted) return;
    setState(() {
      _message = message;
      _showingRecord = showingRecord;
      _loading = false;
    });
    onActualSleep?.call(actualSleepMinutes);
  }

  String _formatSession(int start, int end, int minutes) {
    final localizations = MaterialLocalizations.of(context);
    String formatTime(int millis) {
      final date = DateTime.fromMillisecondsSinceEpoch(millis);
      final time = localizations.formatTimeOfDay(
        TimeOfDay.fromDateTime(date),
        alwaysUse24HourFormat: true,
      );
      return '${date.month}/${date.day} $time';
    }

    return '${formatTime(start)} 〜 ${formatTime(end)}\n'
        '記録の長さ ${minutes ~/ 60}時間${minutes % 60}分';
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Card(
      margin: EdgeInsets.zero,
      elevation: 0,
      color: theme.colorScheme.surfaceContainer,
      child: Padding(
        padding: const EdgeInsets.fromLTRB(16, 12, 16, 4),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Semantics(
              header: true,
              child: Text('昨夜の睡眠', style: theme.textTheme.titleMedium),
            ),
            const SizedBox(height: 4),
            Semantics(liveRegion: true, child: Text(_message)),
            TextButton(
              onPressed: _loading ? null : _readSleep,
              child: const Text('睡眠を読み込む'),
            ),
          ],
        ),
      ),
    );
  }
}
