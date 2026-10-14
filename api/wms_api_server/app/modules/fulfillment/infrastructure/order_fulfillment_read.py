"""One current authorised order snapshot; reuse the original fulfillment facts."""
from typing import Any
import json
from fastapi import HTTPException
from ....transaction_gateway import TransactionGateway
from .store_source_scope import assert_store_scope


class OrderFulfillmentRead:
    def __init__(self,gateway: Any)->None:
        self.gateway=gateway

    def get(self,customer_order_id: int,actor: str)->list[dict]:
        if customer_order_id<1:
            raise ValueError("Positive order ID required")
        with self.gateway.transaction("Order fulfillment READ ONLY current warehouse")as cur:
            if not getattr(self.gateway,"transaction_bound",False):
                cur.execute("set transaction read only")
            cur.execute("select WARE_ID from RRL_CUSTOMER_ORDER where CUSTOMER_ORDER_ID=:id",id=customer_order_id)
            header=cur.fetchone()
            if header is None:
                raise LookupError("Customer order not found")
            assert_store_scope(cur,actor,"customer_fulfillment_view",header[0])
            return OrderFulfillmentRead(TransactionGateway(cur))._rows(customer_order_id,header[0])

    def _rows(self,customer_order_id: int,warehouse: int)->list[dict]:
        rows = self.gateway.fetch_all(
            """
            select f.*,p.TRANSTASK_ID CURRENT_TRIP_ID,tt.CONDITION CURRENT_TRIP_CONDITION,tt.DOCK CURRENT_DOCK,ct.SSCC CASE_IDENTIFIER,ct.CURRENT_CELL CASE_CURRENT_CELL,
                   ct.CONTENT_VERSION CASE_CURRENT_VERSION,ct.STATUS CASE_CURRENT_STATUS
              from (select FULFILLMENT_ID,
                   CUSTOMER_ORDER_ID,
                   LEGACY_SBORKA_PALLET_ID,
                   PALLET_UID,
                   ADDRESS_TEXT,
                   STATUS,
                   FACT_QTY,to_char(FACT_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') FACT_QTY_EXACT,
                   FACT_WEIGHT,to_char(FACT_WEIGHT,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') FACT_WEIGHT_EXACT,
                   PICKED_WAREHOUSE_TASK_ID,PICKED_OPERATION_ID,PICKED_PALLET_UID,PICKED_STOCK_VERSION,
                   SHIPPED_OPERATION_ID,SHIPPED_AT,FACT_UOM,FACT_COMPOSITION_JSON,PICKED_CASE_TASK_ID,PICKED_CONTENT_VERSION,PICKED_AT,PICKED_BY,
                   SOURCE_SYSTEM,
                   CREATED_AT
              from RRL_CUSTOMER_ORDER_FULFILLMENT
             where CUSTOMER_ORDER_ID = :customer_order_id
             order by FULFILLMENT_ID fetch first 201 rows only) f left join RRL_CASE_PICK_TASK ct on ct.CASE_PICK_TASK_ID=f.PICKED_CASE_TASK_ID
               and ct.CUSTOMER_ORDER_ID=f.CUSTOMER_ORDER_ID and ct.WARE_ID=:p_warehouse
             left join RRL_SBORKA_PALLETS p on p.ID=f.LEGACY_SBORKA_PALLET_ID and p.WARE_ID=:p_warehouse
               left join RRL_TRANSPORT_TASK tt on tt.ID=p.TRANSTASK_ID
             order by f.FULFILLMENT_ID
            """,
            {"customer_order_id": customer_order_id,"p_warehouse": warehouse},
        )
        if len(rows)>200:
            raise HTTPException(409,detail="ORDER_FULFILLMENT_BOUND_200")
        for row in rows:
            payload=row.pop("fact_composition_json",None)
            payload=payload.read() if hasattr(payload,"read") else payload
            composition=json.loads(payload) if payload else []
            if not isinstance(composition,list) or len(composition)>200:
                raise HTTPException(409,detail="ORDER_PHYSICAL_COMPOSITION_INVALID")
            row["physical_composition"]=composition
        for row in rows:
            row["case_binding_version_matches"] = (row.get("case_current_version") is not None
                and row.get("case_current_version") == row.get("picked_content_version"))
            row["case_place_current"] = (row.get("status") == "PICKED"
                and row.get("case_current_status") in ("WAIT_CONTROL","CONTROL_IN_PROGRESS","CONTROLLED","READY_TO_SHIP")
                and row.get("case_current_cell") is not None and row["case_binding_version_matches"])
        return rows
