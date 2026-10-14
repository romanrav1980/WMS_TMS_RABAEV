from pathlib import Path
import ast,json
root=Path("api/wms_api_server/app");out={}
# Passive public contracts, preserving legacy import names without loading the module composition.
p=root/"schemas.py";text=p.read_text(encoding="utf-8");tree=ast.parse(text);lines=text.splitlines(keepends=True)
nodes=[x for x in tree.body if isinstance(x,ast.ClassDef)and x.name in{"StockReservationCreateRequest","StockReservationPromoteRequest","StockReservationStatusRequest"}]
assert len(nodes)==3
models="\n\n".join("".join(lines[x.lineno-1:x.end_lineno])for x in nodes)
out[str(root/"modules/inventory/contracts.py")]=""""""+'"""Passive public reservation DTOs; schemas.py retains compatibility aliases."""\nfrom decimal import Decimal\nfrom pydantic import BaseModel, Field\n\n'+models+"\n"
for node in sorted(nodes,key=lambda x:x.lineno,reverse=True):del lines[node.lineno-1:node.end_lineno]
text="from .modules.inventory.contracts import (StockReservationCreateRequest, StockReservationPromoteRequest, StockReservationStatusRequest)\n"+"".join(lines)
out[str(p)]=text
# Case endpoint construction is owned by module public composition.
out[str(root/"modules/inventory/infrastructure/case_task_services.py")]='''"""Existing CASE reads and metadata binding; no new physical executor."""
from typing import Any
from ....oracle_gateway import OracleGateway
from .case_pick_policy import case_pick_policy
from .case_shipment_binding import bind_case_shipment

class CaseTaskServices:
    def __init__(self,gateway: OracleGateway) -> None:self.gateway=gateway
    def marking_policy(self,task: int,line: int) -> dict[str,Any]:
        return case_pick_policy(self.gateway,task,line)
    def bind_shipment(self,task: int,pallet: str,container: str,version: int,actor: str) -> dict[str,Any]:
        return bind_case_shipment(self.gateway,task,pallet,container,version,actor)
'''
p=root/"modules/inventory/public.py";text=p.read_text(encoding="utf-8")
text+='''\nfrom .infrastructure.case_task_services import CaseTaskServices

def build_case_task_services() -> CaseTaskServices:
    return CaseTaskServices(OracleGateway())
'''
out[str(p)]=text
p=root/"routers/case_pick.py";text=p.read_text(encoding="utf-8")
text=text.replace("    from ..modules.inventory.public import existing_case_pick_policy\n    from ..oracle_gateway import OracleGateway","    from ..modules.inventory.public import build_case_task_services")
text=text.replace("existing_case_pick_policy(OracleGateway(), case_pick_task_id, line_id)","build_case_task_services().marking_policy(case_pick_task_id, line_id)")
text=text.replace("    from ..modules.inventory.public import bind_existing_case_shipment\n    from ..oracle_gateway import OracleGateway","    from ..modules.inventory.public import build_case_task_services")
text=text.replace("bind_existing_case_shipment(OracleGateway(), case_pick_task_id,","build_case_task_services().bind_shipment(case_pick_task_id,")
out[str(p)]=text
p=Path("admin/wms_admin_frontend/src/features/delivery/index.ts");out[str(p)]=p.read_text(encoding="utf-8")+'\nexport { StoreCasesPanel } from "./StoreCasesPanel";\n'
p=Path("admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx");out[str(p)]=p.read_text(encoding="utf-8").replace('"../features/delivery/StoreCasesPanel"','"../features/delivery"')
for path,text in out.items():
 if path.endswith(".py"):ast.parse(text)
print(json.dumps(out,ensure_ascii=True))
