"""Prepare every original ST continuation in one metadata transaction."""
from hashlib import sha256
import json
from decimal import Decimal
from typing import Any
import oracledb
from ...platform.public import read_oracle_json
from .metadata_transactions import receipt_task_metadata
from .interwarehouse_onward import InterwarehouseOnward
from ..contracts_store_returns import StoreReturnReceiveError


def _scope(q: Any,receipt: str,actor: str)->tuple[Any,...]:
    q.execute("""select r.WARE_ID,p.SOURCE_LOAD_OPERATION_ID,p.TARGET_TT_ID,p.OUTBOUND_DOCK
        from RRL_IW_GROUP_RECEIPT r join RRL_IW_GROUP_PLAN p on p.OPERATION_ID=r.PLAN_OPERATION_ID
        where r.OPERATION_ID=:receipt_id""",receipt_id=receipt)
    row=q.fetchone()
    if row is None:raise StoreReturnReceiveError("INTERWARE_GROUP_RECEIPT_REQUIRED","Actual group receipt required")
    q.execute("""select count(*)from RUSERS where ID=:actor and nvl(DELETED,0)=0
        and RRL_HAS_WRIGHT(ID,'transport_dispatch_edit')=1 and RRL_HAS_WRIGHT(ID,'outgoing_pallet_edit')=1
        and(WARE_ID=:ware or upper(trim(USER_GROUP))='GLOBAL_ADMIN')""",actor=actor,ware=row[0])
    if q.fetchone()[0]!=1:raise StoreReturnReceiveError("INTERWARE_GROUP_DISPATCHER_REQUIRED","Current warehouse dispatcher required",403)
    return row


def _part(q: Any,operation: str,receipt: str,row: tuple[Any,...],source: tuple[Any,...],actor: str)->dict[str,Any]:
    lot,article,qty,unit,source_st=source;ware,load,trip,dock=row
    q.execute("""select r.STOCK_VERSION from RRL_REMAINS r
        join RRL_IW_GROUP_PLACEMENT p on p.RECEIPT_OPERATION_ID=:receipt_id and p.TARGET_CELL=r.CELL
        join RRL_IW_GROUP_CUSTODY c on c.RECEIPT_OPERATION_ID=p.RECEIPT_OPERATION_ID
        where r.UID_POLETA=:lot_id and r.CELL=:cell and r.REMAIN=:qty and r.BASE_UOM=:uom
        and r.HARD_RESERVED_BASE=0""",receipt_id=receipt,lot_id=lot,cell=dock,qty=qty,uom=unit)
    stock=q.fetchone()
    if stock is None:raise StoreReturnReceiveError("INTERWARE_GROUP_PLACED_CUSTODY_REQUIRED","Whole placed stock and original custody required")
    q.execute("select DESTINATION_ADDR from RRL_TT_HU_LOAD_ST where LOAD_OPERATION_ID=:load_id and SBORKA_PALLET_ID=:st_id",load_id=load,st_id=source_st)
    address=q.fetchone()[0]
    if not address:raise StoreReturnReceiveError("INTERWARE_GROUP_FROZEN_ADDRESS_REQUIRED","Frozen original recipient required")
    q.execute("""select json_arrayagg(json_object('fulfillment_id'value FULFILLMENT_ID,'customer_order_id'value CUSTOMER_ORDER_ID,
        'quantity'value RRL_STOCK_PLAN_HELPER.decimal_text(FACT_QTY),'base_uom'value FACT_UOM,'status'value STATUS)
        order by FULFILLMENT_ID returning clob)from RRL_CUSTOMER_ORDER_FULFILLMENT where LEGACY_SBORKA_PALLET_ID=:st_id""",st_id=source_st)
    ownership=read_oracle_json(q.fetchone()[0])or []
    if any(x["status"]!="SHIPPED"for x in ownership):raise StoreReturnReceiveError("INTERWARE_GROUP_ORIGINAL_SHIPMENT_REQUIRED","Original fulfillment must remain shipped")
    child="IW.GROUP.BIND:"+sha256(json.dumps([operation,lot],separators=(",",":")).encode()).hexdigest()
    st,identifier,number=InterwarehouseOnward._create_st(q,child,address,article,str(qty),unit,ware,actor)
    return dict(operation_id=child,receipt_operation_id=receipt,st_id=st,shipment_identifier=identifier,st_number=number,
        source_st_id=source_st,source_load_operation_id=load,target_trip_id=trip,warehouse_id=ware,pallet_identifier=lot,
        quantity=str(qty),base_uom=unit,article=article,final_address=address,stock_version=stock[0],original_fulfillment=ownership)


class InterwarehouseGroupOnward:
    def __init__(self,gateway: Any)->None:self.gateway=gateway

    def prepare(self,operation: str,receipt: str,reason: str,reference: str,actor: str)->dict[str,Any]:
        digest=sha256(json.dumps([receipt,reason,reference,actor],ensure_ascii=False,separators=(",",":")).encode()).digest()
        try:
            with receipt_task_metadata(self.gateway,"Original grouped onward ST preparation",actor,"outgoing_pallet_edit")as q:
                row=_scope(q,receipt,actor)
                q.execute("select PAYLOAD_HASH,RESULT_JSON from RRL_IW_GROUP_ONWARD where OPERATION_ID=:op",op=operation)
                old=q.fetchone()
                if old:
                    if old[0]!=digest:raise StoreReturnReceiveError("INTERWARE_GROUP_ONWARD_PAYLOAD_CONFLICT","Operation content changed")
                    return read_oracle_json(old[1])
                q.execute("select ID from RRL_TRANSPORT_TASK where ID=:trip and DOCK=:dock and CONDITION='Спланирован'and nvl(DELETED,0)=0 for update wait 5",trip=row[2],dock=row[3])
                if q.fetchone()is None:raise StoreReturnReceiveError("INTERWARE_GROUP_TARGET_TRIP_CHANGED","Original planned target trip required")
                q.execute("select ROOT_UID,ARTICLE,BASE_QTY,BASE_UOM,ST_ID from RRL_IW_GROUP_RECEIPT_LINE where OPERATION_ID=:receipt_id order by ROOT_UID fetch first 201 rows only",receipt_id=receipt)
                sources=q.fetchall()
                if not 2<=len(sources)<=200:raise StoreReturnReceiveError("INTERWARE_GROUP_SOURCE_BOUND","Two to 200 exact receipt leaves required")
                parts=[_part(q,operation,receipt,row,x,actor)for x in sources]
                result=dict(operation_id=operation,receipt_operation_id=receipt,status="PREPARED",target_trip_id=row[2],members=parts,stock_changed=False,customer_fulfillment_repeated=False,reason=reason,decision_reference=reference)
                q.setinputsizes(result_json=oracledb.DB_TYPE_CLOB)
                q.execute("insert into RRL_IW_GROUP_ONWARD(OPERATION_ID,PAYLOAD_HASH,RECEIPT_OPERATION_ID,ACTOR,RESULT_JSON)values(:op,:digest,:receipt_id,:actor,:result_json)",op=operation,digest=digest,receipt_id=receipt,actor=actor,result_json=json.dumps(result))
                q.setinputsizes(ownership=oracledb.DB_TYPE_CLOB,result_json=oracledb.DB_TYPE_CLOB)
                for part in parts:
                    q.execute("""insert into RRL_IW_GROUP_ST_BIND(OPERATION_ID,ONWARD_OPERATION_ID,RECEIPT_OPERATION_ID,ST_ID,
                        ST_IDENTIFIER,SOURCE_ST_ID,SOURCE_LOAD_OPERATION_ID,TARGET_TT_ID,WARE_ID,ROOT_UID,STOCK_VERSION,
                        SOURCE_CELL,FINAL_ADDRESS,ORIGINAL_FULFILLMENT_JSON,ACTOR,RESULT_JSON)
                        values(:op,:head,:receipt_id,:st,:identifier,:source_st,:load_id,:trip,:ware,:lot_id,:version,
                        :cell,:address,:ownership,:actor,:result_json)""",op=part["operation_id"],head=operation,receipt_id=receipt,
                        st=part["st_id"],identifier=part["shipment_identifier"],source_st=part["source_st_id"],load_id=row[1],
                        trip=row[2],ware=row[0],lot_id=part["pallet_identifier"],version=part["stock_version"],cell=row[3],
                        address=part["final_address"],ownership=json.dumps(part["original_fulfillment"]),actor=actor,result_json=json.dumps(part))
                return result
        except oracledb.DatabaseError as exc:
            code=getattr(exc.args[0],"code",0)
            if code==1 or 20800<=code<=20999:raise StoreReturnReceiveError("INTERWARE_GROUP_ONWARD_REJECTED",str(exc.args[0]).split("\n",1)[0],403 if code==20882 else 409)from exc
            raise
