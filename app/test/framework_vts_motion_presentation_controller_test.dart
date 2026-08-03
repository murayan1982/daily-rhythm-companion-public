import 'dart:async';

import 'package:app/models/framework_vts_motion_presentation.dart';
import 'package:app/services/framework_vts_motion_presentation_client.dart';
import 'package:app/services/framework_vts_motion_presentation_controller.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test(
    'controller applies one request and publishes normalized result',
    () async {
      var calls = 0;
      final controller = FrameworkVtsMotionPresentationController(
        client: FrameworkVtsMotionPresentationClient(
          transport: (request) async {
            calls += 1;
            expect(request.intent, FrameworkVtsMotionIntent.expression);
            return _result();
          },
        ),
      );
      await controller.apply(_request());
      expect(calls, 1);
      expect(
        controller.state.phase,
        FrameworkVtsMotionPresentationPhase.disabled,
      );
      controller.dispose();
    },
  );

  test('duplicate apply is rejected while active', () async {
    final completer = Completer<Map<String, Object?>>();
    final controller = FrameworkVtsMotionPresentationController(
      client: FrameworkVtsMotionPresentationClient(
        transport: (_) => completer.future,
      ),
    );
    final first = controller.apply(_request());
    await Future<void>.delayed(Duration.zero);
    await expectLater(
      controller.apply(_request()),
      throwsA(isA<FrameworkVtsMotionPresentationProblemException>()),
    );
    completer.complete(_result());
    await first;
    controller.dispose();
  });

  test('reset invalidates a late result', () async {
    final completer = Completer<Map<String, Object?>>();
    final controller = FrameworkVtsMotionPresentationController(
      client: FrameworkVtsMotionPresentationClient(
        transport: (_) => completer.future,
      ),
    );
    final future = controller.apply(_request());
    controller.reset();
    completer.complete(_result());
    await future;
    expect(controller.state.phase, FrameworkVtsMotionPresentationPhase.idle);
    controller.dispose();
  });
}

FrameworkVtsMotionPresentationRequest _request() =>
    FrameworkVtsMotionPresentationRequest(
      intent: FrameworkVtsMotionIntent.expression,
      selectorValue: 'smile',
    );

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
  'safe_message': 'disabled',
};
