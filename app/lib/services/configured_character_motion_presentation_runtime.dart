import 'dart:convert';

import 'package:http/http.dart' as http;

import '../models/character_motion_presentation.dart';
import 'backend_api_client.dart';
import 'character_motion_presentation_client.dart';
import 'character_motion_presentation_controller.dart';

const String configuredCharacterMotionPresentationPath =
    '/demo/character-motion/presentation';
const int configuredCharacterMotionPresentationMaxResponseBytes = 65536;
const Duration configuredCharacterMotionPresentationTimeout = Duration(
  seconds: 10,
);

typedef CharacterMotionPresentationHttpClientFactory = http.Client Function();

/// Default-off RT-6f assembly for one explicit HomeScreen Apply request.
///
/// Runtime construction, factory lookup, controller construction, HomeScreen
/// load, opt-in, reset, opt-out, and disposal do not execute HTTP requests.
class ConfiguredCharacterMotionPresentationRuntime {
  ConfiguredCharacterMotionPresentationRuntime({
    required this.enabled,
    required this.apiClient,
    CharacterMotionPresentationHttpClientFactory? httpClientFactory,
    this.requestTimeout = configuredCharacterMotionPresentationTimeout,
  }) : _httpClientFactory = httpClientFactory ?? http.Client.new;

  factory ConfiguredCharacterMotionPresentationRuntime.fromEnvironment({
    BackendApiClient apiClient = const BackendApiClient(),
    CharacterMotionPresentationHttpClientFactory? httpClientFactory,
  }) {
    return ConfiguredCharacterMotionPresentationRuntime(
      enabled: const bool.fromEnvironment(
        'DRC_RT6_ENABLE_CONFIGURED_MOCK_MOTION',
        defaultValue: false,
      ),
      apiClient: apiClient,
      httpClientFactory: httpClientFactory,
    );
  }

  final bool enabled;
  final BackendApiClient apiClient;
  final Duration requestTimeout;
  final CharacterMotionPresentationHttpClientFactory _httpClientFactory;

  CharacterMotionPresentationController Function()? buildControllerFactory() {
    final configuredBaseUrl = apiClient.baseUrl.trim();
    if (!enabled || !_isValidBackendBaseUrl(configuredBaseUrl)) {
      return null;
    }
    final normalizedBaseUrl = configuredBaseUrl.replaceFirst(
      RegExp(r'/+$'),
      '',
    );

    return () {
      final httpClient = _httpClientFactory();
      final transport = _ConfiguredCharacterMotionPresentationTransport(
        client: httpClient,
        endpoint: Uri.parse(
          '$normalizedBaseUrl$configuredCharacterMotionPresentationPath',
        ),
        timeout: requestTimeout,
      );
      return _OwnedCharacterMotionPresentationController(
        client: CharacterMotionPresentationClient(transport: transport.call),
        httpClient: httpClient,
      );
    };
  }
}

class _ConfiguredCharacterMotionPresentationTransport {
  const _ConfiguredCharacterMotionPresentationTransport({
    required this.client,
    required this.endpoint,
    required this.timeout,
  });

  final http.Client client;
  final Uri endpoint;
  final Duration timeout;

  Future<Map<String, Object?>> call(
    CharacterMotionPresentationRequest request,
  ) async {
    try {
      return await _sendAndDecode(request).timeout(timeout);
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

  Future<Map<String, Object?>> _sendAndDecode(
    CharacterMotionPresentationRequest request,
  ) async {
    final httpRequest = http.Request('POST', endpoint)
      ..followRedirects = false
      ..maxRedirects = 0
      ..headers['content-type'] = 'application/json; charset=utf-8'
      ..headers['accept'] = 'application/json'
      ..body = jsonEncode(request.toJson());

    final response = await client.send(httpRequest);
    if (response.statusCode != 200) {
      throw const FormatException('unexpected response status');
    }
    final contentType = response.headers['content-type']?.toLowerCase() ?? '';
    final mediaType = contentType.split(';').first.trim();
    if (mediaType != 'application/json') {
      throw const FormatException('unexpected response content type');
    }
    final contentLength = response.contentLength;
    if (contentLength != null &&
        contentLength > configuredCharacterMotionPresentationMaxResponseBytes) {
      throw const FormatException('response body too large');
    }

    final bytes = <int>[];
    await for (final chunk in response.stream) {
      if (bytes.length + chunk.length >
          configuredCharacterMotionPresentationMaxResponseBytes) {
        throw const FormatException('response body too large');
      }
      bytes.addAll(chunk);
    }
    final decoded = jsonDecode(utf8.decode(bytes, allowMalformed: false));
    if (decoded is! Map<String, dynamic>) {
      throw const FormatException('response body must be a JSON object');
    }
    return Map<String, Object?>.from(decoded);
  }
}

class _OwnedCharacterMotionPresentationController
    extends CharacterMotionPresentationController {
  _OwnedCharacterMotionPresentationController({
    required super.client,
    required http.Client httpClient,
  }) : _httpClient = httpClient;

  final http.Client _httpClient;
  bool _resourcesClosed = false;

  @override
  void dispose() {
    if (!_resourcesClosed) {
      _resourcesClosed = true;
      _httpClient.close();
    }
    super.dispose();
  }
}

bool _isValidBackendBaseUrl(String value) {
  final uri = Uri.tryParse(value.trim());
  if (uri == null || !uri.isAbsolute) {
    return false;
  }
  if (uri.scheme != 'http' && uri.scheme != 'https') {
    return false;
  }
  if (uri.host.isEmpty || uri.hasFragment || uri.userInfo.isNotEmpty) {
    return false;
  }
  return true;
}
