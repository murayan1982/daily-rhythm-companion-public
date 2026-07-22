from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ENV = PROJECT_ROOT / "backend" / ".env"

SENSITIVE_KEYS = {
    "GEMINI_API_KEY",
    "GOOGLE_API_KEY",
    "XAI_API_KEY",
    "FITBIT_CLIENT_SECRET",
    "GOOGLE_HEALTH_EXPECTED_CLIENT_ID",
}


@dataclass(frozen=True)
class EnvCheckResult:
    errors: list[str]
    warnings: list[str]
    values: dict[str, str]


def _load_dotenv_values(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}

    if not path.exists():
        return values

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()

        if not line or line.startswith("#"):
            continue

        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        values[key] = value

    return values


def _value(values: dict[str, str], key: str, default: str = "") -> str:
    return values.get(key, default).strip()


def _is_enabled(values: dict[str, str], key: str) -> bool:
    return _value(values, key).lower() in {"1", "true", "yes", "on"}


def _is_set(values: dict[str, str], key: str) -> bool:
    return bool(_value(values, key))


def _add_if(
    errors: list[str],
    condition: bool,
    message: str,
) -> None:
    if condition:
        errors.append(message)


def _check_mock_safe(values: dict[str, str]) -> EnvCheckResult:
    errors: list[str] = []
    warnings: list[str] = []

    _add_if(
        errors,
        _value(values, "CONVERSATION_ENGINE", "mock").lower() != "mock",
        "CONVERSATION_ENGINE must be mock for mock-safe checks.",
    )
    _add_if(
        errors,
        _value(values, "SLEEP_PROVIDER", "mock").lower() != "mock",
        "SLEEP_PROVIDER must be mock for mock-safe checks.",
    )

    for key in (
        "GOOGLE_HEALTH_ENABLE_REAL_TOKEN_EXCHANGE",
        "GOOGLE_HEALTH_ENABLE_REAL_TOKEN_REFRESH",
        "GOOGLE_HEALTH_ENABLE_REAL_API_REQUESTS",
        "GOOGLE_HEALTH_REAL_API_OPT_IN",
        "GOOGLE_HEALTH_REAL_ENDPOINT_VERIFIED",
        "FITBIT_ENABLE_REAL_TOKEN_EXCHANGE",
    ):
        _add_if(errors, _is_enabled(values, key), f"{key} must be 0 for mock-safe.")

    if _is_set(values, "GEMINI_API_KEY"):
        warnings.append("GEMINI_API_KEY is set, but mock-safe does not need it.")
    if _is_set(values, "GOOGLE_API_KEY"):
        warnings.append("GOOGLE_API_KEY is set, but mock-safe does not need it.")
    if _is_set(values, "XAI_API_KEY"):
        warnings.append("XAI_API_KEY is set, but mock-safe does not need it.")

    if _is_set(values, "GEMINI_API_KEY") and _is_set(values, "GOOGLE_API_KEY"):
        warnings.append(
            "Both GEMINI_API_KEY and GOOGLE_API_KEY are set. "
            "Use only one to avoid provider precedence confusion."
        )

    return EnvCheckResult(errors=errors, warnings=warnings, values=values)


def _check_framework_local(values: dict[str, str]) -> EnvCheckResult:
    errors: list[str] = []
    warnings: list[str] = []

    _add_if(
        errors,
        _value(values, "CONVERSATION_ENGINE").lower() != "framework",
        "CONVERSATION_ENGINE must be framework for framework-local.",
    )

    has_framework_root = _is_set(values, "FRAMEWORK_ROOT") or _is_set(
        values,
        "FRAMEWORK_PROJECT_ROOT",
    )
    _add_if(
        errors,
        not has_framework_root,
        "FRAMEWORK_ROOT or FRAMEWORK_PROJECT_ROOT must be set for framework-local.",
    )

    _add_if(
        errors,
        _value(values, "FRAMEWORK_ADAPTER_MODE", "local_import").lower()
        != "local_import",
        "FRAMEWORK_ADAPTER_MODE must be local_import for framework-local.",
    )

    _add_if(
        errors,
        _value(values, "SLEEP_PROVIDER", "mock").lower() != "mock",
        "SLEEP_PROVIDER should be mock for framework-local checks.",
    )

    has_gemini = _is_set(values, "GEMINI_API_KEY") or _is_set(values, "GOOGLE_API_KEY")
    has_xai = _is_set(values, "XAI_API_KEY")

    _add_if(
        errors,
        not has_gemini and not has_xai,
        "At least one LLM API key must be set for framework-local.",
    )

    if _is_set(values, "GEMINI_API_KEY") and _is_set(values, "GOOGLE_API_KEY"):
        warnings.append(
            "Both GEMINI_API_KEY and GOOGLE_API_KEY are set. "
            "Prefer GEMINI_API_KEY in backend/.env and leave GOOGLE_API_KEY empty."
        )

    for key in (
        "GOOGLE_HEALTH_ENABLE_REAL_TOKEN_EXCHANGE",
        "GOOGLE_HEALTH_ENABLE_REAL_TOKEN_REFRESH",
        "GOOGLE_HEALTH_ENABLE_REAL_API_REQUESTS",
        "GOOGLE_HEALTH_REAL_API_OPT_IN",
        "GOOGLE_HEALTH_REAL_ENDPOINT_VERIFIED",
        "FITBIT_ENABLE_REAL_TOKEN_EXCHANGE",
    ):
        if _is_enabled(values, key):
            warnings.append(
                f"{key} is enabled during framework-local. "
                "Keep wearable real actions separate unless this is intentional."
            )

    return EnvCheckResult(errors=errors, warnings=warnings, values=values)


def _check_google_health_oauth(values: dict[str, str]) -> EnvCheckResult:
    errors: list[str] = []
    warnings: list[str] = []

    _add_if(
        errors,
        _value(values, "CONVERSATION_ENGINE", "mock").lower() != "mock",
        "CONVERSATION_ENGINE should be mock during Google Health OAuth token exchange.",
    )
    _add_if(
        errors,
        _value(values, "SLEEP_PROVIDER", "google_health").lower() != "google_health",
        "SLEEP_PROVIDER must be google_health during Google Health OAuth token exchange.",
    )
    _add_if(
        errors,
        not _is_enabled(values, "GOOGLE_HEALTH_ENABLE_REAL_TOKEN_EXCHANGE"),
        "GOOGLE_HEALTH_ENABLE_REAL_TOKEN_EXCHANGE must be 1 for oauth-token-exchange.",
    )
    _add_if(
        errors,
        _is_enabled(values, "GOOGLE_HEALTH_ENABLE_REAL_TOKEN_REFRESH"),
        "GOOGLE_HEALTH_ENABLE_REAL_TOKEN_REFRESH must stay 0 during OAuth token exchange.",
    )
    _add_if(
        errors,
        _is_enabled(values, "GOOGLE_HEALTH_ENABLE_REAL_API_REQUESTS"),
        "GOOGLE_HEALTH_ENABLE_REAL_API_REQUESTS must stay 0 during OAuth token exchange.",
    )
    _add_if(
        errors,
        _is_enabled(values, "GOOGLE_HEALTH_REAL_API_OPT_IN"),
        "GOOGLE_HEALTH_REAL_API_OPT_IN must stay 0 during OAuth token exchange.",
    )
    _add_if(
        errors,
        _is_enabled(values, "GOOGLE_HEALTH_REAL_ENDPOINT_VERIFIED"),
        "GOOGLE_HEALTH_REAL_ENDPOINT_VERIFIED must stay 0 during OAuth token exchange.",
    )

    if not _is_set(values, "GOOGLE_HEALTH_CREDENTIALS_FILE"):
        warnings.append("GOOGLE_HEALTH_CREDENTIALS_FILE is not set.")
    if not _is_set(values, "GOOGLE_HEALTH_REDIRECT_URI"):
        warnings.append("GOOGLE_HEALTH_REDIRECT_URI is not set.")

    return EnvCheckResult(errors=errors, warnings=warnings, values=values)


def _check_google_health_real_api(values: dict[str, str]) -> EnvCheckResult:
    errors: list[str] = []
    warnings: list[str] = []

    _add_if(
        errors,
        _value(values, "CONVERSATION_ENGINE", "mock").lower() != "mock",
        "CONVERSATION_ENGINE should be mock during guarded real Google Health API checks.",
    )
    _add_if(
        errors,
        _value(values, "SLEEP_PROVIDER", "google_health").lower() != "google_health",
        "SLEEP_PROVIDER must be google_health for guarded real Google Health API checks.",
    )
    _add_if(
        errors,
        _is_enabled(values, "GOOGLE_HEALTH_ENABLE_REAL_TOKEN_EXCHANGE"),
        "GOOGLE_HEALTH_ENABLE_REAL_TOKEN_EXCHANGE must be 0 for guarded-real-api; run token exchange separately.",
    )

    for key in (
        "GOOGLE_HEALTH_ENABLE_REAL_TOKEN_REFRESH",
        "GOOGLE_HEALTH_ENABLE_REAL_API_REQUESTS",
        "GOOGLE_HEALTH_REAL_API_OPT_IN",
        "GOOGLE_HEALTH_REAL_ENDPOINT_VERIFIED",
    ):
        _add_if(
            errors,
            not _is_enabled(values, key),
            f"{key} must be 1 for guarded-real-api.",
        )

    _add_if(
        errors,
        not _is_set(values, "GOOGLE_HEALTH_CREDENTIALS_FILE"),
        "GOOGLE_HEALTH_CREDENTIALS_FILE must be set.",
    )
    _add_if(
        errors,
        not _is_set(values, "GOOGLE_HEALTH_API_BASE_URL"),
        "GOOGLE_HEALTH_API_BASE_URL must be set.",
    )
    _add_if(
        errors,
        not _is_set(values, "GOOGLE_HEALTH_SLEEP_API_PATH"),
        "GOOGLE_HEALTH_SLEEP_API_PATH must be set.",
    )

    if _is_set(values, "GEMINI_API_KEY") or _is_set(values, "GOOGLE_API_KEY") or _is_set(values, "XAI_API_KEY"):
        warnings.append(
            "LLM API key values are set during guarded-real-api. "
            "They are not required for Google Health real API verification."
        )

    return EnvCheckResult(errors=errors, warnings=warnings, values=values)


def _redacted_summary(values: dict[str, str]) -> list[str]:
    keys = [
        "CONVERSATION_ENGINE",
        "SLEEP_PROVIDER",
        "FRAMEWORK_ROOT",
        "FRAMEWORK_PROJECT_ROOT",
        "FRAMEWORK_ADAPTER_MODE",
        "GEMINI_API_KEY",
        "GOOGLE_API_KEY",
        "XAI_API_KEY",
        "GOOGLE_HEALTH_ENABLE_REAL_TOKEN_EXCHANGE",
        "GOOGLE_HEALTH_ENABLE_REAL_TOKEN_REFRESH",
        "GOOGLE_HEALTH_ENABLE_REAL_API_REQUESTS",
        "GOOGLE_HEALTH_REAL_API_OPT_IN",
        "GOOGLE_HEALTH_REAL_ENDPOINT_VERIFIED",
        "FITBIT_ENABLE_REAL_TOKEN_EXCHANGE",
    ]

    lines: list[str] = []

    for key in keys:
        if key in SENSITIVE_KEYS or key.endswith("_KEY") or key.endswith("_SECRET"):
            lines.append(f"{key}: set={_is_set(values, key)}")
        else:
            lines.append(f"{key}: {_value(values, key, '<unset>') or '<empty>'}")

    return lines


def _run(profile: str, env_path: Path) -> int:
    values = _load_dotenv_values(env_path)

    if not env_path.exists():
        print(f"[env-profile-check] env_path={env_path}")
        print("[env-profile-check] ERROR: backend/.env was not found.")
        print("Create it from backend/env_profiles/mock_safe.env or backend/.env.example.")
        return 1

    checkers = {
        "mock-safe": _check_mock_safe,
        "framework-local": _check_framework_local,
        "google-health-oauth": _check_google_health_oauth,
        "google-health-real-api": _check_google_health_real_api,
    }

    checker = checkers[profile]
    result = checker(values)

    print("[env-profile-check]")
    print(f"profile={profile}")
    print(f"env_path={env_path}")
    print("summary:")
    for line in _redacted_summary(values):
        print(f"- {line}")

    if result.warnings:
        print("warnings:")
        for warning in result.warnings:
            print(f"- {warning}")

    if result.errors:
        print("errors:")
        for error in result.errors:
            print(f"- {error}")
        print("[env-profile-check] FAILED")
        return 1

    print("[env-profile-check] OK")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--profile",
        choices=[
            "mock-safe",
            "framework-local",
            "google-health-oauth",
            "google-health-real-api",
        ],
        default="mock-safe",
    )
    parser.add_argument(
        "--env-path",
        type=Path,
        default=BACKEND_ENV,
    )

    args = parser.parse_args()
    return _run(profile=args.profile, env_path=args.env_path)


if __name__ == "__main__":
    raise SystemExit(main())
