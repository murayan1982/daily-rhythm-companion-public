import 'package:flutter/foundation.dart';

import '../models/framework_vts_motion_presentation.dart';
import 'framework_vts_motion_presentation_client.dart';

class FrameworkVtsMotionPresentationController extends ChangeNotifier {
  FrameworkVtsMotionPresentationController({
    required FrameworkVtsMotionPresentationClient client,
  }) : _client = client;
  final FrameworkVtsMotionPresentationClient _client;
  FrameworkVtsMotionPresentationState _state =
      const FrameworkVtsMotionPresentationState.idle();
  int _operation = 0;
  bool _disposed = false;
  FrameworkVtsMotionPresentationState get state => _state;

  Future<void> apply(FrameworkVtsMotionPresentationRequest request) async {
    if (_disposed || _state.isClosed) return;
    if (_state.isApplying) {
      throw const FrameworkVtsMotionPresentationProblemException(
        FrameworkVtsMotionPresentationProblem(
          code: 'vts_motion_already_applying',
          message: 'A VTS motion request is already active.',
          retryable: false,
        ),
      );
    }
    final operation = ++_operation;
    _set(
      FrameworkVtsMotionPresentationState(
        phase: FrameworkVtsMotionPresentationPhase.applying,
        request: request,
      ),
    );
    try {
      final result = await _client.apply(request);
      if (!_current(operation)) return;
      _set(
        FrameworkVtsMotionPresentationState(
          phase: result.presentationPhase,
          request: request,
          result: result,
          problem: result.status == FrameworkVtsMotionExecutionStatus.failed
              ? FrameworkVtsMotionPresentationProblem(
                  code: result.reasonCode,
                  message: result.safeMessage.isEmpty
                      ? 'The VTS motion request failed.'
                      : result.safeMessage,
                  retryable: result.commandResults.any(
                    (item) => item.retryable,
                  ),
                )
              : null,
        ),
      );
    } on FrameworkVtsMotionPresentationProblemException catch (error) {
      if (_current(operation)) {
        _set(
          FrameworkVtsMotionPresentationState(
            phase: FrameworkVtsMotionPresentationPhase.failed,
            request: request,
            problem: error.problem,
          ),
        );
      }
    } catch (_) {
      if (_current(operation)) {
        _set(
          const FrameworkVtsMotionPresentationState(
            phase: FrameworkVtsMotionPresentationPhase.failed,
            problem: FrameworkVtsMotionPresentationProblem(
              code: 'vts_motion_apply_failed',
              message: 'The VTS motion presentation request failed.',
              retryable: true,
            ),
          ),
        );
      }
    }
  }

  void reset() {
    if (_disposed || _state.isClosed) return;
    _operation += 1;
    _set(const FrameworkVtsMotionPresentationState.idle());
  }

  bool _current(int operation) =>
      !_disposed && !_state.isClosed && operation == _operation;
  void _set(FrameworkVtsMotionPresentationState value) {
    if (_disposed) return;
    _state = value;
    notifyListeners();
  }

  @override
  void dispose() {
    if (_disposed) return;
    _operation += 1;
    _state = const FrameworkVtsMotionPresentationState(
      phase: FrameworkVtsMotionPresentationPhase.closed,
    );
    _disposed = true;
    super.dispose();
  }
}
