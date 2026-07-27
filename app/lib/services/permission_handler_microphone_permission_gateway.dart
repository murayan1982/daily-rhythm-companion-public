import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import 'package:permission_handler/permission_handler.dart' as handler;

import 'microphone_permission.dart';

/// Narrow driver around `permission_handler` so the app-owned gateway can be
/// tested without invoking an operating-system permission dialog.
abstract interface class PermissionHandlerMicrophoneDriver {
  Future<handler.PermissionStatus> checkMicrophonePermission();

  Future<handler.PermissionStatus> requestMicrophonePermission();

  Future<bool> openApplicationSettings();
}

class DefaultPermissionHandlerMicrophoneDriver
    implements PermissionHandlerMicrophoneDriver {
  const DefaultPermissionHandlerMicrophoneDriver();

  @override
  Future<handler.PermissionStatus> checkMicrophonePermission() {
    return handler.Permission.microphone.status;
  }

  @override
  Future<handler.PermissionStatus> requestMicrophonePermission() {
    return handler.Permission.microphone.request();
  }

  @override
  Future<bool> openApplicationSettings() {
    return handler.openAppSettings();
  }
}

/// Android/iOS-only implementation of the DRC-owned permission contract.
///
/// Merely constructing this gateway does not request permission or access a
/// microphone. `requestPermission` must be called from a later explicit user
/// action. RT-2c intentionally does not wire this gateway into application UI.
class PermissionHandlerMicrophonePermissionGateway
    implements MicrophonePermissionGateway {
  PermissionHandlerMicrophonePermissionGateway({
    PermissionHandlerMicrophoneDriver? driver,
    TargetPlatform? platform,
    bool? isWeb,
  })  : _driver = driver ?? const DefaultPermissionHandlerMicrophoneDriver(),
        _platform = platform ?? defaultTargetPlatform,
        _isWeb = isWeb ?? kIsWeb;

  final PermissionHandlerMicrophoneDriver _driver;
  final TargetPlatform _platform;
  final bool _isWeb;

  bool get _supportsMobilePermission =>
      !_isWeb &&
      (_platform == TargetPlatform.android ||
          _platform == TargetPlatform.iOS);

  @override
  Future<MicrophonePermissionResult> checkPermission() async {
    if (!_supportsMobilePermission) {
      return _unsupportedResult(MicrophonePermissionOperation.check);
    }

    try {
      final status = await _driver.checkMicrophonePermission();
      return _resultFromHandlerStatus(
        status: status,
        operation: MicrophonePermissionOperation.check,
        requestAttempted: false,
      );
    } on MissingPluginException {
      return _pluginUnavailableResult(MicrophonePermissionOperation.check);
    } on UnsupportedError {
      return _unsupportedResult(MicrophonePermissionOperation.check);
    } catch (_) {
      return _failedResult(
        operation: MicrophonePermissionOperation.check,
        requestAttempted: false,
        technicalCode: 'permission_handler_check_failed',
      );
    }
  }

  @override
  Future<MicrophonePermissionResult> requestPermission() async {
    if (!_supportsMobilePermission) {
      return _unsupportedResult(
        MicrophonePermissionOperation.request,
        requestAttempted: false,
      );
    }

    try {
      final status = await _driver.requestMicrophonePermission();
      return _resultFromHandlerStatus(
        status: status,
        operation: MicrophonePermissionOperation.request,
        requestAttempted: true,
      );
    } on MissingPluginException {
      return _pluginUnavailableResult(
        MicrophonePermissionOperation.request,
        requestAttempted: true,
      );
    } on UnsupportedError {
      return _unsupportedResult(
        MicrophonePermissionOperation.request,
        requestAttempted: true,
      );
    } catch (_) {
      return _failedResult(
        operation: MicrophonePermissionOperation.request,
        requestAttempted: true,
        technicalCode: 'permission_handler_request_failed',
      );
    }
  }

  @override
  Future<MicrophonePermissionResult> openAppSettings() async {
    if (!_supportsMobilePermission) {
      return _unsupportedResult(MicrophonePermissionOperation.openSettings);
    }

    try {
      final status = await _driver.checkMicrophonePermission();
      final opened = await _driver.openApplicationSettings();
      if (!opened) {
        return _failedResult(
          operation: MicrophonePermissionOperation.openSettings,
          requestAttempted: false,
          technicalCode: 'permission_handler_settings_not_opened',
          publicMetadata: <String, Object?>{
            ..._baseMetadata,
            'settings_opened': false,
            'plugin_status': status.name,
          },
        );
      }

      return _resultFromHandlerStatus(
        status: status,
        operation: MicrophonePermissionOperation.openSettings,
        requestAttempted: false,
        technicalCode: 'permission_handler_settings_opened',
        extraMetadata: const <String, Object?>{'settings_opened': true},
      );
    } on MissingPluginException {
      return _pluginUnavailableResult(
        MicrophonePermissionOperation.openSettings,
      );
    } on UnsupportedError {
      return _unsupportedResult(MicrophonePermissionOperation.openSettings);
    } catch (_) {
      return _failedResult(
        operation: MicrophonePermissionOperation.openSettings,
        requestAttempted: false,
        technicalCode: 'permission_handler_settings_failed',
      );
    }
  }

  MicrophonePermissionResult _resultFromHandlerStatus({
    required handler.PermissionStatus status,
    required MicrophonePermissionOperation operation,
    required bool requestAttempted,
    String? technicalCode,
    Map<String, Object?> extraMetadata = const <String, Object?>{},
  }) {
    final mapped = _mapStatus(status);
    final unexpected = status == handler.PermissionStatus.limited ||
        status == handler.PermissionStatus.provisional;

    return MicrophonePermissionResult.forStatus(
      status: mapped,
      operation: operation,
      requestAttempted: requestAttempted,
      technicalCode: technicalCode ??
          (unexpected
              ? 'permission_handler_unexpected_${status.name}'
              : 'permission_handler_${status.name}'),
      publicMetadata: <String, Object?>{
        ..._baseMetadata,
        'platform_permission_requested': requestAttempted,
        'plugin_status': status.name,
        ...extraMetadata,
      },
    );
  }

  MicrophonePermissionStatus _mapStatus(handler.PermissionStatus status) {
    switch (status) {
      case handler.PermissionStatus.denied:
        return MicrophonePermissionStatus.denied;
      case handler.PermissionStatus.granted:
        return MicrophonePermissionStatus.granted;
      case handler.PermissionStatus.restricted:
        return MicrophonePermissionStatus.restricted;
      case handler.PermissionStatus.permanentlyDenied:
        return MicrophonePermissionStatus.permanentlyDenied;
      case handler.PermissionStatus.limited:
      case handler.PermissionStatus.provisional:
        return MicrophonePermissionStatus.failed;
    }
  }

  MicrophonePermissionResult _unsupportedResult(
    MicrophonePermissionOperation operation, {
    bool requestAttempted = false,
  }) {
    return MicrophonePermissionResult.forStatus(
      status: MicrophonePermissionStatus.unsupported,
      operation: operation,
      requestAttempted: requestAttempted,
      technicalCode: 'permission_handler_platform_unsupported',
      publicMetadata: <String, Object?>{
        ..._baseMetadata,
        'platform_permission_requested': false,
      },
    );
  }

  MicrophonePermissionResult _pluginUnavailableResult(
    MicrophonePermissionOperation operation, {
    bool requestAttempted = false,
  }) {
    return MicrophonePermissionResult.forStatus(
      status: MicrophonePermissionStatus.unsupported,
      operation: operation,
      requestAttempted: requestAttempted,
      technicalCode: 'permission_handler_plugin_unavailable',
      publicMetadata: <String, Object?>{
        ..._baseMetadata,
        'platform_permission_requested': false,
      },
    );
  }

  MicrophonePermissionResult _failedResult({
    required MicrophonePermissionOperation operation,
    required bool requestAttempted,
    required String technicalCode,
    Map<String, Object?>? publicMetadata,
  }) {
    return MicrophonePermissionResult.forStatus(
      status: MicrophonePermissionStatus.failed,
      operation: operation,
      requestAttempted: requestAttempted,
      technicalCode: technicalCode,
      publicMetadata: publicMetadata ??
          <String, Object?>{
            ..._baseMetadata,
            'platform_permission_requested': requestAttempted,
          },
    );
  }

  Map<String, Object?> get _baseMetadata => <String, Object?>{
        'gateway': 'permission_handler',
        'permission': 'microphone',
        'platform': _isWeb ? 'web' : _platform.name,
        'microphone_accessed': false,
        'audio_captured': false,
      };
}
