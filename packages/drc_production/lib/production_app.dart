import 'package:flutter/material.dart';

import 'production_home_screen.dart';

class ProductionApp extends StatelessWidget {
  const ProductionApp({super.key, this.journeyHeader});

  final Widget? journeyHeader;

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Daily Rhythm Companion',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.teal),
      ),
      home: ProductionHomeScreen(journeyHeader: journeyHeader),
    );
  }
}
