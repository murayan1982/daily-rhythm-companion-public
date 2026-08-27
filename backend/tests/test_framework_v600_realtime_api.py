from __future__ import annotations

from collections.abc import Callable

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api import framework_v600_realtime
from app.models.framework_v600_realtime import (
    FrameworkV600AdapterStatus,
    FrameworkV600CapabilitySnapshot,
    FrameworkV600DiagnosticsSnapshot,
    FrameworkV600InterruptResult,
    FrameworkV600OpenResult,
    FrameworkV600RecoveryAction,
    FrameworkV600TurnOutcome,
    FrameworkV600TurnResult,
)
from app.models.framework_v600_realtime_api import (
    VALID_INTERRUPT_REASONS,
    VALID_INTERRUPT_SCOPES,
    FrameworkV600RealtimeInterruptRequest,
    FrameworkV600RealtimeTurnRequest,
)
from app.services.framework_v600_realtime_api_registry import (
    FrameworkV600RealtimeApiRegistry,
    MAX_SESSIONS,
)

SESSION_PREFIX = "/realtime/framework-v6/provider-free/sessions"
SESSION_ID_TEMPLATE = "fw_session_0123456789abcdef0123456789abcde{suffix}"
TURN_ID = "fw_turn_0123456789abcdef0123456789abcdef"
GENERATION_ID = "fw_generation_0123456789abcdef0123456789abcdef"


class FakeAdapter:
    def __init__(
        self,
        *,
        session_id: str,
        open_result: FrameworkV600OpenResult | None = None,
        turn_result: FrameworkV600TurnResult | None = None,
        diagnostics: FrameworkV600DiagnosticsSnapshot | None = None,
        fail_open: bool = False,
        fail_turn: bool = False,
        fail_interrupt: bool = False,
        fail_diagnostics: bool = False,
    ) -> None:
        self.session_id = session_id
        self.open_result = open_result
        self.turn_result = turn_result
        self.diagnostics = diagnostics
        self.fail_open = fail_open
        self.fail_turn = fail_turn
        self.fail_interrupt = fail_interrupt
        self.fail_diagnostics = fail_diagnostics
        self.open_count = 0
        self.close_count = 0
        self.turn_inputs: list[str] = []
        self.interrupt_requests: list[tuple[str, str]] = []
        self.provider_execution_attempted = False
        self.real_runtime_construction_knob = None

    def open(self) -> FrameworkV600OpenResult:
        self.open_count += 1
        if self.fail_open:
            raise RuntimeError("PRIVATE_PROVIDER_EXCEPTION_SENTINEL")
        return self.open_result or FrameworkV600OpenResult(
            status=FrameworkV600AdapterStatus.OPEN,
            available=True,
            session_id=self.session_id,
            real_runtime_requested=False,
            real_runtime_enabled=False,
            runtime_executable=True,
            capabilities=_capabilities(self.session_id),
        )

    async def run_turn(self, *, input_text: str) -> FrameworkV600TurnResult:
        self.turn_inputs.append(input_text)
        if self.fail_turn:
            raise RuntimeError("secret provider payload leaked")
        return self.turn_result or FrameworkV600TurnResult(
            outcome=FrameworkV600TurnOutcome.COMPLETED,
            terminal=True,
            session_id=self.session_id,
            turn_id=TURN_ID,
            generation_id=GENERATION_ID,
            capabilities=_capabilities(self.session_id),
            diagnostics=_diagnostics(self.session_id),
        )

    def interrupt(self, *, scope: str, reason: str) -> FrameworkV600InterruptResult:
        self.interrupt_requests.append((scope, reason))
        if self.fail_interrupt:
            raise RuntimeError("interrupt secret")
        return FrameworkV600InterruptResult(
            outcome="no_active_turn",
            scope=scope,
            reason=reason,
            safe_message="Cooperative interrupt observed.",
        )

    def diagnostics_snapshot(self) -> FrameworkV600DiagnosticsSnapshot | None:
        if self.fail_diagnostics:
            raise RuntimeError("PRIVATE_PATH_SENTINEL")
        return self.diagnostics or _diagnostics(self.session_id)

    def close(self) -> FrameworkV600OpenResult:
        self.close_count += 1
        return FrameworkV600OpenResult(
            status=FrameworkV600AdapterStatus.CLOSED,
            available=False,
            safe_message="closed",
        )


class FakeFactory:
    def __init__(self, builder: Callable[[int], FakeAdapter] | None = None) -> None:
        self.builder = builder or (lambda index: FakeAdapter(session_id=_session_id(index)))
        self.adapters: list[FakeAdapter] = []

    def __call__(self) -> FakeAdapter:
        adapter = self.builder(len(self.adapters))
        self.adapters.append(adapter)
        return adapter


def _client(factory: FakeFactory | None = None) -> TestClient:
    registry = FrameworkV600RealtimeApiRegistry(adapter_factory=factory or FakeFactory())
    test_app = FastAPI()
    test_app.include_router(framework_v600_realtime.router)
    test_app.dependency_overrides[
        framework_v600_realtime.get_framework_v600_realtime_registry
    ] = lambda: registry
    return TestClient(test_app)


def _session_id(index: int = 0) -> str:
    return SESSION_ID_TEMPLATE.format(suffix=hex(index)[2:])


def _capabilities(session_id: str) -> FrameworkV600CapabilitySnapshot:
    return FrameworkV600CapabilitySnapshot(
        session_id=session_id,
        supports_text_chat=True,
        supports_voice_input=True,
        supports_voice_output=True,
        supports_motion=False,
        real_runtime_enabled=False,
        real_unified_runtime_available=False,
        unified_real_pipeline_claimed=False,
    )


def _diagnostics(session_id: str) -> FrameworkV600DiagnosticsSnapshot:
    return FrameworkV600DiagnosticsSnapshot(
        session_id=session_id,
        state="idle",
        phase="ready",
        is_closed=False,
        queue_depth=0,
        active_generation_count=0,
    )


def _create(client: TestClient) -> dict[str, object]:
    response = client.post(SESSION_PREFIX)
    assert response.status_code == 201
    return response.json()


def _assert_safe_validation_problem(response_text: str) -> None:
    assert '"code":"request_validation_failed"' in response_text
    assert '"message":"Request validation failed."' in response_text
    assert '"retryable":false' in response_text


def test_create_returns_201() -> None:
    with _client() as client:
        response = client.post(SESSION_PREFIX)

    assert response.status_code == 201


def test_create_preserves_canonical_fw_session_id() -> None:
    with _client() as client:
        payload = _create(client)

    assert payload["session_id"] == _session_id()


def test_create_does_not_generate_separate_drc_session_id() -> None:
    with _client() as client:
        payload = _create(client)

    assert "drc_session_id" not in payload


def test_create_reports_provider_free_runtime_truth() -> None:
    with _client() as client:
        payload = _create(client)

    assert payload["real_runtime_requested"] is False
    assert payload["real_runtime_enabled"] is False
    assert payload["capabilities"]["unified_real_pipeline_claimed"] is False


def test_capacity_accepts_eight_sessions() -> None:
    with _client() as client:
        responses = [client.post(SESSION_PREFIX) for _ in range(MAX_SESSIONS)]

    assert [response.status_code for response in responses] == [201] * MAX_SESSIONS


def test_ninth_session_returns_429() -> None:
    with _client() as client:
        for _ in range(MAX_SESSIONS):
            assert client.post(SESSION_PREFIX).status_code == 201
        response = client.post(SESSION_PREFIX)

    assert response.status_code == 429


def test_capacity_error_uses_public_code() -> None:
    with _client() as client:
        for _ in range(MAX_SESSIONS):
            client.post(SESSION_PREFIX)
        response = client.post(SESSION_PREFIX)

    assert response.json()["detail"]["code"] == "session_capacity_reached"


def test_async_turn_forwards_exact_input_text() -> None:
    factory = FakeFactory()
    with _client(factory) as client:
        payload = _create(client)
        response = client.post(f"{SESSION_PREFIX}/{payload['session_id']}/turns", json={"input_text": "hello"})

    assert response.status_code == 200
    assert factory.adapters[0].turn_inputs == ["hello"]


def test_turn_rejects_empty_input_text() -> None:
    with _client() as client:
        payload = _create(client)
        response = client.post(f"{SESSION_PREFIX}/{payload['session_id']}/turns", json={"input_text": ""})

    assert response.status_code == 422


def test_turn_rejects_blank_input_text() -> None:
    with _client() as client:
        payload = _create(client)
        response = client.post(f"{SESSION_PREFIX}/{payload['session_id']}/turns", json={"input_text": "   "})

    assert response.status_code == 422


def test_turn_rejects_over_4096_input_text() -> None:
    with _client() as client:
        payload = _create(client)
        response = client.post(f"{SESSION_PREFIX}/{payload['session_id']}/turns", json={"input_text": "x" * 4097})

    assert response.status_code == 422


def test_overlong_input_text_validation_response_is_public_safe() -> None:
    rejected_input = "NEUTRAL_OVERLONG_SENTINEL" + ("x" * 4097)
    with _client() as client:
        payload = _create(client)
        response = client.post(f"{SESSION_PREFIX}/{payload['session_id']}/turns", json={"input_text": rejected_input})

    assert response.status_code == 422
    _assert_safe_validation_problem(response.text)
    assert "NEUTRAL_OVERLONG_SENTINEL" not in response.text


def test_turn_request_rejects_unexpected_extra_field() -> None:
    with _client() as client:
        payload = _create(client)
        response = client.post(
            f"{SESSION_PREFIX}/{payload['session_id']}/turns",
            json={"input_text": "hello", "extra_marker": "neutral"},
        )

    assert response.status_code == 422


def test_turn_extra_field_validation_response_is_public_safe() -> None:
    rejected_extra_value = "NEUTRAL_TURN_EXTRA_SENTINEL"
    with _client() as client:
        payload = _create(client)
        response = client.post(
            f"{SESSION_PREFIX}/{payload['session_id']}/turns",
            json={"input_text": "hello", "extra_marker": rejected_extra_value},
        )

    assert response.status_code == 422
    _assert_safe_validation_problem(response.text)
    assert rejected_extra_value not in response.text


def test_typed_failed_turn_remains_200() -> None:
    failed_turn = FrameworkV600TurnResult(
        outcome=FrameworkV600TurnOutcome.FAILED,
        terminal=True,
        public_error_code="framework_turn_failed",
        safe_message="FW v6 provider-free turn failed safely.",
        recovery_action=FrameworkV600RecoveryAction.RETRY,
    )
    factory = FakeFactory(lambda index: FakeAdapter(session_id=_session_id(index), turn_result=failed_turn))
    with _client(factory) as client:
        payload = _create(client)
        response = client.post(f"{SESSION_PREFIX}/{payload['session_id']}/turns", json={"input_text": "hello"})

    assert response.status_code == 200
    assert response.json()["outcome"] == "failed"


def test_interrupt_uses_default_scope() -> None:
    factory = FakeFactory()
    with _client(factory) as client:
        payload = _create(client)
        response = client.post(f"{SESSION_PREFIX}/{payload['session_id']}/interrupt", json={})

    assert response.status_code == 200
    assert factory.adapters[0].interrupt_requests == [("current_turn", "host_app_request")]


def test_interrupt_uses_default_reason() -> None:
    with _client() as client:
        payload = _create(client)
        response = client.post(f"{SESSION_PREFIX}/{payload['session_id']}/interrupt", json={"scope": "all"})

    assert response.status_code == 200
    assert response.json()["reason"] == "host_app_request"


def test_all_approved_interrupt_scopes_are_accepted() -> None:
    for scope in VALID_INTERRUPT_SCOPES:
        with _client() as client:
            payload = _create(client)
            response = client.post(
                f"{SESSION_PREFIX}/{payload['session_id']}/interrupt",
                json={"scope": scope, "reason": "host_app_request"},
            )
        assert response.status_code == 200
        assert response.json()["scope"] == scope


def test_all_approved_interrupt_reasons_are_accepted() -> None:
    for reason in VALID_INTERRUPT_REASONS:
        with _client() as client:
            payload = _create(client)
            response = client.post(
                f"{SESSION_PREFIX}/{payload['session_id']}/interrupt",
                json={"scope": "current_turn", "reason": reason},
            )
        assert response.status_code == 200
        assert response.json()["reason"] == reason


def test_invalid_interrupt_scope_is_422() -> None:
    with _client() as client:
        payload = _create(client)
        response = client.post(
            f"{SESSION_PREFIX}/{payload['session_id']}/interrupt",
            json={"scope": "turn", "reason": "host_app_request"},
        )

    assert response.status_code == 422


def test_invalid_interrupt_reason_is_422() -> None:
    with _client() as client:
        payload = _create(client)
        response = client.post(
            f"{SESSION_PREFIX}/{payload['session_id']}/interrupt",
            json={"scope": "current_turn", "reason": "operator_requested"},
        )

    assert response.status_code == 422


def test_invalid_interrupt_validation_response_is_public_safe() -> None:
    rejected_scope = "NEUTRAL_INTERRUPT_SCOPE_SENTINEL"
    with _client() as client:
        payload = _create(client)
        response = client.post(
            f"{SESSION_PREFIX}/{payload['session_id']}/interrupt",
            json={"scope": rejected_scope, "reason": "host_app_request"},
        )

    assert response.status_code == 422
    _assert_safe_validation_problem(response.text)
    assert rejected_scope not in response.text


def test_interrupt_request_rejects_unexpected_extra_field() -> None:
    with _client() as client:
        payload = _create(client)
        response = client.post(
            f"{SESSION_PREFIX}/{payload['session_id']}/interrupt",
            json={"scope": "current_turn", "reason": "host_app_request", "extra_marker": "neutral"},
        )

    assert response.status_code == 422


def test_diagnostics_are_bounded() -> None:
    with _client() as client:
        payload = _create(client)
        response = client.get(f"{SESSION_PREFIX}/{payload['session_id']}/diagnostics")

    assert response.status_code == 200
    assert set(response.json()) == set(FrameworkV600DiagnosticsSnapshot(session_id=_session_id()).model_dump())


def test_unknown_turn_session_returns_404() -> None:
    with _client() as client:
        response = client.post(f"{SESSION_PREFIX}/{_session_id(9)}/turns", json={"input_text": "hello"})

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "session_not_found"


def test_unknown_interrupt_session_returns_404() -> None:
    with _client() as client:
        response = client.post(f"{SESSION_PREFIX}/{_session_id(9)}/interrupt", json={})

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "session_not_found"


def test_unknown_diagnostics_session_returns_404() -> None:
    with _client() as client:
        response = client.get(f"{SESSION_PREFIX}/{_session_id(9)}/diagnostics")

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "session_not_found"


def test_close_returns_204() -> None:
    with _client() as client:
        payload = _create(client)
        response = client.delete(f"{SESSION_PREFIX}/{payload['session_id']}")

    assert response.status_code == 204
    assert response.content == b""


def test_duplicate_close_returns_204() -> None:
    with _client() as client:
        payload = _create(client)
        first = client.delete(f"{SESSION_PREFIX}/{payload['session_id']}")
        second = client.delete(f"{SESSION_PREFIX}/{payload['session_id']}")

    assert first.status_code == 204
    assert second.status_code == 204


def test_old_session_is_unusable_after_close() -> None:
    with _client() as client:
        payload = _create(client)
        client.delete(f"{SESSION_PREFIX}/{payload['session_id']}")
        response = client.post(f"{SESSION_PREFIX}/{payload['session_id']}/turns", json={"input_text": "hello"})

    assert response.status_code == 404


def test_unavailable_open_returns_503() -> None:
    unavailable = FrameworkV600OpenResult(
        status=FrameworkV600AdapterStatus.UNAVAILABLE,
        available=False,
        public_error_code="framework_realtime_unavailable",
        safe_message="FW v6 RealtimeSession is unavailable.",
        retryable=True,
    )
    factory = FakeFactory(lambda index: FakeAdapter(session_id=_session_id(index), open_result=unavailable))
    with _client(factory) as client:
        response = client.post(SESSION_PREFIX)

    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "framework_realtime_unavailable"


def test_version_mismatch_style_unavailable_is_safe_503() -> None:
    unavailable = FrameworkV600OpenResult(
        status=FrameworkV600AdapterStatus.UNAVAILABLE,
        available=False,
        public_error_code="framework_distribution_version_mismatch",
        safe_message="Installed FW version does not match the required v6.0.0 contract.",
        retryable=True,
    )
    factory = FakeFactory(lambda index: FakeAdapter(session_id=_session_id(index), open_result=unavailable))
    with _client(factory) as client:
        response = client.post(SESSION_PREFIX)

    assert response.status_code == 503
    assert "v6.0.0" in response.json()["detail"]["message"]


def test_raw_exception_strings_do_not_leak() -> None:
    factory = FakeFactory(lambda index: FakeAdapter(session_id=_session_id(index), fail_open=True))
    with _client(factory) as client:
        response = client.post(SESSION_PREFIX)

    body = response.text
    assert response.status_code == 503
    assert "PRIVATE_PROVIDER_EXCEPTION_SENTINEL" not in body


def test_filesystem_paths_do_not_leak() -> None:
    factory = FakeFactory(lambda index: FakeAdapter(session_id=_session_id(index), fail_diagnostics=True))
    with _client(factory) as client:
        payload = _create(client)
        response = client.get(f"{SESSION_PREFIX}/{payload['session_id']}/diagnostics")

    assert response.status_code == 503
    assert "PRIVATE_PATH_SENTINEL" not in response.text


def test_input_text_does_not_leak_in_safe_error() -> None:
    secret_input = "do not echo this input"
    factory = FakeFactory(lambda index: FakeAdapter(session_id=_session_id(index), fail_turn=True))
    with _client(factory) as client:
        payload = _create(client)
        response = client.post(f"{SESSION_PREFIX}/{payload['session_id']}/turns", json={"input_text": secret_input})

    assert response.status_code == 503
    assert secret_input not in response.text


def test_provider_execution_false() -> None:
    factory = FakeFactory()
    with _client(factory) as client:
        _create(client)

    assert factory.adapters[0].provider_execution_attempted is False


def test_no_real_runtime_construction_knob_supplied() -> None:
    factory = FakeFactory()
    with _client(factory) as client:
        _create(client)

    assert factory.adapters[0].real_runtime_construction_knob is None


def test_v4_2_response_model_types_are_reused() -> None:
    route_models = {
        route.path: getattr(route, "response_model", None)
        for route in framework_v600_realtime.router.routes
    }

    assert route_models[f"{SESSION_PREFIX}"] is FrameworkV600OpenResult
    assert route_models[f"{SESSION_PREFIX}/{{session_id}}/turns"] is FrameworkV600TurnResult


def test_v4_3_request_models_are_api_specific() -> None:
    assert FrameworkV600RealtimeTurnRequest(input_text="hello").input_text == "hello"
    assert FrameworkV600RealtimeInterruptRequest().scope == "current_turn"
