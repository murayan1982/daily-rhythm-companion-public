from pydantic import BaseModel


class CapabilityStatus(BaseModel):
    """App-facing status for one demo capability."""

    status: str
    source: str
    message: str


class DemoStatusResponse(BaseModel):
    """Current demo mode and AI Character Framework capability visibility."""

    engine: str
    mode: str
    capabilities: dict[str, CapabilityStatus]
