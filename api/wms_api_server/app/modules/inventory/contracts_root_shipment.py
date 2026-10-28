"""C-0193: bind one existing root HU (PALLET/BOX with closed CASE children) to one existing prepared ST for one recipient."""
from typing import Any, Protocol
from pydantic import BaseModel, ConfigDict, Field
from .domain.root_shipment import RootShipmentError  # re-exported public refusal


class RootShipmentBindRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    operation_id: str = Field(strict=True, min_length=1, max_length=80, pattern=r"^[A-Za-z0-9_.:-]+$")  # + ":<task>" fits OFFLINE_EVENT_ID(100)
    shipment_identifier: str = Field(strict=True, min_length=1, max_length=100)
    scanned_root: str = Field(strict=True, min_length=1, max_length=200)
    expected_root_version: int = Field(strict=True, ge=0)


class RootShipmentPort(Protocol):
    def bind(self, request: RootShipmentBindRequest, actor: str) -> dict[str, Any]: ...


def root_shipment_service() -> RootShipmentPort:
    raise RuntimeError("Root HU shipment binding not wired")
