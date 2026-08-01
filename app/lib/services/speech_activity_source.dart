import 'dart:async';

import 'package:flutter/foundation.dart';

const double speechActivityDefaultThresholdDbfs = -24.0;
const int speechActivityDefaultRequiredConsecutiveSamples = 3;
const Duration speechActivityDefaultSampleInterval = Duration(
  milliseconds: 100,
);
const Duration speechActivityDefaultCooldown = Duration(milliseconds: 1500);
const Duration speechActivityDefaultMaximumLifetime = Duration(seconds: 90);

@immutable
class SpeechActivitySourceConfig {
  const SpeechActivitySourceConfig({
    this.thresholdDbfs = speechActivityDefaultThresholdDbfs,
    this.requiredConsecutiveSamples =
        speechActivityDefaultRequiredConsecutiveSamples,
    this.sampleInterval = speechActivityDefaultSampleInterval,
    this.cooldown = speechActivityDefaultCooldown,
    this.maximumLifetime = speechActivityDefaultMaximumLifetime,
  });

  final double thresholdDbfs;
  final int requiredConsecutiveSamples;
  final Duration sampleInterval;
  final Duration cooldown;
  final Duration maximumLifetime;

  bool get isValid =>
      thresholdDbfs.isFinite &&
      thresholdDbfs <= 0 &&
      requiredConsecutiveSamples > 0 &&
      requiredConsecutiveSamples <= 32 &&
      sampleInterval >= const Duration(milliseconds: 20) &&
      sampleInterval <= const Duration(seconds: 2) &&
      cooldown >= Duration.zero &&
      cooldown <= const Duration(seconds: 30) &&
      maximumLifetime > Duration.zero &&
      maximumLifetime <= const Duration(minutes: 5);
}

enum SpeechActivitySourcePhase {
  idle,
  starting,
  armed,
  cooldown,
  stopping,
  stopped,
  failed,
  disposed,
}

@immutable
class SpeechActivityEvent {
  const SpeechActivityEvent({
    required this.eventId,
    required this.confirmed,
    required this.foreground,
  });

  final String eventId;
  final bool confirmed;
  final bool foreground;
}

@immutable
class SpeechActivitySourceState {
  const SpeechActivitySourceState({
    required this.phase,
    required this.armingGeneration,
    required this.emittedEventCount,
    required this.foreground,
    this.technicalCode,
  });

  const SpeechActivitySourceState.idle()
    : this(
        phase: SpeechActivitySourcePhase.idle,
        armingGeneration: 0,
        emittedEventCount: 0,
        foreground: true,
      );

  final SpeechActivitySourcePhase phase;
  final int armingGeneration;
  final int emittedEventCount;
  final bool foreground;
  final String? technicalCode;

  bool get isActive =>
      phase == SpeechActivitySourcePhase.starting ||
      phase == SpeechActivitySourcePhase.armed ||
      phase == SpeechActivitySourcePhase.cooldown ||
      phase == SpeechActivitySourcePhase.stopping;
}

typedef SpeechActivityEventHandler =
    FutureOr<void> Function(SpeechActivityEvent event);

/// DRC-owned bounded speech-activity boundary.
///
/// Public state is metadata-only. Implementations must not expose amplitude,
/// PCM bytes, device identifiers, paths, transcript text, provider metadata, or
/// raw exceptions through this contract.
abstract class SpeechActivitySource extends ChangeNotifier {
  SpeechActivitySourceState get state;

  void setEventHandler(SpeechActivityEventHandler? handler);

  Future<bool> arm({required int generation, required bool foreground});

  Future<void> setForeground(bool foreground);

  Future<void> disarm();

  Future<void> close();
}

abstract interface class SpeechActivityDeadline {
  void cancel();
}

abstract interface class SpeechActivityDeadlineScheduler {
  SpeechActivityDeadline schedule(
    Duration duration,
    FutureOr<void> Function() onDeadline,
  );
}

class TimerSpeechActivityDeadlineScheduler
    implements SpeechActivityDeadlineScheduler {
  const TimerSpeechActivityDeadlineScheduler();

  @override
  SpeechActivityDeadline schedule(
    Duration duration,
    FutureOr<void> Function() onDeadline,
  ) {
    return _TimerSpeechActivityDeadline(
      Timer(duration, () => unawaited(Future<void>.sync(onDeadline))),
    );
  }
}

class _TimerSpeechActivityDeadline implements SpeechActivityDeadline {
  _TimerSpeechActivityDeadline(this._timer);

  final Timer _timer;

  @override
  void cancel() => _timer.cancel();
}
