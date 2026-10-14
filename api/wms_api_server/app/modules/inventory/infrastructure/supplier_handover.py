"""Documentary supplier handover; no goods mutation or fabricated external ACK."""
from hashlib import sha256
from typing import Any
import json,oracledb
from ...platform.public import read_oracle_json
from ..contracts_store_returns import StoreReturnReceiveError
from .metadata_transactions import receipt_task_metadata

class SupplierHandover:
    def __init__(self,gateway: Any) -> None:
        self.gateway=gateway

    def record(self,operation_id: str,dispatch_id: str,reference: str,document_hash: str,receiver: str,actor: str) -> dict[str,Any]:
        return self._write(operation_id,"REPORT",[dispatch_id,reference,document_hash,receiver],actor)

    def confirm(self,operation_id: str,handover_id: str,reference: str,reason: str,actor: str) -> dict[str,Any]:
        return self._write(operation_id,"CONFIRM",[handover_id,reference,reason],actor)

    def _write(self,op: str,kind: str,values: list[str],actor: str) -> dict[str,Any]:
        table="RRL_SUP_RETURN_HANDOVER" if kind=="REPORT" else "RRL_SUP_RETURN_CONFIRM"
        permission="warehouse_return_dispatch" if kind=="REPORT" else "store_return_approve"
        digest=sha256(json.dumps([kind,values,actor],ensure_ascii=False,separators=(",",":")).encode()).digest()
        try:
            with receipt_task_metadata(self.gateway,"Supplier documentary handover",actor,permission) as cur:
                cur.execute("select PAYLOAD_HASH,RESULT_JSON from "+table+" where OPERATION_ID=:op",{"op":op})
                old=cur.fetchone()
                if old:
                    if old[0]!=digest:raise StoreReturnReceiveError("SUP_HANDOVER_PAYLOAD_CONFLICT","Операция уже имеет другое содержание")
                    return read_oracle_json(old[1])
                if kind=="REPORT":
                    cur.execute("select count(*)from RRL_SUP_RETURN_HANDOVER where DISPATCH_OPERATION_ID=:id",{"id":values[0]})
                else:
                    cur.execute("select count(*)from RRL_SUP_RETURN_CONFIRM where HANDOVER_OPERATION_ID=:id",{"id":values[0]})
                if cur.fetchone()[0]:raise StoreReturnReceiveError("SUP_HANDOVER_ALREADY_RECORDED","Используйте ранее сохранённое подтверждение")
                result={"operation_id":op,"source_operation_id":values[0],"status":"DOCUMENT_RECORDED" if kind=="REPORT" else "HANDOVER_CONFIRMED","stock_changed":False,"external_sap_ack":False}
                cur.setinputsizes(result_body=oracledb.DB_TYPE_CLOB)
                params={"op":op,"hash_value":digest,"source":values[0],"reference":values[1],"actor":actor,"result_body":json.dumps(result)}
                if kind=="REPORT":
                    params.update(document_hash=values[2],receiver=values[3])
                    cur.execute("insert into RRL_SUP_RETURN_HANDOVER(OPERATION_ID,PAYLOAD_HASH,DISPATCH_OPERATION_ID,DOCUMENT_REFERENCE,DOCUMENT_SHA256,RECEIVER_NAME,ACTOR,RESULT_JSON)values(:op,:hash_value,:source,:reference,:document_hash,:receiver,:actor,:result_body)",params)
                else:
                    params["reason"]=values[2]
                    cur.execute("insert into RRL_SUP_RETURN_CONFIRM(OPERATION_ID,PAYLOAD_HASH,HANDOVER_OPERATION_ID,DECISION_REFERENCE,REASON_TEXT,ACTOR,RESULT_JSON)values(:op,:hash_value,:source,:reference,:reason,:actor,:result_body)",params)
                    cur.execute("""select h.DISPATCH_OPERATION_ID,d.RECEIPT_OPERATION_ID,d.SUPPLIER_INN,d.UID_PALLET,
                    to_char(d.BASE_QTY,'TM9'),d.BASE_UOM,h.DOCUMENT_REFERENCE,h.DOCUMENT_SHA256,h.RECEIVER_NAME
                    from RRL_SUP_RETURN_HANDOVER h join RRL_STORE_RETURN_SUP_DISPATCH d on d.OPERATION_ID=h.DISPATCH_OPERATION_ID
                    where h.OPERATION_ID=:id""",{"id":values[0]})
                    row=cur.fetchone()
                    payload=dict(zip(["dispatch_operation_id","receipt_operation_id","supplier_inn","pallet_identifier","quantity","base_uom","document_reference","document_sha256","receiver_name"],row))
                    payload.update(result,confirmation_actor=actor,evidence_kind="MANUAL_DOCUMENTARY_HANDOVER",decision_reference=values[1])
                    cur.setinputsizes(payload_body=oracledb.DB_TYPE_CLOB)
                    cur.execute("insert into RRL_SAP_RECEIPT_OUTBOX(EVENT_ID,EVENT_TYPE,PAYLOAD_JSON)values(:id,'SUPPLIER_RETURN_HANDED_OVER',:payload_body)",{"id":"SUP.HANDOVER:"+sha256(op.encode()).hexdigest(),"payload_body":json.dumps(payload)})
                return result
        except oracledb.DatabaseError as exc:
            code=getattr(exc.args[0],"code",0)
            if 20800<=code<=20999:raise StoreReturnReceiveError("SUP_HANDOVER_REJECTED",str(exc.args[0]).split("\n",1)[0],403 if code==20882 else 409) from exc
            raise

    def pending(self,ware_id: int,actor: str) -> list[dict[str,Any]]:
        allowed=self.gateway.fetch_all("select count(*) ALLOWED from RUSERS where ID=:actor and nvl(DELETED,0)=0 and(WARE_ID=:ware or upper(trim(USER_GROUP))='GLOBAL_ADMIN')",{"actor":actor,"ware":ware_id})
        if allowed[0]["allowed"]!=1:raise StoreReturnReceiveError("SUP_HANDOVER_WARE_FORBIDDEN","Пользователь не назначен складу",403)
        return self.gateway.fetch_all("""select d.OPERATION_ID DISPATCH_OPERATION_ID,d.UID_PALLET,d.SUPPLIER_INN,
        h.OPERATION_ID HANDOVER_OPERATION_ID,h.DOCUMENT_REFERENCE,h.DOCUMENT_SHA256,h.RECEIVER_NAME,h.ACTOR REPORTER,
        c.OPERATION_ID CONFIRMATION_OPERATION_ID,l.STATUS LOAD_STATUS
        from RRL_STORE_RETURN_SUP_DISPATCH d join RRL_STORE_RETURN_RECEIPT r on r.OPERATION_ID=d.RECEIPT_OPERATION_ID
        join RRL_TT_HU_LOAD_FACT l on l.LOAD_OPERATION_ID=d.OPERATION_ID
        left join RRL_SUP_RETURN_HANDOVER h on h.DISPATCH_OPERATION_ID=d.OPERATION_ID
        left join RRL_SUP_RETURN_CONFIRM c on c.HANDOVER_OPERATION_ID=h.OPERATION_ID
        where r.WARE_ID=:ware order by d.CREATED_AT,d.OPERATION_ID fetch first 100 rows only""",{"ware":ware_id})
