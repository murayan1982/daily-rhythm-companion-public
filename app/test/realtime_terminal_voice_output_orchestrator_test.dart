import 'dart:async';

import 'package:app/models/realtime_text_stream.dart';
import 'package:app/services/realtime_terminal_voice_output_orchestrator.dart';
import 'package:app/services/realtime_text_stream_controller.dart';
import 'package:app/services/voice_output_queue.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('RealtimeTerminalVoiceOutputOrchestrator', () {
    test('starts idle without retaining terminal text in public state', () {
      final harness = _Harness();

      expect(
        harness.orchestrator.state.phase,
        RealtimeTerminalVoiceOutputPhase.idle,
      );
      expect(harness.orchestrator.state.pendingCount, 0);
      expect(harness.orchestrator.state.activeItem, isNull);
      expect(
        harness.orchestrator.state.toString(),
        isNot(contains('private terminal output')),
      );

      harness.dispose();
    });

    test('requires explicit enqueue and one explicit process call', () async {
      final harness = _Harness();
      final terminal = _completedState(
        text: 'first output',
        sessionId: 'session-a',
        turnId: 'turn-a',
      );

      final enqueue = harness.orchestrator.enqueueCompletedTerminal(terminal);

      expect(enqueue.accepted, isTrue);
      expect(harness.synthesis.calls, isEmpty);
      expect(harness.playback.calls, isEmpty);
      expect(harness.orchestrator.state.pendingCount, 1);

      final process = await harness.orchestrator.processNext();

      expect(
        process.outcome,
        RealtimeTerminalVoiceOutputProcessOutcome.completed,
      );
      expect(harness.synthesis.calls, hasLength(1));
      expect(harness.synthesis.calls.single.utterance, 'first output');
      expect(harness.playback.calls, hasLength(1));
      expect(harness.queue.state.pendingCount, 0);
      expect(harness.queue.state.activeItem, isNull);

      harness.dispose();
    });

    test('rejects non-completed and inconsistent terminal snapshots', () {
      final invalidStates = <RealtimeTextStreamControllerState>[
        _completedState(
          text: 'output',
          sessionId: 'session-a',
          turnId: 'turn-a',
          phase: RealtimeTextStreamControllerPhase.streaming,
        ),
        _completedState(
          text: 'output',
          sessionId: 'session-b',
          turnId: 'turn-b',
          outcome: RealtimeTextStreamTerminalOutcome.cancelled,
        ),
        _completedState(
          text: 'output',
          sessionId: 'session-c',
          turnId: 'turn-c',
          problem: const RealtimeTextStreamProblem(
            code: 'safe_problem',
            message: 'safe failure',
            retryable: false,
          ),
        ),
        _completedState(
          text: 'output',
          sessionId: 'session-d',
          turnId: 'turn-d',
          terminalSequence: 2,
          lastSequence: 1,
        ),
        _completedState(
          text: 'output',
          terminalText: 'different',
          sessionId: 'session-e',
          turnId: 'turn-e',
        ),
        _completedState(
          text: 'output',
          terminalCount: 2,
          sessionId: 'session-f',
          turnId: 'turn-f',
        ),
        _completedState(text: '   ', sessionId: 'session-g', turnId: 'turn-g'),
        _completedState(text: 'output', sessionId: '', turnId: 'turn-h'),
        _completedState(
          text: 'output',
          sessionId: ' session-i',
          turnId: 'turn-i',
        ),
        _completedState(
          text: 'output',
          sessionId: 'session-j',
          turnId: 'turn-j',
          terminalSequence: 0,
        ),
      ];

      for (final state in invalidStates) {
        final harness = _Harness();
        final result = harness.orchestrator.enqueueCompletedTerminal(state);

        expect(result.accepted, isFalse);
        expect(
          result.rejection,
          RealtimeTerminalVoiceOutputEnqueueRejection.invalidCompletedTerminal,
        );
        expect(harness.queue.state.pendingCount, 0);

        harness.dispose();
      }
    });

    test('deduplicates only after queue enqueue succeeds', () async {
      final harness = _Harness(maxPendingItems: 1);
      final first = _completedState(
        text: 'first',
        sessionId: 'session-a',
        turnId: 'turn-a',
      );
      final second = _completedState(
        text: 'second',
        sessionId: 'session-b',
        turnId: 'turn-b',
      );

      expect(
        harness.orchestrator.enqueueCompletedTerminal(first).accepted,
        isTrue,
      );
      final duplicate = harness.orchestrator.enqueueCompletedTerminal(first);
      expect(duplicate.accepted, isFalse);
      expect(
        duplicate.rejection,
        RealtimeTerminalVoiceOutputEnqueueRejection.duplicateCompletedTerminal,
      );

      final full = harness.orchestrator.enqueueCompletedTerminal(second);
      expect(full.accepted, isFalse);
      expect(
        full.rejection,
        RealtimeTerminalVoiceOutputEnqueueRejection.queueRejected,
      );
      expect(
        full.queueRejection,
        VoiceOutputQueueRejection.pendingLimitReached,
      );

      expect(
        (await harness.orchestrator.processNext()).outcome,
        RealtimeTerminalVoiceOutputProcessOutcome.completed,
      );
      expect(
        harness.orchestrator.enqueueCompletedTerminal(second).accepted,
        isTrue,
      );

      harness.dispose();
    });

    test(
      'keeps bounded completed-terminal deduplication across flush',
      () async {
        final harness = _Harness(maxRememberedTerminals: 2);
        final first = _completedState(
          text: 'first',
          sessionId: 'session-a',
          turnId: 'turn-a',
        );
        final second = _completedState(
          text: 'second',
          sessionId: 'session-b',
          turnId: 'turn-b',
        );
        final third = _completedState(
          text: 'third',
          sessionId: 'session-c',
          turnId: 'turn-c',
        );

        expect(
          harness.orchestrator.enqueueCompletedTerminal(first).accepted,
          isTrue,
        );
        await harness.orchestrator.flush();
        expect(
          harness.orchestrator.enqueueCompletedTerminal(first).accepted,
          isFalse,
        );

        expect(
          harness.orchestrator.enqueueCompletedTerminal(second).accepted,
          isTrue,
        );
        await harness.orchestrator.flush();
        expect(
          harness.orchestrator.enqueueCompletedTerminal(third).accepted,
          isTrue,
        );
        await harness.orchestrator.flush();

        expect(
          harness.orchestrator.enqueueCompletedTerminal(first).accepted,
          isTrue,
        );

        harness.dispose();
      },
    );

    test('processes FIFO items one per explicit process call', () async {
      final harness = _Harness();
      harness.orchestrator.enqueueCompletedTerminal(
        _completedState(
          text: 'first',
          sessionId: 'session-a',
          turnId: 'turn-a',
        ),
      );
      harness.orchestrator.enqueueCompletedTerminal(
        _completedState(
          text: 'second',
          sessionId: 'session-b',
          turnId: 'turn-b',
        ),
      );

      await harness.orchestrator.processNext();

      expect(
        harness.synthesis.calls.map((request) => request.utterance),
        <String>['first'],
      );
      expect(harness.queue.state.pendingCount, 1);

      await harness.orchestrator.processNext();

      expect(
        harness.synthesis.calls.map((request) => request.utterance),
        <String>['first', 'second'],
      );
      expect(harness.queue.state.pendingCount, 0);

      harness.dispose();
    });

    test(
      'rejects concurrent processing without replacing active work',
      () async {
        final synthesisCompleter =
            Completer<RealtimeTerminalVoiceSynthesisResult>();
        final harness = _Harness(
          synthesisResponses: <Future<RealtimeTerminalVoiceSynthesisResult>>[
            synthesisCompleter.future,
          ],
        );
        harness.orchestrator.enqueueCompletedTerminal(
          _completedState(
            text: 'output',
            sessionId: 'session-a',
            turnId: 'turn-a',
          ),
        );

        final active = harness.orchestrator.processNext();
        await _drainMicrotasks();
        final rejected = await harness.orchestrator.processNext();

        expect(
          rejected.outcome,
          RealtimeTerminalVoiceOutputProcessOutcome.processInProgress,
        );
        expect(harness.synthesis.calls, hasLength(1));

        synthesisCompleter.complete(
          const RealtimeTerminalVoiceSynthesisResult.audioReady(
            'https://audio.example.test/first.mp3',
          ),
        );
        expect(
          (await active).outcome,
          RealtimeTerminalVoiceOutputProcessOutcome.completed,
        );

        harness.dispose();
      },
    );

    test(
      'maps synthesis rejection failure and exception to bounded codes',
      () async {
        final cases = <_SynthesisCase>[
          _SynthesisCase(
            createFuture: () =>
                Future<RealtimeTerminalVoiceSynthesisResult>.value(
                  const RealtimeTerminalVoiceSynthesisResult.rejected(),
                ),
            outcome:
                RealtimeTerminalVoiceOutputProcessOutcome.synthesisRejected,
            technicalCode: 'synthesis_rejected',
          ),
          _SynthesisCase(
            createFuture: () =>
                Future<RealtimeTerminalVoiceSynthesisResult>.value(
                  const RealtimeTerminalVoiceSynthesisResult.failed(),
                ),
            outcome: RealtimeTerminalVoiceOutputProcessOutcome.synthesisFailed,
            technicalCode: 'synthesis_request_failed',
          ),
          _SynthesisCase(
            createFuture: () =>
                Future<RealtimeTerminalVoiceSynthesisResult>.error(
                  StateError('private synthesis exception'),
                ),
            outcome: RealtimeTerminalVoiceOutputProcessOutcome.synthesisFailed,
            technicalCode: 'synthesis_request_failed',
          ),
        ];

        for (var index = 0; index < cases.length; index += 1) {
          final testCase = cases[index];
          final harness = _Harness(
            synthesisResponses: <Future<RealtimeTerminalVoiceSynthesisResult>>[
              testCase.createFuture(),
            ],
          );
          harness.orchestrator.enqueueCompletedTerminal(
            _completedState(
              text: 'output',
              sessionId: 'session-$index',
              turnId: 'turn-$index',
            ),
          );

          final result = await harness.orchestrator.processNext();

          expect(result.outcome, testCase.outcome);
          expect(result.technicalCode, testCase.technicalCode);
          expect(
            result.toString(),
            isNot(contains('private synthesis exception')),
          );
          expect(
            harness.queue.state.lastOutcome,
            VoiceOutputQueueItemOutcome.failed,
          );
          expect(harness.playback.calls, isEmpty);

          harness.dispose();
        }
      },
    );

    test('accepts only bounded absolute opaque HTTP audio URIs', () async {
      final valid = <String>[
        'https://audio.example.test/file.mp3',
        'http://audio.example.test/file.mp3?opaque=fake',
      ];
      for (var index = 0; index < valid.length; index += 1) {
        final harness = _Harness(
          synthesisResponses: <Future<RealtimeTerminalVoiceSynthesisResult>>[
            Future<RealtimeTerminalVoiceSynthesisResult>.value(
              RealtimeTerminalVoiceSynthesisResult.audioReady(valid[index]),
            ),
          ],
        );
        harness.orchestrator.enqueueCompletedTerminal(
          _completedState(
            text: 'output',
            sessionId: 'valid-session-$index',
            turnId: 'valid-turn-$index',
          ),
        );

        expect(
          (await harness.orchestrator.processNext()).outcome,
          RealtimeTerminalVoiceOutputProcessOutcome.completed,
        );
        expect(harness.playback.calls.single.toString(), valid[index]);
        harness.dispose();
      }

      final invalid = <String>[
        '',
        ' https://audio.example.test/file.mp3',
        'https://audio.example.test/file.mp3 ',
        '/relative/file.mp3',
        'file:///private/file.mp3',
        'ftp://audio.example.test/file.mp3',
        'https://user:pass@audio.example.test/file.mp3',
        'https://audio.example.test/file.mp3#fragment',
        r'https:\\audio.example.test\\file.mp3',
        'https://audio.example.test/file name.mp3',
        'https://audio.example.test/file.mp3\n',
        List<String>.filled(
          realtimeTerminalVoiceOutputMaxAudioUriCodePoints + 1,
          'a',
        ).join(),
      ];
      for (var index = 0; index < invalid.length; index += 1) {
        final harness = _Harness(
          synthesisResponses: <Future<RealtimeTerminalVoiceSynthesisResult>>[
            Future<RealtimeTerminalVoiceSynthesisResult>.value(
              RealtimeTerminalVoiceSynthesisResult.audioReady(invalid[index]),
            ),
          ],
        );
        harness.orchestrator.enqueueCompletedTerminal(
          _completedState(
            text: 'output',
            sessionId: 'invalid-session-$index',
            turnId: 'invalid-turn-$index',
          ),
        );

        final result = await harness.orchestrator.processNext();

        expect(
          result.outcome,
          RealtimeTerminalVoiceOutputProcessOutcome.invalidAudioUri,
        );
        expect(result.technicalCode, 'invalid_audio_uri');
        expect(harness.playback.calls, isEmpty);
        harness.dispose();
      }
    });

    test('completes the queue only for completed playback terminal', () async {
      final cases = <_PlaybackCase>[
        const _PlaybackCase(
          result: RealtimeTerminalVoicePlaybackResult.completed(),
          outcome: RealtimeTerminalVoiceOutputProcessOutcome.completed,
          queueOutcome: VoiceOutputQueueItemOutcome.completed,
        ),
        const _PlaybackCase(
          result: RealtimeTerminalVoicePlaybackResult.failed(),
          outcome: RealtimeTerminalVoiceOutputProcessOutcome.playbackFailed,
          queueOutcome: VoiceOutputQueueItemOutcome.failed,
          technicalCode: 'playback_failed',
        ),
        const _PlaybackCase(
          result: RealtimeTerminalVoicePlaybackResult.expired(),
          outcome: RealtimeTerminalVoiceOutputProcessOutcome.playbackExpired,
          queueOutcome: VoiceOutputQueueItemOutcome.failed,
          technicalCode: 'playback_expired',
        ),
        const _PlaybackCase(
          result: RealtimeTerminalVoicePlaybackResult.stopped(),
          outcome: RealtimeTerminalVoiceOutputProcessOutcome.playbackStopped,
          queueOutcome: VoiceOutputQueueItemOutcome.failed,
          technicalCode: 'playback_stopped',
        ),
      ];

      for (var index = 0; index < cases.length; index += 1) {
        final testCase = cases[index];
        final harness = _Harness(
          playbackResponses: <Future<RealtimeTerminalVoicePlaybackResult>>[
            Future<RealtimeTerminalVoicePlaybackResult>.value(testCase.result),
          ],
        );
        harness.orchestrator.enqueueCompletedTerminal(
          _completedState(
            text: 'output',
            sessionId: 'session-$index',
            turnId: 'turn-$index',
          ),
        );

        final result = await harness.orchestrator.processNext();

        expect(result.outcome, testCase.outcome);
        expect(result.technicalCode, testCase.technicalCode);
        expect(harness.queue.state.lastOutcome, testCase.queueOutcome);
        expect(harness.queue.state.activeItem, isNull);

        harness.dispose();
      }
    });

    test('maps playback lifecycle exception without exposing it', () async {
      final playbackCompleter =
          Completer<RealtimeTerminalVoicePlaybackResult>();
      final harness = _Harness(
        playbackResponses: <Future<RealtimeTerminalVoicePlaybackResult>>[
          playbackCompleter.future,
        ],
      );
      harness.orchestrator.enqueueCompletedTerminal(
        _completedState(
          text: 'output',
          sessionId: 'session-a',
          turnId: 'turn-a',
        ),
      );

      final process = harness.orchestrator.processNext();
      await _drainMicrotasks();
      playbackCompleter.completeError(StateError('private playback exception'));
      final result = await process;

      expect(
        result.outcome,
        RealtimeTerminalVoiceOutputProcessOutcome.playbackLifecycleFailed,
      );
      expect(result.technicalCode, 'playback_lifecycle_failed');
      expect(result.toString(), isNot(contains('private playback exception')));
      expect(
        harness.queue.state.lastOutcome,
        VoiceOutputQueueItemOutcome.failed,
      );

      harness.dispose();
    });

    test(
      'flush from synthesizing notification prevents synthesis start',
      () async {
        final harness = _Harness();
        Future<VoiceOutputQueueFlushResult>? reentrantFlush;

        void listener() {
          if (harness.orchestrator.state.phase ==
                  RealtimeTerminalVoiceOutputPhase.synthesizing &&
              reentrantFlush == null) {
            reentrantFlush = harness.orchestrator.flush();
          }
        }

        harness.orchestrator.addListener(listener);
        harness.orchestrator.enqueueCompletedTerminal(
          _completedState(
            text: 'output',
            sessionId: 'session-a',
            turnId: 'turn-a',
          ),
        );

        final process = harness.orchestrator.processNext();
        final flush = reentrantFlush;

        expect(flush, isNotNull);
        await flush!;
        expect(
          (await process).outcome,
          RealtimeTerminalVoiceOutputProcessOutcome.invalidated,
        );
        expect(harness.synthesis.calls, isEmpty);
        expect(harness.playback.calls, isEmpty);

        harness.orchestrator.removeListener(listener);
        harness.dispose();
      },
    );

    test('flush during synthesis prevents late playback start', () async {
      final synthesisCompleter =
          Completer<RealtimeTerminalVoiceSynthesisResult>();
      final harness = _Harness(
        synthesisResponses: <Future<RealtimeTerminalVoiceSynthesisResult>>[
          synthesisCompleter.future,
        ],
      );
      harness.orchestrator.enqueueCompletedTerminal(
        _completedState(
          text: 'output',
          sessionId: 'session-a',
          turnId: 'turn-a',
        ),
      );

      final process = harness.orchestrator.processNext();
      await _drainMicrotasks();
      final flush = await harness.orchestrator.flush();
      synthesisCompleter.complete(
        const RealtimeTerminalVoiceSynthesisResult.audioReady(
          'https://audio.example.test/late.mp3',
        ),
      );

      expect(flush.invalidatedActiveItem, isTrue);
      expect(
        (await process).outcome,
        RealtimeTerminalVoiceOutputProcessOutcome.invalidated,
      );
      expect(harness.playback.calls, isEmpty);
      expect(harness.queue.state.pendingCount, 0);
      expect(harness.queue.state.activeItem, isNull);

      harness.dispose();
    });

    test(
      'flush during playback requests one stop and ignores late terminal',
      () async {
        final playbackCompleter =
            Completer<RealtimeTerminalVoicePlaybackResult>();
        final harness = _Harness(
          playbackResponses: <Future<RealtimeTerminalVoicePlaybackResult>>[
            playbackCompleter.future,
          ],
        );
        harness.orchestrator.enqueueCompletedTerminal(
          _completedState(
            text: 'output',
            sessionId: 'session-a',
            turnId: 'turn-a',
          ),
        );

        final process = harness.orchestrator.processNext();
        await _drainMicrotasks();
        expect(harness.playback.calls, hasLength(1));

        final flush = await harness.orchestrator.flush();
        playbackCompleter.complete(
          const RealtimeTerminalVoicePlaybackResult.completed(),
        );

        expect(flush.invalidatedActiveItem, isTrue);
        expect(harness.stop.calls, 1);
        expect(
          (await process).outcome,
          RealtimeTerminalVoiceOutputProcessOutcome.invalidated,
        );
        expect(harness.queue.state.lastOutcome, isNull);

        harness.dispose();
      },
    );

    test(
      'flushing notification exposes an already-invalidated queue',
      () async {
        final stopCompleter = Completer<void>();
        final harness = _Harness(stopCompleter: stopCompleter);
        RealtimeTerminalVoiceOutputEnqueueResult? enqueueDuringFlush;
        Future<RealtimeTerminalVoiceOutputProcessResult>? processDuringFlush;
        int? observedPendingCount;
        var handled = false;

        harness.orchestrator.enqueueCompletedTerminal(
          _completedState(
            text: 'queued',
            sessionId: 'session-a',
            turnId: 'turn-a',
          ),
        );

        void listener() {
          if (handled ||
              harness.orchestrator.state.phase !=
                  RealtimeTerminalVoiceOutputPhase.flushing) {
            return;
          }
          handled = true;
          observedPendingCount = harness.orchestrator.state.pendingCount;
          enqueueDuringFlush = harness.orchestrator.enqueueCompletedTerminal(
            _completedState(
              text: 'late',
              sessionId: 'session-b',
              turnId: 'turn-b',
            ),
          );
          processDuringFlush = harness.orchestrator.processNext();
        }

        harness.orchestrator.addListener(listener);
        final flush = harness.orchestrator.flush();

        expect(observedPendingCount, 0);
        expect(enqueueDuringFlush?.accepted, isFalse);
        expect(
          enqueueDuringFlush?.queueRejection,
          VoiceOutputQueueRejection.flushInProgress,
        );
        expect(
          (await processDuringFlush!).queueRejection,
          VoiceOutputQueueRejection.flushInProgress,
        );
        expect(harness.synthesis.calls, isEmpty);

        stopCompleter.complete();
        await flush;
        harness.orchestrator.removeListener(listener);
        harness.dispose();
      },
    );

    test(
      'publishes the in-flight flush before flushing notification',
      () async {
        final stopCompleter = Completer<void>();
        final harness = _Harness(stopCompleter: stopCompleter);
        Future<VoiceOutputQueueFlushResult>? reentrantFlush;

        void listener() {
          if (harness.orchestrator.state.phase ==
                  RealtimeTerminalVoiceOutputPhase.flushing &&
              reentrantFlush == null) {
            reentrantFlush = harness.orchestrator.flush();
          }
        }

        harness.orchestrator.addListener(listener);
        final first = harness.orchestrator.flush();

        expect(reentrantFlush, isNotNull);
        expect(identical(first, reentrantFlush), isTrue);
        expect(harness.stop.calls, 1);

        stopCompleter.complete();
        await first;
        harness.orchestrator.removeListener(listener);
        harness.dispose();
      },
    );

    test('concurrent flush callers share one local stop request', () async {
      final stopCompleter = Completer<void>();
      final harness = _Harness(stopCompleter: stopCompleter);
      harness.orchestrator.enqueueCompletedTerminal(
        _completedState(
          text: 'output',
          sessionId: 'session-a',
          turnId: 'turn-a',
        ),
      );

      final first = harness.orchestrator.flush();
      final second = harness.orchestrator.flush();

      expect(identical(first, second), isTrue);
      expect(harness.stop.calls, 1);
      stopCompleter.complete();
      await Future.wait(<Future<VoiceOutputQueueFlushResult>>[first, second]);
      expect(harness.stop.calls, 1);

      harness.dispose();
    });

    test('flush releases the process slot for a new generation', () async {
      final firstSynthesis = Completer<RealtimeTerminalVoiceSynthesisResult>();
      final harness = _Harness(
        synthesisResponses: <Future<RealtimeTerminalVoiceSynthesisResult>>[
          firstSynthesis.future,
          Future<RealtimeTerminalVoiceSynthesisResult>.value(
            const RealtimeTerminalVoiceSynthesisResult.audioReady(
              'https://audio.example.test/new.mp3',
            ),
          ),
        ],
      );
      harness.orchestrator.enqueueCompletedTerminal(
        _completedState(
          text: 'old',
          sessionId: 'session-old',
          turnId: 'turn-old',
        ),
      );

      final oldProcess = harness.orchestrator.processNext();
      await _drainMicrotasks();
      await harness.orchestrator.flush();

      harness.orchestrator.enqueueCompletedTerminal(
        _completedState(
          text: 'new',
          sessionId: 'session-new',
          turnId: 'turn-new',
        ),
      );
      final newResult = await harness.orchestrator.processNext();

      expect(
        newResult.outcome,
        RealtimeTerminalVoiceOutputProcessOutcome.completed,
      );
      expect(harness.synthesis.calls, hasLength(2));

      firstSynthesis.complete(
        const RealtimeTerminalVoiceSynthesisResult.audioReady(
          'https://audio.example.test/old.mp3',
        ),
      );
      expect(
        (await oldProcess).outcome,
        RealtimeTerminalVoiceOutputProcessOutcome.invalidated,
      );
      expect(harness.playback.calls, hasLength(1));
      expect(harness.playback.calls.single.path, '/new.mp3');

      harness.dispose();
    });

    test('flush stop failure never restores pending or active items', () async {
      final playbackCompleter =
          Completer<RealtimeTerminalVoicePlaybackResult>();
      final harness = _Harness(
        stopError: StateError('private stop failure'),
        playbackResponses: <Future<RealtimeTerminalVoicePlaybackResult>>[
          playbackCompleter.future,
        ],
      );
      harness.orchestrator.enqueueCompletedTerminal(
        _completedState(
          text: 'first',
          sessionId: 'session-a',
          turnId: 'turn-a',
        ),
      );
      harness.orchestrator.enqueueCompletedTerminal(
        _completedState(
          text: 'second',
          sessionId: 'session-b',
          turnId: 'turn-b',
        ),
      );
      final process = harness.orchestrator.processNext();
      await _drainMicrotasks();

      final result = await harness.orchestrator.flush();

      expect(
        result.outcome,
        VoiceOutputQueueFlushOutcome.completedWithLocalPlaybackStopFailure,
      );
      expect(result.technicalCode, 'local_playback_stop_failed');
      expect(harness.queue.state.pendingCount, 0);
      expect(harness.queue.state.activeItem, isNull);

      playbackCompleter.complete(
        const RealtimeTerminalVoicePlaybackResult.completed(),
      );
      expect(
        (await process).outcome,
        RealtimeTerminalVoiceOutputProcessOutcome.invalidated,
      );
      harness.dispose();
    });

    test(
      'dispose invalidates late work and rejects later operations',
      () async {
        final synthesisCompleter =
            Completer<RealtimeTerminalVoiceSynthesisResult>();
        final harness = _Harness(
          synthesisResponses: <Future<RealtimeTerminalVoiceSynthesisResult>>[
            synthesisCompleter.future,
          ],
        );
        final terminal = _completedState(
          text: 'output',
          sessionId: 'session-a',
          turnId: 'turn-a',
        );
        harness.orchestrator.enqueueCompletedTerminal(terminal);
        final process = harness.orchestrator.processNext();
        await _drainMicrotasks();

        harness.orchestrator.dispose();
        synthesisCompleter.complete(
          const RealtimeTerminalVoiceSynthesisResult.audioReady(
            'https://audio.example.test/late.mp3',
          ),
        );

        expect(
          (await process).outcome,
          RealtimeTerminalVoiceOutputProcessOutcome.invalidated,
        );
        expect(harness.playback.calls, isEmpty);
        expect(
          harness.orchestrator.state.phase,
          RealtimeTerminalVoiceOutputPhase.disposed,
        );
        expect(
          harness.orchestrator.enqueueCompletedTerminal(terminal).rejection,
          RealtimeTerminalVoiceOutputEnqueueRejection.disposed,
        );
        expect(
          (await harness.orchestrator.processNext()).outcome,
          RealtimeTerminalVoiceOutputProcessOutcome.disposed,
        );

        harness.queue.dispose();
      },
    );

    test(
      'public state and results do not expose text IDs URI or raw errors',
      () async {
        const privateOutput = 'private terminal output';
        const privateSession = 'private-session-id';
        const privateTurn = 'private-turn-id';
        const opaqueUri =
            'https://audio.example.test/private-file.mp3?opaque=fake-value';
        final harness = _Harness(
          synthesisResponses: <Future<RealtimeTerminalVoiceSynthesisResult>>[
            Future<RealtimeTerminalVoiceSynthesisResult>.value(
              const RealtimeTerminalVoiceSynthesisResult.audioReady(opaqueUri),
            ),
          ],
        );
        final enqueue = harness.orchestrator.enqueueCompletedTerminal(
          _completedState(
            text: privateOutput,
            sessionId: privateSession,
            turnId: privateTurn,
          ),
        );
        final process = await harness.orchestrator.processNext();
        final publicText = <Object?>[
          harness.orchestrator.state,
          enqueue,
          process,
        ].join('\n');

        expect(publicText, isNot(contains(privateOutput)));
        expect(publicText, isNot(contains(privateSession)));
        expect(publicText, isNot(contains(privateTurn)));
        expect(publicText, isNot(contains(opaqueUri)));
        expect(harness.orchestrator.state.lastTechnicalCode, isNull);

        harness.dispose();
      },
    );

    test('returns typed empty-queue result without synthesis', () async {
      final harness = _Harness();

      final result = await harness.orchestrator.processNext();

      expect(
        result.outcome,
        RealtimeTerminalVoiceOutputProcessOutcome.noPendingItem,
      );
      expect(result.queueRejection, VoiceOutputQueueRejection.noPendingItem);
      expect(harness.synthesis.calls, isEmpty);
      expect(harness.playback.calls, isEmpty);

      harness.dispose();
    });
  });
}

class _Harness {
  _Harness({
    int maxPendingItems = voiceOutputQueueMaxPendingItems,
    int maxRememberedTerminals =
        realtimeTerminalVoiceOutputMaxRememberedTerminals,
    List<Future<RealtimeTerminalVoiceSynthesisResult>>? synthesisResponses,
    List<Future<RealtimeTerminalVoicePlaybackResult>>? playbackResponses,
    Completer<void>? stopCompleter,
    Object? stopError,
  }) : stop = _FakeStop(completer: stopCompleter, error: stopError),
       synthesis = _FakeSynthesis(synthesisResponses),
       playback = _FakePlayback(playbackResponses) {
    queue = VoiceOutputQueueController(
      stopLocalPlayback: stop.call,
      maxPendingItems: maxPendingItems,
    );
    orchestrator = RealtimeTerminalVoiceOutputOrchestrator(
      queue: queue,
      synthesize: synthesis.call,
      playToTerminal: playback.call,
      maxRememberedTerminals: maxRememberedTerminals,
    );
  }

  final _FakeStop stop;
  final _FakeSynthesis synthesis;
  final _FakePlayback playback;
  late final VoiceOutputQueueController queue;
  late final RealtimeTerminalVoiceOutputOrchestrator orchestrator;

  void dispose() {
    orchestrator.dispose();
    queue.dispose();
  }
}

class _FakeStop {
  _FakeStop({this.completer, this.error});

  final Completer<void>? completer;
  final Object? error;
  int calls = 0;

  Future<void> call() {
    calls += 1;
    if (error != null) {
      return Future<void>.error(error!);
    }
    return completer?.future ?? Future<void>.value();
  }
}

class _FakeSynthesis {
  _FakeSynthesis(List<Future<RealtimeTerminalVoiceSynthesisResult>>? responses)
    : _responses = responses == null
          ? <Future<RealtimeTerminalVoiceSynthesisResult>>[]
          : List<Future<RealtimeTerminalVoiceSynthesisResult>>.from(responses);

  final List<Future<RealtimeTerminalVoiceSynthesisResult>> _responses;
  final List<RealtimeTerminalVoiceSynthesisRequest> calls =
      <RealtimeTerminalVoiceSynthesisRequest>[];

  Future<RealtimeTerminalVoiceSynthesisResult> call(
    RealtimeTerminalVoiceSynthesisRequest request,
  ) {
    calls.add(request);
    if (_responses.isNotEmpty) {
      return _responses.removeAt(0);
    }
    return Future<RealtimeTerminalVoiceSynthesisResult>.value(
      RealtimeTerminalVoiceSynthesisResult.audioReady(
        'https://audio.example.test/item-${calls.length}.mp3?opaque=fake',
      ),
    );
  }
}

class _FakePlayback {
  _FakePlayback(List<Future<RealtimeTerminalVoicePlaybackResult>>? responses)
    : _responses = responses == null
          ? <Future<RealtimeTerminalVoicePlaybackResult>>[]
          : List<Future<RealtimeTerminalVoicePlaybackResult>>.from(responses);

  final List<Future<RealtimeTerminalVoicePlaybackResult>> _responses;
  final List<Uri> calls = <Uri>[];

  Future<RealtimeTerminalVoicePlaybackResult> call(Uri source) {
    calls.add(source);
    if (_responses.isNotEmpty) {
      return _responses.removeAt(0);
    }
    return Future<RealtimeTerminalVoicePlaybackResult>.value(
      const RealtimeTerminalVoicePlaybackResult.completed(),
    );
  }
}

class _SynthesisCase {
  const _SynthesisCase({
    required this.createFuture,
    required this.outcome,
    required this.technicalCode,
  });

  final Future<RealtimeTerminalVoiceSynthesisResult> Function() createFuture;
  final RealtimeTerminalVoiceOutputProcessOutcome outcome;
  final String technicalCode;
}

class _PlaybackCase {
  const _PlaybackCase({
    required this.result,
    required this.outcome,
    required this.queueOutcome,
    this.technicalCode,
  });

  final RealtimeTerminalVoicePlaybackResult result;
  final RealtimeTerminalVoiceOutputProcessOutcome outcome;
  final VoiceOutputQueueItemOutcome queueOutcome;
  final String? technicalCode;
}

RealtimeTextStreamControllerState _completedState({
  required String text,
  required String sessionId,
  required String turnId,
  int terminalSequence = 1,
  int? lastSequence,
  String? terminalText,
  int? terminalCount,
  RealtimeTextStreamControllerPhase phase =
      RealtimeTextStreamControllerPhase.completed,
  RealtimeTextStreamTerminalOutcome outcome =
      RealtimeTextStreamTerminalOutcome.completed,
  RealtimeTextStreamProblem? problem,
}) {
  return RealtimeTextStreamControllerState(
    phase: phase,
    outputText: text,
    lastSequence: lastSequence ?? terminalSequence,
    cancelMode: 'cooperative',
    hardCancelSupported: false,
    createResponse: RealtimeTextStreamCreateResponse(
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
      eventsPath: '/realtime/fake/events',
      cancelPath: '/realtime/fake/cancel',
      idleTtlSeconds: 30,
      maxDurationSeconds: 120,
      maxPendingEvents: 8,
      maxEventBytes: 4096,
    ),
    terminal: RealtimeTextStreamTerminal(
      sequence: terminalSequence,
      outcome: outcome,
      finalText: terminalText ?? text,
      outputCharCount: terminalCount ?? text.runes.length,
      publicErrorCode: null,
      safeMessage: '',
      retryable: false,
    ),
    problem: problem,
  );
}

Future<void> _drainMicrotasks() => Future<void>.delayed(Duration.zero);
