import 'package:http/http.dart' as http;

import 'backend_api_client.dart';
import 'framework_v600_realtime_session_client.dart';
import 'framework_v600_realtime_session_controller.dart';

typedef FrameworkV600RealtimeSessionHttpClientFactory =
    http.Client Function();

class ConfiguredFrameworkV600RealtimeSessionRuntime {
  ConfiguredFrameworkV600RealtimeSessionRuntime({
    required this.enabled,
    required this.baseUrl,
    FrameworkV600RealtimeSessionHttpClientFactory? httpClientFactory,
  }) : _httpClientFactory = httpClientFactory ?? http.Client.new;

  factory ConfiguredFrameworkV600RealtimeSessionRuntime.fromEnvironment({
    BackendApiClient apiClient = const BackendApiClient(),
    FrameworkV600RealtimeSessionHttpClientFactory? httpClientFactory,
  }) {
    return ConfiguredFrameworkV600RealtimeSessionRuntime(
      enabled: const bool.fromEnvironment(
        'DRC_V4_ENABLE_FRAMEWORK_V6_PROVIDER_FREE_SESSION',
        defaultValue: false,
      ),
      baseUrl: apiClient.baseUrl,
      httpClientFactory: httpClientFactory,
    );
  }

  final bool enabled;
  final String baseUrl;
  final FrameworkV600RealtimeSessionHttpClientFactory _httpClientFactory;

  FrameworkV600RealtimeSessionController Function()? buildControllerFactory() {
    final configuredBaseUrl = baseUrl.trim();
    if (!enabled || !_isValidBaseUrl(configuredBaseUrl)) {
      return null;
    }
    return () {
      final httpClient = _httpClientFactory();
      final sessionClient = FrameworkV600RealtimeSessionClient(
        baseUrl: configuredBaseUrl,
        client: httpClient,
      );
      return FrameworkV600RealtimeSessionController(client: sessionClient);
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
