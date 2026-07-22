"""v2.0.0 pre-release requirements checkpoint.

This module records release requirements only. It does not call providers,
open sockets, access Google Health, synthesize audio, render images, or build
release artifacts.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class V200PrereleaseRequirement:
    key: str
    status: str
    description: str


@dataclass(frozen=True)
class V200PrereleaseRequirementsResult:
    status: str
    requirements: tuple[V200PrereleaseRequirement, ...]
    remaining_required_count: int
    next_focus: str


def build_v200_prerelease_requirements() -> V200PrereleaseRequirementsResult:
    requirements = (
        V200PrereleaseRequirement(
            key="real_llm_web_answer",
            status="required-before-v2.0.0",
            description="Use a real LLM API and confirm that answers can be generated and displayed on Web.",
        ),
        V200PrereleaseRequirement(
            key="real_tts_web_audio_output",
            status="required-before-v2.0.0",
            description="Use a real TTS API and confirm that voice output works on Web.",
        ),
        V200PrereleaseRequirement(
            key="real_google_health_sleep_data",
            status="required-before-v2.0.0",
            description="Use the real Google Health API and confirm that real sleep data can be retrieved.",
        ),
        V200PrereleaseRequirement(
            key="web_image_display",
            status="required-before-v2.0.0",
            description="Use images and confirm that they display on Web.",
        ),
        V200PrereleaseRequirement(
            key="public_repo_ready_fw_demo_app",
            status="required-before-v2.0.0",
            description="Make the repository public-ready as an AI Character Framework demo app, including LICENSE if needed.",
        ),
        V200PrereleaseRequirement(
            key="explicit_release_requirements",
            status="required-before-v2.0.0",
            description="Explicitly include the above items as release requirements.",
        ),
    )
    return V200PrereleaseRequirementsResult(
        status="documented-pending-before-v2.0.0",
        requirements=requirements,
        remaining_required_count=len(requirements),
        next_focus="real-llm-web-answer-generation",
    )


def render_v200_prerelease_requirements(result: V200PrereleaseRequirementsResult) -> str:
    lines = [
        "v200_prerelease_requirements_status: " + result.status,
        "v200_prerelease_requirements_remaining_required_count: " + str(result.remaining_required_count),
    ]
    for requirement in result.requirements:
        lines.append(f"v200_prerelease_requirement_{requirement.key}: {requirement.status}")
    lines.append("v200_prerelease_requirements_next_focus: " + result.next_focus)
    lines.append(
        "v200_prerelease_requirements_safe_summary: v2.0.0 cannot be treated as release-ready until real LLM Web answers, real TTS Web voice output, real Google Health sleep retrieval, Web image display, public repository readiness, and explicit release requirements are all verified."
    )
    return "\n".join(lines)


def requirement_keys(result: V200PrereleaseRequirementsResult) -> Iterable[str]:
    return (requirement.key for requirement in result.requirements)
