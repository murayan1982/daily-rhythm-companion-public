from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from hashlib import sha256
import re
from secrets import token_urlsafe
from uuid import UUID, uuid4

from app.services.public_advice import AdviceGenerator, PublicAdviceRuntime, QuotaExceeded


_SCHEMA = """
CREATE TABLE IF NOT EXISTS drc_advice_invites (
    token_id uuid PRIMARY KEY,
    token_hash bytea UNIQUE NOT NULL CHECK (octet_length(token_hash) = 32),
    user_id text NOT NULL,
    expires_at timestamptz NOT NULL,
    revoked_at timestamptz
);
CREATE TABLE IF NOT EXISTS drc_advice_daily_total (
    utc_day date PRIMARY KEY,
    attempts bigint NOT NULL DEFAULT 0 CHECK (attempts >= 0)
);
CREATE TABLE IF NOT EXISTS drc_advice_daily_user (
    utc_day date NOT NULL,
    user_id text NOT NULL,
    attempts bigint NOT NULL CHECK (attempts >= 0),
    PRIMARY KEY (utc_day, user_id)
);
"""


@contextmanager
def _connection(dsn: str) -> Iterator:
    from psycopg import IsolationLevel, connect

    with connect(dsn, connect_timeout=3, autocommit=False) as connection:
        connection.isolation_level = IsolationLevel.READ_COMMITTED
        connection.execute("SET LOCAL statement_timeout = '5s'")
        yield connection


@dataclass(frozen=True)
class IssuedAdviceToken:
    token_id: UUID
    expires_at: datetime
    bearer_token: str = field(repr=False)


class PostgresAdviceInvites:
    def __init__(self, dsn: str):
        self._dsn = dsn

    def initialize_schema(self) -> None:
        with _connection(self._dsn) as connection:
            connection.execute(_SCHEMA)

    def issue(self, user_id: str, ttl: timedelta) -> IssuedAdviceToken:
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", user_id) or ttl <= timedelta(0):
            raise ValueError("A valid participant ID and positive token lifetime are required.")
        token = token_urlsafe(32)
        token_id = uuid4()
        with _connection(self._dsn) as connection:
            expires_at, = connection.execute(
                """
                INSERT INTO drc_advice_invites (token_id, token_hash, user_id, expires_at)
                VALUES (%s, %s, %s, clock_timestamp() + make_interval(secs => %s))
                RETURNING expires_at
                """,
                (token_id, sha256(token.encode("ascii")).digest(), user_id, ttl.total_seconds()),
            ).fetchone()
        return IssuedAdviceToken(token_id, expires_at, token)

    def revoke(self, token_id: UUID) -> bool:
        with _connection(self._dsn) as connection:
            return connection.execute(
                """
                UPDATE drc_advice_invites SET revoked_at = clock_timestamp()
                WHERE token_id = %s AND revoked_at IS NULL
                """,
                (token_id,),
            ).rowcount == 1

    def authenticate(self, token: str) -> str | None:
        if not re.fullmatch(r"[A-Za-z0-9_-]{43}", token):
            return None
        with _connection(self._dsn) as connection:
            row = connection.execute(
                """
                SELECT user_id FROM drc_advice_invites
                WHERE token_hash = %s AND revoked_at IS NULL AND expires_at > clock_timestamp()
                """,
                (sha256(token.encode("ascii")).digest(),),
            ).fetchone()
        return row[0] if row else None


class PostgresDailyAdviceQuota:
    def __init__(self, dsn: str, *, per_user: int, total: int):
        if per_user <= 0 or total <= 0:
            raise ValueError("Daily limits must be positive.")
        self._dsn = dsn
        self._per_user = per_user
        self._total = total

    def reserve(self, user_id: str) -> QuotaExceeded | None:
        with _connection(self._dsn) as connection:
            utc_day, = connection.execute(
                "SELECT (CURRENT_TIMESTAMP AT TIME ZONE 'UTC')::date"
            ).fetchone()
            connection.execute(
                "INSERT INTO drc_advice_daily_total (utc_day) VALUES (%s) ON CONFLICT DO NOTHING",
                (utc_day,),
            )
            # All workers lock the same row before reading or changing either counter.
            total, = connection.execute(
                "SELECT attempts FROM drc_advice_daily_total WHERE utc_day = %s FOR UPDATE",
                (utc_day,),
            ).fetchone()
            user = connection.execute(
                "SELECT attempts FROM drc_advice_daily_user WHERE utc_day = %s AND user_id = %s",
                (utc_day, user_id),
            ).fetchone()
            if user and user[0] >= self._per_user:
                return "user_quota_exceeded"
            if total >= self._total:
                return "global_quota_exceeded"
            connection.execute(
                "UPDATE drc_advice_daily_total SET attempts = attempts + 1 WHERE utc_day = %s",
                (utc_day,),
            )
            connection.execute(
                """
                INSERT INTO drc_advice_daily_user (utc_day, user_id, attempts) VALUES (%s, %s, 1)
                ON CONFLICT (utc_day, user_id)
                DO UPDATE SET attempts = drc_advice_daily_user.attempts + 1
                """,
                (utc_day, user_id),
            )
        return None


def postgres_advice_runtime(
    dsn: str, *, per_user: int, total: int, generate: AdviceGenerator
) -> PublicAdviceRuntime:
    return PublicAdviceRuntime(
        authenticate=PostgresAdviceInvites(dsn).authenticate,
        quota=PostgresDailyAdviceQuota(dsn, per_user=per_user, total=total),
        generate=generate,
    )
