"""Bounded document samples and batched counts from the existing reconciliation predicates."""
from typing import Any
from .reconciliation_sources import DAILY, BACKLOG

DOCUMENTS = {
    'transport_cost_unrecognized': ('s.DEPARTURE_OPERATION_ID','TRIP_DEPARTURE'),
    'store_unloads_open': ('s.OPERATION_ID','STORE_UNLOAD'),
    'interwarehouse_onward_pending': ('p.OPERATION_ID','INTERWARE_PLACEMENT'),
    'interwarehouse_custody_pending': ('r.OPERATION_ID','INTERWARE_RECEIPT'),
    'interwarehouse_placement_pending': ('r.OPERATION_ID','INTERWARE_RECEIPT'),
    'interwarehouse_unload_pending': ('p.OPERATION_ID','INTERWARE_PLAN'),
    'interwarehouse_receipt_pending': ('u.OPERATION_ID','INTERWARE_UNLOAD'),
    'open_warehouse_tasks': ('TASK_ID','WAREHOUSE_TASK'),
    'return_placement_pending': ('r.OPERATION_ID','STORE_RETURN_RECEIPT'),
    'supplier_handover_pending': ('d.OPERATION_ID','SUPPLIER_DISPATCH'),
    'disposal_pending': ('r.OPERATION_ID','STORE_RETURN_RECEIPT'),
    'delivery_discrepancies': ('c.CASE_ID','DELIVERY_CASE'),
    'tare_offers_unaccepted': ('o.OPERATION_ID','TARE_OFFER'),
    'tare_loss_unresolved': ('c.OPERATION_ID','TARE_LOSS_CLAIM'),
    'expense_approval_pending': ('e.OPERATION_ID','LOGISTICS_EXPENSE'),
    'expense_allocation_pending': ('e.OPERATION_ID','LOGISTICS_EXPENSE'),
}

def daily_counts(cursor: Any, params: dict[str,Any]) -> dict[str,int]:
    # Fixed repository SQL; only warehouse/day bounds are data bindings.
    sql=' union all '.join("select '"+key+"' METRIC,("+query+") TOTAL_COUNT from dual" for key,query in DAILY)
    cursor.execute(sql,params)
    return {key:int(count) for key,count in cursor.fetchall()}

def backlog_documents(cursor: Any, warehouse: int) -> tuple[dict[str,int],dict[str,Any]]:
    parts=[]
    for key,query in BACKLOG:
        identifier,_=DOCUMENTS[key]
        if not query.startswith('select count(*)from '):
            raise ValueError('Unsupported reconciliation predicate: '+key)
        source=query[len('select count(*)'):]
        parts.append("select '"+key+"' METRIC,DOCUMENT_ID,TOTAL_COUNT from (select cast("+identifier+
                     " as varchar2(160)) DOCUMENT_ID,count(*) over() TOTAL_COUNT "+source+
                     " order by "+identifier+" fetch first 20 rows only)")
    cursor.execute(' union all '.join(parts),{'ware':warehouse})
    counts={key:0 for key,_ in BACKLOG}
    details={key:{'document_kind':DOCUMENTS[key][1],'document_ids':[], 'has_more':False,
                  'limit':20,'scope':'CURRENT_BACKLOG','available':True} for key,_ in BACKLOG}
    for key,identifier,count in cursor.fetchall():
        counts[key]=int(count);details[key]['document_ids'].append(identifier)
        details[key]['has_more']=int(count)>20
    return counts,details