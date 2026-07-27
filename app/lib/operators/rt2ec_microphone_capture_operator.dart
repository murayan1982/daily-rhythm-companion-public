import 'package:flutter/material.dart';

import '../services/microphone_capture.dart';
import '../services/microphone_permission.dart';
import '../services/record_microphone_capture_engine.dart';

const Duration rt2ecOperatorMaximumCaptureDuration = Duration(seconds: 15);

const Key rt2ecOperatorAcknowledgementKey =
    Key('rt2ec-operator-acknowledgement');
const Key rt2ecOperatorActivateKey = Key('rt2ec-operator-activate');
const Key rt2ecOperatorPermissionCheckKey =
    Key('rt2ec-operator-permission-check');
const Key rt2ecOperatorPermissionRequestKey =
    Key('rt2ec-operator-permission-request');
const Key rt2ecOperatorCaptureStartKey = Key('rt2ec-operator-capture-start');
const Key rt2ecOperatorCaptureStopKey = Key('rt2ec-operator-capture-stop');
const Key rt2ecOperatorCaptureCancelKey =
    Key('rt2ec-operator-capture-cancel');

@immutable
class Rt2ecOperatorCaptureEvidence {
  const Rt2ecOperatorCaptureEvidence({
    required this.operatorTargetEnabled,
    required this.acknowledgementCompleted,
    this.permissionStatus = 'unknown',
    this.permissionRequestAttempted = false,
    this.capturePhase = 'idle',
    this.captureOutcome = 'none',
    this.technicalCode = 'none',
    this.requestedMaximumDurationMilliseconds = 15000,
    this.capturedDurationMilliseconds = 0,
    this.microphoneAccessed = false,
    this.audioCaptured = false,
    this.rawAudioExposed = false,
    this.privateArtifactRegistered = false,
    this.privateArtifactDiscarded = false,
    this.cleanupSucceeded = false,
  });

  final bool operatorTargetEnabled;
  final bool acknowledgementCompleted;
  final String permissionStatus;
  final bool permissionRequestAttempted;
  final String capturePhase;
  final String captureOutcome;
  final String technicalCode;
  final int requestedMaximumDurationMilliseconds;
  final int capturedDurationMilliseconds;
  final bool microphoneAccessed;
  final bool audioCaptured;
  final bool rawAudioExposed;
  final bool privateArtifactRegistered;
  final bool privateArtifactDiscarded;
  final bool cleanupSucceeded;

  Rt2ecOperatorCaptureEvidence copyWith({
    bool? operatorTargetEnabled,
    bool? acknowledgementCompleted,
    String? permissionStatus,
    bool? permissionRequestAttempted,
    String? capturePhase,
    String? captureOutcome,
    String? technicalCode,
    int? requestedMaximumDurationMilliseconds,
    int? capturedDurationMilliseconds,
    bool? microphoneAccessed,
    bool? audioCaptured,
    bool? rawAudioExposed,
    bool? privateArtifactRegistered,
    bool? privateArtifactDiscarded,
    bool? cleanupSucceeded,
  }) {
    return Rt2ecOperatorCaptureEvidence(
      operatorTargetEnabled:
          operatorTargetEnabled ?? this.operatorTargetEnabled,
      acknowledgementCompleted:
          acknowledgementCompleted ?? this.acknowledgementCompleted,
      permissionStatus: permissionStatus ?? this.permissionStatus,
      permissionRequestAttempted:
          permissionRequestAttempted ?? this.permissionRequestAttempted,
      capturePhase: capturePhase ?? this.capturePhase,
      captureOutcome: captureOutcome ?? this.captureOutcome,
      technicalCode: technicalCode ?? this.technicalCode,
      requestedMaximumDurationMilliseconds:
          requestedMaximumDurationMilliseconds ??
              this.requestedMaximumDurationMilliseconds,
      capturedDurationMilliseconds:
          capturedDurationMilliseconds ?? this.capturedDurationMilliseconds,
      microphoneAccessed: microphoneAccessed ?? this.microphoneAccessed,
      audioCaptured: audioCaptured ?? this.audioCaptured,
      rawAudioExposed: rawAudioExposed ?? this.rawAudioExposed,
      privateArtifactRegistered:
          privateArtifactRegistered ?? this.privateArtifactRegistered,
      privateArtifactDiscarded:
          privateArtifactDiscarded ?? this.privateArtifactDiscarded,
      cleanupSucceeded: cleanupSucceeded ?? this.cleanupSucceeded,
    );
  }

  Map<String, Object> toSafeMap() {
    return <String, Object>{
      'operator target enabled': operatorTargetEnabled,
      'acknowledgement completed': acknowledgementCompleted,
      'permission status': permissionStatus,
      'permission request attempted': permissionRequestAttempted,
      'capture phase': capturePhase,
      'capture outcome': captureOutcome,
      'technical code': technicalCode,
      'requested maximum duration': requestedMaximumDurationMilliseconds,
      'captured duration': capturedDurationMilliseconds,
      'microphone accessed': microphoneAccessed,
      'audio captured': audioCaptured,
      'raw audio exposed': rawAudioExposed,
      'private artifact registered': privateArtifactRegistered,
      'private artifact discarded': privateArtifactDiscarded,
      'cleanup succeeded': cleanupSucceeded,
    };
  }
}

class Rt2ecOperatorCaptureDependencies {
  const Rt2ecOperatorCaptureDependencies({
    required this.permissionGateway,
    required this.captureController,
    required this.privateArtifactAccess,
  });

  final MicrophonePermissionGateway permissionGateway;
  final MicrophoneCaptureController captureController;
  final RecordMicrophoneCapturePrivateArtifactAccess privateArtifactAccess;

  void dispose() {
    captureController.dispose();
  }
}

typedef Rt2ecOperatorCaptureDependenciesFactory =
    Rt2ecOperatorCaptureDependencies Function();

class Rt2ecOperatorCaptureApp extends StatelessWidget {
  const Rt2ecOperatorCaptureApp({
    required this.operatorTargetEnabled,
    required this.dependenciesFactory,
    super.key,
  });

  final bool operatorTargetEnabled;
  final Rt2ecOperatorCaptureDependenciesFactory dependenciesFactory;

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'DRC RT-2e-c operator harness',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.blueGrey),
      ),
      home: Rt2ecOperatorCaptureBootstrap(
        operatorTargetEnabled: operatorTargetEnabled,
        dependenciesFactory: dependenciesFactory,
      ),
    );
  }
}

class Rt2ecOperatorCaptureBootstrap extends StatefulWidget {
  const Rt2ecOperatorCaptureBootstrap({
    required this.operatorTargetEnabled,
    required this.dependenciesFactory,
    super.key,
  });

  final bool operatorTargetEnabled;
  final Rt2ecOperatorCaptureDependenciesFactory dependenciesFactory;

  @override
  State<Rt2ecOperatorCaptureBootstrap> createState() =>
      _Rt2ecOperatorCaptureBootstrapState();
}

class _Rt2ecOperatorCaptureBootstrapState
    extends State<Rt2ecOperatorCaptureBootstrap> {
  bool _acknowledged = false;
  bool _activationFailed = false;
  Rt2ecOperatorCaptureDependencies? _dependencies;

  @override
  void dispose() {
    _dependencies?.dispose();
    super.dispose();
  }

  void _activateHarness() {
    if (!widget.operatorTargetEnabled || !_acknowledged) {
      return;
    }
    try {
      final dependencies = widget.dependenciesFactory();
      setState(() {
        _dependencies = dependencies;
        _activationFailed = false;
      });
    } catch (_) {
      setState(() {
        _activationFailed = true;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (!widget.operatorTargetEnabled) {
      return const _Rt2ecOperatorBlockedScreen();
    }

    final dependencies = _dependencies;
    if (dependencies != null) {
      return Rt2ecOperatorCaptureHarness(dependencies: dependencies);
    }

    return Scaffold(
      appBar: AppBar(title: const Text('RT-2e-c operator opt-in')),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(20),
          children: <Widget>[
            const Text(
              'これは実デバイス確認専用の分離ハーネスです。通常アプリではありません。',
            ),
            const SizedBox(height: 12),
            CheckboxListTile(
              key: rt2ecOperatorAcknowledgementKey,
              contentPadding: EdgeInsets.zero,
              value: _acknowledged,
              onChanged: (value) {
                setState(() {
                  _acknowledged = value ?? false;
                  _activationFailed = false;
                });
              },
              title: const Text(
                '機密性のないテスト音声だけを話し、アップロードやSTTが行われないことを確認しました。',
              ),
              controlAffinity: ListTileControlAffinity.leading,
            ),
            const SizedBox(height: 12),
            FilledButton(
              key: rt2ecOperatorActivateKey,
              onPressed: _acknowledged ? _activateHarness : null,
              child: const Text('オペレーターハーネスを有効化'),
            ),
            if (_activationFailed) ...<Widget>[
              const SizedBox(height: 12),
              const Text('オペレーターハーネスを初期化できませんでした。'),
            ],
            const SizedBox(height: 24),
            const Text('operator target enabled: true'),
            Text('acknowledgement completed: $_acknowledged'),
          ],
        ),
      ),
    );
  }
}

class _Rt2ecOperatorBlockedScreen extends StatelessWidget {
  const _Rt2ecOperatorBlockedScreen();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('RT-2e-c operator target blocked')),
      body: const SafeArea(
        child: Padding(
          padding: EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: <Widget>[
              Text('operator target enabled: false'),
              SizedBox(height: 12),
              Text(
                'このターゲットは無効です。DRC_RT2EC_OPERATOR=trueを明示して起動してください。',
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class Rt2ecOperatorCaptureHarness extends StatefulWidget {
  const Rt2ecOperatorCaptureHarness({
    required this.dependencies,
    super.key,
  });

  final Rt2ecOperatorCaptureDependencies dependencies;

  @override
  State<Rt2ecOperatorCaptureHarness> createState() =>
      _Rt2ecOperatorCaptureHarnessState();
}

class _Rt2ecOperatorCaptureHarnessState
    extends State<Rt2ecOperatorCaptureHarness> {
  late Rt2ecOperatorCaptureEvidence _evidence;
  MicrophonePermissionResult? _permissionResult;
  bool _operationInFlight = false;
  String _safeStatus = '権限確認、権限要求、録音開始を明示的に操作してください。';

  MicrophoneCaptureController get _captureController =>
      widget.dependencies.captureController;

  @override
  void initState() {
    super.initState();
    _evidence = const Rt2ecOperatorCaptureEvidence(
      operatorTargetEnabled: true,
      acknowledgementCompleted: true,
    );
    _captureController.addListener(_syncCaptureState);
  }

  @override
  void dispose() {
    _captureController.removeListener(_syncCaptureState);
    super.dispose();
  }

  Future<void> _checkPermission() async {
    if (_operationInFlight || _captureController.state.isActive) {
      return;
    }
    _setOperationInFlight(true);
    try {
      final result = await widget.dependencies.permissionGateway.checkPermission();
      _applyPermissionResult(result);
    } catch (_) {
      _setSafeFailure('operator_permission_check_failed');
    } finally {
      _setOperationInFlight(false);
    }
  }

  Future<void> _requestPermission() async {
    if (_operationInFlight || _captureController.state.isActive) {
      return;
    }
    _setOperationInFlight(true);
    try {
      final result =
          await widget.dependencies.permissionGateway.requestPermission();
      _applyPermissionResult(result);
    } catch (_) {
      _setSafeFailure('operator_permission_request_failed');
    } finally {
      _setOperationInFlight(false);
    }
  }

  Future<void> _startCapture() async {
    if (_operationInFlight || _permissionResult?.isGranted != true) {
      return;
    }
    _setOperationInFlight(true);
    if (mounted) {
      setState(() {
        _evidence = _evidence.copyWith(
          captureOutcome: 'none',
          technicalCode: 'none',
          requestedMaximumDurationMilliseconds:
              rt2ecOperatorMaximumCaptureDuration.inMilliseconds,
          capturedDurationMilliseconds: 0,
          microphoneAccessed: false,
          audioCaptured: false,
          rawAudioExposed: false,
          privateArtifactRegistered: false,
          privateArtifactDiscarded: false,
          cleanupSucceeded: false,
        );
      });
    }
    try {
      await _captureController.start(
        MicrophoneCaptureRequest(
          maxDuration: rt2ecOperatorMaximumCaptureDuration,
          publicMetadata: const <String, Object?>{
            'operator_target': 'rt2ec',
          },
        ),
      );
    } catch (_) {
      _setSafeFailure('operator_capture_start_failed');
    } finally {
      _setOperationInFlight(false);
    }
  }

  Future<void> _stopCapture() async {
    if (_operationInFlight || !_captureController.state.canStop) {
      return;
    }
    _setOperationInFlight(true);
    try {
      final result = await _captureController.stop();
      if (result.isCompleted && result.engineResult != null) {
        var discarded = false;
        try {
          discarded = await widget.dependencies.privateArtifactAccess
              .discardPrivateArtifact(
            result.engineResult!.opaqueCaptureId,
          );
        } catch (_) {
          discarded = false;
        }
        if (mounted) {
          setState(() {
            _evidence = _evidence.copyWith(
              privateArtifactDiscarded: discarded,
              cleanupSucceeded: discarded,
              technicalCode: discarded
                  ? result.technicalCode
                  : 'operator_private_artifact_discard_failed',
            );
            _safeStatus = discarded
                ? '録音を停止し、private artifactを削除しました。'
                : '録音停止後のprivate artifact削除に失敗しました。';
          });
        }
      }
    } catch (_) {
      _setSafeFailure('operator_capture_stop_failed');
    } finally {
      _setOperationInFlight(false);
    }
  }

  Future<void> _cancelCapture() async {
    if (_operationInFlight || !_captureController.state.canCancel) {
      return;
    }
    _setOperationInFlight(true);
    try {
      await _captureController.cancel();
    } catch (_) {
      _setSafeFailure('operator_capture_cancel_failed');
    } finally {
      _setOperationInFlight(false);
    }
  }

  void _applyPermissionResult(MicrophonePermissionResult result) {
    if (!mounted) {
      return;
    }
    setState(() {
      _permissionResult = result;
      _safeStatus = result.safeMessage;
      _evidence = _evidence.copyWith(
        permissionStatus: result.status.name,
        permissionRequestAttempted: result.requestAttempted,
        technicalCode: result.technicalCode ?? result.status.name,
      );
    });
  }

  void _syncCaptureState() {
    if (!mounted) {
      return;
    }
    final state = _captureController.state;
    final result = state.lastResult;
    final resultMetadata = result?.publicMetadata ?? const <String, Object?>{};
    final engineMetadata =
        result?.engineResult?.publicMetadata ?? const <String, Object?>{};
    setState(() {
      _safeStatus = state.safeMessage;
      _evidence = _evidence.copyWith(
        capturePhase: state.displayPhase,
        captureOutcome: result?.outcome.name ?? _evidence.captureOutcome,
        technicalCode:
            result?.technicalCode ?? state.technicalCode ?? _evidence.technicalCode,
        requestedMaximumDurationMilliseconds:
            state.requestedMaxDuration?.inMilliseconds ??
                _evidence.requestedMaximumDurationMilliseconds,
        capturedDurationMilliseconds:
            result?.engineResult?.capturedDuration.inMilliseconds ??
                _evidence.capturedDurationMilliseconds,
        microphoneAccessed:
            resultMetadata['microphone_accessed'] == true ||
                engineMetadata['microphone_accessed'] == true,
        audioCaptured: resultMetadata['audio_captured'] == true ||
            engineMetadata['audio_captured'] == true,
        rawAudioExposed: resultMetadata['raw_audio_exposed'] == true ||
            engineMetadata['raw_audio_exposed'] == true,
        privateArtifactRegistered:
            resultMetadata['private_artifact_registered'] == true ||
                engineMetadata['private_artifact_registered'] == true,
        cleanupSucceeded: resultMetadata.containsKey('cleanup_succeeded')
            ? resultMetadata['cleanup_succeeded'] == true
            : _evidence.cleanupSucceeded,
      );
    });
  }

  void _setSafeFailure(String technicalCode) {
    if (!mounted) {
      return;
    }
    setState(() {
      _safeStatus = 'オペレーター操作に失敗しました。';
      _evidence = _evidence.copyWith(
        technicalCode: technicalCode,
        cleanupSucceeded: false,
      );
    });
  }

  void _setOperationInFlight(bool value) {
    if (!mounted) {
      return;
    }
    setState(() {
      _operationInFlight = value;
    });
  }

  @override
  Widget build(BuildContext context) {
    final captureState = _captureController.state;
    final canUsePermissionActions =
        !_operationInFlight && !captureState.isActive;
    final canStart = !_operationInFlight &&
        _permissionResult?.isGranted == true &&
        captureState.canStart;
    final canStop = !_operationInFlight && captureState.canStop;
    final canCancel = !_operationInFlight && captureState.canCancel;

    return Scaffold(
      appBar: AppBar(title: const Text('RT-2e-c microphone operator')),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(20),
          children: <Widget>[
            const Text(
              '明示操作専用です。音声はアップロードされず、STTも実行されません。',
            ),
            const SizedBox(height: 12),
            Text(_safeStatus, key: const Key('rt2ec-operator-safe-status')),
            const SizedBox(height: 16),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: <Widget>[
                OutlinedButton(
                  key: rt2ecOperatorPermissionCheckKey,
                  onPressed:
                      canUsePermissionActions ? _checkPermission : null,
                  child: const Text('権限を確認'),
                ),
                OutlinedButton(
                  key: rt2ecOperatorPermissionRequestKey,
                  onPressed:
                      canUsePermissionActions ? _requestPermission : null,
                  child: const Text('権限を要求'),
                ),
                FilledButton(
                  key: rt2ecOperatorCaptureStartKey,
                  onPressed: canStart ? _startCapture : null,
                  child: const Text('録音を開始'),
                ),
                FilledButton.tonal(
                  key: rt2ecOperatorCaptureStopKey,
                  onPressed: canStop ? _stopCapture : null,
                  child: const Text('録音を停止'),
                ),
                OutlinedButton(
                  key: rt2ecOperatorCaptureCancelKey,
                  onPressed: canCancel ? _cancelCapture : null,
                  child: const Text('キャンセル'),
                ),
              ],
            ),
            const SizedBox(height: 24),
            const Text(
              'Safe evidence',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            _Rt2ecSafeEvidencePanel(evidence: _evidence),
          ],
        ),
      ),
    );
  }
}

class _Rt2ecSafeEvidencePanel extends StatelessWidget {
  const _Rt2ecSafeEvidencePanel({required this.evidence});

  final Rt2ecOperatorCaptureEvidence evidence;

  @override
  Widget build(BuildContext context) {
    final entries = evidence.toSafeMap().entries.toList(growable: false);
    return Column(
      key: const Key('rt2ec-operator-safe-evidence'),
      crossAxisAlignment: CrossAxisAlignment.start,
      children: entries
          .map(
            (entry) => Text('${entry.key}: ${entry.value}'),
          )
          .toList(growable: false),
    );
  }
}
