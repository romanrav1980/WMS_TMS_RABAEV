from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/services/picking_service.py");s=p.read_text(encoding="utf-8-sig")
start=s.index("    def assign_pick_face_articul(");end=s.index("    def list_articul_replenishment_rules(",start)
old=s[start:end]
base=old[old.index("        base_params ="):old.index("        self.gateway.execute(")]
extra=old[old.index("        self.gateway.execute("):old.index("        return pick_face_articul_id")]
def dedent(text):
 return "\n".join(line[4:] if line.startswith("    ") else line for line in text.splitlines())+"\n"
header='''"""Reuse original SKU-face assignment and extended attributes in one CONFIG UOW."""
from typing import Any
import oracledb
from fastapi import HTTPException
from ....schemas import PickFaceArticulUpsertRequest
from ....transaction_gateway import TransactionGateway
from ...platform.public import stock_configuration_transaction

def _base_assign(bound: TransactionGateway,request: PickFaceArticulUpsertRequest) -> int:
'''
helpers=header+dedent(base.replace("self.gateway","bound"))+"    return pick_face_articul_id\n\n"
helpers+='''def _extended_attributes(bound: TransactionGateway,pick_face_articul_id: int,request: PickFaceArticulUpsertRequest) -> None:
'''+dedent(extra.replace("self.gateway","bound"))
out["api/wms_api_server/app/modules/inventory/infrastructure/pickface_attributes.py"]=helpers
s=s[:start]+'''    def assign_pick_face_articul(self, request: PickFaceArticulUpsertRequest) -> int:
        from ..modules.inventory.public import configure_existing_pick_face_article
        return configure_existing_pick_face_article(self.gateway,request,request.updated_by or "")

'''+s[end:];out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/public.py")
out[str(p)]=p.read_text(encoding="utf-8-sig")+"\nfrom .infrastructure.pickface_configuration import configure_existing_pick_face_article\n"
p=Path("api/wms_api_server/app/schemas.py");s=p.read_text(encoding="utf-8-sig")
start=s.index("class PickFaceArticulUpsertRequest(");end=s.index("\n\nclass ",start)
section=s[start:end].replace("priority: float =","priority: Decimal =").replace(": float | None",": Decimal | None")
s=s[:start]+section+s[end:];out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
