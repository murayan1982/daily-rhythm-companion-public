import '../models/framework_vts_motion_presentation.dart';

typedef FrameworkVtsMotionPresentationTransport =
    Future<Map<String, Object?>> Function(
      FrameworkVtsMotionPresentationRequest request,
    );

class FrameworkVtsMotionPresentationClient {
  const FrameworkVtsMotionPresentationClient({required this.transport});
  final FrameworkVtsMotionPresentationTransport transport;

  Future<FrameworkVtsMotionPresentationResult> apply(
    FrameworkVtsMotionPresentationRequest request,
  ) async {
    try {
      return FrameworkVtsMotionPresentationResult.fromJson(
        await transport(request),
      );
    } on FrameworkVtsMotionPresentationProblemException {
      rethrow;
    } catch (_) {
      throw const FrameworkVtsMotionPresentationProblemException(
        FrameworkVtsMotionPresentationProblem(
          code: 'vts_motion_transport_failed',
          message: 'The VTS motion presentation request failed.',
          retryable: true,
        ),
      );
    }
  }
}
