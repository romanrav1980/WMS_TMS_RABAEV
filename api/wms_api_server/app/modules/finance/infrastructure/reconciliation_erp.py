from typing import Any

ERP_SOURCE="""    from RRL_SAP_RECEIPT_OUTBOX o where o.STATUS!='ACKNOWLEDGED' and(
    json_value(o.PAYLOAD_JSON,'$.warehouse_id' returning number null on error)=:ware
    or exists(select 1 from RRL_STORE_RETURN_RECEIPT r where r.WARE_ID=:ware and r.OPERATION_ID=json_value(o.PAYLOAD_JSON,'$.receipt_operation_id'))
    or exists(select 1 from RRL_LOGISTICS_EXPENSE e where e.WARE_ID=:ware and e.OPERATION_ID=json_value(o.PAYLOAD_JSON,'$.expense_operation_id')))
"""

def erp_snapshot(cursor: Any,ware: int) -> list[dict[str,Any]]:
    cursor.execute("""select o.EVENT_TYPE,o.STATUS,count(*)
"""+ERP_SOURCE+"""
    group by o.EVENT_TYPE,o.STATUS order by o.EVENT_TYPE,o.STATUS""",{"ware":ware})
    return [{"event_type":kind,"status":status,"count":count}for kind,status,count in cursor.fetchall()]
