import 'dart:convert';

import 'package:http/http.dart' as http;

import '../models/framework_vts_motion_presentation.dart';
import 'backend_api_client.dart';
import 'framework_vts_motion_presentation_client.dart';
import 'framework_vts_motion_presentation_controller.dart';

const String configuredFrameworkVtsMotionPresentationPath =
    '/demo/character-motion/vts/presentation';
const int configuredFrameworkVtsMotionMaxResponseBytes = 65536;
const Duration configuredFrameworkVtsMotionTimeout = Duration(seconds: 10);
typedef FrameworkVtsMotionHttpClientFactory = http.Client Function();

class ConfiguredFrameworkVtsMotionPresentationRuntime {
  ConfiguredFrameworkVtsMotionPresentationRuntime({
    required this.enabled,
    required this.apiClient,
    FrameworkVtsMotionHttpClientFactory? httpClientFactory,
    this.requestTimeout = configuredFrameworkVtsMotionTimeout,
  }) : _httpClientFactory = httpClientFactory ?? http.Client.new;

  factory ConfiguredFrameworkVtsMotionPresentationRuntime.fromEnvironment({
    BackendApiClient apiClient = const BackendApiClient(),
    FrameworkVtsMotionHttpClientFactory? httpClientFactory,
  }) => ConfiguredFrameworkVtsMotionPresentationRuntime(
    enabled: const bool.fromEnvironment(
      'DRC_RT7_ENABLE_CONFIGURED_VTS_MOTION',
      defaultValue: false,
    ),
    apiClient: apiClient,
    httpClientFactory: httpClientFactory,
  );

  final bool enabled;
  final BackendApiClient apiClient;
  final Duration requestTimeout;
  final FrameworkVtsMotionHttpClientFactory _httpClientFactory;

  FrameworkVtsMotionPresentationController Function()?
  buildControllerFactory() {
    final base = apiClient.baseUrl.trim();
    if (!enabled || !_validBaseUrl(base)) return null;
    final endpoint = Uri.parse(
      '${base.replaceFirst(RegExp(r'/+$'), '')}$configuredFrameworkVtsMotionPresentationPath',
    );
    return () {
      final httpClient = _httpClientFactory();
      final transport = _ConfiguredFrameworkVtsMotionTransport(
        client: httpClient,
        endpoint: endpoint,
        timeout: requestTimeout,
      );
      return _OwnedFrameworkVtsMotionController(
        client: FrameworkVtsMotionPresentationClient(transport: transport.call),
        httpClient: httpClient,
      );
    };
  }
}

class _ConfiguredFrameworkVtsMotionTransport {
  const _ConfiguredFrameworkVtsMotionTransport({
    required this.client,
    required this.endpoint,
    required this.timeout,
  });
  final http.Client client;
  final Uri endpoint;
  final Duration timeout;

  Future<Map<String, Object?>> call(
    FrameworkVtsMotionPresentationRequest request,
  ) async {
    try {
      return await _send(request).timeout(timeout);
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

  Future<Map<String, Object?>> _send(
    FrameworkVtsMotionPresentationRequest request,
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
    if ((response.headers['content-type'] ?? '')
            .split(';')
            .first
            .trim()
            .toLowerCase() !=
        'application/json') {
      throw const FormatException('unexpected response content type');
    }
    if (response.contentLength != null &&
        response.contentLength! >
            configuredFrameworkVtsMotionMaxResponseBytes) {
      throw const FormatException('response too large');
    }
    final bytes = <int>[];
    await for (final chunk in response.stream) {
      if (bytes.length + chunk.length >
          configuredFrameworkVtsMotionMaxResponseBytes) {
        throw const FormatException('response too large');
      }
      bytes.addAll(chunk);
    }
    final decoded = jsonDecode(utf8.decode(bytes, allowMalformed: false));
    if (decoded is! Map<String, dynamic>) {
      throw const FormatException('response must be object');
    }
    return Map<String, Object?>.from(decoded);
  }
}

class _OwnedFrameworkVtsMotionController
    extends FrameworkVtsMotionPresentationController {
  _OwnedFrameworkVtsMotionController({
    required super.client,
    required http.Client httpClient,
  }) : _httpClient = httpClient;
  final http.Client _httpClient;
  bool _closed = false;
  @override
  void dispose() {
    if (!_closed) {
      _closed = true;
      _httpClient.close();
    }
    super.dispose();
  }
}

bool _validBaseUrl(String value) {
  final uri = Uri.tryParse(value);
  return uri != null &&
      uri.isAbsolute &&
      (uri.scheme == 'http' || uri.scheme == 'https') &&
      uri.host.isNotEmpty &&
      !uri.hasFragment &&
      uri.userInfo.isEmpty;
}
