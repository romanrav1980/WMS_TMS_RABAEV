"""Composition of an assembled trade order and its business acknowledgments (C-0164).

The report is a WMS-internal message (schema WMS_INTERNAL_COMPOSITION_V1) queued once per physical composition; the acknowledgment is an
internal contract for the business result of SAP (the assigned source) or SKM (the active marking system). Neither is a declared SAP/SKM
wire format or a real adapter: a transport delivery is not an acknowledgment, only this explicit business result is."""
import json
from hashlib import sha256
from typing import Any, Literal, Protocol
from pydantic import AwareDatetime, Field, model_validator
from .contracts_trade_base import Key, TradeModel


class CompositionReport(TradeModel):
    warehouse_id: int = Field(strict=True, gt=0)
    order_id: Key


class CompositionAck(TradeModel):
    schema_version: Literal[1]
    warehouse_id: int = Field(strict=True, gt=0)
    system_code: Literal["SAP", "SKM"]
    sender_id: Key
    event_id: Key
    order_id: Key
    composition_no: int = Field(strict=True, ge=1)
    signature: str = Field(pattern=r"^[a-f0-9]{64}$")
    outcome: Literal["ACCEPTED", "REJECTED"]
    reason: str | None = Field(default=None, min_length=1, max_length=2000)
    occurred_at: AwareDatetime

    @model_validator(mode="after")
    def refusal_has_reason(self) -> "CompositionAck":
        if self.outcome == "REJECTED" and not self.reason:
            raise ValueError("a rejection needs its reason")
        return self


def ack_wire(body: CompositionAck) -> dict[str, Any]:
    """The whole body binds the event: the same event id with another body is a conflict, never a second answer."""
    value = body.model_dump(mode="json")
    raw = json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return {**value, "payload_hash": sha256(raw.encode()).hexdigest()}


class CompositionAckPort(Protocol):
    def report(self, body: CompositionReport, actor: str) -> dict[str, Any]: ...
    def acknowledge(self, body: CompositionAck, actor: str) -> dict[str, Any]: ...
    def orders(self, warehouse: int, limit: int, actor: str) -> dict[str, Any]: ...


def composition_ack_service() -> CompositionAckPort:
    raise RuntimeError("Order composition acknowledgments are not wired")
