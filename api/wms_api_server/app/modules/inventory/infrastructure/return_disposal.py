"""Metadata report; the existing stock root alone executes destruction."""
from hashlib import sha256
from typing import Any
import json,oracledb
from ...platform.public import read_oracle_json
from ..contracts_stock import StockCommand
from ..domain.mark_identity import normalize_unit_scan_codes
from ..contracts_store_returns import StoreReturnReceiveError
from .stock_posting_uow import StockPosting
from .metadata_transactions import receipt_task_metadata

class ReturnDisposal:
    def __init__(self,gateway: Any,posting: StockPosting) -> None:
        self.gateway=gateway
        self.posting=posting

    def report(self,operation_id: str,receipt_id: str,reference: str,document_hash: str,reason: str,actor: str) -> dict[str,Any]:
        digest=sha256(json.dumps([receipt_id,reference,document_hash,reason,actor],ensure_ascii=False,separators=(",",":")).encode()).digest()
        try:
            with receipt_task_metadata(self.gateway,"Return disposal document",actor,"warehouse_return_dispatch") as cur:
                cur.execute("select PAYLOAD_HASH,RESULT_JSON from RRL_RETURN_DISPOSAL_REQUEST where OPERATION_ID=:op",{"op":operation_id})
                old=cur.fetchone()
                if old:
                    if old[0]!=digest:raise StoreReturnReceiveError("RETURN_DISPOSAL_PAYLOAD_CONFLICT","Операция уже имеет другое содержание")
                    return read_oracle_json(old[1])
                cur.execute("select count(*)from RRL_RETURN_DISPOSAL_REQUEST where RECEIPT_OPERATION_ID=:id",{"id":receipt_id})
                if cur.fetchone()[0]:raise StoreReturnReceiveError("RETURN_DISPOSAL_ALREADY_REPORTED","Используйте ранее сохранённый акт")
                result={"operation_id":operation_id,"receipt_operation_id":receipt_id,"status":"REPORTED","stock_changed":False}
                cur.setinputsizes(result_body=oracledb.DB_TYPE_CLOB)
                cur.execute("insert into RRL_RETURN_DISPOSAL_REQUEST(OPERATION_ID,PAYLOAD_HASH,RECEIPT_OPERATION_ID,DOCUMENT_REFERENCE,DOCUMENT_SHA256,REASON_TEXT,ACTOR,RESULT_JSON)values(:op,:hash_value,:receipt,:reference,:document_hash,:reason,:actor,:result_body)",{"op":operation_id,"hash_value":digest,"receipt":receipt_id,"reference":reference,"document_hash":document_hash,"reason":reason,"actor":actor,"result_body":json.dumps(result)})
                return result
        except oracledb.DatabaseError as exc:
            code=getattr(exc.args[0],"code",0)
            if 20800<=code<=20999:raise StoreReturnReceiveError("RETURN_DISPOSAL_REPORT_REJECTED",str(exc.args[0]).split("\n",1)[0],403 if code==20882 else 409) from exc
            raise

    def dispose(self,operation_id: str,request_id: str,version: int,pallet: str,cell: str,reference: str,actor: str,scans: list[dict[str,str]]|None=None) -> dict[str,Any]:
        scan_metadata={"unit_scans":normalize_unit_scan_codes(scans)}if scans else {}
        return self.posting.post(StockCommand(operation_id=operation_id,command_type="STORE_RETURN_DISPOSE",actor=actor,source={"request_operation_id":request_id},lines=(),metadata={"request_operation_id":request_id,"expected_stock_version":version,"scan_pallet":pallet,"scan_cell":cell,"decision_reference":reference,**scan_metadata}))

    def pending(self,ware_id: int,actor: str) -> list[dict[str,Any]]:
        allowed=self.gateway.fetch_all("select count(*) ALLOWED from RUSERS where ID=:actor and nvl(DELETED,0)=0 and(WARE_ID=:ware or upper(trim(USER_GROUP))='GLOBAL_ADMIN')",{"actor":actor,"ware":ware_id})
        if allowed[0]["allowed"]!=1:raise StoreReturnReceiveError("RETURN_DISPOSAL_WARE_FORBIDDEN","Пользователь не назначен складу",403)
        rows=self.gateway.fetch_all("""select r.OPERATION_ID RECEIPT_OPERATION_ID,r.UID_PALLET,r.ARTICLE,
        to_char(r.BASE_QTY,'TM9') QUANTITY,r.BASE_UOM,x.CELL,x.STOCK_VERSION,
        (select json_arrayagg(json_object('system_code'value p.SYSTEM_CODE,'profile_code'value p.PROFILE_CODE,'profile_version'value p.PROFILE_VERSION,'scan_mode'value p.SCAN_MODE)order by p.SYSTEM_CODE,p.PROFILE_CODE returning clob)from RRL_SKU_RECEIPT_PROFILE p where p.ARTICUL=r.ARTICLE) MARKED_PROFILES_JSON,
        (select count(*)from RRL_WMS_RECEIPT_UNIT u where u.CURRENT_UID=r.UID_PALLET and u.CURRENT_CELL=x.CELL and u.STOCK_STATUS='AVAILABLE') PHYSICAL_UNIT_COUNT,
        req.OPERATION_ID REQUEST_OPERATION_ID,req.DOCUMENT_REFERENCE,req.DOCUMENT_SHA256,req.ACTOR REPORTER,
        f.OPERATION_ID DISPOSAL_OPERATION_ID,f.LOSS_STORE_ADDR
        from RRL_STORE_RETURN_RECEIPT r
        left join RRL_REMAINS x on x.UID_POLETA=r.UID_PALLET and x.REMAIN>0
        left join RRL_RETURN_DISPOSAL_REQUEST req on req.RECEIPT_OPERATION_ID=r.OPERATION_ID
        left join RRL_RETURN_DISPOSAL_FACT f on f.RECEIPT_OPERATION_ID=r.OPERATION_ID
        where r.WARE_ID=:ware and r.DISPOSITION='DISPOSAL' order by r.RECEIVED_AT,r.OPERATION_ID fetch first 100 rows only""",{"ware":ware_id})
        for row in rows:
            profiles=read_oracle_json(row.pop("marked_profiles_json"))or []
            count=row.pop("physical_unit_count")
            row["marked_unit_control"]={"supported":all(p["scan_mode"]=="UNIT"for p in profiles),"physical_unit_count":count,"expected_scan_count":count*len(profiles),"profiles":profiles}if profiles else None
        return rows
