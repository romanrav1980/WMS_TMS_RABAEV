from typing import Any,Protocol

class CaseTypePort(Protocol):
    def read(self,task_id: int,actor: str)->dict[str,Any]: ...
    def change(self,task_id: int,operation: str,metadata: dict[str,Any],actor: str)->dict[str,Any]: ...

def case_type_service()->CaseTypePort:
    raise RuntimeError("Case type service not wired")
