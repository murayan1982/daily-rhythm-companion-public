class GoogleHealthDiagnostics {
  const GoogleHealthDiagnostics({
    required this.provider,
    required this.overallStatus,
    required this.readyForOauth,
    required this.readyForSleepProvider,
    required this.readyForRealApiRequest,
    required this.config,
    required this.runtimeGuard,
    required this.token,
    required this.message,
    this.error,
  });

  final String provider;
  final String overallStatus;
  final bool readyForOauth;
  final bool readyForSleepProvider;
  final bool readyForRealApiRequest;
  final GoogleHealthDiagnosticConfig config;
  final GoogleHealthDiagnosticRuntimeGuard runtimeGuard;
  final GoogleHealthDiagnosticToken token;
  final String message;
  final String? error;

  factory GoogleHealthDiagnostics.fromJson(Map<String, dynamic> json) {
    return GoogleHealthDiagnostics(
      provider: _stringFromJson(json['provider'], fallback: 'unknown'),
      overallStatus: _stringFromJson(
        json['overall_status'],
        fallback: 'unknown',
      ),
      readyForOauth: _boolFromJson(json['ready_for_oauth']),
      readyForSleepProvider: _boolFromJson(json['ready_for_sleep_provider']),
      readyForRealApiRequest: _boolFromJson(
        json['ready_for_real_api_request'],
      ),
      config: GoogleHealthDiagnosticConfig.fromJson(
        _mapFromJson(json['config']),
      ),
      runtimeGuard: GoogleHealthDiagnosticRuntimeGuard.fromJson(
        _mapFromJson(json['runtime_guard']),
      ),
      token: GoogleHealthDiagnosticToken.fromJson(
        _mapFromJson(json['token']),
      ),
      message: _stringFromJson(json['message']),
      error: _nullableStringFromJson(json['error']),
    );
  }

  String get displayStatus {
    switch (overallStatus) {
      case 'ready_for_real_api':
        return 'ready';
      case 'api_blocked':
        return 'guard blocked';
      case 'api_disabled':
        return 'API disabled';
      case 'needs_credentials':
        return 'credentials不足';
      case 'needs_auth':
        return 'auth不足';
      case 'mock_mode':
        return 'mock';
      default:
        return overallStatus;
    }
  }

  String get displayReason {
    if (error != null && error!.isNotEmpty) {
      return error!;
    }
    if (message.isNotEmpty) {
      return message;
    }
    return 'Google Health diagnostics の状態を確認してください。';
  }

  String get displayNextAction {
    switch (overallStatus) {
      case 'mock_mode':
        return 'SLEEP_PROVIDER=google_health に切り替えると、Google Health 経路の self-check を確認できます。';
      case 'needs_credentials':
        return 'credentials.json と GOOGLE_HEALTH_REDIRECT_URI の設定を確認してください。';
      case 'needs_auth':
        return '/google-health/connect から OAuth 認証を実行し、token snapshot を保存してください。';
      case 'api_disabled':
        return runtimeGuard.nextAction.isNotEmpty
            ? runtimeGuard.nextAction
            : 'guard は安全側です。endpoint/scope を確認してから real API flags を有効化してください。';
      case 'api_blocked':
        if (runtimeGuard.nextAction.isNotEmpty) {
          return runtimeGuard.nextAction;
        }
        return runtimeGuard.message.isNotEmpty
            ? runtimeGuard.message
            : '実API guard によりリクエストはブロックされています。';
      case 'ready_for_real_api':
        return '実APIリクエストを試せる状態です。v0.21.0 で real credentials 検証へ進めます。';
    }

    if (!config.credentialsLoaded) {
      return 'Google Health credentials の設定または読み込み状態を確認してください。';
    }
    if (!readyForOauth) {
      return 'OAuth 設定と redirect URI を確認してください。';
    }
    if (!token.stored) {
      return 'OAuth 認証を実行して token を保存してください。';
    }
    if (token.refreshRecommended == true) {
      return 'refresh token による access token 更新を確認してください。';
    }
    if (!runtimeGuard.realApiAllowed) {
      return runtimeGuard.message.isNotEmpty
          ? runtimeGuard.message
          : '実API guard によりリクエストはブロックされています。';
    }
    return message.isNotEmpty ? message : 'Google Health の状態を確認してください。';
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

class GoogleHealthDiagnosticConfig {
  const GoogleHealthDiagnosticConfig({
    required this.sleepProvider,
    required this.provider,
    required this.oauthConfigured,
    required this.credentialsFileConfigured,
    required this.credentialsLoaded,
    required this.redirectUriConfigured,
    required this.realTokenExchangeEnabled,
    required this.realTokenRefreshEnabled,
    required this.realApiRequestsEnabled,
    required this.endpointVerified,
  });

  final String sleepProvider;
  final String provider;
  final bool oauthConfigured;
  final bool credentialsFileConfigured;
  final bool credentialsLoaded;
  final bool redirectUriConfigured;
  final bool realTokenExchangeEnabled;
  final bool realTokenRefreshEnabled;
  final bool realApiRequestsEnabled;
  final bool endpointVerified;

  factory GoogleHealthDiagnosticConfig.fromJson(Map<String, dynamic> json) {
    return GoogleHealthDiagnosticConfig(
      sleepProvider: GoogleHealthDiagnostics._stringFromJson(
        json['sleep_provider'],
        fallback: 'unknown',
      ),
      provider: GoogleHealthDiagnostics._stringFromJson(
        json['provider'],
        fallback: 'unknown',
      ),
      oauthConfigured: GoogleHealthDiagnostics._boolFromJson(
        json['oauth_configured'],
      ),
      credentialsFileConfigured: GoogleHealthDiagnostics._boolFromJson(
        json['credentials_file_configured'],
      ),
      credentialsLoaded: GoogleHealthDiagnostics._boolFromJson(
        json['credentials_loaded'],
      ),
      redirectUriConfigured: GoogleHealthDiagnostics._boolFromJson(
        json['redirect_uri_configured'],
      ),
      realTokenExchangeEnabled: GoogleHealthDiagnostics._boolFromJson(
        json['real_token_exchange_enabled'],
      ),
      realTokenRefreshEnabled: GoogleHealthDiagnostics._boolFromJson(
        json['real_token_refresh_enabled'],
      ),
      realApiRequestsEnabled: GoogleHealthDiagnostics._boolFromJson(
        json['real_api_requests_enabled'],
      ),
      endpointVerified: GoogleHealthDiagnostics._boolFromJson(
        json['endpoint_verified'],
      ),
    );
  }
}

class GoogleHealthDiagnosticRuntimeGuard {
  const GoogleHealthDiagnosticRuntimeGuard({
    required this.realApiRequested,
    required this.realApiAllowed,
    required this.apiBaseUrlPlaceholder,
    required this.endpointVerified,
    required this.sleepApiPathConfigured,
    required this.apiTimeoutValid,
    required this.message,
    required this.nextAction,
    this.error,
  });

  final bool realApiRequested;
  final bool realApiAllowed;
  final bool apiBaseUrlPlaceholder;
  final bool endpointVerified;
  final bool sleepApiPathConfigured;
  final bool apiTimeoutValid;
  final String message;
  final String nextAction;
  final String? error;

  factory GoogleHealthDiagnosticRuntimeGuard.fromJson(
    Map<String, dynamic> json,
  ) {
    return GoogleHealthDiagnosticRuntimeGuard(
      realApiRequested: GoogleHealthDiagnostics._boolFromJson(
        json['real_api_requested'],
      ),
      realApiAllowed: GoogleHealthDiagnostics._boolFromJson(
        json['real_api_allowed'],
      ),
      apiBaseUrlPlaceholder: GoogleHealthDiagnostics._boolFromJson(
        json['api_base_url_placeholder'],
        fallback: true,
      ),
      endpointVerified: GoogleHealthDiagnostics._boolFromJson(
        json['endpoint_verified'],
      ),
      sleepApiPathConfigured: GoogleHealthDiagnostics._boolFromJson(
        json['sleep_api_path_configured'],
      ),
      apiTimeoutValid: GoogleHealthDiagnostics._boolFromJson(
        json['api_timeout_valid'],
      ),
      message: GoogleHealthDiagnostics._stringFromJson(json['message']),
      nextAction: GoogleHealthDiagnostics._stringFromJson(json['next_action']),
      error: GoogleHealthDiagnostics._nullableStringFromJson(json['error']),
    );
  }
}

class GoogleHealthDiagnosticToken {
  const GoogleHealthDiagnosticToken({
    required this.stored,
    required this.hasRefreshToken,
    required this.accessTokenExpired,
    required this.refreshRecommended,
    this.expiresAt,
    this.tokenType,
    required this.scopeConfigured,
  });

  final bool stored;
  final bool hasRefreshToken;
  final bool? accessTokenExpired;
  final bool? refreshRecommended;
  final String? expiresAt;
  final String? tokenType;
  final bool scopeConfigured;

  factory GoogleHealthDiagnosticToken.fromJson(Map<String, dynamic> json) {
    return GoogleHealthDiagnosticToken(
      stored: GoogleHealthDiagnostics._boolFromJson(json['stored']),
      hasRefreshToken: GoogleHealthDiagnostics._boolFromJson(
        json['has_refresh_token'],
      ),
      accessTokenExpired: GoogleHealthDiagnostics._nullableBoolFromJson(
        json['access_token_expired'],
      ),
      refreshRecommended: GoogleHealthDiagnostics._nullableBoolFromJson(
        json['refresh_recommended'],
      ),
      expiresAt: GoogleHealthDiagnostics._nullableStringFromJson(
        json['expires_at'],
      ),
      tokenType: GoogleHealthDiagnostics._nullableStringFromJson(
        json['token_type'],
      ),
      scopeConfigured: GoogleHealthDiagnostics._boolFromJson(
        json['scope_configured'],
      ),
    );
  }
}
