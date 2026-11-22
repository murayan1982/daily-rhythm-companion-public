import 'package:drc_production/production_app.dart';
import 'package:flutter/material.dart';

import 'health_connect_sleep_card.dart';
import 'invite_advice.dart';

void main() {
  runApp(
    buildInviteReleaseApp(
      endpointUrl: const String.fromEnvironment('DRC_INVITE_ADVICE_URL'),
    ),
  );
}

ProductionApp buildInviteReleaseApp({
  required String endpointUrl,
  InviteAdviceTransport? transport,
}) {
  final endpoint = _httpsAdviceEndpoint(endpointUrl);
  if (endpoint == null) {
    return const ProductionApp(journeyHeader: HealthConnectSleepCard());
  }

  final client = InviteAdviceClient(endpoint: endpoint, transport: transport);
  return ProductionApp(
    journeyHeader: const HealthConnectSleepCard(),
    adviceExtension: (mood, character) =>
        InviteAdviceCard(mood: mood, character: character, client: client),
  );
}

Uri? _httpsAdviceEndpoint(String value) {
  if (RegExp(r'[\s\\]').hasMatch(value)) return null;
  final endpoint = Uri.tryParse(value);
  if (endpoint == null ||
      endpoint.scheme != 'https' ||
      endpoint.host.isEmpty ||
      endpoint.authority.contains('@') ||
      endpoint.port < 1 ||
      endpoint.port > 65535 ||
      endpoint.path != '/v1/advice' ||
      endpoint.hasQuery ||
      endpoint.hasFragment) {
    return null;
  }
  return endpoint;
}
