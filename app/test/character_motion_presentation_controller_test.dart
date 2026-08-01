import 'dart:async';

import 'package:app/models/character_motion_presentation.dart';
import 'package:app/services/character_motion_presentation_client.dart';
import 'package:app/services/character_motion_presentation_controller.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('CharacterMotionPresentationController', () {
    test('starts idle and completes one request', () async {
      final controller = _controller((_) async => _result());
      final phases = <CharacterMotionPresentationPhase>[];
      controller.addListener(() => phases.add(controller.state.phase));

      await controller.apply(_request());

      expect(phases, <CharacterMotionPresentationPhase>[
        CharacterMotionPresentationPhase.applying,
        CharacterMotionPresentationPhase.completed,
      ]);
      expect(controller.state.result?.commandsCompleted, 3);
      expect(controller.state.problem, isNull);
      controller.dispose();
    });

    for (final entry
        in <CharacterMotionExecutionStatus, CharacterMotionPresentationPhase>{
          CharacterMotionExecutionStatus.ignored:
              CharacterMotionPresentationPhase.ignored,
          CharacterMotionExecutionStatus.disabled:
              CharacterMotionPresentationPhase.disabled,
          CharacterMotionExecutionStatus.unavailable:
              CharacterMotionPresentationPhase.unavailable,
          CharacterMotionExecutionStatus.failed:
              CharacterMotionPresentationPhase.failed,
        }.entries) {
      test('applies ${entry.key.wireName} terminal state', () async {
        final controller = _controller((_) async => _result(status: entry.key));

        await controller.apply(_request());

        expect(controller.state.phase, entry.value);
        if (entry.key == CharacterMotionExecutionStatus.failed) {
          expect(controller.state.problem?.code, 'mock_motion_failed');
          expect(controller.state.problem?.message, 'Safe motion failure.');
        } else {
          expect(controller.state.problem, isNull);
        }
        controller.dispose();
      });
    }

    test('rejects simultaneous apply and active replacement', () async {
      final completer = Completer<Map<String, Object?>>();
      final controller = _controller((_) => completer.future);
      final first = controller.apply(_request());

      await expectLater(
        controller.apply(
          CharacterMotionPresentationRequest(
            sourceFact: CharacterMotionLifecycleFact.speaking,
          ),
        ),
        throwsA(
          isA<CharacterMotionPresentationProblemException>().having(
            (error) => error.problem.code,
            'code',
            'active_motion_request_rejected',
          ),
        ),
      );

      completer.complete(_result());
      await first;
      expect(
        controller.state.phase,
        CharacterMotionPresentationPhase.completed,
      );
      controller.dispose();
    });

    test('reset invalidates late completion', () async {
      final completer = Completer<Map<String, Object?>>();
      final controller = _controller((_) => completer.future);
      final apply = controller.apply(_request());

      controller.reset();
      completer.complete(_result());
      await apply;

      expect(controller.state.phase, CharacterMotionPresentationPhase.idle);
      expect(controller.state.result, isNull);
      expect(controller.state.problem, isNull);
      controller.dispose();
    });

    test('close invalidates late completion and rejects new apply', () async {
      final completer = Completer<Map<String, Object?>>();
      final controller = _controller((_) => completer.future);
      final apply = controller.apply(_request());

      controller.close();
      completer.complete(_result());
      await apply;

      expect(controller.state.phase, CharacterMotionPresentationPhase.closed);
      await expectLater(
        controller.apply(_request()),
        throwsA(
          isA<CharacterMotionPresentationProblemException>().having(
            (error) => error.problem.code,
            'code',
            'motion_controller_closed',
          ),
        ),
      );
      controller.dispose();
    });

    test('dispose invalidates late completion without notification', () async {
      final completer = Completer<Map<String, Object?>>();
      final controller = _controller((_) => completer.future);
      var notifications = 0;
      controller.addListener(() => notifications += 1);
      final apply = controller.apply(_request());
      expect(notifications, 1);

      controller.dispose();
      completer.complete(_result());
      await apply;

      expect(notifications, 1);
      expect(controller.state.phase, CharacterMotionPresentationPhase.closed);
    });

    test('terminal state resets to idle', () async {
      final controller = _controller((_) async => _result());

      await controller.apply(_request());
      controller.reset();

      expect(controller.state.phase, CharacterMotionPresentationPhase.idle);
      expect(controller.state.request, isNull);
      expect(controller.state.result, isNull);
      expect(controller.state.problem, isNull);
      controller.dispose();
    });

    test('typed client problem becomes safe failed state', () async {
      const privatePayload = 'private token and provider payload';
      final controller = _controller(
        (_) async => throw StateError(privatePayload),
      );

      await controller.apply(_request());

      expect(controller.state.phase, CharacterMotionPresentationPhase.failed);
      expect(controller.state.problem?.code, 'motion_transport_failed');
      expect(
        controller.state.problem?.message,
        isNot(contains(privatePayload)),
      );
      expect(controller.state.toString(), isNot(contains(privatePayload)));
      controller.dispose();
    });

    test('invalid response becomes typed failed state', () async {
      final controller = _controller(
        (_) async => _result()..['adapter'] = 'real',
      );

      await controller.apply(_request());

      expect(controller.state.phase, CharacterMotionPresentationPhase.failed);
      expect(controller.state.problem?.code, 'unsafe_motion_execution_flags');
      expect(controller.state.result, isNull);
      controller.dispose();
    });

    test(
      'failed normalized result exposes only bounded safe problem',
      () async {
        final controller = _controller(
          (_) async => _result(status: CharacterMotionExecutionStatus.failed),
        );

        await controller.apply(_request());

        expect(controller.state.phase, CharacterMotionPresentationPhase.failed);
        expect(controller.state.problem?.code, 'mock_motion_failed');
        expect(controller.state.problem?.message, 'Safe motion failure.');
        expect(controller.state.problem?.retryable, isTrue);
        expect(controller.state.toString(), isNot(contains('session-1')));
        controller.dispose();
      },
    );

    test('close is idempotent', () {
      final controller = _controller((_) async => _result());
      var notifications = 0;
      controller.addListener(() => notifications += 1);

      controller.close();
      controller.close();

      expect(notifications, 1);
      expect(controller.state.phase, CharacterMotionPresentationPhase.closed);
      controller.dispose();
    });

    test('reset while idle notifies and preserves idle', () {
      final controller = _controller((_) async => _result());
      var notifications = 0;
      controller.addListener(() => notifications += 1);

      controller.reset();

      expect(notifications, 1);
      expect(controller.state.phase, CharacterMotionPresentationPhase.idle);
      controller.dispose();
    });
  });
}

CharacterMotionPresentationController _controller(
  CharacterMotionPresentationTransport transport,
) => CharacterMotionPresentationController(
  client: CharacterMotionPresentationClient(transport: transport),
);

CharacterMotionPresentationRequest _request() =>
    CharacterMotionPresentationRequest(
      sourceFact: CharacterMotionLifecycleFact.idle,
      sourceEventType: 'turn_completed',
      sourceSessionId: 'session-1',
      sourceTurnId: 'turn-1',
      characterId: 'gentle_mina',
    );

Map<String, Object?> _result({
  CharacterMotionExecutionStatus status =
      CharacterMotionExecutionStatus.completed,
}) {
  final inactive =
      status == CharacterMotionExecutionStatus.ignored ||
      status == CharacterMotionExecutionStatus.disabled;
  final completed = status == CharacterMotionExecutionStatus.completed;
  return <String, Object?>{
    'schema_version': 'drc.v3.framework-mock-motion-execution.1',
    'status': status.wireName,
    'source_fact': 'idle',
    'cue': inactive ? null : 'idle',
    'source_event_type': 'turn_completed',
    'source_session_id': 'session-1',
    'source_turn_id': 'turn-1',
    'character_id': 'gentle_mina',
    'commands_requested': 3,
    'commands_completed': completed ? 3 : 0,
    'command_results': inactive
        ? <Object?>[]
        : completed
        ? <Object?>[_command(1), _command(2), _command(3)]
        : <Object?>[_command(1, retryable: true)],
    'event_types': inactive
        ? <String>[]
        : <String>['session_opened', 'motion_applied', 'session_closed'],
    'framework_import_attempted': inactive ? false : true,
    'session_created': inactive ? false : true,
    'session_closed': inactive ? false : true,
    'adapter': 'mock',
    'real_adapter_enabled': false,
    'provider_execution_allowed': false,
    'provider_execution_attempted': false,
    'network_execution': false,
    'reason_code': status == CharacterMotionExecutionStatus.failed
        ? 'mock_motion_failed'
        : '${status.wireName}_motion',
    'safe_message': status == CharacterMotionExecutionStatus.failed
        ? 'Safe motion failure.'
        : '',
  };
}

Map<String, Object?> _command(int order, {bool retryable = false}) =>
    <String, Object?>{
      'order': order,
      'intent': order == 1
          ? 'reset_expression'
          : order == 2
          ? 'speaking_state'
          : 'idle_motion',
      'outcome': 'completed',
      'state': 'idle',
      'adapter_status': 'ready',
      'public_error_code': '',
      'retryable': retryable,
      'safe_message': '',
    };
