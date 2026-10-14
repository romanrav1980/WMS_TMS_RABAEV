"""Current source and original pallet receipts in one bounded authorised snapshot."""
from typing import Any
from ....transaction_gateway import TransactionGateway
from .supply_reads import supply_detail,rows


def receipt_history(gateway: Any, order: str, limit: int, after: str | None, actor: str) -> dict[str, Any]:
    if not 1<=limit<=100:
        raise ValueError("Receipt history page requires 1..100 rows")
    with gateway.transaction("SAP receiving history READ ONLY current warehouse")as cur:
        if not getattr(gateway,"transaction_bound",False):
            cur.execute("set transaction read only")
        source=supply_detail(TransactionGateway(cur),order,None,actor)
        anchor_time=None
        if after is not None:
            cur.execute("select RECEIVED_AT from RRL_SAP_PALLET_RECEIPT where ORDER_ID=:o and OPERATION_ID=:op",o=order,op=after)
            found=cur.fetchone()
            if found is None:
                raise ValueError("RECEIPT_CURSOR_CURRENT_SOURCE_REQUIRED")
            anchor_time=found[0]
        cur.execute("""select r.OPERATION_ID,r.LINE_NUMBER,r.UID_PALLET PALLET_IDENTIFIER,
          to_char(r.POSTED_BASE_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''')ACCEPTED_QUANTITY,r.STOCK_BASE_UOM BASE_UOM,
          r.SUPPLIER_BATCH,r.RECEIVED_AT,r.RECEIVED_BY,
          json_value(r.RESULT_JSON,'$.task_id' returning number null on error)TASK_ID,
          t.STATUS TASK_STATUS,
          to_char(nvl((select sum(s.REMAIN)from RRL_REMAINS s join RRL_CELLS c on c.CELL=s.CELL
             where s.UID_POLETA=r.UID_PALLET and c.WARE_ID=:ware),0),'TM9','NLS_NUMERIC_CHARACTERS=''.,''')CURRENT_WAREHOUSE_QUANTITY,
          to_char(nvl((select sum(s.HARD_RESERVED_BASE)from RRL_REMAINS s join RRL_CELLS c on c.CELL=s.CELL
             where s.UID_POLETA=r.UID_PALLET and c.WARE_ID=:ware),0),'TM9','NLS_NUMERIC_CHARACTERS=''.,''')CURRENT_WAREHOUSE_HARD
          from RRL_SAP_PALLET_RECEIPT r left join RRL_WAREHOUSE_TASK t
            on t.TASK_ID=json_value(r.RESULT_JSON,'$.task_id' returning number null on error)
          where r.ORDER_ID=:order_id and(:after_op is null or r.RECEIVED_AT<:anchor_time
            or(r.RECEIVED_AT=:anchor_time and r.OPERATION_ID<:after_op))
          order by r.RECEIVED_AT desc,r.OPERATION_ID desc fetch first :page_bound rows only""",
          ware=source["ware_id"],order_id=order,after_op=after,anchor_time=anchor_time,page_bound=limit+1)
        receipts=rows(cur)
        more=len(receipts)>limit
        receipts=receipts[:limit]
        return {"source":source,"receipts":receipts,"has_more":more,
          "next_cursor":receipts[-1]["operation_id"]if more else None,
          "consistent_snapshot":True,"warehouse_id":source["ware_id"],"quantity_semantics":"ORIGINAL_RECEIPT_AND_CURRENT_SOURCE_WAREHOUSE"}
