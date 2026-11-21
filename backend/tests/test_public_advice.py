from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Barrier, Event

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.public_advice import (
    InMemoryDailyAdviceQuota,
    LocalAdviceTokenVerifier,
    PublicAdviceRuntime,
)


PATH = "/v1/advice"
VALID_INPUT = {"mood": "normal", "character_id": "gentle_mina"}
TOKENS = {
    "synthetic-mina-session": "participant-1",
    "synthetic-renewed-session": "participant-1",
    "synthetic-sora-session": "participant-2",
    "synthetic-rei-session": "participant-3",
}


def auth(token="synthetic-mina-session"):
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def configure(monkeypatch):
    def install(generate, *, per_user=10, total=10, authenticate=None, quota=None):
        monkeypatch.setattr(
            app.state,
            "public_advice_runtime",
            PublicAdviceRuntime(
                authenticate=authenticate or LocalAdviceTokenVerifier(TOKENS),
                quota=quota or InMemoryDailyAdviceQuota(per_user=per_user, total=total),
                generate=generate,
            ),
            raising=False,
        )

    return install


@pytest.fixture
def calls(configure):
    requests = []

    def generate(**selection):
        requests.append(selection)
        return "  今日は自分のペースでいこう。  "

    configure(generate)
    return requests


def test_missing_runtime_stays_disabled(monkeypatch):
    monkeypatch.delattr(app.state, "public_advice_runtime", raising=False)
    reply = TestClient(app).post(PATH, json=VALID_INPUT, headers=auth())
    assert reply.status_code == 503
    assert reply.json() == {"detail": "advice_unavailable"}


@pytest.mark.parametrize("mood", ["energetic", "normal", "tired"])
@pytest.mark.parametrize("character", ["gentle_mina", "cheerful_sora", "cool_rei"])
def test_only_selected_mood_and_character_reach_generator(calls, mood, character):
    selection = {"mood": mood, "character_id": character}
    reply = TestClient(app).post(PATH, json=selection, headers=auth())
    assert reply.status_code == 200
    assert reply.json() == {"message": "今日は自分のペースでいこう。"}
    assert reply.headers["cache-control"] == "no-store"
    assert calls == [selection]


@pytest.mark.parametrize("extra", ["sleep_summary", "message", "history", "user_id", "other"])
def test_extra_fields_are_rejected_without_echo(calls, extra, caplog):
    reply = TestClient(app).post(
        PATH, json={**VALID_INPUT, extra: "synthetic-private-text"}, headers=auth()
    )
    assert reply.status_code == 422
    assert reply.json() == {"detail": "invalid_request"}
    assert reply.headers["cache-control"] == "no-store"
    assert "synthetic-private-text" not in caplog.text
    assert not calls


@pytest.mark.parametrize("payload", [
    {"mood": "normal"},
    {"mood": "happy", "character_id": "gentle_mina"},
    {"mood": "normal", "character_id": "other"},
    {"mood": 1, "character_id": "gentle_mina"},
])
def test_contract_rejects_missing_or_unsupported_values(calls, payload):
    reply = TestClient(app).post(PATH, json=payload, headers=auth())
    assert reply.status_code == 422
    assert reply.json() == {"detail": "invalid_request"}
    assert not calls


def test_request_rejects_query_parameters_and_malformed_json(calls):
    with TestClient(app) as client:
        query = client.post(PATH, json=VALID_INPUT, headers=auth(), params={"user_id": "participant-1"})
        malformed = client.post(
            PATH, content='{"message":"incomplete', headers={**auth(), "Content-Type": "application/json"}
        )
    for reply in (query, malformed):
        assert reply.status_code == 422
        assert reply.json() == {"detail": "invalid_request"}
    assert not calls


@pytest.mark.parametrize("headers", [
    {},
    auth("synthetic-unknown-token"),
    auth("participant-1"),
    {"Authorization": "Basic synthetic-mina-session"},
    {"X-User-ID": "participant-1"},
])
def test_authentication_failure_precedes_quota_and_generation(configure, headers):
    def must_not_run(*args, **kwargs):
        pytest.fail("Unauthenticated request reached quota or provider.")

    class UnusedQuota:
        reserve = must_not_run

    configure(must_not_run, quota=UnusedQuota())
    reply = TestClient(app).post(PATH, json=VALID_INPUT, headers=headers)
    assert reply.status_code == 401
    assert reply.json() == {"detail": "authentication_required"}
    assert reply.headers["www-authenticate"] == "Bearer"


def test_tokens_for_same_identity_share_quota_and_rejections_do_not_charge_global(configure):
    calls = []
    configure(lambda **selection: calls.append(selection) or "気楽に進もう。", per_user=1, total=2)
    with TestClient(app) as client:
        first, renewed, second, third = [
            client.post(PATH, json=VALID_INPUT, headers=auth(token)) for token in TOKENS
        ]
    assert first.status_code == second.status_code == 200
    assert renewed.status_code == third.status_code == 429
    assert renewed.json() == {"detail": "user_quota_exceeded"}
    assert third.json() == {"detail": "global_quota_exceeded"}
    assert len(calls) == 2


@pytest.mark.parametrize("same_identity", [True, False])
def test_quota_is_reserved_while_another_request_is_generating(configure, same_identity):
    concurrent = Barrier(4)
    provider_entered = Event()
    release_provider = Event()

    def generate(**selection):
        provider_entered.set()
        assert release_provider.wait(timeout=10)
        return "気楽に進もう。"

    configure(generate, per_user=1 if same_identity else 10, total=10 if same_identity else 1)
    tokens = ["synthetic-mina-session"] * 3 if same_identity else [
        "synthetic-mina-session", "synthetic-sora-session", "synthetic-rei-session"
    ]

    def request(token):
        concurrent.wait(timeout=10)
        return client.post(PATH, json=VALID_INPUT, headers=auth(token))

    with TestClient(app) as client, ThreadPoolExecutor(max_workers=3) as pool:
        futures = [pool.submit(request, token) for token in tokens]
        try:
            concurrent.wait(timeout=10)
            assert provider_entered.wait(timeout=10)
            # The second and third requests must be rejected while the admitted call is blocked.
            results = as_completed(futures, timeout=10)
            for _ in range(2):
                rejected = next(results).result()
                assert rejected.status_code == 429
                expected = "user_quota_exceeded" if same_identity else "global_quota_exceeded"
                assert rejected.json() == {"detail": expected}
        finally:
            release_provider.set()
        assert sorted(f.result(timeout=10).status_code for f in futures) == [200, 429, 429]


@pytest.mark.parametrize("result", [None, " ", "長" * 241, {"message": "unexpected"}])
def test_invalid_upstream_reply_is_sanitized(configure, result):
    configure(lambda **selection: result)
    reply = TestClient(app).post(PATH, json=VALID_INPUT, headers=auth())
    assert reply.status_code == 502
    assert reply.json() == {"detail": "upstream_failure"}


def test_upstream_failure_consumes_both_budgets(configure, caplog):
    calls = []

    def generate(**selection):
        calls.append(selection)
        raise RuntimeError("synthetic upstream payload and credential")

    configure(generate, per_user=1, total=1)
    with TestClient(app) as client:
        failure = client.post(PATH, json=VALID_INPUT, headers=auth())
        user_limit = client.post(PATH, json=VALID_INPUT, headers=auth())
        global_limit = client.post(PATH, json=VALID_INPUT, headers=auth("synthetic-sora-session"))
    assert failure.status_code == 502
    assert failure.json() == {"detail": "upstream_failure"}
    assert user_limit.status_code == global_limit.status_code == 429
    assert user_limit.json() == {"detail": "user_quota_exceeded"}
    assert global_limit.json() == {"detail": "global_quota_exceeded"}
    assert calls == [VALID_INPUT]
    assert "synthetic upstream payload" not in caplog.text


@pytest.mark.parametrize("failed_component", ["authentication", "quota"])
def test_backend_dependency_errors_fail_closed(configure, failed_component):
    def fail(*args):
        raise RuntimeError("synthetic private dependency response")

    def must_not_generate(**selection):
        pytest.fail("Unavailable authentication or quota store allowed generation.")

    class UnavailableQuota:
        reserve = fail

    configure(
        must_not_generate,
        authenticate=fail if failed_component == "authentication" else None,
        quota=UnavailableQuota() if failed_component == "quota" else None,
    )
    reply = TestClient(app).post(PATH, json=VALID_INPUT, headers=auth())
    assert reply.status_code == 503
    assert reply.json() == {"detail": "advice_unavailable"}
