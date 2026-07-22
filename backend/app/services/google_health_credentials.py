from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


GOOGLE_HEALTH_CREDENTIALS_ERROR_NOT_CONFIGURED = "credentials_file_not_configured"
GOOGLE_HEALTH_CREDENTIALS_ERROR_NOT_FOUND = "credentials_file_not_found"
GOOGLE_HEALTH_CREDENTIALS_ERROR_INVALID_JSON = "invalid_credentials_json"
GOOGLE_HEALTH_CREDENTIALS_ERROR_UNSUPPORTED_TYPE = "unsupported_credentials_type"
GOOGLE_HEALTH_CREDENTIALS_ERROR_MISSING_FIELD = "missing_credentials_field"


@dataclass(frozen=True)
class GoogleHealthCredentialsPreview:
    """
    Non-sensitive preview of Google Health OAuth credentials.

    This intentionally does not expose client secrets.
    """

    credentials_type: str
    client_id_configured: bool
    client_secret_configured: bool
    auth_uri: str
    token_uri: str
    redirect_uris: tuple[str, ...]


@dataclass(frozen=True)
class GoogleHealthOAuthCredentials:
    """
    Google OAuth web credentials loaded from credentials.json.

    The client secret is sensitive and must not be printed, returned from API
    responses, committed, or included in release packages.
    """

    client_id: str
    client_secret: str = field(repr=False)
    auth_uri: str
    token_uri: str
    redirect_uris: tuple[str, ...]
    project_id: str | None = None

    def to_preview(self) -> GoogleHealthCredentialsPreview:
        """Return a non-sensitive preview of loaded credentials."""

        return GoogleHealthCredentialsPreview(
            credentials_type="web",
            client_id_configured=bool(self.client_id),
            client_secret_configured=bool(self.client_secret),
            auth_uri=self.auth_uri,
            token_uri=self.token_uri,
            redirect_uris=self.redirect_uris,
        )


@dataclass(frozen=True)
class GoogleHealthCredentialsLoadResult:
    """
    Result of loading Google Health OAuth credentials.

    credentials may contain a client secret. Do not expose it through API
    responses or logs.
    """

    loaded: bool
    credentials_file: str | None
    credentials: GoogleHealthOAuthCredentials | None = None
    preview: GoogleHealthCredentialsPreview | None = None
    error: str | None = None
    message: str | None = None


def load_google_health_credentials(
    credentials_file: str | None,
) -> GoogleHealthCredentialsLoadResult:
    """
    Load Google OAuth web credentials from credentials.json.

    Relative paths are resolved from the backend root directory.
    """

    if not credentials_file:
        return GoogleHealthCredentialsLoadResult(
            loaded=False,
            credentials_file=None,
            credentials=None,
            preview=None,
            error=GOOGLE_HEALTH_CREDENTIALS_ERROR_NOT_CONFIGURED,
            message="Google Health credentials file is not configured.",
        )

    credentials_path = _resolve_credentials_path(credentials_file)

    if not credentials_path.exists():
        return GoogleHealthCredentialsLoadResult(
            loaded=False,
            credentials_file=str(credentials_path),
            credentials=None,
            preview=None,
            error=GOOGLE_HEALTH_CREDENTIALS_ERROR_NOT_FOUND,
            message="Google Health credentials file was not found.",
        )

    try:
        data = _read_json(credentials_path)
        credentials = parse_google_health_web_credentials(data)
    except json.JSONDecodeError:
        return GoogleHealthCredentialsLoadResult(
            loaded=False,
            credentials_file=str(credentials_path),
            credentials=None,
            preview=None,
            error=GOOGLE_HEALTH_CREDENTIALS_ERROR_INVALID_JSON,
            message="Google Health credentials file was not valid JSON.",
        )
    except ValueError as exc:
        return GoogleHealthCredentialsLoadResult(
            loaded=False,
            credentials_file=str(credentials_path),
            credentials=None,
            preview=None,
            error=str(exc),
            message="Google Health credentials file could not be loaded.",
        )

    return GoogleHealthCredentialsLoadResult(
        loaded=True,
        credentials_file=str(credentials_path),
        credentials=credentials,
        preview=credentials.to_preview(),
        error=None,
        message="Google Health credentials loaded.",
    )


def parse_google_health_web_credentials(
    data: dict[str, Any],
) -> GoogleHealthOAuthCredentials:
    """
    Parse Google OAuth `web` credentials.

    `installed` credentials are intentionally not accepted for the backend web
    OAuth route.
    """

    if "web" not in data:
        raise ValueError(GOOGLE_HEALTH_CREDENTIALS_ERROR_UNSUPPORTED_TYPE)

    web_data = data.get("web")

    if not isinstance(web_data, dict):
        raise ValueError(GOOGLE_HEALTH_CREDENTIALS_ERROR_UNSUPPORTED_TYPE)

    client_id = _require_string(web_data, "client_id")
    client_secret = _require_string(web_data, "client_secret")
    auth_uri = _require_string(web_data, "auth_uri")
    token_uri = _require_string(web_data, "token_uri")
    redirect_uris = _optional_string_list(web_data, "redirect_uris")

    return GoogleHealthOAuthCredentials(
        client_id=client_id,
        client_secret=client_secret,
        auth_uri=auth_uri,
        token_uri=token_uri,
        redirect_uris=tuple(redirect_uris),
        project_id=_optional_string(web_data, "project_id"),
    )


def _read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError(GOOGLE_HEALTH_CREDENTIALS_ERROR_INVALID_JSON)

    return data


def _resolve_credentials_path(credentials_file: str) -> Path:
    path = Path(credentials_file).expanduser()

    if path.is_absolute():
        return path

    return _backend_root() / path


def _backend_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _require_string(
    data: dict[str, Any],
    key: str,
) -> str:
    value = data.get(key)

    if not isinstance(value, str) or not value:
        raise ValueError(f"{GOOGLE_HEALTH_CREDENTIALS_ERROR_MISSING_FIELD}:{key}")

    return value


def _optional_string(
    data: dict[str, Any],
    key: str,
) -> str | None:
    value = data.get(key)

    if isinstance(value, str) and value:
        return value

    return None


def _optional_string_list(
    data: dict[str, Any],
    key: str,
) -> list[str]:
    value = data.get(key)

    if value is None:
        return []

    if not isinstance(value, list):
        return []

    return [
        item for item in value if isinstance(item, str) and item
    ]