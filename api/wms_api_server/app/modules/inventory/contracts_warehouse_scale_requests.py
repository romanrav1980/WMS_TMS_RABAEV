"""Mass-free warehouse weighing intents and fenced gateway claims."""
from typing import Any, Literal, Protocol
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class WarehouseWeighRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    request_id: str = Field(strict=True, min_length=1, max_length=100)
    device_id: str = Field(strict=True, min_length=1, max_length=100)
    purpose: Literal["PICK", "EMPTY_TARE", "FINAL_GROSS"]
    case_task_id: int = Field(strict=True, ge=1)
    expected_content_version: int = Field(strict=True, ge=0)
    scan_container: str = Field(strict=True, min_length=1, max_length=150)
    zero_progress_required: Literal[True] | None = None
    case_line_id: int | None = Field(default=None, strict=True, ge=1)
    scan_source_cell: str | None = Field(default=None, strict=True, min_length=1, max_length=60)
    scan_product: str | None = Field(default=None, strict=True, min_length=1, max_length=512)
    resource_session_id: int | None = Field(default=None, strict=True, ge=1)
    tare_capture_key: str | None = Field(default=None, strict=True, pattern=r"^[A-F0-9]{64}$")
    expected_composition_signature: str | None = Field(default=None, strict=True, pattern=r"^[A-F0-9]{64}$")

    @field_validator("zero_progress_required", mode="before")
    @classmethod
    def strict_zero_flag(cls, value: Any) -> Any:
        if value is not None and value is not True:
            raise ValueError("Zero progress is explicitly enabled or omitted")
        return value

    @model_validator(mode="after")
    def purpose_fields(self) -> "WarehouseWeighRequest":
        pick = (self.case_line_id, self.scan_source_cell, self.scan_product)
        final = (self.tare_capture_key, self.expected_composition_signature)
        if self.purpose == "PICK" and (not all(pick) or any(final)):
            raise ValueError("PICK requires line/source/product and forbids final fields")
        if self.purpose != "PICK" and any(pick):
            raise ValueError("Line/source/product belong only to PICK")
        if self.purpose == "EMPTY_TARE" and any(final):
            raise ValueError("Empty tare precedes final measurement")
        if self.purpose == "FINAL_GROSS" and (not all(final) or self.resource_session_id is not None):
            raise ValueError("Final measurement requires measured tare and current composition")
        return self


class WarehouseWeighClaim(BaseModel):
    model_config = ConfigDict(extra="forbid")
    claim_id: str = Field(strict=True, min_length=1, max_length=100)
    device_id: str = Field(strict=True, min_length=1, max_length=100)


class WarehouseWeighZero(BaseModel):
    """Gateway-reported original OPC zero, never a loaded weight or goods fact."""
    model_config = ConfigDict(extra="forbid")
    claim_id: str = Field(strict=True, min_length=1, max_length=100)
    device_id: str = Field(strict=True, min_length=1, max_length=100)
    zero_observed_at: str = Field(strict=True, min_length=20, max_length=40)
    zero_source_sha256: str = Field(strict=True, pattern=r"^[A-F0-9]{64}$")
    zero_evidence_json: str = Field(strict=True, min_length=2, max_length=8000)
    profile_sha256: str = Field(strict=True, pattern=r"^[A-F0-9]{64}$")
    unit_namespace_uri: str = Field(strict=True, min_length=1, max_length=512)
    kg_unit_id: int = Field(strict=True)
    no_tare_mode: int = Field(strict=True)


class WarehouseWeighRequestsPort(Protocol):
    def devices(self, task: int, purpose: str, actor: str) -> dict[str, Any]: ...
    def request(self, body: dict[str, Any], actor: str) -> dict[str, Any]: ...
    def status(self, request_id: str, actor: str) -> dict[str, Any]: ...
    def pending(self, device_id: str, actor: str) -> dict[str, Any]: ...
    def claim(self, request_id: str, body: dict[str, Any], actor: str) -> dict[str, Any]: ...
    def zero(self, request_id: str, body: dict[str, Any], actor: str) -> dict[str, Any]: ...


def warehouse_weigh_requests_service() -> WarehouseWeighRequestsPort:
    raise RuntimeError("Warehouse weighing requests not wired")
