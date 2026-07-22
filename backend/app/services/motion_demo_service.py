from __future__ import annotations

from app.config import AppConfig
from app.models.demo_status import CapabilityStatus
from app.models.motion_demo import (
    MotionBoundaryProbeSummary,
    MotionDemoRequest,
    MotionDemoRequestResponse,
    MotionDemoStatusResponse,
)
from app.services.motion_boundary_probe import MotionBoundaryProbe


class MotionDemoService:
    """Build conservative status for the Live2D / VTS motion demo boundary.

    The v0.36.0 boundary is intentionally safe-first. It does not import
    framework motion modules, open a VTube Studio WebSocket connection, load
    Live2D runtime dependencies, or send real motion/expression commands.
    """

    _SUPPORTED_MOTION_EVENTS: tuple[str, ...] = (
        "greeting",
        "thinking",
        "happy",
        "tired_supportive",
        "speaking",
        "idle",
    )
    _SUPPORTED_CHARACTER_IDS: tuple[str, ...] = (
        "gentle_mina",
        "cheerful_sora",
        "cool_rei",
    )
    _SUPPORTED_EXPRESSION_IDS: tuple[str, ...] = (
        "idle",
        "happy",
        "thinking",
        "supportive",
        "speaking",
    )
    _SUPPORTED_REQUESTED_ADAPTER_MODES: tuple[str, ...] = (
        "disabled",
        "framework",
        "vts",
        "simulator",
    )

    def __init__(self, config: AppConfig) -> None:
        self._config = config

    def build_status(self) -> MotionDemoStatusResponse:
        """Return a standalone motion demo status response."""

        engine = self._normalized_engine()
        probe = self._build_framework_probe()
        return MotionDemoStatusResponse(
            engine=engine,
            mode=self._resolve_mode(engine),
            adapter_mode=self._normalized_motion_adapter_mode(),
            capability=self.build_capability_status(engine, probe),
            supported_motion_events=list(self._SUPPORTED_MOTION_EVENTS),
            supported_character_ids=list(self._SUPPORTED_CHARACTER_IDS),
            supported_expression_ids=list(self._SUPPORTED_EXPRESSION_IDS),
            framework_probe=probe,
        )

    def submit_request(self, request: MotionDemoRequest) -> MotionDemoRequestResponse:
        """Return a safe response for a motion demo request.

        v0.36 Day3 normalizes and echoes the future motion request metadata;
        it still never sends a motion event.
        """

        status = self.build_status()
        raw_motion_event = request.motion_event
        motion_event = self._normalized_request_value(raw_motion_event) or "idle"
        character_id = self._normalized_request_value(request.character_id)
        expression_id = self._normalized_request_value(request.expression_id)
        trigger_source = self._normalized_request_value(request.trigger_source) or "manual"
        requested_adapter_mode = self._normalized_adapter_request(request.requested_adapter_mode)

        return MotionDemoRequestResponse(
            accepted=False,
            request_state="not_started",
            engine=status.engine,
            mode=status.mode,
            adapter_mode=status.adapter_mode,
            motion_event=motion_event,
            client_event_id=self._normalized_request_value(request.client_event_id),
            character_id=character_id,
            expression_id=expression_id,
            trigger_source=trigger_source,
            requested_adapter_mode=requested_adapter_mode,
            resolved_adapter_mode=status.adapter_mode,
            motion_sent=False,
            vts_connection_used=False,
            request_warnings=self._build_request_warnings(
                raw_motion_event=raw_motion_event,
                motion_event=motion_event,
                character_id=character_id,
                expression_id=expression_id,
                requested_adapter_mode=requested_adapter_mode,
            ),
            message=self._build_request_not_started_message(status.capability),
            capability=status.capability,
            supported_motion_events=status.supported_motion_events,
            supported_character_ids=status.supported_character_ids,
            supported_expression_ids=status.supported_expression_ids,
            framework_probe=status.framework_probe,
        )

    def build_capability_status(
        self,
        engine: str | None = None,
        probe: MotionBoundaryProbeSummary | None = None,
    ) -> CapabilityStatus:
        """Return the standalone motion demo capability status."""

        engine = engine or self._normalized_engine()
        probe = probe if probe is not None else self._build_framework_probe()

        if not self._config.motion_demo_enabled:
            return CapabilityStatus(
                status="unavailable",
                source="not_configured",
                message=(
                    "Motion demo is disabled. Set MOTION_DEMO_ENABLED=1 "
                    "to test the guarded Live2D/VTS motion demo boundary."
                ),
            )

        if engine == "mock":
            return CapabilityStatus(
                status="unavailable",
                source="mock",
                message="Motion demo requires framework mode; mock mode does not provide Live2D/VTS motion.",
            )

        if engine != "framework":
            return CapabilityStatus(
                status="unavailable",
                source="unsupported_engine",
                message=f"Unsupported conversation engine for motion demo: {engine}",
            )

        adapter_mode = self._normalized_motion_adapter_mode()
        if adapter_mode == "framework":
            if not probe.framework_root:
                return CapabilityStatus(
                    status="unavailable",
                    source="framework_motion_project_root_missing",
                    message=(
                        "Framework motion adapter mode was requested, but "
                        "FRAMEWORK_ROOT / FRAMEWORK_PROJECT_ROOT is not configured."
                    ),
                )

            if not probe.framework_root_exists:
                return CapabilityStatus(
                    status="unavailable",
                    source="framework_motion_project_root_missing",
                    message="Configured framework root for motion demo does not exist.",
                )

            if not probe.candidate_paths:
                return CapabilityStatus(
                    status="unavailable",
                    source="framework_motion_boundary_missing",
                    message=(
                        "Framework motion adapter mode was requested, but no likely "
                        "framework Live2D/VTS motion boundary files were found by the "
                        "no-import probe."
                    ),
                )

            if not probe.public_api_candidates:
                return CapabilityStatus(
                    status="unavailable",
                    source="framework_motion_public_boundary_missing",
                    message=(
                        "Framework motion candidate files were found, but no public "
                        "motion API marker was detected. DRC will not treat this as "
                        "available yet."
                    ),
                )

            return CapabilityStatus(
                status="unavailable",
                source="framework_motion_adapter_not_wired",
                message=(
                    "Framework motion public API-like markers were detected, but DRC "
                    "has not wired a guarded framework motion adapter yet."
                ),
            )

        if adapter_mode == "vts":
            return CapabilityStatus(
                status="unavailable",
                source="vts_motion_adapter_not_wired",
                message=(
                    "VTS motion adapter mode was requested, but DRC has not wired "
                    "VTube Studio / Live2D motion sending yet."
                ),
            )

        return CapabilityStatus(
            status="unavailable",
            source="motion_adapter_unsupported",
            message=f"Unsupported MOTION_DEMO_ADAPTER_MODE: {self._config.motion_adapter_mode}",
        )

    def _build_framework_probe(self) -> MotionBoundaryProbeSummary:
        """Return no-import framework motion probe metadata for status responses."""

        result = MotionBoundaryProbe(self._config.framework_project_root).run()
        return MotionBoundaryProbeSummary(
            framework_root=result.framework_root,
            framework_root_exists=result.framework_root_exists,
            candidate_paths=list(result.candidate_paths),
            public_api_candidates=list(result.public_api_candidates),
            notes=list(result.notes),
        )

    def _build_request_not_started_message(self, capability: CapabilityStatus) -> str:
        """Explain why the guarded request did not send motion."""

        return (
            "Motion demo request was received, but no Live2D/VTS motion was sent "
            f"because motion is {capability.status} / {capability.source}. "
            f"{capability.message}"
        )

    def _build_request_warnings(
        self,
        *,
        raw_motion_event: str | None,
        motion_event: str,
        character_id: str | None,
        expression_id: str | None,
        requested_adapter_mode: str | None,
    ) -> list[str]:
        """Return non-blocking request warnings for future motion wiring."""

        warnings: list[str] = []
        if raw_motion_event is None or not raw_motion_event.strip():
            warnings.append("motion_event was empty; defaulted to idle.")
        elif motion_event not in self._SUPPORTED_MOTION_EVENTS:
            warnings.append(
                "motion_event is not one of the initial supported demo events; "
                "future adapters may reject it."
            )

        if character_id is not None and character_id not in self._SUPPORTED_CHARACTER_IDS:
            warnings.append(
                "character_id is not one of the built-in DRC demo characters; "
                "future lightweight avatar mapping may ignore it."
            )

        if expression_id is not None and expression_id not in self._SUPPORTED_EXPRESSION_IDS:
            warnings.append(
                "expression_id is not one of the initial lightweight avatar expressions; "
                "future adapters may map it to idle."
            )

        if (
            requested_adapter_mode is not None
            and requested_adapter_mode not in self._SUPPORTED_REQUESTED_ADAPTER_MODES
        ):
            warnings.append(
                "requested_adapter_mode is not one of disabled/framework/vts/simulator; "
                "server config still decides the resolved adapter mode."
            )

        return warnings

    def _normalized_request_value(self, value: str | None) -> str | None:
        """Normalize optional request metadata without changing the safe contract."""

        if value is None:
            return None

        normalized = value.strip()
        return normalized or None

    def _normalized_adapter_request(self, value: str | None) -> str | None:
        normalized = self._normalized_request_value(value)
        if normalized is None:
            return None
        return normalized.lower()

    def _normalized_engine(self) -> str:
        return self._config.conversation_engine.strip().lower() or "mock"

    def _normalized_motion_adapter_mode(self) -> str:
        return self._config.motion_adapter_mode.strip().lower() or "disabled"

    def _resolve_mode(self, engine: str) -> str:
        if engine == "framework":
            return "framework_local"

        if engine == "mock" and self._is_mock_safe_profile():
            return "mock_safe"

        if engine == "mock":
            return "mock"

        return "unsupported"

    def _is_mock_safe_profile(self) -> bool:
        return (
            self._config.sleep_provider == "mock"
            and not self._config.gemini_api_key
            and not self._config.xai_api_key
            and not self._config.google_health_enable_real_token_exchange
            and not self._config.google_health_enable_real_token_refresh
            and not self._config.google_health_enable_real_api_requests
            and not self._config.google_health_real_api_opt_in
            and not self._config.fitbit_enable_real_token_exchange
        )
