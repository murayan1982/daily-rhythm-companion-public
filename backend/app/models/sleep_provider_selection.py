from pydantic import BaseModel


class SleepProviderOption(BaseModel):
    provider: str
    display_label: str
    role: str
    deprecated: bool = False
    alias_for: str | None = None
    real_operator_verification_required: bool = False


class SleepProviderSelectionStatus(BaseModel):
    configured_provider: str
    configured_provider_label: str
    configured_provider_role: str
    configured_provider_supported: bool
    selection_mode: str = "backend_config"
    change_requires_backend_restart: bool = True
    provider_options: list[SleepProviderOption]
    message: str
