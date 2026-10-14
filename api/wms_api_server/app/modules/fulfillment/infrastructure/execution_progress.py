"""One bounded Oracle snapshot: root-created CASE lots and physical pallet move facts."""
from typing import Any
from fastapi import HTTPException
from ..domain.execution_progress import line_progress, order_progress_status, line_is_cancelled
from ....transaction_gateway import TransactionGateway
from .store_source_scope import assert_store_scope


class OrderExecution:
    def __init__(self, gateway: Any) -> None:
        self.gateway = gateway

    def get(self, order_id: int, actor: str) -> dict:
        if order_id < 1:
            raise ValueError("Positive order ID required")
        with self.gateway.transaction("Physical order execution READ ONLY current warehouse") as cursor:
            if not getattr(self.gateway,"transaction_bound",False):
                cursor.execute("set transaction read only")
            cursor.execute("select WARE_ID from RRL_CUSTOMER_ORDER where CUSTOMER_ORDER_ID=:order_id",order_id=order_id)
            row = cursor.fetchone()
            if row is None:
                raise LookupError("Customer order not found")
            assert_store_scope(cursor,actor,"customer_fulfillment_view",row[0])
            result = OrderExecution(TransactionGateway(cursor))._snapshot(order_id)
            result.update(warehouse_id=row[0],consistent_snapshot=True)
            return result

    def _snapshot(self, order_id: int) -> dict:
        headers = self.gateway.fetch_all("select CUSTOMER_ORDER_ID,ORDER_NO,STATUS from RRL_CUSTOMER_ORDER where CUSTOMER_ORDER_ID=:id",
                                         {"id": order_id})
        if not headers:
            raise LookupError("Customer order not found")
        rows = self.gateway.fetch_all("""select r.CUSTOMER_ORDER_ROW_ID,r.LINE_NO,r.ARTICUL,r.UNIT_CODE,r.STATUS ROW_STATUS,
            to_char(r.ORDER_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') ORDER_QUANTITY,
            u.BASE_UOM,u.NUMERATOR,u.DENOMINATOR,u.BASE_SCALE,
            to_char(nvl((select sum(p.UNIT_COUNT) from RRL_CASE_CARRIER_LOT h
                join RRL_PALLETS p on p.UID_PALLET=h.LOT_UID
                join RRL_CASE_PICK_LINE l on l.CASE_PICK_LINE_ID=h.CASE_PICK_LINE_ID
                join RRL_CASE_PICK_TASK ct on ct.CASE_PICK_TASK_ID=l.CASE_PICK_TASK_ID
                join RRL_PICK_PLAN_LINE pl on pl.PICK_PLAN_LINE_ID=l.PICK_PLAN_LINE_ID
                join RRL_STOCK_OPERATION op on op.OPERATION_ID=h.CREATED_OPERATION and op.STATE='APPLIED'
                where pl.CUSTOMER_ORDER_ROW_ID=r.CUSTOMER_ORDER_ROW_ID and ct.STATUS not in('CANCELLED','FAILED')),0),
                'TM9','NLS_NUMERIC_CHARACTERS=''.,''') CASE_FACT,
            to_char(nvl((select sum(m.BASE_QTY) from RRL_WAREHOUSE_TASK_STOCK_MOVE m
                join RRL_WAREHOUSE_TASK t on t.TASK_ID=m.TASK_ID
                join RRL_PICK_WAVE_TASK wt on wt.PICK_WAVE_TASK_ID=t.SOURCE_TASK_ID
                join RRL_PICK_TASK pt on pt.PICK_TASK_ID=wt.PICK_TASK_ID
                join RRL_PICK_PLAN_LINE pl on pl.PICK_PLAN_LINE_ID=pt.PICK_PLAN_LINE_ID
                where t.TASK_SOURCE='WAVE' and t.TASK_TYPE='PICKING_MOVE' and pt.TASK_TYPE='FULL_PALLET'
                 and pt.STATUS not in('CANCELLED','FAILED') and pl.CUSTOMER_ORDER_ROW_ID=r.CUSTOMER_ORDER_ROW_ID),0),
                'TM9','NLS_NUMERIC_CHARACTERS=''.,''') PALLET_FACT,
            to_char(nvl((select sum(sr.BASE_QTY) from RRL_STOCK_RESERVATION sr
                join RRL_PICK_TASK pt on pt.PICK_TASK_ID=sr.SOURCE_LINE_ID
                join RRL_PICK_PLAN_LINE pl on pl.PICK_PLAN_LINE_ID=pt.PICK_PLAN_LINE_ID
                where sr.SOURCE_DOC_TYPE='PICK_WAVE' and sr.RESERVATION_KIND='HARD'
                 and sr.STATUS in('ACTIVE','ALLOCATED','PICKING') and pl.CUSTOMER_ORDER_ROW_ID=r.CUSTOMER_ORDER_ROW_ID),0),
                'TM9','NLS_NUMERIC_CHARACTERS=''.,''') HARD_QUANTITY,
            (select count(*) from RRL_CASE_PICK_LINE l join RRL_PICK_PLAN_LINE pl on pl.PICK_PLAN_LINE_ID=l.PICK_PLAN_LINE_ID
                join RRL_CASE_PICK_TASK ct on ct.CASE_PICK_TASK_ID=l.CASE_PICK_TASK_ID
                where pl.CUSTOMER_ORDER_ROW_ID=r.CUSTOMER_ORDER_ROW_ID and l.STATUS='SHORT_PICKED'
                 and ct.STATUS not in('CANCELLED','FAILED')) REFUSED_LINES,
            (select max(sh.REASON_TEXT) keep(dense_rank last order by sh.CREATED_AT,sh.CASE_PICK_SHORT_ID) from RRL_CASE_PICK_SHORT sh join RRL_CASE_PICK_LINE l on l.CASE_PICK_LINE_ID=sh.CASE_PICK_LINE_ID join RRL_PICK_PLAN_LINE pl on pl.PICK_PLAN_LINE_ID=l.PICK_PLAN_LINE_ID
                join RRL_CASE_PICK_TASK ct on ct.CASE_PICK_TASK_ID=l.CASE_PICK_TASK_ID
                where pl.CUSTOMER_ORDER_ROW_ID=r.CUSTOMER_ORDER_ROW_ID and l.STATUS='SHORT_PICKED'
                 and ct.STATUS not in('CANCELLED','FAILED')) REFUSAL_REASON
            from RRL_CUSTOMER_ORDER_ROW r left join RRL_STOCK_UOM_CONVERSION u on u.ARTICUL=r.ARTICUL and u.INPUT_UOM=r.UNIT_CODE
              and u.POLICY_VERSION=(select max(POLICY_VERSION) from RRL_STOCK_UOM_CONVERSION where ARTICUL=r.ARTICUL and INPUT_UOM=r.UNIT_CODE)
            where r.CUSTOMER_ORDER_ID=:id order by r.LINE_NO,r.CUSTOMER_ORDER_ROW_ID fetch first 2001 rows only""",
            {"id": order_id})
        if len(rows) > 2000:
            raise HTTPException(409, detail="ORDER_EXECUTION_LINE_BOUND_2000")
        lines = [line_progress(row) for row in rows]
        active_count = sum(not line_is_cancelled(line) for line in lines)
        return {"customer_order_id": order_id, "order_no": headers[0]["order_no"], "document_status": headers[0]["status"],
                "execution_status": order_progress_status(lines), "line_count": len(lines),
                "active_line_count": active_count, "cancelled_line_count": len(lines) - active_count,
                "lines": lines}
