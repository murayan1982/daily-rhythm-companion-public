import 'package:app/models/framework_vts_motion_presentation.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('request emits one bounded command', () {
    final request = FrameworkVtsMotionPresentationRequest(
      intent: FrameworkVtsMotionIntent.expression,
      selectorValue: 'smile',
      characterId: 'gentle_mina',
    );
    final json = request.toJson();
    expect(
      json['schema_version'],
      'drc.v3.framework-vts-motion-presentation-request.1',
    );
    final command = json['command']! as Map<String, Object?>;
    expect(command['order'], 1);
    expect(command['intent'], 'expression');
    expect(command['expression'], 'smile');
    expect(command['emotion'], isNull);
  });

  test('selector intents require one value', () {
    expect(
      () => FrameworkVtsMotionPresentationRequest(
        intent: FrameworkVtsMotionIntent.gesture,
      ),
      throwsA(isA<FrameworkVtsMotionPresentationProblemException>()),
    );
  });

  test('reset and stop reject selector values', () {
    expect(
      () => FrameworkVtsMotionPresentationRequest(
        intent: FrameworkVtsMotionIntent.resetExpression,
        selectorValue: 'private',
      ),
      throwsA(isA<FrameworkVtsMotionPresentationProblemException>()),
    );
  });

  test('result parses public-safe execution fields', () {
    final result = FrameworkVtsMotionPresentationResult.fromJson(_result());
    expect(result.status, FrameworkVtsMotionExecutionStatus.disabled);
    expect(
      result.presentationPhase,
      FrameworkVtsMotionPresentationPhase.disabled,
    );
    expect(result.commandsRequested, 1);
    expect(result.frameworkImportAttempted, isFalse);
    expect(result.networkExecutionAttempted, isFalse);
  });

  test('result rejects non-boolean execution markers', () {
    final json = _result()..['provider_execution_attempted'] = 'false';
    expect(
      () => FrameworkVtsMotionPresentationResult.fromJson(json),
      throwsA(isA<FrameworkVtsMotionPresentationProblemException>()),
    );
  });

  test('result rejects unexpected private fields', () {
    final json = _result()..['authentication_token'] = 'private';
    expect(
      () => FrameworkVtsMotionPresentationResult.fromJson(json),
      throwsA(isA<FrameworkVtsMotionPresentationProblemException>()),
    );
  });
}

Map<String, Object?> _result() => <String, Object?>{
  'schema_version': 'drc.v3.framework-vts-motion-execution.1',
  'status': 'disabled',
  'commands_requested': 1,
  'commands_applied': 0,
  'commands_completed': 0,
  'optional_commands_skipped': 0,
  'command_results': <Object?>[],
  'event_types': <Object?>[],
  'framework_import_attempted': false,
  'session_created': false,
  'session_closed': false,
  'adapter': 'vts',
  'real_adapter_enabled': false,
  'provider_execution_allowed': false,
  'provider_execution_attempted': false,
  'network_execution_attempted': false,
  'real_motion_executed': false,
  'reason_code': 'framework_vts_motion_disabled',
  'safe_message': 'Framework VTS motion execution is disabled.',
};
