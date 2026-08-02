"""Mock-safe RT-6f API coverage for explicit local motion presentation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import importlib
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from app.api import character_motion_presentation
from app.config import AppConfig
import app.services.framework_mock_motion_session_adapter as adapter_module


class _MotionIntent(str, Enum):
    EXPRESSION = "expression"
    SPEAKING_STATE = "speaking_state"
    IDLE_MOTION = "idle_motion"
    STOP_MOTION = "stop_motion"
    RESET_EXPRESSION = "reset_expression"


@dataclass
class _MotionRequest:
    intent: _MotionIntent
    expression: str | None = None
    speaking: bool | None = None
    character_id: str | None = None
    public_metadata: dict[str, Any] | None = None

    @classmethod
    def expression_change(cls, expression: str, **kwargs: Any) -> "_MotionRequest":
        return cls(intent=_MotionIntent.EXPRESSION, expression=expression, **kwargs)

    @classmethod
    def speaking_state(cls, speaking: bool, **kwargs: Any) -> "_MotionRequest":
        return cls(intent=_MotionIntent.SPEAKING_STATE, speaking=speaking, **kwargs)

    @classmethod
    def stop_motion(cls, **kwargs: Any) -> "_MotionRequest":
        return cls(intent=_MotionIntent.STOP_MOTION, **kwargs)


@dataclass
class _Capability:
    adapter_status: str = "mock_available"
    supports_motion_session: bool = True
    supports_mock_motion: bool = True
    supports_real_adapter: bool = False


@dataclass
class _Result:
    outcome: str = "completed"
    state: str = "idle"
    adapter_status: str = "mock_available"
    public_error_code: str = "none"
    retryable: bool = False


class _Session:
    def __init__(self) -> None:
        self.observers: list[Any] = []
        self.requests: list[_MotionRequest] = []
        self.close_calls = 0

    def on_event(self, callback: Any) -> None:
        self.observers.append(callback)

    def _emit(self, event_type: str) -> None:
        for callback in self.observers:
            callback({"type": event_type, "private": "must-not-escape"})

    def preflight(self) -> _Capability:
        self._emit("motion.adapter.preflight.completed")
        return _Capability()

    def apply_motion(self, request: _MotionRequest) -> _Result:
        self.requests.append(request)
        self._emit("motion.requested")
        self._emit("motion.completed")
        return _Result(state="speaking" if request.speaking else "idle")

    def close(self) -> None:
        self.close_calls += 1
        self._emit("motion.session.closed")


class _FrameworkModule:
    MotionIntent = _MotionIntent
    MotionRequest = _MotionRequest

    def __init__(self) -> None:
        self.create_calls: list[dict[str, Any]] = []
        self.sessions: list[_Session] = []

    def create_motion_session(self, **kwargs: Any) -> _Session:
        self.create_calls.append(kwargs)
        session = _Session()
        self.sessions.append(session)
        return session


def _client(monkeypatch: pytest.MonkeyPatch, config: AppConfig) -> TestClient:
    monkeypatch.setattr(character_motion_presentation, "load_config", lambda: config)
    app = FastAPI()
    app.include_router(character_motion_presentation.router)
    return TestClient(app)


def _payload(*, fact: str = "speaking") -> dict[str, Any]:
    return {
        "schema_version": "drc.v3.character-motion-presentation-request.1",
        "source_fact": fact,
        "source_event_type": "home_screen_manual_motion",
        "source_session_id": None,
        "source_turn_id": None,
        "character_id": "gentle_mina",
    }


def test_default_off_returns_typed_disabled_without_framework_import(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    imports: list[str] = []

    def fail_import(name: str, package: str | None = None) -> Any:
        imports.append(name)
        raise AssertionError("default-off request must not import Framework")

    monkeypatch.setattr(importlib, "import_module", fail_import)
    with _client(monkeypatch, AppConfig()) as client:
        response = client.post("/demo/character-motion/presentation", json=_payload())

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "disabled"
    assert body["source_fact"] == "speaking"
    assert body["source_event_type"] == "home_screen_manual_motion"
    assert body["source_session_id"] is None
    assert body["source_turn_id"] is None
    assert body["framework_import_attempted"] is False
    assert body["session_created"] is False
    assert body["provider_execution_attempted"] is False
    assert body["network_execution"] is False
    assert imports == []


def test_enabled_missing_root_returns_typed_unavailable_without_import(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    imports: list[str] = []
    monkeypatch.setattr(
        adapter_module.importlib,
        "import_module",
        lambda name, package=None: imports.append(name),
    )
    config = AppConfig(framework_mock_motion_presentation_enabled=True)
    with _client(monkeypatch, config) as client:
        response = client.post("/demo/character-motion/presentation", json=_payload())

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "unavailable"
    assert body["reason_code"] == "framework_root_missing"
    assert body["framework_import_attempted"] is False
    assert imports == []


@pytest.mark.parametrize("fact", ["motion_active", "unknown"])
def test_ignored_fact_stops_before_framework_import(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    fact: str,
) -> None:
    framework_root = tmp_path / "framework-root"
    framework_root.mkdir()
    imports: list[str] = []
    monkeypatch.setattr(
        adapter_module.importlib,
        "import_module",
        lambda name, package=None: imports.append(name),
    )
    config = AppConfig(
        framework_project_root=str(framework_root),
        framework_mock_motion_presentation_enabled=True,
    )
    with _client(monkeypatch, config) as client:
        response = client.post(
            "/demo/character-motion/presentation",
            json=_payload(fact=fact),
        )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ignored"
    assert body["commands_requested"] == 0
    assert body["framework_import_attempted"] is False
    assert imports == []


def test_enabled_speaking_request_executes_root_public_mock_session(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    framework_root = tmp_path / "framework-root"
    framework_root.mkdir()
    framework = _FrameworkModule()
    imports: list[str] = []

    def fake_import(name: str, package: str | None = None) -> Any:
        imports.append(name)
        if name == "framework":
            return framework
        raise AssertionError(f"unexpected import: {name}")

    monkeypatch.setattr(adapter_module.importlib, "import_module", fake_import)
    config = AppConfig(
        framework_project_root=str(framework_root),
        framework_mock_motion_presentation_enabled=True,
    )
    with _client(monkeypatch, config) as client:
        response = client.post("/demo/character-motion/presentation", json=_payload())

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "completed"
    assert body["cue"] == "speaking"
    assert body["commands_requested"] == 2
    assert body["commands_completed"] == 2
    assert body["framework_import_attempted"] is True
    assert body["session_created"] is True
    assert body["session_closed"] is True
    assert body["adapter"] == "mock"
    assert body["real_adapter_enabled"] is False
    assert body["provider_execution_allowed"] is False
    assert body["provider_execution_attempted"] is False
    assert body["network_execution"] is False
    assert imports == ["framework"]
    assert len(framework.create_calls) == 1
    assert framework.create_calls[0]["adapter"] == "mock"
    assert framework.create_calls[0]["real_adapter_enabled"] is False
    assert framework.create_calls[0]["allow_provider_execution"] is False
    assert framework.sessions[0].close_calls == 1
    assert len(framework.sessions[0].requests) == 2


@pytest.mark.parametrize(
    "changes",
    [
        {"schema_version": "wrong"},
        {"source_event_type": "automatic_lifecycle"},
        {"source_session_id": "session-private"},
        {"source_turn_id": "turn-private"},
        {"private_metadata": {"token": "not-allowed"}},
    ],
)
def test_route_rejects_non_manual_or_extra_request_shapes(
    monkeypatch: pytest.MonkeyPatch,
    changes: dict[str, Any],
) -> None:
    payload = _payload()
    payload.update(changes)
    with _client(monkeypatch, AppConfig()) as client:
        response = client.post("/demo/character-motion/presentation", json=payload)

    assert response.status_code == 422
