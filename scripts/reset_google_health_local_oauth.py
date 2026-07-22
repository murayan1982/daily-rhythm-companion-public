from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.services.google_health_oauth_state_store import (  # noqa: E402
    GoogleHealthOAuthStateStore,
)
from app.services.google_health_token_store import GoogleHealthTokenStore  # noqa: E402


def main() -> int:
    """
    Reset local Google Health OAuth development files.

    The script never reads or prints token contents. By default it runs in
    dry-run mode so developers can confirm which local files would be removed
    before deleting anything sensitive.
    """

    parser = argparse.ArgumentParser(
        description="Reset local Google Health OAuth token/state files safely."
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually delete local Google Health OAuth token/state files.",
    )
    parser.add_argument(
        "--token-only",
        action="store_true",
        help="Only reset the stored token file.",
    )
    parser.add_argument(
        "--state-only",
        action="store_true",
        help="Only reset the stored OAuth state file.",
    )

    args = parser.parse_args()

    if args.token_only and args.state_only:
        print("[google-health-local-oauth-reset] ERROR")
        print("token_only_and_state_only_cannot_both_be_enabled=True")
        return 1

    token_store = GoogleHealthTokenStore()
    state_store = GoogleHealthOAuthStateStore()

    targets: list[tuple[str, Path]] = []
    if not args.state_only:
        targets.append(("token_file", token_store.token_file))
    if not args.token_only:
        targets.append(("state_file", state_store.state_file))

    print("[google-health-local-oauth-reset]")
    print(f"mode={'apply' if args.apply else 'dry_run'}")
    print("sensitive_contents_printed=False")

    removed: list[str] = []
    missing: list[str] = []

    for label, path in targets:
        exists = path.exists()
        print(f"{label}={path}")
        print(f"{label}_exists={exists}")

        if not exists:
            missing.append(label)
            continue

        if args.apply:
            path.unlink()
            removed.append(label)

    print(f"removed={removed}")
    print(f"missing={missing}")

    if args.apply:
        print("next_step=Start the backend, open GET /google-health/connect, and reauthorize with the minimal sleep scope.")
        print("[google-health-local-oauth-reset] OK")
        return 0

    print("next_step=Re-run with --apply to delete these local OAuth files.")
    print("[google-health-local-oauth-reset] DRY_RUN_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
