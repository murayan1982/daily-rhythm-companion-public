from fastapi.testclient import TestClient
import pytest

from app.main import app as normal_app
from app.public_main import app
from scripts.public_advice_invite import create_local_app


def registered_operations(routes):
    for route in routes:
        # Recent FastAPI versions keep included routers nested until dispatch.
        included_router = getattr(route, "original_router", None)
        if included_router is not None:
            yield from registered_operations(included_router.routes)
        else:
            yield (route.path, sorted(route.methods))


@pytest.mark.parametrize("fixed_response", [False, True])
def test_public_app_exposes_only_advice_and_health(monkeypatch, fixed_response):
    monkeypatch.delenv("DRC_PUBLIC_ADVICE_GEMINI_ENABLED", raising=False)
    monkeypatch.delenv("DRC_PUBLIC_ADVICE_POSTGRES_DSN", raising=False)
    candidate = create_local_app() if fixed_response else app
    with TestClient(candidate, follow_redirects=False) as client:
        assert sorted(registered_operations(candidate.routes)) == [
            ("/health", ["GET"]),
            ("/v1/advice", ["POST"]),
        ]

        response = client.get("/health")
        assert (response.status_code, response.json()) == (200, {"status": "ok"})
        response = client.post(
            "/v1/advice", json={"mood": "normal", "character_id": "gentle_mina"}
        )
        assert (response.status_code, response.json()) == (503, {"detail": "advice_unavailable"})

        methods = {"GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "TRACE"}
        for path, allowed_method in (("/health", "GET"), ("/v1/advice", "POST")):
            for method in methods - {allowed_method}:
                response = client.request(method, path)
                assert response.status_code == 405, (method, path)
                assert response.headers["allow"] == allowed_method
            assert client.request(allowed_method, path + "/").status_code == 404

        # Every operation unique to the usual app must be absent, even if its handler is disabled there.
        for path, operations in normal_app.openapi()["paths"].items():
            if path not in {"/health", "/v1/advice"}:
                concrete_path = path.replace("{", "test-").replace("}", "")
                for method in operations:
                    assert client.request(method.upper(), concrete_path).status_code == 404, path

        for path in ("/docs", "/redoc", "/openapi.json", "/docs/oauth2-redirect"):
            assert client.get(path).status_code == 404
            assert client.head(path).status_code == 404
