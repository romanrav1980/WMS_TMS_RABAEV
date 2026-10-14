from typing import Protocol
from pydantic import BaseModel,ConfigDict,Field

class WaitingTaskRequest(BaseModel):
    model_config=ConfigDict(extra="forbid")
    operation_id: str=Field(min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    decision_operation_id: str=Field(min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    root_identifier: str | None=Field(default=None,min_length=1,max_length=200,pattern=r"^[^\x00]+$")

class WaitingTaskError(Exception):
    def __init__(self,code: str,message: str,status: int) -> None:
        super().__init__(message)
        self.code=code
        self.status=status

class WaitingTaskPort(Protocol):
    def plan(self,request: WaitingTaskRequest,actor: str) -> dict: ...
    def read(self,decision: str,actor: str,after: int,limit: int) -> dict: ...

def waiting_task_dependency() -> WaitingTaskPort:
    raise RuntimeError("Waiting task service not wired")
