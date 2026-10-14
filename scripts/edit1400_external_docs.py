from pathlib import Path
root=Path('api/wms_api_server/app/modules/finance/infrastructure')
for filename,const in [('reconciliation_erp.py','ERP_SOURCE'),('reconciliation_regulatory.py','REGULATORY_SOURCE')]:
 p=root/filename;s=p.read_text(encoding='utf-8');begin=s.index('    from RRL_SAP_RECEIPT_OUTBOX') if const=='ERP_SOURCE' else s.index('        from RRL_EVENT_OUTBOX');end=s.index('    group by',begin) if const=='ERP_SOURCE' else s.index('        group by',begin);source=s[begin:end];s=s[:begin]+'"""+'+const+'+"""\n'+s[end:];insert=s.index('\ndef ');s=s[:insert]+'\n'+const+'="""'+source+'"""\n'+s[insert:];p.write_text(s,encoding='utf-8')
p=root/'reconciliation_external_documents.py';p.write_text('''"""Small source-message samples using exactly the report counter predicates."""
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
''',encoding='utf-8')
p=root/'day_reconciliation.py';s=p.read_text(encoding='utf-8').replace('from .reconciliation_documents import daily_counts,backlog_documents','from .reconciliation_documents import daily_counts,backlog_documents\nfrom .reconciliation_external_documents import external_documents');s=s.replace('            for item in blockers:\n                item.setdefault', '            external=external_documents(cur,ware,{item["code"]:item["count"] for item in blockers})\n            for item in blockers:\n                if item["code"] in external:item["documents"]=external[item["code"]]\n                item.setdefault');p.write_text(s,encoding='utf-8')
p=Path('wiki-raw/wms_admin_ui_reference/day-reconciliation-documents.js');s=p.read_text(encoding='utf-8');s=s.replace("  if(kind==='WAREHOUSE_TASK'", "  if(kind==='EVENT_OUTBOX'&&/^[1-9]\\d*$/.test(id))return 'external-outbox.html?event_id='+encodeURIComponent(id);\n  if(kind==='WAREHOUSE_TASK'");s=s.replace("details.append(node('p','Текущие незавершённые обязательства; порядок по идентификатору. Это не список только за выбранный день.'));", "details.append(node('p',documents.scope==='CURRENT_EXTERNAL_MESSAGES'?'Сообщения текущей очереди; принятие внешней системой проверяется отдельно. Порядок по идентификатору.':'Текущие незавершённые обязательства; порядок по идентификатору. Это не список только за выбранный день.'));");p.write_text(s,encoding='utf-8')
p=Path('wiki-raw/wms_admin_ui_reference/external-outbox.js');s=p.read_text(encoding='utf-8');old='  loadOutbox().catch(showExternalError);\n}\n\nfunction showExternalError';new='''  const eventId = new URLSearchParams(location.search).get("event_id");
  if (eventId && /^[1-9]\\d{0,17}$/.test(eventId)) {
    outboxEl("externalStatusText").textContent = "Открывается сообщение " + eventId;
    loadOutboxDetail(eventId).then(() => loadRegulatoryRuntime()).catch(showExternalError);
  } else loadOutbox().catch(showExternalError);
}

function showExternalError''';assert old in s;s=s.replace(old,new);p.write_text(s,encoding='utf-8')