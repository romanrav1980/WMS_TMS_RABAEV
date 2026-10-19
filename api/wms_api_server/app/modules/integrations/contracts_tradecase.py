"""TRADECASE document v1; acceptance is separate from physical execution."""
from decimal import Decimal
from typing import Annotated, Any, Literal, Protocol

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, PlainSerializer, model_validator

Key = Annotated[str, Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9_.:/-]+$")]
Money = Annotated[Decimal, Field(ge=0, max_digits=12, decimal_places=2, allow_inf_nan=False),
                  PlainSerializer(lambda value: format(value.normalize(), "f"), return_type=str)]
Quantity = Annotated[Decimal, Field(gt=0, max_digits=18, decimal_places=6, allow_inf_nan=False),
                     PlainSerializer(lambda value: format(value.normalize(), "f"), return_type=str)]


class TradeModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class TradeOwner(TradeModel):
    entity_type: Literal["OWNER"]
    title: str = Field(min_length=1, max_length=200)
    active: bool = True


class TradeSku(TradeModel):
    entity_type: Literal["SKU"]
    title: str = Field(min_length=1, max_length=200)
    base_uom: Literal["EA"] = "EA"
    units_per_box: int = Field(strict=True, gt=0, le=100000)
    permitted_mrc: list[Money] = Field(min_length=1, max_length=100)
    active: bool = True

    @model_validator(mode="after")
    def unique_prices(self) -> "TradeSku":
        if len(set(self.permitted_mrc)) != len(self.permitted_mrc):
            raise ValueError("Duplicate MRC")
        return self


class TradeRecipient(TradeModel):
    entity_type: Literal["RECIPIENT"]
    title: str = Field(min_length=1, max_length=200)
    target_owner_id: Key
    permitted_source_owners: list[Key] = Field(min_length=1, max_length=100)
    buyout_mode: Literal["BEFORE_PICK", "AFTER_PICK", "IN_TRANSIT"]
    osg_basis: Literal["SHIP_DATE", "DELIVERY_DATE"] = "SHIP_DATE"
    lead_time_days: int = Field(strict=True, ge=0, le=365)
    min_osg_days: int = Field(strict=True, ge=0, le=3650)
    allow_partial_pick: bool = False
    allow_partial_ship: bool = False
    allow_broken_box: bool = False
    active: bool = True

    @model_validator(mode="after")
    def unique_owners(self) -> "TradeRecipient":
        if len(set(self.permitted_source_owners)) != len(self.permitted_source_owners):
            raise ValueError("Duplicate source owner")
        return self


class TradeOrderLine(TradeModel):
    line_id: Key
    sku_id: Key
    source_owner_id: Key
    target_owner_id: Key
    mrc: Money
    quantity: Quantity
    uom: Literal["BOX", "EA"]
    min_osg_days: int = Field(strict=True, ge=0, le=3650)


class TradeOrder(TradeModel):
    entity_type: Literal["ORDER"]
    recipient_id: Key
    order_kind: Literal["OUTBOUND", "TOPUP"] = "OUTBOUND"
    parent_trip_id: Key | None = None
    planned_ship_at: AwareDatetime
    cancelled: bool = False
    lines: list[TradeOrderLine] = Field(min_length=1, max_length=200)

    @model_validator(mode="after")
    def unique_lines(self) -> "TradeOrder":
        if len({line.line_id for line in self.lines}) != len(self.lines):
            raise ValueError("Duplicate order line")
        if self.order_kind == "TOPUP" and self.parent_trip_id is None:
            raise ValueError("Topup requires parent trip")
        return self


class TradeTripLine(TradeModel):
    order_id: Key
    line_id: Key
    quantity: Quantity


class TradeTrip(TradeModel):
    entity_type: Literal["TRIP"]
    vehicle_id: Key
    planning_source: Literal["SAP", "INTERNAL"]
    planned_departure_at: AwareDatetime
    capacity_kg: Quantity
    capacity_m3: Quantity
    cancelled: bool = False
    orders: list[TradeTripLine] = Field(min_length=1, max_length=200)

    @model_validator(mode="after")
    def unique_assignments(self) -> "TradeTrip":
        if len({(line.order_id, line.line_id) for line in self.orders}) != len(self.orders):
            raise ValueError("Duplicate trip assignment")
        return self


TradePayload = Annotated[TradeOwner | TradeSku | TradeRecipient | TradeOrder | TradeTrip,
                         Field(discriminator="entity_type")]


class TradeEnvelope(TradeModel):
    schema_version: Literal[1]
    event_id: Key
    source_id: Key
    warehouse_id: int = Field(strict=True, gt=0)
    document_id: Key
    version: int = Field(strict=True, gt=0)
    occurred_at: AwareDatetime
    payload: TradePayload


class TradeSiteSetting(TradeModel):
    operation_id: Key
    expected_version: int = Field(strict=True, ge=0)
    source_id: Key
    active_skm: Key
    planning_source: Literal["SAP", "INTERNAL"]
    enabled: bool
    reason: str = Field(min_length=8, max_length=500)


class TradecaseError(RuntimeError):
    def __init__(self, code: str, status: int = 409) -> None:
        self.code = code
        self.status = status
        super().__init__(code)


class TradecaseDocuments(Protocol):
    def configure(self, warehouse_id: int, body: TradeSiteSetting, actor: str) -> dict[str, Any]: ...
    def receive(self, body: TradeEnvelope, actor: str) -> dict[str, Any]: ...
    def site(self, warehouse_id: int, actor: str) -> dict[str, Any]: ...
    def documents(self, warehouse_id: int, kind: str, after: str, limit: int, actor: str) -> dict[str, Any]: ...
    def document(self, warehouse_id: int, kind: str, external_id: str, actor: str) -> dict[str, Any]: ...

    def messages(self, warehouse_id: int, after: str, limit: int, actor: str) -> dict[str, Any]: ...
    def message(self, warehouse_id: int, event_id: str, actor: str) -> dict[str, Any]: ...
