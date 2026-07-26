/// App-owned microphone permission contract used before any platform plugin is
/// introduced.
///
/// This file deliberately contains no platform channel, microphone, capture,
/// provider, or Framework integration. The fake gateway is deterministic and
/// safe for unit tests and future UI state wiring.
enum MicrophonePermissionStatus {
  unknown,
  granted,
  denied,
  permanentlyDenied,
  restricted,
  unsupported,
  failed,
}

enum MicrophonePermissionOperation {
  check,
  request,
  openSettings,
}

class MicrophonePermissionResult {
  MicrophonePermissionResult({
    required this.status,
    required this.operation,
    required this.safeMessage,
    required this.canRequest,
    required this.canOpenSettings,
    required this.requestAttempted,
    this.technicalCode,
    Map<String, Object?> publicMetadata = const <String, Object?>{},
  }) : publicMetadata = Map<String, Object?>.unmodifiable(publicMetadata);

  factory MicrophonePermissionResult.forStatus({
    required MicrophonePermissionStatus status,
    required MicrophonePermissionOperation operation,
    bool requestAttempted = false,
    String? technicalCode,
    Map<String, Object?> publicMetadata = const <String, Object?>{},
  }) {
    return MicrophonePermissionResult(
      status: status,
      operation: operation,
      safeMessage: _safeMessageFor(status),
      canRequest: _canRequestFor(status),
      canOpenSettings: _canOpenSettingsFor(status),
      requestAttempted: requestAttempted,
      technicalCode: technicalCode ?? status.name,
      publicMetadata: publicMetadata,
    );
  }

  final MicrophonePermissionStatus status;
  final MicrophonePermissionOperation operation;
  final String safeMessage;
  final bool canRequest;
  final bool canOpenSettings;
  final bool requestAttempted;
  final String? technicalCode;
  final Map<String, Object?> publicMetadata;

  bool get isGranted => status == MicrophonePermissionStatus.granted;

  bool get isTerminalForCurrentRequest =>
      status == MicrophonePermissionStatus.granted ||
      status == MicrophonePermissionStatus.permanentlyDenied ||
      status == MicrophonePermissionStatus.restricted ||
      status == MicrophonePermissionStatus.unsupported ||
      status == MicrophonePermissionStatus.failed;

  String get displayStatus => status.name.replaceAllMapped(
        RegExp(r'([A-Z])'),
        (match) => '_${match.group(1)!.toLowerCase()}',
      );

  static bool _canRequestFor(MicrophonePermissionStatus status) {
    return status == MicrophonePermissionStatus.unknown ||
        status == MicrophonePermissionStatus.denied;
  }

  static bool _canOpenSettingsFor(MicrophonePermissionStatus status) {
    return status == MicrophonePermissionStatus.permanentlyDenied;
  }

  static String _safeMessageFor(MicrophonePermissionStatus status) {
    switch (status) {
      case MicrophonePermissionStatus.unknown:
        return 'マイクの利用許可はまだ確認されていません。';
      case MicrophonePermissionStatus.granted:
        return 'マイクの利用が許可されています。';
      case MicrophonePermissionStatus.denied:
        return 'マイクの利用が許可されませんでした。';
      case MicrophonePermissionStatus.permanentlyDenied:
        return 'マイクの利用が無効です。端末設定から許可してください。';
      case MicrophonePermissionStatus.restricted:
        return 'この端末ではマイクの利用が制限されています。';
      case MicrophonePermissionStatus.unsupported:
        return 'この環境ではマイク権限を利用できません。';
      case MicrophonePermissionStatus.failed:
        return 'マイク権限の確認に失敗しました。';
    }
  }
}

abstract interface class MicrophonePermissionGateway {
  Future<MicrophonePermissionResult> checkPermission();

  Future<MicrophonePermissionResult> requestPermission();

  Future<MicrophonePermissionResult> openAppSettings();
}

/// Deterministic in-memory gateway for tests and pre-platform UI wiring.
///
/// It never requests an operating-system permission and never opens settings.
class FakeMicrophonePermissionGateway implements MicrophonePermissionGateway {
  FakeMicrophonePermissionGateway({
    MicrophonePermissionStatus initialStatus =
        MicrophonePermissionStatus.unknown,
    Iterable<MicrophonePermissionStatus> requestSequence =
        const <MicrophonePermissionStatus>[],
    this.settingsSupported = true,
  })  : _status = initialStatus,
        _requestSequence = List<MicrophonePermissionStatus>.of(requestSequence);

  MicrophonePermissionStatus _status;
  final List<MicrophonePermissionStatus> _requestSequence;
  final bool settingsSupported;

  int checkCalls = 0;
  int requestCalls = 0;
  int openSettingsCalls = 0;

  MicrophonePermissionStatus get currentStatus => _status;

  void setStatus(MicrophonePermissionStatus status) {
    _status = status;
  }

  @override
  Future<MicrophonePermissionResult> checkPermission() async {
    checkCalls += 1;
    return MicrophonePermissionResult.forStatus(
      status: _status,
      operation: MicrophonePermissionOperation.check,
      publicMetadata: const <String, Object?>{
        'gateway': 'fake',
        'platform_permission_requested': false,
      },
    );
  }

  @override
  Future<MicrophonePermissionResult> requestPermission() async {
    requestCalls += 1;
    if (_requestSequence.isNotEmpty) {
      _status = _requestSequence.removeAt(0);
    }
    return MicrophonePermissionResult.forStatus(
      status: _status,
      operation: MicrophonePermissionOperation.request,
      requestAttempted: true,
      publicMetadata: const <String, Object?>{
        'gateway': 'fake',
        'platform_permission_requested': false,
      },
    );
  }

  @override
  Future<MicrophonePermissionResult> openAppSettings() async {
    openSettingsCalls += 1;
    if (!settingsSupported) {
      return MicrophonePermissionResult.forStatus(
        status: MicrophonePermissionStatus.unsupported,
        operation: MicrophonePermissionOperation.openSettings,
        technicalCode: 'fake_settings_unsupported',
        publicMetadata: const <String, Object?>{
          'gateway': 'fake',
          'settings_opened': false,
        },
      );
    }
    return MicrophonePermissionResult.forStatus(
      status: _status,
      operation: MicrophonePermissionOperation.openSettings,
      technicalCode: 'fake_settings_not_opened',
      publicMetadata: const <String, Object?>{
        'gateway': 'fake',
        'settings_opened': false,
      },
    );
  }
}
