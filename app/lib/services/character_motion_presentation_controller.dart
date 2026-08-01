import 'package:flutter/foundation.dart';

import '../models/character_motion_presentation.dart';
import 'character_motion_presentation_client.dart';

class CharacterMotionPresentationController extends ChangeNotifier {
  CharacterMotionPresentationController({
    required CharacterMotionPresentationClient client,
  }) : _client = client;

  final CharacterMotionPresentationClient _client;
  CharacterMotionPresentationState _state =
      const CharacterMotionPresentationState.idle();
  int _operation = 0;
  bool _isDisposed = false;

  CharacterMotionPresentationState get state => _state;

  Future<void> apply(CharacterMotionPresentationRequest request) async {
    if (_isDisposed || _state.isClosed) {
      throw const CharacterMotionPresentationProblemException(
        CharacterMotionPresentationProblem(
          code: 'motion_controller_closed',
          message: 'The character-motion presentation controller is closed.',
          retryable: false,
        ),
      );
    }
    if (_state.isApplying) {
      throw const CharacterMotionPresentationProblemException(
        CharacterMotionPresentationProblem(
          code: 'active_motion_request_rejected',
          message: 'A character-motion presentation request is already active.',
          retryable: false,
        ),
      );
    }

    final operation = ++_operation;
    _setState(
      CharacterMotionPresentationState(
        phase: CharacterMotionPresentationPhase.applying,
        request: request,
      ),
    );

    try {
      final result = await _client.apply(request);
      if (!_isCurrent(operation)) {
        return;
      }
      _setState(
        CharacterMotionPresentationState(
          phase: result.presentationPhase,
          request: request,
          result: result,
          problem: result.status == CharacterMotionExecutionStatus.failed
              ? CharacterMotionPresentationProblem(
                  code: result.reasonCode,
                  message: result.safeMessage.isEmpty
                      ? 'The character-motion presentation request failed.'
                      : result.safeMessage,
                  retryable: result.commandResults.any(
                    (command) => command.retryable,
                  ),
                )
              : null,
        ),
      );
    } on CharacterMotionPresentationProblemException catch (error) {
      if (_isCurrent(operation)) {
        _setState(
          CharacterMotionPresentationState(
            phase: CharacterMotionPresentationPhase.failed,
            request: request,
            problem: error.problem,
          ),
        );
      }
    } catch (_) {
      if (_isCurrent(operation)) {
        _setState(
          CharacterMotionPresentationState(
            phase: CharacterMotionPresentationPhase.failed,
            request: request,
            problem: const CharacterMotionPresentationProblem(
              code: 'motion_apply_failed',
              message: 'The character-motion presentation request failed.',
              retryable: true,
            ),
          ),
        );
      }
    }
  }

  void reset() {
    if (_isDisposed || _state.isClosed) {
      return;
    }
    _operation += 1;
    _setState(const CharacterMotionPresentationState.idle());
  }

  void close() {
    if (_isDisposed || _state.isClosed) {
      return;
    }
    _operation += 1;
    _setState(
      const CharacterMotionPresentationState(
        phase: CharacterMotionPresentationPhase.closed,
      ),
    );
  }

  bool _isCurrent(int operation) =>
      !_isDisposed && !_state.isClosed && operation == _operation;

  void _setState(CharacterMotionPresentationState next) {
    if (_isDisposed) {
      return;
    }
    _state = next;
    notifyListeners();
  }

  @override
  void dispose() {
    if (_isDisposed) {
      return;
    }
    _operation += 1;
    _state = const CharacterMotionPresentationState(
      phase: CharacterMotionPresentationPhase.closed,
    );
    _isDisposed = true;
    super.dispose();
  }
}
