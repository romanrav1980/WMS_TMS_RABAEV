"""A financial instruction and its external business outcome never post physical quantity."""
import re
from typing import Any,Literal,Protocol
from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, model_validator
from .contracts_trade_stock import TradeStockRequest

class TradeBuyoutRequest(TradeStockRequest):
    buyout_id: str=Field(min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    basis_order_id: str=Field(min_length=1,max_length=100)
    basis_line_id: str=Field(min_length=1,max_length=100)
    expected_basis_version: int=Field(strict=True,gt=0)
    unit_keys: list[str]=Field(min_length=1,max_length=10000)
    demand_order_id: str | None=Field(default=None,min_length=1,max_length=100)
    demand_line_id: str | None=Field(default=None,min_length=1,max_length=100)
    load_operation_id: str | None=Field(default=None,min_length=1,max_length=100)

    @model_validator(mode="after")
    def code_set(self)->"TradeBuyoutRequest":
        if len(set(self.unit_keys))!=len(self.unit_keys)or any(not re.fullmatch('[0-9a-fA-F]{64}',k)for k in self.unit_keys):
            raise ValueError("Unique existing physical unit keys required")
        if bool(self.demand_order_id)!=bool(self.demand_line_id):raise ValueError("Demand order and line must be supplied together")
        self.unit_keys.sort()
        return self

class TradeBuyoutUnitResult(BaseModel):
    model_config=ConfigDict(extra="forbid",str_strip_whitespace=True)
    physical_unit_key: str=Field(pattern=r"^[0-9a-fA-F]{64}$")
    outcome: Literal["CONFIRMED","REJECTED","PENDING"]
    reason: str | None=Field(default=None,min_length=1,max_length=500)
    @model_validator(mode="after")
    def refusal_reason(self)->"TradeBuyoutUnitResult":
        if self.outcome=="REJECTED"and not self.reason:raise ValueError("Rejected transfer requires external reason")
        return self

class TradeBuyoutResult(TradeStockRequest):
    buyout_id: str=Field(min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    expected_version: int=Field(strict=True,gt=0)
    skm_id: str=Field(min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:/-]+$")
    external_event_id: str=Field(min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:/-]+$")
    external_document_id: str=Field(min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:/-]+$")
    occurred_at: AwareDatetime
    items: list[TradeBuyoutUnitResult]=Field(min_length=1,max_length=10000)
    @model_validator(mode="after")
    def unique_units(self)->"TradeBuyoutResult":
        if len({v.physical_unit_key for v in self.items})!=len(self.items):raise ValueError("Duplicate physical unit")
        self.items.sort(key=lambda v:v.physical_unit_key)
        return self

class TradeBuyoutPort(Protocol):
    def request_buyout(self,warehouse:int,body:TradeBuyoutRequest,actor:str)->dict[str,Any]:...
    def buyout_result(self,warehouse:int,body:TradeBuyoutResult,actor:str)->dict[str,Any]:...
    def read_buyouts(self,warehouse:int,kind:str,identity:str,after:str,limit:int,pending_only:bool,actor:str)->dict[str,Any]:...
