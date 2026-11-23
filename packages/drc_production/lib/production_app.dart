import 'package:flutter/material.dart';

import 'components/production_character_selection.dart';
import 'components/production_daily_advice.dart';
import 'components/production_journey_overview.dart';
import 'production_home_screen.dart';

class ProductionApp extends StatelessWidget {
  const ProductionApp({
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
    return MaterialApp(
      title: 'Daily Rhythm Companion',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF8B543D),
          surface: const Color(0xFFFFFAF5),
        ),
      ),
      home: ProductionHomeScreen(
        journeyHeader: journeyHeader,
        characterPortrait: characterPortrait,
        adviceExtension: adviceExtension,
        onlineAdvice: onlineAdvice,
      ),
    );
  }
}
