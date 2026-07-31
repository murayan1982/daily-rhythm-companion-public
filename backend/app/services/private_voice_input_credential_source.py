from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Callable


EnvironmentReader = Callable[[str], str | None]


class PrivateVoiceInputCredentialError(RuntimeError):
    """Public-safe failure for the host-owned private credential boundary."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.retryable = False


@dataclass(frozen=True)
class PrivateVoiceInputCredentialSource:
    """Build one short-lived FW credential object from a private env value.

    The raw value is read only when the Framework credential type is already
    available and the caller is about to assemble the real executor. The value
    is never stored on this object, returned, logged, or added to AppConfig.
    """

    environment_name: str = "OPENAI_API_KEY"
    _environment_reader: EnvironmentReader = field(
        default=os.getenv,
        repr=False,
        compare=False,
    )

    def __post_init__(self) -> None:
        name = str(self.environment_name).strip()
        if not name:
            raise ValueError("environment_name must be non-empty")
        if not callable(self._environment_reader):
            raise ValueError("environment_reader must be callable")
        object.__setattr__(self, "environment_name", name)

    def is_available(self) -> bool:
        value = self._environment_reader(self.environment_name)
        return isinstance(value, str) and bool(value.strip())

    def build_for(self, credential_type: type[Any]) -> Any:
        if not isinstance(credential_type, type):
            raise PrivateVoiceInputCredentialError(
                "private_credential_type_invalid",
                "Private voice-input credential type is unavailable.",
            )

        value = self._environment_reader(self.environment_name)
        if not isinstance(value, str) or not value.strip():
            raise PrivateVoiceInputCredentialError(
                "private_credential_unavailable",
                "Private voice-input credentials are unavailable.",
            )

        try:
            return credential_type(value.strip())
        except Exception as exc:
            raise PrivateVoiceInputCredentialError(
                "private_credential_build_failed",
                "Private voice-input credentials could not be prepared safely.",
            ) from exc
