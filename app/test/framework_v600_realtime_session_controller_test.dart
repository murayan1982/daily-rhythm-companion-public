import 'dart:async';
import 'dart:convert';

import 'package:app/models/framework_v600_realtime_session.dart';
import 'package:app/services/framework_v600_realtime_session_client.dart';
import 'package:app/services/framework_v600_realtime_session_controller.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;

void main() {
  group('FrameworkV600RealtimeSessionController', () {
    test('initial idle and constructor performs no request', () {
      final httpClient = _ControlledHttpClient();
      final controller = _controller(httpClient);

      expect(controller.state.phase, FrameworkV600RealtimeSessionPhase.idle);
      expect(httpClient.requests, isEmpty);

      controller.dispose();
    });

    test('open moves idle opening ready', () async {
      final httpClient = _ControlledHttpClient()..queueJson(201, _open());
      final controller = _controller(httpClient);
      final phases = _listen(controller);

      await controller.open();

      expect(phases, [
        FrameworkV600RealtimeSessionPhase.opening,
        FrameworkV600RealtimeSessionPhase.ready,
      ]);
      expect(controller.state.sessionId, _sessionId);

      controller.dispose();
    });

    test('open safe failure moves idle opening failed', () async {
      final httpClient = _ControlledHttpClient()
        ..queueJson(503, _problem('framework_unavailable'));
      final controller = _controller(httpClient);

      await controller.open();

      expect(controller.state.phase, FrameworkV600RealtimeSessionPhase.failed);
      expect(controller.state.problem!.code, 'framework_unavailable');

      controller.dispose();
    });

    test('open re-entry rejected while opening', () async {
      final openCompleter = Completer<http.StreamedResponse>();
      final httpClient = _ControlledHttpClient()
        ..queueFuture(openCompleter.future);
      final controller = _controller(httpClient);

      final firstOpen = controller.open();
      await Future<void>.delayed(Duration.zero);

      await expectLater(
        controller.open(),
        throwsA(_problemCode('session_open_not_allowed')),
      );
      expect(
        httpClient.requests
            .where(
              (request) =>
                  request.method == 'POST' &&
                  request.url.path ==
                      '/realtime/framework-v6/provider-free/sessions',
            )
            .length,
        1,
      );

      openCompleter.complete(_jsonResponse(201, _open()));
      await firstOpen;
      controller.dispose();
    });

    test('open re-entry rejected while ready keeps existing session', () async {
      final httpClient = _ControlledHttpClient()..queueJson(201, _open());
      final controller = _controller(httpClient);
      await controller.open();

      await expectLater(
        controller.open(),
        throwsA(_problemCode('session_open_not_allowed')),
      );

      expect(controller.state.phase, FrameworkV600RealtimeSessionPhase.ready);
      expect(controller.state.sessionId, _sessionId);
      expect(
        httpClient.requests
            .where((request) => request.url.path.endsWith('/sessions'))
            .length,
        1,
      );

      controller.dispose();
    });

    test('open re-entry rejected while turnRunning keeps turn state', () async {
      final turnCompleter = Completer<http.StreamedResponse>();
      final httpClient = _ControlledHttpClient()
        ..queueJson(201, _open())
        ..queueFuture(turnCompleter.future);
      final controller = _controller(httpClient);
      await controller.open();

      final turn = controller.runTurn(inputText: 'neutral input');
      await Future<void>.delayed(Duration.zero);

      await expectLater(
        controller.open(),
        throwsA(_problemCode('session_open_not_allowed')),
      );
      expect(
        controller.state.phase,
        FrameworkV600RealtimeSessionPhase.turnRunning,
      );

      turnCompleter.complete(_jsonResponse(200, _turn()));
      await turn;
      expect(controller.state.phase, FrameworkV600RealtimeSessionPhase.ready);
      expect(controller.state.sessionId, _sessionId);
      expect(
        httpClient.requests
            .where((request) => request.url.path.endsWith('/sessions'))
            .length,
        1,
      );

      controller.dispose();
    });

    test(
      'turn ready turnRunning ready and typed failed result retained',
      () async {
        final httpClient = _ControlledHttpClient()
          ..queueJson(201, _open())
          ..queueJson(200, _turn(outcome: 'failed'));
        final controller = _controller(httpClient);
        final phases = _listen(controller);

        await controller.open();
        await controller.runTurn(inputText: 'neutral input');

        expect(phases, contains(FrameworkV600RealtimeSessionPhase.turnRunning));
        expect(controller.state.phase, FrameworkV600RealtimeSessionPhase.ready);
        expect(controller.state.latestTurnResult!.outcome, 'failed');
        expect(controller.state.problem, isNull);
        expect(controller.state.toString(), isNot(contains('neutral input')));

        controller.dispose();
      },
    );

    test('second simultaneous turn rejected', () async {
      final turnCompleter = Completer<http.StreamedResponse>();
      final httpClient = _ControlledHttpClient()
        ..queueJson(201, _open())
        ..queueFuture(turnCompleter.future);
      final controller = _controller(httpClient);
      await controller.open();

      final first = controller.runTurn(inputText: 'first neutral input');
      await Future<void>.delayed(Duration.zero);

      await expectLater(
        controller.runTurn(inputText: 'second neutral input'),
        throwsA(_problemCode('turn_already_active')),
      );

      turnCompleter.complete(_jsonResponse(200, _turn()));
      await first;
      expect(controller.state.phase, FrameworkV600RealtimeSessionPhase.ready);

      controller.dispose();
    });

    test(
      'interrupt can execute during in-flight turn without corrupting phase',
      () async {
        final turnCompleter = Completer<http.StreamedResponse>();
        final httpClient = _ControlledHttpClient()
          ..queueJson(201, _open())
          ..queueFuture(turnCompleter.future)
          ..queueJson(200, _interrupt());
        final controller = _controller(httpClient);
        await controller.open();

        final turn = controller.runTurn(inputText: 'neutral input');
        await Future<void>.delayed(Duration.zero);
        final interrupt = controller.interrupt();
        await Future<void>.delayed(Duration.zero);

        expect(
          controller.state.phase,
          FrameworkV600RealtimeSessionPhase.turnRunning,
        );
        expect(controller.state.interruptInFlight, isFalse);
        expect(controller.state.latestInterruptResult!.scope, 'current_turn');

        turnCompleter.complete(_jsonResponse(200, _turn()));
        await turn;
        await interrupt;
        expect(controller.state.phase, FrameworkV600RealtimeSessionPhase.ready);

        controller.dispose();
      },
    );

    test('diagnostics lifecycle retains bounded snapshot', () async {
      final diagnosticsCompleter = Completer<http.StreamedResponse>();
      final httpClient = _ControlledHttpClient()
        ..queueJson(201, _open())
        ..queueFuture(diagnosticsCompleter.future);
      final controller = _controller(httpClient);
      await controller.open();

      final diagnostics = controller.diagnostics();
      await Future<void>.delayed(Duration.zero);
      expect(controller.state.diagnosticsInFlight, isTrue);

      diagnosticsCompleter.complete(_jsonResponse(200, _diagnostics()));
      await diagnostics;
      expect(controller.state.diagnosticsInFlight, isFalse);
      expect(controller.state.latestDiagnostics!.phase, 'ready');

      controller.dispose();
    });

    test(
      'close ready closing closed and duplicate close remains closed',
      () async {
        final httpClient = _ControlledHttpClient()
          ..queueJson(201, _open())
          ..queueText(204, '');
        final controller = _controller(httpClient);
        await controller.open();

        await controller.close();
        await controller.close();

        expect(
          controller.state.phase,
          FrameworkV600RealtimeSessionPhase.closed,
        );
        expect(
          httpClient.requests.where((request) => request.method == 'DELETE'),
          hasLength(1),
        );

        controller.dispose();
      },
    );

    test('concurrent close while ready uses single flight', () async {
      final deleteCompleter = Completer<http.StreamedResponse>();
      final httpClient = _ControlledHttpClient()
        ..queueJson(201, _open())
        ..queueFuture(deleteCompleter.future);
      final controller = _controller(httpClient);
      await controller.open();

      final closeFuture1 = controller.close();
      final closeFuture2 = controller.close();
      await Future<void>.delayed(Duration.zero);

      expect(controller.state.phase, FrameworkV600RealtimeSessionPhase.closing);
      expect(
        httpClient.requests.where((request) => request.method == 'DELETE'),
        hasLength(1),
      );

      deleteCompleter.complete(_textResponse(204, ''));
      await closeFuture1;
      await closeFuture2;

      expect(controller.state.phase, FrameworkV600RealtimeSessionPhase.closed);
      expect(
        httpClient.requests.where((request) => request.method == 'DELETE'),
        hasLength(1),
      );

      controller.dispose();
    });

    test(
      'reentrant close from closing notification uses single flight',
      () async {
        final deleteCompleter = Completer<http.StreamedResponse>();
        final httpClient = _ControlledHttpClient()
          ..queueJson(201, _open())
          ..queueFuture(deleteCompleter.future);
        final controller = _controller(httpClient);
        await controller.open();

        Future<void>? reentrantCloseFuture;
        var reentrantCloseCount = 0;
        controller.addListener(() {
          if (controller.state.phase ==
                  FrameworkV600RealtimeSessionPhase.closing &&
              reentrantCloseFuture == null) {
            reentrantCloseCount++;
            reentrantCloseFuture = controller.close();
          }
        });

        final outerCloseFuture = controller.close();
        await Future<void>.delayed(Duration.zero);

        expect(
          controller.state.phase,
          FrameworkV600RealtimeSessionPhase.closing,
        );
        expect(reentrantCloseFuture, isNotNull);
        expect(reentrantCloseCount, 1);
        expect(
          httpClient.requests.where((request) => request.method == 'DELETE'),
          hasLength(1),
        );

        deleteCompleter.complete(_textResponse(204, ''));
        await outerCloseFuture;
        await reentrantCloseFuture;

        expect(
          controller.state.phase,
          FrameworkV600RealtimeSessionPhase.closed,
        );
        expect(reentrantCloseCount, 1);
        expect(
          httpClient.requests.where((request) => request.method == 'DELETE'),
          hasLength(1),
        );

        controller.dispose();
      },
    );

    test('close during opening cleans late-created session', () async {
      final openCompleter = Completer<http.StreamedResponse>();
      final httpClient = _ControlledHttpClient()
        ..queueFuture(openCompleter.future)
        ..queueText(204, '');
      final controller = _controller(httpClient);

      final open = controller.open();
      await Future<void>.delayed(Duration.zero);
      final close = controller.close();
      await Future<void>.delayed(Duration.zero);

      openCompleter.complete(_jsonResponse(201, _open()));
      await open;
      await close;

      expect(controller.state.phase, FrameworkV600RealtimeSessionPhase.closed);
      expect(controller.state.sessionId, isNull);
      expect(controller.state.openResult, isNull);
      expect(
        httpClient.requests
            .where((request) => request.method == 'DELETE')
            .single
            .url
            .path,
        '/realtime/framework-v6/provider-free/sessions/$_sessionId',
      );

      controller.dispose();
    });

    test('concurrent close during opening uses one cleanup delete', () async {
      final openCompleter = Completer<http.StreamedResponse>();
      final cleanupCompleter = Completer<http.StreamedResponse>();
      final httpClient = _ControlledHttpClient()
        ..queueFuture(openCompleter.future)
        ..queueFuture(cleanupCompleter.future);
      final controller = _controller(httpClient);

      final openFuture = controller.open();
      await Future<void>.delayed(Duration.zero);
      final closeFuture1 = controller.close();
      final closeFuture2 = controller.close();
      await Future<void>.delayed(Duration.zero);

      openCompleter.complete(_jsonResponse(201, _open()));
      await Future<void>.delayed(Duration.zero);

      expect(
        httpClient.requests
            .where(
              (request) =>
                  request.method == 'POST' &&
                  request.url.path ==
                      '/realtime/framework-v6/provider-free/sessions',
            )
            .length,
        1,
      );
      expect(
        httpClient.requests.where((request) => request.method == 'DELETE'),
        hasLength(1),
      );
      expect(controller.state.phase, FrameworkV600RealtimeSessionPhase.closing);

      cleanupCompleter.complete(_textResponse(204, ''));
      await openFuture;
      await closeFuture1;
      await closeFuture2;

      expect(controller.state.phase, FrameworkV600RealtimeSessionPhase.closed);
      expect(controller.state.sessionId, isNull);
      expect(controller.state.openResult, isNull);
      expect(
        httpClient.requests.where((request) => request.method == 'DELETE'),
        hasLength(1),
      );

      controller.dispose();
    });

    test('close during opening cleanup failure remains closed', () async {
      final openCompleter = Completer<http.StreamedResponse>();
      final httpClient = _ControlledHttpClient()
        ..queueFuture(openCompleter.future)
        ..queueJson(503, _problem('cleanup_failed'));
      final controller = _controller(httpClient);

      final open = controller.open();
      await Future<void>.delayed(Duration.zero);
      final close = controller.close();
      await Future<void>.delayed(Duration.zero);

      openCompleter.complete(_jsonResponse(201, _open()));
      await open;
      await close;

      expect(controller.state.phase, FrameworkV600RealtimeSessionPhase.closed);
      expect(controller.state.problem!.code, 'cleanup_failed');
      expect(controller.state.sessionId, isNull);
      expect(
        httpClient.requests
            .where((request) => request.url.path.endsWith('/sessions'))
            .length,
        1,
      );

      controller.dispose();
    });

    test('concurrent close cleanup failure remains closed', () async {
      final deleteCompleter = Completer<http.StreamedResponse>();
      final httpClient = _ControlledHttpClient()
        ..queueJson(201, _open())
        ..queueFuture(deleteCompleter.future);
      final controller = _controller(httpClient);
      await controller.open();

      final closeFuture1 = controller.close();
      final closeFuture2 = controller.close();
      await Future<void>.delayed(Duration.zero);

      deleteCompleter.complete(_jsonResponse(503, _problem('cleanup_failed')));
      await closeFuture1;
      await closeFuture2;

      expect(
        httpClient.requests.where((request) => request.method == 'DELETE'),
        hasLength(1),
      );
      expect(controller.state.phase, FrameworkV600RealtimeSessionPhase.closed);
      expect(controller.state.problem!.code, 'cleanup_failed');

      controller.dispose();
    });

    test(
      'late turn diagnostics and interrupt results ignored after close',
      () async {
        for (final operation in ['turn', 'diagnostics', 'interrupt']) {
          final completer = Completer<http.StreamedResponse>();
          final httpClient = _ControlledHttpClient()..queueJson(201, _open());
          final controller = _controller(httpClient);
          await controller.open();

          Future<void> pending;
          if (operation == 'turn') {
            httpClient
              ..queueFuture(completer.future)
              ..queueText(204, '');
            pending = controller.runTurn(inputText: 'neutral input');
          } else if (operation == 'diagnostics') {
            httpClient
              ..queueFuture(completer.future)
              ..queueText(204, '');
            pending = controller.diagnostics();
          } else {
            httpClient
              ..queueFuture(completer.future)
              ..queueText(204, '');
            pending = controller.interrupt();
          }
          await Future<void>.delayed(Duration.zero);
          await controller.close();

          final lateResponse = operation == 'turn'
              ? _jsonResponse(200, _turn())
              : operation == 'diagnostics'
              ? _jsonResponse(200, _diagnostics())
              : _jsonResponse(200, _interrupt());
          completer.complete(lateResponse);
          await pending;

          expect(
            controller.state.phase,
            FrameworkV600RealtimeSessionPhase.closed,
          );
          expect(controller.state.latestTurnResult, isNull);
          expect(controller.state.latestDiagnostics, isNull);
          expect(controller.state.latestInterruptResult, isNull);
          controller.dispose();
        }
      },
    );

    test(
      'no automatic retry reopen or input retention in public problem',
      () async {
        final httpClient = _ControlledHttpClient()
          ..queueJson(201, _open())
          ..queueJson(503, _problem('turn_failed'));
        final controller = _controller(httpClient);

        await controller.open();
        await controller.runTurn(inputText: 'NEUTRAL_INPUT_SENTINEL');

        expect(
          controller.state.phase,
          FrameworkV600RealtimeSessionPhase.failed,
        );
        expect(controller.state.problem!.code, 'turn_failed');
        expect(
          controller.state.problem!.message,
          isNot(contains('NEUTRAL_INPUT_SENTINEL')),
        );
        expect(
          httpClient.requests.where((request) => request.method == 'POST'),
          hasLength(2),
        );

        controller.dispose();
      },
    );
  });
}

const _sessionId = 'fw_session_0123456789abcdef0123456789abcdef';
const _turnId = 'fw_turn_0123456789abcdef0123456789abcdef';
const _generationId = 'fw_generation_0123456789abcdef0123456789abcdef';

FrameworkV600RealtimeSessionController _controller(
  _ControlledHttpClient httpClient,
) {
  return FrameworkV600RealtimeSessionController(
    client: FrameworkV600RealtimeSessionClient(
      baseUrl: 'http://backend.local',
      client: httpClient,
    ),
  );
}

List<FrameworkV600RealtimeSessionPhase> _listen(
  FrameworkV600RealtimeSessionController controller,
) {
  final phases = <FrameworkV600RealtimeSessionPhase>[];
  controller.addListener(() => phases.add(controller.state.phase));
  return phases;
}

Matcher _problemCode(String code) =>
    isA<FrameworkV600RealtimeProblemException>().having(
      (error) => error.problem.code,
      'code',
      code,
    );

class _ControlledHttpClient extends http.BaseClient {
  final requests = <http.Request>[];
  final _responses = <Future<http.StreamedResponse>>[];

  void queueJson(int status, Map<String, Object?> body) {
    _responses.add(Future.value(_jsonResponse(status, body)));
  }

  void queueText(int status, String body) {
    _responses.add(Future.value(_textResponse(status, body)));
  }

  void queueFuture(Future<http.StreamedResponse> response) {
    _responses.add(response);
  }

  @override
  Future<http.StreamedResponse> send(http.BaseRequest request) {
    requests.add(request as http.Request);
    return _responses.removeAt(0);
  }
}

http.StreamedResponse _jsonResponse(int status, Map<String, Object?> body) {
  return _textResponse(status, jsonEncode(body));
}

http.StreamedResponse _textResponse(int status, String body) {
  return http.StreamedResponse(Stream.value(utf8.encode(body)), status);
}

Map<String, Object?> _problem(String code) => <String, Object?>{
  'detail': <String, Object?>{
    'code': code,
    'message': 'safe problem',
    'retryable': false,
  },
};

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

Map<String, Object?> _turn({String outcome = 'completed'}) => <String, Object?>{
  'schema_version': frameworkV600TurnSchema,
  'outcome': outcome,
  'terminal': true,
  'session_id': _sessionId,
  'turn_id': _turnId,
  'generation_id': _generationId,
  'public_error_code': outcome == 'failed' ? 'framework_turn_failed' : null,
  'safe_message': outcome == 'failed' ? 'safe failed turn' : '',
  'retryable': false,
  'recovery_action': 'none',
  'events': const [],
  'capabilities': _capabilities(),
  'interrupt': null,
  'diagnostics': null,
};

Map<String, Object?> _interrupt() => <String, Object?>{
  'schema_version': frameworkV600InterruptSchema,
  'outcome': 'accepted',
  'scope': 'current_turn',
  'reason': 'host_app_request',
  'provider_cancel_supported': false,
  'provider_cancel_applied': false,
  'queue_flush_supported': true,
  'queue_flush_applied': true,
  'host_playback_stop_supported': false,
  'host_playback_stop_applied': false,
  'safe_message': 'safe',
  'retryable': false,
};

Map<String, Object?> _diagnostics() => <String, Object?>{
  'schema_version': frameworkV600DiagnosticsSchema,
  'session_id': _sessionId,
  'state': 'idle',
  'phase': 'ready',
  'is_closed': false,
  'active_turn_id': null,
  'active_generation_id': null,
  'queue_depth': 0,
  'active_generation_count': 0,
  'last_terminal_event_type': null,
  'last_terminal_turn_id': null,
  'last_terminal_generation_id': null,
  'last_terminal_outcome': null,
  'last_terminal_public_error_code': null,
  'last_terminal_retryable': false,
  'last_terminal_recovery_action': null,
  'last_safe_error_code': null,
  'stale_completion_count': 0,
  'duplicate_terminal_count': 0,
  'overflow_count': 0,
};
