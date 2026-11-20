import 'package:flutter/material.dart';

import 'components/production_character_selection.dart';
import 'production_home_screen.dart';

class ProductionApp extends StatelessWidget {
  const ProductionApp({super.key, this.journeyHeader, this.characterPortrait});

  final Widget? journeyHeader;
  final CharacterPortraitBuilder? characterPortrait;

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Daily Rhythm Companion',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.teal),
      ),
      home: ProductionHomeScreen(
        journeyHeader: journeyHeader,
        characterPortrait: characterPortrait,
      ),
    );
  }
}
