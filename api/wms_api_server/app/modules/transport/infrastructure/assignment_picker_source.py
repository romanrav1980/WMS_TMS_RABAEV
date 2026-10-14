"""Read-only identity for an existing unassigned ST; not an assignment permission token."""
from hashlib import sha256
import json
from typing import Any
from ..contracts_plan import TransportPlanError
from .plan_preflight import current_sources

def assignment_picker_source(cur: Any,st: str,actor: str)->dict[str,Any]:
    rows=current_sources(cur,[st],actor,None)
    if not rows:
        raise TransportPlanError("PLAN_ST_NOT_FOUND","Подготовленная СТ отсутствует",404)
    if len(rows)>200:
        raise TransportPlanError("ST_TRIP_MEMBER_BOUND_200","В СТ более200 мест; разделите выборку",409)
    if any((row["trip_id"]or 0)>0 or row["condition"]==2 for row in rows):
        raise TransportPlanError("ST_ALREADY_ASSIGNED_USE_DEFERRAL","СТ уже назначена или отгружена; используйте существующий перенос",409)
    warehouses={row["warehouse_id"]for row in rows}
    if len(warehouses)!=1:
        raise TransportPlanError("PLAN_ONE_SOURCE_WARE_REQUIRED","Для выбора рейса требуется один склад СТ",409)
    cur.execute("select ID,PALLET_UID,STDATE,ADDR from RRL_SBORKA_PALLETS where ST_NUMBER=:st_number order by ID fetch first 201 rows only",st_number=st)
    members=[{"id":r[0],"pallet_identifier":r[1],"st_date":r[2].isoformat()if r[2]else None,"address":r[3]}for r in cur]
    if len(members)!=len(rows)or any(not member["st_date"]for member in members):
        raise TransportPlanError("ST_TRIP_SOURCE_DATE_REQUIRED","Для каждого места требуется текущая дата СТ",409)
    minimum=max(member["st_date"][:10]for member in members)
    signature=sha256(json.dumps({"sources":rows,"members":members},sort_keys=True,default=str).encode()).hexdigest()
    return {"warehouse_id":next(iter(warehouses)),"source_trip_id":0,"source_trip":{"shipment_date":minimum},
            "members":members,"source_hash":signature,"purpose":"ASSIGN"}
