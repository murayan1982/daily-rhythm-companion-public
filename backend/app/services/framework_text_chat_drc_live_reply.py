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
from app.services.framework_text_chat_live_message_smoke import PROVIDER_ENV_NAMES
from app.services.framework_text_chat_provider_env_diagnosis import (
    classify_framework_text_chat_session_failure,
)


@dataclass(frozen=True)
class FrameworkTextChatDrcLiveReplyResult:
    """DRC-facing result for a live FW text-chat reply.

    Unlike the Day30/Day31 evidence renderers, this object may carry the actual
    assistant reply text because it is returned to the app UI. Logs and smoke
    renderers must still hide the prompt body, response body, provider payloads,
    API key values, authorization headers, private paths, and raw exceptions.
    """

    status: str
    reply_text: str
    provider_call_attempted: bool
    response_received: bool
    response_type: str | None
    response_text_length: int | None
    response_non_empty: bool
    exception_type: str | None
    failure_kind: str
    safe_message: str
    next_step: str


class FrameworkTextChatDrcLiveReplyService:
    """Execute one DRC post-advice chat reply through FW text chat when gated.

    The caller is responsible for checking the DRC app-level gates before using
    this service. The service still performs provider-placeholder and framework
    root checks defensively so accidental local misconfiguration fails safely.
    """

    def __init__(self, config: AppConfig, *, module_name: str = "framework") -> None:
        self._config = config
        self._module_name = module_name

    def reply(self, *, prompt: str) -> FrameworkTextChatDrcLiveReplyResult:
        """Return a DRC-facing live FW reply or a public-safe blocked result."""

        placeholder_env_names = _placeholder_provider_env_names(PROVIDER_ENV_NAMES)
        if placeholder_env_names:
            return FrameworkTextChatDrcLiveReplyResult(
                status="blocked-provider-env-placeholder",
                reply_text=(
                    "FWテキストチャットは有効化されていますが、provider envが"
                    "placeholder値に見えるため実行を止めました。"
                ),
                provider_call_attempted=False,
                response_received=False,
                response_type=None,
                response_text_length=None,
                response_non_empty=False,
                exception_type=None,
                failure_kind="provider-env-placeholder",
                safe_message=(
                    "Live DRC adapter reply is blocked because at least one provider "
                    "env value looks like a placeholder."
                ),
                next_step="replace-placeholder-provider-env-locally",
            )

        project_root = self._framework_project_root()
        if project_root is None or not project_root.exists():
            return FrameworkTextChatDrcLiveReplyResult(
                status="blocked-framework-root-missing",
                reply_text=(
                    "FWテキストチャットは有効化されていますが、FRAMEWORK_ROOT または "
                    "FRAMEWORK_PROJECT_ROOT が未設定のため実行できません。"
                ),
                provider_call_attempted=False,
                response_received=False,
                response_type=None,
                response_text_length=None,
                response_non_empty=False,
                exception_type=None,
                failure_kind="framework-root-missing",
                safe_message="Configured framework project root is missing.",
                next_step="configure-framework-project-root",
            )

        try:
            with framework_text_chat_import_context(project_root):
                module = importlib.import_module(self._module_name)
                create_session = getattr(module, "create_text_chat_session", None)
                if not callable(create_session):
                    return FrameworkTextChatDrcLiveReplyResult(
                        status="blocked-public-api-missing",
                        reply_text=(
                            "FWテキストチャットのpublic APIが見つからないため、"
                            "今回はmock-safe表示に戻します。"
                        ),
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
            return FrameworkTextChatDrcLiveReplyResult(
                status="error",
                reply_text=(
                    "FWテキストチャット応答の取得中に安全に停止しました。"
                    "設定とstrict smoke結果を確認してください。"
                ),
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
                safe_message=(
                    "Live DRC adapter reply failed safely: "
                    + exception_type
                    + ". "
                    + safe_message
                ),
                next_step="inspect-live-drc-adapter-reply-failure-kind",
            )

        text = _extract_response_text(response)
        if not text.strip():
            return FrameworkTextChatDrcLiveReplyResult(
                status="error-empty-response",
                reply_text=(
                    "FWテキストチャットから空の応答が返ったため、"
                    "今回はmock-safe表示に戻します。"
                ),
                provider_call_attempted=True,
                response_received=True,
                response_type=type(response).__name__,
                response_text_length=len(text),
                response_non_empty=False,
                exception_type=None,
                failure_kind="empty-response",
                safe_message=(
                    "Live DRC adapter reply returned an empty response. The response "
                    "body was not printed."
                ),
                next_step="inspect-framework-response-normalization",
            )

        return FrameworkTextChatDrcLiveReplyResult(
            status="responded",
            reply_text=text,
            provider_call_attempted=True,
            response_received=True,
            response_type=type(response).__name__,
            response_text_length=len(text),
            response_non_empty=True,
            exception_type=None,
            failure_kind="none",
            safe_message=(
                "Live FW text-chat reply reached the DRC post-advice chat adapter. "
                "The app UI receives the reply text; logs should keep bodies hidden."
            ),
            next_step="verify-live-fw-response-through-drc-chat-api",
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


def render_drc_live_reply_result(result: FrameworkTextChatDrcLiveReplyResult) -> str:
    """Render public-safe DRC adapter live-reply metadata without body text."""

    lines = [
        "drc_live_text_chat_reply_status: " + result.status,
        "drc_live_text_chat_reply_provider_call_attempted: "
        + str(result.provider_call_attempted),
        "drc_live_text_chat_reply_response_received: "
        + str(result.response_received),
        "drc_live_text_chat_reply_response_type: " + str(result.response_type),
        "drc_live_text_chat_reply_response_text_length_present: "
        + str(result.response_text_length is not None),
        "drc_live_text_chat_reply_response_non_empty: "
        + str(result.response_non_empty),
        "drc_live_text_chat_reply_exception_type: " + str(result.exception_type),
        "drc_live_text_chat_reply_failure_kind: " + result.failure_kind,
        "drc_live_text_chat_reply_next_step: " + result.next_step,
        "drc_live_text_chat_reply_safe_message: " + result.safe_message,
    ]
    return "\n".join(lines)


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
