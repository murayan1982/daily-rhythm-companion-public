"""Mock-safe RT-7d API and composition tests."""

from fastapi.testclient import TestClient

from app.config import AppConfig
from app.main import app
from app.models.framework_vts_motion import (
    FrameworkVtsMotionExecutionResult,
    FrameworkVtsMotionExecutionStatus,
)
from app.models.framework_vts_motion_presentation import FrameworkVtsMotionPresentationRequest
from app.services.framework_vts_motion_presentation_service import FrameworkVtsMotionPresentationService

client = TestClient(app)


def _payload(intent: str = "expression", value: str | None = "smile") -> dict:
    command = {
        "order": 1,
        "intent": intent,
        "expression": value if intent == "expression" else None,
        "emotion": value if intent == "emotion" else None,
        "gesture": value if intent == "gesture" else None,
        "character_id": "gentle_mina",
    }
    return {
        "schema_version": "drc.v3.framework-vts-motion-presentation-request.1",
        "command": command,
    }


def test_default_api_is_disabled_before_framework_import() -> None:
    response = client.post("/demo/character-motion/vts/presentation", json=_payload())
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "disabled"
    assert data["commands_requested"] == 1
    assert data["framework_import_attempted"] is False
    assert data["provider_execution_attempted"] is False
    assert data["network_execution_attempted"] is False
    assert data["real_motion_executed"] is False


def test_existing_rt6_route_remains_available() -> None:
    response = client.post(
        "/demo/character-motion/presentation",
        json={"source_fact": "idle", "source_event_type": "home_screen_manual_motion", "character_id": "gentle_mina"},
    )
    assert response.status_code == 200
    assert response.json()["adapter"] == "mock"


def test_request_requires_exact_schema() -> None:
    payload = _payload()
    payload["schema_version"] = "private"
    assert client.post("/demo/character-motion/vts/presentation", json=payload).status_code == 422


def test_request_requires_order_one() -> None:
    payload = _payload()
    payload["command"]["order"] = 2
    assert client.post("/demo/character-motion/vts/presentation", json=payload).status_code == 422


def test_request_rejects_unsupported_intent() -> None:
    payload = _payload()
    payload["command"]["intent"] = "speaking_state"
    assert client.post("/demo/character-motion/vts/presentation", json=payload).status_code == 422


def test_reset_expression_has_no_selector_payload() -> None:
    response = client.post(
        "/demo/character-motion/vts/presentation",
        json=_payload("reset_expression", None),
    )
    assert response.status_code == 200
    assert response.json()["status"] == "disabled"


def test_invalid_configuration_stops_before_adapter_factory() -> None:
    request = FrameworkVtsMotionPresentationRequest.model_validate(_payload())
    calls = 0

    def factory(_config):
        nonlocal calls
        calls += 1
        raise AssertionError("adapter factory must not be called")

    result = FrameworkVtsMotionPresentationService(
        AppConfig(framework_vts_motion_configuration_error="invalid_hotkey_bindings"),
        adapter_factory=factory,
    ).submit(request)
    assert calls == 0
    assert result.status is FrameworkVtsMotionExecutionStatus.UNAVAILABLE
    assert result.framework_import_attempted is False
    assert result.reason_code == "framework_vts_configuration_invalid"


def test_service_passes_exactly_one_command_to_injected_adapter() -> None:
    request = FrameworkVtsMotionPresentationRequest.model_validate(_payload("gesture", "wave"))
    captured = []

    class FakeAdapter:
        def execute(self, commands):
            captured.extend(commands)
            return FrameworkVtsMotionExecutionResult(
                status=FrameworkVtsMotionExecutionStatus.DISABLED,
                commands_requested=1,
                commands_applied=0,
                commands_completed=0,
                optional_commands_skipped=0,
                reason_code="framework_vts_motion_disabled",
                safe_message="Framework VTS motion execution is disabled.",
            )

    result = FrameworkVtsMotionPresentationService(
        AppConfig(), adapter_factory=lambda _config: FakeAdapter()
    ).submit(request)
    assert result.status is FrameworkVtsMotionExecutionStatus.DISABLED
    assert len(captured) == 1
    assert captured[0].order == 1
    assert captured[0].intent.value == "gesture"
    assert captured[0].gesture == "wave"


def test_response_does_not_expose_private_values(monkeypatch) -> None:
    private = "private-token-hotkey"
    monkeypatch.setenv("DRC_RT7_VTS_AUTHENTICATION_TOKEN", private)
    monkeypatch.setenv("DRC_RT7_VTS_HOTKEY_BINDINGS_JSON", '{"expression:smile":"%s"}' % private)
    response = client.post("/demo/character-motion/vts/presentation", json=_payload())
    assert response.status_code == 200
    assert private not in response.text
