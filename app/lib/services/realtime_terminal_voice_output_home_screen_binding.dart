import 'package:flutter/foundation.dart';

import 'realtime_terminal_voice_output_orchestrator.dart';

typedef RealtimeTerminalVoiceOutputHomeScreenBindingFactory =
    RealtimeTerminalVoiceOutputHomeScreenBinding Function();

abstract interface class RealtimeTerminalVoiceOutputHomeScreenBinding {
  RealtimeTerminalVoiceOutputOrchestrator get orchestrator;

  void dispose();
}

class OwnedRealtimeTerminalVoiceOutputHomeScreenBinding
    implements RealtimeTerminalVoiceOutputHomeScreenBinding {
  OwnedRealtimeTerminalVoiceOutputHomeScreenBinding({
    required this.orchestrator,
    VoidCallback? disposeOwnedResources,
  }) : _disposeOwnedResources = disposeOwnedResources;

  @override
  final RealtimeTerminalVoiceOutputOrchestrator orchestrator;

  final VoidCallback? _disposeOwnedResources;
  bool _isDisposed = false;

  bool get isDisposed => _isDisposed;

  @override
  void dispose() {
    if (_isDisposed) {
      return;
    }
    _isDisposed = true;

    try {
      orchestrator.dispose();
    } catch (_) {
      // HomeScreen teardown must remain fail-closed and idempotent.
    }

    try {
      _disposeOwnedResources?.call();
    } catch (_) {
      // Binding-owned cleanup failures are intentionally not surfaced raw.
    }
  }
}
