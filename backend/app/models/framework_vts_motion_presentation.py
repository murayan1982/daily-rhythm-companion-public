"""Bounded manual presentation request for the RT-7d VTS route."""

from pydantic import BaseModel, ConfigDict, model_validator

from app.models.framework_vts_motion import FrameworkVtsMotionCommand


class FrameworkVtsMotionPresentationRequest(BaseModel):
    """Exactly one explicit, provider-neutral VTS motion command."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: str = "drc.v3.framework-vts-motion-presentation-request.1"
    command: FrameworkVtsMotionCommand

    @model_validator(mode="after")
    def validate_request(self) -> "FrameworkVtsMotionPresentationRequest":
        if self.schema_version != "drc.v3.framework-vts-motion-presentation-request.1":
            raise ValueError("unsupported VTS presentation request schema")
        if self.command.order != 1:
            raise ValueError("manual VTS presentation command order must be 1")
        return self
