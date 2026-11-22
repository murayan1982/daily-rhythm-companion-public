from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from hashlib import sha256
import re
from secrets import token_urlsafe
from uuid import UUID, uuid4

from app.services.advice_cost import (
    SyntheticAdviceModel,
    SyntheticAdviceProvider,
    generate_synthetic_advice,
)
from app.services.public_advice import PublicAdviceRuntime, QuotaExceeded


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
CREATE TABLE IF NOT EXISTS drc_advice_generation_control (
    singleton boolean PRIMARY KEY CHECK (singleton),
    enabled boolean NOT NULL DEFAULT false,
    monthly_budget bigint CHECK (monthly_budget > 0),
    CHECK (NOT enabled OR monthly_budget IS NOT NULL)
);
INSERT INTO drc_advice_generation_control (singleton) VALUES (true) ON CONFLICT DO NOTHING;
CREATE TABLE IF NOT EXISTS drc_advice_monthly_cost (
    utc_month date PRIMARY KEY,
    reserved_units bigint NOT NULL CHECK (reserved_units >= 0)
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


class PostgresAdviceGenerationControl:
    def __init__(self, dsn: str):
        self._dsn = dsn

    def has_monthly_budget(self) -> bool:
        with _connection(self._dsn) as connection:
            row = connection.execute(
                """
                SELECT monthly_budget IS NOT NULL
                FROM drc_advice_generation_control WHERE singleton
                """
            ).fetchone()
        return row is not None and row[0]

    def set_monthly_budget(self, units: int) -> None:
        if units <= 0:
            raise ValueError("The monthly budget must be positive.")
        with _connection(self._dsn) as connection:
            if connection.execute(
                "UPDATE drc_advice_generation_control SET monthly_budget = %s WHERE singleton",
                (units,),
            ).rowcount != 1:
                raise RuntimeError("Generation control has not been initialized.")

    def set_enabled(self, enabled: bool) -> None:
        with _connection(self._dsn) as connection:
            if connection.execute(
                """
                UPDATE drc_advice_generation_control SET enabled = %s
                WHERE singleton AND (NOT %s OR monthly_budget IS NOT NULL)
                """,
                (enabled, enabled),
            ).rowcount != 1:
                raise RuntimeError("Generation control or monthly budget is missing.")


class PostgresDailyAdviceQuota:
    def __init__(self, dsn: str, *, per_user: int, total: int, maximum_cost: int):
        if min(per_user, total, maximum_cost) <= 0:
            raise ValueError("Daily limits and the maximum cost must be positive.")
        self._dsn = dsn
        self._per_user = per_user
        self._total = total
        self._maximum_cost = maximum_cost

    def reserve(self, user_id: str) -> QuotaExceeded | None:
        with _connection(self._dsn) as connection:
            # The operator updates and every reservation take the same row lock.
            control = connection.execute(
                """
                SELECT enabled, monthly_budget FROM drc_advice_generation_control
                WHERE singleton FOR UPDATE
                """
            ).fetchone()
            if not control or not control[0] or control[1] is None:
                raise RuntimeError("Advice generation is unavailable.")
            utc_day, utc_month = connection.execute(
                """
                SELECT utc_now::date, date_trunc('month', utc_now)::date
                FROM (SELECT clock_timestamp() AT TIME ZONE 'UTC' AS utc_now) AS admission
                """
            ).fetchone()
            total = connection.execute(
                "SELECT attempts FROM drc_advice_daily_total WHERE utc_day = %s",
                (utc_day,),
            ).fetchone()
            user = connection.execute(
                "SELECT attempts FROM drc_advice_daily_user WHERE utc_day = %s AND user_id = %s",
                (utc_day, user_id),
            ).fetchone()
            if user and user[0] >= self._per_user:
                return "user_quota_exceeded"
            if total and total[0] >= self._total:
                return "global_quota_exceeded"
            reserved = connection.execute(
                "SELECT reserved_units FROM drc_advice_monthly_cost WHERE utc_month = %s",
                (utc_month,),
            ).fetchone()
            if (reserved[0] if reserved else 0) + self._maximum_cost > control[1]:
                return "global_quota_exceeded"
            connection.execute(
                """
                INSERT INTO drc_advice_daily_total (utc_day, attempts) VALUES (%s, 1)
                ON CONFLICT (utc_day) DO UPDATE SET attempts = drc_advice_daily_total.attempts + 1
                """,
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
            connection.execute(
                """
                INSERT INTO drc_advice_monthly_cost (utc_month, reserved_units) VALUES (%s, %s)
                ON CONFLICT (utc_month)
                DO UPDATE SET reserved_units =
                    drc_advice_monthly_cost.reserved_units + EXCLUDED.reserved_units
                """,
                (utc_month, self._maximum_cost),
            )
        return None


def postgres_advice_runtime(
    dsn: str, *, per_user: int, total: int, model: SyntheticAdviceModel,
    provider: SyntheticAdviceProvider,
) -> PublicAdviceRuntime:
    return PublicAdviceRuntime(
        authenticate=PostgresAdviceInvites(dsn).authenticate,
        quota=PostgresDailyAdviceQuota(
            dsn, per_user=per_user, total=total, maximum_cost=model.maximum_cost
        ),
        generate=generate_synthetic_advice(model, provider),
    )
