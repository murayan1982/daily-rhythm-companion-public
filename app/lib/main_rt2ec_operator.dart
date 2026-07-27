import 'package:flutter/material.dart';

import 'operators/rt2ec_microphone_capture_operator.dart';
import 'services/microphone_capture.dart';
import 'services/permission_handler_microphone_permission_gateway.dart';
import 'services/record_microphone_capture_engine.dart';

const bool kRt2ecOperatorTargetEnabled = bool.fromEnvironment(
  'DRC_RT2EC_OPERATOR',
  defaultValue: false,
);

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(
    Rt2ecOperatorCaptureApp(
      operatorTargetEnabled: kRt2ecOperatorTargetEnabled,
      dependenciesFactory: _createProductionDependencies,
    ),
  );
}

Rt2ecOperatorCaptureDependencies _createProductionDependencies() {
  final permissionGateway = PermissionHandlerMicrophonePermissionGateway();
  final captureEngine = RecordMicrophoneCaptureEngine.mobile();
  final captureController = MicrophoneCaptureController(
    permissionGateway: permissionGateway,
    engine: captureEngine,
    maximumAllowedDuration: rt2ecOperatorMaximumCaptureDuration,
  );
  return Rt2ecOperatorCaptureDependencies(
    permissionGateway: permissionGateway,
    captureController: captureController,
    privateArtifactAccess: captureEngine,
  );
}
