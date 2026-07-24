"""Validate the accepted C-1a post-advice chat behavior inventory.

C-1a is historical after acceptance. This check preserves the accepted inventory,
release records, Framework boundary, and unchanged Flutter baseline while allowing
C-1b to modify the explicitly assigned Backend lifecycle files and tests.
"""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

PROTECTED_RELEASE_HASHES = {
    "docs/DRC_v200_goal_checklist_small_commit.md": "4c043837986c626c6fc44e4f84f73b019b2c8c21da7531a3f029554006b7eb63",
    "release_notes/v2.0.0.md": "d2e13041ae51b9fef330a01a0d9124ccbfb6fb0850a0c2a29966baf96be3417b",
    "docs/DRC_v20x_maintenance_checklist.md": "02e6e2e49a54a5c1360ee5d95d6bed2314ab42aec5dce911f3ed72867c4d46f2",
    "docs/v20x_patch_release.md": "eb6ae9770a4611a463ddb227a1dd8ce8816ee310cddaed327a02404a34a7935d",
    "docs/v201_patch_release_record.md": "9b724a6c5c7ffffdb3e699ad010ff75148ec4549b6cf2d940b44e62e161140bd",
    "release_notes/v2.0.1.md": "1e90c85e51ef848b64bddaa73f1f40c659457935e30831027310ea95fc94656b",
    "build_v200_final_fixed_release_zip_from_head.ps1": "4a4439341b0ad00d56b50038993631fcb48fb417cd0f0648dc3abc5e72d3b360",
    "build_v201_fixed_release_zip_from_head.ps1": "89d3fe3e39484b36272d9c8ec8499276ffe305ec844a87cca5d90fef8931ab1b",
    "scripts/check_v20x_patch_release.py": "e4eefc408abcbccc2651c1113ae8264269cce1d77525067173e0a06a7ef685cf",
}

C1A_UNCHANGED_AFTER_BACKEND_WORK_HASHES = {
    "backend/app/services/framework_text_chat_adapter.py": "706691dfbba83989cbe9ebffbb7e986f95d15e97d3be22ae8ae7ab6644ab6225",
    "backend/app/services/framework_text_chat_drc_live_reply.py": "fada52eed7c6322a87ff6b731904143ba0cd9899f235eb83875ca0a113cdc46f",
    "app/lib/models/chat.dart": "b145e7c335a734ef8609ff579e3533fb0e11f701982ba9a8f7ab48bdb817f1e9",
    "app/lib/services/backend_api_client.dart": "8f790252327c65e7908bd37e13233e4ec5bee6a68b1f2e11b5f536750a82a362",
    "app/lib/screens/home_screen.dart": "3933240c97ec55308342da4b84c8b5087b3eb78f674c7be03f93a0540195d950",
    "app/test/widget_test.dart": "175eec29a41f1cd1731137eeb74444c4e11c02ec6e7494385eb7ca322a2fcfb1",
}


def read(relative: str) -> str:
    path = ROOT / relative
    if not path.is_file():
        raise AssertionError(f"Missing required file: {relative}")
    return path.read_text(encoding="utf-8")


def normalized_hash(relative: str) -> str:
    data = (ROOT / relative).read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return sha256(data).hexdigest()


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise AssertionError(f"Missing {label}: {needle!r}")


def assert_hashes(expected: dict[str, str], label: str) -> None:
    for relative, digest in expected.items():
        actual = normalized_hash(relative)
        if actual != digest:
            raise AssertionError(f"{label} changed: {relative}: {actual} != {digest}")


def assert_no_sensitive_values(relative: str, text: str) -> None:
    patterns = (
        r"sk-[A-Za-z0-9_\-]{12,}",
        r"xai-[A-Za-z0-9_\-]{12,}",
        r"AIza[0-9A-Za-z_\-]{20,}",
        r"Bearer\s+[A-Za-z0-9_\-.]{16,}",
        r"[A-Za-z]:\\Users\\[^<\r\n]+",
        r"192\.168\.\d{1,3}\.\d{1,3}",
    )
    for pattern in patterns:
        if re.search(pattern, text, flags=re.IGNORECASE):
            raise AssertionError(f"Sensitive-looking value in {relative}: {pattern}")


def main() -> None:
    checklist = read("docs/DRC_v210_goal_checklist_small_commit.md")
    inventory = read("docs/v210_post_advice_chat_current_behavior_inventory.md")
    backend_contract = read("docs/v210_post_advice_chat_backend_lifecycle.md")
    roadmap = read("roadmap.md")
    tasklist = read("tasklist.md")
    scripts_readme = read("scripts/README.md")

    require(checklist, "Current small commit: C-1c", "C-1c current small commit")
    require(checklist, "C-1a  COMPLETED / ACCEPTED", "C-1a accepted state")
    require(checklist, "C-1b  COMPLETED / ACCEPTED", "C-1b accepted state")
    require(checklist, "C-1c  CURRENT / NOT_COMPLETED", "C-1c current state")
    require(roadmap, "Current small commit: C-1c", "roadmap current state")
    require(tasklist, "current small commit: C-1c CURRENT / NOT_COMPLETED", "tasklist current state")
    require(scripts_readme, "check_v210_post_advice_chat_backend_lifecycle.py", "C-1b command")

    require(inventory, "Status: C-1a COMPLETED / ACCEPTED", "inventory accepted status")
    require(inventory, "implementation commit: a4263ca", "C-1a implementation record")
    require(inventory, "C-1b status: COMPLETED / ACCEPTED", "C-1b accepted handoff marker")
    require(backend_contract, "Status: C-1b COMPLETED / ACCEPTED", "C-1b contract state")

    for marker in (
        "POST_ADVICE_CHAT_TTL_SECONDS=1800",
        "POST_ADVICE_CHAT_MAX_SESSIONS=100",
        "expired, capacity-evicted, and unknown IDs all become the same HTTP 404 detail",
        "has no maximum-turn or maximum-message limit",
        "a message HTTP 404 leaves the stale session object in memory",
        "C-1a  COMPLETED / ACCEPTED",
        "implementation commit: a4263ca",
    ):
        require(inventory, marker, "accepted C-1a inventory marker")

    config = read("backend/app/config.py")
    adapter = read("backend/app/services/framework_text_chat_adapter.py")
    flutter_client = read("app/lib/services/backend_api_client.dart")
    home = read("app/lib/screens/home_screen.dart")

    require(config, "post_advice_chat_ttl_seconds: int = 1800", "accepted TTL")
    require(config, "post_advice_chat_max_sessions: int = 100", "accepted capacity")
    require(config, "post_advice_chat_max_turns: int = 8", "C-1b turn bound")
    for status in ("skipped", "unavailable", "blocked-live-message-gate", "responded"):
        require(adapter, f'status="{status}"', f"adapter status {status}")
    require(flutter_client, "Post-advice chat message API failed: HTTP", "unchanged generic Flutter error")
    require(home, "_postAdviceChatError = _formatUserFacingError(error)", "unchanged Flutter presentation")

    assert_hashes(PROTECTED_RELEASE_HASHES, "Protected release record")
    assert_hashes(C1A_UNCHANGED_AFTER_BACKEND_WORK_HASHES, "C-1a unchanged Framework/Flutter baseline")

    for relative in (
        "README.md",
        "roadmap.md",
        "tasklist.md",
        "scripts/README.md",
        "docs/DRC_v210_goal_checklist_small_commit.md",
        "docs/v210_post_advice_chat_current_behavior_inventory.md",
        "docs/v210_post_advice_chat_backend_lifecycle.md",
    ):
        assert_no_sensitive_values(relative, read(relative))

    print("v210_post_advice_chat_inventory_status: completed-accepted")
    print("v210_post_advice_chat_inventory_completed_small_commit: C-1a")
    print("v210_post_advice_chat_inventory_current_small_commit: C-1c")
    print("v210_post_advice_chat_inventory_parent_phase: C-1-current-not-completed")
    print("v210_post_advice_chat_inventory_accepted_ttl_seconds: 1800")
    print("v210_post_advice_chat_inventory_accepted_max_sessions: 100")
    print("v210_post_advice_chat_inventory_c1b_backend_runtime_started: true")
    print("v210_post_advice_chat_inventory_flutter_runtime_changed: false")
    print("v210_post_advice_chat_inventory_real_framework_execution: false")
    print("v210_post_advice_chat_inventory_release_records_changed: false")
    print("[v210-post-advice-chat-current-behavior-inventory-check] OK")


if __name__ == "__main__":
    main()
