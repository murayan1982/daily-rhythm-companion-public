import 'package:flutter/foundation.dart';

const int providerNeutralTranscriptMaxTextChars = 4096;
const int providerNeutralTranscriptMaxResultIdChars = 128;
const int providerNeutralTranscriptMaxRememberedResultIds = 32;

@immutable
class ProviderNeutralTranscriptResult {
  const ProviderNeutralTranscriptResult({
    required this.resultId,
    required this.text,
    required this.isFinal,
  });

  final String resultId;
  final String text;
  final bool isFinal;
}
