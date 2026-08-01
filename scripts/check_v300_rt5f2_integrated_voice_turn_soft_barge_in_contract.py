from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_HEAD = "b7bd436196210f27782b64c1a094aa65d6893915"
IMPLEMENTATION_COMMIT = "c538dc89c2aa9780cd3014aa4ba11c17a9e378e6"
CORRECTIVE_COMMIT = "b7bd436196210f27782b64c1a094aa65d6893915"
PREVIOUS_ACCEPTANCE = "1cba847b7c443c4d41a2ff6bd2c18d20689e5029"

EXPECTED_FILES = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_rt5f2_integrated_voice_turn_soft_barge_in_contract.md",
    "scripts/check_v300_rt5f2_integrated_voice_turn_soft_barge_in_contract.py",
}

ORIGINAL_FILES = EXPECTED_FILES | {
    "app/lib/services/integrated_voice_turn_coordinator.dart",
    "app/test/integrated_voice_turn_coordinator_test.dart",
}

CORRECTIVE_FILES = {
    "app/lib/services/integrated_voice_turn_coordinator.dart",
    "app/test/integrated_voice_turn_coordinator_test.dart",
    "docs/v300_rt5f2_integrated_voice_turn_soft_barge_in_contract.md",
    "scripts/check_v300_rt5f2_integrated_voice_turn_soft_barge_in_contract.py",
}


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(ROOT), *args],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git command failed")
    return result.stdout


def require(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise RuntimeError(f"{label} missing marker: {marker}")


def changed_files() -> set[str]:
    tracked = {x.strip() for x in git("diff", "HEAD", "--name-only").splitlines() if x.strip()}
    untracked = {x.strip() for x in git("ls-files", "--others", "--exclude-standard").splitlines() if x.strip()}
    return tracked | untracked


def commit_files(commit: str) -> set[str]:
    return {
        x.strip()
        for x in git("diff-tree", "--no-commit-id", "--name-only", "-r", commit).splitlines()
        if x.strip()
    }


def main() -> None:
    if git("rev-parse", "HEAD").strip() != EXPECTED_HEAD:
        raise RuntimeError("unexpected acceptance-sync baseline HEAD")
    if git("rev-parse", "HEAD^").strip() != IMPLEMENTATION_COMMIT:
        raise RuntimeError("corrective parent mismatch")
    if git("rev-parse", f"{IMPLEMENTATION_COMMIT}^").strip() != PREVIOUS_ACCEPTANCE:
        raise RuntimeError("implementation parent mismatch")
    if commit_files(IMPLEMENTATION_COMMIT) != ORIGINAL_FILES:
        raise RuntimeError("original exact nine-file surface mismatch")
    if commit_files(CORRECTIVE_COMMIT) != CORRECTIVE_FILES:
        raise RuntimeError("corrective exact four-file surface mismatch")
    if changed_files() != EXPECTED_FILES:
        raise RuntimeError("acceptance-sync exact seven-file surface mismatch")

    source = (ROOT / "app/lib/services/integrated_voice_turn_coordinator.dart").read_text(encoding="utf-8")
    tests = (ROOT / "app/test/integrated_voice_turn_coordinator_test.dart").read_text(encoding="utf-8")

    for marker in (
        "_hasExclusiveVoiceOutputAccess()",
        "Voice output must remain empty and idle after phase notification.",
        "_sameVoiceOutputItem(processResult.item, enqueuedItem)",
        "actual.itemId == expected.itemId",
        "actual.generation == expected.generation",
        "integrated_voice_turn_voice_output_item_mismatch",
        "integratedVoiceTurnMaxSpeechEventIdCodePoints = 128",
        "integratedVoiceTurnMaxRememberedSpeechEventIds = 32",
    ):
        require(source, marker, "coordinator")
    if source.count("if (!_hasExclusiveVoiceOutputAccess())") < 3:
        raise RuntimeError("three voice-output exclusivity checks are required")

    for marker in (
        "pre-existing pending voice output blocks turn before capture",
        "pre-existing active synthesis blocks turn before capture",
        "voice output becoming non-exclusive before terminal enqueue rejects turn",
        "voice-output phase listener cannot enqueue between exclusivity check and enqueue",
        "processed voice-output item must match current terminal item",
    ):
        require(tests, marker, "focused tests")

    docs = {
        path: (ROOT / path).read_text(encoding="utf-8")
        for path in EXPECTED_FILES
        if not path.startswith("scripts/check_")
    }
    combined = "\n".join(docs.values())

    for marker in (
        "RT-5f2 COMPLETED / ACCEPTED / PUSHED",
        IMPLEMENTATION_COMMIT,
        CORRECTIVE_COMMIT,
        "RT-5f3: NOT_STARTED / READY_FOR_EXACT_CONTRACT_REVIEW / NOT_AUTHORIZED",
        "focused Flutter: 26 passed",
        "Flutter full: 381 passed",
    ):
        require(combined, marker, "acceptance documents")

    contract = docs["docs/v300_rt5f2_integrated_voice_turn_soft_barge_in_contract.md"]
    for marker in (
        "RT-5f2: COMPLETED / ACCEPTED / PUSHED",
        "RT-5f2 corrective commit: " + CORRECTIVE_COMMIT,
        "## Acceptance record",
        "exact acceptance review: PASS",
        "This seven-file acceptance sync changes documentation",
    ):
        require(contract, marker, "accepted contract")

    readme = docs["README.md"]
    require(
        readme,
        "RT-5f2 is COMPLETED / ACCEPTED / PUSHED through implementation "
        f"commit `{IMPLEMENTATION_COMMIT}` and corrective commit "
        f"`{CORRECTIVE_COMMIT}`.",
        "README current RT-5f2 summary",
    )

    require(
        readme,
        "  RT-5f3  NOT_STARTED / READY_FOR_EXACT_CONTRACT_REVIEW / "
        "NOT_AUTHORIZED  Default-off HomeScreen and production "
        "speech-activity wiring",
        "README current phase table",
    )
    require(
        docs["roadmap.md"],
        "Current implementation boundary: accepted exact nine-file fake-only "
        "coordinator plus exact four-file queue-ownership correction; Backend, "
        "main.dart, HomeScreen, existing runtime files, production speech "
        "activity, dependencies, and versions remain unchanged.",
        "roadmap current implementation boundary",
    )
    require(
        docs["docs/DRC_v300_goal_checklist_small_commit.md"],
        "RT-5f3 NOT_STARTED / READY_FOR_EXACT_CONTRACT_REVIEW / "
        "NOT_AUTHORIZED",
        "v3 checklist current RT-5f3 state",
    )

    for forbidden in (
        "{IMPLEMENTATION_COMMIT}",
        "{CORRECTIVE_COMMIT}",
        "CORRECTIVE_PATCH_AWAITING_REVIEW",
        "Current implementation boundary: exact nine-file fake-only "
        "coordinator candidate",
    ):
        if forbidden in combined:
            raise RuntimeError(
                f"acceptance documents contain forbidden marker: {forbidden}"
            )

    print("v300_rt5f2_status: completed-accepted-pushed")
    print("v300_rt5f2_exact_original_surface: 9")
    print("v300_rt5f2_exact_corrective_surface: 4")
    print("v300_rt5f2_exact_acceptance_sync_surface: 7")
    print("v300_rt5f2_voice_output_exclusive_after_phase_notification: True")
    print("v300_rt5f2_processed_item_identity_required: True")
    print("v300_rt5f2_fake_only: True")
    print("v300_rt5f3_authorization: ready-for-exact-contract-review-not-authorized")


if __name__ == "__main__":
    main()
