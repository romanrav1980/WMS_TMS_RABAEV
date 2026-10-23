"""SUPPLY composition in parts (C-0163): an additive WMS intake contract, not a declared SAP wire format.

A transfer binds source/warehouse/document/version/transfer_id. Every part repeats the SUPPLY header (all fields except codes) and
carries part_no of part_count; END repeats the same header and states the total code count and the SHA-256 of all codes joined by LF
in part order, so END may arrive before any part. Only a complete,
verified transfer becomes the same canonical SUPPLY document through the existing intake."""
from hashlib import sha256
import json
from typing import Any, Literal, Protocol
from pydantic import AwareDatetime, Field, create_model, model_validator
from .contracts_trade_base import Key, TradeModel
from .contracts_tradecase import TradeSupply, TradeSupplyCode

# The SUPPLY header is TradeSupply without its codes: the same field rules, nothing invented.
TradeSupplyHeader = create_model("TradeSupplyHeader", __base__=TradeModel,
                                 **{name: (field.annotation, field) for name, field in TradeSupply.model_fields.items() if name != "codes"})


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value: Any) -> str:
    return sha256(canonical(value).encode()).hexdigest()


class TradeSupplyPart(TradeModel):
    schema_version: Literal[1]
    event_id: Key
    source_id: Key
    warehouse_id: int = Field(strict=True, gt=0)
    document_id: Key
    version: int = Field(strict=True, gt=0)
    transfer_id: Key
    part_no: int = Field(strict=True, ge=1, le=1000)
    part_count: int = Field(strict=True, ge=1, le=1000)
    occurred_at: AwareDatetime
    header: TradeSupplyHeader  # type: ignore[valid-type]
    codes: list[TradeSupplyCode] = Field(min_length=1, max_length=10000)

    @model_validator(mode="after")
    def numbered(self) -> "TradeSupplyPart":
        if self.part_no > self.part_count:
            raise ValueError("part_no must not exceed part_count")
        if any("\n" in item.code or "\r" in item.code for item in self.codes):
            raise ValueError("Part codes must not contain line breaks used by the transfer digest")
        return self


class TradeSupplyPartsEnd(TradeModel):
    schema_version: Literal[1]
    event_id: Key
    source_id: Key
    warehouse_id: int = Field(strict=True, gt=0)
    document_id: Key
    version: int = Field(strict=True, gt=0)
    transfer_id: Key
    part_count: int = Field(strict=True, ge=1, le=1000)
    total_codes: int = Field(strict=True, ge=1, le=10000)
    codes_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    occurred_at: AwareDatetime
    header: TradeSupplyHeader  # type: ignore[valid-type]


def part_wire(body: TradeSupplyPart) -> dict[str, Any]:
    value = body.model_dump(mode="json")
    content = {k: value[k] for k in ("document_id", "version", "transfer_id", "part_no", "part_count", "header", "codes")}
    return {**value, "part_hash": digest(content), "header_hash": digest(value["header"])}


def end_wire(body: TradeSupplyPartsEnd) -> dict[str, Any]:
    value = body.model_dump(mode="json")
    content = {k: value[k] for k in ("document_id", "version", "transfer_id", "part_count", "total_codes", "codes_sha256", "header")}
    return {**value, "end_hash": digest(content), "header_hash": digest(value["header"])}


def codes_sha256(codes: list[str]) -> str:
    return sha256("\n".join(codes).encode()).hexdigest()


class SupplyTransferKey(TradeModel):
    """Hand-over retry target in the body: Key identifiers may contain '/', which a path segment cannot carry."""
    source_id: Key
    transfer_id: Key


def assembled_event_id(source: str, warehouse: int, transfer: str) -> str:
    """Deterministic event of the assembled SUPPLY: every retry/recovery hands the same message to the existing intake."""
    return "PARTS." + sha256(f"{source}|{warehouse}|{transfer}".encode()).hexdigest()[:48]


class SupplyPartsPort(Protocol):
    def put_part(self, body: TradeSupplyPart, actor: str) -> dict[str, Any]: ...
    def put_end(self, body: TradeSupplyPartsEnd, actor: str) -> dict[str, Any]: ...
    def deliver(self, warehouse: int, source: str, transfer: str, actor: str) -> dict[str, Any]: ...
    def transfers(self, warehouse: int, limit: int, actor: str) -> dict[str, Any]: ...


def supply_parts_service() -> SupplyPartsPort:
    raise RuntimeError("SUPPLY parts are not wired")
