import 'dart:convert';

import 'package:app/models/framework_vts_motion_presentation.dart';
import 'package:app/services/backend_api_client.dart';
import 'package:app/services/configured_framework_vts_motion_presentation_runtime.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

void main() {
  test('runtime remains unconfigured when disabled', () {
    final runtime = ConfiguredFrameworkVtsMotionPresentationRuntime(
      enabled: false,
      apiClient: const BackendApiClient(baseUrl: 'http://backend.test'),
    );
    expect(runtime.buildControllerFactory(), isNull);
  });

  test('controller construction and disposal do not send HTTP', () {
    var calls = 0;
    final runtime = ConfiguredFrameworkVtsMotionPresentationRuntime(
      enabled: true,
      apiClient: const BackendApiClient(baseUrl: 'http://backend.test'),
      httpClientFactory: () => MockClient((_) async {
        calls += 1;
        return http.Response('{}', 200);
      }),
    );
    final controller = runtime.buildControllerFactory()!();
    expect(calls, 0);
    controller.dispose();
    expect(calls, 0);
  });

  test('explicit apply sends one POST with one command', () async {
    var calls = 0;
    final runtime = ConfiguredFrameworkVtsMotionPresentationRuntime(
      enabled: true,
      apiClient: const BackendApiClient(baseUrl: 'http://backend.test/'),
      httpClientFactory: () => MockClient((request) async {
        calls += 1;
        expect(request.method, 'POST');
        expect(request.url.path, configuredFrameworkVtsMotionPresentationPath);
        final body = jsonDecode(request.body) as Map<String, dynamic>;
        expect((body['command'] as Map<String, dynamic>)['order'], 1);
        return http.Response(
          jsonEncode(_result()),
          200,
          headers: {'content-type': 'application/json'},
        );
      }),
    );
    final controller = runtime.buildControllerFactory()!();
    await controller.apply(
      FrameworkVtsMotionPresentationRequest(
        intent: FrameworkVtsMotionIntent.expression,
        selectorValue: 'smile',
      ),
    );
    expect(calls, 1);
    controller.dispose();
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
  'safe_message': 'disabled',
};
