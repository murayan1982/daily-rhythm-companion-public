from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class StoredGoogleHealthTokens:
    """
    Google OAuth tokens loaded from local development storage.

    Token values are sensitive and must not be printed, committed, included in
    release packages, or returned from API responses.
    """

    access_token: str
    token_type: str
    refresh_token: str | None = None
    scope: str | None = None
    expires_at: datetime | None = None
    created_at: datetime | None = None
    source: str | None = None

    def is_access_token_expired(
        self,
        *,
        now: datetime | None = None,
        leeway_seconds: int = 60,
    ) -> bool:
        """Return True when the access token is expired or close to expiry."""

        if self.expires_at is None:
            return False

        current_time = now or datetime.now(timezone.utc)
        current_time = _ensure_aware_utc(current_time)
        threshold = current_time + timedelta(seconds=leeway_seconds)

        return self.expires_at <= threshold

    def should_refresh_access_token(
        self,
        *,
        now: datetime | None = None,
        leeway_seconds: int = 60,
    ) -> bool:
        """Return True when an expired token has a refresh token available."""

        return bool(self.refresh_token) and self.is_access_token_expired(
            now=now,
            leeway_seconds=leeway_seconds,
        )

    def to_storage_dict(self) -> dict[str, Any]:
        """Convert loaded tokens back to the local storage shape."""

        data: dict[str, Any] = {
            "access_token": self.access_token,
            "token_type": self.token_type,
        }

        if self.refresh_token:
            data["refresh_token"] = self.refresh_token

        if self.scope:
            data["scope"] = self.scope

        if self.expires_at:
            data["expires_at"] = self.expires_at.isoformat()

        if self.created_at:
            data["created_at"] = self.created_at.isoformat()

        if self.source:
            data["source"] = self.source

        return data


class GoogleHealthTokenStore:
    """
    Local development token store for Google Health OAuth readiness.

    Token values are sensitive and must not be printed, committed, included in
    release packages, or returned from API responses.
    """

    def __init__(self, token_file: Path | None = None):
        self._token_file = token_file or self._default_token_file()

    @property
    def token_file(self) -> Path:
        """Return the local token file path."""

        return self._token_file

    def load_tokens(self) -> StoredGoogleHealthTokens | None:
        """Load locally stored Google OAuth tokens when available."""

        if not self._token_file.exists():
            return None

        with self._token_file.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, dict):
            return None

        access_token = self._optional_string(data, "access_token")
        token_type = self._optional_string(data, "token_type") or "Bearer"

        if not access_token:
            return None

        return StoredGoogleHealthTokens(
            access_token=access_token,
            token_type=token_type,
            refresh_token=self._optional_string(data, "refresh_token"),
            scope=self._optional_string(data, "scope"),
            expires_at=_optional_datetime(data.get("expires_at")),
            created_at=_optional_datetime(data.get("created_at")),
            source=self._optional_string(data, "source"),
        )

    def save_tokens(
        self,
        token_data: dict[str, Any],
        source: str = "google_health_token_exchange",
    ) -> None:
        """Save normalized Google OAuth token data locally."""

        self._token_file.parent.mkdir(parents=True, exist_ok=True)

        now = datetime.now(timezone.utc)
        data = dict(token_data)
        data["created_at"] = now.isoformat()
        data["source"] = source

        if "expires_at" not in data:
            data["expires_at"] = self._build_expires_at(
                created_at=now,
                expires_in=self._optional_int(data, "expires_in"),
            )

        with self._token_file.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, ensure_ascii=False)

    @staticmethod
    def _build_expires_at(
        *,
        created_at: datetime,
        expires_in: int | None,
    ) -> str | None:
        if expires_in is None:
            return None

        return (created_at + timedelta(seconds=expires_in)).isoformat()

    @staticmethod
    def _optional_string(
        data: dict[str, Any],
        key: str,
    ) -> str | None:
        value = data.get(key)

        if isinstance(value, str) and value:
            return value

        return None

    @staticmethod
    def _optional_int(
        data: dict[str, Any],
        key: str,
    ) -> int | None:
        value = data.get(key)

        if isinstance(value, int):
            return value

        if isinstance(value, str) and value.isdigit():
            return int(value)

        return None

    @staticmethod
    def _default_token_file() -> Path:
        backend_root = Path(__file__).resolve().parents[2]
        return backend_root / "local_data" / "google_health_tokens.json"


def _optional_datetime(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None

    try:
        return _ensure_aware_utc(datetime.fromisoformat(value))
    except ValueError:
        return None


def _ensure_aware_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)

    return value.astimezone(timezone.utc)
