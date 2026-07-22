from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


DEFAULT_REFRESH_MARGIN_SECONDS = 300


@dataclass(frozen=True)
class FitbitTokenStatus:
    """
    Lightweight status for local Fitbit token storage.

    v0.4.0+ only checks whether a local token file exists and appears to
    contain token-like fields. Real token validation and refresh will be added
    later.
    """

    exists: bool
    has_access_token: bool
    has_refresh_token: bool


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
        """Return expires_at as an aware datetime when available."""

        if not self.expires_at:
            return None

        try:
            parsed = datetime.fromisoformat(self.expires_at)
        except ValueError:
            return None

        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)

        return parsed

    def is_access_token_expired(
        self,
        now: datetime | None = None,
    ) -> bool:
        """
        Return whether the access token is already expired.

        If expires_at is missing or invalid, treat the token as expired so the
        refresh boundary can take over.
        """

        expires_at = self.expires_at_datetime()

        if expires_at is None:
            return True

        current_time = now or datetime.now(timezone.utc)

        if current_time.tzinfo is None:
            current_time = current_time.replace(tzinfo=timezone.utc)

        return current_time >= expires_at

    def should_refresh_access_token(
        self,
        *,
        now: datetime | None = None,
        margin_seconds: int = DEFAULT_REFRESH_MARGIN_SECONDS,
    ) -> bool:
        """
        Return whether the access token should be refreshed soon.

        The default margin refreshes tokens 5 minutes before expiration to
        avoid calling Fitbit with a nearly expired access token.
        """

        expires_at = self.expires_at_datetime()

        if expires_at is None:
            return True

        current_time = now or datetime.now(timezone.utc)

        if current_time.tzinfo is None:
            current_time = current_time.replace(tzinfo=timezone.utc)

        refresh_at = expires_at - timedelta(seconds=margin_seconds)
        return current_time >= refresh_at


class FitbitTokenStore:
    """
    Local development token store.

    This class owns the local file boundary for Fitbit OAuth tokens. Token
    values are sensitive and must not be printed or returned directly from API
    responses.
    """

    def __init__(self, token_file: Path | None = None):
        self._token_file = token_file or self._default_token_file()

    @property
    def token_file(self) -> Path:
        """Return the local token file path."""

        return self._token_file

    def get_status(self) -> FitbitTokenStatus:
        """Return whether local token data appears to exist."""

        if not self._token_file.exists():
            return FitbitTokenStatus(
                exists=False,
                has_access_token=False,
                has_refresh_token=False,
            )

        try:
            data = self._read_json()
        except (OSError, json.JSONDecodeError):
            return FitbitTokenStatus(
                exists=True,
                has_access_token=False,
                has_refresh_token=False,
            )

        return FitbitTokenStatus(
            exists=True,
            has_access_token=bool(data.get("access_token")),
            has_refresh_token=bool(data.get("refresh_token")),
        )

    def load_tokens(self) -> StoredFitbitTokens | None:
        """
        Load locally stored Fitbit token values.

        Returns None when token data does not exist or does not contain a usable
        access token.
        """

        if not self._token_file.exists():
            return None

        try:
            data = self._read_json()
        except (OSError, json.JSONDecodeError):
            return None

        access_token = data.get("access_token")

        if not isinstance(access_token, str) or not access_token:
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
        """
        Save real Fitbit token data locally.

        The caller is responsible for normalizing token fields before calling
        this method. This method adds storage metadata only.
        """

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

    def save_dummy_tokens_for_development(
        self,
        authorization_code: str,
        state: str | None = None,
    ) -> None:
        """
        Save dummy token data for local development only.

        This does not represent a real Fitbit connection. It exists so the
        app can test the post-callback connected-state flow before real token
        exchange is implemented.
        """

        self._token_file.parent.mkdir(parents=True, exist_ok=True)

        now = datetime.now(timezone.utc)
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

    def _read_json(self) -> dict[str, Any]:
        with self._token_file.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, dict):
            return data

        return {}

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
        return backend_root / "local_data" / "fitbit_tokens.json"