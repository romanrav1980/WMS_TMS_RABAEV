"""Corrective ST via original constructor and existing original-owner lineage."""
from hashlib import sha256
from decimal import Decimal
from typing import Any
import json
import oracledb
from ...platform.public import read_oracle_json
from ..contracts_store_returns import StoreReturnReceiveError
from .interwarehouse_onward import InterwarehouseOnward
from .metadata_transactions import receipt_task_metadata


def prepare_recovery_st(gateway: Any,operation: str,recovery_id: str,trip: int,reason: str,reference: str,actor: str) -> dict[str,Any]:
    digest=sha256(json.dumps([recovery_id,trip,reason,reference,actor],ensure_ascii=False,separators=(",",":")).encode()).digest()
    try:
        with receipt_task_metadata(gateway,"Corrective existing ST preparation",actor,"outgoing_pallet_edit")as cur:
            cur.execute("""select r.WARE_ID,r.ARTICLE,RRL_STOCK_PLAN_HELPER.decimal_text(r.BASE_QTY),r.BASE_UOM,r.ROOT_UID,
                original.SOURCE_ST_ID,original.SOURCE_LOAD_OPERATION_ID,original.RECEIPT_OPERATION_ID,
                original.FINAL_ADDRESS,original.FINAL_ADDRESS_SOURCE,original.ORIGINAL_FULFILLMENT_JSON,placed.TARGET_CELL
                from RRL_INTERWARE_RECOVERY_RECEIPT r
                join RRL_INTERWARE_SHORTAGE_FACT loss on loss.OPERATION_ID=r.LOSS_OPERATION_ID
                join RRL_INTERWARE_ONWARD_BIND original on original.RECEIPT_OPERATION_ID=loss.RECEIPT_OPERATION_ID
                join RRL_IW_RECOVERY_PLACEMENT placed on placed.RECOVERY_OPERATION_ID=r.OPERATION_ID
                join RRL_STOCK_OPERATION op on op.OPERATION_ID=r.OPERATION_ID and op.STATE='APPLIED'and op.COMMAND_TYPE='INTERWARE_SHORTAGE_RECOVER'
                where r.OPERATION_ID=:recovery_id""",recovery_id=recovery_id)
            source=cur.fetchone()
            if not source:raise StoreReturnReceiveError("RECOVERY_ST_PLACED_ORIGINAL_REQUIRED","Размещение найденного груза и исходная доставка обязательны",409)
            ware,article,qty,uom,lot,source_st,source_load,receipt_id,address,address_source,ownership_wire,cell=source
            cur.execute("""select count(*)from RUSERS where ID=:actor and nvl(DELETED,0)=0 and
                (WARE_ID=:ware or upper(trim(USER_GROUP))='GLOBAL_ADMIN')and RRL_HAS_WRIGHT(ID,'transport_dispatch_edit')=1""",actor=actor,ware=ware)
            if cur.fetchone()[0]!=1:raise StoreReturnReceiveError("RECOVERY_ST_CURRENT_WARE_REQUIRED","Требуется диспетчер текущего склада",403)
            cur.execute("select PAYLOAD_HASH,RESULT_JSON from RRL_IW_RECOVERY_ST_BIND where OPERATION_ID=:operation",operation=operation)
            previous=cur.fetchone()
            if previous:
                if previous[0]!=digest:raise StoreReturnReceiveError("RECOVERY_ST_PAYLOAD_CONFLICT","Изменено содержание исходной операции",409)
                return read_oracle_json(previous[1])
            cur.execute("select count(*)from RRL_IW_RECOVERY_ST_BIND where RECOVERY_OPERATION_ID=:recovery_id",recovery_id=recovery_id)
            if cur.fetchone()[0]:raise StoreReturnReceiveError("RECOVERY_ST_ALREADY_PREPARED","Используйте уже созданную СТ",409)
            cur.execute("""select t.ID from RRL_TRANSPORT_TASK t join RRL_TT_DOCK d on d.DOCK=t.DOCK
                where t.ID=:trip_id and t.CONDITION='Спланирован'and nvl(t.DELETED,0)=0 and t.DOCK=:cell
                and d.WARE_ID=:ware and nvl(d.DOCK_IS_BLOCKED,0)=0 for update of t.ID wait 5""",trip_id=trip,cell=cell,ware=ware)
            if not cur.fetchone():raise StoreReturnReceiveError("RECOVERY_ST_CURRENT_TRIP_REQUIRED","Плановый рейс текущего склада у исходного буфера обязателен",409)
            cur.execute("""select STOCK_VERSION from RRL_REMAINS where UID_POLETA=:lot_id and CELL=:cell
                and REMAIN=:qty and HARD_RESERVED_BASE=0 and BASE_UOM=:uom""",lot_id=lot,cell=cell,qty=Decimal(qty),uom=uom)
            stock=cur.fetchone()
            if not stock:raise StoreReturnReceiveError("RECOVERY_ST_WHOLE_STOCK_REQUIRED","Нужен весь найденный остаток без резерва",409)
            ownership=read_oracle_json(ownership_wire)
            if not ownership or len(ownership)>200 or any(x["status"]!="SHIPPED"for x in ownership):
                raise StoreReturnReceiveError("RECOVERY_ST_ORIGINAL_OWNERS_REQUIRED","Необходим исходный выполненный заказ",409)
            st,identifier,number=InterwarehouseOnward._create_st(cur,operation,address,article,qty,uom,ware,actor)
            result=dict(operation_id=operation,recovery_operation_id=recovery_id,receipt_operation_id=receipt_id,st_id=st,
                shipment_identifier=identifier,st_number=number,source_st_id=int(source_st),source_load_operation_id=source_load,
                target_trip_id=trip,warehouse_id=int(ware),pallet_identifier=lot,quantity=qty,base_uom=uom,final_address=address,
                final_address_source="ORIGINAL_ONWARD_BIND",status="PREPARED",stock_changed=False,customer_fulfillment_repeated=False)
            cur.setinputsizes(owners=oracledb.DB_TYPE_CLOB,result_body=oracledb.DB_TYPE_CLOB)
            cur.execute("""insert into RRL_IW_RECOVERY_ST_BIND(OPERATION_ID,PAYLOAD_HASH,RECOVERY_OPERATION_ID,RECEIPT_OPERATION_ID,
                ST_ID,ST_IDENTIFIER,SOURCE_ST_ID,SOURCE_LOAD_OPERATION_ID,TARGET_TT_ID,WARE_ID,ROOT_UID,STOCK_VERSION,SOURCE_CELL,
                FINAL_ADDRESS,FINAL_ADDRESS_SOURCE,ORIGINAL_FULFILLMENT_JSON,REASON_TEXT,DECISION_REFERENCE,ACTOR,RESULT_JSON)
                values(:operation,:digest,:recovery_id,:receipt,:st,:identifier,:source_st,:source_load,:trip,:ware,:lot_id,:version_no,
                :cell,:address,:address_source,:owners,:reason,:reference,:actor,:result_body)""",operation=operation,digest=digest,
                recovery_id=recovery_id,receipt=receipt_id,st=st,identifier=identifier,source_st=source_st,source_load=source_load,
                trip=trip,ware=ware,lot_id=lot,version_no=stock[0],cell=cell,address=address,address_source=address_source,
                owners=json.dumps(ownership),reason=reason,reference=reference,actor=actor,result_body=json.dumps(result))
            return result
    except oracledb.DatabaseError as exc:
        code=getattr(exc.args[0],"code",0)
        if code==1 or 20800<=code<=20999:
            raise StoreReturnReceiveError("RECOVERY_ST_REJECTED",str(exc.args[0]).split("\n",1)[0],403 if code==20882 else 409)from exc
        raise
