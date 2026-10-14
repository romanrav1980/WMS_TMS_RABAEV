"""Source-scoped delivery queue, never infer government ACK from local DONE."""
from typing import Any
from ..contracts import LogisticsCostError

REGULATORY_SOURCE="""        from RRL_EVENT_OUTBOX e left join RRL_STOCK_OPERATION o
          on e.AGGREGATE_TYPE='STOCK_OPERATION' and o.OPERATION_ID=e.AGGREGATE_ID
        where json_value(e.PAYLOAD_JSON,'$.warehouse_id' returning number null on error)=:ware
          and(e.TARGET_SYSTEM in('CRPT','EGAIS','MERCURY')
            or e.EVENT_TYPE in('MARKED_GOODS_DISPOSED','MARKED_SUPPLIER_RETURN_DISPATCHED')
            or exists(select 1 from RRL_SKU_RECEIPT_PROFILE p where p.SYSTEM_CODE=e.TARGET_SYSTEM))
"""

def regulatory_snapshot(cursor: Any, ware: int) -> dict[str, Any]:
    cursor.execute("""select e.TARGET_SYSTEM,e.EVENT_TYPE,e.STATUS,count(*),
        sum(case when e.AGGREGATE_TYPE='STOCK_OPERATION'
          and (o.STATE is null or o.STATE!='APPLIED') then 1 else 0 end)
"""+REGULATORY_SOURCE+"""
        group by e.TARGET_SYSTEM,e.EVENT_TYPE,e.STATUS
        order by e.TARGET_SYSTEM,e.EVENT_TYPE,e.STATUS fetch first 201 rows only""",ware=ware)
    records=cursor.fetchall()
    if len(records)>200:
        raise LogisticsCostError("REGULATORY_RECONCILIATION_GROUP_BOUND_200","Слишком много групп сообщений маркировки",409)
    rows=[{"system_code":system,"event_type":kind,"delivery_status":status,
           "message_count":int(count),"source_operation_unverified_count":int(unverified),
           "government_acceptance":"NOT_VERIFIED_BY_THIS_REPORT"}
          for system,kind,status,count,unverified in records]
    complete={"DONE","EXPORTED","ACKNOWLEDGED"}
    return {"scope":"EXPLICIT_ORIGINAL_WAREHOUSE","coverage_complete":False,
        "groups":rows,"message_count":sum(row["message_count"]for row in rows),
        "delivery_pending_count":sum(row["message_count"]for row in rows if row["delivery_status"]not in complete),
        "source_operation_unverified_count":sum(row["source_operation_unverified_count"]for row in rows),
        "government_ack_reconciled":False,"quantity_totals_inferred":False}
