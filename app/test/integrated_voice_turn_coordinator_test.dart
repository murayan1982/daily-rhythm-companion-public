import 'dart:async';
import 'dart:collection';

import 'package:app/models/provider_neutral_transcript.dart';
import 'package:app/models/realtime_text_stream.dart';
import 'package:app/services/integrated_voice_turn_coordinator.dart';
import 'package:app/services/microphone_capture.dart';
import 'package:app/services/microphone_capture_host_audio_handoff.dart';
import 'package:app/services/realtime_terminal_voice_output_orchestrator.dart';
import 'package:app/services/realtime_text_stream_client.dart';
import 'package:app/services/realtime_text_stream_controller.dart';
import 'package:app/services/realtime_text_stream_transcript_handoff.dart';
import 'package:app/services/voice_output_queue.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;

void main() {
  group('IntegratedVoiceTurnCoordinator', () {
    test(
      'pre-existing pending voice output blocks turn before capture',
      () async {
        final harness = _Harness();
        final enqueue = harness.voiceOutput.enqueueCompletedTerminal(
          _completedVoiceOutputState(
            sessionId: 'preexisting-pending-session',
            turnId: 'preexisting-pending-turn',
            text: 'preexisting pending output',
          ),
        );

        final result = await harness.coordinator.startNextTurn();

        expect(enqueue.accepted, isTrue);
        expect(result.outcome, IntegratedVoiceTurnOutcome.busy);
        expect(result.technicalCode, 'integrated_voice_turn_voice_output_busy');
        expect(harness.captureCalls, 0);
        expect(harness.voiceOutput.state.pendingCount, 1);

        harness.dispose();
      },
    );

    test('pre-existing active synthesis blocks turn before capture', () async {
      final harness = _Harness();
      final synthesis = Completer<RealtimeTerminalVoiceSynthesisResult>();
      harness.synthesisResults.add(synthesis.future);
      final enqueue = harness.voiceOutput.enqueueCompletedTerminal(
        _completedVoiceOutputState(
          sessionId: 'preexisting-active-session',
          turnId: 'preexisting-active-turn',
          text: 'preexisting active output',
        ),
      );
      final processFuture = harness.voiceOutput.processNext();
      await _waitFor(
        () =>
            harness.voiceOutput.state.phase ==
            RealtimeTerminalVoiceOutputPhase.synthesizing,
      );

      final result = await harness.coordinator.startNextTurn();

      expect(enqueue.accepted, isTrue);
      expect(result.outcome, IntegratedVoiceTurnOutcome.busy);
      expect(harness.captureCalls, 0);

      synthesis.complete(
        const RealtimeTerminalVoiceSynthesisResult.audioReady(
          'https://audio.test/preexisting-active.mp3',
        ),
      );
      expect(
        (await processFuture).outcome,
        RealtimeTerminalVoiceOutputProcessOutcome.completed,
      );

      harness.dispose();
    });

    test(
      'voice output becoming non-exclusive before terminal enqueue rejects turn',
      () async {
        final harness = _Harness();

        final turnFuture = harness.coordinator.startNextTurn();
        final client = await harness.waitForStreaming(0);
        final externalEnqueue = harness.voiceOutput.enqueueCompletedTerminal(
          _completedVoiceOutputState(
            sessionId: 'external-pending-session',
            turnId: 'external-pending-turn',
            text: 'external pending output',
          ),
        );
        client.emitCompleted('current terminal output');

        final result = await turnFuture;

        expect(externalEnqueue.accepted, isTrue);
        expect(result.outcome, IntegratedVoiceTurnOutcome.voiceOutputRejected);
        expect(
          result.technicalCode,
          'integrated_voice_turn_voice_output_not_exclusive',
        );
        expect(harness.synthesisCalls, 0);
        expect(harness.voiceOutput.state.pendingCount, 1);

        harness.dispose();
      },
    );

    test(
      'voice-output phase listener cannot enqueue between exclusivity check and enqueue',
      () async {
        final harness = _Harness();
        var listenerAttempted = false;
        RealtimeTerminalVoiceOutputEnqueueResult? listenerEnqueue;

        void listener() {
          if (listenerAttempted ||
              harness.coordinator.state.phase !=
                  IntegratedVoiceTurnPhase.voiceOutput) {
            return;
          }
          listenerAttempted = true;
          listenerEnqueue = harness.voiceOutput.enqueueCompletedTerminal(
            _completedVoiceOutputState(
              sessionId: 'listener-pending-session',
              turnId: 'listener-pending-turn',
              text: 'listener pending output',
            ),
          );
        }

        harness.coordinator.addListener(listener);
        final turnFuture = harness.coordinator.startNextTurn();
        final client = await harness.waitForStreaming(0);
        client.emitCompleted('current listener-race output');

        final result = await turnFuture;

        expect(listenerAttempted, isTrue);
        expect(listenerEnqueue?.accepted, isTrue);
        expect(result.outcome, IntegratedVoiceTurnOutcome.voiceOutputRejected);
        expect(
          result.technicalCode,
          'integrated_voice_turn_voice_output_not_exclusive',
        );
        expect(harness.synthesisCalls, 0);
        expect(harness.voiceOutput.state.pendingCount, 1);

        harness.coordinator.removeListener(listener);
        harness.dispose();
      },
    );

    test(
      'processed voice-output item must match current terminal item',
      () async {
        final harness = _Harness(mismatchProcessedItem: true);

        final turnFuture = harness.coordinator.startNextTurn();
        final client = await harness.waitForStreaming(0);
        client.emitCompleted('mismatched item output');

        final result = await turnFuture;

        expect(result.outcome, IntegratedVoiceTurnOutcome.voiceOutputFailed);
        expect(
          result.technicalCode,
          'integrated_voice_turn_voice_output_item_mismatch',
        );
        expect(harness.captureCalls, 1);
        expect(harness.stagingCalls, 1);

        harness.dispose();
      },
    );
    test('happy-path full fake voice turn completes exactly once', () async {
      final harness = _Harness();

      final turnFuture = harness.coordinator.startNextTurn();
      final client = await harness.waitForStreaming(0);
      client.emitCompleted('assistant output');

      final result = await turnFuture;

      expect(result.outcome, IntegratedVoiceTurnOutcome.completed);
      expect(harness.captureCalls, 1);
      expect(harness.stagingCalls, 1);
      expect(harness.synthesisCalls, 1);
      expect(harness.playbackCalls, 1);
      expect(harness.localStopCalls, 0);
      expect(
        harness.coordinator.state.phase,
        IntegratedVoiceTurnPhase.completed,
      );
      expect(harness.coordinator.state.pendingVoiceOutputCount, 0);

      harness.dispose();
    });

    test('speech during capture makes a late capture result inert', () async {
      final harness = _Harness();
      final capture = Completer<MicrophoneCaptureResult>();
      harness.captureResults.add(capture.future);

      final turnFuture = harness.coordinator.startNextTurn();
      await _waitFor(
        () =>
            harness.coordinator.state.phase ==
            IntegratedVoiceTurnPhase.capturing,
      );

      final speech = await harness.coordinator.handleSpeechActivity(
        _speech('capture-speech'),
      );
      capture.complete(_completedCapture());

      expect(speech.outcome, IntegratedVoiceTurnSpeechOutcome.interrupted);
      expect(
        (await turnFuture).outcome,
        IntegratedVoiceTurnOutcome.invalidated,
      );
      expect(harness.stagingCalls, 0);
      expect(harness.synthesisCalls, 0);

      harness.dispose();
    });

    test('speech during staging makes a late staging result inert', () async {
      final harness = _Harness();
      final staging = Completer<HostAudioHandoffResult>();
      harness.stagingResults.add(staging.future);

      final turnFuture = harness.coordinator.startNextTurn();
      await _waitFor(
        () =>
            harness.coordinator.state.phase == IntegratedVoiceTurnPhase.staging,
      );

      final speech = await harness.coordinator.handleSpeechActivity(
        _speech('staging-speech'),
      );
      staging.complete(_completedStaging());

      expect(speech.outcome, IntegratedVoiceTurnSpeechOutcome.interrupted);
      expect(
        (await turnFuture).outcome,
        IntegratedVoiceTurnOutcome.invalidated,
      );
      expect(harness.clients, isEmpty);
      expect(harness.synthesisCalls, 0);

      harness.dispose();
    });

    test('speech during transcript acquisition makes late STT inert', () async {
      final harness = _Harness();
      final transcript = Completer<ProviderNeutralTranscriptResult?>();
      harness.transcriptResults.add(transcript.future);

      final turnFuture = harness.coordinator.startNextTurn();
      await harness.waitForClient(0);
      await _waitFor(
        () =>
            harness.coordinator.state.phase ==
            IntegratedVoiceTurnPhase.acquiringTranscript,
      );

      final speech = await harness.coordinator.handleSpeechActivity(
        _speech('transcript-speech'),
      );
      transcript.complete(_transcript('late-stt', 'late transcript'));

      expect(speech.outcome, IntegratedVoiceTurnSpeechOutcome.interrupted);
      expect(
        (await turnFuture).outcome,
        IntegratedVoiceTurnOutcome.invalidated,
      );
      expect(harness.clients.single.createCalls, 0);
      expect(harness.synthesisCalls, 0);

      harness.dispose();
    });

    test('speech during stream requests one cooperative cancel', () async {
      final harness = _Harness();

      final turnFuture = harness.coordinator.startNextTurn();
      final client = await harness.waitForClient(0);
      await _waitFor(
        () =>
            harness.coordinator.state.phase ==
            IntegratedVoiceTurnPhase.streaming,
      );

      final speech = await harness.coordinator.handleSpeechActivity(
        _speech('stream-speech'),
      );
      client.emitCompleted('late stream result');

      expect(speech.outcome, IntegratedVoiceTurnSpeechOutcome.interrupted);
      expect(client.cancelCalls, 1);
      expect(
        (await turnFuture).outcome,
        IntegratedVoiceTurnOutcome.invalidated,
      );
      expect(harness.synthesisCalls, 0);

      harness.dispose();
    });

    test(
      'speech during synthesis permits a new turn before old Future completion',
      () async {
        final harness = _Harness();
        final oldSynthesis = Completer<RealtimeTerminalVoiceSynthesisResult>();
        harness.synthesisResults.add(oldSynthesis.future);

        final oldTurn = harness.coordinator.startNextTurn();
        final oldClient = await harness.waitForStreaming(0);
        oldClient.emitCompleted('old response');
        await _waitFor(
          () =>
              harness.voiceOutput.state.phase ==
              RealtimeTerminalVoiceOutputPhase.synthesizing,
        );

        final speech = await harness.coordinator.handleSpeechActivity(
          _speech('synthesis-speech'),
        );
        expect(speech.outcome, IntegratedVoiceTurnSpeechOutcome.interrupted);

        final newTurn = harness.coordinator.startNextTurn();
        final newClient = await harness.waitForStreaming(1);
        newClient.emitCompleted('new response');

        expect((await newTurn).outcome, IntegratedVoiceTurnOutcome.completed);
        expect(oldSynthesis.isCompleted, isFalse);

        oldSynthesis.complete(
          const RealtimeTerminalVoiceSynthesisResult.audioReady(
            'https://audio.test/old.mp3',
          ),
        );
        expect((await oldTurn).outcome, IntegratedVoiceTurnOutcome.invalidated);
        expect(harness.playbackCalls, 1);

        harness.dispose();
      },
    );

    test(
      'speech during playback permits new playback before old Future completion',
      () async {
        final harness = _Harness();
        final oldPlayback = Completer<RealtimeTerminalVoicePlaybackResult>();
        harness.playbackResults.add(oldPlayback.future);

        final oldTurn = harness.coordinator.startNextTurn();
        final oldClient = await harness.waitForStreaming(0);
        oldClient.emitCompleted('old playback response');
        await _waitFor(
          () =>
              harness.voiceOutput.state.phase ==
              RealtimeTerminalVoiceOutputPhase.playing,
        );

        final speech = await harness.coordinator.handleSpeechActivity(
          _speech('playback-speech'),
        );
        expect(speech.outcome, IntegratedVoiceTurnSpeechOutcome.interrupted);

        final newTurn = harness.coordinator.startNextTurn();
        final newClient = await harness.waitForStreaming(1);
        newClient.emitCompleted('new playback response');

        expect((await newTurn).outcome, IntegratedVoiceTurnOutcome.completed);
        expect(oldPlayback.isCompleted, isFalse);

        oldPlayback.complete(
          const RealtimeTerminalVoicePlaybackResult.completed(),
        );
        expect((await oldTurn).outcome, IntegratedVoiceTurnOutcome.invalidated);

        harness.dispose();
      },
    );

    test(
      'duplicate speech is rejected and concurrent distinct events coalesce',
      () async {
        final harness = _Harness();
        final localStop = Completer<void>();
        harness.localStopResults.add(localStop.future);

        final turnFuture = harness.coordinator.startNextTurn();
        final client = await harness.waitForClient(0);
        await _waitFor(
          () =>
              harness.coordinator.state.phase ==
              IntegratedVoiceTurnPhase.streaming,
        );

        final first = harness.coordinator.handleSpeechActivity(
          _speech('speech-one'),
        );
        await _waitFor(
          () =>
              harness.coordinator.state.phase ==
              IntegratedVoiceTurnPhase.interrupting,
        );

        final duplicate = await harness.coordinator.handleSpeechActivity(
          _speech('speech-one'),
        );
        final coalesced = harness.coordinator.handleSpeechActivity(
          _speech('speech-two'),
        );

        expect(duplicate.outcome, IntegratedVoiceTurnSpeechOutcome.duplicate);
        expect(harness.localStopCalls, 1);
        expect(client.cancelCalls, 1);

        localStop.complete();

        expect(
          (await first).outcome,
          IntegratedVoiceTurnSpeechOutcome.interrupted,
        );
        expect(
          (await coalesced).outcome,
          IntegratedVoiceTurnSpeechOutcome.coalesced,
        );
        expect(
          (await turnFuture).outcome,
          IntegratedVoiceTurnOutcome.invalidated,
        );
        expect(harness.localStopCalls, 1);

        harness.dispose();
      },
    );

    test(
      'local playback stop failure blocks turns until speech retry',
      () async {
        final harness = _Harness();
        final failedStop = Completer<void>();
        harness.localStopResults.add(failedStop.future);

        final oldTurn = harness.coordinator.startNextTurn();
        await harness.waitForClient(0);
        await _waitFor(
          () =>
              harness.coordinator.state.phase ==
              IntegratedVoiceTurnPhase.streaming,
        );

        final failedFuture = harness.coordinator.handleSpeechActivity(
          _speech('stop-failure'),
        );
        failedStop.completeError(StateError('stop failed'));
        final failed = await failedFuture;

        expect(
          failed.outcome,
          IntegratedVoiceTurnSpeechOutcome.localStopFailed,
        );
        expect(harness.coordinator.state.localStopRetryRequired, isTrue);
        expect(
          (await harness.coordinator.startNextTurn()).outcome,
          IntegratedVoiceTurnOutcome.localStopRetryRequired,
        );

        final retry = await harness.coordinator.handleSpeechActivity(
          _speech('stop-retry'),
        );
        expect(retry.outcome, IntegratedVoiceTurnSpeechOutcome.interrupted);
        expect(harness.coordinator.state.localStopRetryRequired, isFalse);
        expect((await oldTurn).outcome, IntegratedVoiceTurnOutcome.invalidated);

        final newTurn = harness.coordinator.startNextTurn();
        final newClient = await harness.waitForStreaming(1);
        newClient.emitCompleted('after retry');
        expect((await newTurn).outcome, IntegratedVoiceTurnOutcome.completed);

        harness.dispose();
      },
    );

    test('stream cancel request failure does not revive old work', () async {
      final harness = _Harness();
      final cancel = Completer<RealtimeTextStreamCancelResponse>();
      harness.cancelResults.add(cancel.future);

      final turnFuture = harness.coordinator.startNextTurn();
      final client = await harness.waitForClient(0);
      await _waitFor(
        () =>
            harness.coordinator.state.phase ==
            IntegratedVoiceTurnPhase.streaming,
      );

      final speech = await harness.coordinator.handleSpeechActivity(
        _speech('cancel-failure'),
      );
      cancel.completeError(StateError('cancel failed'));
      client.emitCompleted('late after cancel error');

      expect(speech.outcome, IntegratedVoiceTurnSpeechOutcome.interrupted);
      expect(
        (await turnFuture).outcome,
        IntegratedVoiceTurnOutcome.invalidated,
      );
      expect(harness.synthesisCalls, 0);

      harness.dispose();
    });

    test('cancelled stream terminal never reaches TTS', () async {
      final harness = _Harness();

      final turnFuture = harness.coordinator.startNextTurn();
      final client = await harness.waitForStreaming(0);
      client.emitCancelled();

      final result = await turnFuture;

      expect(result.outcome, IntegratedVoiceTurnOutcome.streamCancelled);
      expect(harness.synthesisCalls, 0);
      expect(harness.playbackCalls, 0);

      harness.dispose();
    });

    test('invalid speech events do not interrupt active work', () async {
      final harness = _Harness();

      final turnFuture = harness.coordinator.startNextTurn();
      final client = await harness.waitForClient(0);
      await _waitFor(
        () =>
            harness.coordinator.state.phase ==
            IntegratedVoiceTurnPhase.streaming,
      );

      for (final activity in <IntegratedVoiceTurnSpeechActivity>[
        const IntegratedVoiceTurnSpeechActivity(
          eventId: '',
          confirmed: true,
          foreground: true,
        ),
        const IntegratedVoiceTurnSpeechActivity(
          eventId: 'not confirmed',
          confirmed: false,
          foreground: true,
        ),
        const IntegratedVoiceTurnSpeechActivity(
          eventId: 'background',
          confirmed: true,
          foreground: false,
        ),
        const IntegratedVoiceTurnSpeechActivity(
          eventId: 'unsafe/event',
          confirmed: true,
          foreground: true,
        ),
        const IntegratedVoiceTurnSpeechActivity(
          eventId: ' padded-event ',
          confirmed: true,
          foreground: true,
        ),
      ]) {
        expect(
          (await harness.coordinator.handleSpeechActivity(activity)).outcome,
          IntegratedVoiceTurnSpeechOutcome.invalid,
        );
      }

      expect(client.cancelCalls, 0);
      expect(harness.localStopCalls, 0);
      client.emitCompleted('still active');
      expect((await turnFuture).outcome, IntegratedVoiceTurnOutcome.completed);

      harness.dispose();
    });

    test('remembered speech-event IDs are bounded to thirty-two', () async {
      final harness = _Harness();

      for (var index = 0; index < 40; index += 1) {
        final result = await harness.coordinator.handleSpeechActivity(
          _speech('inactive-$index'),
        );
        expect(result.outcome, IntegratedVoiceTurnSpeechOutcome.noActiveWork);
      }

      expect(
        harness.coordinator.rememberedSpeechEventCount,
        integratedVoiceTurnMaxRememberedSpeechEventIds,
      );
      expect(
        (await harness.coordinator.handleSpeechActivity(
          _speech('inactive-39'),
        )).outcome,
        IntegratedVoiceTurnSpeechOutcome.duplicate,
      );
      expect(
        (await harness.coordinator.handleSpeechActivity(
          _speech('inactive-0'),
        )).outcome,
        IntegratedVoiceTurnSpeechOutcome.noActiveWork,
      );

      harness.dispose();
    });

    test('dispose during interruption makes late completion inert', () async {
      final harness = _Harness();
      final localStop = Completer<void>();
      harness.localStopResults.add(localStop.future);

      final turnFuture = harness.coordinator.startNextTurn();
      final client = await harness.waitForClient(0);
      await _waitFor(
        () =>
            harness.coordinator.state.phase ==
            IntegratedVoiceTurnPhase.streaming,
      );

      final speechFuture = harness.coordinator.handleSpeechActivity(
        _speech('dispose-interruption'),
      );
      await _waitFor(
        () =>
            harness.coordinator.state.phase ==
            IntegratedVoiceTurnPhase.interrupting,
      );

      harness.coordinator.dispose();
      expect(
        (await speechFuture).outcome,
        IntegratedVoiceTurnSpeechOutcome.disposed,
      );

      localStop.complete();
      client.emitCompleted('late disposed result');
      expect(
        (await turnFuture).outcome,
        IntegratedVoiceTurnOutcome.invalidated,
      );
      expect(harness.synthesisCalls, 0);
      expect(
        harness.coordinator.state.phase,
        IntegratedVoiceTurnPhase.disposed,
      );

      harness.disposeDependencies();
    });

    test('dispose during capture makes late capture inert', () async {
      final harness = _Harness();
      final capture = Completer<MicrophoneCaptureResult>();
      harness.captureResults.add(capture.future);

      final turnFuture = harness.coordinator.startNextTurn();
      await _waitFor(
        () =>
            harness.coordinator.state.phase ==
            IntegratedVoiceTurnPhase.capturing,
      );

      harness.coordinator.dispose();
      capture.complete(_completedCapture());

      expect(
        (await turnFuture).outcome,
        IntegratedVoiceTurnOutcome.invalidated,
      );
      expect(harness.stagingCalls, 0);

      harness.disposeDependencies();
    });

    test('dispose during staging makes late staging inert', () async {
      final harness = _Harness();
      final staging = Completer<HostAudioHandoffResult>();
      harness.stagingResults.add(staging.future);

      final turnFuture = harness.coordinator.startNextTurn();
      await _waitFor(
        () =>
            harness.coordinator.state.phase == IntegratedVoiceTurnPhase.staging,
      );

      harness.coordinator.dispose();
      staging.complete(_completedStaging());

      expect(
        (await turnFuture).outcome,
        IntegratedVoiceTurnOutcome.invalidated,
      );
      expect(harness.clients, isEmpty);

      harness.disposeDependencies();
    });

    test(
      'dispose during transcript acquisition makes late STT inert',
      () async {
        final harness = _Harness();
        final transcript = Completer<ProviderNeutralTranscriptResult?>();
        harness.transcriptResults.add(transcript.future);

        final turnFuture = harness.coordinator.startNextTurn();
        final client = await harness.waitForClient(0);
        await _waitFor(
          () =>
              harness.coordinator.state.phase ==
              IntegratedVoiceTurnPhase.acquiringTranscript,
        );

        harness.coordinator.dispose();
        transcript.complete(_transcript('dispose-stt', 'late transcript'));

        expect(
          (await turnFuture).outcome,
          IntegratedVoiceTurnOutcome.invalidated,
        );
        expect(client.createCalls, 0);
        expect(harness.synthesisCalls, 0);

        harness.disposeDependencies();
      },
    );

    test('dispose during stream makes a late terminal inert', () async {
      final harness = _Harness();

      final turnFuture = harness.coordinator.startNextTurn();
      final client = await harness.waitForStreaming(0);

      harness.coordinator.dispose();
      client.emitCompleted('late stream after dispose');

      expect(
        (await turnFuture).outcome,
        IntegratedVoiceTurnOutcome.invalidated,
      );
      expect(harness.synthesisCalls, 0);

      harness.disposeDependencies();
    });

    test(
      'dispose during synthesis makes a late synthesis result inert',
      () async {
        final harness = _Harness();
        final synthesis = Completer<RealtimeTerminalVoiceSynthesisResult>();
        harness.synthesisResults.add(synthesis.future);

        final turnFuture = harness.coordinator.startNextTurn();
        final client = await harness.waitForStreaming(0);
        client.emitCompleted('dispose synthesis response');
        await _waitFor(
          () =>
              harness.voiceOutput.state.phase ==
              RealtimeTerminalVoiceOutputPhase.synthesizing,
        );

        harness.coordinator.dispose();
        synthesis.complete(
          const RealtimeTerminalVoiceSynthesisResult.audioReady(
            'https://audio.test/late-dispose.mp3',
          ),
        );

        expect(
          (await turnFuture).outcome,
          IntegratedVoiceTurnOutcome.invalidated,
        );
        expect(harness.playbackCalls, 0);

        harness.disposeDependencies();
      },
    );

    test(
      'dispose during playback makes a late playback result inert',
      () async {
        final harness = _Harness();
        final playback = Completer<RealtimeTerminalVoicePlaybackResult>();
        harness.playbackResults.add(playback.future);

        final turnFuture = harness.coordinator.startNextTurn();
        final client = await harness.waitForStreaming(0);
        client.emitCompleted('dispose playback response');
        await _waitFor(
          () =>
              harness.voiceOutput.state.phase ==
              RealtimeTerminalVoiceOutputPhase.playing,
        );

        harness.coordinator.dispose();
        playback.complete(
          const RealtimeTerminalVoicePlaybackResult.completed(),
        );

        expect(
          (await turnFuture).outcome,
          IntegratedVoiceTurnOutcome.invalidated,
        );

        harness.disposeDependencies();
      },
    );

    test('public coordinator messages are production-neutral', () async {
      final harness = _Harness();
      final capture = Completer<MicrophoneCaptureResult>();
      harness.captureResults.add(capture.future);

      final turnFuture = harness.coordinator.startNextTurn();
      await _waitFor(
        () =>
            harness.coordinator.state.phase ==
            IntegratedVoiceTurnPhase.capturing,
      );

      expect(
        harness.coordinator.state.safeMessage.toLowerCase(),
        isNot(contains('fake')),
      );
      final speechFuture = harness.coordinator.handleSpeechActivity(
        _speech('production-neutral-message'),
      );
      capture.complete(_completedCapture());

      await speechFuture;
      await turnFuture;
      expect(
        harness.coordinator.state.safeMessage.toLowerCase(),
        isNot(contains('fake')),
      );
      harness.dispose();
    });

    test(
      'public state retains no transcript IDs text URI or raw error',
      () async {
        final harness = _Harness(
          transcriptText: 'private transcript sentinel',
          audioUri: 'https://audio.test/private-sentinel.mp3',
        );

        final turnFuture = harness.coordinator.startNextTurn();
        final client = await harness.waitForStreaming(0);
        client.emitCompleted('private generated response sentinel');
        expect(
          (await turnFuture).outcome,
          IntegratedVoiceTurnOutcome.completed,
        );

        final stateText = <Object?>[
          harness.coordinator.state.phase,
          harness.coordinator.state.operationEpoch,
          harness.coordinator.state.turnGeneration,
          harness.coordinator.state.interruptionCount,
          harness.coordinator.state.pendingVoiceOutputCount,
          harness.coordinator.state.localStopRetryRequired,
          harness.coordinator.state.lastTurnOutcome,
          harness.coordinator.state.lastSpeechOutcome,
          harness.coordinator.state.safeMessage,
          harness.coordinator.state.technicalCode,
        ].join('|');

        for (final forbidden in <String>[
          'private transcript sentinel',
          'private generated response sentinel',
          'private-sentinel.mp3',
          'capture-secret',
          'staging-secret',
          'result-secret',
          'session-secret',
          'turn-secret',
          'raw exception',
        ]) {
          expect(stateText, isNot(contains(forbidden)));
        }

        harness.dispose();
      },
    );
  });
}

IntegratedVoiceTurnSpeechActivity _speech(String id) {
  return IntegratedVoiceTurnSpeechActivity(
    eventId: id,
    confirmed: true,
    foreground: true,
  );
}

ProviderNeutralTranscriptResult _transcript(String id, String text) {
  return ProviderNeutralTranscriptResult(
    resultId: id,
    text: text,
    isFinal: true,
  );
}

MicrophoneCaptureResult _completedCapture() {
  return MicrophoneCaptureResult(
    outcome: MicrophoneCaptureOutcome.completed,
    safeMessage: 'capture complete',
    technicalCode: 'capture_completed',
    engineResult: MicrophoneCaptureEngineResult(
      opaqueCaptureId: 'capture-secret',
      capturedDuration: const Duration(seconds: 1),
      publicMetadata: const <String, Object?>{
        'engine': 'fake',
        'microphone_accessed': false,
        'audio_captured': false,
        'raw_audio_exposed': false,
      },
    ),
  );
}

HostAudioHandoffResult _completedStaging() {
  return HostAudioHandoffResult(
    outcome: HostAudioHandoffOutcome.completed,
    technicalCode: 'fake_staging_completed',
    safeMessage: 'fake staging complete',
    consumerInvoked: true,
    privateArtifactDiscarded: true,
    cleanupSucceeded: true,
    publicMetadata: const <String, Object?>{
      'audio_uploaded': false,
      'backend_staging_created': false,
      'backend_staging_id_available': false,
    },
  );
}

RealtimeTextStreamControllerState _completedVoiceOutputState({
  required String sessionId,
  required String turnId,
  required String text,
}) {
  final count = text.runes.length;
  return RealtimeTextStreamControllerState(
    phase: RealtimeTextStreamControllerPhase.completed,
    outputText: text,
    lastSequence: 3,
    cancelMode: 'cooperative',
    hardCancelSupported: false,
    createResponse: _createResponse(sessionId: sessionId, turnId: turnId),
    terminal: RealtimeTextStreamTerminal(
      sequence: 3,
      outcome: RealtimeTextStreamTerminalOutcome.completed,
      finalText: text,
      outputCharCount: count,
      publicErrorCode: null,
      safeMessage: '',
      retryable: false,
    ),
  );
}

class _Harness {
  _Harness({
    this.transcriptText = 'user transcript',
    this.audioUri = 'https://audio.test/fake.mp3',
    this.mismatchProcessedItem = false,
  }) {
    queue = VoiceOutputQueueController(
      stopLocalPlayback: () {
        localStopCalls += 1;
        if (localStopResults.isNotEmpty) {
          return localStopResults.removeFirst();
        }
        return Future<void>.value();
      },
    );
    if (mismatchProcessedItem) {
      voiceOutput = _MismatchedVoiceOutputOrchestrator(queue: queue);
    } else {
      voiceOutput = RealtimeTerminalVoiceOutputOrchestrator(
        queue: queue,
        synthesize: (request) {
          synthesisCalls += 1;
          synthesizedUtterances.add(request.utterance);
          if (synthesisResults.isNotEmpty) {
            return synthesisResults.removeFirst();
          }
          return Future<RealtimeTerminalVoiceSynthesisResult>.value(
            RealtimeTerminalVoiceSynthesisResult.audioReady(audioUri),
          );
        },
        playToTerminal: (source) {
          playbackCalls += 1;
          playbackUris.add(source);
          if (playbackResults.isNotEmpty) {
            return playbackResults.removeFirst();
          }
          return Future<RealtimeTerminalVoicePlaybackResult>.value(
            const RealtimeTerminalVoicePlaybackResult.completed(),
          );
        },
      );
    }
    coordinator = IntegratedVoiceTurnCoordinator(
      captureCompleted: () {
        captureCalls += 1;
        if (captureResults.isNotEmpty) {
          return captureResults.removeFirst();
        }
        return Future<MicrophoneCaptureResult>.value(_completedCapture());
      },
      stageCapture: (capture) {
        stagingCalls += 1;
        if (stagingResults.isNotEmpty) {
          return stagingResults.removeFirst();
        }
        return Future<HostAudioHandoffResult>.value(_completedStaging());
      },
      streamControllerFactory: () {
        final cancelFuture = cancelResults.isNotEmpty
            ? cancelResults.removeFirst()
            : null;
        final client = _FakeRealtimeTextStreamClient(
          index: clients.length,
          cancelFuture: cancelFuture,
        );
        clients.add(client);
        return RealtimeTextStreamController(client: client);
      },
      transcriptHandoffFactory: (controller) {
        final transcriptFuture = transcriptResults.isNotEmpty
            ? transcriptResults.removeFirst()
            : Future<ProviderNeutralTranscriptResult?>.value(
                _transcript('result-${clients.length}', transcriptText),
              );
        return RealtimeTextStreamTranscriptHandoff(
          controller: controller,
          transcriptProvider: () => transcriptFuture,
        );
      },
      voiceOutput: voiceOutput,
    );
  }

  final String transcriptText;
  final String audioUri;
  final bool mismatchProcessedItem;

  final Queue<Future<MicrophoneCaptureResult>> captureResults =
      Queue<Future<MicrophoneCaptureResult>>();
  final Queue<Future<HostAudioHandoffResult>> stagingResults =
      Queue<Future<HostAudioHandoffResult>>();
  final Queue<Future<ProviderNeutralTranscriptResult?>> transcriptResults =
      Queue<Future<ProviderNeutralTranscriptResult?>>();
  final Queue<Future<RealtimeTextStreamCancelResponse>> cancelResults =
      Queue<Future<RealtimeTextStreamCancelResponse>>();
  final Queue<Future<RealtimeTerminalVoiceSynthesisResult>> synthesisResults =
      Queue<Future<RealtimeTerminalVoiceSynthesisResult>>();
  final Queue<Future<RealtimeTerminalVoicePlaybackResult>> playbackResults =
      Queue<Future<RealtimeTerminalVoicePlaybackResult>>();
  final Queue<Future<void>> localStopResults = Queue<Future<void>>();

  late final VoiceOutputQueueController queue;
  late final RealtimeTerminalVoiceOutputOrchestrator voiceOutput;
  late final IntegratedVoiceTurnCoordinator coordinator;

  final List<_FakeRealtimeTextStreamClient> clients =
      <_FakeRealtimeTextStreamClient>[];
  final List<String> synthesizedUtterances = <String>[];
  final List<Uri> playbackUris = <Uri>[];

  int captureCalls = 0;
  int stagingCalls = 0;
  int synthesisCalls = 0;
  int playbackCalls = 0;
  int localStopCalls = 0;

  Future<_FakeRealtimeTextStreamClient> waitForClient(int index) async {
    await _waitFor(() => clients.length > index);
    return clients[index];
  }

  Future<_FakeRealtimeTextStreamClient> waitForStreaming(int index) async {
    final client = await waitForClient(index);
    await _waitFor(
      () =>
          client.createCalls > 0 &&
          coordinator.state.phase == IntegratedVoiceTurnPhase.streaming,
    );
    return client;
  }

  void dispose() {
    coordinator.dispose();
    disposeDependencies();
  }

  void disposeDependencies() {
    voiceOutput.dispose();
    queue.dispose();
    for (final client in clients) {
      client.disposeFake();
    }
  }
}

class _MismatchedVoiceOutputOrchestrator
    extends RealtimeTerminalVoiceOutputOrchestrator {
  _MismatchedVoiceOutputOrchestrator({required super.queue})
    : super(
        synthesize: (_) async =>
            const RealtimeTerminalVoiceSynthesisResult.rejected(),
        playToTerminal: (_) async =>
            const RealtimeTerminalVoicePlaybackResult.failed(),
      );

  static const VoiceOutputQueueItemMetadata _enqueuedItem =
      VoiceOutputQueueItemMetadata(
        itemId: 'tts-current-terminal',
        generation: 1,
        characterCount: 24,
      );

  @override
  RealtimeTerminalVoiceOutputEnqueueResult enqueueCompletedTerminal(
    RealtimeTextStreamControllerState terminalState,
  ) {
    return const RealtimeTerminalVoiceOutputEnqueueResult(
      accepted: true,
      item: _enqueuedItem,
    );
  }

  @override
  Future<RealtimeTerminalVoiceOutputProcessResult> processNext() {
    return Future<RealtimeTerminalVoiceOutputProcessResult>.value(
      const RealtimeTerminalVoiceOutputProcessResult(
        outcome: RealtimeTerminalVoiceOutputProcessOutcome.completed,
        item: VoiceOutputQueueItemMetadata(
          itemId: 'tts-different-terminal',
          generation: 1,
          characterCount: 24,
        ),
      ),
    );
  }
}

class _FakeRealtimeTextStreamClient extends RealtimeTextStreamClient {
  _FakeRealtimeTextStreamClient({required this.index, this.cancelFuture})
    : super(baseUrl: 'https://stream.test', client: http.Client());

  final int index;
  final Future<RealtimeTextStreamCancelResponse>? cancelFuture;
  final StreamController<RealtimeTextStreamEvent> _events =
      StreamController<RealtimeTextStreamEvent>.broadcast(sync: true);

  int createCalls = 0;
  int cancelCalls = 0;
  int closeCalls = 0;
  bool _closed = false;

  String get sessionId => 'session-$index';
  String get turnId => 'turn-$index';

  @override
  Future<RealtimeTextStreamCreateResponse> createSession({
    required String inputText,
  }) async {
    createCalls += 1;
    return _createResponse(sessionId: sessionId, turnId: turnId);
  }

  @override
  Stream<RealtimeTextStreamEvent> streamEvents(
    RealtimeTextStreamCreateResponse createResponse,
  ) {
    return _events.stream;
  }

  @override
  Future<RealtimeTextStreamCancelResponse> cancel(
    RealtimeTextStreamCreateResponse createResponse,
  ) {
    cancelCalls += 1;
    return cancelFuture ??
        Future<RealtimeTextStreamCancelResponse>.value(
          RealtimeTextStreamCancelResponse(
            accepted: true,
            sessionId: sessionId,
            turnId: turnId,
            state: RealtimeTextStreamState.cancelRequested,
            cancelMode: 'cooperative',
            hardCancelSupported: false,
            terminal: false,
            safeMessage: 'cancel requested',
          ),
        );
  }

  void emitCompleted(String text) {
    final count = text.runes.length;
    _events.add(
      RealtimeTextStreamEvent(
        eventType: RealtimeTextStreamEventType.streamStarted,
        sessionId: sessionId,
        turnId: turnId,
        sequence: 1,
        state: RealtimeTextStreamState.streaming,
        chunk: null,
        terminal: null,
        safeMessage: '',
      ),
    );
    _events.add(
      RealtimeTextStreamEvent(
        eventType: RealtimeTextStreamEventType.streamChunk,
        sessionId: sessionId,
        turnId: turnId,
        sequence: 2,
        state: RealtimeTextStreamState.streaming,
        chunk: RealtimeTextStreamChunk(
          sequence: 2,
          text: text,
          outputCharCount: count,
        ),
        terminal: null,
        safeMessage: '',
      ),
    );
    _events.add(
      RealtimeTextStreamEvent(
        eventType: RealtimeTextStreamEventType.streamCompleted,
        sessionId: sessionId,
        turnId: turnId,
        sequence: 3,
        state: RealtimeTextStreamState.completed,
        chunk: null,
        terminal: RealtimeTextStreamTerminal(
          sequence: 3,
          outcome: RealtimeTextStreamTerminalOutcome.completed,
          finalText: text,
          outputCharCount: count,
          publicErrorCode: null,
          safeMessage: '',
          retryable: false,
        ),
        safeMessage: '',
      ),
    );
  }

  void emitCancelled() {
    _events.add(
      RealtimeTextStreamEvent(
        eventType: RealtimeTextStreamEventType.streamStarted,
        sessionId: sessionId,
        turnId: turnId,
        sequence: 1,
        state: RealtimeTextStreamState.streaming,
        chunk: null,
        terminal: null,
        safeMessage: '',
      ),
    );
    _events.add(
      RealtimeTextStreamEvent(
        eventType: RealtimeTextStreamEventType.streamCancelled,
        sessionId: sessionId,
        turnId: turnId,
        sequence: 2,
        state: RealtimeTextStreamState.cancelled,
        chunk: null,
        terminal: const RealtimeTextStreamTerminal(
          sequence: 2,
          outcome: RealtimeTextStreamTerminalOutcome.cancelled,
          finalText: '',
          outputCharCount: 0,
          publicErrorCode: null,
          safeMessage: 'cancelled',
          retryable: false,
        ),
        safeMessage: 'cancelled',
      ),
    );
  }

  @override
  void close() {
    closeCalls += 1;
    if (!_closed) {
      _closed = true;
      super.close();
    }
  }

  void disposeFake() {
    if (!_events.isClosed) {
      unawaited(_events.close());
    }
    close();
  }
}

RealtimeTextStreamCreateResponse _createResponse({
  required String sessionId,
  required String turnId,
}) {
  return RealtimeTextStreamCreateResponse(
    accepted: true,
    session: RealtimeTextStreamSession(
      sessionId: sessionId,
      state: RealtimeTextStreamState.streaming,
      activeTurnId: turnId,
      lastSequence: 0,
      isClosed: false,
      cancelMode: 'cooperative',
      hardCancelSupported: false,
    ),
    turn: RealtimeTextStreamTurn(
      sessionId: sessionId,
      turnId: turnId,
      state: RealtimeTextStreamState.streaming,
      chunkCount: 0,
      outputCharCount: 0,
      cancelRequested: false,
      terminalOutcome: null,
    ),
    eventsPath: '/realtime/text/sessions/$sessionId/events',
    cancelPath: '/realtime/text/sessions/$sessionId/cancel',
    idleTtlSeconds: 30,
    maxDurationSeconds: 60,
    maxPendingEvents: 32,
    maxEventBytes: 32768,
  );
}

Future<void> _waitFor(bool Function() condition) async {
  for (var attempt = 0; attempt < 200; attempt += 1) {
    if (condition()) {
      return;
    }
    await Future<void>.delayed(Duration.zero);
  }
  fail('condition did not become true');
}
