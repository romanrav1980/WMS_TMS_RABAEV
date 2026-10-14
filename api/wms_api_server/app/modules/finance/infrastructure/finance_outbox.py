from hashlib import sha256
from typing import Any
import json,oracledb

def enqueue(cursor: Any,event_type: str,operation_id: str,payload: dict[str,Any],semantics: str) -> str:
    event_id="FIN:"+sha256((event_type+":"+operation_id).encode()).hexdigest()
    body={**payload,"operation_id":operation_id,"event_type":event_type,"posting_semantics":semantics,"external_sap_ack":False}
    cursor.setinputsizes(payload_body=oracledb.DB_TYPE_CLOB)
    cursor.execute("insert into RRL_SAP_RECEIPT_OUTBOX(EVENT_ID,EVENT_TYPE,PAYLOAD_JSON)values(:event_id,:event_type,:payload_body)",{"event_id":event_id,"event_type":event_type,"payload_body":json.dumps(body,ensure_ascii=False)})
    return event_id

def expense_payload(cursor: Any,expense: str,result: dict[str,Any]) -> dict[str,Any]:
    cursor.execute("""select ARTICLE_CODE,ARTICLE_NAME,WARE_ID,OBJECT_KIND,OBJECT_ID,
    to_char(AMOUNT*ADJUSTMENT_SIGN,'TM9','NLS_NUMERIC_CHARACTERS=''.,'''),CURRENCY,
    to_char(EXPENSE_DATE,'YYYY-MM-DD'),DOCUMENT_REFERENCE,CORRECTION_OF_OP,ACTOR,COST_CORRECTION_OF_OP
    from RRL_LOGISTICS_EXPENSE where OPERATION_ID=:id""",{"id":expense})
    names=["article_code","article_name","warehouse_id","object_kind","object_id","amount","currency","expense_date","document_reference","correction_of_operation_id","reported_by","cost_correction_of_operation_id"]
    return {**dict(zip(names,cursor.fetchone())),**result,"expense_operation_id":expense}
