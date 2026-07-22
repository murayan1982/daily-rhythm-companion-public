from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class MotionBoundaryProbeResult:
    """Static no-import probe result for future FW/VTS/Live2D motion wiring."""

    framework_root: str | None
    framework_root_exists: bool
    candidate_paths: list[str] = field(default_factory=list)
    public_api_candidates: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @property
    def has_candidate_files(self) -> bool:
        return bool(self.candidate_paths)

    @property
    def has_public_api_candidates(self) -> bool:
        return bool(self.public_api_candidates)


class MotionBoundaryProbe:
    """Find likely framework Live2D/VTS motion boundaries without importing them.

    The v0.36.0 motion demo must stay safe when optional framework, VTS, or
    Live2D dependencies are absent. This probe only inspects paths and source
    text under FRAMEWORK_ROOT / FRAMEWORK_PROJECT_ROOT; it never imports the
    framework and never opens a VTube Studio WebSocket connection.
    """

    _CANDIDATE_RELATIVE_PATHS: tuple[str, ...] = (
        "framework/motion.py",
        "framework/live2d.py",
        "framework/vts.py",
        "framework/runtime/motion.py",
        "framework/runtime/live2d.py",
        "framework/runtime/vts.py",
        "framework/runtime/voice_vts.py",
        "framework/integrations/live2d.py",
        "framework/integrations/vts.py",
        "framework/app/motion.py",
        "framework/app/live2d.py",
        "framework/app/vts.py",
    )

    _PUBLIC_API_SCAN_PATHS: tuple[str, ...] = (
        "framework/__init__.py",
        "framework/facade.py",
        "framework/app_sdk.py",
        "framework/public_api.py",
        "framework/runtime/__init__.py",
    )

    _PUBLIC_API_MARKERS: tuple[str, ...] = (
        "create_motion_session",
        "create_live2d_motion_session",
        "create_vts_motion_session",
        "MotionSession",
        "Live2DMotionSession",
        "VTSMotionSession",
        "send_motion_event",
        "trigger_motion_event",
        "trigger_character_motion",
    )

    def __init__(self, framework_root: str | None) -> None:
        self._framework_root = framework_root.strip() if framework_root else None

    def run(self) -> MotionBoundaryProbeResult:
        """Return static probe metadata for status and smoke checks."""

        if not self._framework_root:
            return MotionBoundaryProbeResult(
                framework_root=None,
                framework_root_exists=False,
                notes=["FRAMEWORK_ROOT / FRAMEWORK_PROJECT_ROOT is not configured."],
            )

        root = Path(self._framework_root).expanduser()
        if not root.exists():
            return MotionBoundaryProbeResult(
                framework_root=str(root),
                framework_root_exists=False,
                notes=["Configured framework root does not exist."],
            )

        candidate_paths = self._find_existing_candidates(root)
        public_api_candidates = self._find_public_api_candidates(root)
        notes: list[str] = []
        if not candidate_paths:
            notes.append("No likely framework Live2D/VTS motion boundary files were found.")
        if candidate_paths and not public_api_candidates:
            notes.append("Candidate files exist, but no public motion API marker was found.")
        if public_api_candidates:
            notes.append("Public motion API-like markers were found; DRC adapter is still not wired.")

        return MotionBoundaryProbeResult(
            framework_root=str(root),
            framework_root_exists=True,
            candidate_paths=candidate_paths,
            public_api_candidates=public_api_candidates,
            notes=notes,
        )

    def _find_existing_candidates(self, root: Path) -> list[str]:
        found: list[str] = []
        for relative_path in self._CANDIDATE_RELATIVE_PATHS:
            path = root / relative_path
            if path.exists():
                found.append(relative_path.replace("/", "\\"))
        return found

    def _find_public_api_candidates(self, root: Path) -> list[str]:
        found: list[str] = []
        for relative_path in self._PUBLIC_API_SCAN_PATHS:
            path = root / relative_path
            if not path.exists() or not path.is_file():
                continue

            text = self._read_text_safely(path)
            for marker in self._PUBLIC_API_MARKERS:
                if marker in text:
                    found.append(f"{relative_path.replace('/', '\\')}::{marker}")
        return found

    def _read_text_safely(self, path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return ""
