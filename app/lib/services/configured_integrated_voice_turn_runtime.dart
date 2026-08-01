import 'dart:async';

import 'package:flutter/foundation.dart';

import 'backend_api_client.dart';
import 'backend_provider_neutral_transcript_provider.dart';
import 'backend_voice_input_staging_consumer.dart';
import 'configured_realtime_terminal_voice_output_runtime.dart';
import 'configured_realtime_text_stream_runtime.dart';
import 'integrated_voice_turn_coordinator.dart';
import 'integrated_voice_turn_home_screen_binding.dart';
import 'microphone_capture.dart';
import 'microphone_capture_host_audio_handoff.dart';
import 'permission_handler_microphone_permission_gateway.dart';
import 'realtime_text_stream_transcript_handoff.dart';
import 'record_microphone_capture_engine.dart';
import 'record_speech_activity_source.dart';

const String configuredIntegratedVoiceTurnEnvironmentName =
    'DRC_RT5F3_ENABLE_CONFIGURED_VOICE_TURN';

typedef ConfiguredIntegratedVoiceTurnBindingBuilder =
    IntegratedVoiceTurnHomeScreenBinding Function();

/// Default-off RT-5f3 production assembly.
///
/// Building this runtime or obtaining its binding factory does not request
/// microphone permission, start package:record, execute HTTP/provider work,
/// synthesize speech, or start local playback. Every execution path still
/// requires the compile-time switch, both prerequisite runtime switches, a
/// supported mobile platform, session-local opt-in, and an explicit UI action.
class ConfiguredIntegratedVoiceTurnRuntime {
  ConfiguredIntegratedVoiceTurnRuntime({
    required this.enabled,
    required this.textStreamEnabled,
    required this.voiceOutputEnabled,
    required this.apiClient,
    bool? supportedPlatform,
    ConfiguredIntegratedVoiceTurnBindingBuilder? bindingBuilder,
  }) : supportedPlatform =
           supportedPlatform ??
           (!kIsWeb &&
               (defaultTargetPlatform == TargetPlatform.android ||
                   defaultTargetPlatform == TargetPlatform.iOS)),
       _bindingBuilder = bindingBuilder;

  factory ConfiguredIntegratedVoiceTurnRuntime.fromEnvironment({
    BackendApiClient apiClient = const BackendApiClient(),
  }) {
    return ConfiguredIntegratedVoiceTurnRuntime(
      enabled: const bool.fromEnvironment(
        configuredIntegratedVoiceTurnEnvironmentName,
        defaultValue: false,
      ),
      textStreamEnabled: const bool.fromEnvironment(
        'DRC_RT4_ENABLE_CONFIGURED_TEXT_STREAM',
        defaultValue: false,
      ),
      voiceOutputEnabled: const bool.fromEnvironment(
        'DRC_RT5_ENABLE_CONFIGURED_VOICE_OUTPUT',
        defaultValue: false,
      ),
      apiClient: apiClient,
    );
  }

  final bool enabled;
  final bool textStreamEnabled;
  final bool voiceOutputEnabled;
  final BackendApiClient apiClient;
  final bool supportedPlatform;
  final ConfiguredIntegratedVoiceTurnBindingBuilder? _bindingBuilder;

  IntegratedVoiceTurnHomeScreenBindingFactory? buildBindingFactory() {
    final configuredBaseUrl = apiClient.baseUrl.trim();
    if (!enabled ||
        !textStreamEnabled ||
        !voiceOutputEnabled ||
        !supportedPlatform ||
        !_isValidBackendBaseUrl(configuredBaseUrl)) {
      return null;
    }

    return _bindingBuilder ??
        () => _buildProductionBinding(configuredBaseUrl: configuredBaseUrl);
  }

  IntegratedVoiceTurnHomeScreenBinding _buildProductionBinding({
    required String configuredBaseUrl,
  }) {
    final captureEngine = RecordMicrophoneCaptureEngine.mobile();
    final captureController = MicrophoneCaptureController(
      permissionGateway: PermissionHandlerMicrophonePermissionGateway(),
      engine: captureEngine,
      maximumAllowedDuration: integratedVoiceTurnCaptureMaximumDuration,
    );
    final captureSession = IntegratedVoiceTurnCaptureSession(
      controller: captureController,
    );

    final stagingConsumer = BackendVoiceInputStagingConsumer(
      baseUrl: configuredBaseUrl,
    );
    final handoffController = HostAudioHandoffController(
      privateArtifactAccess: captureEngine,
      consumer: stagingConsumer,
      maximumAllowedDuration: integratedVoiceTurnCaptureMaximumDuration,
    );

    late IntegratedVoiceTurnHomeScreenBinding binding;
    final transcriptProvider = BackendProviderNeutralTranscriptProvider(
      baseUrl: configuredBaseUrl,
      takeStagedArtifact: stagingConsumer.takeStagedArtifact,
      foregroundOptIn: () =>
          binding.state.optedIn && binding.state.foreground,
    );

    void disposeBaseResources() {
      unawaited(captureSession.close());
      unawaited(handoffController.close());
      transcriptProvider.dispose();
    }

    final streamControllerFactory = ConfiguredRealtimeTextStreamRuntime(
      enabled: true,
      baseUrl: configuredBaseUrl,
    ).buildControllerFactory();
    final voiceBindingFactory = ConfiguredRealtimeTerminalVoiceOutputRuntime(
      enabled: true,
      apiClient: apiClient,
    ).buildBindingFactory();
    if (streamControllerFactory == null || voiceBindingFactory == null) {
      disposeBaseResources();
      throw StateError('configured_integrated_voice_turn_assembly_failed');
    }

    try {
      final dedicatedVoiceBinding = voiceBindingFactory();
      IntegratedVoiceTurnCoordinator? coordinator;
      RecordSpeechActivitySource? speechActivitySource;
      try {
        coordinator = IntegratedVoiceTurnCoordinator(
          captureCompleted: captureSession.captureCompleted,
          stageCapture: (captureResult) async {
            final retained = await handoffController.retain(
              captureResult,
              language: 'ja',
              maximumDuration: integratedVoiceTurnCaptureMaximumDuration,
              publicMetadata: const <String, Object?>{
                'capture_owner': 'drc_integrated_voice_turn',
                'host_app': 'daily_rhythm_companion',
                'input_mode': 'microphone',
                'private_artifact_cleanup_required': true,
                'raw_audio_exposed': false,
              },
            );
            if (retained.outcome != HostAudioHandoffOutcome.retained) {
              return retained;
            }
            return handoffController.consume();
          },
          streamControllerFactory: streamControllerFactory,
          transcriptHandoffFactory: (controller) {
            return RealtimeTextStreamTranscriptHandoff(
              controller: controller,
              transcriptProvider: transcriptProvider.acquireNextTranscript,
            );
          },
          voiceOutput: dedicatedVoiceBinding.orchestrator,
        );
        speechActivitySource = RecordSpeechActivitySource();

        binding = IntegratedVoiceTurnHomeScreenBinding(
          coordinator: coordinator,
          captureSession: captureSession,
          speechActivitySource: speechActivitySource,
          disposeOwnedResources: () async {
            await handoffController.close();
            transcriptProvider.dispose();
            dedicatedVoiceBinding.dispose();
          },
        );
        return binding;
      } catch (_) {
        coordinator?.dispose();
        final source = speechActivitySource;
        if (source != null) {
          unawaited(source.close());
        }
        dedicatedVoiceBinding.dispose();
        rethrow;
      }
    } catch (_) {
      disposeBaseResources();
      rethrow;
    }
  }
}

bool _isValidBackendBaseUrl(String value) {
  final uri = Uri.tryParse(value.trim());
  if (uri == null || !uri.isAbsolute) {
    return false;
  }
  if (uri.scheme != 'http' && uri.scheme != 'https') {
    return false;
  }
  if (uri.host.isEmpty ||
      uri.hasQuery ||
      uri.hasFragment ||
      uri.userInfo.isNotEmpty) {
    return false;
  }
  return uri.path.isEmpty || uri.path == '/';
}
