"""Bind external legal-order rules to the existing native customer-order planner."""
from typing import Any, Protocol
from pydantic import BaseModel, ConfigDict, Field, model_validator

class TradeOrderRowMap(BaseModel):
    model_config=ConfigDict(extra="forbid",str_strip_whitespace=True)
    line_id: str=Field(min_length=1,max_length=100)
    customer_order_row_id: int=Field(strict=True,gt=0)

class TradeOrderBind(BaseModel):
    model_config=ConfigDict(extra="forbid",str_strip_whitespace=True)
    operation_id: str=Field(min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    expected_order_version: int=Field(strict=True,gt=0)
    customer_order_id: int=Field(strict=True,gt=0)
    lines: list[TradeOrderRowMap]=Field(min_length=1,max_length=200)

    @model_validator(mode="after")
    def unique_rows(self)->"TradeOrderBind":
        if len({v.line_id for v in self.lines})!=len(self.lines)or len({v.customer_order_row_id for v in self.lines})!=len(self.lines):
            raise ValueError("Order-line mapping must be one-to-one")
        return self

class TradePlanningError(RuntimeError):
    def __init__(self,code:str,status:int=409)->None:
        self.code,self.status=code,status
        super().__init__(code)

class TradePlanningPort(Protocol):
    def bind(self,warehouse:int,order:str,body:TradeOrderBind,actor:str)->dict[str,Any]:...
