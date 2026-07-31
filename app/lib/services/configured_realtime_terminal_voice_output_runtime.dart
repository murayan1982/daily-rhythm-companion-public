import 'dart:async';

import '../models/voice_output_demo.dart';
import 'audioplayers_voice_output_audio_engine.dart';
import 'backend_api_client.dart';
import 'realtime_terminal_voice_output_home_screen_binding.dart';
import 'realtime_terminal_voice_output_orchestrator.dart';
import 'voice_output_audio_player.dart';
import 'voice_output_queue.dart';

const String configuredRealtimeTerminalVoiceOutputFrameworkApiName =
    'framework.create_voice_output_session().create_output';
const String configuredRealtimeTerminalVoiceOutputClientEventId =
    'rt5e-realtime-terminal-voice-output';
const String configuredRealtimeTerminalVoiceOutputPurpose = 'realtime_terminal';

typedef ConfiguredRealtimeTerminalVoiceOutputAudioEngineFactory =
    VoiceOutputAudioEngine Function();

/// Default-off RT-5e runtime assembly for one explicitly processed queue item.
///
/// Building this object or its binding factory does not enqueue terminal text,
/// execute Backend/FW synthesis, drain the app-owned queue, or start playback.
/// The returned binding owns a dedicated local player that is separate from the
/// existing Voice Output Demo player owned directly by HomeScreen.
class ConfiguredRealtimeTerminalVoiceOutputRuntime {
  ConfiguredRealtimeTerminalVoiceOutputRuntime({
    required this.enabled,
    required this.apiClient,
    ConfiguredRealtimeTerminalVoiceOutputAudioEngineFactory? audioEngineFactory,
  }) : _audioEngineFactory =
           audioEngineFactory ?? (() => AudioplayersVoiceOutputAudioEngine());

  factory ConfiguredRealtimeTerminalVoiceOutputRuntime.fromEnvironment({
    BackendApiClient apiClient = const BackendApiClient(),
    ConfiguredRealtimeTerminalVoiceOutputAudioEngineFactory? audioEngineFactory,
  }) {
    return ConfiguredRealtimeTerminalVoiceOutputRuntime(
      enabled: const bool.fromEnvironment(
        'DRC_RT5_ENABLE_CONFIGURED_VOICE_OUTPUT',
        defaultValue: false,
      ),
      apiClient: apiClient,
      audioEngineFactory: audioEngineFactory,
    );
  }

  final bool enabled;
  final BackendApiClient apiClient;
  final ConfiguredRealtimeTerminalVoiceOutputAudioEngineFactory
  _audioEngineFactory;

  RealtimeTerminalVoiceOutputHomeScreenBindingFactory? buildBindingFactory() {
    final configuredBaseUrl = apiClient.baseUrl.trim();
    if (!enabled || !_isValidBackendBaseUrl(configuredBaseUrl)) {
      return null;
    }

    return () {
      final audioPlayer = VoiceOutputAudioPlayerController(
        engine: _audioEngineFactory(),
      );
      final terminalPlayback = _ConfiguredRealtimeTerminalVoicePlayback(
        controller: audioPlayer,
      );
      final queue = VoiceOutputQueueController(
        stopLocalPlayback: terminalPlayback.stop,
      );
      final synthesis = _ConfiguredRealtimeTerminalVoiceSynthesis(
        apiClient: apiClient,
        configuredBaseUrl: configuredBaseUrl,
      );
      final orchestrator = RealtimeTerminalVoiceOutputOrchestrator(
        queue: queue,
        synthesize: synthesis.call,
        playToTerminal: terminalPlayback.playToTerminal,
      );

      return OwnedRealtimeTerminalVoiceOutputHomeScreenBinding(
        orchestrator: orchestrator,
        disposeOwnedResources: () {
          terminalPlayback.dispose();
          queue.dispose();
        },
      );
    };
  }
}

class _ConfiguredRealtimeTerminalVoiceSynthesis {
  const _ConfiguredRealtimeTerminalVoiceSynthesis({
    required this.apiClient,
    required this.configuredBaseUrl,
  });

  final BackendApiClient apiClient;
  final String configuredBaseUrl;

  Future<RealtimeTerminalVoiceSynthesisResult> call(
    RealtimeTerminalVoiceSynthesisRequest request,
  ) async {
    VoiceOutputDemoRequestResponse response;
    try {
      response = await apiClient.submitVoiceOutputDemoRequest(
        clientEventId: configuredRealtimeTerminalVoiceOutputClientEventId,
        outputMode: 'tts',
        textContent: request.utterance,
        characterId: null,
        voiceProfileId: null,
        audioFormat: 'mp3',
        utterancePurpose: configuredRealtimeTerminalVoiceOutputPurpose,
      );
    } catch (_) {
      return const RealtimeTerminalVoiceSynthesisResult.failed();
    }

    if (!_hasExactGeneratedContract(response)) {
      if (!response.accepted ||
          const <String>{
            'rejected',
            'unavailable',
            'skipped',
          }.contains(response.requestState)) {
        return const RealtimeTerminalVoiceSynthesisResult.rejected();
      }
      return const RealtimeTerminalVoiceSynthesisResult.failed();
    }

    final source = _resolveConfiguredAudioSource(
      baseUrl: configuredBaseUrl,
      audioUrl: response.audioUrl,
    );
    if (source == null) {
      return const RealtimeTerminalVoiceSynthesisResult.failed();
    }

    return RealtimeTerminalVoiceSynthesisResult.audioReady(source.toString());
  }
}

class _ConfiguredRealtimeTerminalVoicePlayback {
  _ConfiguredRealtimeTerminalVoicePlayback({required this.controller}) {
    controller.addListener(_handleStateChanged);
  }

  final VoiceOutputAudioPlayerController controller;

  Completer<RealtimeTerminalVoicePlaybackResult>? _activeCompleter;
  bool _isDisposed = false;

  Future<RealtimeTerminalVoicePlaybackResult> playToTerminal(Uri source) async {
    if (_isDisposed || _activeCompleter != null) {
      return const RealtimeTerminalVoicePlaybackResult.failed();
    }

    final completer = Completer<RealtimeTerminalVoicePlaybackResult>();
    _activeCompleter = completer;

    try {
      await controller.play(source);
      _completeFromCurrentState();
    } catch (_) {
      _complete(const RealtimeTerminalVoicePlaybackResult.failed());
    }

    return completer.future;
  }

  Future<void> stop() async {
    if (_isDisposed) {
      return;
    }

    await controller.stop();
    _completeFromCurrentState();
  }

  void _handleStateChanged() {
    _completeFromCurrentState();
  }

  void _completeFromCurrentState() {
    switch (controller.state.phase) {
      case VoiceOutputPlaybackPhase.completed:
        _complete(const RealtimeTerminalVoicePlaybackResult.completed());
        break;
      case VoiceOutputPlaybackPhase.failed:
        _complete(const RealtimeTerminalVoicePlaybackResult.failed());
        break;
      case VoiceOutputPlaybackPhase.expired:
        _complete(const RealtimeTerminalVoicePlaybackResult.expired());
        break;
      case VoiceOutputPlaybackPhase.stopped:
        _complete(const RealtimeTerminalVoicePlaybackResult.stopped());
        break;
      case VoiceOutputPlaybackPhase.idle:
      case VoiceOutputPlaybackPhase.loading:
      case VoiceOutputPlaybackPhase.playing:
        break;
    }
  }

  void _complete(RealtimeTerminalVoicePlaybackResult result) {
    final completer = _activeCompleter;
    if (completer == null || completer.isCompleted) {
      return;
    }
    _activeCompleter = null;
    completer.complete(result);
  }

  void dispose() {
    if (_isDisposed) {
      return;
    }
    _isDisposed = true;
    _complete(const RealtimeTerminalVoicePlaybackResult.stopped());
    controller.removeListener(_handleStateChanged);
    controller.dispose();
  }
}

bool _hasExactGeneratedContract(VoiceOutputDemoRequestResponse response) {
  return response.accepted &&
      response.requestState == 'generated' &&
      response.frameworkCallState == 'generated' &&
      response.frameworkApiName ==
          configuredRealtimeTerminalVoiceOutputFrameworkApiName &&
      response.audioReady &&
      response.hasAudioHandoff &&
      response.audioHandoffKind == 'url' &&
      response.isGenerated &&
      response.audioArtifactRef == null &&
      response.audioFormat == 'mp3';
}

Uri? _resolveConfiguredAudioSource({
  required String baseUrl,
  required String? audioUrl,
}) {
  final normalized = audioUrl?.trim();
  if (normalized == null ||
      !RegExp(
        r'^/demo/voice-output/audio/[0-9a-f]{32}$',
      ).hasMatch(normalized)) {
    return null;
  }

  final relative = Uri.tryParse(normalized);
  final base = Uri.tryParse(baseUrl);
  if (relative == null ||
      base == null ||
      relative.isAbsolute ||
      relative.hasQuery ||
      relative.hasFragment ||
      relative.userInfo.isNotEmpty) {
    return null;
  }

  final resolved = base.resolveUri(relative);
  if (!resolved.isAbsolute ||
      (resolved.scheme != 'http' && resolved.scheme != 'https') ||
      resolved.host.isEmpty ||
      resolved.hasQuery ||
      resolved.hasFragment ||
      resolved.userInfo.isNotEmpty) {
    return null;
  }
  return resolved;
}

bool _isValidBackendBaseUrl(String value) {
  final uri = Uri.tryParse(value);
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
