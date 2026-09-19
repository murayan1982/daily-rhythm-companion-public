import 'package:flutter/material.dart';

import 'components/production_journey_overview.dart';

class ProductionHomeScreen extends StatelessWidget {
  const ProductionHomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(title: const Text('Daily Rhythm Companion')),
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
                    '睡眠と気分を確認して、今日の過ごし方を整える流れです。',
                    style: theme.textTheme.bodyLarge,
                  ),
                  const SizedBox(height: 24),
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
