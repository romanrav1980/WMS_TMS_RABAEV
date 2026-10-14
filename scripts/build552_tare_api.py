import json
from pathlib import Path
out={};f="db/migrations/2026-10-12_ni063_damage_custody/"
def patch(path,a,b):
 v=out.get(path,Path(path).read_text(encoding="utf-8"));assert v.count(a)==1,(path,a,v.count(a));out[path]=v.replace(a,b)
p="api/wms_api_server/app/modules/inventory/api/tare_routes.py"
out[f+"000_before_tare_routes.py"]=Path(p).read_text(encoding="utf-8")
patch(p,'    condition: Literal["GOOD","DAMAGED"]\n    from_kind:', '    condition: Literal["GOOD","DAMAGED"]\n    damage_operation_id: str|None=Field(default=None,strict=True,min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")\n    from_kind:')
patch(p,'operation=values.pop("operation_id");source={name:values.pop(name) for name in source_fields}','damage=values.pop("damage_operation_id",None)\n    operation=values.pop("operation_id");source={name:values.pop(name) for name in source_fields}\n    if damage is not None:source["damage_operation_id"]=damage')
out[p]+="""

@router.get("/warehouses/{ware_id}/damage-custody")
def damage_custody(ware_id: int,user: AdminUser=Depends(require_permission("tare_view")),service: TarePort=Depends(tare_service)) -> dict[str,Any]:
    if ware_id<1:raise HTTPException(422,"Укажите склад-владелец")
    try:return service.damage_custody(ware_id,user.username)
    except TareError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)})from exc
"""
p="api/wms_api_server/app/modules/inventory/api/tare_resolution_routes.py"
out[f+"000_before_resolution_routes.py"]=Path(p).read_text(encoding="utf-8")
patch(p,'class Writeoff(Resolution):\n    damage_operation_id:', 'class Writeoff(Resolution):\n    writeoff_warehouse_id: int|None=Field(default=None,strict=True,ge=1)\n    damage_operation_id:')
patch(p,'values=body.model_dump();operation=values.pop("operation_id");source=', 'values=body.model_dump()\n    if values.get("writeoff_warehouse_id")is None:values.pop("writeoff_warehouse_id",None)\n    operation=values.pop("operation_id");source=')
p="api/wms_api_server/app/modules/inventory/contracts_tare.py"
out[f+"000_before_contracts_tare.py"]=Path(p).read_text(encoding="utf-8")
patch(p,'    def damage_cases(', '    def damage_custody(self,ware_id: int,actor: str) -> dict[str,Any]: ...\n    def damage_cases(')
p="api/wms_api_server/app/modules/inventory/infrastructure/tare.py"
out[f+"000_before_tare.py"]=Path(p).read_text(encoding="utf-8")
patch(p,'from ..contracts_tare import TareError', 'from ..contracts_tare import TareError\nfrom .tare_damage_custody import damage_custody')
patch(p,'    def damage_cases(', '    def damage_custody(self,ware_id: int,actor: str) -> dict[str,Any]:\n        return damage_custody(self.gateway,ware_id,actor)\n\n    def damage_cases(')
print(json.dumps(out))
