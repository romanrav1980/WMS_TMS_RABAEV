"""Small source-message samples using exactly the report counter predicates."""
from typing import Any
from .reconciliation_erp import ERP_SOURCE
from .reconciliation_regulatory import REGULATORY_SOURCE

SOURCES={
 "external_erp_ack_pending":("o.EVENT_ID","SAP_OUTBOX",ERP_SOURCE),
 "regulatory_ack_not_reconciled":("e.EVENT_OUTBOX_ID","EVENT_OUTBOX",REGULATORY_SOURCE),
 "regulatory_stock_source_unverified":("e.EVENT_OUTBOX_ID","EVENT_OUTBOX",REGULATORY_SOURCE+
     " and e.AGGREGATE_TYPE='STOCK_OPERATION' and(o.STATE is null or o.STATE!='APPLIED') ")
}

def external_documents(cursor: Any,ware: int,counts: dict[str,int]) -> dict[str,Any]:
    parts=[]
    result={}
    for key,(identifier,kind,source) in SOURCES.items():
        if not counts.get(key):continue
        result[key]={"available":True,"document_kind":kind,"document_ids":[],"limit":20,
                     "has_more":counts[key]>20,"scope":"CURRENT_EXTERNAL_MESSAGES"}
        parts.append("select '"+key+"' METRIC,DOCUMENT_ID from (select cast("+identifier+
                     " as varchar2(160)) DOCUMENT_ID "+source+" order by "+identifier+" fetch first 20 rows only)")
    if parts:
        cursor.execute(" union all ".join(parts),ware=ware)
        for key,identifier in cursor.fetchall():result[key]["document_ids"].append(identifier)
    return result
