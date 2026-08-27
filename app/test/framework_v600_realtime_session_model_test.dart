import 'package:app/models/framework_v600_realtime_session.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('FrameworkV600RealtimeSession models', () {
    test('accepted schema versions parse and capability projection preserved', () {
      final open = FrameworkV600RealtimeOpenResult.fromJson(_open());

      expect(open.schemaVersion, frameworkV600OpenSchema);
      expect(open.sessionId, _sessionId);
      expect(open.capabilities.supportsTextChat, isTrue);
      expect(open.capabilities.supportsVoiceInput, isTrue);
      expect(open.capabilities.supportsVoiceOutput, isTrue);
      expect(open.capabilities.supportsMotion, isFalse);
      expect(open.capabilities.hostPlaybackOwnedByDrc, isTrue);
    });

    test('wrong schema version rejected', () {
      expect(
        () => FrameworkV600RealtimeOpenResult.fromJson(
          _open()..['schema_version'] = 'drc.v4.unexpected.1',
        ),
        throwsA(_problemCode('invalid_schema_version')),
      );
    });

    test('canonical session turn and generation ids are validated', () {
      final turn = FrameworkV600RealtimeTurnResult.fromJson(_turn());

      expect(turn.sessionId, _sessionId);
      expect(turn.turnId, _turnId);
      expect(turn.generationId, _generationId);
      expect(
        () => FrameworkV600RealtimeTurnResult.fromJson(
          _turn()..['turn_id'] = 'turn-neutral',
        ),
        throwsA(_problemCode('invalid_turn_id')),
      );
      expect(
        () => FrameworkV600RealtimeTurnResult.fromJson(
          _turn()..['generation_id'] = 'generation-neutral',
        ),
        throwsA(_problemCode('invalid_generation_id')),
      );
      expect(
        () => FrameworkV600RealtimeOpenResult.fromJson(
          _open()..['session_id'] = 'session-neutral',
        ),
        throwsA(_problemCode('invalid_session_id')),
      );
    });

    test('provider-free invariants reject real runtime contradictions', () {
      expect(FrameworkV600RealtimeOpenResult.fromJson(_open()).available, isTrue);
      expect(
        () => FrameworkV600RealtimeOpenResult.fromJson(
          _open()..['real_runtime_enabled'] = true,
        ),
        throwsA(_problemCode('invalid_open_invariant')),
      );
      final contradicted = _open();
      contradicted['capabilities'] =
          _capabilities()..['unified_real_pipeline_claimed'] = true;
      expect(
        () => FrameworkV600RealtimeOpenResult.fromJson(contradicted),
        throwsA(_problemCode('invalid_open_invariant')),
      );
    });

    test('event metadata projected but payload not retained or exposed', () {
      final event = FrameworkV600RealtimeEventSummary.fromJson(_event());

      expect(event.eventType, 'turn_completed');
      expect(event.sequence, 1);
      expect(event.terminal, isTrue);
      expect(event.toString(), isNot(contains('payload_marker')));
      expect(event.toString(), isNot(contains('payload')));
    });

    test('malformed shape rejected safely', () {
      expect(
        () => FrameworkV600RealtimeDiagnosticsSnapshot.fromJson(<String, Object?>{
          'schema_version': frameworkV600DiagnosticsSchema,
          'session_id': _sessionId,
        }),
        throwsA(isA<FrameworkV600RealtimeProblemException>()),
      );
    });

    test('problem representation contains only bounded safe fields', () {
      const problem = FrameworkV600RealtimeProblem(
        code: 'invalid_response',
        message: 'safe message',
        retryable: false,
      );

      expect(problem.toString(), contains('invalid_response'));
      expect(problem.toString(), isNot(contains('safe message')));
    });
  });
}

const _sessionId = 'fw_session_0123456789abcdef0123456789abcdef';
const _turnId = 'fw_turn_0123456789abcdef0123456789abcdef';
const _generationId = 'fw_generation_0123456789abcdef0123456789abcdef';

Matcher _problemCode(String code) => isA<FrameworkV600RealtimeProblemException>()
    .having((error) => error.problem.code, 'code', code);

Map<String, Object?> _open() => <String, Object?>{
  'schema_version': frameworkV600OpenSchema,
  'status': 'open',
  'available': true,
  'session_id': _sessionId,
  'public_error_code': null,
  'safe_message': '',
  'retryable': false,
  'real_runtime_requested': false,
  'real_runtime_enabled': false,
  'runtime_executable': true,
  'capabilities': _capabilities(),
};

Map<String, Object?> _capabilities() => <String, Object?>{
  'schema_version': frameworkV600CapabilitySchema,
  'session_id': _sessionId,
  'supports_text_chat': true,
  'supports_voice_input': true,
  'supports_voice_output': true,
  'supports_motion': false,
  'real_runtime_enabled': false,
  'hard_cancel_supported': false,
  'tts_queue_flush_supported': true,
  'runtime_available': true,
  'fake_runtime': 'provider_free',
  'real_runtime': 'unavailable',
  'guarded': true,
  'cooperative_cancel_supported': true,
  'provider_hard_cancel_supported': false,
  'pending_flush_supported': true,
  'host_playback_owned_by_drc': true,
  'real_unified_runtime_available': false,
  'unified_real_pipeline_claimed': false,
};

Map<String, Object?> _turn() => <String, Object?>{
  'schema_version': frameworkV600TurnSchema,
  'outcome': 'completed',
  'terminal': true,
  'session_id': _sessionId,
  'turn_id': _turnId,
  'generation_id': _generationId,
  'public_error_code': null,
  'safe_message': '',
  'retryable': false,
  'recovery_action': 'none',
  'events': [_event()],
  'capabilities': _capabilities(),
  'interrupt': null,
  'diagnostics': null,
};

Map<String, Object?> _event() => <String, Object?>{
  'schema_version': frameworkV600EventSchema,
  'event_type': 'turn_completed',
  'session_id': _sessionId,
  'turn_id': _turnId,
  'generation_id': _generationId,
  'sequence': 1,
  'phase': 'completed',
  'terminal': true,
  'public_error_code': null,
  'safe_message': 'safe',
  'retryable': false,
  'payload': <String, Object?>{'payload_marker': 'neutral'},
};
