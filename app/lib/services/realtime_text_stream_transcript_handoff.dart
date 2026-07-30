import 'package:flutter/foundation.dart';

import '../models/provider_neutral_transcript.dart';
import '../models/realtime_text_stream.dart';
import 'realtime_text_stream_controller.dart';

typedef ProviderNeutralTranscriptProvider =
    Future<ProviderNeutralTranscriptResult?> Function();

typedef RealtimeTextStreamTranscriptHandoffFactory =
    RealtimeTextStreamTranscriptHandoff Function(
      RealtimeTextStreamController controller,
    );

@visibleForTesting
String boundRealtimeTextStreamTranscriptHandoffSafeMessageForTesting(
  String message,
) {
  return _safeMessage(message);
}

enum RealtimeTextStreamTranscriptHandoffPhase {
  ready,
  acquiring,
  accepted,
  rejected,
  failed,
  disposed,
}

@immutable
class RealtimeTextStreamTranscriptHandoffState {
  const RealtimeTextStreamTranscriptHandoffState({
    required this.phase,
    required this.safeMessage,
  });

  const RealtimeTextStreamTranscriptHandoffState.ready()
    : this(
        phase: RealtimeTextStreamTranscriptHandoffPhase.ready,
        safeMessage: '',
      );

  final RealtimeTextStreamTranscriptHandoffPhase phase;
  final String safeMessage;

  bool get isBusy =>
      phase == RealtimeTextStreamTranscriptHandoffPhase.acquiring;
}

class RealtimeTextStreamTranscriptHandoff extends ChangeNotifier {
  RealtimeTextStreamTranscriptHandoff({
    required RealtimeTextStreamController controller,
    required ProviderNeutralTranscriptProvider transcriptProvider,
  }) : _controller = controller,
       _transcriptProvider = transcriptProvider;

  final RealtimeTextStreamController _controller;
  final ProviderNeutralTranscriptProvider _transcriptProvider;
  final List<String> _consumedResultIds = <String>[];
  RealtimeTextStreamTranscriptHandoffState _state =
      const RealtimeTextStreamTranscriptHandoffState.ready();
  bool _startInFlight = false;
  bool _isDisposed = false;

  RealtimeTextStreamTranscriptHandoffState get state => _state;

  @visibleForTesting
  int get rememberedResultIdCount => _consumedResultIds.length;

  Future<void> startFromNextTranscript() async {
    if (_isDisposed) {
      return;
    }
    if (_startInFlight) {
      return;
    }
    if (_controller.state.isActive) {
      _reject('The text stream is already active.');
      return;
    }

    _startInFlight = true;
    try {
      _setState(
        const RealtimeTextStreamTranscriptHandoffState(
          phase: RealtimeTextStreamTranscriptHandoffPhase.acquiring,
          safeMessage: '',
        ),
      );

      ProviderNeutralTranscriptResult? result;
      try {
        result = await _transcriptProvider();
      } catch (_) {
        _fail('The transcript handoff could not acquire input safely.');
        return;
      }

      if (_isDisposed) {
        return;
      }
      if (result == null) {
        _reject('No final transcript is available for streaming.');
        return;
      }

      final resultId = result.resultId.trim();
      if (resultId.isEmpty ||
          resultId.runes.length > providerNeutralTranscriptMaxResultIdChars) {
        _reject('The transcript result could not be accepted safely.');
        return;
      }
      if (!result.isFinal) {
        _reject('Only a final transcript can start a text stream.');
        return;
      }

      final normalizedTranscript = result.text.trim();
      if (normalizedTranscript.isEmpty) {
        _reject('The final transcript was empty.');
        return;
      }
      if (normalizedTranscript.runes.length >
          providerNeutralTranscriptMaxTextChars) {
        _reject('The final transcript exceeded the text stream input limit.');
        return;
      }
      if (_consumedResultIds.contains(resultId)) {
        _reject('The transcript result was already used.');
        return;
      }
      _rememberResultId(resultId);

      try {
        await _controller.start(inputText: normalizedTranscript);
      } on RealtimeTextStreamProblemException catch (error) {
        _fail(error.problem.message);
        return;
      } catch (_) {
        _fail('The transcript handoff could not start the stream safely.');
        return;
      }

      if (_isDisposed) {
        return;
      }
      if (_controller.state.phase == RealtimeTextStreamControllerPhase.failed) {
        _fail(
          _controller.state.problem?.message ??
              'The transcript handoff could not start the stream safely.',
        );
        return;
      }
      _setState(
        const RealtimeTextStreamTranscriptHandoffState(
          phase: RealtimeTextStreamTranscriptHandoffPhase.accepted,
          safeMessage: '',
        ),
      );
    } finally {
      _startInFlight = false;
    }
  }

  void _rememberResultId(String resultId) {
    _consumedResultIds.add(resultId);
    while (_consumedResultIds.length >
        providerNeutralTranscriptMaxRememberedResultIds) {
      _consumedResultIds.removeAt(0);
    }
  }

  void _reject(String message) {
    _setState(
      RealtimeTextStreamTranscriptHandoffState(
        phase: RealtimeTextStreamTranscriptHandoffPhase.rejected,
        safeMessage: _safeMessage(message),
      ),
    );
  }

  void _fail(String message) {
    _setState(
      RealtimeTextStreamTranscriptHandoffState(
        phase: RealtimeTextStreamTranscriptHandoffPhase.failed,
        safeMessage: _safeMessage(message),
      ),
    );
  }

  void _setState(RealtimeTextStreamTranscriptHandoffState state) {
    if (_isDisposed) {
      return;
    }
    _state = state;
    notifyListeners();
  }

  @override
  void dispose() {
    if (_isDisposed) {
      return;
    }
    _isDisposed = true;
    _consumedResultIds.clear();
    _state = const RealtimeTextStreamTranscriptHandoffState(
      phase: RealtimeTextStreamTranscriptHandoffPhase.disposed,
      safeMessage: '',
    );
    super.dispose();
  }
}

String _safeMessage(String message) {
  final compact = message
      .trim()
      .split(RegExp(r'\s+'))
      .where((part) => part.isNotEmpty)
      .join(' ');
  if (compact.isEmpty) {
    return 'The transcript handoff could not continue safely.';
  }
  if (compact.runes.length <= realtimeTextStreamMaxProblemMessageChars) {
    return compact;
  }
  return String.fromCharCodes(
    compact.runes.take(realtimeTextStreamMaxProblemMessageChars),
  );
}
