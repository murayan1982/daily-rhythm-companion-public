"""Verify D-next-18 public-safe real TTS Web audio acceptance synchronization.

This source-tree check reads committed documentation markers only. It does not
call providers, call AI Character Framework voice output, start the DRC backend,
open Flutter Web, play audio, inspect screenshots, read operator evidence, or
build release artifacts.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

_CHECKLIST_PATH = ROOT / "docs/DRC_v200_goal_checklist_small_commit.md"
_ACCEPTANCE_DOC_PATH = ROOT / "docs/v200_real_tts_web_audio_acceptance_evidence.md"
_ROADMAP_PATH = ROOT / "roadmap.md"
_SCRIPTS_README_PATH = ROOT / "scripts/README.md"

_ACCEPTANCE_SCOPE = "commit_scope: Commit D-next-18 only"
_ACCEPTANCE_REQUIRED_SNIPPETS = (
    "implementation_status: real-tts-web-audio-acceptance-public-safe-synchronized",
    "accepted_requirement_key: real_tts_web_audio_output",
    "actual_drc_backend_api_status: confirmed",
    "pc_web_audible_playback_status: confirmed",
    "smartphone_web_audible_playback_status: confirmed",
    "day54_output_evidence_status: accepted",
    "day65_execution_evidence_status: accepted",
    "day65_requirement_satisfied: True",
    "day77_screenshot_evidence_status: accepted",
    "day77_public_safe: True",
    "combined_acceptance_status: accepted",
    "combined_requirement_satisfied: True",
    "real_google_health_sleep_data: NOT_ACCEPTED",
    "accepted_private_evidence_manifest: NOT_ACCEPTED",
    "final_fixed_release_zip: not-built",
    "DRC_v2.0.0_tag: not-created",
    "release_completion_status: NOT_RELEASED",
    "real_tts_web_audio_output: ACCEPTED",
)
_PRIVATE_SAFETY_SNIPPET = (
    "private_evidence_policy: raw audio, screenshots, provider payloads, secrets, URLs, "
    "LAN IPs, private paths, and operator evidence files remain uncommitted"
)
_TTS_CHECKLIST_ITEMS = (
    "Real TTS provider / FW voice output path is configured with private environment variables only.",
    "The Web UI / smartphone Web UI calls the actual DRC backend API.",
    "Real TTS audio is generated.",
    "Audio playback is confirmed from the Web UI.",
    "The Web UI visibly shows the TTS/audio output result.",
    "A screenshot of the Web UI audio output/result is captured.",
    "The screenshot reference is recorded in private operator evidence.",
    "Raw audio, raw provider payload, API key, token, and private paths are not committed.",
    "Mock, fallback, skipped, unavailable, silent output, or placeholder output is not counted as success.",
)
_FORBIDDEN_ACCEPTANCE_BLOCK_TOKENS = (
    "http://",
    "https://",
    "file://",
    "localhost",
    "127.0.0.1",
    "\\operator_evidence\\",
    "/operator_evidence/",
    "ELEVENLABS_API_KEY",
    "OPENAI_API_KEY",
    "GEMINI_API_KEY",
    "XAI_API_KEY",
)


def main() -> int:
    print("[smoke-framework-v200-real-tts-web-audio-acceptance-sync] RESULT")

    if not _check_required_files():
        return 1
    if not _check_checklist_source_of_truth():
        return 1
    if not _check_tts_definition_of_done():
        return 1
    if not _check_public_safe_acceptance_blocks():
        return 1
    if not _check_unresolved_release_gates():
        return 1
    if not _check_roadmap_sync():
        return 1
    if not _check_scripts_readme_sync():
        return 1
    if not _check_gitignore_boundary():
        return 1

    print("v200_real_tts_web_audio_acceptance_sync_status: accepted")
    print("v200_real_tts_web_audio_acceptance_sync_public_safe: True")
    print("v200_real_tts_web_audio_acceptance_sync_requirement_satisfied: True")
    print("v200_real_tts_web_audio_acceptance_sync_remaining_release_status: NOT_RELEASED")
    print("[smoke-framework-v200-real-tts-web-audio-acceptance-sync] OK")
    print(
        "No provider call, FW voice output call, backend/Web startup, audio playback, "
        "screenshot inspection, private evidence read, fixed zip build, or tag creation was performed."
    )
    return 0


def _check_required_files() -> bool:
    paths = (_CHECKLIST_PATH, _ACCEPTANCE_DOC_PATH, _ROADMAP_PATH, _SCRIPTS_README_PATH)
    missing = [str(path.relative_to(ROOT)) for path in paths if not path.exists()]
    if missing:
        print(
            "[smoke-framework-v200-real-tts-web-audio-acceptance-sync] ERROR: "
            "missing required files: " + ",".join(missing)
        )
        return False
    print("v200_real_tts_web_audio_acceptance_sync_required_files: present")
    return True


def _check_checklist_source_of_truth() -> bool:
    legacy_path = ROOT / "DRC_v200_goal_checklist_small_commit.md"
    if legacy_path.exists():
        return _error("legacy root checklist copy still exists")
    print("v200_real_tts_web_audio_acceptance_sync_checklist_source_of_truth: docs-only")
    return True


def _extract_section(text: str, start_marker: str, end_marker: str) -> str:
    start = text.find(start_marker)
    if start < 0:
        return ""
    end = text.find(end_marker, start)
    if end < 0:
        return ""
    return text[start:end]


def _extract_commit_block(text: str) -> str:
    start = text.find(_ACCEPTANCE_SCOPE)
    if start < 0:
        return ""
    end = text.find("```", start)
    if end < 0:
        return ""
    return text[start:end]


def _check_tts_definition_of_done() -> bool:
    text = _CHECKLIST_PATH.read_text(encoding="utf-8")
    section = _extract_section(
        text,
        "### 2.2 Real TTS Web audio output evidence",
        "### 2.3 Real Google Health sleep data evidence",
    )
    if not section:
        print(
            "[smoke-framework-v200-real-tts-web-audio-acceptance-sync] ERROR: "
            "TTS Definition of Done section is missing."
        )
        return False
    missing = [item for item in _TTS_CHECKLIST_ITEMS if f"- [x] {item}" not in section]
    if missing:
        print(
            "[smoke-framework-v200-real-tts-web-audio-acceptance-sync] ERROR: "
            "TTS Definition of Done remains incomplete: " + " | ".join(missing)
        )
        return False
    if "real_tts_web_audio_output: ACCEPTED" not in section:
        print(
            "[smoke-framework-v200-real-tts-web-audio-acceptance-sync] ERROR: "
            "TTS source-of-truth status is not ACCEPTED."
        )
        return False
    print("v200_real_tts_web_audio_acceptance_sync_definition_of_done: complete")
    return True


def _check_public_safe_acceptance_blocks() -> bool:
    paths = (_CHECKLIST_PATH, _ACCEPTANCE_DOC_PATH,)
    for path in paths:
        text = path.read_text(encoding="utf-8")
        block = _extract_commit_block(text)
        if not block:
            print(
                "[smoke-framework-v200-real-tts-web-audio-acceptance-sync] ERROR: "
                f"{path.relative_to(ROOT)} is missing the D-next-18 acceptance block."
            )
            return False
        missing = [snippet for snippet in _ACCEPTANCE_REQUIRED_SNIPPETS if snippet not in block]
        if _PRIVATE_SAFETY_SNIPPET not in block:
            missing.append(_PRIVATE_SAFETY_SNIPPET)
        if missing:
            print(
                "[smoke-framework-v200-real-tts-web-audio-acceptance-sync] ERROR: "
                f"{path.relative_to(ROOT)} is missing acceptance markers: "
                + " | ".join(missing)
            )
            return False
        forbidden = [token for token in _FORBIDDEN_ACCEPTANCE_BLOCK_TOKENS if token in block]
        if forbidden:
            print(
                "[smoke-framework-v200-real-tts-web-audio-acceptance-sync] ERROR: "
                f"{path.relative_to(ROOT)} exposes private or endpoint-shaped data: "
                + " | ".join(forbidden)
            )
            return False
    print("v200_real_tts_web_audio_acceptance_sync_public_blocks: safe")
    return True


def _check_unresolved_release_gates() -> bool:
    text = _CHECKLIST_PATH.read_text(encoding="utf-8")
    required = (
        "- [x] Real Web UI execution evidence has been collected.",
        "- [x] Web UI result screenshots have been collected.",
        "real_google_health_sleep_data: ACCEPTED",
        "accepted_private_evidence_manifest: NOT_ACCEPTED",
        "final_fixed_release_zip: not-built",
        "DRC_v2.0.0_tag: not-created",
        "Status: **NOT RELEASED**",
    )
    missing = [snippet for snippet in required if snippet not in text]
    if missing:
        print(
            "[smoke-framework-v200-real-tts-web-audio-acceptance-sync] ERROR: "
            "a later release gate advanced early: " + " | ".join(missing)
        )
        return False
    print("v200_real_tts_web_audio_acceptance_sync_later_gates: unchanged")
    return True


def _check_roadmap_sync() -> bool:
    text = _ROADMAP_PATH.read_text(encoding="utf-8")
    checkpoint = _extract_section(text, "Current v2.0.0 checkpoint:", "## Current baseline")
    required = (
        "real_tts_web_audio_output: ACCEPTED",
        "real_google_health_sleep_data: ACCEPTED",
        "accepted_private_evidence_manifest: ACCEPTED",
        "final_fixed_release_zip: not-built",
        "DRC_v2.0.0_tag: not-created",
        "release_status: NOT_RELEASED",
        "D-next-18 synchronizes public-safe acceptance",
        "E-9 synchronizes public-safe acceptance",
        "G-5 synchronizes public-safe acceptance",
    )
    missing = [snippet for snippet in required if snippet not in checkpoint]
    if missing:
        print(
            "[smoke-framework-v200-real-tts-web-audio-acceptance-sync] ERROR: "
            "roadmap checkpoint is not synchronized: " + " | ".join(missing)
        )
        return False
    print("v200_real_tts_web_audio_acceptance_sync_roadmap: synchronized")
    return True


def _check_scripts_readme_sync() -> bool:
    text = _SCRIPTS_README_PATH.read_text(encoding="utf-8")
    required = (
        "## v2.0.0 D-next-18 public-safe real TTS Web audio acceptance synchronization",
        "smoke_framework_v200_real_tts_web_audio_acceptance_sync.py",
        "real_tts_web_audio_output: ACCEPTED",
        "real_google_health_sleep_data",
        "accepted_private_evidence_manifest",
        "release_status: NOT_RELEASED",
    )
    missing = [snippet for snippet in required if snippet not in text]
    if missing:
        print(
            "[smoke-framework-v200-real-tts-web-audio-acceptance-sync] ERROR: "
            "scripts README is not synchronized: " + " | ".join(missing)
        )
        return False
    print("v200_real_tts_web_audio_acceptance_sync_scripts_readme: synchronized")
    return True


def _check_gitignore_boundary() -> bool:
    text = (ROOT / ".gitignore").read_text(encoding="utf-8")
    required = ("operator_evidence/", "_local/", "*.local.env")
    missing = [snippet for snippet in required if snippet not in text]
    if missing:
        print(
            "[smoke-framework-v200-real-tts-web-audio-acceptance-sync] ERROR: "
            "gitignore no longer protects local-only evidence: " + " | ".join(missing)
        )
        return False
    print("v200_real_tts_web_audio_acceptance_sync_gitignore_boundary: protected")
    return True


if __name__ == "__main__":
    raise SystemExit(main())
