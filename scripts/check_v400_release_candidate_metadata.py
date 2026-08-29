"""Validate DRC v4.0.0 Release Preparation Protocol Control B.

This static gate is credential-free, provider-free, network-free, and
artifact-free. It supports both the exact uncommitted Control B candidate and a
future clean committed state without hard-coding the future implementation SHA.
"""

from __future__ import annotations

from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
BASELINE = "b752491632c58c557c02b06587cab28edcb901ca"
EXPECTED_MODIFIED = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v400_goal_checklist_small_commit.md",
    "docs/v400_release_preparation_protocol.md",
    "backend/app/version.py",
    "app/pubspec.yaml",
    "scripts/check_v20x_application_version_metadata.py",
}
EXPECTED_ADDED = {
    "docs/v400_release_candidate_metadata.md",
    "docs/v400_release_record.md",
    "release_notes/v4.0.0.md",
    "scripts/check_v400_release_candidate_metadata.py",
}
COORDINATION_DOCS = (
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v400_goal_checklist_small_commit.md",
)


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
        status = part[:2]
        path = part[3:].replace("\\", "/")
        entries.append((status, path))
    return entries


def require_branch_main() -> None:
    branch = git_out("rev-parse", "--abbrev-ref", "HEAD")
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
    if len(re.findall(r"^APP_VERSION\s*=", version_source, flags=re.MULTILINE)) != 1:
        raise AssertionError("backend/app/version.py must define APP_VERSION exactly once")

    pubspec = read("app/pubspec.yaml")
    match = re.search(r"^version:\s*([^\s]+)\s*$", pubspec, flags=re.MULTILINE)
    if not match:
        raise AssertionError("Missing app/pubspec.yaml version")
    flutter_version = match.group(1)
    if flutter_version != "4.0.0+5":
        raise AssertionError(f"Unexpected Flutter version: {flutter_version}")
    if flutter_version.split("+", 1)[0] != "4.0.0":
        raise AssertionError("Backend and Flutter semantic versions differ")

    active_checker = read("scripts/check_v20x_application_version_metadata.py")
    require_regex(
        active_checker,
        r'"4\.0\.0"\s*:\s*"5"',
        "active 4.0.0 -> build 5 mapping",
    )


def check_release_notes() -> None:
    notes = read("release_notes/v4.0.0.md")
    for label, value in (
        ("State", "RELEASE CANDIDATE / NOT_RELEASED"),
        ("Backend semantic version", "4.0.0"),
        ("Flutter package version", "4.0.0+5"),
        ("fixed release ZIP", "NOT_BUILT"),
        ("GitHub Release", "NOT_CREATED"),
        ("Current published release remains", "v3.0.0 RELEASED / ACCEPTED"),
        ("Framework v6.0.0 framework-level readiness", "PARTIAL_READY / HISTORICAL_AND_STILL_TRUE"),
        ("real unified FW runtime", "NOT_AVAILABLE / NOT_CLAIMED"),
        ("real unified FW runtime release blocker", "NO"),
        ("existing v3 real runtime", "PRESERVED / RELEASED / ACCEPTED"),
        ("existing v3 replacement", "NO"),
        ("/realtime/text replacement", "NO"),
        ("automatic FW-v6 startup network", "NO"),
        ("automatic FW-v6 session open", "NO"),
        ("FW-v6 provider execution", "NO"),
        ("FW-v6 microphone", "NO"),
        ("FW-v6 STT", "NO"),
        ("FW-v6 real LLM provider", "NO"),
        ("FW-v6 TTS", "NO"),
        ("FW-v6 audio playback", "NO"),
        ("FW-v6 VTube Studio", "NO"),
        ("FW-v6 motion", "NO"),
    ):
        require_associated(notes, label, value, "release notes")
    require_regex(notes, r"planned tag\s*:?\s*\n\s*DRC_v4\.0\.0\s+-\s+NOT_CREATED", "planned tag")


def check_release_record() -> None:
    record = read("docs/v400_release_record.md")
    for label, value in (
        ("Status", "PREPARED / NOT_RELEASED"),
        ("Current phase", "Control B IMPLEMENTED / AWAITING_REVIEW"),
        ("release version", "v4.0.0"),
        ("Backend APP_VERSION", "4.0.0"),
        ("Flutter package version", "4.0.0+5"),
        ("planned annotated tag", "DRC_v4.0.0"),
        ("planned GitHub Release title", "Daily Rhythm Companion v4.0.0"),
        ("current published release", "v3.0.0 RELEASED / ACCEPTED"),
        ("Control A accepted commit", BASELINE),
        ("Control B implementation baseline", BASELINE),
        ("release source HEAD", "NOT_RECORDED"),
        ("verification HEAD", "NOT_RECORDED"),
        ("fixed ZIP basename", "NOT_BUILT"),
        ("fixed ZIP size", "NOT_RECORDED"),
        ("fixed ZIP SHA-256", "NOT_RECORDED"),
        ("fixed ZIP builder invocation count", "0"),
        ("same-artifact verification", "NOT_COMPLETED"),
        ("release-package hygiene", "NOT_COMPLETED"),
        ("ZIP CRC/single-package-root verification", "NOT_COMPLETED"),
        ("extracted ZIP Backend verification", "NOT_RUN"),
        ("extracted ZIP Flutter verification/builds", "NOT_RUN"),
        ("verifier rebuilt artifact", "false"),
        ("explicit final operator approval", "NOT_RECEIVED"),
        ("annotated tag publication", "NOT_CREATED"),
        ("GitHub Release publication", "NOT_CREATED"),
        ("post-publication downloaded asset", "NOT_DOWNLOADED"),
        ("post-publication SHA-256 verification", "NOT_COMPLETED"),
    ):
        require_associated(record, label, value, "release record")
    require(record, "that accepted artifact is invalidated", "artifact invalidation rule")
    for needle in ("release source HEAD", "verification HEAD", "artifact SHA-256"):
        require(record, needle, "source/verification/artifact separation")


def check_candidate_metadata_doc() -> None:
    metadata = read("docs/v400_release_candidate_metadata.md")
    for label, value in (
        ("Status", "IMPLEMENTED / AWAITING_REVIEW"),
        ("Control B baseline", BASELINE),
        ("Control A", "COMPLETED / VERIFIED / REVIEWED / ACCEPTED / COMMITTED / PUSHED / CLOSED"),
        ("Control A commit", BASELINE),
        ("current released version", "v3.0.0 RELEASED / ACCEPTED"),
        ("Backend candidate version", "4.0.0"),
        ("Flutter candidate version", "4.0.0+5"),
        ("candidate release", "v4.0.0 RELEASE CANDIDATE / NOT_RELEASED"),
        ("planned tag", "DRC_v4.0.0"),
        ("fixed ZIP", "NOT_BUILT"),
        ("builder invocation count", "0"),
        ("GitHub Release", "NOT_CREATED"),
        ("DRC v4.0.0", "NOT_RELEASED"),
        ("Control C", "FUTURE / NOT_AUTHORIZED"),
        ("Control D", "FUTURE / NOT_AUTHORIZED"),
        ("Control E", "FUTURE / NOT_AUTHORIZED"),
    ):
        require_associated(metadata, label, value, "candidate metadata")
    for needle in (
        "backend/app/version.py",
        "app/pubspec.yaml",
        "Control B performs candidate metadata and release-document preparation only",
        "Control C owns release-candidate verification and no-build preflight",
        "Control D owns fixed ZIP and same-artifact acceptance",
        "Control E owns publication",
    ):
        require(metadata, needle, "candidate metadata contract")


def check_protocol_doc() -> None:
    protocol = read("docs/v400_release_preparation_protocol.md")
    for label, value in (
        ("Current checkpoint", "DRC v4.0.0 Release Preparation Protocol Control B"),
        ("Control B baseline", BASELINE),
        ("current released version", "v3.0.0 RELEASED / ACCEPTED"),
        ("current v4 candidate metadata", "Backend 4.0.0 / Flutter 4.0.0+5 NOT_RELEASED"),
        ("DRC-V4 aggregate", "READY_FOR_RELEASE_PREPARATION"),
        ("DRC v4.0.0", "NOT_RELEASED"),
        ("Control A", "COMPLETED / VERIFIED / REVIEWED / ACCEPTED / COMMITTED / PUSHED / CLOSED"),
        ("Control A commit", BASELINE),
        ("Control B", "IMPLEMENTED / AWAITING_REVIEW"),
        ("Candidate Backend", "4.0.0"),
        ("Candidate Flutter", "4.0.0+5"),
        ("release notes", "RELEASE CANDIDATE / NOT_RELEASED"),
        ("release record", "PREPARED / NOT_RELEASED"),
        ("Control C", "FUTURE / NOT_AUTHORIZED"),
        ("Control D", "FUTURE / NOT_AUTHORIZED"),
        ("Control E", "FUTURE / NOT_AUTHORIZED"),
        ("fixed ZIP builder invocation count", "0"),
        ("fixed ZIP", "NOT_BUILT"),
        ("annotated tag", "NOT_CREATED"),
        ("GitHub Release", "NOT_CREATED"),
        ("stage", "NOT_AUTHORIZED / NOT_RUN"),
        ("commit", "NOT_AUTHORIZED / NOT_RUN"),
        ("push", "NOT_AUTHORIZED / NOT_RUN"),
        ("package", "NOT_AUTHORIZED / NOT_RUN"),
        ("tag", "NOT_AUTHORIZED / NOT_RUN"),
        ("publication", "NOT_AUTHORIZED / NOT_RUN"),
    ):
        require_associated(protocol, label, value, "release preparation protocol")
    for needle in (
        "No future version or build number was selected in Control A.",
        "implementation approval != stage approval",
        "stage/commit approval != push approval",
        "commit/push approval != package approval",
        "package approval != tag approval",
        "tag approval != publication approval",
        "artifact is treated as invalidated",
        "release source HEAD",
        "verification HEAD",
        "artifact SHA-256",
    ):
        require(protocol, needle, "release preparation protocol rule")


def check_coordination_docs() -> None:
    for relative in COORDINATION_DOCS:
        text = read(relative)
        for label, value in (
            ("current released version", "v3.0.0 RELEASED / ACCEPTED"),
            ("current v4 candidate metadata", "Backend 4.0.0 / Flutter 4.0.0+5 NOT_RELEASED"),
            ("Control B baseline", BASELINE),
            ("Control B", "IMPLEMENTED / AWAITING_REVIEW"),
            ("Control C", "FUTURE / NOT_AUTHORIZED"),
            ("Control D", "FUTURE / NOT_AUTHORIZED"),
            ("Control E", "FUTURE / NOT_AUTHORIZED"),
            ("DRC-V4 aggregate", "READY_FOR_RELEASE_PREPARATION"),
            ("DRC v4.0.0", "NOT_RELEASED"),
            ("Framework v6.0.0 framework-level readiness", "PARTIAL_READY / HISTORICAL_AND_STILL_TRUE"),
            ("existing v3 real runtime", "PRESERVED / RELEASED / ACCEPTED"),
            ("existing v3 replacement", "NO"),
            ("/realtime/text replacement", "NO"),
            ("real unified FW runtime", "NOT_AVAILABLE / NOT_CLAIMED"),
            ("real unified FW runtime release blocker", "NO"),
            ("fixed ZIP builder invocation count", "0"),
            ("fixed ZIP", "NOT_BUILT"),
            ("annotated tag", "NOT_CREATED"),
            ("GitHub Release", "NOT_CREATED"),
            ("stage", "NOT_AUTHORIZED / NOT_RUN"),
            ("commit", "NOT_AUTHORIZED / NOT_RUN"),
            ("push", "NOT_AUTHORIZED / NOT_RUN"),
            ("package", "NOT_AUTHORIZED / NOT_RUN"),
            ("tag", "NOT_AUTHORIZED / NOT_RUN"),
            ("publication", "NOT_AUTHORIZED / NOT_RUN"),
        ):
            require_associated(text, label, value, relative)
        require(text, "DRC v4.0.0 Release Preparation Protocol Control A: CLOSED", f"{relative} Control A")
        require(text, BASELINE, f"{relative} Control A commit")


def reject_current_state_contradictions() -> None:
    current_text = "\n".join(
        read(relative)
        for relative in (
            *COORDINATION_DOCS,
            "docs/v400_release_preparation_protocol.md",
            "docs/v400_release_candidate_metadata.md",
            "docs/v400_release_record.md",
            "release_notes/v4.0.0.md",
        )
    )
    for needle in (
        "v4.0.0 RELEASED",
        "fixed ZIP: BUILT",
        "fixed release ZIP: BUILT",
        "tag: CREATED",
        "tag: PUBLISHED",
        "annotated tag: CREATED",
        "annotated tag publication: CREATED",
        "GitHub Release: CREATED",
        "GitHub Release publication: CREATED",
        "Control C: AUTHORIZED",
        "Control D: AUTHORIZED",
        "Control E: AUTHORIZED",
        "existing v3 replacement: YES",
        "/realtime/text replacement: YES",
        "real unified FW runtime: AVAILABLE",
    ):
        reject(current_text, needle, "current-state contradiction")


def main() -> None:
    mode = determine_mode()
    check_versions()
    check_release_notes()
    check_release_record()
    check_candidate_metadata_doc()
    check_protocol_doc()
    check_coordination_docs()
    reject_current_state_contradictions()

    print(f"v400_release_candidate_metadata_source_state: {mode}")
    print("v400_release_candidate_metadata_status: implemented-awaiting-review")
    print(f"v400_release_candidate_metadata_baseline: {BASELINE}")
    print("v400_release_candidate_metadata_backend_version: 4.0.0")
    print("v400_release_candidate_metadata_flutter_version: 4.0.0+5")
    print("v400_release_candidate_metadata_current_released: v3.0.0")
    print("v400_release_candidate_metadata_v400_released: False")
    print("v400_release_candidate_metadata_fixed_zip_builder_invocation_count: 0")
    print("v400_release_candidate_metadata_fixed_zip_built: False")
    print("v400_release_candidate_metadata_tag_created: False")
    print("v400_release_candidate_metadata_github_release_created: False")
    print("v400_release_candidate_metadata_stage_commit_push_authorized: False")
    print("v400_release_candidate_metadata_package_tag_publication_authorized: False")
    print("[v400-release-candidate-metadata-check] OK")


if __name__ == "__main__":
    main()
