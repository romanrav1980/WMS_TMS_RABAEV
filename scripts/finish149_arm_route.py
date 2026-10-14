from pathlib import Path
import ast,json
root=Path("api/wms_api_server/app");out={}
out[str(root/"modules/transport/contracts_operation_fact.py")]='''from typing import Any, Protocol

class OperationFactPort(Protocol):
    def write(self,operation: int,fields: dict[str,Any],actor: str) -> dict[str,Any]: ...

def operation_fact_service() -> OperationFactPort:
    raise RuntimeError("Existing ARM fact service not wired")
'''
out[str(root/"modules/transport/infrastructure/operation_fact_service.py")]='''"""Same native fact writer and existing availability-cache invalidation."""
from collections.abc import Callable
from typing import Any
from ....oracle_gateway import OracleGateway
from .operation_fact import update_existing_operation_fact

class OperationFacts:
    def __init__(self,gateway: OracleGateway,on_success: Callable[[],None]) -> None:
        self.gateway=gateway;self.on_success=on_success
    def write(self,operation: int,fields: dict[str,Any],actor: str) -> dict[str,Any]:
        result=update_existing_operation_fact(self.gateway,operation,fields,actor)
        self.on_success()
        return result
'''
out[str(root/"modules/transport/api/operation_fact_routes.py")]='''"""Original ARM fact endpoint, through the transport public port."""
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from ....schemas import OperationFactUpdate
from ...platform.public import AdminUser, require_permission
from ..contracts_operation_fact import OperationFactPort, operation_fact_service
from ..contracts_plan import TransportPlanError

router=APIRouter(prefix="/api/admin/transport",tags=["transport"])

@router.patch("/operations/{op_id}/fact")
def update_operation_fact(op_id: int,data: OperationFactUpdate,
    user: AdminUser=Depends(require_permission("transport_dispatch_edit")),
    service: OperationFactPort=Depends(operation_fact_service)) -> dict[str,Any]:
    fields=data.model_dump(exclude_none=True,mode="json")
    if not fields:raise HTTPException(400,detail="Нет полей для обновления")
    try:return service.write(op_id,fields,user.username)
    except TransportPlanError as exc:
        raise HTTPException(exc.status,detail={"code":exc.code,"message":str(exc)}) from exc
'''
# Actual error contract lives in contracts_plan? Resolve exact existing declaration.
# The same error class moves to a passive contract, original infrastructure alias retained.
p=root/"modules/transport/infrastructure/plan_application.py";text=p.read_text(encoding="utf-8")
start=text.index("class TransportPlanError(ValueError):");end=text.index("\ndef apply_existing_plan(",start)
model=text[start:end]
out[str(root/"modules/transport/contracts_plan.py")]=model+"\n"
out[str(p)]=text[:start]+"from ..contracts_plan import TransportPlanError\n"+text[end:]
p=root/"modules/transport/public.py";out[str(p)]=p.read_text(encoding="utf-8")+'''
from .contracts_operation_fact import OperationFactPort, operation_fact_service
from .api.operation_fact_routes import router as operation_fact_router
from .infrastructure.operation_fact_service import OperationFacts
'''
out[str(root/"transport_operation_composition.py")]='''"""Original availability cache and native writer wired at application composition."""
from .oracle_gateway import OracleGateway
from .services.transport_service import _clear_vehicle_availability_cache
from .modules.transport.public import OperationFactPort, OperationFacts

def build_operation_fact_service() -> OperationFactPort:
    return OperationFacts(OracleGateway(),_clear_vehicle_availability_cache)
'''
p=root/"routers/transport.py";text=p.read_text(encoding="utf-8");tree=ast.parse(text);lines=text.splitlines(keepends=True)
node=next(x for x in tree.body if isinstance(x,ast.FunctionDef)and x.name=="update_operation_fact")
start=min([node.lineno]+[x.lineno for x in node.decorator_list]);del lines[start-1:node.end_lineno]
text="".join(lines).replace("    OperationFactUpdate,\n","")
out[str(p)]=text
p=root/"main.py";out[str(p)]=p.read_text(encoding="utf-8")+'''
from .modules.transport.public import operation_fact_router, operation_fact_service
from .transport_operation_composition import build_operation_fact_service
app.dependency_overrides[operation_fact_service]=build_operation_fact_service
app.include_router(operation_fact_router)
'''
for path,text in out.items():ast.parse(text)
print(json.dumps(out,ensure_ascii=True))
