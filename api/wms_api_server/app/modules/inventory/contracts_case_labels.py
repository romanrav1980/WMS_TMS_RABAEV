"""Commands for the original CASE logistic label, independent of quantity effects."""
from pydantic import BaseModel,ConfigDict,Field

class CaseSsccLabelRequest(BaseModel):
    model_config=ConfigDict(extra="forbid")
    operation_id:str=Field(min_length=1,max_length=100,pattern=r"^[ -~]+$")
    scan_container:str=Field(min_length=1,max_length=64)
    expected_content_version:int=Field(ge=0,strict=True)

class CaseSsccConfirmRequest(BaseModel):
    model_config=ConfigDict(extra="forbid")
    scan:str=Field(min_length=1,max_length=64)

from typing import Protocol
class CaseLabelPort(Protocol):
    def issue(self,task:int,request:CaseSsccLabelRequest,actor:str)->dict:...
    def current(self,task:int,actor:str)->dict:...
    def confirm(self,task:int,scan:str,actor:str)->dict:...
    def document(self,task:int,actor:str,format:str,dpi:int)->str:...
