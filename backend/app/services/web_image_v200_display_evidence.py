"""v2.0.0 Web image display evidence checkpoint.

This module records the public-safe evidence contract for the fourth v2.0.0
pre-release requirement: displaying image assets on Web. It deliberately avoids
image generation, image decoding, Flutter startup, browser automation, backend
calls, release builds, screenshot validation, or artifact writes.

The actual configured run remains an operator-only step. Public evidence should
prove the shape of the run without committing raw screenshots, raw LAN IPs,
private paths, unreviewed image artifacts, copyrighted source-image references,
or private generated prompts.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class V200WebImageDisplayEvidenceItem:
    """One required Web image display evidence item."""

    key: str
    status: str
    description: str


@dataclass(frozen=True)
class V200WebImageDisplayEvidenceResult:
    """Public-safe Day56 Web image display evidence contract."""

    status: str
    requirement_key: str
    evidence_items: tuple[V200WebImageDisplayEvidenceItem, ...]
    required_operator_markers: tuple[str, ...]
    public_safe_omissions: tuple[str, ...]
    suggested_asset_paths: tuple[str, ...]
    operator_run_required: bool
    mock_safe_default: bool
    next_focus: str


@dataclass(frozen=True)
class V200WebImageDisplayOperatorEvidenceValidation:
    """Validation result for a marker-only operator evidence summary."""

    status: str
    accepted_markers: tuple[str, ...]
    missing_markers: tuple[str, ...]
    public_safe: bool


def build_v200_web_image_display_evidence_contract() -> V200WebImageDisplayEvidenceResult:
    """Build the Day56 Web image display evidence contract.

    This function is intentionally static and side-effect free. It should not
    generate images, read Flutter assets, inspect screenshots, open browsers,
    build Web artifacts, or access the backend.
    """

    evidence_items = (
        V200WebImageDisplayEvidenceItem(
            key="public_safe_image_assets_selected",
            status="required",
            description=(
                "The configured run must use reviewed public-safe generated "
                "or placeholder image assets."
            ),
        ),
        V200WebImageDisplayEvidenceItem(
            key="flutter_asset_manifest_registration_confirmed",
            status="required",
            description=(
                "The operator must confirm required image assets are registered "
                "in the Flutter asset manifest."
            ),
        ),
        V200WebImageDisplayEvidenceItem(
            key="flutter_web_release_build_display_confirmed",
            status="required",
            description=(
                "The configured run must confirm the image surface displays in "
                "a Flutter Web build."
            ),
        ),
        V200WebImageDisplayEvidenceItem(
            key="smartphone_web_display_confirmed",
            status="required",
            description=(
                "The operator must confirm the image surface is visible from "
                "smartphone Web access to the app."
            ),
        ),
        V200WebImageDisplayEvidenceItem(
            key="missing_image_fallback_confirmed",
            status="required",
            description=(
                "The configured run must confirm a missing or unavailable image "
                "uses a visible non-crashing fallback."
            ),
        ),
        V200WebImageDisplayEvidenceItem(
            key="release_package_asset_inclusion_confirmed",
            status="required",
            description=(
                "The release package must include required public-safe image "
                "assets or placeholders."
            ),
        ),
        V200WebImageDisplayEvidenceItem(
            key="public_safe_evidence_recorded",
            status="required",
            description=(
                "Shared evidence must be marker-based and must omit raw screenshots, "
                "raw LAN IPs, private paths, unreviewed image artifacts, copyrighted "
                "source-image references, and private generated prompts."
            ),
        ),
    )

    return V200WebImageDisplayEvidenceResult(
        status="operator-evidence-contract-ready",
        requirement_key="web_image_display",
        evidence_items=evidence_items,
        required_operator_markers=(
            "public_safe_image_assets_selected",
            "flutter_asset_manifest_registration_confirmed",
            "flutter_web_release_build_display_confirmed",
            "smartphone_web_display_confirmed",
            "missing_image_fallback_confirmed",
            "release_package_asset_inclusion_confirmed",
            "public_safe_evidence_recorded",
        ),
        public_safe_omissions=(
            "raw_screenshots",
            "raw_lan_ips",
            "private_paths",
            "unreviewed_image_artifacts",
            "copyrighted_source_image_references",
            "private_generated_prompts",
            "local_image_generation_work_folders",
        ),
        suggested_asset_paths=(
            "app/assets/images/characters/gentle_mina_demo.png",
            "app/assets/images/characters/cheerful_sora_demo.png",
            "app/assets/images/characters/cool_rei_demo.png",
            "app/assets/images/backgrounds/morning_room_soft.png",
            "app/assets/images/backgrounds/night_room_calm.png",
            "app/assets/images/placeholders/character_fallback.png",
        ),
        operator_run_required=True,
        mock_safe_default=True,
        next_focus="public-repo-readiness-license-secret-hygiene",
    )


def render_v200_web_image_display_evidence(
    result: V200WebImageDisplayEvidenceResult,
) -> str:
    """Render public-safe Day56 evidence markers."""

    lines = [
        "v200_web_image_display_evidence_status: " + result.status,
        "v200_web_image_display_requirement_key: " + result.requirement_key,
        "v200_web_image_display_operator_run_required: "
        + str(result.operator_run_required),
        "v200_web_image_display_mock_safe_default: " + str(result.mock_safe_default),
        "v200_web_image_display_required_operator_markers: "
        + ",".join(result.required_operator_markers),
        "v200_web_image_display_public_safe_omissions: "
        + ",".join(result.public_safe_omissions),
        "v200_web_image_display_suggested_asset_paths: "
        + ",".join(result.suggested_asset_paths),
    ]

    for item in result.evidence_items:
        lines.append(f"v200_web_image_display_evidence_{item.key}: {item.status}")

    lines.extend(
        [
            "v200_web_image_display_default_image_generation_status: not-called",
            "v200_web_image_display_default_flutter_status: not-started",
            "v200_web_image_display_default_browser_status: not-opened",
            "v200_web_image_display_default_backend_call_status: not-called",
            "v200_web_image_display_default_release_build_status: not-built",
            "v200_web_image_display_default_screenshot_status: not-recorded",
            "v200_web_image_display_default_image_artifact_status: not-created",
            "v200_web_image_display_public_evidence_body_policy: marker-only-no-raw-screenshots",
            "v200_web_image_display_next_focus: " + result.next_focus,
        ]
    )

    return "\n".join(lines)


def validate_v200_web_image_display_operator_evidence(
    evidence: Mapping[str, object],
) -> V200WebImageDisplayOperatorEvidenceValidation:
    """Validate a redacted Web image display operator evidence shape.

    This helper checks marker booleans only. It should be used on a small
    redacted JSON summary, not on raw screenshots, image files, browser dumps,
    local build artifacts, or image-generation work folders.
    """

    contract = build_v200_web_image_display_evidence_contract()
    accepted: list[str] = []
    missing: list[str] = []

    for marker in contract.required_operator_markers:
        if evidence.get(marker) is True:
            accepted.append(marker)
        else:
            missing.append(marker)

    forbidden_publication_flags = (
        "raw_screenshots_included",
        "raw_lan_ips_included",
        "private_paths_included",
        "unreviewed_image_artifacts_included",
        "copyrighted_source_image_references_included",
        "private_generated_prompts_included",
        "local_image_generation_work_folders_included",
    )
    public_safe = all(evidence.get(flag) is not True for flag in forbidden_publication_flags)

    status = "accepted" if not missing and public_safe else "incomplete-or-unsafe"
    return V200WebImageDisplayOperatorEvidenceValidation(
        status=status,
        accepted_markers=tuple(accepted),
        missing_markers=tuple(missing),
        public_safe=public_safe,
    )
