from __future__ import annotations

import json
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


DEFAULT_GOOGLE_HEALTH_OAUTH_STATE_TTL_SECONDS = 600


@dataclass(frozen=True)
class GoogleHealthOAuthState:
    """Stored Google Health OAuth state metadata."""

    state: str
    created_at: str
    expires_at: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "state": self.state,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
        }


class GoogleHealthOAuthStateStore:
    """
    Local development OAuth state store for Google Health OAuth readiness.

    The state value is used to protect the callback flow from CSRF-style
    mismatches. This local JSON store is for development only.
    """

    def __init__(self, state_file: Path | None = None):
        self._state_file = state_file or self._default_state_file()

    @property
    def state_file(self) -> Path:
        """Return the local OAuth state file path."""

        return self._state_file

    def create_state(
        self,
        ttl_seconds: int = DEFAULT_GOOGLE_HEALTH_OAUTH_STATE_TTL_SECONDS,
    ) -> GoogleHealthOAuthState:
        """Create, store, and return a new OAuth state value."""

        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(seconds=ttl_seconds)

        oauth_state = GoogleHealthOAuthState(
            state=secrets.token_urlsafe(32),
            created_at=now.isoformat(),
            expires_at=expires_at.isoformat(),
        )

        self._state_file.parent.mkdir(parents=True, exist_ok=True)

        with self._state_file.open("w", encoding="utf-8") as file:
            json.dump(oauth_state.to_dict(), file, indent=2, ensure_ascii=False)

        return oauth_state

    def load_state(self) -> GoogleHealthOAuthState | None:
        """Load the currently stored OAuth state when available."""

        if not self._state_file.exists():
            return None

        try:
            with self._state_file.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except (OSError, json.JSONDecodeError):
            return None

        if not isinstance(data, dict):
            return None

        state = data.get("state")
        created_at = data.get("created_at")
        expires_at = data.get("expires_at")

        if not all(isinstance(value, str) and value for value in (
            state,
            created_at,
            expires_at,
        )):
            return None

        return GoogleHealthOAuthState(
            state=state,
            created_at=created_at,
            expires_at=expires_at,
        )

    @staticmethod
    def _default_state_file() -> Path:
        backend_root = Path(__file__).resolve().parents[2]
        return backend_root / "local_data" / "google_health_oauth_state.json"