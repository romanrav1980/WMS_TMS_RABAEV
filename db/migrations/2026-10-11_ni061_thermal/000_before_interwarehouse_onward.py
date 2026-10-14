"""Existing ordinary ST constructor; immutable original shipment lineage."""
from hashlib import sha256
from decimal import Decimal
from typing import Any
import json
import oracledb
from ...platform.public import read_oracle_json
from ..contracts_store_returns import StoreReturnReceiveError
from .metadata_transactions import receipt_task_metadata

class InterwarehouseOnward:
    def __init__(self,gateway: Any) -> None:
        self.gateway=gateway

    def prepare(self,operation_id: str,receipt_id: str,reason: str,reference: str,actor: str,accept_legacy_address: bool=False) -> dict[str,Any]:
        digest=sha256(json.dumps([receipt_id,reason,reference,actor,accept_legacy_address],ensure_ascii=False,separators=(",",":")).encode()).digest()
        try:
            with receipt_task_metadata(self.gateway,"Existing onward ST preparation",actor,"outgoing_pallet_edit") as cur:
                cur.execute("select r.WARE_ID,r.ARTICLE,to_char(r.BASE_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,'''),r.BASE_UOM,r.ROOT_UID,p.SOURCE_ST_ID,p.SOURCE_LOAD_OPERATION_ID,RRL_INTERWARE_ROUTING.target_trip(p.OPERATION_ID),RRL_INTERWARE_ROUTING.outbound_dock(p.OPERATION_ID) from RRL_INTERWARE_RECEIPT r join RRL_INTERWARE_PLAN p on p.OPERATION_ID=r.PLAN_OPERATION_ID where r.OPERATION_ID=:receipt",receipt=receipt_id)
                source=cur.fetchone()
                if not source:
                    raise StoreReturnReceiveError("INTERWARE_ONWARD_RECEIPT_REQUIRED","Actual target receipt required")
                ware,article,qty,unit,uid,source_st,source_load,target_trip,dock=source
                cur.execute("select count(*)from RUSERS where ID=:actor and nvl(DELETED,0)=0 and(WARE_ID=:ware or upper(trim(USER_GROUP))='GLOBAL_ADMIN')and RRL_HAS_WRIGHT(ID,'transport_dispatch_edit')=1",actor=actor,ware=ware)
                if cur.fetchone()[0]!=1:
                    raise StoreReturnReceiveError("INTERWARE_ONWARD_WARE_ACTOR_REQUIRED","Current target dispatcher required",403)
                cur.execute("select PAYLOAD_HASH,RESULT_JSON from RRL_INTERWARE_ONWARD_BIND where OPERATION_ID=:op",op=operation_id)
                old=cur.fetchone()
                if old:
                    if old[0]!=digest:
                        raise StoreReturnReceiveError("INTERWARE_ONWARD_PAYLOAD_CONFLICT","Operation content changed")
                    return read_oracle_json(old[1])
                cur.execute("select count(*)from RRL_INTERWARE_ONWARD_BIND where RECEIPT_OPERATION_ID=:receipt",receipt=receipt_id)
                if cur.fetchone()[0]:
                    raise StoreReturnReceiveError("INTERWARE_ONWARD_ALREADY_PREPARED","Use original prepared ST")
                cur.execute("select ID from RRL_TRANSPORT_TASK where ID=:trip and CONDITION='Спланирован'and nvl(DELETED,0)=0 and DOCK=:dock for update wait 5",trip=target_trip,dock=dock)
                if not cur.fetchone():
                    raise StoreReturnReceiveError("INTERWARE_ONWARD_TRIP_CHANGED","Original existing target trip required")
                cur.execute("select r.STOCK_VERSION from RRL_REMAINS r join RRL_INTERWARE_PLACEMENT p on p.ROOT_UID=r.UID_POLETA and p.TARGET_CELL=r.CELL join RRL_INTERWARE_CUSTODY_PROOF c on c.RECEIPT_OPERATION_ID=p.RECEIPT_OPERATION_ID where p.RECEIPT_OPERATION_ID=:receipt and r.CELL=:dock and r.REMAIN=:qty and r.HARD_RESERVED_BASE=0 and r.BASE_UOM=:unit",receipt=receipt_id,dock=dock,qty=Decimal(qty),unit=unit)
                stock=cur.fetchone()
                if not stock:
                    raise StoreReturnReceiveError("INTERWARE_ONWARD_PLACED_CUSTODY_REQUIRED","Whole stock at target dock and first-leg custody release required")
                cur.execute("select DESTINATION_ADDR from RRL_TT_HU_LOAD_ST where LOAD_OPERATION_ID=:op and SBORKA_PALLET_ID=:st",op=source_load,st=source_st)
                address=cur.fetchone()[0]
                address_source="FROZEN_LOAD"
                if not address:
                    if not accept_legacy_address:
                        raise StoreReturnReceiveError("INTERWARE_ONWARD_FINAL_ADDRESS_REQUIRED","Historical load has no frozen address; explicit guarded legacy-address decision required")
                    cur.execute("select ADDR from RRL_SBORKA_PALLETS where ID=:st for update wait 5",st=source_st)
                    address=cur.fetchone()[0]
                    if not address:
                        raise StoreReturnReceiveError("INTERWARE_ONWARD_FINAL_ADDRESS_REQUIRED","Original legacy ST has no delivery address")
                    address_source="CURRENT_GUARDED_LEGACY"
                cur.execute("""select json_arrayagg(json_object('fulfillment_id' value f.FULFILLMENT_ID,'customer_order_id' value f.CUSTOMER_ORDER_ID,'quantity' value to_char(f.FACT_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,'''),'base_uom' value f.FACT_UOM,'status' value f.STATUS)order by f.FULFILLMENT_ID returning clob)
                    from RRL_CUSTOMER_ORDER_FULFILLMENT f where f.LEGACY_SBORKA_PALLET_ID=:st""",st=source_st)
                ownership=cur.fetchone()[0]
                ownership=read_oracle_json(ownership) if ownership is not None else []
                if len(ownership)>200 or any(x["status"]!="SHIPPED" for x in ownership):
                    raise StoreReturnReceiveError("INTERWARE_ONWARD_ORIGINAL_FULFILLMENT_REQUIRED","Original first-leg shipment ownership required")
                st_id,identifier,number=self._create_st(cur,operation_id,address,article,qty,unit,ware,actor)
                result={"operation_id":operation_id,"receipt_operation_id":receipt_id,"st_id":st_id,"shipment_identifier":identifier,"st_number":number,"source_st_id":int(source_st),"source_load_operation_id":source_load,"target_trip_id":int(target_trip),"warehouse_id":int(ware),"pallet_identifier":uid,"quantity":qty,"base_uom":unit,"final_address":address,"final_address_source":address_source,"legacy_address_confirmed":address_source=="CURRENT_GUARDED_LEGACY","status":"PREPARED","stock_changed":False,"customer_fulfillment_repeated":False}
                cur.setinputsizes(ownership=oracledb.DB_TYPE_CLOB,result_body=oracledb.DB_TYPE_CLOB)
                cur.execute("""insert into RRL_INTERWARE_ONWARD_BIND(OPERATION_ID,PAYLOAD_HASH,RECEIPT_OPERATION_ID,ST_ID,ST_IDENTIFIER,SOURCE_ST_ID,SOURCE_LOAD_OPERATION_ID,TARGET_TT_ID,WARE_ID,ROOT_UID,STOCK_VERSION,SOURCE_CELL,FINAL_ADDRESS,FINAL_ADDRESS_SOURCE,ORIGINAL_FULFILLMENT_JSON,REASON_TEXT,DECISION_REFERENCE,ACTOR,RESULT_JSON)values(:op,:digest,:receipt,:st,:identifier,:source_st,:source_load,:trip,:ware,:lot_id,:version,:cell,:address,:address_source,:ownership,:reason,:reference,:actor,:result_body)""",op=operation_id,digest=digest,receipt=receipt_id,st=st_id,identifier=identifier,source_st=source_st,source_load=source_load,trip=target_trip,ware=ware,lot_id=uid,version=stock[0],cell=dock,address=address,address_source=address_source,ownership=json.dumps(ownership),reason=reason,reference=reference,actor=actor,result_body=json.dumps(result))
                return result
        except oracledb.DatabaseError as exc:
            code=getattr(exc.args[0],"code",0)
            if code==1 or 20800<=code<=20999:
                raise StoreReturnReceiveError("INTERWARE_ONWARD_REJECTED",str(exc.args[0]).split("\n",1)[0],403 if code==20882 else 409) from exc
            raise

    @staticmethod
    def _create_st(cur: Any,operation_id: str,address: str,article: str,qty: str,unit: str,ware: int,actor: str) -> tuple[int,str,str]:
        from decimal import Decimal
        identifier="IW.ST:"+sha256(operation_id.encode()).hexdigest()[:40]
        number="IW_"+sha256(operation_id.encode()).hexdigest()[:20]
        cur.execute("select count(*)from RRL_SBORKA_PALLETS where PALLET_UID=:identifier or ST_NUMBER=:st_number_text",identifier=identifier,st_number_text=number)
        if cur.fetchone()[0]:
            raise StoreReturnReceiveError("INTERWARE_ONWARD_CONSTRUCTOR_ID_CONFLICT","New ordinary ST identity required")
        st=int(cur.callfunc("RRL_SBORKA_PALLETS_ADD2",oracledb.DB_TYPE_NUMBER,[number,address,1,identifier,None,None,None,actor,ware]))
        cur.execute("update RRL_SBORKA_PALLETS set CONDITION=0,CREATE_DATE=sysdate where ID=:st and PALLET_UID=:identifier and WARE_ID=:ware and RETURN_SUPPLIER_ID is null",st=st,identifier=identifier,ware=ware)
        if cur.rowcount!=1:
            raise StoreReturnReceiveError("INTERWARE_ONWARD_CONSTRUCTOR_FAILED","Original ordinary ST constructor failed")
        row=int(cur.callfunc("PALL_SPLITTER.add_row_2sborka_pallets",oracledb.DB_TYPE_NUMBER,[article,Decimal(qty),identifier,ware,number]))
        cur.execute("update RRL_SBORKA_PALLET_ROWS set EI=:unit where ID=:row_id and ARTICUL=:article and QUANTITY=:qty and PALLET_UID=:identifier",unit=unit,row_id=row,article=article,qty=Decimal(qty),identifier=identifier)
        if cur.rowcount!=1:
            raise StoreReturnReceiveError("INTERWARE_ONWARD_ROW_FAILED","Original ordinary ST row constructor failed")
        return st,identifier,number
