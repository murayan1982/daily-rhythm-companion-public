from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
import importlib.util
import re
import sys

from app.config import AppConfig


@dataclass(frozen=True)
class FrameworkTextChatImportLayoutCandidate:
    """Public-safe result for one candidate sys.path layout."""

    candidate_name: str
    sys_path_shapes: tuple[str, ...]
    framework_spec_status: str
    registry_spec_status: str
    safe_message: str


@dataclass(frozen=True)
class FrameworkTextChatImportLayoutDiagnosisResult:
    """Public-safe diagnosis result for vendor framework import layout."""

    status: str
    project_root_shape: str | None
    registry_file_shapes: tuple[str, ...]
    candidates: list[FrameworkTextChatImportLayoutCandidate]
    recommendation: str


class FrameworkTextChatImportLayoutDiagnosisService:
    """Diagnose vendor framework package/import layout without runtime calls.

    Day23 inspects only module discovery and repo-relative file shapes. It must
    not create sessions, call ask/ask_stream, or touch provider-backed runtime
    paths.
    """

    def __init__(self, config: AppConfig) -> None:
        self._config = config

    def run(self) -> FrameworkTextChatImportLayoutDiagnosisResult:
        project_root = self._framework_project_root()
        if project_root is None:
            return FrameworkTextChatImportLayoutDiagnosisResult(
                status="unavailable",
                project_root_shape=None,
                registry_file_shapes=(),
                candidates=[],
                recommendation=(
                    "Configure FRAMEWORK_ROOT or FRAMEWORK_PROJECT_ROOT before "
                    "running vendor framework import layout diagnosis."
                ),
            )

        if not project_root.exists():
            return FrameworkTextChatImportLayoutDiagnosisResult(
                status="unavailable",
                project_root_shape="<configured-framework-root>",
                registry_file_shapes=(),
                candidates=[],
                recommendation="Configured framework project root does not exist.",
            )

        registry_file_shapes = tuple(_find_registry_file_shapes(project_root))
        candidates = [
            self._diagnose_candidate(
                "configured-root-only",
                (project_root,),
                project_root=project_root,
            ),
            self._diagnose_candidate(
                "configured-src-only",
                (project_root / "src",),
                project_root=project_root,
            ),
            self._diagnose_candidate(
                "framework-package-dir-only",
                (project_root / "framework",),
                project_root=project_root,
            ),
            self._diagnose_candidate(
                "configured-root-plus-framework-package-dir",
                (project_root, project_root / "framework"),
                project_root=project_root,
            ),
            self._diagnose_candidate(
                "configured-src-plus-framework-package-dir",
                (project_root / "src", project_root / "src" / "framework"),
                project_root=project_root,
            ),
        ]

        status = "resolved" if any(_both_specs_found(candidate) for candidate in candidates) else "blocked"
        return FrameworkTextChatImportLayoutDiagnosisResult(
            status=status,
            project_root_shape="<configured-framework-root>",
            registry_file_shapes=registry_file_shapes,
            candidates=candidates,
            recommendation=_recommend(candidates, registry_file_shapes),
        )

    def _diagnose_candidate(
        self,
        candidate_name: str,
        paths: tuple[Path, ...],
        *,
        project_root: Path,
    ) -> FrameworkTextChatImportLayoutCandidate:
        existing_paths = tuple(path for path in paths if path.exists())
        shapes = tuple(_shape_path(path, project_root) for path in paths)
        if not existing_paths:
            return FrameworkTextChatImportLayoutCandidate(
                candidate_name=candidate_name,
                sys_path_shapes=shapes,
                framework_spec_status="path-missing",
                registry_spec_status="path-missing",
                safe_message="Candidate sys.path root does not exist.",
            )

        with _temporary_sys_path_entries(existing_paths):
            framework_status = _find_spec_status("framework")
            registry_status = _find_spec_status("registry")

        return FrameworkTextChatImportLayoutCandidate(
            candidate_name=candidate_name,
            sys_path_shapes=shapes,
            framework_spec_status=framework_status,
            registry_spec_status=registry_status,
            safe_message=_candidate_message(framework_status, registry_status),
        )

    def _framework_project_root(self) -> Path | None:
        configured = self._config.framework_project_root or getattr(
            self._config,
            "framework_root",
            None,
        )
        if not configured:
            return None
        return Path(configured)


def _both_specs_found(candidate: FrameworkTextChatImportLayoutCandidate) -> bool:
    return (
        candidate.framework_spec_status == "found"
        and candidate.registry_spec_status == "found"
    )


def _candidate_message(framework_status: str, registry_status: str) -> str:
    if framework_status == "found" and registry_status == "found":
        return "Both framework and top-level registry module specs are discoverable."
    if framework_status == "found" and registry_status != "found":
        return "framework is discoverable, but top-level registry is not."
    if framework_status != "found" and registry_status == "found":
        return "top-level registry is discoverable, but framework package is not."
    return "Neither framework nor top-level registry is discoverable from this layout."


def _find_spec_status(module_name: str) -> str:
    try:
        spec = importlib.util.find_spec(module_name)
    except Exception as exc:  # pragma: no cover - checkout dependent.
        return f"error:{type(exc).__name__}"
    return "found" if spec is not None else "missing"


def _find_registry_file_shapes(project_root: Path) -> list[str]:
    shapes: list[str] = []
    for path in sorted(project_root.rglob("registry.py")):
        if _is_ignored_path(path):
            continue
        shapes.append(_shape_path(path, project_root))
    for path in sorted(project_root.rglob("registry/__init__.py")):
        if _is_ignored_path(path):
            continue
        shapes.append(_shape_path(path, project_root))
    return shapes[:20]


def _is_ignored_path(path: Path) -> bool:
    ignored_parts = {".git", "__pycache__", ".venv", "venv", "env", "node_modules"}
    return any(part in ignored_parts for part in path.parts)


def _shape_path(path: Path, project_root: Path) -> str:
    try:
        relative = path.relative_to(project_root)
    except ValueError:
        safe = str(path)
        safe = re.sub(r"[A-Za-z]:[\\/][^\s:'\"]+", "<private-path>", safe)
        safe = re.sub(r"/(?:Users|home|mnt|tmp)/[^\s:'\"]+", "<private-path>", safe)
        return safe
    if str(relative) == ".":
        return "<configured-framework-root>"
    return "<configured-framework-root>/" + relative.as_posix()


def _recommend(
    candidates: list[FrameworkTextChatImportLayoutCandidate],
    registry_file_shapes: tuple[str, ...],
) -> str:
    by_name = {candidate.candidate_name: candidate for candidate in candidates}
    configured = by_name.get("configured-root-only")
    combined = by_name.get("configured-root-plus-framework-package-dir")

    if configured is not None and _both_specs_found(configured):
        return (
            "configured-root-only already resolves framework and top-level "
            "registry; investigate the next session-creation failure site."
        )
    if combined is not None and _both_specs_found(combined):
        return (
            "configured-root plus framework package dir resolves both specs. "
            "DRC may be able to absorb this with a narrow adapter sys.path "
            "layout, but FW-side relative import cleanup is still preferable."
        )
    if registry_file_shapes:
        return (
            "registry files exist in the configured checkout, but no tested "
            "layout resolves both framework and top-level registry. Treat this "
            "as an FW packaging/import-layout feedback item unless a narrower "
            "adapter layout is confirmed."
        )
    return (
        "No registry.py or registry package was found under the configured "
        "checkout. Treat this as an FW-side packaging/export feedback item."
    )


@contextmanager
def _temporary_sys_path_entries(paths: tuple[Path, ...]):
    path_texts = [str(path) for path in paths]
    added: list[str] = []
    for path_text in reversed(path_texts):
        if path_text not in sys.path:
            sys.path.insert(0, path_text)
            added.append(path_text)
    try:
        yield
    finally:
        for path_text in added:
            try:
                sys.path.remove(path_text)
            except ValueError:
                pass
