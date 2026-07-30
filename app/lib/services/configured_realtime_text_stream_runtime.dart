import 'package:http/http.dart' as http;

import 'backend_api_client.dart';
import 'realtime_text_stream_client.dart';
import 'realtime_text_stream_controller.dart';

typedef RealtimeTextStreamHttpClientFactory = http.Client Function();

class ConfiguredRealtimeTextStreamRuntime {
  ConfiguredRealtimeTextStreamRuntime({
    required this.enabled,
    required this.baseUrl,
    RealtimeTextStreamHttpClientFactory? httpClientFactory,
  }) : _httpClientFactory = httpClientFactory ?? http.Client.new;

  factory ConfiguredRealtimeTextStreamRuntime.fromEnvironment({
    BackendApiClient apiClient = const BackendApiClient(),
    RealtimeTextStreamHttpClientFactory? httpClientFactory,
  }) {
    return ConfiguredRealtimeTextStreamRuntime(
      enabled: const bool.fromEnvironment(
        'DRC_RT4_ENABLE_CONFIGURED_TEXT_STREAM',
        defaultValue: false,
      ),
      baseUrl: apiClient.baseUrl,
      httpClientFactory: httpClientFactory,
    );
  }

  final bool enabled;
  final String baseUrl;
  final RealtimeTextStreamHttpClientFactory _httpClientFactory;

  RealtimeTextStreamController Function()? buildControllerFactory() {
    final configuredBaseUrl = baseUrl.trim();
    if (!enabled || !_isValidBaseUrl(configuredBaseUrl)) {
      return null;
    }
    return () {
      final httpClient = _httpClientFactory();
      final streamClient = RealtimeTextStreamClient(
        baseUrl: configuredBaseUrl,
        client: httpClient,
      );
      return RealtimeTextStreamController(client: streamClient);
    };
  }
}

bool _isValidBaseUrl(String value) {
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
