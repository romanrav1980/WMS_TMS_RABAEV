"""Three bounded reads in one Oracle READ ONLY snapshot; no inventory projection writes."""
import json
from pathlib import Path
from typing import Any
from ..domain.order_delivery import project_delivery
from ...fulfillment.public import assert_customer_order_warehouse


def rows(cursor: Any) -> list[dict[str,Any]]:
    names=[column[0].lower() for column in cursor.description]
    return [dict(zip(names,row)) for row in cursor.fetchall()]


class OrderDelivery:
    def __init__(self,gateway: Any) -> None:
        self.gateway=gateway

    def get(self,order_id: int,actor: str) -> dict[str,Any]:
        with self.gateway.transaction("Bounded order delivery READ ONLY snapshot") as q:
            q.execute("set transaction read only")
            q.execute("select ORDER_NO,STATUS,WARE_ID from RRL_CUSTOMER_ORDER where CUSTOMER_ORDER_ID=:order_id",{"order_id":order_id})
            header=q.fetchone()
            if not header:
                raise LookupError("Customer order not found")
            assert_customer_order_warehouse(q,actor,"customer_fulfillment_view",header[2])
            q.execute("""
                select ff.FULFILLMENT_ID,ff.STATUS,ff.LEGACY_SBORKA_PALLET_ID SHIPMENT_ID,
                       ff.SHIPPED_OPERATION_ID SHIPPING_OPERATION,lf.LOAD_OPERATION_ID,lf.STATUS LOAD_STATUS
                  from RRL_CUSTOMER_ORDER_FULFILLMENT ff
                  left join RRL_TT_HU_LOAD_ST ls on ls.SBORKA_PALLET_ID=ff.LEGACY_SBORKA_PALLET_ID
                   and (ls.LOAD_OPERATION_ID=ff.SHIPPED_OPERATION_ID or exists(select 1 from RRL_TT_LOAD_RECONCILE rr
                        where rr.LOAD_OPERATION_ID=ls.LOAD_OPERATION_ID and rr.SHIPPING_OPERATION_ID=ff.SHIPPED_OPERATION_ID))
                  left join RRL_TT_HU_LOAD_FACT lf on lf.LOAD_OPERATION_ID=ls.LOAD_OPERATION_ID
                 where ff.CUSTOMER_ORDER_ID=:order_id order by ff.FULFILLMENT_ID fetch first 201 rows only
            """,{"order_id":order_id})
            fulfillment=rows(q)
            if len(fulfillment)>200:
                raise ValueError("DELIVERY_FULFILLMENT_BOUND_200")
            operations=sorted({row["shipping_operation"] for row in fulfillment if row["status"]=="SHIPPED" and row["shipping_operation"]})
            legs=self._legs(q,operations) if operations else []
            loads=sorted({row["load_operation_id"] for row in fulfillment if row["load_operation_id"]})
            receipt=self._receipts(q,loads) if loads else []
        result=project_delivery(order_id,legs,fulfillment,receipt)
        result.update(order_no=header[0],original_document_status=header[1],receipt_lineage=[{"original_load_operation_id":row["load_operation_id"],"actual_final_load_operation_id":row["actual_final_load_operation_id"],"receipt_operation_id":row["receipt_operation"],"lot_uid":row["lot_uid"],"original_lot_uid":row.get("original_lot_uid",row["lot_uid"]),"transport_shortage_operation_id":row.get("transport_shortage_operation_id"),"historical_transport_shortage":row.get("confirmed_transport_shortage","0"),"recovered_transport_quantity":row.get("recovered_transport_quantity","0"),"is_corrective_receipt":bool(row.get("is_corrective_receipt",False))}for row in receipt])
        return result

    def _legs(self,q: Any,operations: list[str]) -> list[dict[str,Any]]:
        selects=[]
        for kind,path in (("HU_SHIP","$.domain.shipments[*].domain"),("LOAD_SHIPMENT","$.domain.shipment.domain"),("SHIP_PALLET","$.domain")):
            selects.append("""
                select op.OPERATION_ID SHIPPING_OPERATION,j.OWNER_ORDER_ID,j.SHIPMENT_ID,j.LEG_NO,j.LOT_UID,j.ARTICLE,j.BASE_UOM,j.QUANTITY
                  from RRL_STOCK_OPERATION op,
                  json_table(op.RESOLVED_PLAN_JSON,'"""+path+"""' columns(
                    OWNER_ORDER_ID number path '$.customer_order_id',SHIPMENT_ID number path '$.document_id',
                    nested path '$.legs[*]' columns(LEG_NO for ordinality,LOT_UID varchar2(200) path '$.uid',
                       ARTICLE varchar2(160) path '$.article',BASE_UOM varchar2(20) path '$.base_uom',QUANTITY varchar2(40) path '$.quantity')))j
                 where op.STATE='APPLIED' and op.COMMAND_TYPE='"""+kind+"""'
                   and op.OPERATION_ID in(select VALUE from json_table(:operations,'$[*]' columns(VALUE varchar2(100) path '$')))
            """)
        q.execute("select * from("+" union all ".join(selects)+") fetch first 2001 rows only",{"operations":json.dumps(operations)})
        result=rows(q)
        if len(result)>2000:
            raise ValueError("DELIVERY_ORIGINAL_LEG_BOUND_2000")
        if {row["shipping_operation"] for row in result}!=set(operations):
            raise ValueError("DELIVERY_COMMITTED_ORIGINAL_PROVENANCE_REQUIRED")
        return result

    def _receipts(self,q: Any,loads: list[str]) -> list[dict[str,Any]]:
        q.execute(Path(__file__).with_name("order_delivery_receipts.sql").read_text(encoding="utf-8"),{"loads":json.dumps(loads)})
        result=rows(q)
        if len(result)>2000:
            raise ValueError("DELIVERY_RECEIPT_LINE_BOUND_2000")
        return result
