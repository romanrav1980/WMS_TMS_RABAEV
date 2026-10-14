"""Reuse legacy PALL_SPLITTER preparation; source pinning cannot alter stock."""
from hashlib import sha256
from typing import Any
import json,oracledb
from ...platform.public import read_oracle_json
from .metadata_transactions import receipt_task_metadata
from ..contracts_store_returns import StoreReturnReceiveError

class SupplierReturn:
    def __init__(self,gateway: Any) -> None:
        self.gateway=gateway

    def prepare(self,operation_id: str,receipt_id: str,supplier_inn: str,reason: str,reference: str,actor: str) -> dict[str,Any]:
        digest=sha256(json.dumps([receipt_id,supplier_inn,reason,reference,actor],ensure_ascii=False,separators=(",",":")).encode()).digest()
        try:
            with receipt_task_metadata(self.gateway,"Prepare source-pinned existing supplier ST",actor,"outgoing_pallet_edit") as cur:
                cur.execute("select count(*) from RUSERS where ID=:actor and nvl(DELETED,0)=0 and RRL_HAS_WRIGHT(ID,'store_return_approve')=1",{"actor":actor})
                if cur.fetchone()[0]!=1:raise StoreReturnReceiveError("SUP_RETURN_SC_DECISION_REQUIRED","Выбор поставщика требует полномочия Supply Chain",403)
                cur.execute("select r.WARE_ID,r.ARTICLE,r.BASE_QTY,r.BASE_UOM,r.UID_PALLET,p.TARGET_CELL from RRL_STORE_RETURN_RECEIPT r join RRL_STORE_RETURN_PLACEMENT p on p.RECEIPT_OPERATION_ID=r.OPERATION_ID where r.OPERATION_ID=:receipt and r.DISPOSITION='SUPPLIER'",{"receipt":receipt_id})
                rows=cur.fetchmany(2)
                if len(rows)!=1:raise StoreReturnReceiveError("SUP_RETURN_PLACED_SOURCE_REQUIRED","Возврат поставщику должен быть принят и размещён")
                ware,article,quantity,unit,uid,cell=rows[0]
                cur.execute("select count(*) from RUSERS where ID=:actor and nvl(DELETED,0)=0 and(WARE_ID=:ware or upper(trim(USER_GROUP))='GLOBAL_ADMIN')",{"actor":actor,"ware":ware})
                if cur.fetchone()[0]!=1:raise StoreReturnReceiveError("SUP_RETURN_WAREHOUSE_BINDING_REQUIRED","Пользователь не назначен складу",403)
                cur.execute("select PAYLOAD_HASH,RESULT_JSON from RRL_STORE_RETURN_SUP_BIND where OPERATION_ID=:op",{"op":operation_id})
                old=cur.fetchone()
                if old:
                    if old[0]!=digest:raise StoreReturnReceiveError("SUP_RETURN_PREPARATION_PAYLOAD_CONFLICT","Идентификатор операции уже имеет другое содержание")
                    return read_oracle_json(old[1])
                cur.execute("select count(*) from RRL_STORE_RETURN_SUP_BIND where RECEIPT_OPERATION_ID=:receipt",{"receipt":receipt_id})
                if cur.fetchone()[0]:raise StoreReturnReceiveError("SUP_RETURN_ALREADY_PREPARED","Используйте уже подготовленную СТ")
                cur.execute("select INN from RRL_SUPPLIERS where INN=:inn",{"inn":supplier_inn})
                if len(cur.fetchmany(2))!=1:raise StoreReturnReceiveError("SUP_RETURN_UNIQUE_SUPPLIER_REQUIRED","Выберите единственного поставщика из справочника")
                cur.execute("select count(*) from RRL_REMAINS where UID_POLETA=:lot_id and CELL=:cell and REMAIN=:qty and HARD_RESERVED_BASE=0 and BASE_UOM=:unit",{"lot_id":uid,"cell":cell,"qty":quantity,"unit":unit})
                if cur.fetchone()[0]!=1:raise StoreReturnReceiveError("SUP_RETURN_CURRENT_WHOLE_SOURCE_REQUIRED","Количество или место исходного возврата изменилось")
                number=cur.callfunc("PALL_SPLITTER.create_return_task",oracledb.DB_TYPE_VARCHAR,[supplier_inn,actor,ware])
                if not number:raise StoreReturnReceiveError("SUP_RETURN_LEGACY_PREPARATION_FAILED","Прежняя подготовка возвратной СТ отказала")
                cur.execute("select RRL_SBORKA_PALLETS_SQ.currval from dual");st_id=int(cur.fetchone()[0])
                identifier="RTN.ST:"+sha256(operation_id.encode()).hexdigest()[:40]
                cur.execute("update RRL_SBORKA_PALLETS set PALLET_UID=:identifier where ID=:id and RETURN_SUPPLIER_ID=:inn and WARE_ID=:ware",{"identifier":identifier,"id":st_id,"inn":supplier_inn,"ware":ware})
                if cur.rowcount!=1:raise StoreReturnReceiveError("SUP_RETURN_LEGACY_ST_IDENTITY_CONFLICT","Прежняя подготовка создала неподходящую СТ")
                row_id=cur.callfunc("PALL_SPLITTER.add_row_2sborka_pallets",oracledb.DB_TYPE_NUMBER,[article,quantity,identifier,ware,number])
                if not row_id:raise StoreReturnReceiveError("SUP_RETURN_LEGACY_ROWS_FAILED","Прежняя подготовка строки СТ отказала")
                cur.execute("update RRL_SBORKA_PALLET_ROWS set EI=:unit where ID=:id and ARTICUL=:article and QUANTITY=:qty",{"unit":unit,"id":int(row_id),"article":article,"qty":quantity})
                if cur.rowcount!=1:raise StoreReturnReceiveError("SUP_RETURN_LEGACY_ROWS_SOURCE_CONFLICT","Проверьте строку прежней подготовки СТ")
                result={"operation_id":operation_id,"receipt_operation_id":receipt_id,"st_id":st_id,"shipment_identifier":identifier,"st_number":number,"supplier_inn":supplier_inn,"warehouse_id":ware,"quantity":str(quantity),"base_uom":unit,"status":"PREPARED","stock_changed":False}
                cur.setinputsizes(result_body=oracledb.DB_TYPE_CLOB)
                cur.execute("insert into RRL_STORE_RETURN_SUP_BIND(OPERATION_ID,PAYLOAD_HASH,RECEIPT_OPERATION_ID,ST_ID,ST_IDENTIFIER,SUPPLIER_INN,DECISION_REFERENCE,REASON_TEXT,ACTOR,RESULT_JSON)values(:op,:hash_value,:receipt,:st,:identifier,:inn,:reference,:reason,:actor,:result_body)",{"op":operation_id,"hash_value":digest,"receipt":receipt_id,"st":st_id,"identifier":identifier,"inn":supplier_inn,"reference":reference,"reason":reason,"actor":actor,"result_body":json.dumps(result)})
                return result
        except oracledb.DatabaseError as exc:
            code=getattr(exc.args[0],"code",0)
            if 20800<=code<=20999:raise StoreReturnReceiveError("SUP_RETURN_REJECTED",str(exc.args[0]).split("\n",1)[0],403 if code==20882 else 409) from exc
            raise

    def pending(self,ware_id: int,actor: str) -> list[dict[str,Any]]:
        allowed=self.gateway.fetch_all("select count(*) ALLOWED from RUSERS where ID=:actor and nvl(DELETED,0)=0 and(WARE_ID=:ware or upper(trim(USER_GROUP))='GLOBAL_ADMIN')",{"actor":actor,"ware":ware_id})
        if allowed[0]["allowed"]!=1:raise StoreReturnReceiveError("SUP_RETURN_WAREHOUSE_FORBIDDEN","Пользователь не назначен складу",403)
        return self.gateway.fetch_all("""
            select r.OPERATION_ID RECEIPT_OPERATION_ID,r.UID_PALLET,r.ARTICLE,r.BASE_UOM,p.TARGET_CELL,
                   to_char(r.BASE_QTY,'TM9') QUANTITY,b.OPERATION_ID BIND_OPERATION_ID,b.ST_ID,b.ST_IDENTIFIER,
                   b.SUPPLIER_INN,s.NAME SUPPLIER_NAME,st.TRANSTASK_ID,st.CONDITION,d.OPERATION_ID DISPATCH_OPERATION_ID
              from RRL_STORE_RETURN_RECEIPT r join RRL_STORE_RETURN_PLACEMENT p on p.RECEIPT_OPERATION_ID=r.OPERATION_ID
               left join RRL_STORE_RETURN_SUP_BIND b on b.RECEIPT_OPERATION_ID=r.OPERATION_ID
               left join RRL_SUPPLIERS s on s.INN=b.SUPPLIER_INN
               left join RRL_SBORKA_PALLETS st on st.ID=b.ST_ID
               left join RRL_STORE_RETURN_SUP_DISPATCH d on d.BIND_OPERATION_ID=b.OPERATION_ID
             where r.WARE_ID=:ware and r.DISPOSITION='SUPPLIER' order by r.RECEIVED_AT,r.OPERATION_ID fetch first 100 rows only
        """,{"ware":ware_id})

    def suppliers(self) -> list[dict[str,Any]]:
        return self.gateway.fetch_all("select INN,NAME from RRL_SUPPLIERS order by NAME,INN fetch first 200 rows only")
