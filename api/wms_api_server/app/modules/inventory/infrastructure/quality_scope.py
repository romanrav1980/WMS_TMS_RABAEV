"""One CONFIG X transaction for rule version and immutable operation receipt."""
from decimal import Decimal
import hashlib
import json
from typing import Any
from ..contracts_quality_scope import QualityScopeError
from ...platform.public import stock_configuration_transaction, read_oracle_json

COLUMNS = "WARE_ID,STORE_ADDR,PLACE_CATEGORY,RULE_VERSION,ACTIVE_FLAG,CONTROL_MODE,INDEPENDENT_FLAG,SAMPLE_PERCENT,EXEMPT_WHOLE,EXEMPT_STORAGE"
NAMES = ("warehouse_id","store_addr","place_category","version","active","control_mode","independent","sample_percent","exempt_whole","exempt_storage")


def access(cur: Any, warehouse: int, actor: str, permission: str) -> None:
    cur.execute("""select 1 from RUSERS u join RRL_WARES w on w.ID=:ware
        where u.ID=:actor and nvl(u.DELETED,0)=0 and RRL_HAS_WRIGHT(u.ID,:permission)=1
        and (u.WARE_ID=w.ID or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN')""",
        ware=warehouse,actor=actor,permission=permission)
    if cur.fetchone() is None:
        raise QualityScopeError("QUALITY_SCOPE_CURRENT_WAREHOUSE_REQUIRED",403)


def read_rule(cur: Any, warehouse: int, address: str, category: str) -> dict[str, Any]:
    cur.execute("select "+COLUMNS+" from RRL_QC_SCOPE_RULE where WARE_ID=:w and STORE_ADDR=:a and PLACE_CATEGORY=:c",
                w=warehouse,a=address,c=category)
    row=cur.fetchone()
    if row is None:
        return {"warehouse_id":warehouse,"store_addr":address,"place_category":category,"version":0,"configured":False}
    result=dict(zip(NAMES,row))
    result["sample_percent"]=str(result["sample_percent"])
    result["configured"]=True
    return result


class QualityScope:
    def __init__(self, gateway: Any) -> None:
        self.gateway=gateway

    def read(self, warehouse: int, actor: str, address: str, category: str) -> dict[str, Any]:
        with self.gateway.transaction("Current addressed QC rule") as cur:
            cur.execute("set transaction read only")
            access(cur,warehouse,actor,"warehouse_settings_view")
            return read_rule(cur,warehouse,address,category)

    def save(self, warehouse: int, actor: str, body: dict[str, Any]) -> dict[str, Any]:
        wire=json.dumps({"warehouse_id":warehouse,**body},ensure_ascii=False,sort_keys=True,separators=(",",":"))
        digest=hashlib.sha256(wire.encode("utf-8")).hexdigest()
        with stock_configuration_transaction(self.gateway,"Addressed QC rule publication",actor,"warehouse_settings_edit") as cur:
            access(cur,warehouse,actor,"warehouse_settings_edit")
            cur.execute("select ACTOR,REQUEST_HASH,RESULT_JSON from RRL_QC_SCOPE_CHANGE where OPERATION_ID=:op",op=body["operation_id"])
            saved=cur.fetchone()
            if saved:
                if saved[0]!=actor or saved[1]!=digest:
                    raise QualityScopeError("QUALITY_SCOPE_OPERATION_PAYLOAD_CONFLICT")
                return read_oracle_json(saved[2])
            old=read_rule(cur,warehouse,body["store_addr"],body["place_category"])
            if old["version"]!=body["expected_version"]:
                raise QualityScopeError("QUALITY_SCOPE_VERSION_CHANGED")
            if body["store_addr"]!="*":
                cur.execute("select 1 from RRL_ADDR where ADDR=:address and nvl(DELETED3,0)=0 fetch first 2 rows only",address=body["store_addr"])
                if len(cur.fetchall())!=1:
                    raise QualityScopeError("QUALITY_SCOPE_STORE_MISSING_OR_AMBIGUOUS",422)
            params={"w":warehouse,"a":body["store_addr"],"c":body["place_category"],"v":old["version"]+1,
                    "active":int(body["active"]),"mode_name":body["control_mode"],"independent":int(body["independent"]),
                    "percent":Decimal(str(body["sample_percent"])),"whole":int(body["exempt_whole"]),"storage":int(body["exempt_storage"]),"actor":actor}
            cur.execute("""merge into RRL_QC_SCOPE_RULE d using(select :w w,:a a,:c c from dual)s
                on(d.WARE_ID=s.w and d.STORE_ADDR=s.a and d.PLACE_CATEGORY=s.c)
                when matched then update set RULE_VERSION=:v,ACTIVE_FLAG=:active,CONTROL_MODE=:mode_name,
                INDEPENDENT_FLAG=:independent,SAMPLE_PERCENT=:percent,EXEMPT_WHOLE=:whole,EXEMPT_STORAGE=:storage,
                UPDATED_BY=:actor,UPDATED_AT=systimestamp
                when not matched then insert(WARE_ID,STORE_ADDR,PLACE_CATEGORY,RULE_VERSION,ACTIVE_FLAG,CONTROL_MODE,
                INDEPENDENT_FLAG,SAMPLE_PERCENT,EXEMPT_WHOLE,EXEMPT_STORAGE,UPDATED_BY)
                values(:w,:a,:c,:v,:active,:mode_name,:independent,:percent,:whole,:storage,:actor)""",params)
            result={**read_rule(cur,warehouse,body["store_addr"],body["place_category"]),"operation_id":body["operation_id"],"stock_changed":False}
            cur.execute("""insert into RRL_QC_SCOPE_CHANGE(OPERATION_ID,ACTOR,REQUEST_HASH,REQUEST_JSON,RESULT_JSON)
                values(:op,:actor,:hash,:request,:result)""",op=body["operation_id"],actor=actor,hash=digest,request=wire,
                result=json.dumps(result,ensure_ascii=False,separators=(",",":")))
            return result
