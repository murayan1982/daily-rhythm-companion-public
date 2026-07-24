"""Validate the C-1a post-advice chat current-behavior inventory.

The check is source-tree only. It pins the inspected Backend/Flutter implementation
so C-1a cannot silently change runtime behavior or existing tests.
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

C1A_INSPECTED_HASHES = {
    "backend/app/config.py": "063b9fdd7c1b5c3132a5885eddb56fc2b2202d45b202dda25b745393b35ccc06",
    "backend/app/api/chat.py": "18107e3ddfce490f99f0750338a80d7ac0ee48aa3e7c4bc9206767af54a38f99",
    "backend/app/models/chat.py": "43391ee802d236b3625a26eca129853d1dca9044aa6dc7ec638a263d4ef2ebb2",
    "backend/app/services/post_advice_chat_service.py": "98ee953c7f5bfa5e8edf1adcc70d5bbb311d89e2c49c32672fa5cf49d2a49e7c",
    "backend/app/services/framework_text_chat_adapter.py": "706691dfbba83989cbe9ebffbb7e986f95d15e97d3be22ae8ae7ab6644ab6225",
    "backend/app/services/framework_text_chat_drc_live_reply.py": "fada52eed7c6322a87ff6b731904143ba0cd9899f235eb83875ca0a113cdc46f",
    "backend/tests/test_post_advice_chat_lifecycle.py": "ecbf06034c78e52bc3c2a74b129a791e4f3147deff8e1a9764cae05dbac4c2b8",
    "backend/tests/test_temporary_lifecycle_config.py": "fa82d5d7cd083fcf9fa9ad54b8221e88ec0221710a8d0dde13c253257ab5d9c3",
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
    roadmap = read("roadmap.md")
    tasklist = read("tasklist.md")
    scripts_readme = read("scripts/README.md")

    require(checklist, "Current small commit: C-1b", "C-1b current small commit")
    require(checklist, "W-5 state: COMPLETED / ACCEPTED", "W-5 accepted state")
    require(checklist, "C-1  CURRENT / NOT_COMPLETED", "C-1 parent state")
    require(checklist, "C-1a  COMPLETED / ACCEPTED", "C-1a accepted state")
    require(checklist, "C-1b  CURRENT / NOT_COMPLETED", "C-1b current state")
    require(checklist, "C-1c  PLANNED", "C-1c planned state")
    for phase in ("T-1", "V-1", "R-1"):
        require(checklist, f"{phase}  PLANNED", f"{phase} planned state")

    require(roadmap, "Current small commit: C-1b", "roadmap current state")
    require(tasklist, "current small commit: C-1b CURRENT / NOT_COMPLETED", "tasklist current state")
    require(scripts_readme, "check_v210_post_advice_chat_current_behavior_inventory.py", "scripts command")
    require(inventory, "Status: C-1a COMPLETED / ACCEPTED", "inventory accepted status")
    require(checklist, "implementation commit: a4263ca", "implementation commit record")

    for marker in (
        "POST_ADVICE_CHAT_TTL_SECONDS=1800",
        "POST_ADVICE_CHAT_MAX_SESSIONS=100",
        "expired, capacity-evicted, and unknown IDs all become the same HTTP 404 detail",
        "has no maximum-turn or maximum-message limit",
        "a message HTTP 404 leaves the stale session object in memory",
        "C-1a  COMPLETED / ACCEPTED",
        "C-1b  CURRENT / NOT_COMPLETED",
        "C-1c  PLANNED",
        "implementation commit: a4263ca",
    ):
        require(inventory, marker, "inventory marker")

    config = read("backend/app/config.py")
    service = read("backend/app/services/post_advice_chat_service.py")
    api = read("backend/app/api/chat.py")
    models = read("backend/app/models/chat.py")
    adapter = read("backend/app/services/framework_text_chat_adapter.py")
    flutter_client = read("app/lib/services/backend_api_client.dart")
    home = read("app/lib/screens/home_screen.dart")

    require(config, "post_advice_chat_ttl_seconds: int = 1800", "accepted TTL")
    require(config, "post_advice_chat_max_sessions: int = 100", "accepted capacity")
    require(service, "_cleanup_expired_locked", "expiry cleanup")
    require(service, "_evict_for_new_session_locked", "LRU eviction")
    require(api, 'detail="Chat session not found"', "existing 404 contract")
    require(models, "status: str", "existing session status field")
    if "turn_count" in models or "max_turn" in models:
        raise AssertionError("C-1a advanced bounded-turn runtime fields early")
    for status in ("skipped", "unavailable", "blocked-live-message-gate", "responded"):
        require(adapter, f'status="{status}"', f"adapter status {status}")
    require(flutter_client, "Post-advice chat message API failed: HTTP", "generic Flutter chat error")
    require(home, "_postAdviceChatSession = null", "local session clearing path")
    require(home, "_postAdviceChatError = _formatUserFacingError(error)", "generic Flutter error presentation")

    assert_hashes(PROTECTED_RELEASE_HASHES, "Protected release record")
    assert_hashes(C1A_INSPECTED_HASHES, "C-1a inspected implementation")

    for relative in (
        "README.md",
        "roadmap.md",
        "tasklist.md",
        "scripts/README.md",
        "docs/DRC_v210_goal_checklist_small_commit.md",
        "docs/v210_post_advice_chat_current_behavior_inventory.md",
    ):
        assert_no_sensitive_values(relative, read(relative))

    print("v210_post_advice_chat_inventory_status: completed-accepted")
    print("v210_post_advice_chat_inventory_completed_small_commit: C-1a")
    print("v210_post_advice_chat_inventory_current_small_commit: C-1b")
    print("v210_post_advice_chat_inventory_parent_phase: C-1-current-not-completed")
    print("v210_post_advice_chat_inventory_accepted_ttl_seconds: 1800")
    print("v210_post_advice_chat_inventory_accepted_max_sessions: 100")
    print("v210_post_advice_chat_inventory_existing_turn_limit: false")
    print("v210_post_advice_chat_inventory_expired_distinguished_from_unknown: false")
    print("v210_post_advice_chat_inventory_flutter_structured_lifecycle_state: false")
    print("v210_post_advice_chat_inventory_runtime_changed: false")
    print("v210_post_advice_chat_inventory_existing_tests_changed: false")
    print("v210_post_advice_chat_inventory_real_framework_execution: false")
    print("v210_post_advice_chat_inventory_release_records_changed: false")
    print("[v210-post-advice-chat-current-behavior-inventory-check] OK")


if __name__ == "__main__":
    main()
