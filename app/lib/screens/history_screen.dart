import 'package:flutter/material.dart';

import '../models/daily_record.dart';
import '../models/recent_sleep_trend.dart';
import '../models/weekly_sleep_summary.dart';
import '../models/rhythm_report.dart';
import '../services/backend_api_client.dart';

class HistoryScreen extends StatefulWidget {
  const HistoryScreen({
    super.key,
    this.apiClient = const BackendApiClient(),
  });

  final BackendApiClient apiClient;

  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  bool _isLoading = false;
  String? _errorMessage;
  List<DailyRecord> _records = [];
  RecentSleepTrend? _recentSleepTrend;
  WeeklySleepSummary? _weeklySleepSummary;
  RhythmReport? _weeklyRhythmReport;
  RhythmReport? _monthlyRhythmReport;

  @override
  void initState() {
    super.initState();
    _loadDailyRecords();
  }

  Future<void> _loadDailyRecords() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final records = await widget.apiClient.fetchDailyRecords();
      final recentSleepTrend = await _loadRecentSleepTrendSafely();
      final weeklySleepSummary = await _loadWeeklySleepSummarySafely();
      final weeklyRhythmReport = await _loadRhythmReportSafely(period: 'weekly');
      final monthlyRhythmReport = await _loadRhythmReportSafely(period: 'monthly');

      setState(() {
        _records = records;
        _recentSleepTrend = recentSleepTrend;
        _weeklySleepSummary = weeklySleepSummary;
        _weeklyRhythmReport = weeklyRhythmReport;
        _monthlyRhythmReport = monthlyRhythmReport;
      });
    } catch (error) {
      setState(() {
        _errorMessage = _formatUserFacingError(error);
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<RecentSleepTrend?> _loadRecentSleepTrendSafely() async {
    try {
      return await widget.apiClient.fetchRecentSleepTrend();
    } catch (_) {
      return null;
    }
  }

  Future<WeeklySleepSummary?> _loadWeeklySleepSummarySafely() async {
    try {
      return await widget.apiClient.fetchWeeklySleepSummary();
    } catch (_) {
      return null;
    }
  }

  Future<RhythmReport?> _loadRhythmReportSafely({
    required String period,
  }) async {
    try {
      return await widget.apiClient.fetchRhythmReport(period: period);
    } catch (_) {
      return null;
    }
  }

  Widget _buildBody(BuildContext context) {
    if (_isLoading && _records.isEmpty) {
      return const Center(child: CircularProgressIndicator());
    }

    final errorMessage = _errorMessage;
    if (errorMessage != null && _records.isEmpty) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Text(errorMessage),
        ),
      );
    }

    if (_records.isEmpty) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text('まだ履歴がありません。'),
              const SizedBox(height: 12),
              FilledButton.tonal(
                onPressed: _loadDailyRecords,
                child: const Text('再読み込み'),
              ),
            ],
          ),
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _loadDailyRecords,
      child: ListView.separated(
        padding: const EdgeInsets.all(16),
        itemCount: _records.length + 5,
        separatorBuilder: (context, index) => const SizedBox(height: 12),
        itemBuilder: (context, index) {
          if (index == 0) {
            return _HistoryOverviewCard(recordCount: _records.length);
          }

          if (index == 1) {
            return _RecentSleepTrendCard(trend: _recentSleepTrend);
          }

          if (index == 2) {
            return _WeeklySleepSummaryCard(summary: _weeklySleepSummary);
          }

          if (index == 3) {
            return _RhythmReportCard(
              report: _weeklyRhythmReport,
              fallbackTitle: 'Weekly Rhythm Report',
              fallbackUnavailableLabel: '週次リズムレポート: 読み込み未完了',
            );
          }

          if (index == 4) {
            return _RhythmReportCard(
              report: _monthlyRhythmReport,
              fallbackTitle: 'Monthly Rhythm Report',
              fallbackUnavailableLabel: '月次リズムレポート: 読み込み未完了',
            );
          }

          final record = _records[index - 5];

          return _DailyRecordCard(record: record);
        },
      ),
    );
  }

  String _formatUserFacingError(Object error) {
    final message = error.toString();

    if (message.contains('Connection refused') ||
        message.contains('Failed host lookup') ||
        message.contains('SocketException')) {
      return 'バックエンドに接続できませんでした。backend が起動しているか確認してください。';
    }

    if (message.contains('TimeoutException')) {
      return 'バックエンドの応答が遅くなっています。少し待ってからもう一度試してください。';
    }

    return '履歴の読み込みでエラーが発生しました: $message';
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Daily History'),
        actions: [
          IconButton(
            onPressed: _isLoading ? null : _loadDailyRecords,
            icon: const Icon(Icons.refresh),
            tooltip: '再読み込み',
          ),
        ],
      ),
      body: _buildBody(context),
    );
  }
}

class _HistoryOverviewCard extends StatelessWidget {
  const _HistoryOverviewCard({required this.recordCount});

  final int recordCount;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'History / DailyRecord',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 8),
            const Text('過去の記録を振り返ります。'),
            const SizedBox(height: 4),
            const Text(
              '過去の睡眠記録や傾向は参考情報です。今日の睡眠としては扱いません。',
            ),
            const SizedBox(height: 8),
            Text(
              '表示件数: $recordCount',
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ],
        ),
      ),
    );
  }
}


class _RecentSleepTrendCard extends StatelessWidget {
  const _RecentSleepTrendCard({required this.trend});

  final RecentSleepTrend? trend;

  @override
  Widget build(BuildContext context) {
    final currentTrend = trend;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Recent Sleep Trend',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 8),
            const Text('履歴から見た直近傾向ラベルです。'),
            const SizedBox(height: 4),
            const Text('今日の睡眠データや健康状態の断定には使いません。'),
            const SizedBox(height: 12),
            if (currentTrend == null) ...[
              const Text('直近傾向: 読み込み未完了'),
              const SizedBox(height: 4),
              const Text('履歴一覧はそのまま確認できます。'),
            ] else ...[
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: [
                  Chip(label: Text(currentTrend.displayLabel)),
                  Chip(label: Text('平均: ${currentTrend.formattedAverageSleep}')),
                ],
              ),
              const SizedBox(height: 8),
              Text(currentTrend.displaySummary),
              const SizedBox(height: 4),
              Text(currentTrend.displayWindowSummary),
              const SizedBox(height: 4),
              Text(currentTrend.displayRecentDates),
              const SizedBox(height: 4),
              Text(
                currentTrend.displayNote,
                style: Theme.of(context).textTheme.bodySmall,
              ),
            ],
          ],
        ),
      ),
    );
  }
}


class _WeeklySleepSummaryCard extends StatelessWidget {
  const _WeeklySleepSummaryCard({required this.summary});

  final WeeklySleepSummary? summary;

  @override
  Widget build(BuildContext context) {
    final currentSummary = summary;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Simple Weekly Summary',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 8),
            const Text('過去のDailyRecordから作る軽い週次まとめです。'),
            const SizedBox(height: 4),
            const Text('今日の睡眠や健康状態の診断には使いません。'),
            const SizedBox(height: 12),
            if (currentSummary == null) ...[
              const Text('週次まとめ: 読み込み未完了'),
              const SizedBox(height: 4),
              const Text('履歴一覧と直近傾向はそのまま確認できます。'),
            ] else ...[
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: [
                  Chip(label: Text(currentSummary.displayLabel)),
                  Chip(label: Text('週平均: ${currentSummary.formattedAverageSleep}')),
                ],
              ),
              const SizedBox(height: 8),
              Text(currentSummary.displaySummary),
              const SizedBox(height: 4),
              Text('週対象: ${currentSummary.displayCoverage}'),
              const SizedBox(height: 4),
              Text(currentSummary.displayRecentDates),
              const SizedBox(height: 4),
              Text('メモ: ${currentSummary.actionHint}'),
              const SizedBox(height: 4),
              Text(
                currentSummary.displayNote,
                style: Theme.of(context).textTheme.bodySmall,
              ),
            ],
          ],
        ),
      ),
    );
  }
}


class _RhythmReportCard extends StatelessWidget {
  const _RhythmReportCard({
    required this.report,
    required this.fallbackTitle,
    required this.fallbackUnavailableLabel,
  });

  final RhythmReport? report;
  final String fallbackTitle;
  final String fallbackUnavailableLabel;

  @override
  Widget build(BuildContext context) {
    final currentReport = report;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              currentReport?.displayTitle ?? fallbackTitle,
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 8),
            const Text('過去のDailyRecordから作る軽いリズムレポートです。'),
            const SizedBox(height: 4),
            const Text('今日の睡眠や健康状態の診断には使いません。'),
            const SizedBox(height: 12),
            if (currentReport == null) ...[
              Text(fallbackUnavailableLabel),
              const SizedBox(height: 4),
              const Text('リズムレポートはまだ読み込めていません。'),
              const SizedBox(height: 4),
              const Text('履歴一覧と既存の週次まとめはそのまま確認できます。'),
            ] else ...[
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: [
                  Chip(label: Text(currentReport.displayLabel)),
                  Chip(label: Text('平均: ${currentReport.formattedAverageSleep}')),
                  Chip(label: Text(currentReport.displayDataQuality)),
                ],
              ),
              const SizedBox(height: 8),
              Text(currentReport.displaySummary),
              const SizedBox(height: 4),
              Text(currentReport.displayDateRange),
              const SizedBox(height: 4),
              Text(currentReport.displayRecordCoverage),
              const SizedBox(height: 4),
              Text(currentReport.displayRecordDates),
              const SizedBox(height: 4),
              Text(currentReport.displaySourceLabel),
              const SizedBox(height: 4),
              Text(currentReport.displayDataScope),
              const SizedBox(height: 4),
              Text('メモ: ${currentReport.actionHint}'),
              const SizedBox(height: 4),
              Text(
                currentReport.displayNote,
                style: Theme.of(context).textTheme.bodySmall,
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _DailyRecordCard extends StatelessWidget {
  const _DailyRecordCard({required this.record});

  final DailyRecord record;

  @override
  Widget build(BuildContext context) {
    final sleepSummary = record.sleepSummary;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(
                  child: Text(
                    record.date,
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                ),
                const Chip(label: Text('過去の記録')),
              ],
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                Chip(label: Text(record.characterName)),
                Chip(label: Text('気分: ${record.displayMood}')),
                Chip(label: Text(sleepSummary.displayDataKind)),
              ],
            ),
            const SizedBox(height: 12),
            Text('記録種別: 過去の記録'),
            const SizedBox(height: 4),
            Text(record.displayHistorySleepSummary),
            const SizedBox(height: 4),
            Text(record.displayHistorySleepSource),
            const SizedBox(height: 4),
            Text(
              record.displayHistoryContextNote,
              style: Theme.of(context).textTheme.bodySmall,
            ),
            const SizedBox(height: 8),
            Text(record.shortAdviceMessage),
            const SizedBox(height: 8),
            Text('Advice basis: ${record.displayAdviceBasis}'),
            if (record.hasReportReflection) ...[
              const SizedBox(height: 8),
              Text('Report reflection: ${record.displayReportReflectionLabel}'),
              const SizedBox(height: 4),
              Text(record.displayReportReflectionSummary),
              const SizedBox(height: 4),
              Text('Report quality: ${record.displayReportReflectionQuality}'),
              const SizedBox(height: 4),
              Text('Report source: ${record.displayReportReflectionSource}'),
            ],
            if (record.adviceSource != null) ...[
              const SizedBox(height: 8),
              Text('Source: ${record.adviceSource!.displayEngine}'),
            ],
            const SizedBox(height: 8),
            Text(
              '更新: ${record.displayUpdatedAt}',
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ],
        ),
      ),
    );
  }
}
