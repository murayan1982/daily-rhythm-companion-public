import 'dart:async';

import 'package:app/services/record_speech_activity_source.dart';
import 'package:app/services/speech_activity_source.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('RecordSpeechActivitySource', () {
    test('three consecutive threshold samples emit exactly once', () async {
      final fixture = _Fixture();
      final events = <SpeechActivityEvent>[];
      fixture.source.setEventHandler(events.add);

      expect(
        await fixture.source.arm(generation: 7, foreground: true),
        isTrue,
      );
      fixture.driver.emit(-23.0);
      fixture.driver.emit(-22.0);
      expect(events, isEmpty);
      fixture.driver.emit(-21.0);
      await _drainMicrotasks();

      expect(events, hasLength(1));
      expect(events.single.eventId, 'speech-7-1');
      expect(events.single.confirmed, isTrue);
      expect(events.single.foreground, isTrue);
      expect(
        fixture.source.state.phase,
        SpeechActivitySourcePhase.cooldown,
      );
      expect(fixture.source.state.emittedEventCount, 1);

      fixture.driver.emit(-10.0);
      fixture.driver.emit(-10.0);
      fixture.driver.emit(-10.0);
      fixture.scheduler.fireLatestFor(const Duration(milliseconds: 1500));
      fixture.driver.emit(-60.0);
      fixture.driver.emit(-10.0);
      fixture.driver.emit(-10.0);
      fixture.driver.emit(-10.0);
      await _drainMicrotasks();

      expect(events, hasLength(1));
      await fixture.close();
    });

    test('below-threshold sample resets consecutive confirmation', () async {
      final fixture = _Fixture();
      final events = <SpeechActivityEvent>[];
      fixture.source.setEventHandler(events.add);
      await fixture.source.arm(generation: 1, foreground: true);

      fixture.driver.emit(-20.0);
      fixture.driver.emit(-20.0);
      fixture.driver.emit(-40.0);
      fixture.driver.emit(-20.0);
      fixture.driver.emit(-20.0);
      await _drainMicrotasks();
      expect(events, isEmpty);

      fixture.driver.emit(-20.0);
      await _drainMicrotasks();
      expect(events, hasLength(1));
      await fixture.close();
    });

    test('a new arming generation may emit a new event', () async {
      final fixture = _Fixture();
      final events = <SpeechActivityEvent>[];
      fixture.source.setEventHandler(events.add);

      await fixture.source.arm(generation: 1, foreground: true);
      fixture.driver.emitConfirmedSpeech();
      await _drainMicrotasks();
      await fixture.source.disarm();

      expect(
        await fixture.source.arm(generation: 2, foreground: true),
        isTrue,
      );
      fixture.driver.emitConfirmedSpeech();
      await _drainMicrotasks();

      expect(events.map((event) => event.eventId), <String>[
        'speech-1-1',
        'speech-2-2',
      ]);
      expect(fixture.driver.startCalls, 2);
      expect(fixture.driver.stopCalls, 1);
      await fixture.close();
    });

    test('background disarms active source and rejects background arm', () async {
      final fixture = _Fixture();
      expect(
        await fixture.source.arm(generation: 1, foreground: false),
        isFalse,
      );
      expect(fixture.driver.startCalls, 0);

      expect(
        await fixture.source.arm(generation: 1, foreground: true),
        isTrue,
      );
      await fixture.source.setForeground(false);

      expect(fixture.driver.stopCalls, 1);
      expect(fixture.source.state.foreground, isFalse);
      expect(
        fixture.source.state.phase,
        SpeechActivitySourcePhase.stopped,
      );
      expect(
        fixture.source.state.technicalCode,
        'speech_activity_background_disarmed',
      );
      await fixture.close();
    });

    test('maximum lifetime disarms and stops the driver', () async {
      final fixture = _Fixture();
      await fixture.source.arm(generation: 4, foreground: true);

      await fixture.scheduler.fireLatestFor(const Duration(seconds: 90));

      expect(fixture.driver.stopCalls, 1);
      expect(
        fixture.source.state.phase,
        SpeechActivitySourcePhase.stopped,
      );
      expect(
        fixture.source.state.technicalCode,
        'speech_activity_maximum_lifetime_reached',
      );
      await fixture.close();
    });

    test('late samples after disarm are inert', () async {
      final fixture = _Fixture();
      final events = <SpeechActivityEvent>[];
      fixture.source.setEventHandler(events.add);
      await fixture.source.arm(generation: 1, foreground: true);
      await fixture.source.disarm();

      fixture.driver.emitConfirmedSpeech();
      await _drainMicrotasks();

      expect(events, isEmpty);
      expect(
        fixture.source.state.phase,
        SpeechActivitySourcePhase.stopped,
      );
      await fixture.close();
    });

    test('close waits for an in-flight driver start before disposal', () async {
      final startBarrier = Completer<void>();
      final fixture = _Fixture(
        driver: _FakeDriver(startBarrier: startBarrier),
      );

      final armFuture = fixture.source.arm(
        generation: 1,
        foreground: true,
      );
      await _waitFor(() => fixture.driver.startCalls == 1);
      final closeFuture = fixture.source.close();
      await _drainMicrotasks();

      expect(fixture.driver.disposeCalls, 0);
      startBarrier.complete();

      expect(await armFuture, isFalse);
      await closeFuture;
      expect(fixture.driver.stopCalls, 1);
      expect(fixture.driver.disposeCalls, 1);
      expect(
        fixture.source.state.phase,
        SpeechActivitySourcePhase.disposed,
      );
    });

    test('driver start and stream failures expose fixed codes only', () async {
      final startFailure = _Fixture(driver: _FakeDriver(failStart: true));
      expect(
        await startFailure.source.arm(generation: 1, foreground: true),
        isFalse,
      );
      expect(
        startFailure.source.state.technicalCode,
        'speech_activity_driver_start_failed',
      );
      expect(
        startFailure.source.state.technicalCode,
        isNot(contains('private raw exception sentinel')),
      );
      await startFailure.close();

      final streamFailure = _Fixture();
      await streamFailure.source.arm(generation: 1, foreground: true);
      streamFailure.driver.failStream();
      await _drainMicrotasks();
      expect(
        streamFailure.source.state.technicalCode,
        'speech_activity_driver_stream_failed',
      );
      await streamFailure.close();
    });

    test('close is idempotent and disposes the production boundary once', () async {
      final fixture = _Fixture();
      await fixture.source.arm(generation: 1, foreground: true);

      await fixture.source.close();
      await fixture.source.close();

      expect(fixture.driver.disposeCalls, 1);
      expect(
        fixture.source.state.phase,
        SpeechActivitySourcePhase.disposed,
      );
    });
  });
}

class _Fixture {
  _Fixture({_FakeDriver? driver})
    : driver = driver ?? _FakeDriver(),
      scheduler = _FakeScheduler() {
    source = RecordSpeechActivitySource(
      driver: this.driver,
      deadlineScheduler: scheduler,
    );
  }

  final _FakeDriver driver;
  final _FakeScheduler scheduler;
  late final RecordSpeechActivitySource source;

  Future<void> close() => source.close();
}

class _FakeDriver implements RecordSpeechActivityDriver {
  _FakeDriver({this.failStart = false, this.startBarrier});

  final bool failStart;
  final Completer<void>? startBarrier;
  final StreamController<double> _amplitudes =
      StreamController<double>.broadcast(sync: true);
  int startCalls = 0;
  int stopCalls = 0;
  int disposeCalls = 0;
  bool started = false;

  @override
  Stream<double> get amplitudeDbfs => _amplitudes.stream;

  @override
  Future<void> start({required Duration sampleInterval}) async {
    startCalls += 1;
    if (failStart) {
      throw StateError('private raw exception sentinel');
    }
    await startBarrier?.future;
    started = true;
  }

  void emit(double value) => _amplitudes.add(value);

  void emitConfirmedSpeech() {
    emit(-20.0);
    emit(-20.0);
    emit(-20.0);
  }

  void failStream() {
    _amplitudes.addError(StateError('private raw exception sentinel'));
  }

  @override
  Future<void> stop() async {
    if (!started) {
      return;
    }
    stopCalls += 1;
    started = false;
  }

  @override
  Future<void> dispose() async {
    disposeCalls += 1;
    started = false;
    await _amplitudes.close();
  }
}

class _FakeScheduler implements SpeechActivityDeadlineScheduler {
  final List<_FakeDeadline> deadlines = <_FakeDeadline>[];

  @override
  SpeechActivityDeadline schedule(
    Duration duration,
    FutureOr<void> Function() onDeadline,
  ) {
    final deadline = _FakeDeadline(duration, onDeadline);
    deadlines.add(deadline);
    return deadline;
  }

  Future<void> fireLatestFor(Duration duration) async {
    final deadline = deadlines.lastWhere(
      (candidate) => candidate.duration == duration && !candidate.cancelled,
    );
    await deadline.fire();
  }
}

class _FakeDeadline implements SpeechActivityDeadline {
  _FakeDeadline(this.duration, this._onDeadline);

  final Duration duration;
  final FutureOr<void> Function() _onDeadline;
  bool cancelled = false;

  @override
  void cancel() {
    cancelled = true;
  }

  Future<void> fire() async {
    if (!cancelled) {
      await Future<void>.sync(_onDeadline);
    }
  }
}

Future<void> _waitFor(bool Function() predicate) async {
  for (var index = 0; index < 100; index += 1) {
    if (predicate()) {
      return;
    }
    await Future<void>.delayed(Duration.zero);
  }
  fail('condition not reached');
}

Future<void> _drainMicrotasks() async {
  await Future<void>.delayed(Duration.zero);
  await Future<void>.delayed(Duration.zero);
}
