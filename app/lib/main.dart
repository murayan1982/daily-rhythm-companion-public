import 'package:flutter/material.dart';

import 'screens/home_screen.dart';

void main() {
  runApp(const DailyRhythmCompanionApp());
}

class DailyRhythmCompanionApp extends StatelessWidget {
  const DailyRhythmCompanionApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Daily Rhythm Companion',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.blueGrey),
      ),
      home: const HomeScreen(),
    );
  }
}