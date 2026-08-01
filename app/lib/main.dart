import 'package:flutter/material.dart';

import 'screens/home_screen.dart';
import 'services/backend_api_client.dart';
import 'services/configured_integrated_voice_turn_runtime.dart';
import 'services/configured_realtime_terminal_voice_output_runtime.dart';
import 'services/configured_realtime_text_stream_runtime.dart';
import 'services/integrated_voice_turn_home_screen_binding.dart';
import 'services/realtime_terminal_voice_output_home_screen_binding.dart';
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
  final configuredIntegratedVoiceTurnRuntime =
      ConfiguredIntegratedVoiceTurnRuntime.fromEnvironment(
        apiClient: apiClient,
      );
  final configuredVoiceOutputRuntime =
      ConfiguredRealtimeTerminalVoiceOutputRuntime.fromEnvironment(
        apiClient: apiClient,
      );

  runApp(
    DailyRhythmCompanionApp(
      apiClient: apiClient,
      realtimeTextStreamControllerFactory: configuredRuntime
          .buildControllerFactory(),
      realtimeTerminalVoiceOutputBindingFactory: configuredVoiceOutputRuntime
          .buildBindingFactory(),
      integratedVoiceTurnBindingFactory: configuredIntegratedVoiceTurnRuntime
          .buildBindingFactory(),
    ),
  );
}

class DailyRhythmCompanionApp extends StatelessWidget {
  const DailyRhythmCompanionApp({
    super.key,
    this.apiClient = const BackendApiClient(),
    this.realtimeTextStreamControllerFactory,
    this.realtimeTerminalVoiceOutputBindingFactory,
    this.integratedVoiceTurnBindingFactory,
  });

  final BackendApiClient apiClient;
  final RealtimeTextStreamController Function()?
  realtimeTextStreamControllerFactory;
  final RealtimeTerminalVoiceOutputHomeScreenBindingFactory?
  realtimeTerminalVoiceOutputBindingFactory;
  final IntegratedVoiceTurnHomeScreenBindingFactory?
  integratedVoiceTurnBindingFactory;

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
        realtimeTerminalVoiceOutputBindingFactory:
            realtimeTerminalVoiceOutputBindingFactory,
        integratedVoiceTurnBindingFactory: integratedVoiceTurnBindingFactory,
      ),
    );
  }
}
