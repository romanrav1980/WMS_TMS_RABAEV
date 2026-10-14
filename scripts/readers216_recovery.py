from pathlib import Path
import json,hashlib
out={};f=Path("db/migrations/2026-10-11_ni063_load_recovery")
paths=["api/wms_api_server/app/modules/inventory/infrastructure/tare_assembly.py","api/wms_api_server/app/modules/inventory/contracts_tare_assembly.py","wiki-raw/wms_admin_ui_reference/admin-nav.js","wiki-raw/wms_admin_ui_reference/transport-unloading.js","wiki-raw/wms_admin_ui_reference/transport-loading.html"]
for p in paths:out[str(f/("000_before_"+Path(p).name))]=Path(p).read_text(encoding="utf-8")
out["api/wms_api_server/app/modules/inventory/infrastructure/tare_load_recovery.py"]='''"""Read original accepted tare returns and immutable load recovery lineage."""
from typing import Any
from ..contracts_tare import TareError


def recovery_candidates(gateway: Any, load_operation_id: str, actor: str) -> list[dict[str, Any]]:
    rows = gateway.fetch_all("""
        select distinct lf.LOAD_OPERATION_ID,lf.CONTENT_VERSION EXPECTED_LOAD_VERSION,
               lf.WARE_ID,lf.STATUS LOAD_STATUS,b.OPERATION_ID ORIGINAL_BOOKING_OPERATION_ID,
               b.PALLET_TYPE_ID,typ.PALLET_TYPE_NAME,b.PLACE_ID,
               ct.SSCC PLACE_IDENTIFIER,back.OPERATION_ID RETURN_OFFER_OPERATION_ID,
               accepted.OPERATION_ID RETURN_ACCEPT_OPERATION_ID,
               accepted.ACCEPTED_BY,accepted.ACCEPTED_AT,
               recovery.OPERATION_ID RECOVERY_OPERATION_ID,replacement.STATUS RECOVERY_BOOK_STATUS
          from RRL_TT_HU_LOAD_FACT lf join RRL_TARE_OFFER_BOOK association
            on association.LOAD_OPERATION_ID=lf.LOAD_OPERATION_ID
          join RRL_TARE_BOOK b on b.OPERATION_ID=association.BOOK_OPERATION_ID
          join RRL_PALLET_TYPE typ on typ.PALLET_TYPE_ID=b.PALLET_TYPE_ID
          join RRL_CASE_PICK_TASK ct on b.PLACE_KIND='CASE'
            and b.PLACE_ID=to_char(ct.CASE_PICK_TASK_ID,'TM9')
          join RRL_TARE_ACCEPT original_accept on original_accept.OPERATION_ID=b.CLOSED_OPERATION_ID
            and original_accept.OFFER_OPERATION_ID=association.OFFER_OPERATION_ID
          join RRL_TARE_OFFER outgoing on outgoing.OPERATION_ID=association.OFFER_OPERATION_ID
          join RRL_TARE_OFFER back on back.TT_ID=lf.TT_ID and back.VEHICLE_ID=lf.VEHICLE_ID
            and back.FROM_KIND='VEHICLE' and back.TO_KIND='WAREHOUSE'
            and back.FROM_BALANCE_KEY=outgoing.TO_BALANCE_KEY and back.TO_BALANCE_KEY=b.BALANCE_KEY
            and back.OWNER_WARE_ID=b.OWNER_WARE_ID and back.PALLET_TYPE_ID=b.PALLET_TYPE_ID
            and back.CONDITION_CODE='GOOD' and back.QUANTITY=1
            and back.OFFERED_AT>=original_accept.ACCEPTED_AT
          join RRL_TARE_ACCEPT accepted on accepted.OFFER_OPERATION_ID=back.OPERATION_ID
            and accepted.ACCEPTED_QTY=1 and accepted.SHORT_QTY=0
          left join RRL_TARE_LOAD_RECOVERY recovery
            on recovery.ORIGINAL_BOOK_OPERATION_ID=b.OPERATION_ID
            and recovery.RETURN_OFFER_OPERATION_ID=back.OPERATION_ID
          left join RRL_TARE_BOOK replacement on replacement.OPERATION_ID=recovery.OPERATION_ID
         where lf.LOAD_OPERATION_ID=:load_op and b.STATUS='TRANSFERRED'
           and exists(select 1 from RUSERS u where u.ID=:actor and nvl(u.DELETED,0)=0
             and (upper(trim(u.USER_GROUP))='GLOBAL_ADMIN' or u.WARE_ID=lf.WARE_ID
               or RRL_HAS_WRIGHT(u.ID,'tare_manage')=1))
         order by ORIGINAL_BOOKING_OPERATION_ID,RETURN_OFFER_OPERATION_ID fetch first 101 rows only
    """, {"load_op": load_operation_id, "actor": actor})
    if len(rows) > 100:
        raise TareError("TARE_RECOVERY_WINDOW_REQUIRED", "Разделите список подтверждённых возвратов", 409)
    return rows
'''
p=Path(paths[0]);s=p.read_text(encoding="utf-8")
s=s.replace("from ..contracts_tare import TareError","from ..contracts_tare import TareError\nfrom .tare_load_recovery import recovery_candidates",1)
anchor="    def loaded_bookings"
idx=s.index(anchor)
s=s[:idx]+"""    def recovery_candidates(self,load_operation_id: str,actor: str) -> list[dict[str,Any]]:
        return recovery_candidates(self.gateway,load_operation_id,actor)

"""+s[idx:]
# Fix the existing bounded current cargo list to include retained nested CASE books.
s=s.replace("or(b.PLACE_KIND='CASE' and to_char(lf.ROOT_CASE_TASK_ID,'TM9')=b.PLACE_ID)","or(b.PLACE_KIND='CASE' and exists(select 1 from json_table(lf.COMPOSITION_JSON,'$.nodes[*]'columns(CASE_ID number path '$.case_task_id'))node where to_char(node.CASE_ID,'TM9')=b.PLACE_ID))")
out[str(p)]=s
p=Path(paths[1]);s=p.read_text(encoding="utf-8").replace("class TareAssemblyPort(Protocol):","class TareAssemblyPort(Protocol):\n    def recovery_candidates(self,load_operation_id: str,actor: str) -> list[dict[str,Any]]: ...",1);out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/api/tare_assembly_routes.py");s=p.read_text(encoding="utf-8").replace("APIRouter,Depends,HTTPException","APIRouter,Depends,HTTPException,Query")
s+="""
@router.get("/load-recovery-candidates")
def load_recovery_candidates(
    load_operation_id: str=Query(min_length=1,max_length=100),
    user: AdminUser=Depends(require_permission("tare_view")),
    service: TareAssemblyPort=Depends(tare_assembly_service),
) -> list[dict[str,Any]]:
    try:return service.recovery_candidates(load_operation_id,user.username)
    except TareError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)}) from exc
"""
out[str(p)]=s
p=f/"checkpoint.json";j=json.loads(p.read_text(encoding="utf-8"));j["sha256"].update({k:hashlib.sha256(v.encode()).hexdigest()for k,v in out.items()if Path(k).name.startswith("000_before_")});out[str(p)]=json.dumps(j,indent=2)+"\n"
# Correct author assertion to the actual initial warehouse count 2.
p=Path("scripts/ni063_load_tare_recovery_case.py");out[str(p)]=p.read_text(encoding="utf-8").replace('{"WAREHOUSE":1,"VEHICLE":0}','{"WAREHOUSE":2,"VEHICLE":0}').replace("vehicle1→warehouse1","vehicle1→warehouse2(initial2)/held1")
print(json.dumps(out,ensure_ascii=True))
