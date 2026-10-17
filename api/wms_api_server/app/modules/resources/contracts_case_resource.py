"""Strict metadata intents and authoritative acknowledgements; no stock authority."""
from typing import Any,Literal,Protocol,Self
from datetime import datetime
from pydantic import BaseModel,ConfigDict,Field,field_validator,model_validator


class CaseResourceError(Exception):
    def __init__(self,code:str,status:int=503,operation_id:str|None=None)->None:
        super().__init__(code);self.code,self.status,self.operation_id=code,status,operation_id


class CaseResourceCommand(BaseModel):
    model_config=ConfigDict(extra="forbid",strict=True)
    operation_id:str=Field(min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    action:Literal["CLAIM","START"]
    expected_assignment_version:int=Field(ge=0)
    resource_session_id:int=Field(gt=0)
    resource_id:int|None=Field(default=None,gt=0)
    equipment_id:int|None=Field(default=None,gt=0)
    reason:str=Field(min_length=8,max_length=500)

    @field_validator("reason")
    @classmethod
    def meaningful_reason(cls,value:str)->str:
        if len(value.strip())<8:raise ValueError("Explicit reason must contain at least eight meaningful characters")
        return value


class CaseResourceState(BaseModel):
    model_config=ConfigDict(extra="forbid",strict=True)
    task_id:int=Field(gt=0)
    warehouse_id:int=Field(gt=0)
    status:str|None=Field(min_length=1,max_length=40)
    assignment_version:int=Field(ge=0)
    content_version:int|None=Field(ge=0)
    assigned_to:str|None
    resource_id:int|None=Field(ge=1)
    resource_session_id:int|None=Field(ge=1)
    equipment_id:int|None=Field(ge=1)
    started_at_instant:str|None
    started_shift_time_zone:str|None

    @field_validator("started_at_instant")
    @classmethod
    def original_instant_is_aware(cls,value:str|None)->str|None:
        if value is not None and datetime.fromisoformat(value.replace("Z","+00:00")).utcoffset()is None:raise ValueError("Original server instant must include offset")
        return value


class CaseResourceAck(CaseResourceState):
    operation_id:str
    action:Literal["CLAIM","START"]
    actor:str
    outcome:Literal["APPLIED","REJECTED"]
    request_sha256:str=Field(pattern=r"^[A-F0-9]{64}$")
    outcome_confirmed:bool
    may_create_corrected_operation:bool
    error_code:str|None
    changed:bool
    stock_posted:bool

    @model_validator(mode="after")
    def final_metadata_only_outcome(self)->Self:
        if self.outcome=="APPLIED"and(self.status is None or self.content_version is None):raise ValueError("Applied metadata requires known CASE state")
        if not self.outcome_confirmed or self.stock_posted:raise ValueError("Metadata outcome must be confirmed without stock effect")
        rejected=self.outcome=="REJECTED"
        if rejected and(self.changed or not self.error_code):raise ValueError("Rejected metadata cannot change CASE")
        if self.may_create_corrected_operation!=rejected or(not rejected and self.error_code is not None):raise ValueError("Inconsistent corrective acknowledgement")
        return self


class CaseResourcePort(Protocol):
    def context(self,task:int,actor:str)->dict[str,Any]:...
    def sessions(self,task:int,actor:str)->dict[str,Any]:...
    def command(self,task:int,body:CaseResourceCommand,actor:str)->dict[str,Any]:...
    def receipt(self,operation:str,actor:str)->dict[str,Any]:...
    def transfer_receipt(self,task:int,event:str,actor:str)->dict[str,Any]:...


def case_resource_service()->CaseResourcePort:
    raise RuntimeError("CASE resource commands are not wired")
