from __future__ import annotations

from dataclasses import dataclass

from app.config import AppConfig
from app.models.sleep_provider_selection import (
    SleepProviderOption,
    SleepProviderSelectionStatus,
)


@dataclass(frozen=True)
class _SleepProviderDefinition:
    provider: str
    display_label: str
    role: str
    deprecated: bool = False
    alias_for: str | None = None
    real_operator_verification_required: bool = False


_SLEEP_PROVIDER_DEFINITIONS = (
    _SleepProviderDefinition(
        provider="mock",
        display_label="サンプルデータ",
        role="credential_free_default",
    ),
    _SleepProviderDefinition(
        provider="wearable_stub",
        display_label="ウェアラブル連携サンプル",
        role="deterministic_sample",
    ),
    _SleepProviderDefinition(
        provider="google_health",
        display_label="Google Health",
        role="configured_real_provider",
    ),
    _SleepProviderDefinition(
        provider="fitbit_stub",
        display_label="ウェアラブル連携サンプル（旧設定）",
        role="deprecated_alias",
        deprecated=True,
        alias_for="wearable_stub",
    ),
    _SleepProviderDefinition(
        provider="fitbit",
        display_label="Fitbit（実利用検証待ち）",
        role="legacy_real_provider",
        real_operator_verification_required=True,
    ),
)

_DEFINITIONS_BY_PROVIDER = {
    definition.provider: definition for definition in _SLEEP_PROVIDER_DEFINITIONS
}


def get_sleep_provider_selection_status(
    config: AppConfig,
) -> SleepProviderSelectionStatus:
    """Return backend-owned provider selection metadata without provider execution."""

    configured_provider = config.sleep_provider.strip().lower()
    definition = _DEFINITIONS_BY_PROVIDER.get(configured_provider)

    if definition is None:
        configured_label = "未対応のsleep provider設定"
        configured_role = "unsupported"
        configured_supported = False
    else:
        configured_label = definition.display_label
        configured_role = definition.role
        configured_supported = True

    options = [
        SleepProviderOption(
            provider=item.provider,
            display_label=item.display_label,
            role=item.role,
            deprecated=item.deprecated,
            alias_for=item.alias_for,
            real_operator_verification_required=(
                item.real_operator_verification_required
            ),
        )
        for item in _SLEEP_PROVIDER_DEFINITIONS
    ]

    return SleepProviderSelectionStatus(
        configured_provider=configured_provider,
        configured_provider_label=configured_label,
        configured_provider_role=configured_role,
        configured_provider_supported=configured_supported,
        provider_options=options,
        message=(
            "Sleep provider is selected by backend SLEEP_PROVIDER configuration. "
            "Changing it requires an explicit backend configuration update and restart."
        ),
    )
