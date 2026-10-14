"""Persist warehouse scans without changing quantities; posting verifies the saved snapshot."""
import json
from decimal import Decimal, localcontext
from hashlib import sha256
from typing import Any
from fastapi import HTTPException
import oracledb
from ....transaction_gateway import TransactionGateway
from ..domain.mark_identity import canonical_mark

class TaskScanDrafts:
    def __init__(self, gateway: Any) -> None:
        self.gateway = gateway

    def context(self, task_id: int) -> dict[str, Any]:
        rows = self.gateway.fetch_all("""select t.TASK_ID,t.STATUS,t.ASSIGNED_TO,t.FROM_CELL CELL,
            nvl(t.UID_PALLET,t.SSCC) SOURCE_UID,p.ARTICUL ARTICLE,s.STOCK_VERSION,s.BASE_UOM,
            to_char(s.REMAIN,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') PHYSICAL_QUANTITY,
            nvl(pol.MARKING_REQUIRED,0) MARKING_REQUIRED,nvl(pol.POLICY_VERSION,0) POLICY_VERSION,
            RRL_STOCK_TASK_SCAN.profile_signature(p.ARTICUL) PROFILE_SIGNATURE
            from RRL_WAREHOUSE_TASK t join RRL_PALLETS p on p.UID_PALLET=nvl(t.UID_PALLET,t.SSCC)
            join RRL_REMAINS s on s.UID_POLETA=p.UID_PALLET and s.CELL=t.FROM_CELL
            left join RRL_SKU_RECEIPT_POLICY pol on pol.ARTICUL=p.ARTICUL where t.TASK_ID=:id""", {"id":task_id})
        if not rows:
            raise HTTPException(404, detail="Task source stock not found")
        result = rows[0]
        result["uid"]=result.pop("source_uid")
        result["profiles"] = self.gateway.fetch_all("""select SYSTEM_CODE,PROFILE_CODE,PROFILE_VERSION,SCAN_MODE
            from RRL_SKU_RECEIPT_PROFILE where ARTICUL=:article order by SYSTEM_CODE,PROFILE_CODE fetch first 51 rows only""",
            {"article":result["article"]})
        if len(result["profiles"])>50:
            raise HTTPException(409, detail="TASK_MARK_PROFILE_BOUND")
        return result

    def latest(self, task_id: int, actor: str) -> dict[str, Any] | None:
        rows = self.gateway.fetch_all("""select DRAFT_ID,TASK_ID,ACTOR,REQUEST_JSON,UNIT_KEYS_JSON,
            PROFILE_SIGNATURE,STOCK_VERSION,to_char(BASE_QUANTITY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') BASE_QUANTITY
            from RRL_TASK_SCAN_DRAFT where TASK_ID=:task and ACTOR=:actor
            order by CREATED_AT desc,DRAFT_ID desc fetch first 1 row only""", {"task":task_id,"actor":actor})
        if not rows:
            return None
        row=rows[0]
        row["request"]=json.loads(row.pop("request_json"))
        row["unit_keys"]=json.loads(row.pop("unit_keys_json"))
        return row

    def save(self, task_id: int, request: dict[str, Any], actor: str) -> dict[str, Any]:
        wire=json.dumps(request,sort_keys=True,separators=(",",":"),ensure_ascii=False)
        if len(wire.encode("utf-8"))>2*1024*1024:
            raise HTTPException(422,detail="TASK_SCAN_PAYLOAD_BOUND")
        with self.gateway.transaction("Persist warehouse unit scan draft") as cursor:
            try:
                cursor.execute("begin RRL_STOCK_METADATA_TX.begin_change(:actor,'warehouse_task_execute');end;",{"actor":actor})
                bound=TransactionGateway(cursor)
                old=bound.fetch_all("select TASK_ID,ACTOR,REQUEST_JSON from RRL_TASK_SCAN_DRAFT where DRAFT_ID=:id",{"id":request["draft_id"]})
                if old:
                    if old[0]["task_id"]!=task_id or old[0]["actor"]!=actor or old[0]["request_json"]!=wire:
                        raise HTTPException(409,detail="TASK_SCAN_DRAFT_CONTENT_CONFLICT")
                    return {"draft_id":request["draft_id"],"idempotent":True}
                context=TaskScanDrafts(bound).context(task_id)
                if context["status"] not in {"PLANNED","ASSIGNED","IN_PROGRESS"} or context["assigned_to"] not in {None,actor}:
                    raise HTTPException(409,detail="TASK_SCAN_EXECUTOR_OR_STATE_CONFLICT")
                if context["profile_signature"]!=request["profile_signature"] or context["stock_version"]!=request["expected_stock_version"]:
                    raise HTTPException(409,detail="TASK_SCAN_CONTEXT_CHANGED")
                keys,quantity=self.resolve(cursor,context,request["scans"])
                cursor.setinputsizes(request=oracledb.DB_TYPE_CLOB,keys=oracledb.DB_TYPE_CLOB)
                cursor.execute("""insert into RRL_TASK_SCAN_DRAFT(DRAFT_ID,TASK_ID,ACTOR,REQUEST_JSON,UNIT_KEYS_JSON,
                    PROFILE_SIGNATURE,STOCK_VERSION,SOURCE_UID,SOURCE_CELL,BASE_QUANTITY)
                    values(:draft,:task,:actor,:request,:keys,:signature,:version,:source_uid,:cell,:quantity)""",
                    {"draft":request["draft_id"],"task":task_id,"actor":actor,"request":wire,
                     "keys":json.dumps(keys,separators=(",",":")),"signature":context["profile_signature"],
                     "version":context["stock_version"],"source_uid":context["uid"],"cell":context["cell"],"quantity":quantity})
                return {"draft_id":request["draft_id"],"unit_count":len(keys),"base_quantity":format(quantity,"f"),
                        "base_uom":context["base_uom"],"stock_effect":False}
            finally:
                cursor.execute("begin RRL_STOCK_METADATA_TX.end_change;end;")

    @staticmethod
    def resolve(cursor: Any, context: dict[str, Any], scans: list[dict[str, str]]) -> tuple[list[str], Decimal]:
        batch=[];seen=set();profiles={(p["system_code"],p["profile_code"]) for p in context["profiles"] if p["scan_mode"] in {"UNIT","UNIT_OR_AGGREGATION"}}
        for index,scan in enumerate(scans):
            if (scan["system_code"],scan["profile_code"]) not in profiles:
                raise HTTPException(422,detail="TASK_SCAN_PROFILE_NOT_CONFIGURED")
            try:
                identity=canonical_mark(scan["system_code"],scan["profile_code"],scan["code"])["identity"]
            except ValueError as exc:
                raise HTTPException(422,detail=str(exc)) from exc
            digest=sha256(identity.encode("utf-8")).hexdigest();key=(scan["system_code"],digest)
            if key in seen:
                raise HTTPException(422,detail="Duplicate unique unit scan")
            seen.add(key);batch.append({"index":index,"system":scan["system_code"],"profile":scan["profile_code"],"hash":digest})
        resolved={}
        for offset in range(0,len(batch),500):
            selected=batch[offset:offset+500];payload=cursor.var(oracledb.DB_TYPE_CLOB)
            payload.setvalue(0,json.dumps(selected,separators=(",",":")))
            cursor.execute("""select j.I,u.PHYSICAL_UNIT_KEY,
                to_char(u.BASE_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,'''),u.BASE_UOM
                from json_table(:scans,'$[*]' columns(I number path '$.index',S varchar2(40) path '$.system',P varchar2(80) path '$.profile',H varchar2(64) path '$.hash'))j
                join RRL_WMS_RECEIPT_CODE c on c.SYSTEM_CODE=j.S and c.CODE_HASH=j.H
                join RRL_WMS_RECEIPT_UNIT u on u.UID_PALLET=c.UID_PALLET and u.UNIT_ID=c.UNIT_ID
                where u.CURRENT_UID=:source_uid and u.CURRENT_CELL=:cell and u.STOCK_STATUS!='ISSUED'
                and exists(select 1 from json_table(c.PROFILES_JSON,'$[*]' columns(PP varchar2(80) path '$.profile'))pr
                    where pr.PP=j.P)""",
                {"scans":payload,"source_uid":context["uid"],"cell":context["cell"]})
            for index,key,quantity,unit in cursor:
                if int(index) in resolved or unit!=context["base_uom"]:
                    raise HTTPException(409,detail="TASK_SCAN_AMBIGUOUS_OR_UOM_CONFLICT")
                resolved[int(index)]=(key,Decimal(str(quantity)))
            if any(scan["index"] not in resolved for scan in selected):
                raise HTTPException(409,detail="TASK_SCAN_UNIT_NOT_IN_SOURCE")
        physical={key:quantity for key,quantity in resolved.values()}
        with localcontext() as decimal_context:
            decimal_context.prec=50
            quantity=sum(physical.values(),Decimal(0))
        if not physical or quantity<=0:
            raise HTTPException(422,detail="No physical units selected")
        return sorted(physical),quantity
