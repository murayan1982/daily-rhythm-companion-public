import 'package:flutter/material.dart';

import 'production_home_screen.dart';

class ProductionApp extends StatelessWidget {
  const ProductionApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Daily Rhythm Companion',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.teal),
      ),
      home: const ProductionHomeScreen(),
    );
  }
}
