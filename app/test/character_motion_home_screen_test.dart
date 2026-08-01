import 'dart:async';

import 'package:app/models/character_motion_presentation.dart';
import 'package:app/models/character_preset.dart';
import 'package:app/models/demo_status.dart';
import 'package:app/models/sleep_provider_selection.dart';
import 'package:app/models/sleep_summary.dart';
import 'package:app/screens/home_screen.dart';
import 'package:app/services/backend_api_client.dart';
import 'package:app/services/character_motion_presentation_client.dart';
import 'package:app/services/character_motion_presentation_controller.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('normal HomeScreen is unconfigured and performs no motion call', (
    tester,
  ) async {
    await _pumpHome(tester);

    expect(
      find.byKey(const ValueKey('character-motion-presentation-section')),
      findsOneWidget,
    );
    expect(
      _detailText(tester, 'character-motion-configuration'),
      'unconfigured',
    );
    expect(_detailText(tester, 'character-motion-opt-in-status'), 'off');
    expect(_button(tester, 'character-motion-apply-button').enabled, isFalse);
    expect(
      find.byKey(const Key('character-display-static-baseline')),
      findsOne,
    );
  });

  testWidgets(
    'factory is called once and configured state remains default-off',
    (tester) async {
      var factoryCalls = 0;
      final transport = _RecordingTransport();

      await _pumpHome(
        tester,
        controllerFactory: () {
          factoryCalls += 1;
          return _controller(transport.call);
        },
      );

      expect(factoryCalls, 1);
      expect(
        _detailText(tester, 'character-motion-configuration'),
        'configured',
      );
      expect(_detailText(tester, 'character-motion-opt-in-status'), 'off');
      expect(transport.calls, 0);
      expect(_button(tester, 'character-motion-apply-button').enabled, isFalse);
    },
  );

  testWidgets('factory failure becomes configuration_failed', (tester) async {
    await _pumpHome(
      tester,
      controllerFactory: () => throw StateError('private factory detail'),
    );

    expect(
      _detailText(tester, 'character-motion-configuration'),
      'configuration_failed',
    );
    expect(find.textContaining('private factory detail'), findsNothing);
    expect(_switch(tester).onChanged, isNull);
  });

  testWidgets('opt-in alone performs zero transport calls', (tester) async {
    final transport = _RecordingTransport();
    await _pumpConfigured(tester, transport);

    await _setOptIn(tester, true);

    expect(_detailText(tester, 'character-motion-opt-in-status'), 'on');
    expect(transport.calls, 0);
    expect(_button(tester, 'character-motion-apply-button').enabled, isTrue);
  });

  testWidgets('all accepted lifecycle facts are available', (tester) async {
    final transport = _RecordingTransport();
    await _pumpConfigured(tester, transport);
    await _setOptIn(tester, true);

    final fieldFinder = find.byKey(
      const ValueKey('character-motion-lifecycle-fact'),
    );
    expect(fieldFinder, findsOneWidget);

    final dropdownFinder = find.descendant(
      of: fieldFinder,
      matching: find.byType(DropdownButton<CharacterMotionLifecycleFact>),
    );
    expect(dropdownFinder, findsOneWidget);

    final dropdown = tester
        .widget<DropdownButton<CharacterMotionLifecycleFact>>(dropdownFinder);

    final itemValues = dropdown.items!
        .map((item) => item.value)
        .whereType<CharacterMotionLifecycleFact>()
        .toList();

    expect(itemValues, orderedEquals(CharacterMotionLifecycleFact.values));
    expect(transport.requests, isEmpty);
  });

  testWidgets('explicit apply sends one bounded manual request', (
    tester,
  ) async {
    final transport = _RecordingTransport();
    await _pumpConfigured(tester, transport);
    await _setOptIn(tester, true);
    await _selectFact(tester, CharacterMotionLifecycleFact.speaking);

    await _press(tester, 'character-motion-apply-button');
    await tester.pumpAndSettle();

    expect(transport.calls, 1);
    final request = transport.requests.single;
    expect(request.sourceFact, CharacterMotionLifecycleFact.speaking);
    expect(request.sourceEventType, 'home_screen_manual_motion');
    expect(request.characterId, 'gentle_mina');
    expect(request.sourceSessionId, isNull);
    expect(request.sourceTurnId, isNull);
    expect(_detailText(tester, 'character-motion-phase'), 'completed');
    expect(_detailText(tester, 'character-motion-cue'), 'speaking');
  });

  for (final entry in <CharacterMotionExecutionStatus, String>{
    CharacterMotionExecutionStatus.completed: 'completed',
    CharacterMotionExecutionStatus.ignored: 'ignored',
    CharacterMotionExecutionStatus.disabled: 'disabled',
    CharacterMotionExecutionStatus.unavailable: 'unavailable',
    CharacterMotionExecutionStatus.failed: 'failed',
  }.entries) {
    testWidgets('${entry.key.wireName} normalized state is visible safely', (
      tester,
    ) async {
      final transport = _RecordingTransport(status: entry.key);
      await _pumpConfigured(tester, transport);
      await _setOptIn(tester, true);

      await _press(tester, 'character-motion-apply-button');
      await tester.pumpAndSettle();

      expect(_detailText(tester, 'character-motion-phase'), entry.value);
      expect(
        _detailText(tester, 'character-motion-execution-status'),
        entry.key.wireName,
      );
      if (entry.key == CharacterMotionExecutionStatus.failed) {
        expect(
          _detailText(tester, 'character-motion-safe-message'),
          'Safe motion failure.',
        );
      }
    });
  }

  testWidgets('duplicate apply is disabled while one request is active', (
    tester,
  ) async {
    final completer = Completer<Map<String, Object?>>();
    final transport = _RecordingTransport(completer: completer);
    await _pumpConfigured(tester, transport);
    await _setOptIn(tester, true);

    await _press(tester, 'character-motion-apply-button', settle: false);
    await tester.pump();

    expect(transport.calls, 1);
    expect(_detailText(tester, 'character-motion-phase'), 'applying');
    expect(_button(tester, 'character-motion-apply-button').enabled, isFalse);

    completer.complete(_result());
    await tester.pumpAndSettle();
    expect(_detailText(tester, 'character-motion-phase'), 'completed');
  });

  testWidgets('reset is local and performs no extra transport call', (
    tester,
  ) async {
    final transport = _RecordingTransport();
    await _pumpConfigured(tester, transport);
    await _setOptIn(tester, true);
    await _press(tester, 'character-motion-apply-button');
    await tester.pumpAndSettle();

    expect(transport.calls, 1);
    await _press(tester, 'character-motion-reset-button');

    expect(transport.calls, 1);
    expect(_detailText(tester, 'character-motion-phase'), 'idle');
    expect(_detailText(tester, 'character-motion-execution-status'), '-');
  });

  testWidgets('opt-out invalidates a delayed completion', (tester) async {
    final completer = Completer<Map<String, Object?>>();
    final transport = _RecordingTransport(completer: completer);
    await _pumpConfigured(tester, transport);
    await _setOptIn(tester, true);
    await _press(tester, 'character-motion-apply-button', settle: false);
    await tester.pump();

    await _setOptIn(tester, false);
    expect(_detailText(tester, 'character-motion-phase'), 'idle');

    completer.complete(_result());
    await tester.pumpAndSettle();
    expect(_detailText(tester, 'character-motion-phase'), 'idle');
    expect(_detailText(tester, 'character-motion-opt-in-status'), 'off');
    expect(transport.calls, 1);
  });

  testWidgets(
    'controller is disposed exactly once and late result is ignored',
    (tester) async {
      final completer = Completer<Map<String, Object?>>();
      final transport = _RecordingTransport(completer: completer);
      late _TrackingController controller;

      await _pumpHome(
        tester,
        controllerFactory: () {
          controller = _TrackingController(
            client: CharacterMotionPresentationClient(
              transport: transport.call,
            ),
          );
          return controller;
        },
      );
      await _setOptIn(tester, true);
      await _press(tester, 'character-motion-apply-button', settle: false);
      await tester.pump();

      await tester.pumpWidget(const MaterialApp(home: SizedBox.shrink()));
      await tester.pump();
      expect(controller.disposeCalls, 1);

      completer.complete(_result());
      await tester.pump();
      expect(controller.disposeCalls, 1);
    },
  );

  testWidgets(
    'panel hides raw IDs, command details, event strings and errors',
    (tester) async {
      const privateText = 'private-token-provider-payload';
      final controller = _controller(
        (_) async => throw StateError(privateText),
      );
      await _pumpHome(tester, controllerFactory: () => controller);
      await _setOptIn(tester, true);
      await _press(tester, 'character-motion-apply-button');
      await tester.pumpAndSettle();

      expect(_detailText(tester, 'character-motion-phase'), 'failed');
      expect(
        _detailText(tester, 'character-motion-safe-message'),
        'The character-motion presentation request failed.',
      );
      expect(find.textContaining(privateText), findsNothing);
      expect(find.textContaining('session-private'), findsNothing);
      expect(find.textContaining('turn-private'), findsNothing);
      expect(find.textContaining('motion_applied_private'), findsNothing);
      expect(find.textContaining('reset_expression'), findsNothing);
      expect(
        find.byKey(const ValueKey('character-motion-static-safety-note')),
        findsOneWidget,
      );
      expect(
        find.byKey(const Key('character-display-static-baseline')),
        findsOne,
      );
    },
  );
}

Future<void> _pumpConfigured(
  WidgetTester tester,
  _RecordingTransport transport,
) => _pumpHome(tester, controllerFactory: () => _controller(transport.call));

Future<void> _pumpHome(
  WidgetTester tester, {
  CharacterMotionPresentationController Function()? controllerFactory,
}) async {
  await tester.pumpWidget(
    MaterialApp(
      home: HomeScreen(
        apiClient: const _FakeBackendApiClient(),
        characterMotionPresentationControllerFactory: controllerFactory,
      ),
    ),
  );
  await tester.pumpAndSettle();
}

Future<void> _setOptIn(WidgetTester tester, bool value) async {
  final callback = _switch(tester).onChanged;
  expect(callback, isNotNull);
  callback!(value);
  await tester.pump();
}

Future<void> _selectFact(
  WidgetTester tester,
  CharacterMotionLifecycleFact fact,
) async {
  final dropdown = tester
      .widget<DropdownButtonFormField<CharacterMotionLifecycleFact>>(
        find.byKey(const ValueKey('character-motion-lifecycle-fact')),
      );
  expect(dropdown.onChanged, isNotNull);
  dropdown.onChanged!(fact);
  await tester.pump();
}

Future<void> _press(
  WidgetTester tester,
  String key, {
  bool settle = true,
}) async {
  final callback = _button(tester, key).onPressed;
  expect(callback, isNotNull);
  callback!();
  if (settle) {
    await tester.pumpAndSettle();
  }
}

SwitchListTile _switch(WidgetTester tester) => tester.widget<SwitchListTile>(
  find.byKey(const ValueKey('character-motion-opt-in')),
);

ButtonStyleButton _button(WidgetTester tester, String key) =>
    tester.widget<ButtonStyleButton>(find.byKey(ValueKey(key)));

String _detailText(WidgetTester tester, String key) {
  final row = find.byKey(ValueKey(key));
  final texts = tester
      .widgetList<Text>(find.descendant(of: row, matching: find.byType(Text)))
      .map((widget) => widget.data)
      .whereType<String>()
      .toList();
  return texts.last;
}

CharacterMotionPresentationController _controller(
  CharacterMotionPresentationTransport transport,
) => CharacterMotionPresentationController(
  client: CharacterMotionPresentationClient(transport: transport),
);

class _TrackingController extends CharacterMotionPresentationController {
  _TrackingController({required super.client});

  var disposeCalls = 0;

  @override
  void dispose() {
    disposeCalls += 1;
    super.dispose();
  }
}

class _RecordingTransport {
  _RecordingTransport({
    this.status = CharacterMotionExecutionStatus.completed,
    this.completer,
  });

  final CharacterMotionExecutionStatus status;
  final Completer<Map<String, Object?>>? completer;
  final List<CharacterMotionPresentationRequest> requests = [];

  int get calls => requests.length;

  Future<Map<String, Object?>> call(
    CharacterMotionPresentationRequest request,
  ) async {
    requests.add(request);
    if (completer != null) {
      return completer!.future;
    }
    return _result(status: status, sourceFact: request.sourceFact);
  }
}

Map<String, Object?> _result({
  CharacterMotionExecutionStatus status =
      CharacterMotionExecutionStatus.completed,
  CharacterMotionLifecycleFact sourceFact = CharacterMotionLifecycleFact.idle,
}) {
  final inactive =
      status == CharacterMotionExecutionStatus.ignored ||
      status == CharacterMotionExecutionStatus.disabled;
  final completed = status == CharacterMotionExecutionStatus.completed;
  final cue = switch (sourceFact) {
    CharacterMotionLifecycleFact.speaking => 'speaking',
    CharacterMotionLifecycleFact.thinking => 'thinking',
    _ => 'idle',
  };
  return <String, Object?>{
    'schema_version': 'drc.v3.framework-mock-motion-execution.1',
    'status': status.wireName,
    'source_fact': sourceFact.wireName,
    'cue': inactive ? null : cue,
    'source_event_type': 'home_screen_manual_motion',
    'source_session_id': 'session-private',
    'source_turn_id': 'turn-private',
    'character_id': 'gentle_mina',
    'commands_requested': inactive ? 0 : 1,
    'commands_completed': completed ? 1 : 0,
    'command_results': inactive
        ? <Object?>[]
        : <Object?>[
            _command(
              retryable: status == CharacterMotionExecutionStatus.failed,
            ),
          ],
    'event_types': inactive ? <String>[] : <String>['motion_applied_private'],
    'framework_import_attempted': !inactive,
    'session_created': !inactive,
    'session_closed': !inactive,
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

Map<String, Object?> _command({bool retryable = false}) => <String, Object?>{
  'order': 1,
  'intent': 'reset_expression',
  'outcome': 'completed',
  'state': 'idle',
  'adapter_status': 'ready',
  'public_error_code': '',
  'retryable': retryable,
  'safe_message': '',
};

class _FakeBackendApiClient extends BackendApiClient {
  const _FakeBackendApiClient() : super(baseUrl: 'http://backend.test');

  @override
  Future<String> fetchHealthStatus() async => 'ok / API v2.1.0';

  @override
  Future<List<CharacterPreset>> fetchCharacters() async =>
      const <CharacterPreset>[
        CharacterPreset(
          characterId: 'gentle_mina',
          displayName: 'Mina',
          description: 'Gentle test character',
          personalityType: 'gentle',
          speakingStyle: 'casual',
          adviceStyle: 'rest_focused',
        ),
      ];

  @override
  Future<SleepSummary> fetchSleepSummary() async => const SleepSummary(
    date: '2026-08-01',
    totalSleepMinutes: 420,
    efficiency: 88,
    deepSleepMinutes: 80,
    remSleepMinutes: 90,
    awakeMinutes: 20,
    source: 'mock',
    available: true,
  );

  @override
  Future<SleepProviderSelectionStatus>
  fetchSleepProviderSelectionStatus() async =>
      const SleepProviderSelectionStatus(
        configuredProvider: 'mock',
        configuredProviderLabel: 'Mock',
        configuredProviderRole: 'credential_free_default',
        configuredProviderSupported: true,
        selectionMode: 'backend_config',
        changeRequiresBackendRestart: true,
        availableProviders: <SleepProviderOption>[],
        message: 'Mock provider selected.',
      );

  @override
  Future<DemoStatus> fetchDemoStatus() async => const DemoStatus(
    engine: 'mock',
    mode: 'mock_safe',
    capabilities: <String, DemoCapabilityStatus>{
      'llm_response': DemoCapabilityStatus(
        status: 'unavailable',
        source: 'mock',
        message: 'LLM unavailable.',
      ),
      'voice_input': DemoCapabilityStatus(
        status: 'unavailable',
        source: 'not_implemented',
        message: 'Voice input unavailable.',
      ),
      'voice_output': DemoCapabilityStatus(
        status: 'unavailable',
        source: 'not_implemented',
        message: 'Voice output unavailable.',
      ),
      'live2d_motion': DemoCapabilityStatus(
        status: 'unavailable',
        source: 'not_implemented',
        message: 'Motion unavailable.',
      ),
    },
  );
}
