from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from datetime import timedelta
from functools import partial
from hashlib import sha256
import json
import os
from pathlib import Path
from threading import Barrier, Lock
from typing import get_args
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient
import httpx
import pytest

from app.api.public_advice import router
from app.main import app as normal_app
from app.models.advice import AdviceCharacterId, AdviceMood
from app.services.advice_cost import LOCAL_TEST_MODEL
from app.services.gemini_public_advice import (
    GEMINI_MODEL,
    GEMINI_SDK_VERSION,
    MAXIMUM_COST_MICRODOLLARS,
    SYSTEM_INSTRUCTION,
    advice_prompt,
    gemini_advice_runtime,
)
from app.services.postgres_public_advice import (
    PostgresAdviceGenerationControl,
    PostgresAdviceInvites,
    postgres_advice_runtime,
)
from app.services import public_advice_startup
from scripts.public_advice_invite import create_local_app, main


INPUT = {"mood": "normal", "character_id": "gentle_mina"}
PATH = "/v1/advice"
MAX_COST = LOCAL_TEST_MODEL.maximum_cost


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
        control = PostgresAdviceGenerationControl(dsn)
        control.set_monthly_budget(MAX_COST * 9)
        control.set_enabled(True)
        yield dsn, psycopg.connect
    finally:
        with psycopg.connect(base_dsn) as connection:
            connection.execute(f"DROP SCHEMA {schema} CASCADE")


def reply(app, issued):
    with TestClient(app) as client:
        return client.post(PATH, json=INPUT, headers={"Authorization": f"Bearer {issued.bearer_token}"})


def worker(dsn, provider, *, per_user=3, total=9):
    app = FastAPI()
    app.include_router(router)
    app.state.public_advice_runtime = postgres_advice_runtime(
        dsn, per_user=per_user, total=total, model=LOCAL_TEST_MODEL, provider=provider
    )
    return app


def test_unconfigured_invite_app_stays_disabled(monkeypatch):
    monkeypatch.delenv("DRC_PUBLIC_ADVICE_POSTGRES_DSN", raising=False)
    with TestClient(create_local_app()) as client:
        response = client.post(PATH, json=INPUT)
    assert response.status_code == 503
    assert response.json() == {"detail": "advice_unavailable"}


def test_synthetic_cost_rounds_up_and_covers_the_fixed_prompt():
    assert MAX_COST == 394
    with pytest.raises(ValueError, match="full synthetic prompt"):
        replace(LOCAL_TEST_MODEL, max_input_tokens=64)
    with pytest.raises(ValueError, match="positive integer"):
        replace(LOCAL_TEST_MODEL, input_price_per_million=1.5)


def test_missing_model_configuration_does_not_start_generation(monkeypatch):
    monkeypatch.setenv("DRC_PUBLIC_ADVICE_POSTGRES_DSN", "unused")
    monkeypatch.setenv("DRC_PUBLIC_ADVICE_TEST_PER_USER", "3")
    monkeypatch.setenv("DRC_PUBLIC_ADVICE_TEST_TOTAL", "9")
    monkeypatch.delenv("DRC_PUBLIC_ADVICE_TEST_MODEL", raising=False)
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
    monkeypatch.setenv("DRC_PUBLIC_ADVICE_TEST_MODEL", LOCAL_TEST_MODEL.name)
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


@pytest.mark.parametrize("exhausted", ["user", "global", "budget"])
def test_independent_workers_respect_limits(db, exhausted):
    dsn, connect = db
    if exhausted == "budget":
        PostgresAdviceGenerationControl(dsn).set_monthly_budget(MAX_COST * 2)
    invites = PostgresAdviceInvites(dsn)
    tokens = [
        invites.issue("same-user" if exhausted == "user" else f"user-{i}", timedelta(hours=1))
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
        app = worker(dsn, generate, per_user=2, total=2 if exhausted == "global" else 9)
        barrier.wait(timeout=10)
        return reply(app, token)

    with ThreadPoolExecutor(max_workers=len(tokens)) as pool:
        results = list(pool.map(send, tokens))
    assert sorted(result.status_code for result in results) == [200, 200, 429, 429, 429, 429]
    limit = "user_quota_exceeded" if exhausted == "user" else "global_quota_exceeded"
    assert all(result.json() == {"detail": limit} for result in results if result.status_code == 429)
    assert len(calls) == 2
    for call in calls:
        assert call["model"] == LOCAL_TEST_MODEL.name
        assert "Give one short Japanese" in call["prompt"]
        assert call["prompt"].endswith("Mood: normal\nCharacter: gentle_mina")
        assert len(call["prompt"].encode("utf-8")) <= call["max_input_tokens"] == 128
        assert call["max_output_tokens"] == 96
    with connect(dsn) as connection:
        total, = connection.execute("SELECT attempts FROM drc_advice_daily_total").fetchone()
        user_total, = connection.execute("SELECT sum(attempts) FROM drc_advice_daily_user").fetchone()
        cost, = connection.execute("SELECT reserved_units FROM drc_advice_monthly_cost").fetchone()
    assert total == user_total == 2
    assert cost == MAX_COST * 2


@pytest.mark.parametrize("provider_error", [RuntimeError, TimeoutError])
def test_failed_generation_is_charged_and_day_and_month_use_utc(db, provider_error):
    dsn, connect = db
    from psycopg.conninfo import make_conninfo

    with connect(dsn) as connection:
        utc_day, hour = connection.execute(
            "SELECT (now() AT TIME ZONE 'UTC')::date, extract(hour FROM now() AT TIME ZONE 'UTC')"
        ).fetchone()
        # Preserve a previous day's tally without importing it into today's quota.
        connection.execute("INSERT INTO drc_advice_daily_total VALUES (%s, 99)", (utc_day - timedelta(days=1),))
        previous_month = (utc_day.replace(day=1) - timedelta(days=1)).replace(day=1)
        connection.execute(
            "INSERT INTO drc_advice_monthly_cost VALUES (%s, %s)", (previous_month, 99 * MAX_COST)
        )

    zone = "Pacific/Honolulu" if hour < 10 else "Pacific/Kiritimati"
    from psycopg.conninfo import conninfo_to_dict

    dsn = make_conninfo(dsn, options=f"{conninfo_to_dict(dsn)['options']} -c TimeZone={zone}")
    invites = PostgresAdviceInvites(dsn)
    token = invites.issue("worker-test", timedelta(hours=1))

    def fail(**selection):
        raise provider_error("Synthetic upstream failure")

    app = worker(dsn, fail, per_user=1, total=1)
    assert reply(app, token).json() == {"detail": "upstream_failure"}
    assert reply(app, token).json() == {"detail": "user_quota_exceeded"}
    with connect(dsn) as connection:
        day, used = connection.execute("SELECT utc_day, attempts FROM drc_advice_daily_user").fetchone()
        cost, = connection.execute(
            "SELECT reserved_units FROM drc_advice_monthly_cost WHERE utc_month = %s",
            (utc_day.replace(day=1),),
        ).fetchone()
    assert (day, used) == (utc_day, 1)
    assert cost == MAX_COST


@pytest.mark.parametrize("failure", ["authentication", "quota_write", "cost_write"])
def test_store_failure_returns_503_without_generation_and_rolls_back(db, failure):
    dsn, connect = db
    token = PostgresAdviceInvites(dsn).issue("participant-1", timedelta(hours=1))
    with connect(dsn) as connection:
        if failure == "authentication":
            connection.execute("ALTER TABLE drc_advice_invites RENAME TO unavailable_invites")
        elif failure == "quota_write":
            connection.execute("ALTER TABLE drc_advice_daily_user ADD CHECK (attempts = 0)")
        else:
            connection.execute("ALTER TABLE drc_advice_monthly_cost ADD CHECK (reserved_units = 0)")

    def generate(**selection):
        pytest.fail("A storage error must prevent the upstream call.")

    response = reply(worker(dsn, generate), token)
    assert response.status_code == 503
    assert response.json() == {"detail": "advice_unavailable"}
    with connect(dsn) as connection:
        assert connection.execute("SELECT * FROM drc_advice_daily_total").fetchall() == []
        assert connection.execute("SELECT * FROM drc_advice_daily_user").fetchall() == []
        assert connection.execute("SELECT * FROM drc_advice_monthly_cost").fetchall() == []


@pytest.mark.parametrize("remaining", [0, MAX_COST - 1])
def test_exact_budget_or_short_remaining_balance(db, remaining):
    dsn, connect = db
    PostgresAdviceGenerationControl(dsn).set_monthly_budget(MAX_COST + remaining)
    invites = PostgresAdviceInvites(dsn)
    token = invites.issue("worker-test", timedelta(hours=1))
    calls = []

    def generate(**parameters):
        calls.append(parameters)
        return "無理せず進もう。"

    assert reply(worker(dsn, generate), token).status_code == 200
    invites.initialize_schema()
    restarted = worker(dsn, generate)
    denied = reply(restarted, token)
    assert denied.status_code == 429
    assert denied.json() == {"detail": "global_quota_exceeded"}
    assert len(calls) == 1
    with connect(dsn) as connection:
        assert connection.execute("SELECT attempts FROM drc_advice_daily_total").fetchall() == [(1,)]
        assert connection.execute("SELECT attempts FROM drc_advice_daily_user").fetchall() == [(1,)]
        assert connection.execute("SELECT reserved_units FROM drc_advice_monthly_cost").fetchall() == [(MAX_COST,)]


def test_operator_stop_and_missing_budget_fail_closed(db, monkeypatch):
    dsn, connect = db
    token = PostgresAdviceInvites(dsn).issue("worker-test", timedelta(hours=1))
    calls = []

    def generate(**parameters):
        calls.append(parameters)
        return "無理せず進もう。"

    app = worker(dsn, generate)
    monkeypatch.setenv("DRC_PUBLIC_ADVICE_POSTGRES_DSN", dsn)
    monkeypatch.setattr("sys.argv", ["invite", "pause"])
    assert main() == 0
    stopped = reply(app, token)
    assert stopped.status_code == 503
    assert stopped.json() == {"detail": "advice_unavailable"}
    with connect(dsn) as connection:
        connection.execute("UPDATE drc_advice_generation_control SET monthly_budget = NULL")
    monkeypatch.setattr("sys.argv", ["invite", "resume"])
    with pytest.raises(SystemExit) as error:
        main()
    assert error.value.code == 1
    assert reply(app, token).status_code == 503
    assert not calls
    with connect(dsn) as connection:
        assert connection.execute("SELECT * FROM drc_advice_daily_total").fetchall() == []
        assert connection.execute("SELECT * FROM drc_advice_daily_user").fetchall() == []
        assert connection.execute("SELECT * FROM drc_advice_monthly_cost").fetchall() == []

    monkeypatch.setattr("sys.argv", ["invite", "set-monthly-budget", str(MAX_COST)])
    assert main() == 0
    monkeypatch.setattr("sys.argv", ["invite", "resume"])
    assert main() == 0
    assert reply(app, token).status_code == 200
    assert len(calls) == 1


@pytest.fixture
def gemini_candidate(db):
    sdk = pytest.importorskip("google.genai")
    if sdk.__version__ != GEMINI_SDK_VERSION:
        pytest.skip(f"This transport test requires google-genai {GEMINI_SDK_VERSION}.")
    dsn, _ = db

    def create(transport, counter=lambda system, prompt: len((system + prompt).encode("utf-8"))):
        return gemini_advice_runtime(
            dsn, per_user=9, total=9, api_key="mock-transport-only",
            count_input_tokens=counter, transport=httpx.MockTransport(transport),
        )

    return create


def gemini_mock_reply(*, prompt_tokens=79, thoughts_tokens=15, finish_reason="STOP"):
    return httpx.Response(200, json={
        "candidates": [{
            "content": {"role": "model", "parts": [{"text": "無理せず進もう。"}]},
            "finishReason": finish_reason,
        }],
        "usageMetadata": {
            "promptTokenCount": prompt_tokens,
            "candidatesTokenCount": 12,
            "thoughtsTokenCount": thoughts_tokens,
        },
    })


def test_gemini_candidate_sends_only_the_bounded_request(db, gemini_candidate):
    dsn, connect = db
    control = PostgresAdviceGenerationControl(dsn)
    assert MAXIMUM_COST_MICRODOLLARS == 512
    control.set_monthly_budget(9 * MAXIMUM_COST_MICRODOLLARS)
    token = PostgresAdviceInvites(dsn).issue("gemini-test", timedelta(hours=1))
    requests = []

    def handle(request):
        requests.append(request)
        return gemini_mock_reply()

    cases = [(mood, character) for mood in get_args(AdviceMood) for character in get_args(AdviceCharacterId)]
    app = FastAPI()
    app.include_router(router)
    with gemini_candidate(handle) as runtime, TestClient(app) as client:
        app.state.public_advice_runtime = runtime
        for index, (mood, character) in enumerate(cases, start=1):
            response = client.post(
                PATH, json={"mood": mood, "character_id": character},
                headers={"Authorization": f"Bearer {token.bearer_token}"},
            )
            assert response.json() == {"message": "無理せず進もう。"}
            assert response.status_code == 200
            assert len(requests) == index
            sent = requests[-1]
            assert sent.method == "POST"
            assert sent.url == f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
            assert sent.extensions["timeout"]["read"] == 10.0
            assert json.loads(sent.content) == {
                "contents": [{"role": "user", "parts": [{"text": advice_prompt(mood, character)}]}],
                "systemInstruction": {"parts": [{"text": SYSTEM_INSTRUCTION}]},
                "generationConfig": {
                    "candidateCount": 1,
                    "maxOutputTokens": 256,
                    "thinkingConfig": {"thinking_level": "MINIMAL", "include_thoughts": False},
                },
                "serviceTier": "standard",
            }
    with connect(dsn) as connection:
        assert connection.execute("SELECT reserved_units FROM drc_advice_monthly_cost").fetchall() == [(9 * 512,)]


@pytest.mark.parametrize("outcome", [429, 503, "timeout", "redirect", "too_many_thoughts", "too_much_input", "truncated"])
def test_gemini_candidate_failure_makes_one_attempt_and_keeps_the_reservation(db, gemini_candidate, outcome):
    dsn, connect = db
    token = PostgresAdviceInvites(dsn).issue("gemini-test", timedelta(hours=1))
    requests = []

    def handle(request):
        requests.append(request)
        if outcome == "timeout":
            raise httpx.ReadTimeout("Synthetic timeout", request=request)
        if outcome == "redirect":
            return httpx.Response(307, headers={"Location": "https://unconfigured.invalid"})
        if outcome == "too_many_thoughts":
            return gemini_mock_reply(thoughts_tokens=245)
        if outcome == "too_much_input":
            return gemini_mock_reply(prompt_tokens=513)
        if outcome == "truncated":
            return gemini_mock_reply(finish_reason="MAX_TOKENS")
        return httpx.Response(outcome, json={"error": {"code": outcome, "message": "synthetic"}})

    app = FastAPI()
    app.include_router(router)
    with gemini_candidate(handle) as runtime:
        app.state.public_advice_runtime = runtime
        response = reply(app, token)
    assert response.status_code == 502
    assert response.json() == {"detail": "upstream_failure"}
    assert len(requests) == 1
    with connect(dsn) as connection:
        assert connection.execute("SELECT attempts FROM drc_advice_daily_total").fetchall() == [(1,)]
        assert connection.execute("SELECT reserved_units FROM drc_advice_monthly_cost").fetchall() == [(512,)]


def test_gemini_candidate_does_not_send_without_auth_budget_or_operator_enable(db, gemini_candidate):
    dsn, connect = db
    control = PostgresAdviceGenerationControl(dsn)
    control.set_monthly_budget(MAXIMUM_COST_MICRODOLLARS - 1)
    token = PostgresAdviceInvites(dsn).issue("gemini-test", timedelta(hours=1))

    def must_not_send(request):
        pytest.fail("A rejected request reached the Gemini transport.")

    app = FastAPI()
    app.include_router(router)
    with gemini_candidate(must_not_send) as runtime, TestClient(app) as client:
        app.state.public_advice_runtime = runtime
        assert client.post(PATH, json=INPUT).status_code == 401
        denied = reply(app, token)
        assert (denied.status_code, denied.json()) == (429, {"detail": "global_quota_exceeded"})
        control.set_monthly_budget(MAXIMUM_COST_MICRODOLLARS)
        control.set_enabled(False)
        stopped = reply(app, token)
        assert (stopped.status_code, stopped.json()) == (503, {"detail": "advice_unavailable"})
    with connect(dsn) as connection:
        assert connection.execute("SELECT attempts FROM drc_advice_daily_total").fetchall() == []
        assert connection.execute("SELECT reserved_units FROM drc_advice_monthly_cost").fetchall() == []


def test_gemini_candidate_refuses_an_over_limit_input_before_opening_runtime(gemini_candidate):
    def must_not_send(request):
        pytest.fail("Input preflight attempted an HTTP request.")

    with pytest.raises(ValueError, match="input token count"):
        with gemini_candidate(must_not_send, counter=lambda system, prompt: 513):
            pytest.fail("The runtime should be unavailable when an input exceeds the limit.")


@pytest.fixture
def normal_gemini_settings(monkeypatch):
    def configure(dsn):
        monkeypatch.setenv("DRC_PUBLIC_ADVICE_GEMINI_ENABLED", "1")
        monkeypatch.setenv("DRC_PUBLIC_ADVICE_GEMINI_API_KEY", "mock-transport-only")
        monkeypatch.setenv("DRC_PUBLIC_ADVICE_GEMINI_POSTGRES_DSN", dsn)
        monkeypatch.setenv("DRC_PUBLIC_ADVICE_GEMINI_DAILY_PER_USER", "1")
        monkeypatch.setenv("DRC_PUBLIC_ADVICE_GEMINI_DAILY_TOTAL", "2")
        if not os.getenv("DRC_GEMINI_TOKENIZER_DIR"):
            monkeypatch.setenv("DRC_GEMINI_TOKENIZER_DIR", "offline-test-counter")
            monkeypatch.setattr(public_advice_startup, "load_gemini_input_counter", lambda _: lambda *_: 83)

    return configure


@pytest.mark.parametrize("missing", [
    "DRC_PUBLIC_ADVICE_GEMINI_ENABLED",
    "DRC_PUBLIC_ADVICE_GEMINI_API_KEY",
    "DRC_PUBLIC_ADVICE_GEMINI_POSTGRES_DSN",
    "DRC_PUBLIC_ADVICE_GEMINI_DAILY_TOTAL",
    "DRC_GEMINI_TOKENIZER_DIR",
])
def test_normal_app_disables_incomplete_gemini_configuration(monkeypatch, normal_gemini_settings, missing):
    normal_gemini_settings("unused")
    monkeypatch.delenv(missing)

    def unexpected(*args, **kwargs):
        pytest.fail("Disabled or incomplete configuration reached DB or Gemini setup.")

    monkeypatch.setattr(PostgresAdviceGenerationControl, "has_monthly_budget", unexpected)
    monkeypatch.setattr(public_advice_startup, "gemini_advice_runtime", unexpected)
    with TestClient(normal_app) as client:
        response = client.post(PATH, json=INPUT)
    assert (response.status_code, response.json()) == (503, {"detail": "advice_unavailable"})


@pytest.mark.parametrize("fault", ["missing_budget", "missing_database"])
def test_normal_app_starts_with_unavailable_ledger(
    db, monkeypatch, normal_gemini_settings, fault
):
    dsn, connect = db
    if fault == "missing_budget":
        with connect(dsn) as connection:
            connection.execute("UPDATE drc_advice_generation_control SET enabled = false, monthly_budget = NULL")
    else:
        from psycopg.conninfo import make_conninfo

        dsn = make_conninfo(dsn, dbname="drc_missing_" + uuid4().hex)
    normal_gemini_settings(dsn)

    def unexpected(*args, **kwargs):
        pytest.fail("An unavailable ledger reached Gemini setup.")

    monkeypatch.setattr(public_advice_startup, "gemini_advice_runtime", unexpected)
    with TestClient(normal_app) as client:
        response = client.post(PATH, json=INPUT)
        assert (response.status_code, response.json()) == (503, {"detail": "advice_unavailable"})


def test_normal_app_lifespan_enforces_invite_and_quota_before_gemini(
    db, monkeypatch, normal_gemini_settings,
):
    sdk = pytest.importorskip("google.genai")
    if sdk.__version__ != GEMINI_SDK_VERSION:
        pytest.skip(f"This transport test requires google-genai {GEMINI_SDK_VERSION}.")
    dsn, connect = db
    normal_gemini_settings(dsn)
    control = PostgresAdviceGenerationControl(dsn)
    invites = PostgresAdviceInvites(dsn)
    participants = [invites.issue(f"participant-{index}", timedelta(hours=1)) for index in range(3)]
    requests = []

    def handle(request):
        requests.append(request)
        assert request.method == "POST"
        assert request.url.path == f"/v1beta/models/{GEMINI_MODEL}:generateContent"
        with connect(dsn) as connection:
            assert connection.execute("SELECT reserved_units FROM drc_advice_monthly_cost").fetchall() == [
                (len(requests) * 512,),
            ]
        return gemini_mock_reply()

    monkeypatch.setattr(
        public_advice_startup, "gemini_advice_runtime",
        partial(gemini_advice_runtime, transport=httpx.MockTransport(handle)),
    )

    def assert_response(token, status, detail):
        response = client.post(PATH, json=INPUT, headers={"Authorization": f"Bearer {token}"})
        assert (response.status_code, response.json()) == (status, detail)

    unavailable = {"detail": "advice_unavailable"}
    token1, token2, token3 = [participant.bearer_token for participant in participants]
    control.set_enabled(False)
    with TestClient(normal_app) as client:
        assert hasattr(normal_app.state, "public_advice_runtime")
        assert_response("x" * 43, 401, {"detail": "authentication_required"})
        assert_response(token1, 503, unavailable)
        control.set_monthly_budget(511)
        control.set_enabled(True)
        assert_response(token1, 429, {"detail": "global_quota_exceeded"})
        assert not requests

        control.set_monthly_budget(1536)
        assert_response(token1, 200, {"message": "無理せず進もう。"})
        assert_response(token1, 429, {"detail": "user_quota_exceeded"})
        assert len(requests) == 1
        assert_response(token2, 200, {"message": "無理せず進もう。"})
        assert_response(token3, 429, {"detail": "global_quota_exceeded"})
        control.set_enabled(False)
        assert_response(token3, 503, unavailable)
        control.set_enabled(True)
        with connect(dsn) as connection:
            connection.execute("ALTER TABLE drc_advice_generation_control RENAME TO unavailable_control")
        assert_response(token3, 503, unavailable)
        with connect(dsn) as connection:
            connection.execute("ALTER TABLE unavailable_control RENAME TO drc_advice_generation_control")
            connection.execute("ALTER TABLE drc_advice_invites RENAME TO unavailable_invites")
        assert_response(token3, 503, unavailable)
        assert len(requests) == 2
        with connect(dsn) as connection:
            assert connection.execute("SELECT attempts FROM drc_advice_daily_total").fetchall() == [(2,)]
            assert connection.execute("SELECT reserved_units FROM drc_advice_monthly_cost").fetchall() == [(1024,)]
    assert not hasattr(normal_app.state, "public_advice_runtime")


def test_gemini_candidate_input_fits_using_published_local_tokenizer():
    directory = os.getenv("DRC_GEMINI_TOKENIZER_DIR")
    if not directory:
        pytest.skip("Local Gemma tokenizer artifacts are not configured.")
    from tokenizers import Tokenizer

    folder = Path(directory)
    tokenizer = Tokenizer.from_file(str(folder / "tokenizer.json"))
    count = public_advice_startup.load_gemini_input_counter(folder)
    counts = {}
    for mood in get_args(AdviceMood):
        for character in get_args(AdviceCharacterId):
            prompt = advice_prompt(mood, character)
            text_count = sum(len(tokenizer.encode(text).ids) for text in (SYSTEM_INSTRUCTION, prompt))
            framed_count = count(SYSTEM_INSTRUCTION, prompt)
            counts[mood, character] = (text_count, framed_count)
    assert len(counts) == 9
    assert all(0 < text <= framed <= 512 for text, framed in counts.values()), counts
