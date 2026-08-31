"""Validate DRC v4.0.0 Control C release-candidate no-build preflight.

This static gate is credential-free, provider-free, network-free, and
artifact-free. It supports the exact uncommitted Control C candidate and a future
clean committed state without hard-coding the future implementation SHA.
"""

from __future__ import annotations

from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
BASELINE = "5908cb5b0d88c2e8aa6370105c3d618064cb4665"
CONTROL_B_BASELINE = "b752491632c58c557c02b06587cab28edcb901ca"
EXPECTED_MODIFIED = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v400_goal_checklist_small_commit.md",
    "docs/v400_release_preparation_protocol.md",
    "docs/v400_release_candidate_metadata.md",
    "docs/v400_release_record.md",
}
EXPECTED_ADDED = {
    "docs/v400_release_candidate_no_build_preflight.md",
    "scripts/check_v400_release_candidate_no_build_preflight.py",
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
    "release",
)
PRIVATE_PATTERNS = (
    re.compile(r"(?i)sk-[a-z0-9_-]{12,}"),
    re.compile(r"(?i)bearer\s+[a-z0-9._~+/-]{12,}"),
    re.compile(r"(?i)\b[a-z]:\\users\\"),
    re.compile(r"\b(?:10|127|169\.254|172\.(?:1[6-9]|2\d|3[0-1])|192\.168)\.\d{1,3}\.\d{1,3}\b"),
)
PENDING_POST_EDIT_MARKER = "PENDING_POST_EDIT_" + "VERIFICATION"
FORBIDDEN_PACKAGE_NAMES = {
    ".env",
    "credentials.json",
    "google_health_tokens.json",
    "fitbit_tokens.json",
    "token.json",
}
FORBIDDEN_PACKAGE_PARTS = {
    ".git",
    "release",
    "build",
    "operator_evidence",
    "local_data",
}


def git_out(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def git_success(*args: str) -> bool:
    return subprocess.run(["git", *args], cwd=ROOT).returncode == 0


def read(relative: str) -> str:
    path = ROOT / relative
    if not path.is_file():
        raise AssertionError(f"Missing required file: {relative}")
    return path.read_text(encoding="utf-8")


def norm(text: str) -> str:
    normalized = text.replace("\r\n", "\n")
    return normalized.replace("`", "").replace("*", "").replace("(", "").replace(")", "")


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise AssertionError(f"Missing {label}: {needle!r}")


def reject(text: str, needle: str, label: str) -> None:
    if needle in text:
        raise AssertionError(f"Unexpected {label}: {needle!r}")


def require_associated(text: str, label: str, value: str, scope: str) -> None:
    compact = norm(text)
    pattern = rf"{re.escape(label)}\s*:?\s*\n?\s*{re.escape(value)}"
    if not re.search(pattern, compact, flags=re.IGNORECASE):
        raise AssertionError(f"Missing associated {scope}: {label} -> {value}")


def require_regex(text: str, pattern: str, label: str) -> None:
    if not re.search(pattern, norm(text), flags=re.MULTILINE):
        raise AssertionError(f"Missing {label}: {pattern}")


def status_entries() -> list[tuple[str, str]]:
    raw = subprocess.check_output(
        ["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"],
        cwd=ROOT,
    )
    entries: list[tuple[str, str]] = []
    parts = raw.decode("utf-8").split("\0")
    for part in parts:
        if not part:
            continue
        entries.append((part[:2], part[3:].replace("\\", "/")))
    return entries


def require_branch_main() -> None:
    branch = git_out("branch", "--show-current")
    if branch != "main":
        raise AssertionError(f"Unexpected branch: {branch}")


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
    require_branch_main()
    entries = status_entries()
    if entries:
        head = git_out("rev-parse", "HEAD")
        origin = git_out("rev-parse", "origin/main")
        if head != BASELINE:
            raise AssertionError(f"Dirty candidate HEAD mismatch: {head} != {BASELINE}")
        if origin != BASELINE:
            raise AssertionError(f"Dirty candidate origin/main mismatch: {origin} != {BASELINE}")
        check_dirty_surface(entries)
        return "DIRTY_CANDIDATE"

    if not git_success("cat-file", "-e", f"{BASELINE}^{{commit}}"):
        raise AssertionError(f"Missing baseline commit: {BASELINE}")
    if not git_success("merge-base", "--is-ancestor", BASELINE, "HEAD"):
        raise AssertionError(f"Baseline is not an ancestor of HEAD: {BASELINE}")
    return "CLEAN_COMMITTED_STATIC"


def check_versions() -> None:
    version_source = read("backend/app/version.py")
    require(version_source, 'APP_VERSION = "4.0.0"', "Backend APP_VERSION")

    pubspec = read("app/pubspec.yaml")
    match = re.search(r"^version:\s*([^\s]+)\s*$", pubspec, flags=re.MULTILINE)
    if not match:
        raise AssertionError("Missing app/pubspec.yaml version")
    if match.group(1) != "4.0.0+5":
        raise AssertionError(f"Unexpected Flutter version: {match.group(1)}")

    active_checker = read("scripts/check_v20x_application_version_metadata.py")
    require_regex(active_checker, r'"4\.0\.0"\s*:\s*"5"', "active 4.0.0 -> build 5 mapping")


def check_release_state_docs() -> None:
    for relative in COORDINATION_DOCS:
        text = read(relative)
        for label, value in (
            ("current small commit", "DRC v4.0.0 Release Preparation Protocol Control C"),
            ("current implementation", "DRC v4.0.0 Release Preparation Protocol Control C"),
            ("current implementation state", "IMPLEMENTED / VERIFIED / AWAITING_REVIEW"),
            ("Control C baseline", BASELINE),
            ("Control B", "COMPLETED / VERIFIED / REVIEWED / ACCEPTED / COMMITTED / PUSHED / CLOSED"),
            ("Control B implementation commit", BASELINE),
            ("Control C", "IMPLEMENTED / VERIFIED / AWAITING_REVIEW"),
            ("Control D", "FUTURE / NOT_AUTHORIZED"),
            ("Control E", "FUTURE / NOT_AUTHORIZED"),
            ("current released version", "v3.0.0 RELEASED / ACCEPTED"),
            ("current v4 candidate metadata", "Backend 4.0.0 / Flutter 4.0.0+5 NOT_RELEASED"),
            ("DRC v4.0.0", "NOT_RELEASED"),
            ("fixed ZIP builder invocation count", "0"),
            ("fixed ZIP", "NOT_BUILT"),
            ("annotated tag", "NOT_CREATED"),
            ("GitHub Release", "NOT_CREATED"),
            ("real unified FW runtime", "NOT_AVAILABLE / NOT_CLAIMED"),
            ("real unified FW runtime release blocker", "NO"),
            ("existing v3 real runtime", "PRESERVED / RELEASED / ACCEPTED"),
            ("existing v3 replacement", "NO"),
            ("/realtime/text replacement", "NO"),
        ):
            require_associated(text, label, value, relative)


def check_protocol_doc() -> None:
    protocol = read("docs/v400_release_preparation_protocol.md")
    for label, value in (
        ("Current checkpoint", "DRC v4.0.0 Release Preparation Protocol Control C"),
        ("Control C baseline", BASELINE),
        ("Control B", "COMPLETED / VERIFIED / REVIEWED / ACCEPTED / COMMITTED / PUSHED / CLOSED"),
        ("Control B implementation commit", BASELINE),
        ("Control C", "IMPLEMENTED / VERIFIED / AWAITING_REVIEW"),
        ("Control D", "FUTURE / NOT_AUTHORIZED"),
        ("Control E", "FUTURE / NOT_AUTHORIZED"),
        ("full source/runtime regression", "AUTHORIZED_FOR_VERIFICATION"),
        (
            "v3/FW-v6 provider-free coexistence focused verification",
            "AUTHORIZED_FOR_SOURCE_AND_IN_PROCESS_TESTS",
        ),
        ("source-only release-package hygiene preflight", "AUTHORIZED"),
        ("exact surface", "10 files / M8 A2 D0"),
        ("fixed ZIP builder invocation count", "0"),
        ("fixed ZIP", "NOT_BUILT"),
    ):
        require_associated(protocol, label, value, "protocol")
    for needle in (
        "## Control C Boundary",
        "Control C is the current release-candidate verification and no-build preflight.",
        "Control D owns the release source HEAD, verification HEAD, and fixed ZIP.",
        "Control E owns tag, GitHub Release, and publication.",
        "release builder",
        "stage, commit, push, tag, or publish",
    ):
        require(protocol, needle, "Control C protocol boundary")
    require_regex(
        protocol,
        r"Control C:\s*\nRelease Candidate verification / no-build preflight\s*\nIMPLEMENTED / VERIFIED / AWAITING_REVIEW",
        "current Control C sequencing status",
    )
    require_regex(
        protocol,
        r"## Stop State[\s\S]*?DRC v4\.0\.0 Release Preparation Protocol:\s*\nIMPLEMENTED / VERIFIED / AWAITING_REVIEW",
        "current Stop State protocol status",
    )
    reject(protocol, "## Future Control C", "future Control C heading")


def check_candidate_metadata_doc() -> None:
    metadata = read("docs/v400_release_candidate_metadata.md")
    for label, value in (
        ("Status", "COMPLETED / VERIFIED / REVIEWED / ACCEPTED / COMMITTED / PUSHED / CLOSED"),
        ("Control B implementation commit", BASELINE),
        ("Backend candidate version", "4.0.0"),
        ("Flutter candidate version", "4.0.0+5"),
        ("candidate release", "v4.0.0 RELEASE CANDIDATE / NOT_RELEASED"),
        ("planned tag", "DRC_v4.0.0"),
        ("fixed ZIP", "NOT_BUILT"),
        ("builder invocation count", "0"),
        ("GitHub Release", "NOT_CREATED"),
        ("DRC v4.0.0", "NOT_RELEASED"),
        ("Control C", "IMPLEMENTED / VERIFIED / AWAITING_REVIEW"),
        ("Control D", "FUTURE / NOT_AUTHORIZED"),
        ("Control E", "FUTURE / NOT_AUTHORIZED"),
    ):
        require_associated(metadata, label, value, "candidate metadata")


def check_release_record() -> None:
    record = read("docs/v400_release_record.md")
    for label, value in (
        ("Status", "PREPARED / NOT_RELEASED"),
        ("Current phase", "Control C IMPLEMENTED / VERIFIED / AWAITING_REVIEW"),
        ("Control B implementation commit", BASELINE),
        ("Control C verification baseline", BASELINE),
        ("release source HEAD", "NOT_RECORDED"),
        ("verification HEAD", "NOT_RECORDED"),
        ("fixed ZIP basename", "NOT_BUILT"),
        ("fixed ZIP size", "NOT_RECORDED"),
        ("fixed ZIP SHA-256", "NOT_RECORDED"),
        ("fixed ZIP builder invocation count", "0"),
        ("same-artifact verification", "NOT_COMPLETED"),
        ("ZIP CRC/single-package-root verification", "NOT_COMPLETED"),
        ("explicit final operator approval", "NOT_RECEIVED"),
        ("annotated tag publication", "NOT_CREATED"),
        ("GitHub Release publication", "NOT_CREATED"),
    ):
        require_associated(record, label, value, "release record")


def check_preflight_doc() -> None:
    preflight = read("docs/v400_release_candidate_no_build_preflight.md")
    for label, value in (
        ("Status", "IMPLEMENTED / VERIFIED / AWAITING_REVIEW"),
        ("Control C baseline", BASELINE),
        ("Control B", "COMPLETED / VERIFIED / REVIEWED / ACCEPTED / COMMITTED / PUSHED / CLOSED"),
        ("Control B implementation commit", BASELINE),
        ("Control C", "IMPLEMENTED / VERIFIED / AWAITING_REVIEW"),
        ("Backend candidate", "4.0.0"),
        ("Flutter candidate", "4.0.0+5"),
        ("fixed ZIP builder invocation count", "0"),
        ("fixed ZIP", "NOT_BUILT"),
        ("Control D", "FUTURE / NOT_AUTHORIZED"),
        ("Control E", "FUTURE / NOT_AUTHORIZED"),
        ("Python compileall", "PASS / exit 0"),
        ("Control C dedicated checker", "PASS / OK"),
        ("application version metadata checker", "PASS / OK"),
        ("source-only package hygiene", "PASS"),
        ("exact surface", "10 files / M8 A2 D0"),
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
    ):
        require_associated(preflight, label, value, "preflight")
    for needle in (
        "benign note:\nCan't list 'backend\\.pytest_cache'",
        "source-only release-package hygiene:\nPASS",
        "Backend full:",
        "Flutter full:",
        "Backend full:\n479 PASS",
        "Flutter full:\n570 PASS",
        "Flutter FW-v6 focused corrective:\n70 PASS / exit 0",
        "Flutter v3 realtime preservation:\n328 PASS / exit 0",
        "NON_PRODUCT_COMPLETION_TIMEOUT / RESOLVED_BY_CORRECTIVE_RERUN",
        "source-only release-package hygiene",
        "candidate diff",
        "backend/app/version.py",
        "app/pubspec.yaml",
        "release_notes/v4.0.0.md",
    ):
        require(preflight, needle, "preflight contract")
    reject(preflight, PENDING_POST_EDIT_MARKER, "pending post-edit verification marker")


def check_no_release_outputs() -> None:
    if git_out("tag", "--list", "DRC_v4.0.0"):
        raise AssertionError("DRC_v4.0.0 tag exists")
    release_root = ROOT / "release"
    if release_root.exists() and any(release_root.glob("*v4.0.0*.zip")):
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
    tracked = git_out("ls-files").splitlines()
    for relative in tracked:
        normalized = relative.replace("\\", "/")
        path = ROOT / normalized
        parts = set(Path(normalized).parts)
        lower_name = path.name.lower()
        if lower_name in FORBIDDEN_PACKAGE_NAMES:
            raise AssertionError(f"Forbidden tracked package member: {normalized}")
        if lower_name.endswith(".zip"):
            raise AssertionError(f"Forbidden tracked ZIP: {normalized}")
        if parts & FORBIDDEN_PACKAGE_PARTS:
            raise AssertionError(f"Forbidden tracked package path: {normalized}")

    for relative in sorted(EXPECTED_MODIFIED):
        text = subprocess.check_output(
            ["git", "diff", "--", relative],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        for pattern in PRIVATE_PATTERNS:
            if pattern.search(text):
                raise AssertionError(f"Private-looking value in candidate diff: {relative}")

    for relative in sorted(EXPECTED_ADDED):
        text = read(relative)
        for pattern in PRIVATE_PATTERNS:
            if pattern.search(text):
                raise AssertionError(f"Private-looking value in candidate diff: {relative}")


def reject_current_state_contradictions() -> None:
    current_text = "\n".join(read(relative) for relative in CURRENT_DOCS)
    for needle in (
        "v4.0.0 RELEASED",
        "fixed ZIP: BUILT",
        "fixed release ZIP: BUILT",
        "annotated tag: CREATED",
        "GitHub Release: CREATED",
        "Control D: AUTHORIZED",
        "Control E: AUTHORIZED",
        "existing v3 replacement: YES",
        "/realtime/text replacement: YES",
        "real unified FW runtime: AVAILABLE",
    ):
        reject(current_text, needle, "current-state contradiction")
    reject(current_text, PENDING_POST_EDIT_MARKER, "pending post-edit verification marker")


def main() -> None:
    mode = determine_mode()
    check_versions()
    check_release_state_docs()
    check_protocol_doc()
    check_candidate_metadata_doc()
    check_release_record()
    check_preflight_doc()
    check_no_release_outputs()
    check_protected_surface()
    check_source_only_package_hygiene()
    reject_current_state_contradictions()

    print(f"v400_release_candidate_no_build_preflight_source_state: {mode}")
    print("v400_release_candidate_no_build_preflight_status: implemented-verified-awaiting-review")
    print(f"v400_release_candidate_no_build_preflight_baseline: {BASELINE}")
    print("v400_release_candidate_no_build_preflight_control_b_closed: True")
    print(f"v400_release_candidate_no_build_preflight_control_b_commit: {BASELINE}")
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
