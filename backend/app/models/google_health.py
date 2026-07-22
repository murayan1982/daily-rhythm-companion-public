from pydantic import BaseModel, Field


class GoogleHealthStatusResponse(BaseModel):
    configured: bool
    credentials_loaded: bool
    redirect_uri_configured: bool
    provider: str
    message: str
    error: str | None = None
    real_token_exchange_enabled: bool = False
    real_token_refresh_enabled: bool = False
    real_api_requests_enabled: bool = False
    real_api_requests_allowed: bool = False
    endpoint_verified: bool = False
    real_api_opt_in: bool = False
    api_base_url_placeholder: bool = True
    sleep_api_path_configured: bool = True
    api_timeout_valid: bool = True


class GoogleHealthConnectResponse(BaseModel):
    ready: bool
    connect_url: str | None = None
    state: str | None = None
    message: str
    error: str | None = None


class GoogleHealthTokenRequestPreviewModel(BaseModel):
    endpoint: str
    grant_type: str
    redirect_uri: str
    has_client_id: bool
    has_client_secret: bool
    has_code: bool


class GoogleHealthCallbackResponse(BaseModel):
    received_code: bool
    received_state: bool
    state_valid: bool = False
    state_expired: bool = False
    token_exchange_attempted: bool = False
    token_request_prepared: bool = False
    real_token_exchange_enabled: bool = False
    token_saved: bool = False
    message: str
    error: str | None = None
    error_description: str | None = None
    token_request_preview: GoogleHealthTokenRequestPreviewModel | None = None


class GoogleHealthDiagnosticConfigModel(BaseModel):
    sleep_provider: str
    provider: str
    oauth_configured: bool
    credentials_file_configured: bool
    credentials_loaded: bool
    redirect_uri_configured: bool
    real_token_exchange_enabled: bool
    real_token_refresh_enabled: bool
    real_api_requests_enabled: bool
    endpoint_verified: bool
    real_api_opt_in: bool


class GoogleHealthDiagnosticRuntimeGuardModel(BaseModel):
    real_api_requested: bool
    real_api_allowed: bool
    api_base_url_placeholder: bool
    endpoint_verified: bool
    real_api_opt_in: bool
    sleep_api_path_configured: bool
    api_timeout_valid: bool
    message: str
    next_action: str
    error: str | None = None


class GoogleHealthDiagnosticTokenModel(BaseModel):
    stored: bool
    has_refresh_token: bool = False
    access_token_expired: bool | None = None
    refresh_recommended: bool | None = None
    expires_at: str | None = None
    token_type: str | None = None
    scope_configured: bool = False


class GoogleHealthDiagnosticsResponse(BaseModel):
    provider: str
    overall_status: str
    ready_for_oauth: bool
    ready_for_sleep_provider: bool
    ready_for_real_api_request: bool
    config: GoogleHealthDiagnosticConfigModel
    runtime_guard: GoogleHealthDiagnosticRuntimeGuardModel
    token: GoogleHealthDiagnosticTokenModel
    message: str
    error: str | None = None


class GoogleHealthApiRequestPreviewModel(BaseModel):
    endpoint: str
    method: str
    has_bearer_auth: bool
    query_param_keys: list[str]
    query_params: dict[str, str] = Field(default_factory=dict)
    preview_url: str


class GoogleHealthProviderErrorSummaryModel(BaseModel):
    http_status_code: int | None = None
    provider_error_code: int | None = None
    provider_error_status: str | None = None
    provider_error_message_hint: str | None = None
    provider_error_reason: str | None = None
    provider_error_domain: str | None = None
    provider_error_metadata_keys: list[str] = Field(default_factory=list)
    www_authenticate_hint: str | None = None
    suggested_cause: str | None = None


class GoogleHealthSelfCheckRefreshModel(BaseModel):
    checked: bool
    attempted: bool = False
    request_prepared: bool = False
    real_refresh_enabled: bool = False
    refreshed: bool = False
    saved: bool = False
    message: str | None = None
    error: str | None = None


class GoogleHealthSelfCheckApiModel(BaseModel):
    requested: bool
    attempted: bool = False
    request_prepared: bool = False
    real_api_enabled: bool = False
    succeeded: bool = False
    status_code: int | None = None
    request_preview: GoogleHealthApiRequestPreviewModel | None = None
    provider_error_category: str | None = None
    provider_error_summary: GoogleHealthProviderErrorSummaryModel | None = None
    message: str | None = None
    error: str | None = None


class GoogleHealthSelfCheckSessionModel(BaseModel):
    token_available: bool
    refresh_checked: bool
    api_requested: bool
    succeeded: bool
    endpoint: str | None = None
    refresh: GoogleHealthSelfCheckRefreshModel | None = None
    api: GoogleHealthSelfCheckApiModel | None = None
    message: str | None = None
    error: str | None = None


class GoogleHealthSelfCheckResponse(BaseModel):
    provider: str
    target_date: str
    diagnostics_status: str
    source_status: str
    safe_to_use_sleep_summary: bool
    real_http_attempted: bool
    session: GoogleHealthSelfCheckSessionModel | None = None
    message: str
    error: str | None = None


class GoogleHealthRefreshRequestPreviewModel(BaseModel):
    endpoint: str
    grant_type: str
    has_client_id: bool
    has_client_secret: bool
    has_refresh_token: bool


class GoogleHealthTokenRefreshCheckResponse(BaseModel):
    provider: str
    credentials_loaded: bool
    token_stored: bool
    refresh_recommended: bool | None = None
    real_token_refresh_enabled: bool
    attempted: bool = False
    request_prepared: bool = False
    refreshed: bool = False
    saved: bool = False
    request_preview: GoogleHealthRefreshRequestPreviewModel | None = None
    message: str
    error: str | None = None


class GoogleHealthScopeCheckResponse(BaseModel):
    provider: str
    required_sleep_scope_configured: bool
    required_sleep_scope: str | None = None
    configured_scopes: list[str]
    configured_scope_count: int
    token_stored: bool
    token_scope_configured: bool
    token_scopes: list[str]
    token_scope_count: int
    missing_configured_scopes_in_token: list[str]
    missing_required_scopes_in_token: list[str] = []
    missing_optional_configured_scopes_in_token: list[str] = []
    required_sleep_scope_in_config: bool | None = None
    required_sleep_scope_in_token: bool | None = None
    reconnect_recommended: bool
    ready_for_permission_retest: bool
    message: str
    next_action: str
    error: str | None = None




class GoogleHealthPermissionRetestReadinessResponse(BaseModel):
    provider: str
    status: str
    ready_for_guarded_permission_retest: bool
    scope_ready: bool
    cloud_api_enabled_confirmed: bool
    oauth_consent_sleep_scope_confirmed: bool
    oauth_test_user_confirmed: bool
    endpoint_query_confirmed: bool
    required_sleep_scope: str | None = None
    confirmed_checks: list[str] = Field(default_factory=list)
    unresolved_checks: list[str] = Field(default_factory=list)
    message: str
    next_action: str
    error: str | None = None


class GoogleHealthProjectAccessReadinessResponse(BaseModel):
    provider: str
    status: str
    ready_for_access_retest: bool
    credentials_file_configured: bool
    credentials_loaded: bool
    credentials_error: str | None = None
    credentials_project_id_present: bool = False
    credentials_project_id_hash: str | None = None
    credentials_project_id_suffix: str | None = None
    credentials_client_id_present: bool = False
    credentials_client_id_hash: str | None = None
    credentials_client_id_suffix: str | None = None
    expected_client_id_configured: bool = False
    expected_client_id_hash: str | None = None
    expected_client_id_suffix: str | None = None
    client_id_matches_expected: bool | None = None
    cloud_api_enabled_confirmed: bool
    oauth_consent_sleep_scope_confirmed: bool
    oauth_test_user_confirmed: bool
    endpoint_query_confirmed: bool
    data_access_scope_confirmed: bool
    oauth_publishing_status_testing_confirmed: bool
    oauth_user_type_external_confirmed: bool
    test_user_email_confirmed: bool
    access_approval_confirmed: bool
    confirmed_checks: list[str] = Field(default_factory=list)
    unresolved_checks: list[str] = Field(default_factory=list)
    message: str
    next_action: str
    error: str | None = None


class GoogleHealthCodelabExerciseCheckResponse(BaseModel):
    provider: str
    codelab_reference: str
    endpoint: str
    real_http_attempted: bool
    safe_to_use_raw_payload: bool = False
    data_point_count: int | None = None
    data_points_present: bool | None = None
    next_page_token_present: bool | None = None
    session: GoogleHealthSelfCheckSessionModel | None = None
    message: str
    next_action: str
    error: str | None = None


class GoogleHealthConnectionChecklistItemModel(BaseModel):
    key: str
    label: str
    ok: bool
    status: str
    message: str
    next_action: str


class GoogleHealthConnectionChecklistCommandModel(BaseModel):
    oauth_helper: str
    reset_dry_run: str
    reset_apply: str
    config_check: str
    connection_checklist: str
    safe_preview: str


class GoogleHealthConnectionChecklistResponse(BaseModel):
    provider: str
    status: str
    ready_for_local_oauth: bool
    ready_for_reauthorization: bool
    ready_for_safe_preview: bool
    ready_for_guarded_real_request: bool
    reconnect_recommended: bool
    recommended_sleep_scope: str
    configured_scopes: list[str]
    mixed_scope_warnings: list[str] = Field(default_factory=list)
    token_store_configured: bool
    token_stored: bool
    required_sleep_scope_in_config: bool | None = None
    required_sleep_scope_in_token: bool | None = None
    real_api_requested: bool
    real_api_allowed: bool
    runtime_guard_error: str | None = None
    checks: list[GoogleHealthConnectionChecklistItemModel] = Field(default_factory=list)
    commands: GoogleHealthConnectionChecklistCommandModel
    message: str
    next_action: str
    error: str | None = None


class GoogleHealthConnectionUxStateDetailModel(BaseModel):
    key: str
    label: str
    value: str
    tone: str = "info"
    guidance: str = ""


class GoogleHealthConnectionUxActionModel(BaseModel):
    key: str
    label: str
    description: str
    enabled: bool
    action_type: str = "review"
    guidance: str = ""
    expected_result: str = ""
    risk_level: str = "safe"
    is_destructive: bool = False


class GoogleHealthConnectionUxResponse(BaseModel):
    provider: str
    state: str
    severity: str
    title: str
    message: str
    status_summary: str = ""
    user_guidance: str = ""
    safe_guard_summary: str = ""
    state_stage: str = ""
    state_reason: str = ""
    state_details: list[GoogleHealthConnectionUxStateDetailModel] = Field(default_factory=list)
    next_action: str
    recovery_steps: list[str] = Field(default_factory=list)
    safe_mode_note: str = ""
    primary_action: GoogleHealthConnectionUxActionModel | None = None
    secondary_actions: list[GoogleHealthConnectionUxActionModel] = Field(default_factory=list)
    connection_actions: list[GoogleHealthConnectionUxActionModel] = Field(default_factory=list)
    retry_actions: list[GoogleHealthConnectionUxActionModel] = Field(default_factory=list)
    reset_actions: list[GoogleHealthConnectionUxActionModel] = Field(default_factory=list)

    sleep_provider: str
    token_stored: bool
    reconnect_recommended: bool
    real_api_requested: bool
    real_api_allowed: bool

    can_start_oauth: bool
    can_reset_local_token: bool
    can_use_safe_preview: bool
    can_use_guarded_real_request: bool

    developer_status: str | None = None
    developer_note: str | None = None
    developer_summary: str = ""
    developer_details: list[GoogleHealthConnectionUxStateDetailModel] = Field(default_factory=list)
    user_visible_details_limited: bool = True
    error: str | None = None

class GoogleHealthPreflightCredentialsModel(BaseModel):
    credentials_file_configured: bool
    credentials_file_exists: bool
    credentials_loaded: bool
    client_id_configured: bool = False
    client_secret_configured: bool = False
    redirect_uri_configured: bool
    redirect_uri_registered: bool | None = None
    message: str | None = None
    error: str | None = None


class GoogleHealthPreflightOAuthModel(BaseModel):
    scopes_configured: bool
    scope_count: int
    auth_url_ready: bool
    state_ready: bool
    message: str | None = None
    error: str | None = None


class GoogleHealthPreflightTokenModel(BaseModel):
    stored: bool
    has_refresh_token: bool = False
    access_token_expired: bool | None = None
    refresh_recommended: bool | None = None
    scope_configured: bool = False


class GoogleHealthPreflightApiModel(BaseModel):
    real_token_exchange_enabled: bool
    real_token_refresh_enabled: bool
    real_api_requests_enabled: bool
    real_api_requests_allowed: bool
    endpoint_verified: bool
    real_api_opt_in: bool
    api_base_url_placeholder: bool
    sleep_api_path_configured: bool
    api_timeout_valid: bool
    message: str | None = None
    next_action: str | None = None
    error: str | None = None


class GoogleHealthPreflightResponse(BaseModel):
    provider: str
    status: str
    ready_for_oauth: bool
    ready_for_auth_callback: bool
    ready_for_token_refresh: bool
    ready_for_real_api_request: bool
    credentials: GoogleHealthPreflightCredentialsModel
    oauth: GoogleHealthPreflightOAuthModel
    token: GoogleHealthPreflightTokenModel
    api: GoogleHealthPreflightApiModel
    message: str
    next_action: str
    error: str | None = None
