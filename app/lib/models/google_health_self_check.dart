class GoogleHealthSelfCheck {
  const GoogleHealthSelfCheck({
    required this.provider,
    required this.targetDate,
    required this.diagnosticsStatus,
    required this.sourceStatus,
    required this.safeToUseSleepSummary,
    required this.realHttpAttempted,
    this.session,
    required this.message,
    this.error,
  });

  final String provider;
  final String targetDate;
  final String diagnosticsStatus;
  final String sourceStatus;
  final bool safeToUseSleepSummary;
  final bool realHttpAttempted;
  final GoogleHealthSelfCheckSession? session;
  final String message;
  final String? error;

  factory GoogleHealthSelfCheck.fromJson(Map<String, dynamic> json) {
    return GoogleHealthSelfCheck(
      provider: _stringFromJson(json['provider'], fallback: 'unknown'),
      targetDate: _stringFromJson(json['target_date']),
      diagnosticsStatus: _stringFromJson(
        json['diagnostics_status'],
        fallback: 'unknown',
      ),
      sourceStatus: _stringFromJson(
        json['source_status'],
        fallback: 'unknown',
      ),
      safeToUseSleepSummary: _boolFromJson(json['safe_to_use_sleep_summary']),
      realHttpAttempted: _boolFromJson(json['real_http_attempted']),
      session: json['session'] == null
          ? null
          : GoogleHealthSelfCheckSession.fromJson(_mapFromJson(json['session'])),
      message: _stringFromJson(json['message']),
      error: _nullableStringFromJson(json['error']),
    );
  }

  String get displaySourceStatus {
    switch (sourceStatus) {
      case 'ready':
        return 'ready';
      case 'blocked':
        return 'guard blocked';
      case 'mock':
        return 'mock';
      case 'missing_auth':
        return 'auth不足';
      case 'missing_credentials':
        return 'credentials不足';
      case 'skipped':
        return 'skipped';
      case 'error':
        return 'error';
      default:
        return sourceStatus;
    }
  }

  String get displayReason {
    final sessionError = session?.error;
    if (sessionError != null && sessionError.isNotEmpty) {
      return sessionError;
    }
    if (error != null && error!.isNotEmpty) {
      return error!;
    }
    if (message.isNotEmpty) {
      return message;
    }
    return 'Google Health self-check の結果を確認してください。';
  }

  String get displayNextAction {
    if (sourceStatus == 'skipped') {
      return 'SLEEP_PROVIDER=google_health に切り替えると、sleep source 経路を確認できます。';
    }

    if (safeToUseSleepSummary && !realHttpAttempted) {
      return 'sleep summary 側の安全確認はOKです。実HTTPはまだブロックされています。';
    }

    if (safeToUseSleepSummary && realHttpAttempted) {
      return '実HTTPを含む sleep summary 経路を確認しました。';
    }

    final refresh = session?.refresh;
    if (refresh != null && refresh.error != null && refresh.error!.isNotEmpty) {
      return refresh.error!;
    }

    final api = session?.api;
    if (api != null && api.error != null && api.error!.isNotEmpty) {
      return api.error!;
    }

    final sessionError = session?.error;
    if (sessionError != null && sessionError.isNotEmpty) {
      return sessionError;
    }

    if (error != null && error!.isNotEmpty) {
      return error!;
    }

    return message.isNotEmpty ? message : 'self-check の結果を確認してください。';
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

  static int? _nullableIntFromJson(Object? value) {
    if (value is int) {
      return value;
    }
    if (value is num) {
      return value.toInt();
    }
    if (value is String) {
      return int.tryParse(value.trim());
    }
    return null;
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

class GoogleHealthSelfCheckSession {
  const GoogleHealthSelfCheckSession({
    required this.tokenAvailable,
    required this.refreshChecked,
    required this.apiRequested,
    required this.succeeded,
    this.endpoint,
    this.refresh,
    this.api,
    this.message,
    this.error,
  });

  final bool tokenAvailable;
  final bool refreshChecked;
  final bool apiRequested;
  final bool succeeded;
  final String? endpoint;
  final GoogleHealthSelfCheckRefresh? refresh;
  final GoogleHealthSelfCheckApi? api;
  final String? message;
  final String? error;

  factory GoogleHealthSelfCheckSession.fromJson(Map<String, dynamic> json) {
    return GoogleHealthSelfCheckSession(
      tokenAvailable: GoogleHealthSelfCheck._boolFromJson(
        json['token_available'],
      ),
      refreshChecked: GoogleHealthSelfCheck._boolFromJson(
        json['refresh_checked'],
      ),
      apiRequested: GoogleHealthSelfCheck._boolFromJson(json['api_requested']),
      succeeded: GoogleHealthSelfCheck._boolFromJson(json['succeeded']),
      endpoint: GoogleHealthSelfCheck._nullableStringFromJson(json['endpoint']),
      refresh: json['refresh'] == null
          ? null
          : GoogleHealthSelfCheckRefresh.fromJson(
              GoogleHealthSelfCheck._mapFromJson(json['refresh']),
            ),
      api: json['api'] == null
          ? null
          : GoogleHealthSelfCheckApi.fromJson(
              GoogleHealthSelfCheck._mapFromJson(json['api']),
            ),
      message: GoogleHealthSelfCheck._nullableStringFromJson(json['message']),
      error: GoogleHealthSelfCheck._nullableStringFromJson(json['error']),
    );
  }
}

class GoogleHealthSelfCheckRefresh {
  const GoogleHealthSelfCheckRefresh({
    required this.checked,
    required this.attempted,
    required this.requestPrepared,
    required this.realRefreshEnabled,
    required this.refreshed,
    required this.saved,
    this.message,
    this.error,
  });

  final bool checked;
  final bool attempted;
  final bool requestPrepared;
  final bool realRefreshEnabled;
  final bool refreshed;
  final bool saved;
  final String? message;
  final String? error;

  factory GoogleHealthSelfCheckRefresh.fromJson(Map<String, dynamic> json) {
    return GoogleHealthSelfCheckRefresh(
      checked: GoogleHealthSelfCheck._boolFromJson(json['checked']),
      attempted: GoogleHealthSelfCheck._boolFromJson(json['attempted']),
      requestPrepared: GoogleHealthSelfCheck._boolFromJson(
        json['request_prepared'],
      ),
      realRefreshEnabled: GoogleHealthSelfCheck._boolFromJson(
        json['real_refresh_enabled'],
      ),
      refreshed: GoogleHealthSelfCheck._boolFromJson(json['refreshed']),
      saved: GoogleHealthSelfCheck._boolFromJson(json['saved']),
      message: GoogleHealthSelfCheck._nullableStringFromJson(json['message']),
      error: GoogleHealthSelfCheck._nullableStringFromJson(json['error']),
    );
  }
}

class GoogleHealthSelfCheckApi {
  const GoogleHealthSelfCheckApi({
    required this.requested,
    required this.attempted,
    required this.requestPrepared,
    required this.realApiEnabled,
    required this.succeeded,
    this.statusCode,
    this.message,
    this.error,
  });

  final bool requested;
  final bool attempted;
  final bool requestPrepared;
  final bool realApiEnabled;
  final bool succeeded;
  final int? statusCode;
  final String? message;
  final String? error;

  factory GoogleHealthSelfCheckApi.fromJson(Map<String, dynamic> json) {
    return GoogleHealthSelfCheckApi(
      requested: GoogleHealthSelfCheck._boolFromJson(json['requested']),
      attempted: GoogleHealthSelfCheck._boolFromJson(json['attempted']),
      requestPrepared: GoogleHealthSelfCheck._boolFromJson(
        json['request_prepared'],
      ),
      realApiEnabled: GoogleHealthSelfCheck._boolFromJson(
        json['real_api_enabled'],
      ),
      succeeded: GoogleHealthSelfCheck._boolFromJson(json['succeeded']),
      statusCode: GoogleHealthSelfCheck._nullableIntFromJson(
        json['status_code'],
      ),
      message: GoogleHealthSelfCheck._nullableStringFromJson(json['message']),
      error: GoogleHealthSelfCheck._nullableStringFromJson(json['error']),
    );
  }
}
