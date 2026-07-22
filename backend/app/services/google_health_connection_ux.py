from __future__ import annotations

from app.config import AppConfig
from app.models.google_health import (
    GoogleHealthConnectionChecklistResponse,
    GoogleHealthConnectionUxActionModel,
    GoogleHealthConnectionUxResponse,
    GoogleHealthConnectionUxStateDetailModel,
)
from app.services.google_health_connection_checklist import (
    get_google_health_connection_checklist,
)
from app.services.google_health_service import GOOGLE_HEALTH_PROVIDER_NAME
from app.services.google_health_token_store import GoogleHealthTokenStore


GOOGLE_HEALTH_CONNECTION_UX_STATE_MOCK_MODE = "mock_mode"
GOOGLE_HEALTH_CONNECTION_UX_STATE_NOT_CONFIGURED = "not_configured"
GOOGLE_HEALTH_CONNECTION_UX_STATE_AUTHORIZATION_REQUIRED = "authorization_required"
GOOGLE_HEALTH_CONNECTION_UX_STATE_RECONNECT_REQUIRED = "reconnect_required"
GOOGLE_HEALTH_CONNECTION_UX_STATE_TOKEN_UNAVAILABLE = "token_unavailable"
GOOGLE_HEALTH_CONNECTION_UX_STATE_REAL_REQUEST_DISABLED = "real_request_disabled"
GOOGLE_HEALTH_CONNECTION_UX_STATE_GUARDED_REAL_REQUEST_READY = "guarded_real_request_ready"
GOOGLE_HEALTH_CONNECTION_UX_STATE_NEEDS_REVIEW = "needs_review"

# Backward-compatible name kept for older scripts/tests that imported the v0.37
# constant. The app-facing state value is now the clearer v0.38 name.
GOOGLE_HEALTH_CONNECTION_UX_STATE_REAUTHORIZATION_RECOMMENDED = (
    GOOGLE_HEALTH_CONNECTION_UX_STATE_RECONNECT_REQUIRED
)

GOOGLE_HEALTH_CONNECTION_UX_SEVERITY_INFO = "info"
GOOGLE_HEALTH_CONNECTION_UX_SEVERITY_READY = "ready"
GOOGLE_HEALTH_CONNECTION_UX_SEVERITY_WARNING = "warning"
GOOGLE_HEALTH_CONNECTION_UX_SEVERITY_BLOCKED = "blocked"

GOOGLE_HEALTH_CONNECTION_ACTION_TYPE_CONNECT = "connect"
GOOGLE_HEALTH_CONNECTION_ACTION_TYPE_CONTINUE = "continue"
GOOGLE_HEALTH_CONNECTION_ACTION_TYPE_REVIEW = "review"
GOOGLE_HEALTH_CONNECTION_ACTION_TYPE_RETRY = "retry"
GOOGLE_HEALTH_CONNECTION_ACTION_TYPE_RESET = "reset"
GOOGLE_HEALTH_CONNECTION_ACTION_TYPE_SAFE_PREVIEW = "safe_preview"
GOOGLE_HEALTH_CONNECTION_ACTION_TYPE_GUARDED_REQUEST = "guarded_request"

_SAFE_MODE_NOTE = (
    "mock-safe が既定です。Google Health の実APIは、明示的な guarded real request "
    "用フラグが揃うまで呼び出しません。"
)
_DEVELOPER_NOTE = (
    "このUXレスポンスは token / secret / local path / raw command / raw health payload "
    "を含めないユーザー向けサマリーです。詳細確認は developer check 側に寄せます。"
)


def get_google_health_connection_ux(
    *,
    config: AppConfig,
    token_store: GoogleHealthTokenStore | None = None,
) -> GoogleHealthConnectionUxResponse:
    """
    Build a safe, user-facing Google Health connection status view.

    This wraps the developer-facing connection checklist and intentionally
    omits token file paths, helper commands, credential details, token values,
    authorization headers, and raw Google Health payloads.
    """

    checklist = get_google_health_connection_checklist(
        config=config,
        token_store=token_store,
    )

    if config.sleep_provider != GOOGLE_HEALTH_PROVIDER_NAME:
        return _response(
            checklist=checklist,
            config=config,
            state=GOOGLE_HEALTH_CONNECTION_UX_STATE_MOCK_MODE,
            severity=GOOGLE_HEALTH_CONNECTION_UX_SEVERITY_INFO,
            title="モック睡眠データで動作中",
            message="現在はGoogle Health連携ではなく、開発用のモック睡眠データを使っています。",
            status_summary="通常のローカル開発では安全なモック睡眠データを使います。",
            next_action=(
                "通常のローカル開発ではこの状態でOKです。Google Health連携を試す場合は"
                "SLEEP_PROVIDER=google_health に切り替えてから設定状態を確認してください。"
            ),
            recovery_steps=[
                "日次ループやUI確認は、このままモック睡眠データで続ける。",
                "Google Healthを試す時だけ、sleep providerをgoogle_healthに切り替える。",
                "切り替え後に接続状態をRefreshして、不足している設定だけ確認する。",
            ],
            primary_action=_action(
                key="keep_mock_mode",
                label="このまま使う",
                description="通常の開発・UI確認はモックモードで安全に続けられます。",
                enabled=True,
                action_type=GOOGLE_HEALTH_CONNECTION_ACTION_TYPE_CONTINUE,
                guidance="日次ループ確認を優先する場合の安全な継続アクションです。",
                expected_result="Google Health実APIを呼ばずに、mock sleep summaryでHome画面を確認できます。",
            ),
            secondary_actions=[
                _action(
                    key="review_google_health_setup_later",
                    label="Google Health設定は後で確認",
                    description="実データ連携の検証時だけ、接続設定とOAuth状態を確認します。",
                    enabled=True,
                    action_type=GOOGLE_HEALTH_CONNECTION_ACTION_TYPE_REVIEW,
                    guidance="今は接続せず、必要になった時だけ設定状態を確認します。",
                    expected_result="mock-safeのまま、Google Health接続作業を先送りできます。",
                ),
            ],
            error=None,
        )

    if not checklist.ready_for_local_oauth:
        return _response(
            checklist=checklist,
            config=config,
            state=GOOGLE_HEALTH_CONNECTION_UX_STATE_NOT_CONFIGURED,
            severity=GOOGLE_HEALTH_CONNECTION_UX_SEVERITY_BLOCKED,
            title="Google Health連携の設定が未完了です",
            message="Google HealthのOAuth設定に不足があります。認証を開始する前に設定を確認してください。",
            status_summary="接続開始前の設定がまだ揃っていません。",
            next_action="OAuth設定を確認し、不足項目を直してから接続状態を再読み込みしてください。",
            recovery_steps=[
                "credentials と redirect URI が設定済みか確認する。",
                "OAuth scope がGoogle Health sleep read用の最小scopeになっているか確認する。",
                "設定を直したらRefreshして、接続開始できる状態か確認する。",
            ],
            primary_action=_action(
                key="review_google_health_setup",
                label="設定を確認する",
                description="credentials、redirect URI、sleep scopeの不足を確認します。",
                enabled=True,
                action_type=GOOGLE_HEALTH_CONNECTION_ACTION_TYPE_REVIEW,
                guidance="接続ボタンを押す前に、OAuthを開始できる最低限の設定を確認します。",
                expected_result="不足項目を直すと、authorization_required状態に進めます。",
            ),
            secondary_actions=[
                _action(
                    key="keep_real_api_disabled",
                    label="実APIはOFFのままにする",
                    description="設定確認中もGoogle Health実APIは呼び出さない状態を維持します。",
                    enabled=True,
                    action_type=GOOGLE_HEALTH_CONNECTION_ACTION_TYPE_CONTINUE,
                    guidance="設定作業中に誤って実データ取得を走らせないための安全確認です。",
                    expected_result="real API flagsをOFFのまま維持できます。",
                ),
            ],
            error=checklist.error,
        )

    if checklist.reconnect_recommended:
        return _response(
            checklist=checklist,
            config=config,
            state=GOOGLE_HEALTH_CONNECTION_UX_STATE_RECONNECT_REQUIRED,
            severity=GOOGLE_HEALTH_CONNECTION_UX_SEVERITY_WARNING,
            title="Google Healthの再接続が必要です",
            message="保存済みトークンの権限が現在のGoogle Health sleep scope設定と一致していません。",
            status_summary="古い認証情報が残っているため、現在のsleep scopeで接続し直す必要があります。",
            next_action=checklist.next_action,
            recovery_steps=[
                "ローカルのGoogle Health OAuth token/stateをリセットする。",
                "現在のsleep scope設定でOAuth認証をやり直す。",
                "再接続後にsafe previewまたはdeveloper checkで状態を確認する。",
            ],
            primary_action=_action(
                key="reset_and_reconnect_google_health",
                label="リセットして再接続する",
                description="ローカルのOAuthトークンをリセットして、現在のsleep scopeで再認証します。",
                enabled=checklist.ready_for_reauthorization,
                action_type=GOOGLE_HEALTH_CONNECTION_ACTION_TYPE_RESET,
                guidance="scope mismatch時だけ使う、再接続前提のリセットアクションです。",
                expected_result="古いOAuth状態を消して、現在のsleep scopeで再認証できます。",
                risk_level="destructive_local",
                is_destructive=True,
            ),
            secondary_actions=[
                _action(
                    key="review_scope_mismatch",
                    label="scope差分を確認する",
                    description="保存済みtokenのscopeと現在のsleep scope設定の差分を確認します。",
                    enabled=True,
                    action_type=GOOGLE_HEALTH_CONNECTION_ACTION_TYPE_REVIEW,
                    guidance="リセット前に、なぜ再接続が必要なのかを確認します。",
                    expected_result="再接続が必要な理由を確認してからtoken resetに進めます。",
                ),
                _action(
                    key="keep_real_api_disabled",
                    label="実APIはOFFのままにする",
                    description="再接続が終わるまでGoogle Health実APIを呼びません。",
                    enabled=True,
                    action_type=GOOGLE_HEALTH_CONNECTION_ACTION_TYPE_CONTINUE,
                    guidance="再接続作業中に実APIを走らせないための安全確認です。",
                    expected_result="再接続が完了するまでreal APIをOFFに保ちます。",
                ),
            ],
            error=checklist.error or "reconnect_required",
        )

    if not checklist.token_stored:
        return _response(
            checklist=checklist,
            config=config,
            state=GOOGLE_HEALTH_CONNECTION_UX_STATE_AUTHORIZATION_REQUIRED,
            severity=GOOGLE_HEALTH_CONNECTION_UX_SEVERITY_WARNING,
            title="Google Healthの認証が必要です",
            message="OAuth設定は認証を開始できる状態ですが、まだローカルにGoogle Healthトークンがありません。",
            status_summary="接続設定は揃っています。次はGoogle Health認証を開始します。",
            next_action="Google Healthの認証フローを開始してください。",
            recovery_steps=[
                "Google HealthのOAuth認証フローを開始する。",
                "ブラウザで権限を確認し、ローカルcallbackが完了するのを確認する。",
                "認証後にRefreshして、token storedがreadyになるか確認する。",
            ],
            primary_action=_action(
                key="start_google_health_oauth",
                label="Google Healthを接続する",
                description="Google HealthのOAuth認証フローを開始します。",
                enabled=True,
                action_type=GOOGLE_HEALTH_CONNECTION_ACTION_TYPE_CONNECT,
                guidance="初回接続用です。まだtokenが無い時だけOAuthを開始します。",
                expected_result="ブラウザ認証とcallback後に、ローカルtokenが保存されます。",
            ),
            secondary_actions=[
                _action(
                    key="use_safe_preview_after_auth",
                    label="認証後は安全プレビューを使う",
                    description="認証直後も実APIはOFFのまま、まず安全なpreview/checkで状態を確認します。",
                    enabled=True,
                    action_type=GOOGLE_HEALTH_CONNECTION_ACTION_TYPE_SAFE_PREVIEW,
                    guidance="認証直後に実APIへ進まず、まず安全な確認だけ行います。",
                    expected_result="実データ取得前に、リクエスト準備状態を確認できます。",
                ),
            ],
            error="token_not_stored",
        )

    if checklist.ready_for_guarded_real_request:
        return _response(
            checklist=checklist,
            config=config,
            state=GOOGLE_HEALTH_CONNECTION_UX_STATE_GUARDED_REAL_REQUEST_READY,
            severity=GOOGLE_HEALTH_CONNECTION_UX_SEVERITY_READY,
            title="Google Healthの実リクエスト準備ができています",
            message="トークンとsleep scopeが揃っており、明示的な安全フラグもONです。",
            status_summary="guarded real requestを実行できる一時的な検証状態です。",
            next_action="意図した検証時だけ実行し、確認後はreal API flagsをOFFに戻してください。",
            recovery_steps=[
                "実データ検証の目的・対象日・期待結果を確認する。",
                "guarded real requestを一度だけ実行し、結果を記録する。",
                "検証後はreal API関連フラグをOFFに戻してmock-safeへ戻す。",
            ],
            primary_action=_action(
                key="run_guarded_real_request",
                label="guarded real requestを実行",
                description="明示的に許可されたローカル検証としてGoogle Health実リクエストを行います。",
                enabled=True,
                action_type=GOOGLE_HEALTH_CONNECTION_ACTION_TYPE_GUARDED_REQUEST,
                guidance="目的が明確な一時検証時だけ使う実リクエストアクションです。",
                expected_result="Google Health sleep APIへの実HTTPリクエストを1回実行します。",
                risk_level="real_api",
            ),
            secondary_actions=[
                _action(
                    key="turn_real_api_flags_off_after_test",
                    label="検証後は実APIフラグをOFFに戻す",
                    description="通常開発へ戻すため、real API request / opt-in flagsをOFFにします。",
                    enabled=True,
                    action_type=GOOGLE_HEALTH_CONNECTION_ACTION_TYPE_RESET,
                    guidance="検証後にmock-safeへ戻すための安全リセットです。",
                    expected_result="実API実行可能状態を解除し、通常の安全状態へ戻します。",
                    risk_level="safe_reset",
                ),
            ],
            error=None,
        )

    if checklist.token_stored and not checklist.real_api_requested:
        return _response(
            checklist=checklist,
            config=config,
            state=GOOGLE_HEALTH_CONNECTION_UX_STATE_REAL_REQUEST_DISABLED,
            severity=GOOGLE_HEALTH_CONNECTION_UX_SEVERITY_READY,
            title="Google Healthは接続済みです",
            message="ローカルにGoogle Healthトークンがあります。実APIリクエストは安全ガードによりOFFです。",
            status_summary="接続情報はありますが、実データ取得は安全ガードで止めています。",
            next_action="通常の開発ではこの状態でOKです。実データ取得を試す場合はguarded real request用のenv flagsを明示的にONにしてください。",
            recovery_steps=[
                "通常のUI確認では、この安全状態のまま使う。",
                "実データ検証前にsafe previewとdeveloper checkで設定を確認する。",
                "実データ検証が必要な時だけ、guarded real request用フラグを一時的にONにする。",
            ],
            primary_action=_action(
                key="use_safe_preview",
                label="安全プレビューを使う",
                description="実APIを呼ばずにリクエスト内容を確認します。",
                enabled=checklist.ready_for_safe_preview,
                action_type=GOOGLE_HEALTH_CONNECTION_ACTION_TYPE_SAFE_PREVIEW,
                guidance="接続済み状態で、実APIを呼ぶ前に安全なpreviewだけ確認します。",
                expected_result="実HTTPリクエストなしで、呼び出し準備状態だけ確認できます。",
            ),
            secondary_actions=[
                _action(
                    key="reset_local_google_health_token",
                    label="必要ならローカルtokenをリセット",
                    description="権限やscopeを変えた場合だけ、ローカルOAuth tokenをリセットして再接続します。",
                    enabled=checklist.token_stored,
                    action_type=GOOGLE_HEALTH_CONNECTION_ACTION_TYPE_RESET,
                    guidance="scope変更や接続先見直しが必要な時だけ使います。通常は不要です。",
                    expected_result="ローカルtokenを削除し、authorization_required状態から再接続できます。",
                    risk_level="destructive_local",
                    is_destructive=True,
                ),
            ],
            error=None,
        )

    return _response(
        checklist=checklist,
        config=config,
        state=GOOGLE_HEALTH_CONNECTION_UX_STATE_NEEDS_REVIEW,
        severity=GOOGLE_HEALTH_CONNECTION_UX_SEVERITY_WARNING,
        title="Google Health連携状態の確認が必要です",
        message=checklist.message,
        status_summary="接続状態に確認が必要な項目があります。",
        next_action="接続状態を再確認し、必要な準備項目だけdeveloper checkで確認してください。",
        recovery_steps=[
            "表示されている状態とdeveloper checkの不足項目を確認する。",
            "token / secret / path などの詳細はUIに出さず、必要なready状態だけ確認する。",
            "設定変更後にRefreshして、状態がauthorization requiredまたはconnectedへ進むか確認する。",
        ],
        primary_action=_action(
            key="review_google_health_setup",
            label="状態を確認する",
            description="接続チェックリストで不足している設定や安全ガードを確認します。",
            enabled=True,
            action_type=GOOGLE_HEALTH_CONNECTION_ACTION_TYPE_REVIEW,
            guidance="どの接続段階で止まっているかを確認します。",
            expected_result="設定・token・guardのどこに確認項目があるか分かります。",
        ),
        secondary_actions=[
            _action(
                key="keep_real_api_disabled",
                label="実APIはOFFのまま確認する",
                description="確認中はGoogle Health実APIを呼ばない安全状態を維持します。",
                enabled=True,
                action_type=GOOGLE_HEALTH_CONNECTION_ACTION_TYPE_CONTINUE,
                guidance="状態確認中に実APIを呼ばないための安全確認です。",
                expected_result="real API flagsをOFFのまま接続状態を確認できます。",
            ),
        ],
        error=checklist.error,
    )


def _response(
    *,
    checklist: GoogleHealthConnectionChecklistResponse,
    config: AppConfig,
    state: str,
    severity: str,
    title: str,
    message: str,
    status_summary: str,
    next_action: str,
    recovery_steps: list[str],
    primary_action: GoogleHealthConnectionUxActionModel | None = None,
    secondary_actions: list[GoogleHealthConnectionUxActionModel] | None = None,
    error: str | None = None,
) -> GoogleHealthConnectionUxResponse:
    secondary_actions = secondary_actions or []
    connection_actions = _connection_actions(primary_action, secondary_actions)
    retry_actions = [_refresh_status_action()]
    reset_actions = _reset_actions(primary_action, secondary_actions)

    return GoogleHealthConnectionUxResponse(
        provider=GOOGLE_HEALTH_PROVIDER_NAME,
        state=state,
        severity=severity,
        title=title,
        message=message,
        status_summary=status_summary,
        user_guidance=_user_guidance(state),
        safe_guard_summary=_safe_guard_summary(checklist),
        state_stage=_state_stage(state),
        state_reason=_state_reason(state, checklist, config),
        state_details=_state_details(state, checklist, config),
        next_action=next_action,
        recovery_steps=recovery_steps,
        safe_mode_note=_SAFE_MODE_NOTE,
        primary_action=primary_action,
        secondary_actions=secondary_actions,
        connection_actions=connection_actions,
        retry_actions=retry_actions,
        reset_actions=reset_actions,
        sleep_provider=config.sleep_provider,
        token_stored=checklist.token_stored,
        reconnect_recommended=checklist.reconnect_recommended,
        real_api_requested=checklist.real_api_requested,
        real_api_allowed=checklist.real_api_allowed,
        can_start_oauth=checklist.ready_for_local_oauth,
        can_reset_local_token=checklist.token_stored,
        can_use_safe_preview=checklist.ready_for_safe_preview,
        can_use_guarded_real_request=checklist.ready_for_guarded_real_request,
        developer_status=checklist.status,
        developer_note=_DEVELOPER_NOTE,
        developer_summary=_developer_summary(state, checklist),
        developer_details=_developer_details(checklist, config),
        user_visible_details_limited=True,
        error=_safe_error(error),
    )


def _safe_error(error: str | None) -> str | None:
    if error is None:
        return None
    sensitive_fragments = (
        "token",
        "secret",
        "credential",
        "credentials",
        "file",
        "path",
        "command",
        "Authorization",
        "Bearer",
        ".json",
    )
    normalized = error.lower()
    if any(fragment.lower() in normalized for fragment in sensitive_fragments):
        return "google_health_connection_needs_review"
    return error


def _connection_actions(
    primary_action: GoogleHealthConnectionUxActionModel | None,
    secondary_actions: list[GoogleHealthConnectionUxActionModel],
) -> list[GoogleHealthConnectionUxActionModel]:
    connect_like_types = {
        GOOGLE_HEALTH_CONNECTION_ACTION_TYPE_CONNECT,
        GOOGLE_HEALTH_CONNECTION_ACTION_TYPE_CONTINUE,
        GOOGLE_HEALTH_CONNECTION_ACTION_TYPE_REVIEW,
        GOOGLE_HEALTH_CONNECTION_ACTION_TYPE_SAFE_PREVIEW,
        GOOGLE_HEALTH_CONNECTION_ACTION_TYPE_GUARDED_REQUEST,
    }
    return [
        action
        for action in _all_actions(primary_action, secondary_actions)
        if action.action_type in connect_like_types
    ]


def _reset_actions(
    primary_action: GoogleHealthConnectionUxActionModel | None,
    secondary_actions: list[GoogleHealthConnectionUxActionModel],
) -> list[GoogleHealthConnectionUxActionModel]:
    return [
        action
        for action in _all_actions(primary_action, secondary_actions)
        if action.action_type == GOOGLE_HEALTH_CONNECTION_ACTION_TYPE_RESET
    ]


def _all_actions(
    primary_action: GoogleHealthConnectionUxActionModel | None,
    secondary_actions: list[GoogleHealthConnectionUxActionModel],
) -> list[GoogleHealthConnectionUxActionModel]:
    actions: list[GoogleHealthConnectionUxActionModel] = []
    if primary_action is not None:
        actions.append(primary_action)
    actions.extend(secondary_actions)
    return actions


def _refresh_status_action() -> GoogleHealthConnectionUxActionModel:
    return _action(
        key="refresh_google_health_connection_status",
        label="状態を再読み込み",
        description="設定や認証状態を変えた後に、Google Health接続状態を再取得します。",
        enabled=True,
        action_type=GOOGLE_HEALTH_CONNECTION_ACTION_TYPE_RETRY,
        guidance="設定変更・OAuth完了・token reset後に使う再確認アクションです。",
        expected_result="最新の接続状態、次の操作、利用可能な安全アクションを再表示します。",
    )


def _action(
    *,
    key: str,
    label: str,
    description: str,
    enabled: bool,
    action_type: str = GOOGLE_HEALTH_CONNECTION_ACTION_TYPE_REVIEW,
    guidance: str = "",
    expected_result: str = "",
    risk_level: str = "safe",
    is_destructive: bool = False,
) -> GoogleHealthConnectionUxActionModel:
    return GoogleHealthConnectionUxActionModel(
        key=key,
        label=label,
        description=description,
        enabled=enabled,
        action_type=action_type,
        guidance=guidance,
        expected_result=expected_result,
        risk_level=risk_level,
        is_destructive=is_destructive,
    )



def _user_guidance(state: str) -> str:
    guidance_by_state = {
        GOOGLE_HEALTH_CONNECTION_UX_STATE_MOCK_MODE: (
            "通常の確認はこのままでOKです。外部の健康データ取得は使わず、"
            "安全なモック睡眠データで日次ループを確認します。"
        ),
        GOOGLE_HEALTH_CONNECTION_UX_STATE_NOT_CONFIGURED: (
            "まだ接続開始前の準備段階です。接続ボタンを押す前に、OAuth設定が"
            "揃っているかを開発者向けチェックで確認します。"
        ),
        GOOGLE_HEALTH_CONNECTION_UX_STATE_AUTHORIZATION_REQUIRED: (
            "接続準備はできています。Google Healthを使う場合は認証を開始し、"
            "完了後に状態を再読み込みしてください。"
        ),
        GOOGLE_HEALTH_CONNECTION_UX_STATE_RECONNECT_REQUIRED: (
            "以前の接続情報が現在のsleep scopeと合っていません。必要な場合だけ"
            "ローカル接続情報をリセットして再接続します。"
        ),
        GOOGLE_HEALTH_CONNECTION_UX_STATE_TOKEN_UNAVAILABLE: (
            "Google Healthの接続情報を確認できません。認証状態を再確認し、"
            "必要なら接続をやり直します。"
        ),
        GOOGLE_HEALTH_CONNECTION_UX_STATE_REAL_REQUEST_DISABLED: (
            "Google Healthの接続情報はありますが、実データ取得は安全ガードで止めています。"
            "通常のUI確認ではこの状態でOKです。"
        ),
        GOOGLE_HEALTH_CONNECTION_UX_STATE_GUARDED_REAL_REQUEST_READY: (
            "明示的な検証用フラグが揃っています。目的がはっきりした一時検証だけ行い、"
            "確認後は実APIフラグをOFFに戻してください。"
        ),
        GOOGLE_HEALTH_CONNECTION_UX_STATE_NEEDS_REVIEW: (
            "接続状態に確認が必要です。まず状態を再読み込みし、開発者向けチェックで"
            "不足している準備項目だけ確認してください。"
        ),
    }
    return guidance_by_state.get(state, guidance_by_state[GOOGLE_HEALTH_CONNECTION_UX_STATE_NEEDS_REVIEW])


def _safe_guard_summary(checklist: GoogleHealthConnectionChecklistResponse) -> str:
    if checklist.ready_for_guarded_real_request:
        return (
            "guarded real request の条件が揃っています。実API検証は一時的に行い、"
            "完了後はreal API flagsをOFFに戻す前提です。"
        )
    if checklist.real_api_requested and not checklist.real_api_allowed:
        return (
            "real API request は要求されていますが、endpoint確認または明示opt-inが不足しているため"
            "ガードで停止しています。"
        )
    return "real API requests は通常OFFです。mock-safeまたはsafe previewで確認します。"


def _developer_summary(
    state: str,
    checklist: GoogleHealthConnectionChecklistResponse,
) -> str:
    if state == GOOGLE_HEALTH_CONNECTION_UX_STATE_MOCK_MODE:
        return "SLEEP_PROVIDER is not google_health; Google Health connection work is intentionally inactive."
    if state == GOOGLE_HEALTH_CONNECTION_UX_STATE_NOT_CONFIGURED:
        return "OAuth prerequisites are incomplete; keep connect actions as review-only until ready_for_local_oauth is true."
    if state == GOOGLE_HEALTH_CONNECTION_UX_STATE_AUTHORIZATION_REQUIRED:
        return "OAuth prerequisites are ready but no token snapshot is stored; start local OAuth before safe preview."
    if state == GOOGLE_HEALTH_CONNECTION_UX_STATE_RECONNECT_REQUIRED:
        return "Token scope metadata is stale or incomplete; reset local token/state before reauthorization."
    if state == GOOGLE_HEALTH_CONNECTION_UX_STATE_REAL_REQUEST_DISABLED:
        return "Token and scope are available; real API execution remains disabled until all guarded flags are explicit."
    if state == GOOGLE_HEALTH_CONNECTION_UX_STATE_GUARDED_REAL_REQUEST_READY:
        return "Guarded real request is ready; run only an intentional test and revert real API flags afterward."
    if checklist.error:
        return f"Checklist status is {checklist.status} with error {checklist.error}; inspect developer checks without surfacing secrets."
    return f"Checklist status is {checklist.status}; inspect readiness booleans before choosing the next action."


def _developer_details(
    checklist: GoogleHealthConnectionChecklistResponse,
    config: AppConfig,
) -> list[GoogleHealthConnectionUxStateDetailModel]:
    details = [
        _detail(
            key="developer_status",
            label="Checklist status",
            value=checklist.status,
            tone="ready" if checklist.status in {"ready", "connected"} else "warning",
            guidance="Developer-only readiness summary. It does not include token values or local file paths.",
        ),
        _detail(
            key="oauth_ready",
            label="OAuth ready",
            value="ready" if checklist.ready_for_local_oauth else "not ready",
            tone="ready" if checklist.ready_for_local_oauth else "blocked",
            guidance="Controls whether the UI should offer connection start instead of setup review.",
        ),
        _detail(
            key="safe_preview_ready",
            label="Safe preview",
            value="ready" if checklist.ready_for_safe_preview else "not ready",
            tone="ready" if checklist.ready_for_safe_preview else "info",
            guidance="Safe preview must not perform real Google Health HTTP requests.",
        ),
        _detail(
            key="guarded_real_request",
            label="Guarded real request",
            value="ready" if checklist.ready_for_guarded_real_request else "off",
            tone="ready" if checklist.ready_for_guarded_real_request else "info",
            guidance="Requires token, scope, endpoint verification, and explicit opt-in flags.",
        ),
    ]

    if checklist.reconnect_recommended:
        details.append(
            _detail(
                key="reconnect_required",
                label="Reconnect",
                value="required",
                tone="warning",
                guidance="Scope mismatch is handled by local reset + OAuth reauthorization, not by displaying token metadata.",
            )
        )
    if checklist.runtime_guard_error:
        details.append(
            _detail(
                key="runtime_guard",
                label="Runtime guard",
                value="blocked",
                tone="warning",
                guidance="Guard error is summarized here; raw commands and env internals stay out of the user-facing card.",
            )
        )
    if config.sleep_provider != GOOGLE_HEALTH_PROVIDER_NAME:
        details.append(
            _detail(
                key="provider_mode",
                label="Provider mode",
                value="mock-safe",
                tone="ready",
                guidance="Google Health details are informational until SLEEP_PROVIDER is switched to google_health.",
            )
        )

    return details


def _state_stage(state: str) -> str:
    stage_by_state = {
        GOOGLE_HEALTH_CONNECTION_UX_STATE_MOCK_MODE: "Mock-safe development",
        GOOGLE_HEALTH_CONNECTION_UX_STATE_NOT_CONFIGURED: "Setup required",
        GOOGLE_HEALTH_CONNECTION_UX_STATE_AUTHORIZATION_REQUIRED: "認証が必要",
        GOOGLE_HEALTH_CONNECTION_UX_STATE_RECONNECT_REQUIRED: "Reconnect required",
        GOOGLE_HEALTH_CONNECTION_UX_STATE_TOKEN_UNAVAILABLE: "Token unavailable",
        GOOGLE_HEALTH_CONNECTION_UX_STATE_REAL_REQUEST_DISABLED: "Connected / real API disabled",
        GOOGLE_HEALTH_CONNECTION_UX_STATE_GUARDED_REAL_REQUEST_READY: "Guarded real request ready",
        GOOGLE_HEALTH_CONNECTION_UX_STATE_NEEDS_REVIEW: "Needs review",
    }
    return stage_by_state.get(state, "Needs review")


def _state_reason(
    state: str,
    checklist: GoogleHealthConnectionChecklistResponse,
    config: AppConfig,
) -> str:
    if state == GOOGLE_HEALTH_CONNECTION_UX_STATE_MOCK_MODE:
        return "SLEEP_PROVIDER is not google_health, so the daily loop is using mock sleep data."
    if state == GOOGLE_HEALTH_CONNECTION_UX_STATE_NOT_CONFIGURED:
        return "OAuth setup is incomplete, so the app should not start the Google Health authorization flow yet."
    if state == GOOGLE_HEALTH_CONNECTION_UX_STATE_AUTHORIZATION_REQUIRED:
        return "OAuth setup is ready, but no local Google Health token snapshot is stored yet."
    if state == GOOGLE_HEALTH_CONNECTION_UX_STATE_RECONNECT_REQUIRED:
        return "A local token exists, but its scope metadata does not match the current required sleep scope."
    if state == GOOGLE_HEALTH_CONNECTION_UX_STATE_TOKEN_UNAVAILABLE:
        return "The app cannot confirm a usable local token for Google Health sleep access."
    if state == GOOGLE_HEALTH_CONNECTION_UX_STATE_REAL_REQUEST_DISABLED:
        return "A local token is stored, but guarded real API requests are intentionally disabled for normal development."
    if state == GOOGLE_HEALTH_CONNECTION_UX_STATE_GUARDED_REAL_REQUEST_READY:
        return "Token, scope, endpoint verification, and explicit opt-in flags are all aligned for a guarded real request."
    if checklist.error:
        return f"The developer checklist still reports {checklist.error}; review safe setup details before continuing."
    return "The Google Health connection state needs a safe developer review before the next user action."


def _state_details(
    state: str,
    checklist: GoogleHealthConnectionChecklistResponse,
    config: AppConfig,
) -> list[GoogleHealthConnectionUxStateDetailModel]:
    details = [
        _detail(
            key="sleep_provider",
            label="Sleep provider",
            value=config.sleep_provider,
            tone="ready" if config.sleep_provider == GOOGLE_HEALTH_PROVIDER_NAME else "info",
            guidance=(
                "Google Health connection states are active."
                if config.sleep_provider == GOOGLE_HEALTH_PROVIDER_NAME
                else "Mock sleep data is active; Google Health real data is not used."
            ),
        ),
        _detail(
            key="token_state",
            label="Token",
            value="stored" if checklist.token_stored else "not stored",
            tone="ready" if checklist.token_stored else "warning",
            guidance=(
                "A local token snapshot exists; do not display token values in the UI."
                if checklist.token_stored
                else "OAuth authorization must complete before real Google Health sleep access can be tested."
            ),
        ),
        _detail(
            key="real_api_guard",
            label="Real API guard",
            value=(
                "allowed"
                if checklist.real_api_allowed
                else "requested but blocked"
                if checklist.real_api_requested
                else "off"
            ),
            tone=(
                "ready"
                if checklist.real_api_allowed
                else "warning"
                if checklist.real_api_requested
                else "info"
            ),
            guidance=(
                "Use only for an intentional guarded test, then return the flags to OFF."
                if checklist.real_api_allowed
                else "Real Google Health HTTP requests remain disabled by default."
            ),
        ),
    ]

    if state == GOOGLE_HEALTH_CONNECTION_UX_STATE_NOT_CONFIGURED:
        details.append(
            _detail(
                key="blocker",
                label="Blocker",
                value=checklist.error or "oauth_setup",
                tone="blocked",
                guidance="Fix credentials, redirect URI, or required sleep scope before starting OAuth.",
            )
        )
    elif state == GOOGLE_HEALTH_CONNECTION_UX_STATE_AUTHORIZATION_REQUIRED:
        details.append(
            _detail(
                key="next_stage",
                label="Next stage",
                value="start OAuth",
                tone="warning",
                guidance="Start OAuth only after the setup checklist is ready.",
            )
        )
    elif state == GOOGLE_HEALTH_CONNECTION_UX_STATE_RECONNECT_REQUIRED:
        details.append(
            _detail(
                key="blocker",
                label="Blocker",
                value="scope mismatch",
                tone="warning",
                guidance="Reset the local token/state and reconnect with the current sleep scope.",
            )
        )
    elif state == GOOGLE_HEALTH_CONNECTION_UX_STATE_REAL_REQUEST_DISABLED:
        details.append(
            _detail(
                key="safe_default",
                label="Safe default",
                value="real API disabled",
                tone="ready",
                guidance="Use safe preview for normal development; enable guarded real requests only for a planned test.",
            )
        )
    elif state == GOOGLE_HEALTH_CONNECTION_UX_STATE_GUARDED_REAL_REQUEST_READY:
        details.append(
            _detail(
                key="guarded_test",
                label="Guarded test",
                value="ready",
                tone="ready",
                guidance="Run a small intentional test, record the result, then disable real API flags.",
            )
        )
    elif state == GOOGLE_HEALTH_CONNECTION_UX_STATE_MOCK_MODE:
        details.append(
            _detail(
                key="safe_default",
                label="Safe default",
                value="mock sleep",
                tone="ready",
                guidance="This is the expected state for ordinary local UI and daily loop checks.",
            )
        )

    return details


def _detail(
    *,
    key: str,
    label: str,
    value: str,
    tone: str = "info",
    guidance: str = "",
) -> GoogleHealthConnectionUxStateDetailModel:
    return GoogleHealthConnectionUxStateDetailModel(
        key=key,
        label=label,
        value=value,
        tone=tone,
        guidance=guidance,
    )
