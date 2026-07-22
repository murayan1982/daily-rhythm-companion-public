from __future__ import annotations

from app.config import AppConfig
from app.models.google_health import GoogleHealthScopeCheckResponse
from app.services.google_health_service import GOOGLE_HEALTH_PROVIDER_NAME
from app.services.google_health_token_store import GoogleHealthTokenStore


GOOGLE_HEALTH_SCOPE_CHECK_STATUS_NEEDS_REQUIRED_SCOPE = "needs_required_sleep_scope"
GOOGLE_HEALTH_SCOPE_CHECK_STATUS_NEEDS_RECONNECT = "needs_reconnect"
GOOGLE_HEALTH_SCOPE_CHECK_STATUS_NO_TOKEN = "no_token"
GOOGLE_HEALTH_SCOPE_CHECK_STATUS_READY = "ready_for_permission_retest"


def get_google_health_scope_check(
    *,
    config: AppConfig,
    token_store: GoogleHealthTokenStore | None = None,
) -> GoogleHealthScopeCheckResponse:
    """
    Compare configured Google Health scopes with the locally stored token scope.

    This endpoint is a v0.23 troubleshooting helper for 403 permission_denied.
    It does not perform OAuth, refresh tokens, or call the Google Health API.
    Scope names are not secrets, but token values must never be returned.

    v0.23.0 Day2 intentionally separates the required sleep-read scope from
    optional identity scopes. Google OAuth token responses may not echo
    openid/email/profile in the stored token scope field even after a successful
    sign-in. That should not block the Google Health permission retest when the
    required sleep-read scope is present.
    """

    configured_scopes = _normalize_scopes(config.google_health_oauth_scopes)
    required_sleep_scope = _normalize_optional_scope(
        config.google_health_required_sleep_scope
    )

    store = token_store or GoogleHealthTokenStore()
    tokens = store.load_tokens()
    token_scopes = _parse_scope_string(tokens.scope) if tokens else []

    missing_configured_scopes = [
        scope for scope in configured_scopes if scope not in token_scopes
    ]
    missing_required_scopes = [
        scope
        for scope in [required_sleep_scope]
        if scope and scope in configured_scopes and scope not in token_scopes
    ]
    missing_optional_scopes = [
        scope
        for scope in missing_configured_scopes
        if scope not in missing_required_scopes
    ]

    required_scope_configured = bool(required_sleep_scope)
    required_scope_in_config = (
        required_sleep_scope in configured_scopes if required_sleep_scope else None
    )
    required_scope_in_token = (
        required_sleep_scope in token_scopes if required_sleep_scope else None
    )

    reconnect_recommended = bool(
        tokens
        and (
            required_scope_in_config is False
            or required_scope_in_token is False
            or (required_sleep_scope and not tokens.scope)
        )
    )
    ready_for_permission_retest = bool(
        tokens
        and required_sleep_scope
        and required_scope_in_config
        and required_scope_in_token
    )

    status, message, next_action = _build_scope_check_guidance(
        required_sleep_scope=required_sleep_scope,
        token_stored=bool(tokens),
        token_scope_configured=bool(tokens and tokens.scope),
        required_scope_in_config=required_scope_in_config,
        required_scope_in_token=required_scope_in_token,
        missing_optional_scopes=missing_optional_scopes,
        reconnect_recommended=reconnect_recommended,
        ready_for_permission_retest=ready_for_permission_retest,
    )

    return GoogleHealthScopeCheckResponse(
        provider=GOOGLE_HEALTH_PROVIDER_NAME,
        required_sleep_scope_configured=required_scope_configured,
        required_sleep_scope=required_sleep_scope,
        configured_scopes=configured_scopes,
        configured_scope_count=len(configured_scopes),
        token_stored=bool(tokens),
        token_scope_configured=bool(tokens and tokens.scope),
        token_scopes=token_scopes,
        token_scope_count=len(token_scopes),
        missing_configured_scopes_in_token=missing_configured_scopes,
        missing_required_scopes_in_token=missing_required_scopes,
        missing_optional_configured_scopes_in_token=missing_optional_scopes,
        required_sleep_scope_in_config=required_scope_in_config,
        required_sleep_scope_in_token=required_scope_in_token,
        reconnect_recommended=reconnect_recommended,
        ready_for_permission_retest=ready_for_permission_retest,
        message=message,
        next_action=next_action,
        error=None if status == GOOGLE_HEALTH_SCOPE_CHECK_STATUS_READY else status,
    )


def _normalize_scopes(scopes: tuple[str, ...]) -> list[str]:
    """Return sorted unique scope strings from configured scope values."""

    normalized: set[str] = set()
    for scope in scopes:
        normalized.update(_parse_scope_string(scope))

    return sorted(normalized)


def _parse_scope_string(scope_value: str | None) -> list[str]:
    """Parse a space/comma separated OAuth scope string."""

    if not scope_value:
        return []

    return sorted(
        {
            part.strip()
            for part in scope_value.replace(",", " ").split()
            if part.strip()
        }
    )


def _normalize_optional_scope(scope: str | None) -> str | None:
    """Normalize a single optional required scope value."""

    scopes = _parse_scope_string(scope)
    return scopes[0] if scopes else None


def _build_scope_check_guidance(
    *,
    required_sleep_scope: str | None,
    token_stored: bool,
    token_scope_configured: bool,
    required_scope_in_config: bool | None,
    required_scope_in_token: bool | None,
    missing_optional_scopes: list[str],
    reconnect_recommended: bool,
    ready_for_permission_retest: bool,
) -> tuple[str, str, str]:
    """Build safe v0.23 troubleshooting guidance for scope mismatch checks."""

    if not required_sleep_scope:
        return (
            GOOGLE_HEALTH_SCOPE_CHECK_STATUS_NEEDS_REQUIRED_SCOPE,
            "Google Health required sleep scope is not configured yet.",
            (
                "Confirm the official Google Health sleep read scope, set "
                "GOOGLE_HEALTH_REQUIRED_SLEEP_SCOPE, add it to "
                "GOOGLE_HEALTH_OAUTH_SCOPES, then reconnect/re-authorize."
            ),
        )

    if required_scope_in_config is False:
        return (
            GOOGLE_HEALTH_SCOPE_CHECK_STATUS_NEEDS_REQUIRED_SCOPE,
            "Required sleep scope is not included in configured OAuth scopes.",
            (
                "Add GOOGLE_HEALTH_REQUIRED_SLEEP_SCOPE to "
                "GOOGLE_HEALTH_OAUTH_SCOPES before starting the OAuth connect flow."
            ),
        )

    if not token_stored:
        return (
            GOOGLE_HEALTH_SCOPE_CHECK_STATUS_NO_TOKEN,
            "No local Google Health token is stored yet.",
            "Run the OAuth connect flow after the required sleep scope is configured.",
        )

    if not token_scope_configured:
        return (
            GOOGLE_HEALTH_SCOPE_CHECK_STATUS_NEEDS_RECONNECT,
            "Stored token does not include a scope field that can be compared.",
            (
                "Reconnect/re-authorize after confirming the sleep scope so the "
                "stored token is minted with comparable scope metadata."
            ),
        )

    if reconnect_recommended or required_scope_in_token is False:
        return (
            GOOGLE_HEALTH_SCOPE_CHECK_STATUS_NEEDS_RECONNECT,
            "Stored token does not include the required Google Health sleep scope.",
            (
                "Reconnect/re-authorize so the local refresh token is minted with "
                "the current Google Health sleep read scope."
            ),
        )

    if ready_for_permission_retest:
        if missing_optional_scopes:
            return (
                GOOGLE_HEALTH_SCOPE_CHECK_STATUS_READY,
                (
                    "Stored token includes the required sleep scope. Optional "
                    "configured identity scopes are not present in the token scope metadata."
                ),
                (
                    "Proceed with a guarded permission retest. If 403 persists, check "
                    "Google Cloud API enablement, OAuth consent approval/test-user access, "
                    "and endpoint/query details."
                ),
            )

        return (
            GOOGLE_HEALTH_SCOPE_CHECK_STATUS_READY,
            "Configured scopes and stored token scope include the required sleep scope.",
            (
                "If 403 persists, check Google Cloud API enablement, OAuth consent "
                "approval/test-user access, and endpoint/query details before another "
                "guarded real request."
            ),
        )

    return (
        GOOGLE_HEALTH_SCOPE_CHECK_STATUS_NEEDS_RECONNECT,
        "Google Health scope state needs another local review.",
        "Review configured scopes, stored token scopes, and reconnect if they differ.",
    )
