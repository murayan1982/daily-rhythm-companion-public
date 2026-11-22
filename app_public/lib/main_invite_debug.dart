import 'package:drc_production/core/production_character.dart';
import 'package:drc_production/core/production_mood.dart';
import 'package:drc_production/production_app.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

import 'health_connect_sleep_card.dart';
import 'invite_advice_debug.dart';

void main() {
  runApp(
    const ProductionApp(
      journeyHeader: HealthConnectSleepCard(),
      adviceExtension: kDebugMode ? _buildInviteAdviceCard : null,
    ),
  );
}

Widget _buildInviteAdviceCard(
  ProductionMood? mood,
  ProductionCharacter? character,
) => InviteAdviceDebugCard(mood: mood, character: character);
