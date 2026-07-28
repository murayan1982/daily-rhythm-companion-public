# Validate DRC v3.0.0 RT-3d0 Framework real STT requirement feedback.

from __future__ import annotations

from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]

EXPECTED_CHANGED_PATHS = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_framework_real_stt_requirement_feedback.md",
    "scripts/check_v300_framework_real_stt_requirement_feedback.py",
}

SENSITIVE_PATTERNS = (
    r"sk-[A-Za-z0-9_\-]{12,}",
    r"xai-[A-Za-z0-9_\-]{12,}",
    r"AIza[0-9A-Za-z_\-]{20,}",
    r"Bearer\s+[A-Za-z0-9_\-.]{16,}",
    r"[A-Za-z]:\\Users\\[^<\r\n]+",
    r"192\.168\.\d{1,3}\.\d{1,3}",
)


def read(relative: str) -> str:
    path = ROOT / relative
    if not path.is_file():
        raise AssertionError(f"Missing required file: {relative}")
    return path.read_text(encoding="utf-8")


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise AssertionError(f"Missing {label}: {needle!r}")


def changed_paths() -> set[str]:
    result = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    paths: set[str] = set()
    for raw_line in result.stdout.splitlines():
        if not raw_line:
            continue
        path_text = raw_line[3:]
        if " -> " in path_text:
            path_text = path_text.split(" -> ", 1)[1]
        paths.add(path_text.replace("\\", "/"))
    return paths


def main() -> None:
    actual = changed_paths()
    if actual != EXPECTED_CHANGED_PATHS:
        raise AssertionError(
            "RT-3d0 changed surface mismatch: "
            f"unexpected={sorted(actual - EXPECTED_CHANGED_PATHS)}, "
            f"missing={sorted(EXPECTED_CHANGED_PATHS - actual)}"
        )

    sources = {
        "feedback": read("docs/v300_framework_real_stt_requirement_feedback.md"),
        "checklist": read("docs/DRC_v300_goal_checklist_small_commit.md"),
        "README": read("README.md"),
        "roadmap": read("roadmap.md"),
        "tasklist": read("tasklist.md"),
        "scripts README": read("scripts/README.md"),
    }

    for label, source in sources.items():
        require(source, "RT-3d0", f"{label} RT-3d0 marker")
        require(source, "v5.3.0", f"{label} Framework baseline")
        require(
            source,
            "BLOCKED_FRAMEWORK_REAL_PROVIDER_EXECUTION_NOT_IMPLEMENTED",
            f"{label} RT-3d block",
        )
        for pattern in SENSITIVE_PATTERNS:
            if re.search(pattern, source, flags=re.IGNORECASE):
                raise AssertionError(
                    f"Sensitive-looking value in {label}: {pattern}"
                )

    feedback = sources["feedback"]
    require(
        feedback,
        "Additional Framework development requirement identified for DRC v3.0.0",
        "formal Framework handoff statement",
    )
    require(feedback, "RT-3d0: COMPLETED / ACCEPTED", "accepted RT-3d0 state")
    require(feedback, "next Framework version: UNDECIDED", "undecided version")
    require(feedback, "first real STT provider: UNDECIDED", "undecided provider")
    require(
        feedback,
        "DRC must not unblock RT-3d using an uncommitted Framework worktree",
        "released Framework rule",
    )
    require(
        feedback,
        "provider-specific STT clients inside DRC",
        "DRC provider-client exclusion",
    )
    require(
        sources["checklist"],
        "Current small commit: none (RT-3d0 accepted; RT-3d blocked)",
        "active checklist state",
    )
    require(
        sources["scripts README"],
        "check_v300_framework_real_stt_requirement_feedback.py",
        "gate command",
    )

    forbidden = (
        "OpenAIVoiceInputProviderAdapter",
        "client.audio.transcriptions.create",
        "next Framework version: v5.4.0",
        "first real STT provider: openai",
    )
    for marker in forbidden:
        if marker in feedback:
            raise AssertionError(
                f"RT-3d0 must not preselect Framework implementation: {marker}"
            )

    print("v300_framework_real_stt_requirement_feedback_status: completed-accepted")
    print("v300_latest_released_framework: v5.3.0")
    print("v300_framework_additional_development_requirement_identified: True")
    print("v300_next_framework_version_selected: False")
    print("v300_first_real_stt_provider_selected: False")
    print("v300_drc_runtime_changed: False")
    print("v300_framework_runtime_changed: False")
    print("v300_audio_read: False")
    print("v300_microphone_accessed: False")
    print("v300_provider_execution_executed: False")
    print("v300_rt3d_status: blocked-framework-real-provider-execution-not-implemented")
    print("v300_rt3d0_operator_approval: accepted")
    print("[OK] RT-3d0 Framework requirement feedback is completed and accepted")


if __name__ == "__main__":
    main()
