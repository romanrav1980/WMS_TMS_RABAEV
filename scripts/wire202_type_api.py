from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/schemas.py");s=p.read_text(encoding="utf-8")
a=s.index("class PalletTypeUpsertRequest(BaseModel):");b=s.index("class MesRawSupplyCalculateRequest",a)
dto=s[a:b].strip()
dto=dto.replace("float | None = Field(default=None, ge=0)","Decimal | None = Field(default=None, ge=0, max_digits=27, decimal_places=9)")
dto=dto.replace("    active: int = 1","    final_weight_required: bool | None = None\n    active: int = Field(default=1,ge=0,le=1)")
dto=dto.replace("    pallet_type_code: str","    pallet_type_code: str = Field(min_length=1,max_length=50)").replace("    pallet_type_name: str","    pallet_type_name: str = Field(min_length=1,max_length=160)").replace('    load_unit_class: str = "PALLET"','    load_unit_class: str = Field(default="PALLET",min_length=1,max_length=20)')
new=Path("api/wms_api_server/app/modules/inventory/contracts_pallet_types.py");assert not new.exists()
out[str(new)]='"""Existing logistics carrier type contract with an explicit final weight requirement."""\nfrom decimal import Decimal\nfrom pydantic import BaseModel,Field\n\n'+dto+"\n"
out[str(p)]=s[:a]+"from .modules.inventory.contracts_pallet_types import PalletTypeUpsertRequest\n\n\n"+s[b:]
p=Path("api/wms_api_server/app/services/case_pick_service.py");s=p.read_text(encoding="utf-8")
a=s.index("    def upsert_pallet_type(");b=s.index("    def _line_for_update(",a)
out[str(p)]=s[:a]+'''    def upsert_pallet_type(self, request: PalletTypeUpsertRequest) -> int:
        from ..modules.inventory.public import upsert_existing_pallet_type
        return upsert_existing_pallet_type(self.gateway,request)

'''+s[b:]
out[str(p)]=out[str(p)].replace("                   DEFAULT_MAX_CLIENT_PALLETS,\n                   ACTIVE","                   DEFAULT_MAX_CLIENT_PALLETS,\n                   FINAL_WEIGHT_REQUIRED,ACTIVE",1)
p=Path("api/wms_api_server/app/routers/case_pick.py");s=p.read_text(encoding="utf-8").replace("request.updated_by = request.updated_by or user.username","request.updated_by = user.username")
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/pallet_types.py");assert not p.exists()
out[str(p)]='''"""Use the original global pallet types behind the existing metadata transaction."""
import json
import oracledb
from ....oracle_gateway import OracleGateway
from ..contracts_pallet_types import PalletTypeUpsertRequest
from ..contracts_stock import StockPostingError
from .metadata_transactions import receipt_task_metadata


def upsert_pallet_type(gateway: OracleGateway,request: PalletTypeUpsertRequest)->int:
    actor=request.updated_by
    if not actor:
        raise StockPostingError("PALLET_TYPE_ACTOR_REQUIRED",None,20882)
    wire=json.dumps(request.model_dump(mode="json",exclude={"updated_by"}),ensure_ascii=True,sort_keys=True,separators=(",",":"))
    try:
        with receipt_task_metadata(gateway,"Existing carrier type and final weight policy",actor,"case_pick_manage")as q:
            result=q.var(oracledb.DB_TYPE_NUMBER)
            q.callproc("RRL_PALLET_TYPE_API.upsert_request",[wire,actor,result])
            return int(result.getvalue())
    except oracledb.DatabaseError as exc:
        code=exc.args[0].code
        raise StockPostingError("PALLET_TYPE_UPDATE_REJECTED" if code and(code==1 or 20800<=code<=20899)else "RESULT_UNCERTAIN",None,code)from exc
'''
p=Path("api/wms_api_server/app/modules/inventory/public.py");out[str(p)]=p.read_text(encoding="utf-8")+'''
from .contracts_pallet_types import PalletTypeUpsertRequest

def upsert_existing_pallet_type(gateway: OracleGateway,request: PalletTypeUpsertRequest)->int:
    from .infrastructure.pallet_types import upsert_pallet_type
    return upsert_pallet_type(gateway,request)
'''
print(json.dumps(out,ensure_ascii=True))
