"""Local operator commands and a provider-free ASGI entry point for invite testing."""

import argparse
from datetime import UTC, timedelta
import os
from uuid import UUID

from fastapi import FastAPI

from app.api.public_advice import router
from app.services.postgres_public_advice import PostgresAdviceInvites, postgres_advice_runtime


_DSN_ENV = "DRC_PUBLIC_ADVICE_POSTGRES_DSN"


def _test_advice(*, mood: str, character_id: str) -> str:
    return "今日は自分のペースでいこう。"


def create_local_app() -> FastAPI:
    app = FastAPI(title="DRC local invite test")
    app.include_router(router)
    dsn = os.getenv(_DSN_ENV)
    try:
        per_user = int(os.getenv("DRC_PUBLIC_ADVICE_TEST_PER_USER", ""))
        total = int(os.getenv("DRC_PUBLIC_ADVICE_TEST_TOTAL", ""))
    except ValueError:
        return app
    if dsn and per_user > 0 and total > 0:
        app.state.public_advice_runtime = postgres_advice_runtime(
            dsn, per_user=per_user, total=total, generate=_test_advice
        )
    return app


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("init-db")
    issue = commands.add_parser("issue")
    issue.add_argument("user_id")
    issue.add_argument("--ttl-hours", type=int, required=True)
    revoke = commands.add_parser("revoke")
    revoke.add_argument("token_id", type=UUID)
    args = parser.parse_args()
    dsn = os.getenv(_DSN_ENV)
    if not dsn:
        parser.error(f"{_DSN_ENV} is required.")

    invites = PostgresAdviceInvites(dsn)
    try:
        if args.command == "init-db":
            invites.initialize_schema()
            print("Invite schema ready.")
        elif args.command == "revoke":
            if not invites.revoke(args.token_id):
                parser.exit(1, "Token not found or already revoked.\n")
            print("Token revoked.")
        else:
            issued = invites.issue(args.user_id, timedelta(hours=args.ttl_hours))
            print(f"Token ID: {issued.token_id}")
            print(f"Expires (UTC): {issued.expires_at.astimezone(UTC).isoformat()}")
            print(f"Bearer token (displayed once): {issued.bearer_token}")
    except Exception:
        # Connection and SQL errors can include connection parameters.
        parser.exit(1, "Invite operation failed. Check settings and database availability.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
