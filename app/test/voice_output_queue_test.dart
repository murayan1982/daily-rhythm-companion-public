import 'dart:async';

import 'package:app/services/voice_output_queue.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('VoiceOutputQueueController', () {
    test('starts idle without retaining utterance text in public state', () {
      final stop = _FakeLocalPlaybackStop();
      final controller = VoiceOutputQueueController(
        stopLocalPlayback: stop.call,
      );

      expect(controller.state.phase, VoiceOutputQueuePhase.idle);
      expect(controller.state.pendingCount, 0);
      expect(controller.state.retainedCodePoints, 0);
      expect(controller.state.activeItem, isNull);
      expect(controller.state.toString(), isNot(contains('private utterance')));

      controller.dispose();
    });

    test('enqueues and claims pending utterances in FIFO order', () {
      final stop = _FakeLocalPlaybackStop();
      final controller = VoiceOutputQueueController(
        stopLocalPlayback: stop.call,
      );

      final first = controller.enqueue('first utterance');
      final second = controller.enqueue('second utterance');

      expect(first.accepted, isTrue);
      expect(second.accepted, isTrue);
      expect(controller.state.pendingCount, 2);
      expect(controller.state.phase, VoiceOutputQueuePhase.ready);

      final firstClaim = controller.claimNext();
      expect(firstClaim.accepted, isTrue);
      expect(firstClaim.claim!.utterance, 'first utterance');
      expect(controller.state.activeItem!.itemId, first.item!.itemId);
      expect(controller.state.pendingCount, 1);

      expect(controller.complete(firstClaim.claim!).accepted, isTrue);
      final secondClaim = controller.claimNext();
      expect(secondClaim.claim!.utterance, 'second utterance');
      expect(controller.state.activeItem!.itemId, second.item!.itemId);

      controller.dispose();
    });

    test('rejects empty and whitespace-only utterances', () {
      final controller = VoiceOutputQueueController(
        stopLocalPlayback: _FakeLocalPlaybackStop().call,
      );

      final empty = controller.enqueue('');
      final whitespace = controller.enqueue('  \n\t  ');

      expect(empty.accepted, isFalse);
      expect(empty.rejection, VoiceOutputQueueRejection.invalidUtterance);
      expect(whitespace.accepted, isFalse);
      expect(whitespace.rejection, VoiceOutputQueueRejection.invalidUtterance);
      expect(controller.state.pendingCount, 0);

      controller.dispose();
    });

    test('enforces Unicode code-point utterance bounds', () {
      final controller = VoiceOutputQueueController(
        stopLocalPlayback: _FakeLocalPlaybackStop().call,
        maxUtteranceCodePoints: 2,
      );

      final accepted = controller.enqueue('😀😀');
      final rejected = controller.enqueue('😀😀😀');

      expect(accepted.accepted, isTrue);
      expect(accepted.item!.characterCount, 2);
      expect(rejected.accepted, isFalse);
      expect(rejected.rejection, VoiceOutputQueueRejection.utteranceTooLong);

      controller.dispose();
    });

    test('enforces the pending item limit', () {
      final controller = VoiceOutputQueueController(
        stopLocalPlayback: _FakeLocalPlaybackStop().call,
        maxPendingItems: 2,
      );

      expect(controller.enqueue('one').accepted, isTrue);
      expect(controller.enqueue('two').accepted, isTrue);
      final rejected = controller.enqueue('three');

      expect(rejected.accepted, isFalse);
      expect(rejected.rejection, VoiceOutputQueueRejection.pendingLimitReached);
      expect(controller.state.pendingCount, 2);

      controller.dispose();
    });

    test(
      'enforces the retained text limit across active and pending items',
      () {
        final controller = VoiceOutputQueueController(
          stopLocalPlayback: _FakeLocalPlaybackStop().call,
          maxRetainedCodePoints: 5,
        );

        expect(controller.enqueue('abc').accepted, isTrue);
        final active = controller.claimNext();
        expect(active.accepted, isTrue);
        expect(controller.enqueue('de').accepted, isTrue);

        final rejected = controller.enqueue('f');
        expect(rejected.accepted, isFalse);
        expect(
          rejected.rejection,
          VoiceOutputQueueRejection.retainedTextLimitReached,
        );
        expect(controller.state.retainedCodePoints, 5);

        controller.dispose();
      },
    );

    test('allows only one active claimed item', () {
      final controller = VoiceOutputQueueController(
        stopLocalPlayback: _FakeLocalPlaybackStop().call,
      );
      controller.enqueue('one');
      controller.enqueue('two');

      final first = controller.claimNext();
      final second = controller.claimNext();

      expect(first.accepted, isTrue);
      expect(second.accepted, isFalse);
      expect(second.rejection, VoiceOutputQueueRejection.activeItemExists);
      expect(controller.state.pendingCount, 1);

      controller.dispose();
    });

    test('completion releases retained text and makes the next item ready', () {
      final controller = VoiceOutputQueueController(
        stopLocalPlayback: _FakeLocalPlaybackStop().call,
      );
      controller.enqueue('one');
      controller.enqueue('second');
      final claim = controller.claimNext().claim!;

      final completed = controller.complete(claim);

      expect(completed.accepted, isTrue);
      expect(
        controller.state.lastOutcome,
        VoiceOutputQueueItemOutcome.completed,
      );
      expect(controller.state.retainedCodePoints, 'second'.runes.length);
      expect(controller.state.phase, VoiceOutputQueuePhase.ready);
      expect(controller.state.activeItem, isNull);

      controller.dispose();
    });

    test(
      'failure releases the item and exposes only a bounded technical code',
      () {
        final controller = VoiceOutputQueueController(
          stopLocalPlayback: _FakeLocalPlaybackStop().call,
        );
        controller.enqueue('private utterance');
        final claim = controller.claimNext().claim!;

        final failed = controller.fail(claim, technicalCode: 'decoder_failed');

        expect(failed.accepted, isTrue);
        expect(failed.technicalCode, 'decoder_failed');
        expect(
          controller.state.lastOutcome,
          VoiceOutputQueueItemOutcome.failed,
        );
        expect(controller.state.lastTechnicalCode, 'decoder_failed');
        expect(controller.state.retainedCodePoints, 0);
        expect(
          controller.state.toString(),
          isNot(contains('private utterance')),
        );

        controller.dispose();
      },
    );

    test(
      'flush clears pending and active items and requests local stop once',
      () async {
        final stop = _FakeLocalPlaybackStop();
        final controller = VoiceOutputQueueController(
          stopLocalPlayback: stop.call,
        );
        controller.enqueue('active');
        final active = controller.claimNext().claim!;
        controller.enqueue('pending one');
        controller.enqueue('pending two');

        final result = await controller.flush();

        expect(result.outcome, VoiceOutputQueueFlushOutcome.completed);
        expect(result.clearedPendingCount, 2);
        expect(result.invalidatedActiveItem, isTrue);
        expect(result.localPlaybackStopRequested, isTrue);
        expect(result.localPlaybackStopSucceeded, isTrue);
        expect(stop.calls, 1);
        expect(controller.state.phase, VoiceOutputQueuePhase.idle);
        expect(controller.state.pendingCount, 0);
        expect(controller.state.activeItem, isNull);
        expect(controller.state.retainedCodePoints, 0);

        final late = controller.complete(active);
        expect(late.accepted, isFalse);
        expect(late.rejection, VoiceOutputQueueRejection.staleGeneration);

        controller.dispose();
      },
    );

    test(
      'flush keeps the queue cleared when local playback stop fails',
      () async {
        final stop = _FakeLocalPlaybackStop(
          error: StateError('private driver failure'),
        );
        final controller = VoiceOutputQueueController(
          stopLocalPlayback: stop.call,
        );
        controller.enqueue('private utterance');
        controller.claimNext();
        controller.enqueue('pending');

        final result = await controller.flush();

        expect(
          result.outcome,
          VoiceOutputQueueFlushOutcome.completedWithLocalPlaybackStopFailure,
        );
        expect(result.localPlaybackStopRequested, isTrue);
        expect(result.localPlaybackStopSucceeded, isFalse);
        expect(result.technicalCode, 'local_playback_stop_failed');
        expect(controller.state.phase, VoiceOutputQueuePhase.idle);
        expect(controller.state.pendingCount, 0);
        expect(controller.state.activeItem, isNull);
        expect(controller.state.retainedCodePoints, 0);
        expect(
          controller.state.toString(),
          isNot(contains('private driver failure')),
        );

        controller.dispose();
      },
    );

    test(
      'concurrent flush callers share one local playback stop request',
      () async {
        final stop = _FakeLocalPlaybackStop()..hold();
        final controller = VoiceOutputQueueController(
          stopLocalPlayback: stop.call,
        );
        controller.enqueue('one');

        final first = controller.flush();
        final second = controller.flush();

        expect(identical(first, second), isTrue);
        expect(stop.calls, 1);
        expect(controller.state.phase, VoiceOutputQueuePhase.flushing);

        stop.release();
        final results = await Future.wait(<Future<VoiceOutputQueueFlushResult>>[
          first,
          second,
        ]);
        expect(results[0].outcome, VoiceOutputQueueFlushOutcome.completed);
        expect(results[1].outcome, VoiceOutputQueueFlushOutcome.completed);
        expect(stop.calls, 1);

        controller.dispose();
      },
    );

    test('enqueue and claim are rejected while flush is in progress', () async {
      final stop = _FakeLocalPlaybackStop()..hold();
      final controller = VoiceOutputQueueController(
        stopLocalPlayback: stop.call,
      );
      controller.enqueue('one');

      final flush = controller.flush();
      final enqueue = controller.enqueue('two');
      final claim = controller.claimNext();

      expect(enqueue.accepted, isFalse);
      expect(enqueue.rejection, VoiceOutputQueueRejection.flushInProgress);
      expect(claim.accepted, isFalse);
      expect(claim.rejection, VoiceOutputQueueRejection.flushInProgress);

      stop.release();
      await flush;
      controller.dispose();
    });

    test('stale and mismatched claims cannot complete the active item', () {
      final controller = VoiceOutputQueueController(
        stopLocalPlayback: _FakeLocalPlaybackStop().call,
      );
      controller.enqueue('one');
      final claim = controller.claimNext().claim!;
      final mismatched = VoiceOutputQueueClaim(
        item: VoiceOutputQueueItemMetadata(
          itemId: 'different-item',
          generation: claim.item.generation,
          characterCount: claim.item.characterCount,
        ),
        utterance: 'not retained',
      );

      final rejected = controller.complete(mismatched);

      expect(rejected.accepted, isFalse);
      expect(rejected.rejection, VoiceOutputQueueRejection.staleItem);
      expect(controller.state.activeItem!.itemId, claim.item.itemId);

      controller.dispose();
    });

    test('dispose clears retained queue data and rejects later operations', () {
      final controller = VoiceOutputQueueController(
        stopLocalPlayback: _FakeLocalPlaybackStop().call,
      );
      controller.enqueue('private utterance');
      final claim = controller.claimNext().claim!;

      controller.dispose();

      expect(controller.state.phase, VoiceOutputQueuePhase.disposed);
      expect(controller.state.pendingCount, 0);
      expect(controller.state.activeItem, isNull);
      expect(controller.state.retainedCodePoints, 0);
      expect(
        controller.enqueue('later').rejection,
        VoiceOutputQueueRejection.disposed,
      );
      expect(
        controller.complete(claim).rejection,
        VoiceOutputQueueRejection.disposed,
      );
    });
  });
}

class _FakeLocalPlaybackStop {
  _FakeLocalPlaybackStop({this.error});

  final Object? error;
  int calls = 0;
  Completer<void>? _held;

  void hold() {
    _held = Completer<void>();
  }

  void release() {
    _held?.complete();
  }

  Future<void> call() async {
    calls += 1;
    if (error != null) {
      throw error!;
    }
    await _held?.future;
  }
}
