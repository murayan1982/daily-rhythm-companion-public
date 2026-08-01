import '../models/character_motion_presentation.dart';

typedef CharacterMotionPresentationTransport =
    Future<Map<String, Object?>> Function(
      CharacterMotionPresentationRequest request,
    );

class CharacterMotionPresentationClient {
  const CharacterMotionPresentationClient({required this.transport});

  final CharacterMotionPresentationTransport transport;

  Future<CharacterMotionPresentationResult> apply(
    CharacterMotionPresentationRequest request,
  ) async {
    try {
      final response = await transport(request);
      return CharacterMotionPresentationResult.fromJson(response);
    } on CharacterMotionPresentationProblemException {
      rethrow;
    } catch (_) {
      throw const CharacterMotionPresentationProblemException(
        CharacterMotionPresentationProblem(
          code: 'motion_transport_failed',
          message: 'The character-motion presentation request failed.',
          retryable: true,
        ),
      );
    }
  }
}
