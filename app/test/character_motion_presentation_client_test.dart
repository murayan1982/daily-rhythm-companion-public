import 'package:app/models/character_motion_presentation.dart';
import 'package:app/services/character_motion_presentation_client.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('CharacterMotionPresentationClient', () {
    test('parses completed mock result with three ordered commands', () async {
      final client = CharacterMotionPresentationClient(
        transport: (_) async => _result(),
      );

      final result = await client.apply(_request());

      expect(result.status, CharacterMotionExecutionStatus.completed);
      expect(
        result.presentationPhase,
        CharacterMotionPresentationPhase.completed,
      );
      expect(result.commandsRequested, 3);
      expect(result.commandsCompleted, 3);
      expect(result.commandResults.map((item) => item.order), <int>[1, 2, 3]);
      expect(result.eventTypes, hasLength(3));
      expect(result.adapter, 'mock');
      expect(result.realAdapterEnabled, isFalse);
      expect(result.providerExecutionAllowed, isFalse);
      expect(result.providerExecutionAttempted, isFalse);
      expect(result.networkExecution, isFalse);
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
      test('maps ${entry.key.wireName} result to presentation phase', () async {
        final client = CharacterMotionPresentationClient(
          transport: (_) async => _result(status: entry.key),
        );

        final result = await client.apply(_request());

        expect(result.status, entry.key);
        expect(result.presentationPhase, entry.value);
      });
    }

    test('request keeps only bounded public-safe fields', () {
      final request = CharacterMotionPresentationRequest(
        sourceFact: CharacterMotionLifecycleFact.thinking,
        sourceEventType: 'stream_started',
        sourceSessionId: 'session-1',
        sourceTurnId: 'turn-1',
        characterId: 'gentle_mina',
      );

      expect(request.toJson(), <String, Object?>{
        'schema_version': 'drc.v3.character-motion-presentation-request.1',
        'source_fact': 'thinking',
        'source_event_type': 'stream_started',
        'source_session_id': 'session-1',
        'source_turn_id': 'turn-1',
        'character_id': 'gentle_mina',
      });
      expect(request.toString(), isNot(contains('session-1')));
    });

    test('rejects oversized request identifier', () {
      expect(
        () => CharacterMotionPresentationRequest(
          sourceFact: CharacterMotionLifecycleFact.idle,
          sourceSessionId: List<String>.filled(129, 'x').join(),
        ),
        throwsA(
          isA<CharacterMotionPresentationProblemException>().having(
            (error) => error.problem.code,
            'code',
            'invalid_motion_source_session_id',
          ),
        ),
      );
    });

    test('rejects unknown response schema', () async {
      final body = _result()..['schema_version'] = 'unknown';
      await _expectProblem(body, 'invalid_motion_result_schema');
    });

    test('rejects unknown status enum', () async {
      final body = _result()..['status'] = 'mystery';
      await _expectProblem(body, 'invalid_motion_execution_status');
    });

    test('rejects unknown source fact enum', () async {
      final body = _result()..['source_fact'] = 'mystery';
      await _expectProblem(body, 'invalid_motion_source_fact');
    });

    test('rejects unknown cue enum', () async {
      final body = _result()..['cue'] = 'mystery';
      await _expectProblem(body, 'invalid_motion_cue');
    });

    test('rejects unknown command intent enum', () async {
      final body = _result();
      final commands = body['command_results']! as List<Object?>;
      (commands.first as Map<String, Object?>)['intent'] = 'mystery';
      await _expectProblem(body, 'invalid_motion_command_intent');
    });

    test('rejects more than three command results', () async {
      final body = _result();
      body['commands_requested'] = 3;
      body['commands_completed'] = 3;
      body['command_results'] = <Object?>[
        _command(1),
        _command(2),
        _command(3),
        _command(3),
      ];
      await _expectProblem(body, 'invalid_motion_command_results');
    });

    test('rejects more than twelve event types', () async {
      final body = _result()
        ..['event_types'] = List<String>.generate(
          13,
          (index) => 'event_$index',
        );
      await _expectProblem(body, 'invalid_motion_event_types');
    });

    test('rejects non-contiguous command order', () async {
      final body = _result();
      body['command_results'] = <Object?>[
        _command(1),
        _command(3),
        _command(3),
      ];
      await _expectProblem(body, 'invalid_motion_command_order');
    });

    test('rejects inconsistent command counts', () async {
      final body = _result()..['commands_completed'] = 2;
      await _expectProblem(body, 'invalid_completed_motion_result');
    });

    test('rejects completed result without closed session', () async {
      final body = _result()..['session_closed'] = false;
      await _expectProblem(body, 'invalid_completed_motion_result');
    });

    test('rejects inactive result that touched Framework', () async {
      final body = _result(status: CharacterMotionExecutionStatus.disabled)
        ..['framework_import_attempted'] = true;
      await _expectProblem(body, 'invalid_inactive_motion_result');
    });

    for (final mutation in <String, void Function(Map<String, Object?>)>{
      'adapter': (body) => body['adapter'] = 'real',
      'real_adapter_enabled': (body) => body['real_adapter_enabled'] = true,
      'provider_execution_allowed': (body) =>
          body['provider_execution_allowed'] = true,
      'provider_execution_attempted': (body) =>
          body['provider_execution_attempted'] = true,
      'network_execution': (body) => body['network_execution'] = true,
    }.entries) {
      test('rejects unsafe ${mutation.key} flag', () async {
        final body = _result();
        mutation.value(body);
        await _expectProblem(body, 'unsafe_motion_execution_flags');
      });
    }

    test('rejects oversized reason code and safe message', () async {
      final reason = _result()
        ..['reason_code'] = List<String>.filled(65, 'x').join();
      await _expectProblem(reason, 'invalid_motion_reason_code');

      final message = _result()
        ..['safe_message'] = List<String>.filled(257, 'x').join();
      await _expectProblem(message, 'invalid_motion_safe_message');
    });

    test('rejects unexpected response fields', () async {
      final body = _result()..['raw_framework_result'] = 'private';
      await _expectProblem(body, 'invalid_motion_result_shape');
    });

    test('normalizes raw transport exception to safe problem', () async {
      const privateError = 'private provider payload marker';
      final client = CharacterMotionPresentationClient(
        transport: (_) async => throw StateError(privateError),
      );

      await expectLater(
        client.apply(_request()),
        throwsA(
          isA<CharacterMotionPresentationProblemException>()
              .having(
                (error) => error.problem.code,
                'code',
                'motion_transport_failed',
              )
              .having(
                (error) => error.problem.message,
                'message',
                isNot(contains(privateError)),
              ),
        ),
      );
    });
  });
}

CharacterMotionPresentationRequest _request() =>
    CharacterMotionPresentationRequest(
      sourceFact: CharacterMotionLifecycleFact.idle,
      sourceEventType: 'turn_completed',
      sourceSessionId: 'session-1',
      sourceTurnId: 'turn-1',
      characterId: 'gentle_mina',
    );

Future<void> _expectProblem(Map<String, Object?> body, String code) async {
  final client = CharacterMotionPresentationClient(
    transport: (_) async => body,
  );
  await expectLater(
    client.apply(_request()),
    throwsA(
      isA<CharacterMotionPresentationProblemException>().having(
        (error) => error.problem.code,
        'code',
        code,
      ),
    ),
  );
}

Map<String, Object?> _result({
  CharacterMotionExecutionStatus status =
      CharacterMotionExecutionStatus.completed,
}) {
  final inactive =
      status == CharacterMotionExecutionStatus.ignored ||
      status == CharacterMotionExecutionStatus.disabled;
  final completed = status == CharacterMotionExecutionStatus.completed;
  final commandResults = inactive
      ? <Object?>[]
      : completed
      ? <Object?>[_command(1), _command(2), _command(3)]
      : <Object?>[
          _command(
            1,
            retryable: status == CharacterMotionExecutionStatus.failed,
          ),
        ];
  final requested = inactive
      ? 3
      : completed
      ? 3
      : 3;
  final completedCount = inactive
      ? 0
      : completed
      ? 3
      : 0;
  return <String, Object?>{
    'schema_version': 'drc.v3.framework-mock-motion-execution.1',
    'status': status.wireName,
    'source_fact': 'idle',
    'cue': inactive ? null : 'idle',
    'source_event_type': 'turn_completed',
    'source_session_id': 'session-1',
    'source_turn_id': 'turn-1',
    'character_id': 'gentle_mina',
    'commands_requested': requested,
    'commands_completed': completedCount,
    'command_results': commandResults,
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
        ? 'The character-motion request failed safely.'
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
