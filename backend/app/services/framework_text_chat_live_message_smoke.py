from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
import importlib
import inspect
import os
import re
from typing import Any

from app.config import AppConfig
from app.services.framework_text_chat_import_setup import (
    framework_text_chat_import_context,
)
from app.services.framework_text_chat_live_message_gate import (
    FrameworkTextChatLiveMessageGateResult,
    FrameworkTextChatLiveMessageGateService,
)
from app.services.framework_text_chat_provider_env_diagnosis import (
    classify_framework_text_chat_session_failure,
)
from app.services.framework_text_chat_session_created_evidence import (
    FrameworkTextChatSessionCreatedEvidenceService,
)
from app.services.framework_text_chat_session_diagnosis import (
    FrameworkTextChatSessionDiagnosisService,
)


LIVE_TEXT_CHAT_MESSAGE_SMOKE_PROMPT_SHAPE = "<bounded-live-text-chat-smoke-prompt>"
DEFAULT_LIVE_TEXT_CHAT_MESSAGE_SMOKE_PROMPT = (
    "ローカル動作確認です。日本語で短く一言だけ、やさしく挨拶してください。"
)
PROVIDER_ENV_NAMES = (
    "GOOGLE_API_KEY",
    "GEMINI_API_KEY",
    "OPENAI_API_KEY",
    "XAI_API_KEY",
)


@dataclass(frozen=True)
class FrameworkTextChatLiveMessageSmokeResult:
    """Public-safe result for one explicitly gated live text-chat message smoke.

    This result intentionally does not contain the prompt body, response body,
    provider payload, request headers, token counts, API key values, private
    paths, or raw exceptions.
    """

    status: str
    gate_status: str
    gate_enabled: bool
    session_created: bool
    has_session_info: bool
    prompt_shape: str
    provider_call_attempted: bool
    response_received: bool
    response_type: str | None
    response_text_length: int | None
    response_non_empty: bool
    exception_type: str | None
    failure_kind: str
    safe_message: str
    next_step: str


class FrameworkTextChatLiveMessageSmokeService:
    """Run one bounded FW text-chat message only after all explicit gates pass."""

    def __init__(self, config: AppConfig, *, module_name: str = "framework") -> None:
        self._config = config
        self._module_name = module_name

    def run(
        self,
        *,
        prompt: str = DEFAULT_LIVE_TEXT_CHAT_MESSAGE_SMOKE_PROMPT,
    ) -> FrameworkTextChatLiveMessageSmokeResult:
        """Execute one local live-message smoke after public-safe gate checks.

        The order is intentionally conservative:
        1. Re-run session-created evidence.
        2. Re-evaluate ``DRC_FW40_ENABLE_LIVE_TEXT_CHAT_MESSAGE``.
        3. Block placeholder-looking provider env values before any provider call.
        4. Create a fresh session and call ``session.ask(prompt)`` once.

        The returned result only exposes shapes and booleans.
        """

        diagnosis = FrameworkTextChatSessionDiagnosisService(
            self._config,
            module_name=self._module_name,
        ).run()
        evidence = FrameworkTextChatSessionCreatedEvidenceService().from_diagnosis(
            diagnosis
        )
        gate = FrameworkTextChatLiveMessageGateService(self._config).evaluate(evidence)

        if gate.status != "ready":
            return self._blocked_from_gate(gate)

        placeholder_env_names = _placeholder_provider_env_names(PROVIDER_ENV_NAMES)
        if placeholder_env_names:
            return FrameworkTextChatLiveMessageSmokeResult(
                status="blocked-provider-env-placeholder",
                gate_status=gate.status,
                gate_enabled=gate.gate_enabled,
                session_created=gate.session_created,
                has_session_info=gate.has_session_info,
                prompt_shape=LIVE_TEXT_CHAT_MESSAGE_SMOKE_PROMPT_SHAPE,
                provider_call_attempted=False,
                response_received=False,
                response_type=None,
                response_text_length=None,
                response_non_empty=False,
                exception_type=None,
                failure_kind="provider-env-placeholder",
                safe_message=(
                    "Live text-chat message smoke is blocked because at least one "
                    "configured provider env value looks like a placeholder. Replace "
                    "it locally or unset it before running the live provider call."
                ),
                next_step="replace-placeholder-provider-env-locally",
            )

        project_root = self._framework_project_root()
        if project_root is None or not project_root.exists():
            return FrameworkTextChatLiveMessageSmokeResult(
                status="blocked-framework-root-missing",
                gate_status=gate.status,
                gate_enabled=gate.gate_enabled,
                session_created=gate.session_created,
                has_session_info=gate.has_session_info,
                prompt_shape=LIVE_TEXT_CHAT_MESSAGE_SMOKE_PROMPT_SHAPE,
                provider_call_attempted=False,
                response_received=False,
                response_type=None,
                response_text_length=None,
                response_non_empty=False,
                exception_type=None,
                failure_kind="framework-root-missing",
                safe_message=(
                    "Live text-chat message smoke is blocked because the configured "
                    "framework project root is missing."
                ),
                next_step="configure-framework-project-root",
            )

        try:
            with framework_text_chat_import_context(project_root):
                module = importlib.import_module(self._module_name)
                create_session = getattr(module, "create_text_chat_session", None)
                if not callable(create_session):
                    return FrameworkTextChatLiveMessageSmokeResult(
                        status="blocked-public-api-missing",
                        gate_status=gate.status,
                        gate_enabled=gate.gate_enabled,
                        session_created=gate.session_created,
                        has_session_info=gate.has_session_info,
                        prompt_shape=LIVE_TEXT_CHAT_MESSAGE_SMOKE_PROMPT_SHAPE,
                        provider_call_attempted=False,
                        response_received=False,
                        response_type=None,
                        response_text_length=None,
                        response_non_empty=False,
                        exception_type=None,
                        failure_kind="public-api-missing",
                        safe_message="create_text_chat_session is not available.",
                        next_step="inspect-framework-public-api",
                    )

                with _temporary_cwd(project_root):
                    session = self._create_session(
                        create_session,
                        project_root=project_root,
                    )
                    response = self._ask_session(session=session, prompt=prompt)
        except Exception as exc:  # pragma: no cover - depends on operator checkout.
            exception_type = type(exc).__name__
            safe_message = _sanitize_message(str(exc), project_root)
            return FrameworkTextChatLiveMessageSmokeResult(
                status="error",
                gate_status=gate.status,
                gate_enabled=gate.gate_enabled,
                session_created=gate.session_created,
                has_session_info=gate.has_session_info,
                prompt_shape=LIVE_TEXT_CHAT_MESSAGE_SMOKE_PROMPT_SHAPE,
                provider_call_attempted=True,
                response_received=False,
                response_type=None,
                response_text_length=None,
                response_non_empty=False,
                exception_type=exception_type,
                failure_kind=classify_framework_text_chat_session_failure(
                    exception_type=exception_type,
                    safe_message=safe_message,
                ),
                safe_message="Live text-chat message smoke failed safely: "
                + exception_type
                + ". "
                + safe_message,
                next_step="inspect-live-message-failure-kind",
            )

        summary = _response_summary(response)
        if not summary["non_empty"]:
            return FrameworkTextChatLiveMessageSmokeResult(
                status="error-empty-response",
                gate_status=gate.status,
                gate_enabled=gate.gate_enabled,
                session_created=gate.session_created,
                has_session_info=gate.has_session_info,
                prompt_shape=LIVE_TEXT_CHAT_MESSAGE_SMOKE_PROMPT_SHAPE,
                provider_call_attempted=True,
                response_received=True,
                response_type=summary["type"],
                response_text_length=summary["text_length"],
                response_non_empty=False,
                exception_type=None,
                failure_kind="empty-response",
                safe_message=(
                    "Live text-chat message smoke returned an empty response. "
                    "The response body was not printed."
                ),
                next_step="inspect-framework-response-normalization",
            )

        return FrameworkTextChatLiveMessageSmokeResult(
            status="responded",
            gate_status=gate.status,
            gate_enabled=gate.gate_enabled,
            session_created=gate.session_created,
            has_session_info=gate.has_session_info,
            prompt_shape=LIVE_TEXT_CHAT_MESSAGE_SMOKE_PROMPT_SHAPE,
            provider_call_attempted=True,
            response_received=True,
            response_type=summary["type"],
            response_text_length=summary["text_length"],
            response_non_empty=True,
            exception_type=None,
            failure_kind="none",
            safe_message=(
                "Live text-chat message smoke completed with one bounded "
                "session.ask call. Prompt and response bodies are hidden."
            ),
            next_step="record-live-text-chat-message-evidence",
        )

    def _blocked_from_gate(
        self,
        gate: FrameworkTextChatLiveMessageGateResult,
    ) -> FrameworkTextChatLiveMessageSmokeResult:
        return FrameworkTextChatLiveMessageSmokeResult(
            status="blocked",
            gate_status=gate.status,
            gate_enabled=gate.gate_enabled,
            session_created=gate.session_created,
            has_session_info=gate.has_session_info,
            prompt_shape=LIVE_TEXT_CHAT_MESSAGE_SMOKE_PROMPT_SHAPE,
            provider_call_attempted=False,
            response_received=False,
            response_type=None,
            response_text_length=None,
            response_non_empty=False,
            exception_type=None,
            failure_kind="gate-not-ready",
            safe_message=gate.safe_message,
            next_step=gate.next_step,
        )

    def _create_session(self, create_session: Any, *, project_root: Path) -> Any:
        signature = inspect.signature(create_session)
        kwargs: dict[str, Any] = {}
        candidate_values = {
            "preset": self._config.framework_preset,
            "preset_name": self._config.framework_preset,
            "preset_id": self._config.framework_preset,
            "character": self._config.framework_character,
            "character_name": self._config.framework_character,
            "character_id": self._config.framework_character,
            "project_root": str(project_root),
            "framework_project_root": str(project_root),
        }
        has_var_keyword = any(
            parameter.kind == inspect.Parameter.VAR_KEYWORD
            for parameter in signature.parameters.values()
        )
        if has_var_keyword:
            kwargs = {
                "preset": self._config.framework_preset,
                "character": self._config.framework_character,
                "project_root": str(project_root),
            }
        else:
            for name in signature.parameters:
                value = candidate_values.get(name)
                if value is not None:
                    kwargs[name] = value
        return create_session(**kwargs)

    def _ask_session(self, *, session: Any, prompt: str) -> Any:
        ask = getattr(session, "ask", None)
        if not callable(ask):
            raise RuntimeError("Framework text chat session does not expose ask(text).")
        return ask(prompt)

    def _framework_project_root(self) -> Path | None:
        configured = self._config.framework_project_root or getattr(
            self._config,
            "framework_root",
            None,
        )
        if not configured:
            return None
        return Path(configured).expanduser().resolve()


def render_live_message_smoke(
    result: FrameworkTextChatLiveMessageSmokeResult,
) -> str:
    """Render public-safe live-message smoke lines for logs and docs."""

    lines = [
        "live_text_chat_message_smoke_status: " + result.status,
        "live_text_chat_message_smoke_gate_status: " + result.gate_status,
        "live_text_chat_message_smoke_gate_enabled: " + str(result.gate_enabled),
        "live_text_chat_message_smoke_session_created: "
        + str(result.session_created),
        "live_text_chat_message_smoke_has_session_info: "
        + str(result.has_session_info),
        "live_text_chat_message_smoke_prompt_shape: " + result.prompt_shape,
        "live_text_chat_message_smoke_provider_call_attempted: "
        + str(result.provider_call_attempted),
        "live_text_chat_message_smoke_response_received: "
        + str(result.response_received),
        "live_text_chat_message_smoke_response_type: "
        + str(result.response_type),
        "live_text_chat_message_smoke_response_text_length: "
        + str(result.response_text_length),
        "live_text_chat_message_smoke_response_non_empty: "
        + str(result.response_non_empty),
        "live_text_chat_message_smoke_exception_type: "
        + str(result.exception_type),
        "live_text_chat_message_smoke_failure_kind: " + result.failure_kind,
        "live_text_chat_message_smoke_next_step: " + result.next_step,
        "live_text_chat_message_smoke_safe_message: " + result.safe_message,
    ]
    return "\n".join(lines)


def _response_summary(response: Any) -> dict[str, Any]:
    text = _extract_response_text(response)
    return {
        "type": type(response).__name__,
        "text_length": len(text),
        "non_empty": bool(text.strip()),
    }


def _extract_response_text(response: Any) -> str:
    if isinstance(response, str):
        return response.strip()
    for attr_name in ("message", "text", "content"):
        attr_value = getattr(response, attr_name, None)
        if isinstance(attr_value, str) and attr_value.strip():
            return attr_value.strip()
    if response is None:
        return ""
    return str(response).strip()


def _placeholder_provider_env_names(env_names: tuple[str, ...]) -> tuple[str, ...]:
    placeholders: list[str] = []
    for name in env_names:
        value = os.getenv(name)
        if value is not None and _looks_like_placeholder_secret(value):
            placeholders.append(name)
    return tuple(placeholders)


def _looks_like_placeholder_secret(value: str) -> bool:
    normalized = value.strip().lower()
    if not normalized:
        return False
    if normalized.startswith("<") and normalized.endswith(">"):
        return True
    return normalized in {
        "local-secret-value",
        "replace-me",
        "replace_me",
        "changeme",
        "change-me",
        "dummy",
        "example",
        "your-api-key",
        "your_api_key",
    }


def _sanitize_message(message: str, project_root: Path) -> str:
    if not message:
        return "<empty-error-message>"
    safe = message.replace(str(project_root), "<configured-framework-root>")
    safe = safe.replace(str(project_root).replace("\\", "/"), "<configured-framework-root>")
    safe = re.sub(r"[A-Za-z]:[\\/][^\s:'\"]+", "<private-path>", safe)
    safe = re.sub(r"/(?:Users|home|mnt|tmp)/[^\s:'\"]+", "<private-path>", safe)
    safe = re.sub(r"sk-[A-Za-z0-9_\-]{12,}", "<redacted-api-key>", safe)
    safe = re.sub(r"AIza[0-9A-Za-z_\-]{20,}", "<redacted-api-key>", safe)
    safe = re.sub(r"xai-[A-Za-z0-9_\-]{12,}", "<redacted-api-key>", safe)
    safe = " ".join(safe.split())
    return safe[:240]


@contextmanager
def _temporary_cwd(path: Path):
    previous = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)
