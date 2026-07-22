from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.config import load_config  # noqa: E402
from app.services.google_health_connection_checklist import (  # noqa: E402
    get_google_health_connection_checklist,
)
from app.services.google_health_token_store import GoogleHealthTokenStore  # noqa: E402


def main() -> int:
    """Print the non-sensitive Google Health connection checklist."""

    parser = argparse.ArgumentParser(
        description="Print the non-sensitive Google Health connection checklist."
    )
    parser.add_argument(
        "--token-file",
        type=Path,
        help=argparse.SUPPRESS,
    )
    args = parser.parse_args()

    token_store = (
        GoogleHealthTokenStore(token_file=args.token_file)
        if args.token_file is not None
        else None
    )
    checklist = get_google_health_connection_checklist(
        config=load_config(),
        token_store=token_store,
    )

    print("[google-health-connection-checklist]")
    print(f"status={checklist.status}")
    print(f"recommended_sleep_scope={checklist.recommended_sleep_scope}")
    print(f"configured_scopes={checklist.configured_scopes}")
    print(f"mixed_scope_warnings={checklist.mixed_scope_warnings}")
    print(f"token_store_configured={checklist.token_store_configured}")
    print(f"token_stored={checklist.token_stored}")
    print(f"required_sleep_scope_in_config={checklist.required_sleep_scope_in_config}")
    print(f"required_sleep_scope_in_token={checklist.required_sleep_scope_in_token}")
    print(f"reconnect_recommended={checklist.reconnect_recommended}")
    print(f"ready_for_local_oauth={checklist.ready_for_local_oauth}")
    print(f"ready_for_reauthorization={checklist.ready_for_reauthorization}")
    print(f"ready_for_safe_preview={checklist.ready_for_safe_preview}")
    print(f"ready_for_guarded_real_request={checklist.ready_for_guarded_real_request}")
    print(f"real_api_requested={checklist.real_api_requested}")
    print(f"real_api_allowed={checklist.real_api_allowed}")
    print(f"runtime_guard_error={checklist.runtime_guard_error}")
    print(f"message={checklist.message}")
    print(f"next_action={checklist.next_action}")
    print("checks=")
    for check in checklist.checks:
        print(f"  - {check.key}: ok={check.ok} status={check.status} next_action={check.next_action}")
    print(f"oauth_helper={checklist.commands.oauth_helper}")
    print(f"reset_dry_run={checklist.commands.reset_dry_run}")
    print(f"reset_apply={checklist.commands.reset_apply}")
    print(f"config_check={checklist.commands.config_check}")
    print(f"connection_checklist={checklist.commands.connection_checklist}")
    print(f"safe_preview={checklist.commands.safe_preview}")

    if checklist.error:
        print("[google-health-connection-checklist] WARN")
        return 1

    print("[google-health-connection-checklist] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
