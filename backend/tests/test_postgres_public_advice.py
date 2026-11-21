from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from hashlib import sha256
import os
from threading import Barrier, Lock
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from app.api.public_advice import router
from app.services.postgres_public_advice import PostgresAdviceInvites, postgres_advice_runtime
from scripts.public_advice_invite import create_local_app, main


INPUT = {"mood": "normal", "character_id": "gentle_mina"}
PATH = "/v1/advice"


@pytest.fixture
def db():
    base_dsn = os.getenv("DRC_PUBLIC_ADVICE_TEST_POSTGRES_DSN")
    if not base_dsn:
        pytest.skip("Local PostgreSQL test DSN is not configured.")
    import psycopg
    from psycopg.conninfo import make_conninfo

    # Each test uses only tables in its own disposable schema.
    schema = "drc_test_" + uuid4().hex
    dsn = make_conninfo(base_dsn, options=f"-c search_path={schema}")
    with psycopg.connect(base_dsn) as connection:
        connection.execute(f"CREATE SCHEMA {schema}")
    try:
        PostgresAdviceInvites(dsn).initialize_schema()
        yield dsn, psycopg.connect
    finally:
        with psycopg.connect(base_dsn) as connection:
            connection.execute(f"DROP SCHEMA {schema} CASCADE")


def reply(app, issued):
    with TestClient(app) as client:
        return client.post(PATH, json=INPUT, headers={"Authorization": f"Bearer {issued.bearer_token}"})


def worker(dsn, generate, *, per_user=3, total=9):
    app = FastAPI()
    app.include_router(router)
    app.state.public_advice_runtime = postgres_advice_runtime(
        dsn, per_user=per_user, total=total, generate=generate
    )
    return app


def test_unconfigured_invite_app_stays_disabled(monkeypatch):
    monkeypatch.delenv("DRC_PUBLIC_ADVICE_POSTGRES_DSN", raising=False)
    with TestClient(create_local_app()) as client:
        response = client.post(PATH, json=INPUT)
    assert response.status_code == 503
    assert response.json() == {"detail": "advice_unavailable"}


def test_operator_expiry_revocation_reissue_and_backend_restart(db, monkeypatch, capsys):
    dsn, connect = db
    invites = PostgresAdviceInvites(dsn)
    expired = invites.issue("expired", timedelta(hours=1))
    with connect(dsn) as connection:
        connection.execute(
            "UPDATE drc_advice_invites SET expires_at = clock_timestamp() - interval '1 second' WHERE token_id = %s",
            (expired.token_id,),
        )

    monkeypatch.setenv("DRC_PUBLIC_ADVICE_POSTGRES_DSN", dsn)
    monkeypatch.setenv("DRC_PUBLIC_ADVICE_TEST_PER_USER", "1")
    monkeypatch.setenv("DRC_PUBLIC_ADVICE_TEST_TOTAL", "2")
    monkeypatch.setattr("sys.argv", ["invite", "issue", "participant-1", "--ttl-hours", "1"])
    assert main() == 0
    issued = capsys.readouterr().out.splitlines()
    token_id = issued[0].split(": ", 1)[1]
    token = issued[2].split(": ", 1)[1]
    with connect(dsn) as connection:
        stored_hash, = connection.execute(
            "SELECT token_hash FROM drc_advice_invites WHERE token_id = %s", (token_id,)
        ).fetchone()
    assert stored_hash == sha256(token.encode("ascii")).digest()

    app = create_local_app()
    with TestClient(app) as client:
        assert client.post(PATH, json=INPUT, headers={"Authorization": f"Bearer {token}"}).status_code == 200
    assert reply(app, expired).status_code == 401

    monkeypatch.setattr("sys.argv", ["invite", "revoke", token_id])
    assert main() == 0
    assert token not in capsys.readouterr().out
    replacement = invites.issue("participant-1", timedelta(hours=1))
    other = invites.issue("participant-2", timedelta(hours=1))
    third = invites.issue("participant-3", timedelta(hours=1))

    # A new application has no in-process counter or previous runtime object.
    restarted = create_local_app()
    with TestClient(restarted) as client:
        denied = client.post(PATH, json=INPUT, headers={"Authorization": f"Bearer {token}"})
    assert denied.status_code == 401
    assert reply(restarted, replacement).json() == {"detail": "user_quota_exceeded"}
    assert reply(restarted, other).status_code == 200
    assert reply(restarted, third).json() == {"detail": "global_quota_exceeded"}


@pytest.mark.parametrize("same_user", [True, False])
def test_independent_workers_respect_both_limits(db, same_user):
    dsn, connect = db
    invites = PostgresAdviceInvites(dsn)
    tokens = [
        invites.issue("same-user" if same_user else f"user-{i}", timedelta(hours=1))
        for i in range(6)
    ]
    barrier = Barrier(len(tokens))
    calls = []
    lock = Lock()

    def generate(**selection):
        with lock:
            calls.append(selection)
        return "無理せず進もう。"

    def send(token):
        app = worker(dsn, generate, per_user=2, total=9 if same_user else 2)
        barrier.wait(timeout=10)
        return reply(app, token)

    with ThreadPoolExecutor(max_workers=len(tokens)) as pool:
        results = list(pool.map(send, tokens))
    assert sorted(result.status_code for result in results) == [200, 200, 429, 429, 429, 429]
    limit = "user_quota_exceeded" if same_user else "global_quota_exceeded"
    assert all(result.json() == {"detail": limit} for result in results if result.status_code == 429)
    assert calls == [INPUT, INPUT]
    with connect(dsn) as connection:
        total, = connection.execute("SELECT attempts FROM drc_advice_daily_total").fetchone()
        user_total, = connection.execute("SELECT sum(attempts) FROM drc_advice_daily_user").fetchone()
    assert total == user_total == 2


def test_failed_generation_is_charged_and_day_uses_utc(db):
    dsn, connect = db
    from psycopg.conninfo import make_conninfo

    with connect(dsn) as connection:
        utc_day, hour = connection.execute(
            "SELECT (now() AT TIME ZONE 'UTC')::date, extract(hour FROM now() AT TIME ZONE 'UTC')"
        ).fetchone()
        # Preserve a previous day's tally without importing it into today's quota.
        connection.execute("INSERT INTO drc_advice_daily_total VALUES (%s, 99)", (utc_day - timedelta(days=1),))

    zone = "Pacific/Honolulu" if hour < 10 else "Pacific/Kiritimati"
    from psycopg.conninfo import conninfo_to_dict

    dsn = make_conninfo(dsn, options=f"{conninfo_to_dict(dsn)['options']} -c TimeZone={zone}")
    invites = PostgresAdviceInvites(dsn)
    token = invites.issue("worker-test", timedelta(hours=1))

    def fail(**selection):
        raise RuntimeError("Synthetic upstream failure")

    app = worker(dsn, fail, per_user=1, total=1)
    assert reply(app, token).json() == {"detail": "upstream_failure"}
    assert reply(app, token).json() == {"detail": "user_quota_exceeded"}
    with connect(dsn) as connection:
        day, used = connection.execute("SELECT utc_day, attempts FROM drc_advice_daily_user").fetchone()
    assert (day, used) == (utc_day, 1)


@pytest.mark.parametrize("failure", ["authentication", "quota_write"])
def test_store_failure_returns_503_without_generation_and_rolls_back(db, failure):
    dsn, connect = db
    token = PostgresAdviceInvites(dsn).issue("participant-1", timedelta(hours=1))
    with connect(dsn) as connection:
        if failure == "authentication":
            connection.execute("ALTER TABLE drc_advice_invites RENAME TO unavailable_invites")
        else:
            connection.execute("ALTER TABLE drc_advice_daily_user ADD CHECK (attempts = 0)")

    def generate(**selection):
        pytest.fail("A storage error must prevent the upstream call.")

    response = reply(worker(dsn, generate), token)
    assert response.status_code == 503
    assert response.json() == {"detail": "advice_unavailable"}
    with connect(dsn) as connection:
        assert connection.execute("SELECT * FROM drc_advice_daily_total").fetchall() == []
        assert connection.execute("SELECT * FROM drc_advice_daily_user").fetchall() == []
