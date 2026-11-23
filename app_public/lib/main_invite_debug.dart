import 'package:drc_production/production_app.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

import 'health_connect_sleep_card.dart';
import 'invite_advice.dart';

void main() {
  runApp(
    kDebugMode
        ? InviteAdviceApp(
            client: InviteAdviceClient(endpoint: _loopbackEndpoint),
            tokenLabel: '招待トークン（検証用）',
            initiallyShowToken: true,
          )
        : const ProductionApp(journeyHeader: HealthConnectSleepCard()),
  );
}

final _loopbackEndpoint = Uri.http('127.0.0.1:8000', '/v1/advice');
