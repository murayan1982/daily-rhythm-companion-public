import 'package:flutter/material.dart';

import 'components/production_character_selection.dart';
import 'components/production_daily_advice.dart';
import 'components/production_journey_overview.dart';
import 'production_about_screen.dart';

class ProductionHomeScreen extends StatelessWidget {
  const ProductionHomeScreen({
    super.key,
    this.journeyHeader,
    this.characterPortrait,
    this.adviceExtension,
    this.onlineAdvice,
  });

  final Widget? journeyHeader;
  final CharacterPortraitBuilder? characterPortrait;
  final JourneyAdviceBuilder? adviceExtension;
  final ProductionOnlineAdvice? onlineAdvice;

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
        title: Text(
          'Daily Rhythm Companion',
          style: theme.textTheme.titleMedium,
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
        ),
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
          padding: const EdgeInsets.fromLTRB(20, 12, 20, 24),
          child: Center(
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 720),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Semantics(
                    header: true,
                    child: Text(
                      '今日のリズム',
                      style: theme.textTheme.headlineMedium?.copyWith(
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                  if (journeyHeader case final header?) ...[
                    header,
                    const SizedBox(height: 20),
                  ],
                  ProductionJourneyOverview(
                    characterPortrait: characterPortrait,
                    adviceExtension: adviceExtension,
                    onlineAdvice: onlineAdvice,
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
