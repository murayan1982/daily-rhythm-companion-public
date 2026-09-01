"""Validate DRC v4.0.0 Control C and Control D Stage 1 static boundary."""

from __future__ import annotations

from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
CONTROL_C_BASELINE = "5908cb5b0d88c2e8aa6370105c3d618064cb4665"
CONTROL_C_COMMIT = "4cae15573f3332cbc476557461babdfe2eb3c0bf"
EXPECTED_MODIFIED = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v400_goal_checklist_small_commit.md",
    "docs/v400_release_preparation_protocol.md",
    "docs/v400_release_candidate_metadata.md",
    "docs/v400_release_candidate_no_build_preflight.md",
    "docs/v400_release_record.md",
    "scripts/check_v400_release_candidate_no_build_preflight.py",
}
EXPECTED_ADDED = {
    "docs/v400_fixed_release_zip.md",
    "build_v400_fixed_release_zip_from_head.ps1",
    "scripts/check_v400_fixed_release_zip.py",
}
COORDINATION_DOCS = (
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v400_goal_checklist_small_commit.md",
)
CURRENT_DOCS = (
    *COORDINATION_DOCS,
    "docs/v400_release_preparation_protocol.md",
    "docs/v400_release_candidate_metadata.md",
    "docs/v400_release_record.md",
    "docs/v400_release_candidate_no_build_preflight.md",
    "docs/v400_fixed_release_zip.md",
)
PROTECTED_PATHS = (
    "backend/app/version.py",
    "app/pubspec.yaml",
    "scripts/check_v20x_application_version_metadata.py",
    "scripts/check_v400_release_candidate_metadata.py",
    "release_notes/v4.0.0.md",
    "backend/tests",
    "app/test",
    "app/pubspec.lock",
    "backend/requirements.txt",
    "backend/requirements-dev.txt",
    "backend/requirements-framework.txt",
    "build_release.bat",
    "build_v300_fixed_release_zip_from_head.ps1",
    "scripts/check_v300_fixed_release_zip.py",
    "release",
)
PRIVATE_PATTERNS = (
    re.compile(r"(?i)sk-[a-z0-9_-]{12,}"),
    re.compile(r"(?i)bearer\s+[a-z0-9._~+/-]{12,}"),
    re.compile(r"(?i)\b[a-z]:\\users\\"),
    re.compile(r"\b(?:10|127|169\.254|172\.(?:1[6-9]|2\d|3[0-1])|192\.168)\.\d{1,3}\.\d{1,3}\b"),
)
FORBIDDEN_PACKAGE_NAMES = {".env", "credentials.json", "token.json"}
FORBIDDEN_PACKAGE_PARTS = {".git", "release", "build", "operator_evidence", "local_data", "vendor"}
PENDING_POST_EDIT_MARKER = "PENDING_POST_EDIT_" + "VERIFICATION"


def git_out(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def read(relative: str) -> str:
    path = ROOT / relative
    if not path.is_file():
        raise AssertionError(f"Missing required file: {relative}")
    return path.read_text(encoding="utf-8")


def norm(text: str) -> str:
    return text.replace("\r\n", "\n").replace("`", "").replace("*", "")


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise AssertionError(f"Missing {label}: {needle!r}")


def reject(text: str, needle: str, label: str) -> None:
    if needle in text:
        raise AssertionError(f"Unexpected {label}: {needle!r}")


def require_associated(text: str, label: str, value: str, scope: str) -> None:
    pattern = rf"{re.escape(label)}\s*:?\s*\n?\s*{re.escape(value)}"
    if not re.search(pattern, norm(text), flags=re.IGNORECASE):
        raise AssertionError(f"Missing associated {scope}: {label} -> {value}")


def status_entries() -> list[tuple[str, str]]:
    raw = subprocess.check_output(
        ["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"],
        cwd=ROOT,
    )
    return [
        (part[:2], part[3:].replace("\\", "/"))
        for part in raw.decode("utf-8").split("\0")
        if part
    ]


def check_dirty_surface(entries: list[tuple[str, str]]) -> None:
    modified: set[str] = set()
    added: set[str] = set()
    deleted: set[str] = set()
    other: list[tuple[str, str]] = []
    for status, path in entries:
        if status == " M":
            modified.add(path)
        elif status == "??":
            added.add(path)
        elif "D" in status:
            deleted.add(path)
        else:
            other.append((status, path))
    if modified != EXPECTED_MODIFIED:
        raise AssertionError(f"Unexpected modified surface: {sorted(modified)}")
    if added != EXPECTED_ADDED:
        raise AssertionError(f"Unexpected added surface: {sorted(added)}")
    if deleted:
        raise AssertionError(f"Unexpected deleted files: {sorted(deleted)}")
    if other:
        raise AssertionError(f"Unexpected status entries: {other!r}")


def determine_mode() -> str:
    if git_out("branch", "--show-current") != "main":
        raise AssertionError("Unexpected branch")
    entries = status_entries()
    if entries:
        if git_out("rev-parse", "HEAD") != CONTROL_C_COMMIT:
            raise AssertionError("Dirty candidate HEAD mismatch")
        if git_out("rev-parse", "origin/main") != CONTROL_C_COMMIT:
            raise AssertionError("Dirty candidate origin/main mismatch")
        check_dirty_surface(entries)
        return "DIRTY_CONTROL_D_STAGE1_CANDIDATE"
    subprocess.run(["git", "merge-base", "--is-ancestor", CONTROL_C_COMMIT, "HEAD"], cwd=ROOT, check=True)
    return "CLEAN_COMMITTED_STATIC"


def check_versions() -> None:
    require(read("backend/app/version.py"), 'APP_VERSION = "4.0.0"', "Backend APP_VERSION")
    require(read("app/pubspec.yaml"), "version: 4.0.0+5", "Flutter version")
    require(read("scripts/check_v20x_application_version_metadata.py"), '"4.0.0": "5"', "version mapping")


def check_release_state_docs() -> None:
    for relative in COORDINATION_DOCS:
        text = read(relative)
        for label, value in (
            ("current small commit", "DRC v4.0.0 Release Preparation Protocol Control D Stage 1"),
            ("current implementation", "DRC v4.0.0 Release Preparation Protocol Control D Stage 1"),
            ("current implementation state", "FIXED_ZIP_TOOLING / IMPLEMENTED / AWAITING_REVIEW"),
            ("Control C", "COMPLETED / VERIFIED / REVIEWED / ACCEPTED / COMMITTED / PUSHED / CLOSED"),
            ("Control C implementation commit", CONTROL_C_COMMIT),
            ("Control D Stage 1 baseline", CONTROL_C_COMMIT),
            ("Control D", "CURRENT / NOT_COMPLETED"),
            ("Control D Stage 1", "FIXED_ZIP_TOOLING / IMPLEMENTED / AWAITING_REVIEW"),
            ("Control D Stage 2", "CLEAN_COMMITTED_SOURCE_PREFLIGHT / BLOCKED_PENDING_STAGE1_ACCEPTANCE / NOT_AUTHORIZED"),
            ("Control D Stage 3", "BUILD_EXACTLY_ONCE / BLOCKED_PENDING_STAGE2_ACCEPTANCE / NOT_AUTHORIZED"),
            ("Control D Stage 4", "SAME_ARTIFACT_VERIFICATION_AND_TUPLE_RECORD / BLOCKED_PENDING_STAGE3_ARTIFACT / NOT_AUTHORIZED"),
            ("Control E", "FUTURE / NOT_AUTHORIZED"),
            ("DRC v4.0.0", "NOT_RELEASED"),
            ("fixed ZIP builder invocation count", "0"),
            ("fixed ZIP", "NOT_BUILT"),
            ("annotated tag", "NOT_CREATED"),
            ("GitHub Release", "NOT_CREATED"),
        ):
            require_associated(text, label, value, relative)


def check_protocol_and_records() -> None:
    protocol = read("docs/v400_release_preparation_protocol.md")
    for needle in (
        "Control D Stage 1",
        "FIXED_ZIP_TOOLING / IMPLEMENTED / AWAITING_REVIEW",
        "COMPLETED / VERIFIED / REVIEWED / ACCEPTED / COMMITTED / PUSHED / CLOSED",
        "13 files / M10 A3 D0",
        "build_v400_fixed_release_zip_from_head.ps1",
        "scripts/check_v400_fixed_release_zip.py",
    ):
        require(protocol, needle, "protocol")

    metadata = read("docs/v400_release_candidate_metadata.md")
    for label, value in (
        ("Control C", "COMPLETED / VERIFIED / REVIEWED / ACCEPTED / COMMITTED / PUSHED / CLOSED"),
        ("Control C implementation commit", CONTROL_C_COMMIT),
        ("Control D", "CURRENT / NOT_COMPLETED"),
        ("Control D Stage 1", "FIXED_ZIP_TOOLING / IMPLEMENTED / AWAITING_REVIEW"),
        ("Control E", "FUTURE / NOT_AUTHORIZED"),
        ("DRC v4.0.0", "NOT_RELEASED"),
    ):
        require_associated(metadata, label, value, "candidate metadata")

    record = read("docs/v400_release_record.md")
    for label, value in (
        ("Status", "PREPARED / NOT_RELEASED"),
        ("Current phase", "Control D Stage 1 FIXED_ZIP_TOOLING / IMPLEMENTED / AWAITING_REVIEW"),
        ("Control C verification baseline", CONTROL_C_BASELINE),
        ("Control C implementation commit", CONTROL_C_COMMIT),
        ("release source HEAD", "NOT_RECORDED"),
        ("verification HEAD", "NOT_RECORDED"),
        ("fixed ZIP basename", "NOT_BUILT"),
        ("fixed ZIP size", "NOT_RECORDED"),
        ("fixed ZIP SHA-256", "NOT_RECORDED"),
        ("fixed ZIP builder invocation count", "0"),
        ("same-artifact verification", "NOT_COMPLETED"),
        ("explicit final operator approval", "NOT_RECEIVED"),
        ("annotated tag publication", "NOT_CREATED"),
        ("GitHub Release publication", "NOT_CREATED"),
    ):
        require_associated(record, label, value, "release record")

    preflight = read("docs/v400_release_candidate_no_build_preflight.md")
    for label, value in (
        ("Status", "COMPLETED / VERIFIED / REVIEWED / ACCEPTED / COMMITTED / PUSHED / CLOSED"),
        ("Control C implementation commit", CONTROL_C_COMMIT),
        ("Control D Stage 1", "FIXED_ZIP_TOOLING / IMPLEMENTED / AWAITING_REVIEW"),
        ("Python compileall", "PASS / exit 0"),
        ("Control C dedicated checker", "PASS / OK"),
        ("application version metadata checker", "PASS / OK"),
        ("source-only package hygiene", "PASS"),
        ("privacy boundary", "PASS"),
        ("git diff --check", "PASS / exit 0 / LF-to-CRLF warnings only"),
        ("release builder invocation", "NO"),
        ("release artifact creation", "NO"),
        ("Flutter release build", "NO"),
        ("provider execution", "NO"),
        ("credentials", "NO"),
        ("network", "NO"),
        ("repository stage", "NO"),
        ("commit", "NO"),
        ("push", "NO"),
        ("tag", "NO"),
        ("publication", "NO"),
        ("Backend FW-v6 focused", "62 PASS"),
        ("Backend v3 realtime preservation", "29 PASS"),
        ("Backend full", "479 PASS"),
        ("Flutter analyze", "PASS / No issues found"),
        ("Flutter FW-v6 focused corrective", "70 PASS / exit 0"),
        ("Flutter v3 realtime preservation", "328 PASS / exit 0"),
        ("Flutter full", "570 PASS"),
    ):
        require_associated(preflight, label, value, "preflight")
    for needle in (
        "Backend FW-v6 provider-free focused tests:\n62 PASS / ACCEPTED",
        "Backend v3 realtime preservation focused tests:\n29 PASS / ACCEPTED",
        "Backend full tests:\n479 PASS / ACCEPTED",
        "Flutter FW-v6 provider-free focused tests:\n70 PASS / corrective rerun exit 0",
        "Flutter v3 realtime preservation focused tests:\n328 PASS / exit 0",
        "Flutter full tests:\n570 PASS / exit 0",
        "source-only release-package hygiene:\nPASS",
    ):
        require(preflight, needle, "Control C historical guard")
    if preflight.count(PENDING_POST_EDIT_MARKER) != 0:
        raise AssertionError("PENDING_POST_EDIT_VERIFICATION marker is present")

    fixed = read("docs/v400_fixed_release_zip.md")
    for needle in (
        "credential-free, provider-free, private-evidence-free",
        "builder invocation count:\n0",
        "fixed ZIP:\nNOT_BUILT",
        "release source HEAD:\nNOT_RECORDED",
        "verification HEAD:\nNOT_RECORDED",
        "fixed ZIP SHA-256:\nNOT_RECORDED",
        "## Stage 1 Stop Rule",
    ):
        require(fixed, needle, "fixed ZIP contract")
    current_text = "\n".join(read(relative) for relative in CURRENT_DOCS)
    if current_text.count(PENDING_POST_EDIT_MARKER) != 0:
        raise AssertionError("PENDING_POST_EDIT_VERIFICATION marker is present in current docs")


def check_no_release_outputs() -> None:
    if git_out("tag", "--list", "DRC_v4.0.0"):
        raise AssertionError("DRC_v4.0.0 tag exists")
    release_root = ROOT / "release"
    if release_root.exists() and any(release_root.glob("DailyRhythmCompanion_v4.0.0_*.zip")):
        raise AssertionError("v4.0.0 release ZIP exists")


def check_protected_surface() -> None:
    completed = subprocess.run(
        ["git", "diff", "--exit-code", "--", *PROTECTED_PATHS],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if completed.returncode:
        raise AssertionError("Protected surface diff is not empty")


def check_source_only_package_hygiene() -> None:
    for relative in git_out("ls-files").splitlines():
        normalized = relative.replace("\\", "/")
        path = Path(normalized)
        parts = set(path.parts)
        lower_name = path.name.lower()
        if lower_name in FORBIDDEN_PACKAGE_NAMES:
            raise AssertionError(f"Forbidden tracked package member: {normalized}")
        if lower_name.endswith(".zip"):
            raise AssertionError(f"Forbidden tracked ZIP: {normalized}")
        if parts & FORBIDDEN_PACKAGE_PARTS:
            raise AssertionError(f"Forbidden tracked package path: {normalized}")

    for relative in sorted(EXPECTED_MODIFIED):
        text = subprocess.check_output(["git", "diff", "--", relative], cwd=ROOT, text=True, errors="replace")
        for pattern in PRIVATE_PATTERNS:
            if pattern.search(text):
                raise AssertionError(f"Private-looking value in candidate diff: {relative}")
    for relative in sorted(EXPECTED_ADDED):
        text = read(relative)
        for pattern in PRIVATE_PATTERNS:
            if pattern.search(text):
                raise AssertionError(f"Private-looking value in candidate file: {relative}")


def reject_current_state_contradictions() -> None:
    current_text = "\n".join(read(relative) for relative in CURRENT_DOCS)
    for needle in (
        "v4.0.0 RELEASED",
        "fixed ZIP: BUILT",
        "fixed release ZIP: BUILT",
        "annotated tag: CREATED",
        "GitHub Release: CREATED",
        "Control E: AUTHORIZED",
        "existing v3 replacement: YES",
        "/realtime/text replacement: YES",
        "real unified FW runtime: AVAILABLE",
    ):
        reject(current_text, needle, "current-state contradiction")


def main() -> None:
    mode = determine_mode()
    check_versions()
    check_release_state_docs()
    check_protocol_and_records()
    check_no_release_outputs()
    check_protected_surface()
    check_source_only_package_hygiene()
    reject_current_state_contradictions()

    print(f"v400_release_candidate_no_build_preflight_source_state: {mode}")
    print("v400_release_candidate_no_build_preflight_control_c_status: completed-verified-reviewed-accepted-committed-pushed-closed")
    print(f"v400_release_candidate_no_build_preflight_control_c_implementation_commit: {CONTROL_C_COMMIT}")
    print("v400_release_candidate_no_build_preflight_control_d_stage1_status: fixed-zip-tooling-implemented-awaiting-review")
    print(f"v400_release_candidate_no_build_preflight_control_d_stage1_baseline: {CONTROL_C_COMMIT}")
    print("v400_release_candidate_no_build_preflight_backend_version: 4.0.0")
    print("v400_release_candidate_no_build_preflight_flutter_version: 4.0.0+5")
    print("v400_release_candidate_no_build_preflight_current_released: v3.0.0")
    print("v400_release_candidate_no_build_preflight_v400_released: False")
    print("v400_release_candidate_no_build_preflight_release_source_head_recorded: False")
    print("v400_release_candidate_no_build_preflight_verification_head_recorded: False")
    print("v400_release_candidate_no_build_preflight_fixed_zip_builder_invocation_count: 0")
    print("v400_release_candidate_no_build_preflight_fixed_zip_built: False")
    print("v400_release_candidate_no_build_preflight_tag_created: False")
    print("v400_release_candidate_no_build_preflight_github_release_created: False")
    print("v400_release_candidate_no_build_preflight_stage_commit_push_authorized: False")
    print("v400_release_candidate_no_build_preflight_package_tag_publication_authorized: False")
    print("[v400-release-candidate-no-build-preflight-check] OK")


if __name__ == "__main__":
    main()
