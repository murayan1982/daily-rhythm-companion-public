from __future__ import annotations

from dataclasses import dataclass
import os
import re
from typing import Mapping

from app.config import AppConfig


KNOWN_PROVIDER_ENV_NAMES = (
    "GOOGLE_API_KEY",
    "GEMINI_API_KEY",
    "OPENAI_API_KEY",
    "XAI_API_KEY",
)

_PROVIDER_ENV_PATTERN = re.compile(
    r"\b([A-Z][A-Z0-9_]*(?:API_KEY|TOKEN|SECRET))\b"
)
_MISSING_ENV_HINT_PATTERN = re.compile(
    r"\b(not defined|not set|missing|required|undefined)\b",
    flags=re.IGNORECASE,
)


@dataclass(frozen=True)
class FrameworkTextChatProviderEnvVarStatus:
    """Public-safe status for one provider environment variable."""

    name: str
    is_set: bool
    safe_message: str


@dataclass(frozen=True)
class FrameworkTextChatProviderEnvDiagnosisResult:
    """Public-safe provider-env diagnosis for FW text chat session setup."""

    status: str
    failure_kind: str
    required_env_names: tuple[str, ...]
    env_statuses: tuple[FrameworkTextChatProviderEnvVarStatus, ...]
    safe_message: str


class FrameworkTextChatProviderEnvDiagnosisService:
    """Diagnose provider env readiness without exposing values or calling providers.

    The service records only env var names and boolean presence. It must not
    print, persist, or return actual API key values. It also does not import the
    framework package, create sessions, call ask/ask_stream, or call provider
    APIs.
    """

    def __init__(
        self,
        config: AppConfig,
        *,
        environ: Mapping[str, str] | None = None,
    ) -> None:
        self._config = config
        self._environ = environ if environ is not None else os.environ

    def run_for_session_failure(
        self,
        *,
        exception_type: str | None,
        safe_message: str,
    ) -> FrameworkTextChatProviderEnvDiagnosisResult:
        failure_kind = classify_framework_text_chat_session_failure(
            exception_type=exception_type,
            safe_message=safe_message,
        )
        required_env_names = extract_provider_env_names(safe_message)
        env_statuses = tuple(
            self._status_for_env_name(env_name) for env_name in required_env_names
        )

        if failure_kind == "provider-env-missing" and required_env_names:
            if all(status.is_set for status in env_statuses):
                status = "configured"
                message = (
                    "Provider env vars referenced by the session failure are set, "
                    "but values are intentionally not exposed. Re-run the strict "
                    "session preflight to confirm the next failure site."
                )
            else:
                status = "blocked"
                names = ", ".join(required_env_names)
                message = (
                    "Framework session creation reached provider-env initialization. "
                    f"Missing or unavailable env var names: {names}. "
                    "Set them only in the local operator environment or backend/.env; "
                    "do not commit secrets."
                )
        elif failure_kind == "provider-env-missing":
            status = "blocked"
            message = (
                "Framework session creation appears blocked by provider env setup, "
                "but no public-safe env var name was extracted."
            )
        else:
            status = "not-provider-env"
            message = "The supplied session failure is not classified as provider-env setup."

        return FrameworkTextChatProviderEnvDiagnosisResult(
            status=status,
            failure_kind=failure_kind,
            required_env_names=required_env_names,
            env_statuses=env_statuses,
            safe_message=message,
        )

    def run_known_env_inventory(self) -> FrameworkTextChatProviderEnvDiagnosisResult:
        """Return a public-safe known provider env inventory."""

        statuses = tuple(self._status_for_env_name(name) for name in KNOWN_PROVIDER_ENV_NAMES)
        configured_names = tuple(status.name for status in statuses if status.is_set)
        status = "configured" if configured_names else "not-configured"
        return FrameworkTextChatProviderEnvDiagnosisResult(
            status=status,
            failure_kind="provider-env-inventory",
            required_env_names=KNOWN_PROVIDER_ENV_NAMES,
            env_statuses=statuses,
            safe_message=(
                "Known provider env names were checked by name only. Actual values "
                "were not exposed, persisted, or used for a provider call."
            ),
        )

    def _status_for_env_name(self, env_name: str) -> FrameworkTextChatProviderEnvVarStatus:
        is_set = bool(self._environ.get(env_name, "").strip())
        return FrameworkTextChatProviderEnvVarStatus(
            name=env_name,
            is_set=is_set,
            safe_message=(
                f"{env_name} is set in the local environment. Value is hidden."
                if is_set
                else f"{env_name} is not set in the local environment."
            ),
        )


def classify_framework_text_chat_session_failure(
    *,
    exception_type: str | None,
    safe_message: str,
) -> str:
    """Classify a public-safe session-creation failure message."""

    if not safe_message:
        return "unknown"

    env_names = extract_provider_env_names(safe_message)
    if not env_names:
        return "unknown"

    if exception_type in {"OSError", "RuntimeError", "ValueError", "FacadeConfigError"}:
        if _MISSING_ENV_HINT_PATTERN.search(safe_message):
            return "provider-env-missing"

    return "provider-env-mentioned"


def extract_provider_env_names(message: str) -> tuple[str, ...]:
    """Extract public-safe provider env var names from a sanitized message."""

    names: list[str] = []
    for match in _PROVIDER_ENV_PATTERN.finditer(message or ""):
        name = match.group(1)
        if name not in KNOWN_PROVIDER_ENV_NAMES:
            continue
        if name in names:
            continue
        names.append(name)
    return tuple(names)
