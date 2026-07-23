from __future__ import annotations

import json
import secrets
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class FitbitOAuthStateStatus:
    exists: bool
    state: str | None = None
    created_at: datetime | None = None
    readable: bool = True


@dataclass(frozen=True)
class FitbitOAuthStateConsumeResult:
    matched: bool
    expired: bool
    consumed: bool


class FitbitOAuthStateStore:
    """Local one-time OAuth state store for the Fitbit callback boundary."""

    def __init__(
        self,
        state_file: Path | None = None,
        now_provider: Callable[[], datetime] | None = None,
    ):
        self._state_file = state_file or self._default_state_file()
        self._now_provider = now_provider or (lambda: datetime.now(timezone.utc))

    @property
    def state_file(self) -> Path:
        return self._state_file

    def create_and_save_state(self) -> str:
        """Generate and save a new OAuth state value."""

        state = secrets.token_urlsafe(32)
        self._state_file.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "state": state,
            "created_at": self._now().isoformat(),
            "source": "fitbit_oauth_state",
        }

        with self._state_file.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, ensure_ascii=False)

        return state

    def get_status(self) -> FitbitOAuthStateStatus:
        """Return the saved OAuth state metadata, if available."""

        if not self._state_file.exists():
            return FitbitOAuthStateStatus(exists=False, state=None)

        try:
            data = self._read_json()
        except (OSError, json.JSONDecodeError):
            return FitbitOAuthStateStatus(
                exists=True,
                state=None,
                readable=False,
            )

        state = data.get("state")
        if not isinstance(state, str) or not state:
            return FitbitOAuthStateStatus(exists=True, state=None)

        return FitbitOAuthStateStatus(
            exists=True,
            state=state,
            created_at=self._parse_created_at(data.get("created_at")),
        )

    def validate_state(self, returned_state: str | None) -> bool:
        """Return whether the callback state matches the saved state."""

        if not returned_state:
            return False

        status = self.get_status()
        if not status.state:
            return False

        return secrets.compare_digest(status.state, returned_state)

    def is_state_expired(self, ttl_seconds: int) -> bool:
        """Return whether the saved OAuth state is older than ttl_seconds."""

        status = self.get_status()
        if not status.created_at:
            return True

        age_seconds = (self._now() - status.created_at).total_seconds()
        return age_seconds > max(0, ttl_seconds)

    def consume_state(
        self,
        returned_state: str | None,
        ttl_seconds: int,
    ) -> FitbitOAuthStateConsumeResult:
        """
        Validate and consume one OAuth state.

        A matching unexpired state is deleted before token exchange begins, so
        callback replay cannot reuse it. Matching expired state is also removed
        and requires a new connect flow.
        """

        if not returned_state:
            return FitbitOAuthStateConsumeResult(False, False, False)

        status = self.get_status()
        if not status.state or not secrets.compare_digest(
            status.state,
            returned_state,
        ):
            return FitbitOAuthStateConsumeResult(False, False, False)

        expired = self.is_state_expired(ttl_seconds)
        deleted = self.delete_state()

        return FitbitOAuthStateConsumeResult(
            matched=True,
            expired=expired,
            consumed=deleted and not expired,
        )

    def delete_state(self) -> bool:
        """Delete or invalidate the saved OAuth state, failing closed."""

        try:
            self._state_file.unlink(missing_ok=True)
            return True
        except OSError:
            try:
                self._state_file.write_text("{}", encoding="utf-8")
                return True
            except OSError:
                return False

    def _now(self) -> datetime:
        value = self._now_provider()
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    def _read_json(self) -> dict[str, Any]:
        with self._state_file.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, dict):
            return data

        return {}

    @staticmethod
    def _default_state_file() -> Path:
        backend_root = Path(__file__).resolve().parents[2]
        return backend_root / "local_data" / "fitbit_oauth_state.json"

    @staticmethod
    def _parse_created_at(value: Any) -> datetime | None:
        if not isinstance(value, str) or not value:
            return None

        try:
            parsed = datetime.fromisoformat(value)
        except ValueError:
            return None

        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)

        return parsed.astimezone(timezone.utc)
