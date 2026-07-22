"""Validate Daily Rhythm Companion release zip contents.

Usage:
    python scripts/check_release_package.py release/DailyRhythmCompanion_xxx.zip

The check is intentionally conservative. It rejects secrets, local token stores,
cache files, local env profiles, patch/diff bundles, vendored dependencies,
nested release outputs, internal development logs, handoff prompts, root
replacement-bundle notes, day-by-day check scripts that should stay in the
source repository only, and public text files containing control characters,
private local-machine path literals, or non-placeholder secret assignments.
"""

from __future__ import annotations

import fnmatch
import re
import sys
import zipfile
from pathlib import PurePosixPath


BLOCKED_BASENAMES = {
    ".git",
    ".env",
    "credentials.json",
    "google_health_tokens.json",
    "google_health_oauth_state.json",
    "fitbit_tokens.json",
    "fitbit_oauth_state.json",
    "DailyRhythmCompanion_handoff_v0_15_0.md",
    "release_final_check_v0_16_0_day4.md",
    "release_package_check_result_v0_16_0_day3.md",
    "public_release_checklist.md",
    "DRC_v190_Day22_handoff.md",
    "DRC_v190_next_thread_prompt.md",
    "DRC_v200_goal_checklist_small_commit_CommitC_ACCEPTED.md",
    "README_B0_APPLY.md",
    "PATCH_SUMMARY.md",
    "VERIFICATION_SUMMARY.txt",
    "IMPLEMENTATION_NOTES.txt",
    "LOCAL_VALIDATION_RESULT.txt",
    "README_LOCAL_ONLY.txt",
}

BLOCKED_PARTS = {
    ".git",
    "__pycache__",
    "local_data",
    "operator_evidence",
    "release",
    "vendor",
    "repo_files",
    "optional_replacements",
    ".dart_tool",
    "build",
    "coverage",
    "_local",
    ".release_build",
}

BLOCKED_SUFFIXES = {
    ".pyc",
    ".pyo",
    ".log",
    ".patch",
    ".diff",
    ".tmp",
    ".bak",
    ".swp",
    ".swo",
    ".sqlite",
    ".sqlite3",
    ".db",
}


BLOCKED_NORMALIZED_EXACT_PATHS = {
    "app/android/app/src/main/java/io/flutter/plugins/generatedpluginregistrant.java",
    "app/ios/runner/generatedpluginregistrant.h",
    "app/ios/runner/generatedpluginregistrant.m",
    "app/linux/flutter/generated_plugin_registrant.cc",
    "app/linux/flutter/generated_plugin_registrant.h",
    "app/linux/flutter/generated_plugins.cmake",
    "app/windows/flutter/generated_plugin_registrant.cc",
    "app/windows/flutter/generated_plugin_registrant.h",
    "app/windows/flutter/generated_plugins.cmake",
}

BLOCKED_NORMALIZED_PATTERNS = {
    "docs/internal/*",
    "CHANGE_SUMMARY*",
    "day*_validation.txt",
    "DAY*.md",
    "DOC_UPDATE_BUNDLE*.md",
    "README_v*_day*.md",
    "scripts/check_v*_day*.py",
    "scripts/check_env_profile_v*_day*.py",
    "scripts/check_v190_smartphone_web_fw_demo_day*.py",
}

TEXT_FILE_SUFFIXES = {
    ".bat",
    ".css",
    ".dart",
    ".env",
    ".gradle",
    ".html",
    ".iml",
    ".json",
    ".kt",
    ".kts",
    ".md",
    ".plist",
    ".properties",
    ".ps1",
    ".py",
    ".swift",
    ".toml",
    ".txt",
    ".xcconfig",
    ".xml",
    ".yaml",
    ".yml",
}

TEXT_FILE_BASENAMES = {
    ".gitignore",
    "gradlew",
}

SENSITIVE_TEXT_PATTERNS = {
    "private Windows user path": r"[A-Za-z]:[\\/]Users[\\/]",
    "private DRC work path": r"[A-Za-z]:[\\/](?:[^\\/\r\n]+[\\/]){2,}DailyRhythmCompanion",
    "private LAN IP literal": r"\b(?:10\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+|172\.(?:1[6-9]|2\d|3[0-1])\.\d+\.\d+)\b",
}

ALLOWED_CONTROL_CHARS = {"\t", "\n", "\r"}

ALLOWED_ENV_TEMPLATE_BASENAMES = {
    ".env.example",
    ".env.sample",
    ".env.template",
}

SENSITIVE_ENV_KEY_FRAGMENTS = (
    "API_KEY",
    "CLIENT_SECRET",
    "PRIVATE_KEY",
    "PASSWORD",
    "SECRET",
    "VOICE_ID",
    "MODEL_ID",
)

NON_SECRET_TOKEN_KEY_FRAGMENTS = (
    "ENABLE",
    "_URL",
    "_PATH",
    "_FILE",
    "_TTL",
    "_EXPIR",
)

SAFE_SECRET_PLACEHOLDER_VALUES = {
    "",
    "0",
    "false",
    "none",
    "null",
    "disabled",
    "placeholder",
    "replace_me",
    "replace-me",
    "changeme",
    "change-me",
    "example",
}

# Directories named "build" are blocked only under app/ or platform build output.
# A source file such as advice_prompt_builder.py must not be blocked just because
# its filename contains the word "builder".
BUILD_ALLOWED_PATH_FRAGMENTS = {
    "backend/app/services/advice_prompt_builder.py",
}


def _strip_root(zip_name: str) -> str:
    """Return a normalized path without the top-level package directory."""
    path = PurePosixPath(zip_name.replace("\\", "/"))
    parts = path.parts
    if len(parts) > 1 and parts[0].startswith("DailyRhythmCompanion"):
        return "/".join(parts[1:])
    return "/".join(parts)


def _is_blocked(zip_name: str) -> str | None:
    normalized = _strip_root(zip_name).strip("/")
    if not normalized:
        return None

    path = PurePosixPath(normalized)
    parts = set(path.parts)
    basename = path.name
    lower_basename = basename.lower()

    if lower_basename.endswith(".local.env"):
        return f"blocked local env profile: {basename}"

    if (
        lower_basename.startswith(".env.")
        and lower_basename not in ALLOWED_ENV_TEMPLATE_BASENAMES
    ):
        return f"blocked local env variant: {basename}"

    if basename in BLOCKED_BASENAMES:
        return f"blocked basename: {basename}"

    if normalized.lower() in BLOCKED_NORMALIZED_EXACT_PATHS:
        return f"blocked untracked Flutter generated file: {normalized}"

    for pattern in BLOCKED_NORMALIZED_PATTERNS:
        if fnmatch.fnmatch(normalized.lower(), pattern.lower()):
            return f"blocked release-surface pattern: {pattern}"

    if path.suffix in BLOCKED_SUFFIXES:
        return f"blocked suffix: {path.suffix}"

    blocked_parts = parts & BLOCKED_PARTS
    if blocked_parts:
        # Keep the rule readable and avoid accidental false positives.
        blocked = sorted(blocked_parts)[0]
        if normalized in BUILD_ALLOWED_PATH_FRAGMENTS:
            return None
        return f"blocked path part: {blocked}"

    return None


def _is_text_file(zip_name: str) -> bool:
    normalized = _strip_root(zip_name).strip("/")
    if not normalized:
        return False

    path = PurePosixPath(normalized)
    lower_basename = path.name.lower()
    return (
        path.suffix in TEXT_FILE_SUFFIXES
        or path.name in TEXT_FILE_BASENAMES
        or lower_basename.endswith(".env")
        or ".env." in lower_basename
    )


def _check_text_content(zip_name: str, data: bytes) -> str | None:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return "text file is not valid UTF-8"

    for char in text:
        if ord(char) < 32 and char not in ALLOWED_CONTROL_CHARS:
            return f"text file contains control character U+{ord(char):04X}"

    sanitized = text.replace("http://<PC_LAN_IP>:8000", "").replace(
        "http://<PC_LAN_IP>:18080", ""
    )
    for label, pattern in SENSITIVE_TEXT_PATTERNS.items():
        if re.search(pattern, sanitized, flags=re.IGNORECASE):
            return f"text file contains sensitive-looking value: {label}"

    env_reason = _check_sensitive_env_assignments(zip_name, text)
    if env_reason:
        return env_reason

    return None


def _is_sensitive_env_key(key: str) -> bool:
    upper_key = key.upper()
    if any(fragment in upper_key for fragment in SENSITIVE_ENV_KEY_FRAGMENTS):
        return True
    if "TOKEN" not in upper_key:
        return False
    return not any(fragment in upper_key for fragment in NON_SECRET_TOKEN_KEY_FRAGMENTS)


def _check_sensitive_env_assignments(zip_name: str, text: str) -> str | None:
    normalized = _strip_root(zip_name).strip("/")
    basename = PurePosixPath(normalized).name.lower()
    if not (basename.endswith(".env") or ".env." in basename):
        return None

    assignment_re = re.compile(
        r"^\s*(?:export\s+|\$env:)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?)\s*$"
    )
    for raw_line in text.splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        match = assignment_re.match(raw_line)
        if not match:
            continue

        key, raw_value = match.groups()
        if not _is_sensitive_env_key(key):
            continue

        value = raw_value.split(" #", 1)[0].strip().strip('"').strip("'")
        lower_value = value.lower()
        placeholder = (
            lower_value in SAFE_SECRET_PLACEHOLDER_VALUES
            or (value.startswith("<") and value.endswith(">"))
            or (value.startswith("${") and value.endswith("}"))
            or (value.startswith("%") and value.endswith("%"))
            or (bool(value) and set(value) <= {"*"})
            or lower_value.startswith("your_")
            or lower_value.startswith("your-")
        )
        if not placeholder:
            return f"env-like file contains non-placeholder sensitive assignment: {key}"

    return None


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python scripts/check_release_package.py <release-zip>")
        return 2

    zip_path = sys.argv[1]
    failures: list[tuple[str, str]] = []

    with zipfile.ZipFile(zip_path) as package:
        for name in package.namelist():
            reason = _is_blocked(name)
            if reason:
                failures.append((name, reason))
                continue

            if _is_text_file(name):
                text_reason = _check_text_content(name, package.read(name))
                if text_reason:
                    failures.append((name, text_reason))

    if failures:
        print("[release-package-check] NG")
        for name, reason in failures:
            print(f"- {name} ({reason})")
        return 1

    print("[release-package-check] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
