import 'package:flutter/material.dart';

import 'components/production_journey_overview.dart';
import 'production_about_screen.dart';

class ProductionHomeScreen extends StatelessWidget {
  const ProductionHomeScreen({super.key, this.journeyHeader});

  final Widget? journeyHeader;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    void openAbout() {
      Navigator.of(context).push(
        MaterialPageRoute<void>(
          builder: (context) => const ProductionAboutScreen(),
        ),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Daily Rhythm Companion'),
        actions: [
          Semantics(
            label: 'アプリについて',
            button: true,
            onTap: openAbout,
            child: ExcludeSemantics(
              child: IconButton(
                tooltip: 'アプリについて',
                icon: const Icon(Icons.info_outline),
                onPressed: openAbout,
              ),
            ),
          ),
        ],
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 24),
          child: Center(
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 720),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Semantics(
                    header: true,
                    child: Text('今日のリズム', style: theme.textTheme.headlineSmall),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    '気分とキャラクターを選ぶと、端末内で今日のアドバイスを表示します。選択内容は保存されません。',
                    style: theme.textTheme.bodyLarge,
                  ),
                  const SizedBox(height: 24),
                  if (journeyHeader case final header?) ...[
                    header,
                    const SizedBox(height: 24),
                  ],
                  const ProductionJourneyOverview(),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
