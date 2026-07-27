import 'package:app/services/microphone_permission.dart';
import 'package:app/services/permission_handler_microphone_permission_gateway.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:permission_handler/permission_handler.dart' as handler;

void main() {
  group('PermissionHandlerMicrophonePermissionGateway', () {
    test('check maps granted without requesting permission', () async {
      final driver = _FakePermissionHandlerDriver(
        checkStatus: handler.PermissionStatus.granted,
      );
      final gateway = _gateway(driver);

      final result = await gateway.checkPermission();

      expect(result.status, MicrophonePermissionStatus.granted);
      expect(result.operation, MicrophonePermissionOperation.check);
      expect(result.requestAttempted, isFalse);
      expect(result.publicMetadata['platform_permission_requested'], isFalse);
      expect(result.publicMetadata['microphone_accessed'], isFalse);
      expect(driver.checkCalls, 1);
      expect(driver.requestCalls, 0);
    });

    test('request maps denied and records the explicit request attempt', () async {
      final driver = _FakePermissionHandlerDriver(
        requestStatus: handler.PermissionStatus.denied,
      );
      final gateway = _gateway(driver);

      final result = await gateway.requestPermission();

      expect(result.status, MicrophonePermissionStatus.denied);
      expect(result.operation, MicrophonePermissionOperation.request);
      expect(result.requestAttempted, isTrue);
      expect(result.publicMetadata['platform_permission_requested'], isTrue);
      expect(result.publicMetadata['audio_captured'], isFalse);
      expect(driver.requestCalls, 1);
      expect(driver.checkCalls, 0);
    });

    test('permanently denied remains a settings-capable app status', () async {
      final driver = _FakePermissionHandlerDriver(
        checkStatus: handler.PermissionStatus.permanentlyDenied,
      );
      final gateway = _gateway(driver);

      final result = await gateway.checkPermission();

      expect(result.status, MicrophonePermissionStatus.permanentlyDenied);
      expect(result.canRequest, isFalse);
      expect(result.canOpenSettings, isTrue);
      expect(result.technicalCode, 'permission_handler_permanentlyDenied');
    });

    test('restricted remains distinct from an ordinary denial', () async {
      final driver = _FakePermissionHandlerDriver(
        checkStatus: handler.PermissionStatus.restricted,
      );
      final gateway = _gateway(driver);

      final result = await gateway.checkPermission();

      expect(result.status, MicrophonePermissionStatus.restricted);
      expect(result.canRequest, isFalse);
      expect(result.canOpenSettings, isFalse);
    });

    test('limited microphone result fails closed as unexpected', () async {
      final driver = _FakePermissionHandlerDriver(
        checkStatus: handler.PermissionStatus.limited,
      );
      final gateway = _gateway(driver);

      final result = await gateway.checkPermission();

      expect(result.status, MicrophonePermissionStatus.failed);
      expect(result.technicalCode, 'permission_handler_unexpected_limited');
      expect(result.publicMetadata['plugin_status'], 'limited');
    });

    test('provisional microphone result fails closed as unexpected', () async {
      final driver = _FakePermissionHandlerDriver(
        requestStatus: handler.PermissionStatus.provisional,
      );
      final gateway = _gateway(driver);

      final result = await gateway.requestPermission();

      expect(result.status, MicrophonePermissionStatus.failed);
      expect(result.technicalCode, 'permission_handler_unexpected_provisional');
      expect(result.requestAttempted, isTrue);
    });

    test('web is unsupported and never calls the plugin driver', () async {
      final driver = _FakePermissionHandlerDriver();
      final gateway = PermissionHandlerMicrophonePermissionGateway(
        driver: driver,
        platform: TargetPlatform.android,
        isWeb: true,
      );

      final check = await gateway.checkPermission();
      final request = await gateway.requestPermission();
      final settings = await gateway.openAppSettings();

      expect(check.status, MicrophonePermissionStatus.unsupported);
      expect(request.status, MicrophonePermissionStatus.unsupported);
      expect(settings.status, MicrophonePermissionStatus.unsupported);
      expect(request.requestAttempted, isFalse);
      expect(driver.totalCalls, 0);
    });

    test('desktop is unsupported and never calls the plugin driver', () async {
      final driver = _FakePermissionHandlerDriver();
      final gateway = PermissionHandlerMicrophonePermissionGateway(
        driver: driver,
        platform: TargetPlatform.windows,
        isWeb: false,
      );

      final result = await gateway.requestPermission();

      expect(result.status, MicrophonePermissionStatus.unsupported);
      expect(result.technicalCode, 'permission_handler_platform_unsupported');
      expect(driver.totalCalls, 0);
    });

    test('missing plugin is converted to a safe unsupported result', () async {
      final driver = _FakePermissionHandlerDriver(
        checkError: MissingPluginException('private platform detail'),
      );
      final gateway = _gateway(driver);

      final result = await gateway.checkPermission();

      expect(result.status, MicrophonePermissionStatus.unsupported);
      expect(result.technicalCode, 'permission_handler_plugin_unavailable');
      expect(
        result.publicMetadata.values,
        isNot(contains('private platform detail')),
      );
    });

    test('generic request failure is typed and does not expose raw error', () async {
      final driver = _FakePermissionHandlerDriver(
        requestError: StateError('sensitive native payload'),
      );
      final gateway = _gateway(driver);

      final result = await gateway.requestPermission();

      expect(result.status, MicrophonePermissionStatus.failed);
      expect(result.technicalCode, 'permission_handler_request_failed');
      expect(result.requestAttempted, isTrue);
      expect(
        result.publicMetadata.values,
        isNot(contains('sensitive native payload')),
      );
    });

    test('open settings checks status but never requests permission', () async {
      final driver = _FakePermissionHandlerDriver(
        checkStatus: handler.PermissionStatus.permanentlyDenied,
        settingsOpened: true,
      );
      final gateway = _gateway(driver);

      final result = await gateway.openAppSettings();

      expect(result.status, MicrophonePermissionStatus.permanentlyDenied);
      expect(result.operation, MicrophonePermissionOperation.openSettings);
      expect(result.technicalCode, 'permission_handler_settings_opened');
      expect(result.publicMetadata['settings_opened'], isTrue);
      expect(driver.checkCalls, 1);
      expect(driver.settingsCalls, 1);
      expect(driver.requestCalls, 0);
    });

    test('settings launch failure is typed and capture remains false', () async {
      final driver = _FakePermissionHandlerDriver(
        checkStatus: handler.PermissionStatus.permanentlyDenied,
        settingsOpened: false,
      );
      final gateway = _gateway(driver);

      final result = await gateway.openAppSettings();

      expect(result.status, MicrophonePermissionStatus.failed);
      expect(result.technicalCode, 'permission_handler_settings_not_opened');
      expect(result.publicMetadata['settings_opened'], isFalse);
      expect(result.publicMetadata['audio_captured'], isFalse);
    });

    test('settings exception is typed and does not expose raw error', () async {
      final driver = _FakePermissionHandlerDriver(
        checkStatus: handler.PermissionStatus.permanentlyDenied,
        settingsError: StateError('sensitive settings payload'),
      );
      final gateway = _gateway(driver);

      final result = await gateway.openAppSettings();

      expect(result.status, MicrophonePermissionStatus.failed);
      expect(result.technicalCode, 'permission_handler_settings_failed');
      expect(result.operation, MicrophonePermissionOperation.openSettings);
      expect(result.requestAttempted, isFalse);
      expect(result.publicMetadata['audio_captured'], isFalse);
      expect(
        result.publicMetadata.values,
        isNot(contains('sensitive settings payload')),
      );
      expect(driver.checkCalls, 1);
      expect(driver.settingsCalls, 1);
      expect(driver.requestCalls, 0);
    });
  });
}

PermissionHandlerMicrophonePermissionGateway _gateway(
  PermissionHandlerMicrophoneDriver driver,
) {
  return PermissionHandlerMicrophonePermissionGateway(
    driver: driver,
    platform: TargetPlatform.android,
    isWeb: false,
  );
}

class _FakePermissionHandlerDriver
    implements PermissionHandlerMicrophoneDriver {
  _FakePermissionHandlerDriver({
    this.checkStatus = handler.PermissionStatus.denied,
    this.requestStatus = handler.PermissionStatus.denied,
    this.settingsOpened = false,
    this.checkError,
    this.requestError,
    this.settingsError,
  });

  final handler.PermissionStatus checkStatus;
  final handler.PermissionStatus requestStatus;
  final bool settingsOpened;
  final Object? checkError;
  final Object? requestError;
  final Object? settingsError;

  int checkCalls = 0;
  int requestCalls = 0;
  int settingsCalls = 0;

  int get totalCalls => checkCalls + requestCalls + settingsCalls;

  @override
  Future<handler.PermissionStatus> checkMicrophonePermission() async {
    checkCalls += 1;
    if (checkError != null) {
      throw checkError!;
    }
    return checkStatus;
  }

  @override
  Future<handler.PermissionStatus> requestMicrophonePermission() async {
    requestCalls += 1;
    if (requestError != null) {
      throw requestError!;
    }
    return requestStatus;
  }

  @override
  Future<bool> openApplicationSettings() async {
    settingsCalls += 1;
    if (settingsError != null) {
      throw settingsError!;
    }
    return settingsOpened;
  }
}
