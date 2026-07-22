from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Mapping

from app.config import AppConfig
from app.services.framework_text_chat_provider_env_diagnosis import (
    KNOWN_PROVIDER_ENV_NAMES,
    FrameworkTextChatProviderEnvVarStatus,
)


@dataclass(frozen=True)
class FrameworkTextChatProviderEnvReadinessResult:
    """Public-safe provider env readiness result for FW text chat.

    Only env var names and boolean set/unset states are returned. Actual API key
    values must never be exposed by this boundary.
    """

    status: str
    required_env_names: tuple[str, ...]
    configured_provider_env_names: tuple[str, ...]
    env_statuses: tuple[FrameworkTextChatProviderEnvVarStatus, ...]
    safe_message: str


class FrameworkTextChatProviderEnvReadinessService:
    """Check FW text chat provider env readiness without using secrets.

    Day26 keeps this check deliberately narrow: it reads local environment
    variable names and presence only. It does not import the framework package,
    create sessions, call ask/ask_stream, or call provider APIs.
    """

    def __init__(
        self,
        config: AppConfig,
        *,
        environ: Mapping[str, str] | None = None,
    ) -> None:
        self._config = config
        self._environ = environ if environ is not None else os.environ

    def run(
        self,
        *,
        required_env_names: tuple[str, ...] = ("GOOGLE_API_KEY",),
    ) -> FrameworkTextChatProviderEnvReadinessResult:
        """Return set/unset readiness for required and known provider env names."""

        normalized_required = _normalize_env_names(required_env_names)
        names_to_check = _dedupe_env_names(
            normalized_required + tuple(KNOWN_PROVIDER_ENV_NAMES)
        )
        env_statuses = tuple(self._status_for_env_name(name) for name in names_to_check)
        configured_names = tuple(status.name for status in env_statuses if status.is_set)
        missing_required = tuple(
            status.name
            for status in env_statuses
            if status.name in normalized_required and not status.is_set
        )

        if missing_required:
            status = "blocked"
            safe_message = (
                "Provider env readiness is blocked because required env var "
                f"names are unset: {', '.join(missing_required)}. Set values only "
                "in the local operator environment or backend/.env; never commit "
                "or paste secret values."
            )
        else:
            status = "ready"
            safe_message = (
                "Required provider env names are set locally. Values are hidden. "
                "Re-run strict framework session diagnosis to confirm the next "
                "safe failure site or session creation result."
            )

        return FrameworkTextChatProviderEnvReadinessResult(
            status=status,
            required_env_names=normalized_required,
            configured_provider_env_names=configured_names,
            env_statuses=env_statuses,
            safe_message=safe_message,
        )

    def _status_for_env_name(self, env_name: str) -> FrameworkTextChatProviderEnvVarStatus:
        is_set = bool(self._environ.get(env_name, "").strip())
        return FrameworkTextChatProviderEnvVarStatus(
            name=env_name,
            is_set=is_set,
            safe_message=(
                f"{env_name} is set locally. Value is hidden."
                if is_set
                else f"{env_name} is not set locally."
            ),
        )


def _normalize_env_names(env_names: tuple[str, ...]) -> tuple[str, ...]:
    normalized = tuple(name.strip().upper() for name in env_names if name.strip())
    if not normalized:
        return ("GOOGLE_API_KEY",)
    filtered = _dedupe_env_names(normalized)
    return filtered or ("GOOGLE_API_KEY",)


def _dedupe_env_names(env_names: tuple[str, ...]) -> tuple[str, ...]:
    names: list[str] = []
    for name in env_names:
        if name not in KNOWN_PROVIDER_ENV_NAMES:
            continue
        if name in names:
            continue
        names.append(name)
    return tuple(names)
