class SleepProviderOption {
  const SleepProviderOption({
    required this.provider,
    required this.displayLabel,
    required this.role,
    this.deprecated = false,
    this.aliasFor,
    this.realOperatorVerificationRequired = false,
  });

  final String provider;
  final String displayLabel;
  final String role;
  final bool deprecated;
  final String? aliasFor;
  final bool realOperatorVerificationRequired;

  factory SleepProviderOption.fromJson(Map<String, dynamic> json) {
    return SleepProviderOption(
      provider: json['provider']?.toString() ?? 'unknown',
      displayLabel: json['display_label']?.toString() ?? '未確認',
      role: json['role']?.toString() ?? 'unknown',
      deprecated: json['deprecated'] as bool? ?? false,
      aliasFor: json['alias_for']?.toString(),
      realOperatorVerificationRequired:
          json['real_operator_verification_required'] as bool? ?? false,
    );
  }

  String get displayRole {
    switch (role) {
      case 'credential_free_default':
        return '安全な既定';
      case 'deterministic_sample':
        return 'デモ用サンプル';
      case 'configured_real_provider':
        return '設定済み実データ候補';
      case 'deprecated_alias':
        return '旧設定';
      case 'legacy_real_provider':
        return '実利用検証待ち';
      default:
        return role;
    }
  }
}

class SleepProviderSelectionStatus {
  const SleepProviderSelectionStatus({
    required this.configuredProvider,
    required this.configuredProviderLabel,
    required this.configuredProviderRole,
    required this.configuredProviderSupported,
    required this.selectionMode,
    required this.changeRequiresBackendRestart,
    required this.availableProviders,
    required this.message,
  });

  final String configuredProvider;
  final String configuredProviderLabel;
  final String configuredProviderRole;
  final bool configuredProviderSupported;
  final String selectionMode;
  final bool changeRequiresBackendRestart;
  final List<SleepProviderOption> availableProviders;
  final String message;

  factory SleepProviderSelectionStatus.fromJson(Map<String, dynamic> json) {
    final rawProviders = json['available_providers'];

    return SleepProviderSelectionStatus(
      configuredProvider:
          json['configured_provider']?.toString() ?? 'unknown',
      configuredProviderLabel:
          json['configured_provider_label']?.toString() ?? '未確認',
      configuredProviderRole:
          json['configured_provider_role']?.toString() ?? 'unknown',
      configuredProviderSupported:
          json['configured_provider_supported'] as bool? ?? false,
      selectionMode: json['selection_mode']?.toString() ?? 'backend_config',
      changeRequiresBackendRestart:
          json['change_requires_backend_restart'] as bool? ?? true,
      availableProviders: rawProviders is List
          ? rawProviders
              .whereType<Map<String, dynamic>>()
              .map(SleepProviderOption.fromJson)
              .toList(growable: false)
          : const [],
      message: json['message']?.toString() ?? '',
    );
  }

  SleepProviderOption? get configuredOption {
    for (final option in availableProviders) {
      if (option.provider == configuredProvider) {
        return option;
      }
    }
    return null;
  }

  bool get isGoogleHealth => configuredProvider == 'google_health';

  bool get isFitbit => configuredProvider == 'fitbit';

  bool get isMockSafeProvider =>
      configuredProvider == 'mock' ||
      configuredProvider == 'wearable_stub' ||
      configuredProvider == 'fitbit_stub';

  bool get requiresRealOperatorVerification =>
      configuredOption?.realOperatorVerificationRequired ?? false;

  String get displaySelectionMode {
    switch (selectionMode) {
      case 'backend_config':
        return 'バックエンド設定';
      default:
        return selectionMode;
    }
  }

  String get displayConfiguredState {
    if (!configuredProviderSupported) {
      return '未対応';
    }
    if (configuredOption?.deprecated == true) {
      return '旧設定';
    }
    if (requiresRealOperatorVerification) {
      return '実利用検証待ち';
    }
    if (isMockSafeProvider) {
      return 'デモ利用中';
    }
    return '設定済み';
  }
}
