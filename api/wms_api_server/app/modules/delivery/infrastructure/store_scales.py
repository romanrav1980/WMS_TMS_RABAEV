"""Short equipment transactions; frozen original input is never a stock command."""
import json
from typing import Any
from decimal import Decimal
import oracledb
from ...platform.public import stock_configuration_transaction
from ..contracts import StoreReceiptError
from .store_receipt_read import read_store_preview


def scale_failure(exc: oracledb.DatabaseError) -> StoreReceiptError:
    error=exc.args[0];code=abs(getattr(error,"code",0))
    status=403 if code==20882 else 409 if 20800<=code<=20999 else 503
    return StoreReceiptError("SCALE_CAPTURE_REJECTED" if status<500 else "SCALE_OUTCOME_UNCERTAIN",
                             str(error).split("\n",1)[0],status)


class StoreScales:
    def __init__(self,gateway: Any) -> None:
        self.gateway=gateway

    def configure(self,device_id: str,body: dict[str,Any],actor: str) -> dict[str,Any]:
        capacity=Decimal(body["capacity_kg"]);resolution=Decimal(body["resolution_kg"])
        if not 0<resolution<=capacity<Decimal("1000000000000000000"):
            raise StoreReceiptError("SCALE_POLICY_INVALID","Проверьте предел и дискретность весов",422)
        try:
            with stock_configuration_transaction(self.gateway,"Explicit authenticated store scale",actor,"warehouse_settings_edit") as q:
                q.execute("select count(*) from RUSERS where ID=:sender and nvl(DELETED,0)=0 and upper(trim(USER_GROUP))<>'GLOBAL_ADMIN' and RRL_HAS_WRIGHT(ID,'store_scale_ingest')=1",{"sender":body["sender_id"]})
                if q.fetchone()[0]!=1:
                    raise StoreReceiptError("SCALE_DEDICATED_SENDER_REQUIRED","Нужна отдельная действующая учётная запись шлюза с правом store_scale_ingest")
                q.execute("select POLICY_VERSION from RRL_STORE_SCALE_DEVICE where DEVICE_ID=:device for update",{"device":device_id})
                old=q.fetchone()
                if (int(old[0]) if old else 0)!=body["expected_version"]:
                    raise StoreReceiptError("SCALE_DEVICE_VERSION_CONFLICT","Обновите настройки весов")
                q.execute("""
                    merge into RRL_STORE_SCALE_DEVICE p using(select :device DEVICE_ID from dual)s on(p.DEVICE_ID=s.DEVICE_ID)
                    when matched then update set STORE_ADDR=:addr,SENDER_ID=:sender,POLICY_VERSION=POLICY_VERSION+1,
                        ACTIVE_FLAG=:active,CAPACITY_KG=:capacity,RESOLUTION_KG=:resolution,CALIBRATION_REF=:cal_ref,
                        CALIBRATED_UNTIL=to_timestamp_tz(:until_at,'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM'),CHANGED_BY=:actor,CHANGED_AT=systimestamp
                    when not matched then insert(DEVICE_ID,STORE_ADDR,SENDER_ID,POLICY_VERSION,ACTIVE_FLAG,CAPACITY_KG,RESOLUTION_KG,CALIBRATION_REF,CALIBRATED_UNTIL,CHANGED_BY)
                        values(:device,:addr,:sender,1,:active,:capacity,:resolution,:cal_ref,to_timestamp_tz(:until_at,'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM'),:actor)
                """,{"device":device_id,"addr":body["store_address"],"sender":body["sender_id"],"active":int(body["active"]),
                     "capacity":capacity,"resolution":resolution,"cal_ref":body["calibration_ref"],"until_at":body["calibrated_until"],"actor":actor})
        except oracledb.DatabaseError as exc:
            raise scale_failure(exc) from exc
        return {"device_id":device_id,"device_policy_version":body["expected_version"]+1,"active":body["active"]}

    def capture(self,body: dict[str,Any],actor: str) -> dict[str,Any]:
        packet=json.dumps(body,ensure_ascii=True,sort_keys=True,separators=(",",":"))
        try:
            with self.gateway.transaction("Archive stable store scale packet") as q:
                inp=q.var(oracledb.DB_TYPE_CLOB);out=q.var(oracledb.DB_TYPE_CLOB);inp.setvalue(0,packet)
                q.callproc("RRL_STORE_SCALE_API.capture",[inp,actor,out])
                raw=out.getvalue();result=json.loads(raw.read() if hasattr(raw,"read") else raw)
            return result
        except oracledb.DatabaseError as exc:
            raise scale_failure(exc) from exc

    def readings(self, load_operation_id: str, store_address: str, actor: str) -> dict[str,Any]:
        read_store_preview(self.gateway,load_operation_id,store_address,actor)
        rows=self.gateway.fetch_all("select RESULT_JSON from RRL_STORE_SCALE_CAPTURE where LOAD_OPERATION_ID=:op and STORE_ADDR=:addr order by RECEIVED_AT desc,CAPTURE_KEY desc fetch first 51 rows only",{"op":load_operation_id,"addr":store_address})
        return {"items":[row["result_json"] if isinstance(row["result_json"],dict) else json.loads(row["result_json"]) for row in rows[:50]],"has_older":len(rows)>50}

    def reading(self,key: str,actor: str) -> dict[str,Any]:
        rows=self.gateway.fetch_all("select LOAD_OPERATION_ID,STORE_ADDR,RESULT_JSON from RRL_STORE_SCALE_CAPTURE where CAPTURE_KEY=:key",{"key":key})
        if not rows:
            raise StoreReceiptError("SCALE_CAPTURE_NOT_FOUND","Измерение не найдено",404)
        row=rows[0]
        # Same current destination/receiver checks as the existing receipt.
        read_store_preview(self.gateway,row["load_operation_id"],row["store_addr"],actor)
        result=row["result_json"]
        return result if isinstance(result,dict) else json.loads(result)
