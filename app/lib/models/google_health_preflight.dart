class GoogleHealthPreflight {
  const GoogleHealthPreflight({
    required this.provider,
    required this.status,
    required this.readyForOauth,
    required this.readyForAuthCallback,
    required this.readyForTokenRefresh,
    required this.readyForRealApiRequest,
    required this.credentials,
    required this.oauth,
    required this.token,
    required this.api,
    required this.message,
    required this.nextAction,
    this.error,
  });

  final String provider;
  final String status;
  final bool readyForOauth;
  final bool readyForAuthCallback;
  final bool readyForTokenRefresh;
  final bool readyForRealApiRequest;
  final GoogleHealthPreflightCredentials credentials;
  final GoogleHealthPreflightOAuth oauth;
  final GoogleHealthPreflightToken token;
  final GoogleHealthPreflightApi api;
  final String message;
  final String nextAction;
  final String? error;

  factory GoogleHealthPreflight.fromJson(Map<String, dynamic> json) {
    return GoogleHealthPreflight(
      provider: _stringFromJson(json['provider'], fallback: 'unknown'),
      status: _stringFromJson(json['status'], fallback: 'unknown'),
      readyForOauth: _boolFromJson(json['ready_for_oauth']),
      readyForAuthCallback: _boolFromJson(json['ready_for_auth_callback']),
      readyForTokenRefresh: _boolFromJson(json['ready_for_token_refresh']),
      readyForRealApiRequest: _boolFromJson(
        json['ready_for_real_api_request'],
      ),
      credentials: GoogleHealthPreflightCredentials.fromJson(
        _mapFromJson(json['credentials']),
      ),
      oauth: GoogleHealthPreflightOAuth.fromJson(_mapFromJson(json['oauth'])),
      token: GoogleHealthPreflightToken.fromJson(_mapFromJson(json['token'])),
      api: GoogleHealthPreflightApi.fromJson(_mapFromJson(json['api'])),
      message: _stringFromJson(json['message']),
      nextAction: _stringFromJson(json['next_action']),
      error: _nullableStringFromJson(json['error']),
    );
  }

  String get displayStatus {
    switch (status) {
      case 'ready_for_real_api':
        return 'ready';
      case 'api_blocked':
        return 'guard blocked';
      case 'api_disabled':
        return 'API disabled';
      case 'needs_credentials':
        return 'credentials不足';
      case 'needs_redirect_uri':
        return 'redirect URI不足';
      case 'redirect_uri_not_registered':
        return 'redirect URI未登録';
      case 'needs_scopes':
        return 'scopes不足';
      case 'needs_auth':
        return 'auth不足';
      case 'needs_token_refresh':
        return 'token refresh必要';
      case 'mock_mode':
        return 'mock';
      default:
        return status;
    }
  }

  String get displayReason {
    if (error != null && error!.isNotEmpty) {
      return error!;
    }
    if (message.isNotEmpty) {
      return message;
    }
    return 'Google Health preflight の状態を確認してください。';
  }

  String get displayNextAction {
    if (nextAction.isNotEmpty) {
      return nextAction;
    }

    switch (status) {
      case 'mock_mode':
        return 'SLEEP_PROVIDER=google_health に切り替えて、Google Health preflight を確認してください。';
      case 'needs_credentials':
        return 'credentials.json のパスと内容を確認してください。';
      case 'needs_redirect_uri':
        return 'GOOGLE_HEALTH_REDIRECT_URI を設定してください。';
      case 'redirect_uri_not_registered':
        return 'Google OAuth client に redirect URI が登録されているか確認してください。';
      case 'needs_scopes':
        return 'GOOGLE_HEALTH_OAUTH_SCOPES を設定してください。';
      case 'needs_auth':
        return '/google-health/connect から OAuth 認証を実行してください。';
      case 'needs_token_refresh':
        return 'refresh token による access token 更新を確認してください。';
      case 'api_disabled':
        final apiNextAction = api.nextAction;
        return apiNextAction != null && apiNextAction.isNotEmpty
            ? apiNextAction
            : 'endpoint/scope を確認してから real API flags を安全に有効化してください。';
      case 'api_blocked':
        final apiNextAction = api.nextAction;
        if (apiNextAction != null && apiNextAction.isNotEmpty) {
          return apiNextAction;
        }
        final apiMessage = api.message;
        return apiMessage != null && apiMessage.isNotEmpty
            ? apiMessage
            : '実API guard の状態を確認してください。';
      case 'ready_for_real_api':
        return 'real credentials による Google Health 実API確認に進めます。';
      default:
        return message.isNotEmpty ? message : 'Google Health preflight の状態を確認してください。';
    }
  }

  static Map<String, dynamic> _mapFromJson(Object? value) {
    if (value is Map<String, dynamic>) {
      return value;
    }
    if (value is Map) {
      return value.map((key, item) => MapEntry(key.toString(), item));
    }
    return const <String, dynamic>{};
  }

  static bool _boolFromJson(Object? value, {bool fallback = false}) {
    if (value is bool) {
      return value;
    }
    if (value is num) {
      return value != 0;
    }
    if (value is String) {
      final normalized = value.trim().toLowerCase();
      if (normalized == 'true' || normalized == '1' || normalized == 'yes') {
        return true;
      }
      if (normalized == 'false' || normalized == '0' || normalized == 'no') {
        return false;
      }
    }
    return fallback;
  }

  static bool? _nullableBoolFromJson(Object? value) {
    if (value == null) {
      return null;
    }
    return _boolFromJson(value);
  }

  static int _intFromJson(Object? value, {int fallback = 0}) {
    if (value is int) {
      return value;
    }
    if (value is num) {
      return value.toInt();
    }
    if (value is String) {
      return int.tryParse(value.trim()) ?? fallback;
    }
    return fallback;
  }

  static String _stringFromJson(Object? value, {String fallback = ''}) {
    final stringValue = _nullableStringFromJson(value);
    return stringValue == null || stringValue.isEmpty ? fallback : stringValue;
  }

  static String? _nullableStringFromJson(Object? value) {
    if (value == null) {
      return null;
    }
    final text = value.toString().trim();
    return text.isEmpty ? null : text;
  }
}

class GoogleHealthPreflightCredentials {
  const GoogleHealthPreflightCredentials({
    required this.credentialsFileConfigured,
    required this.credentialsFileExists,
    required this.credentialsLoaded,
    required this.clientIdConfigured,
    required this.clientSecretConfigured,
    required this.redirectUriConfigured,
    this.redirectUriRegistered,
    this.message,
    this.nextAction,
    this.error,
  });

  final bool credentialsFileConfigured;
  final bool credentialsFileExists;
  final bool credentialsLoaded;
  final bool clientIdConfigured;
  final bool clientSecretConfigured;
  final bool redirectUriConfigured;
  final bool? redirectUriRegistered;
  final String? message;
  final String? nextAction;
  final String? error;

  factory GoogleHealthPreflightCredentials.fromJson(
    Map<String, dynamic> json,
  ) {
    return GoogleHealthPreflightCredentials(
      credentialsFileConfigured: GoogleHealthPreflight._boolFromJson(
        json['credentials_file_configured'],
      ),
      credentialsFileExists: GoogleHealthPreflight._boolFromJson(
        json['credentials_file_exists'],
      ),
      credentialsLoaded: GoogleHealthPreflight._boolFromJson(
        json['credentials_loaded'],
      ),
      clientIdConfigured: GoogleHealthPreflight._boolFromJson(
        json['client_id_configured'],
      ),
      clientSecretConfigured: GoogleHealthPreflight._boolFromJson(
        json['client_secret_configured'],
      ),
      redirectUriConfigured: GoogleHealthPreflight._boolFromJson(
        json['redirect_uri_configured'],
      ),
      redirectUriRegistered: GoogleHealthPreflight._nullableBoolFromJson(
        json['redirect_uri_registered'],
      ),
      message: GoogleHealthPreflight._nullableStringFromJson(json['message']),
      nextAction: GoogleHealthPreflight._nullableStringFromJson(
        json['next_action'],
      ),
      error: GoogleHealthPreflight._nullableStringFromJson(json['error']),
    );
  }
}

class GoogleHealthPreflightOAuth {
  const GoogleHealthPreflightOAuth({
    required this.scopesConfigured,
    required this.scopeCount,
    required this.authUrlReady,
    required this.stateReady,
    this.message,
    this.nextAction,
    this.error,
  });

  final bool scopesConfigured;
  final int scopeCount;
  final bool authUrlReady;
  final bool stateReady;
  final String? message;
  final String? nextAction;
  final String? error;

  factory GoogleHealthPreflightOAuth.fromJson(Map<String, dynamic> json) {
    return GoogleHealthPreflightOAuth(
      scopesConfigured: GoogleHealthPreflight._boolFromJson(
        json['scopes_configured'],
      ),
      scopeCount: GoogleHealthPreflight._intFromJson(json['scope_count']),
      authUrlReady: GoogleHealthPreflight._boolFromJson(json['auth_url_ready']),
      stateReady: GoogleHealthPreflight._boolFromJson(json['state_ready']),
      message: GoogleHealthPreflight._nullableStringFromJson(json['message']),
      nextAction: GoogleHealthPreflight._nullableStringFromJson(
        json['next_action'],
      ),
      error: GoogleHealthPreflight._nullableStringFromJson(json['error']),
    );
  }
}

class GoogleHealthPreflightToken {
  const GoogleHealthPreflightToken({
    required this.stored,
    required this.hasRefreshToken,
    this.accessTokenExpired,
    this.refreshRecommended,
    required this.scopeConfigured,
  });

  final bool stored;
  final bool hasRefreshToken;
  final bool? accessTokenExpired;
  final bool? refreshRecommended;
  final bool scopeConfigured;

  factory GoogleHealthPreflightToken.fromJson(Map<String, dynamic> json) {
    return GoogleHealthPreflightToken(
      stored: GoogleHealthPreflight._boolFromJson(json['stored']),
      hasRefreshToken: GoogleHealthPreflight._boolFromJson(
        json['has_refresh_token'],
      ),
      accessTokenExpired: GoogleHealthPreflight._nullableBoolFromJson(
        json['access_token_expired'],
      ),
      refreshRecommended: GoogleHealthPreflight._nullableBoolFromJson(
        json['refresh_recommended'],
      ),
      scopeConfigured: GoogleHealthPreflight._boolFromJson(
        json['scope_configured'],
      ),
    );
  }
}

class GoogleHealthPreflightApi {
  const GoogleHealthPreflightApi({
    required this.realTokenExchangeEnabled,
    required this.realTokenRefreshEnabled,
    required this.realApiRequestsEnabled,
    required this.realApiRequestsAllowed,
    required this.endpointVerified,
    required this.apiBaseUrlPlaceholder,
    required this.sleepApiPathConfigured,
    required this.apiTimeoutValid,
    this.message,
    this.nextAction,
    this.error,
  });

  final bool realTokenExchangeEnabled;
  final bool realTokenRefreshEnabled;
  final bool realApiRequestsEnabled;
  final bool realApiRequestsAllowed;
  final bool endpointVerified;
  final bool apiBaseUrlPlaceholder;
  final bool sleepApiPathConfigured;
  final bool apiTimeoutValid;
  final String? message;
  final String? nextAction;
  final String? error;

  factory GoogleHealthPreflightApi.fromJson(Map<String, dynamic> json) {
    return GoogleHealthPreflightApi(
      realTokenExchangeEnabled: GoogleHealthPreflight._boolFromJson(
        json['real_token_exchange_enabled'],
      ),
      realTokenRefreshEnabled: GoogleHealthPreflight._boolFromJson(
        json['real_token_refresh_enabled'],
      ),
      realApiRequestsEnabled: GoogleHealthPreflight._boolFromJson(
        json['real_api_requests_enabled'],
      ),
      realApiRequestsAllowed: GoogleHealthPreflight._boolFromJson(
        json['real_api_requests_allowed'],
      ),
      endpointVerified: GoogleHealthPreflight._boolFromJson(
        json['endpoint_verified'],
      ),
      apiBaseUrlPlaceholder: GoogleHealthPreflight._boolFromJson(
        json['api_base_url_placeholder'],
        fallback: true,
      ),
      sleepApiPathConfigured: GoogleHealthPreflight._boolFromJson(
        json['sleep_api_path_configured'],
      ),
      apiTimeoutValid: GoogleHealthPreflight._boolFromJson(
        json['api_timeout_valid'],
      ),
      message: GoogleHealthPreflight._nullableStringFromJson(json['message']),
      nextAction: GoogleHealthPreflight._nullableStringFromJson(
        json['next_action'],
      ),
      error: GoogleHealthPreflight._nullableStringFromJson(json['error']),
    );
  }
}
