import 'dart:convert';
import 'dart:io';

import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;

import 'microphone_capture_host_audio_handoff.dart';

/// Path-free Backend staging handle created by the guarded RT-3c3 upload.
@immutable
class BackendVoiceInputStagedArtifact {
  const BackendVoiceInputStagedArtifact({
    required this.stagingId,
    required this.audioFormat,
    required this.mediaType,
    required this.byteCount,
    required this.sampleRateHz,
    required this.channelCount,
    required this.duration,
    required this.expiresIn,
  });

  final String stagingId;
  final String audioFormat;
  final String mediaType;
  final int byteCount;
  final int sampleRateHz;
  final int channelCount;
  final Duration duration;
  final Duration expiresIn;
}

/// Streams one scoped private mobile WAV artifact to the configured DRC Backend.
///
/// The private path is resolved only inside
/// [HostAudioPrivateArtifactLease.withPrivateArtifactPath]. It is never placed
/// in a URL, header, response model, public metadata, error, or log. This
/// consumer does not import Framework code and does not execute STT.
class BackendVoiceInputStagingConsumer implements HostAudioHandoffConsumer {
  BackendVoiceInputStagingConsumer({
    required String baseUrl,
    http.Client? client,
    this.maximumBodyBytes = 1048576,
    this.maximumResponseBytes = 16384,
  })  : _endpoint = Uri.parse(
          '${baseUrl.replaceFirst(RegExp(r'/$'), '')}'
          '/demo/voice-input/staging',
        ),
        _client = client ?? http.Client(),
        _ownsClient = client == null;

  final Uri _endpoint;
  final http.Client _client;
  final bool _ownsClient;
  final int maximumBodyBytes;
  final int maximumResponseBytes;

  BackendVoiceInputStagedArtifact? _stagedArtifact;
  bool _requestInFlight = false;
  bool _transportClosed = false;
  bool _disposed = false;

  BackendVoiceInputStagedArtifact? get stagedArtifact => _stagedArtifact;
  bool get hasStagedArtifact => _stagedArtifact != null;

  /// Transfers ownership of the path-free staging handle to the next app layer.
  BackendVoiceInputStagedArtifact? takeStagedArtifact() {
    final value = _stagedArtifact;
    _stagedArtifact = null;
    return value;
  }

  @override
  Future<HostAudioHandoffConsumerResult> consume(
    HostAudioPrivateArtifactLease lease,
  ) async {
    if (_disposed || _transportClosed) {
      return _failed(
        'backend_staging_consumer_closed',
        retryable: false,
      );
    }
    if (_requestInFlight) {
      return _failed(
        'backend_staging_request_in_progress',
        retryable: true,
      );
    }
    if (_stagedArtifact != null) {
      return _failed(
        'backend_staging_artifact_pending',
        retryable: false,
      );
    }
    if (maximumBodyBytes <= 0 || maximumResponseBytes <= 0) {
      return _failed(
        'backend_staging_consumer_config_invalid',
        retryable: false,
      );
    }

    _requestInFlight = true;
    try {
      return await lease.withPrivateArtifactPath((privatePath) async {
        final entityType = await FileSystemEntity.type(
          privatePath,
          followLinks: false,
        );
        if (entityType != FileSystemEntityType.file) {
          return _failed(
            'backend_staging_private_artifact_invalid',
            retryable: false,
          );
        }

        final file = File(privatePath);
        final byteCount = await file.length();
        if (byteCount <= 0) {
          return _failed(
            'backend_staging_private_artifact_empty',
            retryable: false,
          );
        }
        if (byteCount > maximumBodyBytes) {
          return _failed(
            'backend_staging_private_artifact_too_large',
            retryable: false,
          );
        }

        final descriptor = lease.descriptor;
        final durationMs = descriptor.capturedDuration.inMilliseconds;
        final request = http.StreamedRequest('POST', _endpoint)
          ..contentLength = byteCount
          ..headers.addAll(<String, String>{
            'Content-Type': 'audio/wav',
            'X-DRC-Audio-Format': descriptor.encoding,
            'X-DRC-Sample-Rate-Hz': descriptor.sampleRateHz.toString(),
            'X-DRC-Channel-Count': descriptor.channelCount.toString(),
            'X-DRC-Duration-Ms': durationMs.toString(),
          });

        final responseFuture = _client.send(request);
        try {
          await request.sink.addStream(file.openRead());
        } finally {
          await request.sink.close();
        }

        final response = await responseFuture;
        final responseText = await _readBoundedResponse(response);
        if (response.statusCode != 201) {
          final problem = _parseProblem(responseText);
          return _failed(
            problem.code ?? 'backend_staging_http_${response.statusCode}',
            retryable: problem.retryable ?? response.statusCode >= 500,
          );
        }

        final staged = _parseStagedArtifact(
          responseText,
          expectedByteCount: byteCount,
          expectedDescriptor: descriptor,
        );
        _stagedArtifact = staged;
        return HostAudioHandoffConsumerResult.completed(
          technicalCode: 'host_audio_backend_staging_completed',
          safeMessage: '音声データを安全に一時保存しました。',
          publicMetadata: const <String, Object?>{
            'audio_uploaded': true,
            'backend_staging_created': true,
            'backend_staging_id_available': true,
          },
        );
      });
    } on HostAudioHandoffException catch (error) {
      return _failed(error.code, retryable: false);
    } on FileSystemException {
      return _failed(
        'backend_staging_private_artifact_read_failed',
        retryable: false,
      );
    } on http.ClientException {
      return _failed(
        'backend_staging_network_failed',
        retryable: true,
      );
    } on FormatException {
      return _failed(
        'backend_staging_response_invalid',
        retryable: true,
      );
    } catch (_) {
      return _failed(
        'backend_staging_request_failed',
        retryable: true,
      );
    } finally {
      _requestInFlight = false;
    }
  }

  @override
  Future<void> cancel() async {
    if (_requestInFlight && !_transportClosed) {
      _client.close();
      _transportClosed = true;
    }
  }

  @override
  Future<void> dispose() async {
    if (_disposed) {
      return;
    }
    _disposed = true;
    if (!_transportClosed && _ownsClient) {
      _client.close();
      _transportClosed = true;
    }
  }

  Future<String> _readBoundedResponse(http.StreamedResponse response) async {
    final bytes = <int>[];
    await for (final chunk in response.stream) {
      if (bytes.length + chunk.length > maximumResponseBytes) {
        throw const FormatException('backend staging response too large');
      }
      bytes.addAll(chunk);
    }
    return utf8.decode(bytes);
  }

  BackendVoiceInputStagedArtifact _parseStagedArtifact(
    String responseText, {
    required int expectedByteCount,
    required HostAudioHandoffDescriptor expectedDescriptor,
  }) {
    final decoded = jsonDecode(responseText);
    if (decoded is! Map) {
      throw const FormatException('backend staging response is not an object');
    }
    final body = Map<String, dynamic>.from(decoded);
    final stagingId = body['staging_id']?.toString().trim() ?? '';
    final audioFormat =
        body['audio_format']?.toString().trim().toLowerCase() ?? '';
    final mediaType =
        body['media_type']?.toString().trim().toLowerCase() ?? '';
    final accepted = body['accepted'] == true;
    final requestState = body['request_state']?.toString() ?? '';
    final byteCount = body['byte_count'];
    final sampleRateHz = body['sample_rate_hz'];
    final channelCount = body['channel_count'];
    final durationMs = body['duration_ms'];
    final expiresInSeconds = body['expires_in_seconds'];

    if (!accepted ||
        requestState != 'staged' ||
        !RegExp(r'^[0-9a-f]{32}$').hasMatch(stagingId) ||
        audioFormat != 'wav' ||
        mediaType != 'audio/wav' ||
        byteCount is! int ||
        byteCount != expectedByteCount ||
        sampleRateHz is! int ||
        sampleRateHz != expectedDescriptor.sampleRateHz ||
        channelCount is! int ||
        channelCount != expectedDescriptor.channelCount ||
        durationMs is! int ||
        durationMs != expectedDescriptor.capturedDuration.inMilliseconds ||
        expiresInSeconds is! int ||
        expiresInSeconds <= 0) {
      throw const FormatException('backend staging response contract mismatch');
    }

    return BackendVoiceInputStagedArtifact(
      stagingId: stagingId,
      audioFormat: audioFormat,
      mediaType: mediaType,
      byteCount: byteCount,
      sampleRateHz: sampleRateHz,
      channelCount: channelCount,
      duration: Duration(milliseconds: durationMs),
      expiresIn: Duration(seconds: expiresInSeconds),
    );
  }

  _BackendStagingProblem _parseProblem(String responseText) {
    try {
      final decoded = jsonDecode(responseText);
      if (decoded is Map && decoded['detail'] is Map) {
        final detail = Map<String, dynamic>.from(decoded['detail'] as Map);
        final rawCode = detail['code']?.toString().trim().toLowerCase() ?? '';
        final code = RegExp(r'^[a-z0-9_]{1,80}$').hasMatch(rawCode)
            ? rawCode
            : null;
        return _BackendStagingProblem(
          code: code,
          retryable: detail['retryable'] is bool
              ? detail['retryable'] as bool
              : null,
        );
      }
    } catch (_) {
      // Fall through to the status-derived public-safe failure.
    }
    return const _BackendStagingProblem();
  }

  HostAudioHandoffConsumerResult _failed(
    String technicalCode, {
    required bool retryable,
  }) {
    return HostAudioHandoffConsumerResult.failed(
      technicalCode: technicalCode,
      safeMessage: '音声データの一時保存に失敗しました。',
      retryable: retryable,
      publicMetadata: const <String, Object?>{
        'audio_uploaded': false,
        'backend_staging_created': false,
        'backend_staging_id_available': false,
      },
    );
  }
}

@immutable
class _BackendStagingProblem {
  const _BackendStagingProblem({this.code, this.retryable});

  final String? code;
  final bool? retryable;
}
