import 'package:app/services/microphone_permission.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('MicrophonePermissionResult', () {
    test('unknown stays conservative and requestable', () {
      final result = MicrophonePermissionResult.forStatus(
        status: MicrophonePermissionStatus.unknown,
        operation: MicrophonePermissionOperation.check,
      );

      expect(result.isGranted, isFalse);
      expect(result.canRequest, isTrue);
      expect(result.canOpenSettings, isFalse);
      expect(result.requestAttempted, isFalse);
      expect(result.displayStatus, 'unknown');
    });

    test('granted is usable and terminal for the current request', () {
      final result = MicrophonePermissionResult.forStatus(
        status: MicrophonePermissionStatus.granted,
        operation: MicrophonePermissionOperation.request,
        requestAttempted: true,
      );

      expect(result.isGranted, isTrue);
      expect(result.isTerminalForCurrentRequest, isTrue);
      expect(result.canRequest, isFalse);
      expect(result.canOpenSettings, isFalse);
    });

    test('permanently denied points to settings without retrying permission', () {
      final result = MicrophonePermissionResult.forStatus(
        status: MicrophonePermissionStatus.permanentlyDenied,
        operation: MicrophonePermissionOperation.check,
      );

      expect(result.canRequest, isFalse);
      expect(result.canOpenSettings, isTrue);
      expect(result.displayStatus, 'permanently_denied');
    });

    test('metadata is immutable', () {
      final metadata = <String, Object?>{'source': 'test'};
      final result = MicrophonePermissionResult.forStatus(
        status: MicrophonePermissionStatus.denied,
        operation: MicrophonePermissionOperation.check,
        publicMetadata: metadata,
      );
      metadata['source'] = 'changed';

      expect(result.publicMetadata['source'], 'test');
      expect(
        () => result.publicMetadata['extra'] = true,
        throwsUnsupportedError,
      );
    });
  });

  group('FakeMicrophonePermissionGateway', () {
    test('check never requests a platform permission', () async {
      final gateway = FakeMicrophonePermissionGateway(
        initialStatus: MicrophonePermissionStatus.denied,
      );

      final result = await gateway.checkPermission();

      expect(result.status, MicrophonePermissionStatus.denied);
      expect(result.operation, MicrophonePermissionOperation.check);
      expect(result.requestAttempted, isFalse);
      expect(result.publicMetadata['platform_permission_requested'], isFalse);
      expect(gateway.checkCalls, 1);
      expect(gateway.requestCalls, 0);
    });

    test('request sequence is deterministic', () async {
      final gateway = FakeMicrophonePermissionGateway(
        initialStatus: MicrophonePermissionStatus.unknown,
        requestSequence: const <MicrophonePermissionStatus>[
          MicrophonePermissionStatus.denied,
          MicrophonePermissionStatus.granted,
        ],
      );

      final first = await gateway.requestPermission();
      final second = await gateway.requestPermission();

      expect(first.status, MicrophonePermissionStatus.denied);
      expect(second.status, MicrophonePermissionStatus.granted);
      expect(first.requestAttempted, isTrue);
      expect(second.requestAttempted, isTrue);
      expect(gateway.requestCalls, 2);
    });

    test('open settings is recorded but not executed', () async {
      final gateway = FakeMicrophonePermissionGateway(
        initialStatus: MicrophonePermissionStatus.permanentlyDenied,
      );

      final result = await gateway.openAppSettings();

      expect(result.status, MicrophonePermissionStatus.permanentlyDenied);
      expect(result.operation, MicrophonePermissionOperation.openSettings);
      expect(result.technicalCode, 'fake_settings_not_opened');
      expect(result.publicMetadata['settings_opened'], isFalse);
      expect(gateway.openSettingsCalls, 1);
    });

    test('unsupported settings path stays typed and safe', () async {
      final gateway = FakeMicrophonePermissionGateway(
        initialStatus: MicrophonePermissionStatus.permanentlyDenied,
        settingsSupported: false,
      );

      final result = await gateway.openAppSettings();

      expect(result.status, MicrophonePermissionStatus.unsupported);
      expect(result.technicalCode, 'fake_settings_unsupported');
      expect(result.canRequest, isFalse);
      expect(result.canOpenSettings, isFalse);
    });

    test('manual fake state changes do not access a microphone', () async {
      final gateway = FakeMicrophonePermissionGateway();

      gateway.setStatus(MicrophonePermissionStatus.restricted);
      final result = await gateway.checkPermission();

      expect(result.status, MicrophonePermissionStatus.restricted);
      expect(result.publicMetadata['gateway'], 'fake');
      expect(result.publicMetadata['platform_permission_requested'], isFalse);
    });
  });
}
