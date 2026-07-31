import 'dart:convert';

import 'package:http/http.dart' as http;

import '../models/provider_neutral_transcript.dart';
import 'backend_voice_input_staging_consumer.dart';

typedef BackendStagedArtifactTaker = BackendVoiceInputStagedArtifact? Function();
typedef ForegroundVoiceInputOptIn = bool Function();

class BackendProviderNeutralTranscriptException implements Exception {
  const BackendProviderNeutralTranscriptException(
    this.code, {
    required this.retryable,
  });

  final String code;
  final bool retryable;

  @override
  String toString() => 'BackendProviderNeutralTranscriptException($code)';
}

/// Acquires one final provider-neutral transcript from the guarded DRC Backend.
///
/// The staging ID is sent only in a JSON body. The provider keeps no transcript,
/// result ID, staging ID, response body, provider payload, or raw exception in
/// object state. It performs no automatic retry and allows one in-flight request.
class BackendProviderNeutralTranscriptProvider {
  BackendProviderNeutralTranscriptProvider({
    required String baseUrl,
    required BackendStagedArtifactTaker takeStagedArtifact,
    required ForegroundVoiceInputOptIn foregroundOptIn,
    http.Client? client,
    this.language = 'ja',
    this.maximumResponseBytes = 32768,
  })  : _endpoint = Uri.parse(
          '${baseUrl.replaceFirst(RegExp(r'/$'), '')}'
          '/demo/voice-input/transcript',
        ),
        _takeStagedArtifact = takeStagedArtifact,
        _foregroundOptIn = foregroundOptIn,
        _client = client ?? http.Client(),
        _ownsClient = client == null;

  static const Set<String> _responseKeys = <String>{
    'accepted',
    'request_state',
    'result_id',
    'text',
    'is_final',
  };

  final Uri _endpoint;
  final BackendStagedArtifactTaker _takeStagedArtifact;
  final ForegroundVoiceInputOptIn _foregroundOptIn;
  final http.Client _client;
  final bool _ownsClient;
  final String? language;
  final int maximumResponseBytes;

  bool _requestInFlight = false;
  bool _disposed = false;
  bool _transportClosed = false;

  Future<ProviderNeutralTranscriptResult?> acquireNextTranscript() async {
    if (_disposed || _transportClosed) {
      throw const BackendProviderNeutralTranscriptException(
        'backend_transcript_provider_closed',
        retryable: false,
      );
    }
    if (_requestInFlight) {
      throw const BackendProviderNeutralTranscriptException(
        'backend_transcript_request_in_progress',
        retryable: true,
      );
    }
    if (!_foregroundOptIn()) {
      throw const BackendProviderNeutralTranscriptException(
        'backend_transcript_opt_in_required',
        retryable: false,
      );
    }
    if (maximumResponseBytes <= 0) {
      throw const BackendProviderNeutralTranscriptException(
        'backend_transcript_provider_config_invalid',
        retryable: false,
      );
    }

    final stagedArtifact = _takeStagedArtifact();
    if (stagedArtifact == null) {
      return null;
    }

    _requestInFlight = true;
    try {
      final request = http.Request('POST', _endpoint)
        ..followRedirects = false
        ..headers.addAll(const <String, String>{
          'Content-Type': 'application/json',
          'Accept': 'application/json',
          'Cache-Control': 'no-store',
        })
        ..body = jsonEncode(<String, Object?>{
          'staging_id': stagedArtifact.stagingId,
          'foreground_opt_in': true,
          'language': language,
          'duration_ms': stagedArtifact.duration.inMilliseconds,
        });

      final response = await _client.send(request);
      if (response.isRedirect ||
          (response.statusCode >= 300 && response.statusCode < 400)) {
        throw const BackendProviderNeutralTranscriptException(
          'backend_transcript_redirect_rejected',
          retryable: false,
        );
      }

      final responseText = await _readBoundedResponse(response);
      if (_disposed) {
        return null;
      }
      if (response.statusCode != 200) {
        final problem = _parseProblem(responseText);
        throw BackendProviderNeutralTranscriptException(
          problem.code ?? 'backend_transcript_http_${response.statusCode}',
          retryable: problem.retryable ?? response.statusCode >= 500,
        );
      }

      final cacheControl = response.headers['cache-control']?.toLowerCase() ?? '';
      if (!cacheControl.split(',').any((part) => part.trim() == 'no-store')) {
        throw const BackendProviderNeutralTranscriptException(
          'backend_transcript_no_store_required',
          retryable: false,
        );
      }

      return _parseSuccess(responseText);
    } on BackendProviderNeutralTranscriptException {
      if (_disposed) {
        return null;
      }
      rethrow;
    } on http.ClientException {
      if (_disposed) {
        return null;
      }
      throw const BackendProviderNeutralTranscriptException(
        'backend_transcript_network_failed',
        retryable: true,
      );
    } on FormatException {
      if (_disposed) {
        return null;
      }
      throw const BackendProviderNeutralTranscriptException(
        'backend_transcript_response_invalid',
        retryable: true,
      );
    } catch (_) {
      if (_disposed) {
        return null;
      }
      throw const BackendProviderNeutralTranscriptException(
        'backend_transcript_request_failed',
        retryable: true,
      );
    } finally {
      _requestInFlight = false;
    }
  }

  Future<String> _readBoundedResponse(http.StreamedResponse response) async {
    final bytes = <int>[];
    await for (final chunk in response.stream) {
      if (bytes.length + chunk.length > maximumResponseBytes) {
        throw const FormatException('backend transcript response too large');
      }
      bytes.addAll(chunk);
    }
    return utf8.decode(bytes);
  }

  ProviderNeutralTranscriptResult _parseSuccess(String responseText) {
    final decoded = jsonDecode(responseText);
    if (decoded is! Map) {
      throw const FormatException('backend transcript response is not an object');
    }
    final body = Map<String, dynamic>.from(decoded);
    if (body.keys.toSet().length != _responseKeys.length ||
        !body.keys.toSet().containsAll(_responseKeys)) {
      throw const FormatException('backend transcript response shape invalid');
    }

    final accepted = body['accepted'] == true;
    final requestState = body['request_state']?.toString() ?? '';
    final resultId = body['result_id']?.toString().trim() ?? '';
    final text = body['text'] is String ? body['text'] as String : '';
    final isFinal = body['is_final'] == true;

    if (!accepted || requestState != 'final_transcript_ready' || !isFinal) {
      throw const FormatException('backend transcript final state invalid');
    }
    if (!RegExp(r'^[0-9a-f]{32}$').hasMatch(resultId)) {
      throw const FormatException('backend transcript result id invalid');
    }
    final normalizedText = text.trim();
    if (normalizedText.isEmpty ||
        normalizedText.runes.length > providerNeutralTranscriptMaxTextChars) {
      throw const FormatException('backend transcript text invalid');
    }

    return ProviderNeutralTranscriptResult(
      resultId: resultId,
      text: normalizedText,
      isFinal: true,
    );
  }

  _BackendTranscriptProblem _parseProblem(String responseText) {
    try {
      final decoded = jsonDecode(responseText);
      if (decoded is Map && decoded['detail'] is Map) {
        final detail = Map<String, dynamic>.from(decoded['detail'] as Map);
        final rawCode = detail['code']?.toString().trim().toLowerCase() ?? '';
        final code = RegExp(r'^[a-z0-9_]{1,80}$').hasMatch(rawCode)
            ? rawCode
            : null;
        return _BackendTranscriptProblem(
          code: code,
          retryable: detail['retryable'] is bool
              ? detail['retryable'] as bool
              : null,
        );
      }
    } catch (_) {
      // Fall through to the status-derived safe failure.
    }
    return const _BackendTranscriptProblem();
  }

  void dispose() {
    if (_disposed) {
      return;
    }
    _disposed = true;
    if (_ownsClient && !_transportClosed) {
      _client.close();
      _transportClosed = true;
    }
  }
}

class _BackendTranscriptProblem {
  const _BackendTranscriptProblem({this.code, this.retryable});

  final String? code;
  final bool? retryable;
}
