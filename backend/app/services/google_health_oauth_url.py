from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlencode

from app.config import AppConfig, GOOGLE_HEALTH_DEFAULT_OAUTH_SCOPES
from app.services.google_health_credentials import GoogleHealthOAuthCredentials


@dataclass(frozen=True)
class GoogleHealthOAuthUrlResult:
    """
    Result of building a Google Health OAuth authorization URL.

    The URL contains a state value but must not contain client secrets.
    """

    ready: bool
    auth_url: str | None
    state: str | None
    scopes: tuple[str, ...]
    message: str
    error: str | None = None


def build_google_health_authorization_url(
    *,
    config: AppConfig,
    credentials: GoogleHealthOAuthCredentials,
    state: str,
    scopes: tuple[str, ...] | None = None,
) -> GoogleHealthOAuthUrlResult:
    """
    Build a Google OAuth authorization URL for Google Health readiness.

    This is only the OAuth entry boundary. Use the minimal sleep-read scope
    unless a specific test plan intentionally requires additional scopes.
    """

    redirect_uri = config.google_health_redirect_uri
    selected_scopes = scopes or config.google_health_oauth_scopes or GOOGLE_HEALTH_DEFAULT_OAUTH_SCOPES

    if not redirect_uri:
        return GoogleHealthOAuthUrlResult(
            ready=False,
            auth_url=None,
            state=state,
            scopes=selected_scopes,
            message="Google Health redirect URI is not configured.",
            error="redirect_uri_not_configured",
        )

    query = urlencode(
        {
            "client_id": credentials.client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": " ".join(selected_scopes),
            "state": state,
            "access_type": "offline",
            "prompt": "consent",
        }
    )

    return GoogleHealthOAuthUrlResult(
        ready=True,
        auth_url=f"{credentials.auth_uri}?{query}",
        state=state,
        scopes=selected_scopes,
        message="Google Health OAuth authorization URL was prepared.",
        error=None,
    )