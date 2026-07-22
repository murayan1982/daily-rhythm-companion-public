from __future__ import annotations

import sys
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
from app.services.google_health_token_store import GoogleHealthTokenStore  # noqa: E402


def main() -> int:
    """Run a safe Google Health connection configuration check."""

    config = load_config()
    guard = evaluate_google_health_runtime_guard(config)
    scope_check = get_google_health_scope_check(config=config)
    token_store = GoogleHealthTokenStore()

    warnings: list[str] = []

    configured_scopes = set(config.google_health_oauth_scopes)
    unnecessary_default_scopes = {
        "openid",
        "email",
        "profile",
        "https://www.googleapis.com/auth/fitness.sleep.read",
        "https://www.googleapis.com/auth/googlehealth.activity_and_fitness.readonly",
    }
    mixed_scopes = sorted(configured_scopes & unnecessary_default_scopes)

    if GOOGLE_HEALTH_SLEEP_READONLY_SCOPE not in configured_scopes:
        warnings.append("missing_minimal_sleep_scope")

    if mixed_scopes:
        warnings.append("mixed_or_unnecessary_scopes_configured")

    if config.google_health_enable_real_api_requests or config.google_health_real_api_opt_in:
        warnings.append("real_api_flags_enabled")

    print("[google-health-connection-config]")
    print(f"recommended_sleep_scope={GOOGLE_HEALTH_SLEEP_READONLY_SCOPE}")
    print(f"configured_scopes={list(config.google_health_oauth_scopes)}")
    print(f"required_sleep_scope={config.google_health_required_sleep_scope}")
    print(f"mixed_scope_warnings={mixed_scopes}")
    print(f"token_file={token_store.token_file}")
    print(f"token_stored={scope_check.token_stored}")
    print(f"required_sleep_scope_in_config={scope_check.required_sleep_scope_in_config}")
    print(f"required_sleep_scope_in_token={scope_check.required_sleep_scope_in_token}")
    print(f"reconnect_recommended={scope_check.reconnect_recommended}")
    print(f"real_api_requested={guard.real_api_requested}")
    print(f"real_api_allowed={guard.real_api_allowed}")
    print(f"runtime_guard_error={guard.error}")
    print(f"warnings={warnings}")

    if warnings:
        print("[google-health-connection-config] WARN")
        return 1

    print("[google-health-connection-config] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
