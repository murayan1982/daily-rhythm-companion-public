from __future__ import annotations

import argparse
import sys
import webbrowser
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.config import GOOGLE_HEALTH_SLEEP_READONLY_SCOPE, load_config  # noqa: E402
from app.services.google_health_runtime_guard import (  # noqa: E402
    evaluate_google_health_runtime_guard,
)
from app.services.google_health_scope_check import get_google_health_scope_check  # noqa: E402
from app.services.google_health_service import build_google_health_connect_response  # noqa: E402
from app.services.google_health_token_store import GoogleHealthTokenStore  # noqa: E402


UNNECESSARY_DEFAULT_SCOPES = {
    "openid",
    "email",
    "profile",
    "https://www.googleapis.com/auth/fitness.sleep.read",
    "https://www.googleapis.com/auth/googlehealth.activity_and_fitness.readonly",
}


def main() -> int:
    """
    Prepare a local Google Health OAuth authorization URL and print guidance.

    This helper is intentionally operator-facing. It does not exchange tokens,
    does not print token contents, and does not make Google Health API calls.
    Real token exchange is handled by the backend callback only when
    GOOGLE_HEALTH_ENABLE_REAL_TOKEN_EXCHANGE=1 is explicitly enabled.
    """

    parser = argparse.ArgumentParser(
        description="Prepare Google Health OAuth authorization guidance."
    )
    parser.add_argument(
        "--open-browser",
        action="store_true",
        help="Open the generated Google OAuth URL in the default browser.",
    )
    parser.add_argument(
        "--no-url",
        action="store_true",
        help="Do not print the generated OAuth URL.",
    )
    parser.add_argument(
        "--require-ready",
        action="store_true",
        help="Return a non-zero exit code when the OAuth URL cannot be prepared.",
    )
    args = parser.parse_args()

    config = load_config()
    guard = evaluate_google_health_runtime_guard(config)
    scope_check = get_google_health_scope_check(config=config)
    token_store = GoogleHealthTokenStore()
    configured_scopes = set(config.google_health_oauth_scopes)
    mixed_scopes = sorted(configured_scopes & UNNECESSARY_DEFAULT_SCOPES)
    missing_minimal_sleep_scope = GOOGLE_HEALTH_SLEEP_READONLY_SCOPE not in configured_scopes

    connect_response = build_google_health_connect_response(config)

    print("[google-health-oauth-helper]")
    print(f"recommended_sleep_scope={GOOGLE_HEALTH_SLEEP_READONLY_SCOPE}")
    print(f"configured_scopes={list(config.google_health_oauth_scopes)}")
    print(f"missing_minimal_sleep_scope={missing_minimal_sleep_scope}")
    print(f"mixed_scope_warnings={mixed_scopes}")
    print(f"credentials_and_redirect_ready={connect_response.ready}")
    print(f"connect_error={connect_response.error}")
    print(f"real_token_exchange_enabled={config.google_health_enable_real_token_exchange}")
    print(f"real_api_requested={guard.real_api_requested}")
    print(f"real_api_allowed={guard.real_api_allowed}")
    print(f"token_file={token_store.token_file}")
    print(f"token_stored={scope_check.token_stored}")
    print(f"required_sleep_scope_in_token={scope_check.required_sleep_scope_in_token}")
    print(f"reconnect_recommended={scope_check.reconnect_recommended}")
    print("sensitive_contents_printed=False")

    warnings: list[str] = []
    if missing_minimal_sleep_scope:
        warnings.append("missing_minimal_sleep_scope")
    if mixed_scopes:
        warnings.append("mixed_or_unnecessary_scopes_configured")
    if config.google_health_enable_real_api_requests or config.google_health_real_api_opt_in:
        warnings.append("real_api_flags_enabled_for_oauth_flow")
    if scope_check.reconnect_recommended:
        warnings.append("reauthorization_recommended")

    print(f"warnings={warnings}")

    if warnings:
        print("next_check=python scripts\\check_google_health_connection_config.py")

    print("reset_dry_run=python scripts\\reset_google_health_local_oauth.py")
    print("reset_apply=python scripts\\reset_google_health_local_oauth.py --apply")
    print("post_auth_check=python scripts\\check_google_health_connection_config.py")
    print(
        "token_exchange_note=Temporarily set GOOGLE_HEALTH_ENABLE_REAL_TOKEN_EXCHANGE=1 only while completing a local OAuth callback that should save a token."
    )
    print(
        "real_api_note=GOOGLE_HEALTH_ENABLE_REAL_API_REQUESTS and GOOGLE_HEALTH_REAL_API_OPT_IN are separate from OAuth and should stay 0 during authorization."
    )

    if not connect_response.ready:
        print(f"message={connect_response.message}")
        print("next_step=Configure backend/credentials.json and GOOGLE_HEALTH_REDIRECT_URI, then rerun this helper.")
        print("[google-health-oauth-helper] NOT_READY")
        return 1 if args.require_ready else 0

    print(f"message={connect_response.message}")
    print("next_step=Open connect_url, finish Google OAuth, then verify the token with the post_auth_check command.")

    if not args.no_url:
        print(f"connect_url={connect_response.connect_url}")

    if args.open_browser:
        if connect_response.connect_url:
            webbrowser.open(connect_response.connect_url)
            print("browser_open_attempted=True")
        else:
            print("browser_open_attempted=False")

    print("[google-health-oauth-helper] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
