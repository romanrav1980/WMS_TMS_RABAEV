"""A business transport document is separate from receipt of its message."""
from typing import Any,Literal,Protocol
from pydantic import AwareDatetime,Field,model_validator
from .contracts_tradecase import TradeModel,Key

class TripBinding(TradeModel):
    operation_id: Key
    native_task_id: int=Field(strict=True,gt=0)
    expected_trip_version: int=Field(strict=True,gt=0)
    expected_binding_version: int=Field(strict=True,ge=0)

class TransportDocumentResult(TradeModel):
    operation_id: Key
    source_id: Key
    external_event_id: Key
    expected_trip_version: int=Field(strict=True,gt=0)
    expected_binding_version: int=Field(strict=True,gt=0)
    document_version: int=Field(strict=True,gt=0)
    document_status: Literal["READY","ERROR","REVOKED"]
    external_document_id: str|None=Field(default=None,min_length=1,max_length=100)
    manifest_signature: str=Field(pattern=r"^[A-F0-9]{64}$")
    error_reason: str|None=Field(default=None,min_length=1,max_length=500)
    occurred_at: AwareDatetime

    @model_validator(mode="after")
    def evidence(self)->"TransportDocumentResult":
        if self.document_status=="READY" and not self.external_document_id:
            raise ValueError("Ready result requires the issued transport document")
        if self.document_status!="READY" and not self.error_reason:
            raise ValueError("Error or revocation requires a business reason")
        return self

class TradeTransportError(RuntimeError):
    def __init__(self,code:str,status:int)->None:
        self.code,self.status=code,status
        super().__init__(code)

class TradeTransportPort(Protocol):
    def capacity(self,ware:int,trip:str,sku:str,requested:int,actor:str)->dict[str,Any]:...
    def bind(self,ware:int,trip:str,body:TripBinding,actor:str)->dict[str,Any]:...
    def result(self,ware:int,trip:str,body:TransportDocumentResult,actor:str)->dict[str,Any]:...
    def state(self,ware:int,trip:str,actor:str)->dict[str,Any]:...
