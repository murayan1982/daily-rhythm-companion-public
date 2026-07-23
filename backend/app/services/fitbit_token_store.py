from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


DEFAULT_REFRESH_MARGIN_SECONDS = 300


@dataclass(frozen=True)
class FitbitTokenStatus:
    """Non-sensitive status for the local Fitbit token store."""

    exists: bool
    has_access_token: bool
    has_refresh_token: bool
    readable: bool = True
    source: str | None = None
    expiration_known: bool = False
    access_token_expired: bool = False
    should_refresh: bool = False
    is_development_dummy: bool = False


@dataclass(frozen=True)
class StoredFitbitTokens:
    """
    Token values loaded from the local Fitbit token store.

    This object contains sensitive token values. Do not return it directly
    from API responses or print it to logs.
    """

    access_token: str
    refresh_token: str | None = None
    token_type: str | None = None
    expires_in: int | None = None
    expires_at: str | None = None
    scope: str | None = None
    user_id: str | None = None

    def expires_at_datetime(self) -> datetime | None:
        """Return expires_at as an aware UTC datetime when available."""

        if not self.expires_at:
            return None

        try:
            parsed = datetime.fromisoformat(self.expires_at)
        except ValueError:
            return None

        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)

        return parsed.astimezone(timezone.utc)

    def is_access_token_expired(
        self,
        now: datetime | None = None,
    ) -> bool:
        """
        Return whether the access token is already expired.

        Missing or invalid expires_at is treated as expired so callers use the
        guarded refresh/reconnect boundary instead of assuming validity.
        """

        expires_at = self.expires_at_datetime()

        if expires_at is None:
            return True

        current_time = _as_utc(now or datetime.now(timezone.utc))
        return current_time >= expires_at

    def should_refresh_access_token(
        self,
        *,
        now: datetime | None = None,
        margin_seconds: int = DEFAULT_REFRESH_MARGIN_SECONDS,
    ) -> bool:
        """Return whether the token is expired or within the refresh margin."""

        expires_at = self.expires_at_datetime()

        if expires_at is None:
            return True

        current_time = _as_utc(now or datetime.now(timezone.utc))
        refresh_at = expires_at - timedelta(seconds=max(0, margin_seconds))
        return current_time >= refresh_at


class FitbitTokenStore:
    """
    Local development token store.

    Token values remain inside this file boundary. Status inspection exposes
    only booleans and non-sensitive metadata.
    """

    def __init__(
        self,
        token_file: Path | None = None,
        now_provider: Callable[[], datetime] | None = None,
    ):
        self._token_file = token_file or self._default_token_file()
        self._now_provider = now_provider or (lambda: datetime.now(timezone.utc))

    @property
    def token_file(self) -> Path:
        """Return the local token file path."""

        return self._token_file

    def get_status(
        self,
        *,
        refresh_margin_seconds: int = DEFAULT_REFRESH_MARGIN_SECONDS,
    ) -> FitbitTokenStatus:
        """Return a non-sensitive classification of local token data."""

        if not self._token_file.exists():
            return FitbitTokenStatus(
                exists=False,
                has_access_token=False,
                has_refresh_token=False,
            )

        try:
            data = self._read_json()
        except (OSError, json.JSONDecodeError, ValueError):
            return FitbitTokenStatus(
                exists=True,
                has_access_token=False,
                has_refresh_token=False,
                readable=False,
            )

        access_token = self._optional_string(data, "access_token")
        refresh_token = self._optional_string(data, "refresh_token")
        expires_at_text = self._optional_string(data, "expires_at")
        expires_at = self._parse_datetime(expires_at_text)
        source = self._optional_string(data, "source")

        expiration_known = expires_at is not None
        expired = False
        should_refresh = False

        if access_token:
            if expires_at is None:
                should_refresh = True
            else:
                now = self._now()
                expired = now >= expires_at
                should_refresh = now >= (
                    expires_at
                    - timedelta(seconds=max(0, refresh_margin_seconds))
                )
        elif refresh_token:
            should_refresh = True

        return FitbitTokenStatus(
            exists=True,
            has_access_token=bool(access_token),
            has_refresh_token=bool(refresh_token),
            readable=True,
            source=source,
            expiration_known=expiration_known,
            access_token_expired=expired,
            should_refresh=should_refresh,
            is_development_dummy=source == "development_dummy_token",
        )

    def load_tokens(self) -> StoredFitbitTokens | None:
        """Load sensitive token values, returning None when unusable."""

        if not self._token_file.exists():
            return None

        try:
            data = self._read_json()
        except (OSError, json.JSONDecodeError, ValueError):
            return None

        access_token = self._optional_string(data, "access_token")
        if not access_token:
            return None

        return StoredFitbitTokens(
            access_token=access_token,
            refresh_token=self._optional_string(data, "refresh_token"),
            token_type=self._optional_string(data, "token_type"),
            expires_in=self._optional_int(data, "expires_in"),
            expires_at=self._optional_string(data, "expires_at"),
            scope=self._optional_string(data, "scope"),
            user_id=self._optional_string(data, "user_id"),
        )

    def save_real_tokens(
        self,
        token_data: dict[str, Any],
        source: str = "fitbit_oauth_token_exchange",
    ) -> None:
        """Save normalized real Fitbit token data locally."""

        self._token_file.parent.mkdir(parents=True, exist_ok=True)

        now = self._now()
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

    def save_dummy_tokens_for_development(
        self,
        authorization_code: str,
        state: str | None = None,
    ) -> None:
        """Save clearly marked dummy token data for local development only."""

        self._token_file.parent.mkdir(parents=True, exist_ok=True)

        now = self._now()
        expires_in = 3600

        data = {
            "access_token": "dummy_access_token",
            "refresh_token": "dummy_refresh_token",
            "token_type": "Bearer",
            "expires_in": expires_in,
            "expires_at": self._build_expires_at(
                created_at=now,
                expires_in=expires_in,
            ),
            "created_at": now.isoformat(),
            "source": "development_dummy_token",
            "authorization_code": authorization_code,
            "state": state,
        }

        with self._token_file.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, ensure_ascii=False)

    def _now(self) -> datetime:
        return _as_utc(self._now_provider())

    def _read_json(self) -> dict[str, Any]:
        with self._token_file.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, dict):
            return data

        raise ValueError("fitbit_token_store_not_object")

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
    def _parse_datetime(value: str | None) -> datetime | None:
        if not value:
            return None

        try:
            return _as_utc(datetime.fromisoformat(value))
        except ValueError:
            return None

    @staticmethod
    def _default_token_file() -> Path:
        backend_root = Path(__file__).resolve().parents[2]
        return backend_root / "local_data" / "fitbit_tokens.json"


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)
