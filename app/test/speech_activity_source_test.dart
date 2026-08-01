import 'package:app/services/speech_activity_source.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('SpeechActivitySourceConfig', () {
    test('production defaults remain bounded and default-off safe', () {
      const config = SpeechActivitySourceConfig();

      expect(config.thresholdDbfs, -24.0);
      expect(config.requiredConsecutiveSamples, 3);
      expect(config.sampleInterval, const Duration(milliseconds: 100));
      expect(config.cooldown, const Duration(milliseconds: 1500));
      expect(config.maximumLifetime, const Duration(seconds: 90));
      expect(config.isValid, isTrue);
    });

    test('rejects unbounded or nonsensical detector settings', () {
      expect(
        const SpeechActivitySourceConfig(
          requiredConsecutiveSamples: 0,
        ).isValid,
        isFalse,
      );
      expect(
        const SpeechActivitySourceConfig(
          sampleInterval: Duration(milliseconds: 1),
        ).isValid,
        isFalse,
      );
      expect(
        const SpeechActivitySourceConfig(
          cooldown: Duration(minutes: 1),
        ).isValid,
        isFalse,
      );
      expect(
        const SpeechActivitySourceConfig(
          maximumLifetime: Duration(minutes: 10),
        ).isValid,
        isFalse,
      );
    });
  });

  test('public event and state contain metadata only', () {
    const event = SpeechActivityEvent(
      eventId: 'speech-1-1',
      confirmed: true,
      foreground: true,
    );
    const state = SpeechActivitySourceState(
      phase: SpeechActivitySourcePhase.armed,
      armingGeneration: 1,
      emittedEventCount: 0,
      foreground: true,
    );

    expect(event.eventId, 'speech-1-1');
    expect(event.confirmed, isTrue);
    expect(event.foreground, isTrue);
    expect(state.isActive, isTrue);
    expect(state.technicalCode, isNull);
  });
}
