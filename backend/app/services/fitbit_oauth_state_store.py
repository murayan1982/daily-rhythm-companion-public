from __future__ import annotations

import json
import secrets
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class FitbitOAuthStateStatus:
    exists: bool
    state: str | None = None
    created_at: datetime | None = None


class FitbitOAuthStateStore:
    """
    Local development OAuth state store.

    This stores the latest generated OAuth state so the callback can validate
    whether the returned state matches the connect request.
    """

    def __init__(self, state_file: Path | None = None):
        self._state_file = state_file or self._default_state_file()

    @property
    def state_file(self) -> Path:
        return self._state_file

    def create_and_save_state(self) -> str:
        """Generate and save a new OAuth state value."""

        state = secrets.token_urlsafe(32)

        self._state_file.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "state": state,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "source": "fitbit_oauth_state",
        }

        with self._state_file.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, ensure_ascii=False)

        return state

    def get_status(self) -> FitbitOAuthStateStatus:
        """Return the saved OAuth state, if available."""

        if not self._state_file.exists():
            return FitbitOAuthStateStatus(exists=False, state=None)

        try:
            data = self._read_json()
        except (OSError, json.JSONDecodeError):
            return FitbitOAuthStateStatus(exists=True, state=None)

        state = data.get("state")
        if not isinstance(state, str) or not state:
            return FitbitOAuthStateStatus(exists=True, state=None)

        created_at = self._parse_created_at(data.get("created_at"))

        return FitbitOAuthStateStatus(
            exists=True,
            state=state,
            created_at=created_at,
        )

    def validate_state(self, returned_state: str | None) -> bool:
        """Return whether the callback state matches the saved state."""

        if not returned_state:
            return False

        status = self.get_status()
        if not status.state:
            return False

        return secrets.compare_digest(status.state, returned_state)

    def _read_json(self) -> dict[str, Any]:
        with self._state_file.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, dict):
            return data

        return {}

    def is_state_expired(self, ttl_seconds: int) -> bool:
        """Return whether the saved OAuth state is older than ttl_seconds."""

        status = self.get_status()

        if not status.created_at:
            return True

        now = datetime.now(timezone.utc)
        age_seconds = (now - status.created_at).total_seconds()

        return age_seconds > ttl_seconds
    
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