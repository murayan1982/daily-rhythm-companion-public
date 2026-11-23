import 'package:flutter/material.dart';

import 'package:drc_production/production_app.dart';

import 'bundled_character_portrait.dart';
import 'health_connect_sleep_card.dart';

void main() {
  runApp(
    const ProductionApp(
      journeyHeader: HealthConnectSleepCard(),
      characterPortrait: buildBundledCharacterPortrait,
    ),
  );
}
