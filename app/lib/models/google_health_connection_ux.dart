class GoogleHealthConnectionUxStateDetail {
  const GoogleHealthConnectionUxStateDetail({
    required this.key,
    required this.label,
    required this.value,
    this.tone = 'info',
    this.guidance = '',
  });

  final String key;
  final String label;
  final String value;
  final String tone;
  final String guidance;

  factory GoogleHealthConnectionUxStateDetail.fromJson(
    Map<String, dynamic> json,
  ) {
    return GoogleHealthConnectionUxStateDetail(
      key: GoogleHealthConnectionUx._stringFromJson(json['key']),
      label: GoogleHealthConnectionUx._stringFromJson(json['label']),
      value: GoogleHealthConnectionUx._stringFromJson(json['value']),
      tone: GoogleHealthConnectionUx._stringFromJson(
        json['tone'],
        fallback: 'info',
      ),
      guidance: GoogleHealthConnectionUx._stringFromJson(json['guidance']),
    );
  }

  String get displayTone {
    switch (tone) {
      case 'ready':
        return 'ready';
      case 'warning':
        return '確認';
      case 'blocked':
        return '要対応';
      case 'info':
        return 'info';
      default:
        return tone;
    }
  }
}


class GoogleHealthConnectionUxAction {
  const GoogleHealthConnectionUxAction({
    required this.key,
    required this.label,
    required this.description,
    required this.enabled,
    this.actionType = 'review',
    this.guidance = '',
    this.expectedResult = '',
    this.riskLevel = 'safe',
    this.isDestructive = false,
  });

  final String key;
  final String label;
  final String description;
  final bool enabled;
  final String actionType;
  final String guidance;
  final String expectedResult;
  final String riskLevel;
  final bool isDestructive;

  factory GoogleHealthConnectionUxAction.fromJson(Map<String, dynamic> json) {
    return GoogleHealthConnectionUxAction(
      key: GoogleHealthConnectionUx._stringFromJson(json['key']),
      label: GoogleHealthConnectionUx._stringFromJson(json['label']),
      description: GoogleHealthConnectionUx._stringFromJson(
        json['description'],
      ),
      enabled: GoogleHealthConnectionUx._boolFromJson(json['enabled']),
      actionType: GoogleHealthConnectionUx._stringFromJson(
        json['action_type'],
        fallback: 'review',
      ),
      guidance: GoogleHealthConnectionUx._stringFromJson(json['guidance']),
      expectedResult: GoogleHealthConnectionUx._stringFromJson(
        json['expected_result'],
      ),
      riskLevel: GoogleHealthConnectionUx._stringFromJson(
        json['risk_level'],
        fallback: 'safe',
      ),
      isDestructive: GoogleHealthConnectionUx._boolFromJson(
        json['is_destructive'],
      ),
    );
  }

  String get displayActionType {
    switch (actionType) {
      case 'connect':
        return '接続';
      case 'continue':
        return '継続';
      case 'review':
        return '確認';
      case 'retry':
        return '再確認';
      case 'reset':
        return 'リセット';
      case 'safe_preview':
        return '安全プレビュー';
      case 'guarded_request':
        return '実API検証';
      default:
        return actionType;
    }
  }

  String get displayRiskLevel {
    switch (riskLevel) {
      case 'safe':
        return '安全';
      case 'safe_reset':
        return '安全側へ戻す';
      case 'destructive_local':
        return 'ローカル状態を削除';
      case 'real_api':
        return '実API';
      default:
        return riskLevel;
    }
  }
}

class GoogleHealthConnectionUx {
  const GoogleHealthConnectionUx({
    required this.provider,
    required this.state,
    required this.severity,
    required this.title,
    required this.message,
    this.statusSummary = '',
    this.userGuidance = '',
    this.safeGuardSummary = '',
    this.stateStage = '',
    this.stateReason = '',
    this.stateDetails = const [],
    required this.nextAction,
    this.recoverySteps = const [],
    this.safeModeNote = '',
    required this.primaryAction,
    required this.secondaryActions,
    this.connectionActions = const [],
    this.retryActions = const [],
    this.resetActions = const [],
    required this.sleepProvider,
    required this.tokenStored,
    required this.reconnectRecommended,
    required this.realApiRequested,
    required this.realApiAllowed,
    required this.canStartOauth,
    required this.canResetLocalToken,
    required this.canUseSafePreview,
    required this.canUseGuardedRealRequest,
    this.developerStatus,
    this.developerNote,
    this.developerSummary = '',
    this.developerDetails = const [],
    this.userVisibleDetailsLimited = true,
    this.error,
  });

  final String provider;
  final String state;
  final String severity;
  final String title;
  final String message;
  final String statusSummary;
  final String userGuidance;
  final String safeGuardSummary;
  final String stateStage;
  final String stateReason;
  final List<GoogleHealthConnectionUxStateDetail> stateDetails;
  final String nextAction;
  final List<String> recoverySteps;
  final String safeModeNote;
  final GoogleHealthConnectionUxAction? primaryAction;
  final List<GoogleHealthConnectionUxAction> secondaryActions;
  final List<GoogleHealthConnectionUxAction> connectionActions;
  final List<GoogleHealthConnectionUxAction> retryActions;
  final List<GoogleHealthConnectionUxAction> resetActions;
  final String sleepProvider;
  final bool tokenStored;
  final bool reconnectRecommended;
  final bool realApiRequested;
  final bool realApiAllowed;
  final bool canStartOauth;
  final bool canResetLocalToken;
  final bool canUseSafePreview;
  final bool canUseGuardedRealRequest;
  final String? developerStatus;
  final String? developerNote;
  final String developerSummary;
  final List<GoogleHealthConnectionUxStateDetail> developerDetails;
  final bool userVisibleDetailsLimited;
  final String? error;

  factory GoogleHealthConnectionUx.fromJson(Map<String, dynamic> json) {
    return GoogleHealthConnectionUx(
      provider: _stringFromJson(json['provider'], fallback: 'unknown'),
      state: _stringFromJson(json['state'], fallback: 'unknown'),
      severity: _stringFromJson(json['severity'], fallback: 'info'),
      title: _stringFromJson(json['title']),
      message: _stringFromJson(json['message']),
      statusSummary: _stringFromJson(json['status_summary']),
      userGuidance: _stringFromJson(json['user_guidance']),
      safeGuardSummary: _stringFromJson(json['safe_guard_summary']),
      stateStage: _stringFromJson(json['state_stage']),
      stateReason: _stringFromJson(json['state_reason']),
      stateDetails: _stateDetailsFromJson(json['state_details']),
      nextAction: _stringFromJson(json['next_action']),
      recoverySteps: _stringListFromJson(json['recovery_steps']),
      safeModeNote: _stringFromJson(json['safe_mode_note']),
      primaryAction: _actionFromJson(json['primary_action']),
      secondaryActions: _actionsFromJson(json['secondary_actions']),
      connectionActions: _actionsFromJson(json['connection_actions']),
      retryActions: _actionsFromJson(json['retry_actions']),
      resetActions: _actionsFromJson(json['reset_actions']),
      sleepProvider: _stringFromJson(
        json['sleep_provider'],
        fallback: 'unknown',
      ),
      tokenStored: _boolFromJson(json['token_stored']),
      reconnectRecommended: _boolFromJson(json['reconnect_recommended']),
      realApiRequested: _boolFromJson(json['real_api_requested']),
      realApiAllowed: _boolFromJson(json['real_api_allowed']),
      canStartOauth: _boolFromJson(json['can_start_oauth']),
      canResetLocalToken: _boolFromJson(json['can_reset_local_token']),
      canUseSafePreview: _boolFromJson(json['can_use_safe_preview']),
      canUseGuardedRealRequest: _boolFromJson(
        json['can_use_guarded_real_request'],
      ),
      developerStatus: _nullableStringFromJson(json['developer_status']),
      developerNote: _nullableStringFromJson(json['developer_note']),
      developerSummary: _stringFromJson(json['developer_summary']),
      developerDetails: _stateDetailsFromJson(json['developer_details']),
      userVisibleDetailsLimited: _boolFromJson(
        json['user_visible_details_limited'],
        fallback: true,
      ),
      error: _nullableStringFromJson(json['error']),
    );
  }

  bool get hasRecoverySteps => recoverySteps.isNotEmpty;

  bool get hasStateDetails => stateDetails.isNotEmpty;

  bool get hasUserGuidance => userGuidance.isNotEmpty;

  bool get hasSafeGuardSummary => safeGuardSummary.isNotEmpty;

  bool get hasDeveloperSummary => developerSummary.isNotEmpty;

  bool get hasDeveloperDetails => developerDetails.isNotEmpty;

  bool get hasDeveloperPanel =>
      hasDeveloperSummary || hasDeveloperDetails || developerNote != null;

  bool get hasSecondaryActions => secondaryActions.isNotEmpty;

  List<GoogleHealthConnectionUxAction> get displayConnectionActions {
    if (connectionActions.isNotEmpty) {
      return connectionActions;
    }

    final actions = <GoogleHealthConnectionUxAction>[];
    if (primaryAction != null) {
      actions.add(primaryAction!);
    }
    actions.addAll(secondaryActions);
    return actions;
  }

  bool get hasConnectionActions => displayConnectionActions.isNotEmpty;

  bool get hasRetryActions => retryActions.isNotEmpty;

  bool get hasResetActions => resetActions.isNotEmpty;

  String get displayState {
    switch (state) {
      case 'mock_mode':
        return 'モックモード';
      case 'not_configured':
        return '未設定';
      case 'authorization_required':
        return '認証が必要';
      case 'reconnect_required':
        return '再接続が必要';
      case 'reauthorization_recommended':
        return '再認証が必要';
      case 'token_unavailable':
        return 'token確認が必要';
      case 'real_request_disabled':
        return '接続済み / 実API OFF';
      case 'guarded_real_request_ready':
        return '実API検証準備OK';
      case 'needs_review':
        return '確認が必要';
      default:
        return state;
    }
  }

  String get displaySeverity {
    switch (severity) {
      case 'ready':
        return 'ready';
      case 'warning':
        return '確認';
      case 'blocked':
        return '要設定';
      case 'info':
        return 'info';
      default:
        return severity;
    }
  }

  String get displayProvider {
    switch (provider) {
      case 'google_health':
        return 'Google Health';
      default:
        return provider;
    }
  }

  String get displaySleepProvider {
    switch (sleepProvider) {
      case 'google_health':
        return 'Google Health';
      case 'mock':
        return 'モック';
      default:
        return sleepProvider;
    }
  }

  String get displaySafeRealApiState {
    if (canUseGuardedRealRequest) {
      return '明示フラグON / guarded real request可能';
    }
    if (realApiAllowed) {
      return '許可状態ですが、UI上は慎重に扱ってください';
    }
    if (realApiRequested) {
      return 'リクエスト要求あり / guardで未許可';
    }
    return 'OFF / 安全ガード中';
  }

  static GoogleHealthConnectionUxAction? _actionFromJson(Object? value) {
    final map = _mapFromJson(value);
    if (map.isEmpty) {
      return null;
    }
    return GoogleHealthConnectionUxAction.fromJson(map);
  }

  static List<GoogleHealthConnectionUxStateDetail> _stateDetailsFromJson(
    Object? value,
  ) {
    if (value is! List) {
      return const [];
    }

    return value
        .map(_mapFromJson)
        .where((item) => item.isNotEmpty)
        .map(GoogleHealthConnectionUxStateDetail.fromJson)
        .toList(growable: false);
  }

  static List<GoogleHealthConnectionUxAction> _actionsFromJson(Object? value) {
    if (value is! List) {
      return const [];
    }

    return value
        .map(_mapFromJson)
        .where((item) => item.isNotEmpty)
        .map(GoogleHealthConnectionUxAction.fromJson)
        .toList(growable: false);
  }

  static List<String> _stringListFromJson(Object? value) {
    if (value is! List) {
      return const [];
    }

    return value
        .map(_nullableStringFromJson)
        .whereType<String>()
        .where((item) => item.isNotEmpty)
        .toList(growable: false);
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
