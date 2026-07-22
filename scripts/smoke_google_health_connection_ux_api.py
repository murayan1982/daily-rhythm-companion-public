from __future__ import annotations

import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from fastapi.testclient import TestClient

from app.main import app


EXPECTED_TOP_LEVEL_KEYS = {
    "provider",
    "state",
    "severity",
    "title",
    "message",
    "next_action",
    "primary_action",
    "secondary_actions",
    "sleep_provider",
    "token_stored",
    "reconnect_recommended",
    "real_api_requested",
    "real_api_allowed",
    "can_start_oauth",
    "can_reset_local_token",
    "can_use_safe_preview",
    "can_use_guarded_real_request",
    "developer_status",
    "error",
}

EXPECTED_ACTION_KEYS = {
    "key",
    "label",
    "description",
    "enabled",
}

# These top-level booleans are intentionally user-facing and safe.
ALLOWED_TOKEN_KEYS = {
    "token_stored",
}

# This endpoint is user-facing. It must not expose developer checklist internals,
# credential material, local paths, raw commands, or raw token values.
FORBIDDEN_EXACT_KEYS = {
    "access_token",
    "refresh_token",
    "id_token",
    "client_secret",
    "token_file",
    "credentials_file",
    "credentials_path",
    "commands",
    "checks",
    "configured_scopes",
    "recommended_sleep_scope",
    "raw",
    "raw_payload",
    "authorization_header",
}

FORBIDDEN_KEY_FRAGMENTS = {
    "secret",
    "credential",
    "path",
    "command",
}

FORBIDDEN_VALUE_FRAGMENTS = {
    "test-access-token",
    "test-refresh-token",
    "bearer ",
    "authorization:",
    "client_secret",
    "credentials.json",
    "google_health_token",
    "\\backend\\",
    "/backend/",
    "scripts\\",
    "scripts/",
    "python ",
    "powershell",
}


def _assert_expected_contract(data: Mapping[str, Any]) -> None:
    missing_keys = sorted(EXPECTED_TOP_LEVEL_KEYS - set(data))
    assert not missing_keys, f"missing response keys: {missing_keys}"

    unexpected_keys = sorted(set(data) - EXPECTED_TOP_LEVEL_KEYS)
    assert not unexpected_keys, f"unexpected response keys: {unexpected_keys}"

    assert data["provider"] == "google_health"
    assert isinstance(data["state"], str)
    assert isinstance(data["severity"], str)
    assert isinstance(data["title"], str)
    assert isinstance(data["message"], str)
    assert isinstance(data["next_action"], str)
    assert isinstance(data["secondary_actions"], list)

    assert isinstance(data["token_stored"], bool)
    assert isinstance(data["reconnect_recommended"], bool)
    assert isinstance(data["real_api_requested"], bool)
    assert isinstance(data["real_api_allowed"], bool)
    assert isinstance(data["can_start_oauth"], bool)
    assert isinstance(data["can_reset_local_token"], bool)
    assert isinstance(data["can_use_safe_preview"], bool)
    assert isinstance(data["can_use_guarded_real_request"], bool)


def _assert_action_contract(action: Mapping[str, Any] | None, *, path: str) -> None:
    if action is None:
        return

    missing_keys = sorted(EXPECTED_ACTION_KEYS - set(action))
    assert not missing_keys, f"{path}: missing action keys: {missing_keys}"

    unexpected_keys = sorted(set(action) - EXPECTED_ACTION_KEYS)
    assert not unexpected_keys, f"{path}: unexpected action keys: {unexpected_keys}"

    assert isinstance(action["key"], str), f"{path}.key must be str"
    assert isinstance(action["label"], str), f"{path}.label must be str"
    assert isinstance(action["description"], str), f"{path}.description must be str"
    assert isinstance(action["enabled"], bool), f"{path}.enabled must be bool"


def _assert_no_sensitive_shape(value: Any, *, path: str = "$") -> None:
    if isinstance(value, Mapping):
        for raw_key, child in value.items():
            key = str(raw_key)
            key_lower = key.lower()

            if key not in ALLOWED_TOKEN_KEYS:
                assert key_lower not in FORBIDDEN_EXACT_KEYS, (
                    f"forbidden key leaked at {path}.{key}: {key}"
                )
                assert not any(fragment in key_lower for fragment in FORBIDDEN_KEY_FRAGMENTS), (
                    f"forbidden key fragment leaked at {path}.{key}: {key}"
                )

            _assert_no_sensitive_shape(child, path=f"{path}.{key}")
        return

    if isinstance(value, str):
        value_lower = value.lower()
        assert not any(fragment in value_lower for fragment in FORBIDDEN_VALUE_FRAGMENTS), (
            f"forbidden value fragment leaked at {path}: {value}"
        )
        return

    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            _assert_no_sensitive_shape(child, path=f"{path}[{index}]")


def main() -> None:
    client = TestClient(app)

    response = client.get("/google-health/connection-ux")
    assert response.status_code == 200, response.text

    data = response.json()

    _assert_expected_contract(data)
    _assert_action_contract(data["primary_action"], path="$.primary_action")

    for index, action in enumerate(data["secondary_actions"]):
        assert isinstance(action, dict), f"secondary action must be object: index={index}"
        _assert_action_contract(action, path=f"$.secondary_actions[{index}]")

    _assert_no_sensitive_shape(data)

    # mock-safe profile should keep the endpoint descriptive and safe.
    assert data["sleep_provider"] == "mock"
    assert data["state"] == "mock_mode"
    assert data["real_api_requested"] is False
    assert data["real_api_allowed"] is False
    assert data["can_use_guarded_real_request"] is False

    print("[google-health-connection-ux-api-smoke-v0.29.0] OK")


if __name__ == "__main__":
    main()
