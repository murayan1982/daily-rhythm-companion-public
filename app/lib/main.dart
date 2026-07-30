import 'package:flutter/material.dart';

import 'screens/home_screen.dart';
import 'services/backend_api_client.dart';
import 'services/configured_realtime_text_stream_runtime.dart';
import 'services/realtime_text_stream_controller.dart';

void main() {
  const apiClient = BackendApiClient();
  final configuredRuntime = ConfiguredRealtimeTextStreamRuntime(
    enabled: const bool.fromEnvironment(
      'DRC_RT4_ENABLE_CONFIGURED_TEXT_STREAM',
      defaultValue: false,
    ),
    baseUrl: apiClient.baseUrl,
  );

  runApp(
    DailyRhythmCompanionApp(
      apiClient: apiClient,
      realtimeTextStreamControllerFactory: configuredRuntime
          .buildControllerFactory(),
    ),
  );
}

class DailyRhythmCompanionApp extends StatelessWidget {
  const DailyRhythmCompanionApp({
    super.key,
    this.apiClient = const BackendApiClient(),
    this.realtimeTextStreamControllerFactory,
  });

  final BackendApiClient apiClient;
  final RealtimeTextStreamController Function()?
  realtimeTextStreamControllerFactory;

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Daily Rhythm Companion',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.blueGrey),
      ),
      home: HomeScreen(
        apiClient: apiClient,
        realtimeTextStreamControllerFactory:
            realtimeTextStreamControllerFactory,
      ),
    );
  }
}
