"""Public-safe W-5a Fitbit operator environment preflight.

Default mode and ``--check-example`` are credential-free and network-free.
``--env-file`` reads a private KEY=VALUE file but prints only key names and
allow-listed boolean/status markers, never values or the supplied path.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_ENV = ROOT / "backend/env_profiles/fitbit_real_operator.env.example"

REQUIRED_EXACT = {
    "CONVERSATION_ENGINE": "mock",
    "SLEEP_PROVIDER": "fitbit",
    "FITBIT_ENABLE_REAL_TOKEN_EXCHANGE": "1",
    "FITBIT_DEV_SAVE_DUMMY_TOKEN": "0",
}
REQUIRED_PRIVATE = {
    "FITBIT_CLIENT_ID",
    "FITBIT_CLIENT_SECRET",
    "FITBIT_REDIRECT_URI",
}
OPTIONAL_KEYS = {
    "WEB_CORS_ORIGINS",
    "FITBIT_OAUTH_STATE_TTL_SECONDS",
}
ALLOWED_KEYS = set(REQUIRED_EXACT) | REQUIRED_PRIVATE | OPTIONAL_KEYS
FORBIDDEN_KEYS = {
    "FITBIT_ACCESS_TOKEN",
    "FITBIT_REFRESH_TOKEN",
    "FITBIT_AUTHORIZATION_CODE",
    "FITBIT_OAUTH_STATE",
    "AUTHORIZATION",
    "GOOGLE_API_KEY",
    "GEMINI_API_KEY",
    "OPENAI_API_KEY",
    "XAI_API_KEY",
    "FRAMEWORK_ROOT",
    "FRAMEWORK_PROJECT_ROOT",
    "GOOGLE_HEALTH_CREDENTIALS_FILE",
    "GOOGLE_HEALTH_ACCESS_TOKEN",
    "GOOGLE_HEALTH_REFRESH_TOKEN",
}
PLACEHOLDER_MARKERS = ("<", ">", "change_me", "replace_me")


@dataclass(frozen=True)
class ValidationResult:
    status: str
    accepted_keys: tuple[str, ...]
    missing_or_invalid_keys: tuple[str, ...]
    forbidden_keys_present: tuple[str, ...]
    unknown_keys_present: tuple[str, ...]
    public_safe: bool


def parse_env_file(path: Path) -> dict[str, str]:
    env: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise ValueError("invalid KEY=VALUE line")
        key, value = line.split("=", 1)
        key = key.strip()
        if not key or not key.replace("_", "A").isalnum() or key.upper() != key:
            raise ValueError("invalid environment key name")
        env[key] = value.strip()
    return env


def _is_placeholder(value: str) -> bool:
    lowered = value.strip().lower()
    return not lowered or any(marker in lowered for marker in PLACEHOLDER_MARKERS)


def _redirect_uri_is_valid(value: str, *, allow_placeholder: bool) -> bool:
    if _is_placeholder(value):
        return allow_placeholder
    parsed = urlparse(value)
    return (
        parsed.scheme in {"http", "https"}
        and bool(parsed.netloc)
        and parsed.path.rstrip("/") == "/fitbit/callback"
        and not parsed.fragment
    )


def validate_env(env: dict[str, str], *, allow_placeholders: bool) -> ValidationResult:
    invalid: list[str] = []

    for key, expected in REQUIRED_EXACT.items():
        if env.get(key) != expected:
            invalid.append(key)

    for key in sorted(REQUIRED_PRIVATE):
        value = env.get(key, "")
        if key == "FITBIT_REDIRECT_URI":
            valid = _redirect_uri_is_valid(value, allow_placeholder=allow_placeholders)
        elif allow_placeholders:
            valid = bool(value)
        else:
            valid = not _is_placeholder(value)
        if not valid:
            invalid.append(key)

    ttl = env.get("FITBIT_OAUTH_STATE_TTL_SECONDS")
    if ttl is not None:
        try:
            ttl_value = int(ttl)
        except ValueError:
            ttl_value = 0
        if ttl_value <= 0:
            invalid.append("FITBIT_OAUTH_STATE_TTL_SECONDS")

    forbidden = sorted(FORBIDDEN_KEYS.intersection(env))
    unknown = sorted(set(env) - ALLOWED_KEYS)
    accepted = sorted(set(env) & ALLOWED_KEYS)
    public_safe = not forbidden and not unknown
    status = "accepted" if not invalid and public_safe else "rejected"

    return ValidationResult(
        status=status,
        accepted_keys=tuple(accepted),
        missing_or_invalid_keys=tuple(sorted(set(invalid))),
        forbidden_keys_present=tuple(forbidden),
        unknown_keys_present=tuple(unknown),
        public_safe=public_safe,
    )


def _print_contract() -> None:
    print("v210_fitbit_real_operator_preflight_status: contract-ready")
    print("v210_fitbit_real_operator_preflight_small_commit: W-5a")
    print("v210_fitbit_real_operator_preflight_parent_phase: W-5-current-not-completed")
    print("v210_fitbit_real_operator_preflight_mock_safe_default: True")
    print("v210_fitbit_real_operator_preflight_network_request: False")
    print("v210_fitbit_real_operator_preflight_oauth_browser: False")
    print("v210_fitbit_real_operator_preflight_real_operator_execution: False")
    print("v210_fitbit_real_operator_preflight_release_records_changed: False")


def _print_validation(prefix: str, result: ValidationResult) -> None:
    print(f"{prefix}_status: {result.status}")
    print(f"{prefix}_accepted_keys: {','.join(result.accepted_keys)}")
    print(
        f"{prefix}_missing_or_invalid_keys: "
        f"{','.join(result.missing_or_invalid_keys)}"
    )
    print(
        f"{prefix}_forbidden_keys_present: "
        f"{','.join(result.forbidden_keys_present)}"
    )
    print(
        f"{prefix}_unknown_keys_present: "
        f"{','.join(result.unknown_keys_present)}"
    )
    print(f"{prefix}_public_safe: {result.public_safe}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate public-safe Fitbit W-5 operator env markers."
    )
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--check-example", action="store_true")
    args = parser.parse_args()

    _print_contract()

    if args.check_example:
        try:
            env = parse_env_file(EXAMPLE_ENV)
        except (OSError, ValueError) as exc:
            print(
                "v210_fitbit_real_operator_preflight_example_error: "
                + exc.__class__.__name__
            )
            return 1
        result = validate_env(env, allow_placeholders=True)
        _print_validation("v210_fitbit_real_operator_preflight_example", result)
        if result.status != "accepted":
            return 1

    if args.env_file is not None:
        try:
            env = parse_env_file(args.env_file)
        except (OSError, ValueError) as exc:
            print(
                "v210_fitbit_real_operator_preflight_env_file_error: "
                + exc.__class__.__name__
            )
            return 1
        result = validate_env(env, allow_placeholders=False)
        _print_validation("v210_fitbit_real_operator_preflight_env_file", result)
        if result.status != "accepted":
            return 1

    print("[v210-fitbit-real-operator-preflight] OK")
    print(
        "No Fitbit network request, OAuth browser, token value output, raw payload "
        "inspection, smartphone Web acceptance, release build, or tag change was performed."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
