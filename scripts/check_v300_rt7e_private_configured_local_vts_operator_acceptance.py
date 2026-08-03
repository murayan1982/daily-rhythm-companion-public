"""Credential-free RT-7e Stage 1 operator-tooling verification."""

from __future__ import annotations

import argparse
import io
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
BASELINE = "715b28a97f46260efc0bd76e59828d46c8749dbd"
EXPECTED = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_rt7e_private_configured_local_vts_operator_acceptance.md",
    "scripts/check_v300_rt7e_private_configured_local_vts_operator_acceptance.py",
    "scripts/run_v300_rt7e_private_configured_local_vts_operator.py",
    "backend/tests/test_v300_rt7e_private_configured_local_vts_operator.py",
}
DOCS = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_rt7e_private_configured_local_vts_operator_acceptance.md",
}
RUNNER = "scripts/run_v300_rt7e_private_configured_local_vts_operator.py"
TEST = "backend/tests/test_v300_rt7e_private_configured_local_vts_operator.py"


def fail(message: str) -> None:
    raise SystemExit(f"v300_rt7e_gate_error: {message}")


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(ROOT), *args],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="strict",
    )
    if result.returncode != 0:
        fail(result.stderr.strip() or "git command failed")
    return result.stdout.strip()


def changed_paths() -> set[str]:
    tracked = {
        line.replace("\\", "/")
        for line in git("diff", "--name-only", "HEAD").splitlines()
        if line.strip()
    }
    untracked = {
        line.replace("\\", "/")
        for line in git(
            "ls-files",
            "--others",
            "--exclude-standard",
        ).splitlines()
        if line.strip()
    }
    return tracked | untracked


def read(relative: str) -> str:
    path = ROOT / relative
    if not path.is_file():
        fail(f"missing required file: {relative}")
    return path.read_text(encoding="utf-8")


def require(text: str, marker: str, label: str) -> None:
    if marker not in text:
        fail(f"{label} missing required marker: {marker}")


def forbid(text: str, marker: str, label: str) -> None:
    if marker in text:
        fail(f"{label} contains forbidden marker: {marker}")


def validate_scope(snapshot: bool) -> None:
    missing = sorted(path for path in EXPECTED if not (ROOT / path).is_file())
    if missing:
        fail(f"missing Stage 1 files: {missing}")
    if snapshot:
        return
    if git("rev-parse", "HEAD") != BASELINE:
        fail("HEAD is not the accepted RT-7d acceptance baseline")
    actual = changed_paths()
    if actual != EXPECTED:
        fail(
            "exact change surface mismatch: "
            f"expected={sorted(EXPECTED)}, actual={sorted(actual)}"
        )


def validate_docs() -> None:
    texts = {path: read(path) for path in DOCS}
    combined = "\n".join(texts.values())
    for marker in (
        "RT-7e operator tooling: IMPLEMENTED / AWAITING_REVIEW",
        BASELINE,
        "exact 9 files",
        "real VTube Studio operator execution: NOT_AUTHORIZED",
        "private token / hotkey read: NOT_AUTHORIZED",
        "RT-7e acceptance sync: NOT_AUTHORIZED",
        "commit / push: NOT_AUTHORIZED",
        "--execute-real-vts",
        "rt7e_acceptance_gesture",
        "http://127.0.0.1:8000",
        "provider execution attempted: false",
        "network execution attempted: false",
        "real motion executed: false",
    ):
        require(combined, marker, "RT-7e Stage 1 documentation")

    detailed = texts[
        "docs/v300_rt7e_private_configured_local_vts_operator_acceptance.md"
    ]
    for marker in (
        "Stage 1: credential-free operator tooling implementation and tests",
        "Stage 2: private configured local VTube Studio execution and acceptance",
        "backend/app/**",
        "app/lib/**",
        "one POST, no redirect, no retry, no loop",
        "at most 65536 response bytes",
        "operator tooling: implemented-awaiting-review",
        "Control A: private local VTube Studio readiness",
        "Control E: restore all real flags to zero and verify clean tree",
    ):
        require(detailed, marker, "RT-7e detailed contract")

    private_patterns = {
        "credential-shaped value": r"\b(?:sk|sess)-[A-Za-z0-9_-]{16,}\b",
        "private LAN IPv4": (
            r"\b(?:10\.(?:\d{1,3}\.){2}\d{1,3}|"
            r"192\.168\.(?:\d{1,3}\.)\d{1,3}|"
            r"172\.(?:1[6-9]|2\d|3[01])\.(?:\d{1,3}\.)\d{1,3})\b"
        ),
        "Windows private path": r"[A-Za-z]:\\(?:Users|work|private|temp)\\",
    }
    for label, pattern in private_patterns.items():
        if re.search(pattern, combined, flags=re.IGNORECASE):
            fail(f"Stage 1 documents contain {label}")


def validate_runner_source() -> None:
    runner = read(RUNNER)
    for marker in (
        'BASE_URL = "http://127.0.0.1:8000"',
        'PRESENTATION_PATH = "/demo/character-motion/vts/presentation"',
        "REQUEST_TIMEOUT_SECONDS = 10.0",
        "MAX_RESPONSE_BYTES = 65536",
        'ACCEPTANCE_GESTURE_ALIAS = "rt7e_acceptance_gesture"',
        '"--execute-real-vts"',
        'method="POST"',
        "class _NoRedirectHandler(HTTPRedirectHandler)",
        "return None",
        "if not execute_real_vts:",
        "if not _valid_fixed_base_url(base_url):",
        "response.read(MAX_RESPONSE_BYTES + 1)",
        "if confirmation() is not True:",
        "v300_rt7e_operator_http_post_count: 1",
        "v300_rt7e_operator_real_motion_executed: True",
    ):
        require(runner, marker, "RT-7e operator runner")

    for marker in (
        "os.environ",
        "load_dotenv",
        "dotenv_values",
        "backend/.env",
        "pyvts",
        "websockets",
        "AI-Character-Framework\\Development",
        "AI-Character-Framework/Development",
        "print(payload",
        "print(response",
        "json.dumps(payload",
    ):
        forbid(runner, marker, "RT-7e operator runner")

    test_text = read(TEST)
    test_names = re.findall(r"^def (test_[A-Za-z0-9_]+)\(", test_text, flags=re.MULTILINE)
    if len(test_names) != 8:
        fail(f"focused test count must remain exactly 8, got {len(test_names)}")
    for marker in (
        "test_without_explicit_flag_performs_zero_requests",
        "test_non_loopback_or_changed_backend_url_is_rejected",
        "test_fixed_gesture_request_uses_exactly_one_post",
        "test_redirect_handler_never_follows_redirects",
        "test_response_is_bounded_to_65536_bytes",
        "test_missing_completed_marker_fails_closed",
        "test_visible_motion_confirmation_false_fails",
        "test_output_never_echoes_private_or_raw_response_fields",
    ):
        require(test_text, marker, "RT-7e focused tests")


def validate_inert_runtime() -> None:
    if str(ROOT / "scripts") not in sys.path:
        sys.path.insert(0, str(ROOT / "scripts"))
    import run_v300_rt7e_private_configured_local_vts_operator as runner

    attempted: list[object] = []

    def forbidden_open(request: object, timeout: float) -> object:
        attempted.append((request, timeout))
        raise AssertionError("inert Stage 1 gate attempted HTTP")

    stdout = io.StringIO()
    stderr = io.StringIO()
    code = runner.run_operator(
        execute_real_vts=False,
        open_request=forbidden_open,
        stdout=stdout,
        stderr=stderr,
    )
    if code != 2 or attempted:
        fail("default operator runner did not remain transport-inert")
    output = stdout.getvalue()
    for marker in (
        "v300_rt7e_operator_execution_authorized: False",
        "v300_rt7e_operator_http_request_attempted: False",
        "v300_rt7e_operator_provider_execution_attempted: False",
        "v300_rt7e_operator_network_execution_attempted: False",
        "v300_rt7e_operator_real_motion_executed: False",
    ):
        require(output, marker, "inert runner output")
    if stderr.getvalue():
        fail("inert runner wrote unexpected stderr output")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Validate RT-7e credential-free Stage 1 operator tooling"
    )
    parser.add_argument(
        "--snapshot",
        action="store_true",
        help="Skip HEAD and worktree checks for an extracted candidate snapshot.",
    )
    args = parser.parse_args(argv)

    validate_scope(args.snapshot)
    validate_docs()
    validate_runner_source()
    validate_inert_runtime()

    print("v300_rt7e_status: operator-tooling-implemented-awaiting-review")
    print("v300_rt7e_baseline:", BASELINE)
    print("v300_rt7e_exact_change_surface: True")
    print("v300_rt7e_change_file_count: 9")
    print("v300_rt7d_runtime_changed: False")
    print("v300_rt7e_backend_runtime_changed: False")
    print("v300_rt7e_flutter_runtime_changed: False")
    print("v300_rt7e_existing_tests_changed: False")
    print("v300_rt7e_private_configuration_read: False")
    print("v300_rt7e_provider_execution_attempted: False")
    print("v300_rt7e_network_execution_attempted: False")
    print("v300_rt7e_real_motion_executed: False")
    print("v300_rt7e_real_operator_execution_authorized: False")
    print("v300_rt7e_private_token_hotkey_read_authorized: False")
    print("v300_rt7e_acceptance_sync_authorized: False")
    print("v300_rt7e_commit_push_authorized: False")
    print("v300_rt7e_snapshot_mode:", args.snapshot)


if __name__ == "__main__":
    main()
