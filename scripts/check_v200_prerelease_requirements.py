"""Check that v2.0.0 pre-release requirements are explicit in public docs."""

from __future__ import annotations

from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app.services.framework_v200_prerelease_requirements import (
    build_v200_prerelease_requirements,
    render_v200_prerelease_requirements,
)


def read(path: str) -> str:
    target = ROOT / path
    if not target.exists():
        raise AssertionError(f"Missing required file: {path}")
    return target.read_text(encoding="utf-8")


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise AssertionError(f"Missing {label}: {needle!r}")


def assert_no_obvious_secrets(path: str, text: str) -> None:
    forbidden_patterns = [
        r"sk-[A-Za-z0-9_\-]{12,}",
        r"AIza[0-9A-Za-z_\-]{20,}",
        r"xai-[A-Za-z0-9_\-]{12,}",
        r"Bearer\s+[A-Za-z0-9_\-\.]{12,}",
        r"Authorization:\s*Bearer",
        r"refresh_token\s*[:=]\s*['\"][^'\"]+",
        r"access_token\s*[:=]\s*['\"][^'\"]+",
        r"client_secret\s*[:=]\s*['\"][^'\"]+",
        r"[A-Za-z]:\\Users\\",
        r"[A-Za-z]:[\\/](?:[^\\/\\r\\n]+[\\/]){2,}DailyRhythmCompanion",
        r"192\.168\.0\.94",
    ]
    sanitized = text.replace("http://<PC_LAN_IP>:8000", "").replace(
        "http://<PC_LAN_IP>:18080", ""
    )
    for pattern in forbidden_patterns:
        if re.search(pattern, sanitized, flags=re.IGNORECASE):
            raise AssertionError(f"Sensitive-looking value found in {path}: {pattern}")


def run_smoke() -> str:
    result = build_v200_prerelease_requirements()
    output = render_v200_prerelease_requirements(result)
    require(output, "v200_prerelease_requirements_status: documented-pending-before-v2.0.0", "v2 prerelease rendered status")
    return output


def main() -> None:
    smoke_output = run_smoke()

    files = {
        "README.md": read("README.md"),
        "roadmap.md": read("roadmap.md"),
        "scripts/README.md": read("scripts/README.md"),
        "docs/v2_prerelease_requirements.md": read("docs/v2_prerelease_requirements.md"),
        "release_notes/v1.9.0.md": read("release_notes/v1.9.0.md"),
        "backend/app/services/framework_v200_prerelease_requirements.py": read("backend/app/services/framework_v200_prerelease_requirements.py"),
        "scripts/smoke_framework_v200_prerelease_requirements.py": read("scripts/smoke_framework_v200_prerelease_requirements.py"),
    }

    required_markers = [
        "v2.0.0 pre-release requirements",
        "real LLM API",
        "Web上で回答",  # README/roadmap may use Japanese wording for the user-facing requirement.
        "real TTS API",
        "Web上で音声出力",
        "real Google Health API",
        "実睡眠データ",
        "Web image display",
        "画像を用いて",
        "public-repo-ready as an AI Character Framework demo app",
        "LICENSE",
        "explicit release requirements",
    ]

    # The canonical requirements doc must contain every exact concept.
    doc = files["docs/v2_prerelease_requirements.md"]
    for needle in [
        "v200_prerelease_requirement_real_llm_web_answer: required",
        "v200_prerelease_requirement_real_tts_web_audio_output: required",
        "v200_prerelease_requirement_real_google_health_sleep_data: required",
        "v200_prerelease_requirement_web_image_display: required",
        "v200_prerelease_requirement_public_repo_ready_fw_demo_app: required",
        "v200_prerelease_requirement_explicit_release_requirements: required",
        "v190_release_scope: fw40-smartphone-web-public-demo-evidence",
        "v190_v200_prerelease_requirements_status: documented-pending",
    ]:
        require(doc, needle, "v2 prerelease requirements doc")

    # Public index docs must link or name the requirement doc and list the six gates.
    for path in ["README.md", "roadmap.md"]:
        text = files[path]
        for needle in [
            "docs/v2_prerelease_requirements.md",
            "real LLM API",
            "real TTS API",
            "real Google Health API",
            "Web image display",
            "public-repo-ready as an AI Character Framework demo app",
            "explicit release requirements",
        ]:
            require(text, needle, f"{path} v2 prerelease requirements")

    # Release docs must make clear that v1.9.0 is not the v2.0.0 completion gate.
    for path in [
        "release_notes/v1.9.0.md",
    ]:
        text = files[path]
        for needle in [
            "v2.0.0 pre-release requirements",
            "documented-pending-before-v2.0.0",
            "v1.9.0 is not a general consumer/app-store release",
            "docs/v2_prerelease_requirements.md",
        ]:
            require(text, needle, f"{path} release scope correction")

    scripts_readme = files["scripts/README.md"]
    for needle in [
        "scripts/check_v200_prerelease_requirements.py",
        "scripts/smoke_framework_v200_prerelease_requirements.py",
        "v200_prerelease_requirements_status: documented-pending-before-v2.0.0",
    ]:
        require(scripts_readme, needle, "scripts README v2 prerelease checks")

    service = files["backend/app/services/framework_v200_prerelease_requirements.py"]
    for needle in [
        "build_v200_prerelease_requirements",
        "render_v200_prerelease_requirements",
        "real_llm_web_answer",
        "real_tts_web_audio_output",
        "real_google_health_sleep_data",
        "web_image_display",
        "public_repo_ready_fw_demo_app",
        "explicit_release_requirements",
    ]:
        require(service, needle, "v2 prerelease service")

    for needle in [
        "v200_prerelease_requirements_status: documented-pending-before-v2.0.0",
        "v200_prerelease_requirements_remaining_required_count: 6",
        "v200_prerelease_requirement_real_llm_web_answer: required-before-v2.0.0",
        "v200_prerelease_requirement_real_tts_web_audio_output: required-before-v2.0.0",
        "v200_prerelease_requirement_real_google_health_sleep_data: required-before-v2.0.0",
        "v200_prerelease_requirement_web_image_display: required-before-v2.0.0",
        "v200_prerelease_requirement_public_repo_ready_fw_demo_app: required-before-v2.0.0",
        "v200_prerelease_requirement_explicit_release_requirements: required-before-v2.0.0",
    ]:
        require(smoke_output, needle, "v2 prerelease smoke output")

    for path, text in files.items():
        assert_no_obvious_secrets(path, text)
    assert_no_obvious_secrets("v2 prerelease smoke output", smoke_output)

    print("[v200-prerelease-requirements-check] OK")


if __name__ == "__main__":
    main()
