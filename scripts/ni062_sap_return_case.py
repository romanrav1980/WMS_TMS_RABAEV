"""Assumed UTF-8 gateway XML bound to actual own approval, not a real SAP transmission."""
import sys,base64,json
from pathlib import Path
from uuid import uuid4
import xml.etree.ElementTree as ET
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.modules.integrations.domain.store_return import read_store_return
cfg=get_settings();tag=uuid4().hex[:10];base="http://127.0.0.1:8088"
client=httpx.Client(auth=("admin","admin123"),timeout=30)
with oracledb.connect(user=cfg.oracle_user,password=cfg.oracle_password,dsn=cfg.oracle_dsn) as c:
 q=c.cursor()
 q.execute("select OPERATION_ID,RECEIPT_OPERATION_ID,LINE_NO,LOT_UID,ARTICLE,BASE_UOM,to_char(BASE_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,'''),DISPOSITION from RRL_STORE_RETURN_APPROVAL where RECEIPT_OPERATION_ID='STORE.RECEIPT:bea258a7dd' and DISPOSITION='SUPPLIER'")
 approval,receipt,line,lot,article,uom,qty,disposition=q.fetchone()
 q.execute("select DEFAULT_RECEIVE_CELL from RRL_WARES where ID=9104");cell=q.fetchone()[0]
 values={"Sender":"OWN.QA.SAP","MessageId":"RETURN."+tag,"ReturnDocumentNumber":"OWN.RTN."+tag,"ApprovalOperationId":approval,"OriginalReceiptOperationId":receipt,"OriginalLineNumber":str(line),"WarehouseId":"9104","ReceiveCell":cell,"Article":article,"LotId":lot,"Quantity":qty,"Disposition":disposition}
 def xml(fields):
  root=ET.Element("WarehouseStoreReturn",version="1")
  for name,value in fields.items():
   node=ET.SubElement(root,name,**({"unit":uom} if name=="Quantity" else {}));node.text=value
  return ET.tostring(root,encoding="utf-8",xml_declaration=True)
 raw=xml(values);parsed=read_store_return(raw)
 def call(payload,status):
  r=client.post(base+"/api/integrations/sap/store-returns",content=payload,headers={"Content-Type":"application/xml"});assert r.status_code==status,(r.status_code,r.text[:1800]);return r.json()
 wrong=call(xml({**values,"MessageId":"BAD.QTY."+tag,"Quantity":"2"}),409);assert "SAP_RETURN_ORIGINAL_APPROVAL_MISMATCH" in wrong["detail"]["message"],wrong
 wrong=call(xml({**values,"MessageId":"BAD.WARE."+tag,"ReceiveCell":"FOREIGN"}),409);assert "SAP_RETURN_CONFIGURED_RECEIVING_ZONE_REQUIRED" in wrong["detail"]["message"],wrong
 command={"contract_version":2,"operation_id":"SAP.RETURN.BAD.RAW:"+tag,"command_type":"STORE_RETURN_SAP_BIND","actor":"admin","source":{"approval_operation_id":approval},"lines":[],"units":[],"metadata":{**parsed["metadata"],"article":"FORGED"}}
 # Mismatched original XML cannot be substituted by direct command metadata.
 command["metadata"]["article"]=article
 forged=xml({**values,"Article":"FORGED"})
 from hashlib import sha256
 command["metadata"]["raw_base64"]=base64.b64encode(forged).decode();command["metadata"]["payload_hash"]=sha256(forged).hexdigest()
 inp,out=q.var(oracledb.DB_TYPE_CLOB),q.var(oracledb.DB_TYPE_CLOB);inp.setvalue(0,json.dumps(command))
 try:
  q.callproc("RRL_STOCK_POSTING_API.prepare_command",[inp,"admin",out,None]);raise AssertionError("Raw XML fields bypassed")
 except oracledb.DatabaseError as exc:
  c.rollback();assert "SAP_RETURN_ORIGINAL_XML_FIELDS_CONFLICT" in str(exc),str(exc)
 finally:q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 result=call(raw,202);assert result["approval_operation_id"]==approval and result["sap_contract_imported"] and not result["warehouse_stock_changed"] and not result["external_ack_created"],result
 assert call(raw,202)==result
 wrong=call(xml({**values,"ReturnDocumentNumber":"OTHER."+tag}),409);assert wrong["detail"]["outcome_confirmed"],wrong
 wrong=call(xml({**values,"MessageId":"SECOND."+tag}),409);assert "SAP_RETURN_APPROVAL_OR_DOCUMENT_ALREADY_BOUND" in wrong["detail"]["message"],wrong
 op=parsed["operation_id"]
 q.execute("select dbms_lob.substr(ORIGINAL_XML_BASE64,32767,1),ORIGINAL_SHA256 from RRL_STORE_RETURN_SAP where OPERATION_ID=:op",op=op)
 saved,digest=q.fetchone();assert base64.b64decode(saved)==raw and digest==sha256(raw).hexdigest()
 q.execute("select count(*) from RRL_EVENTS where OPERATION_ID=:op",op=op);assert q.fetchone()==(0,)
 q.execute("select count(*) from RRL_EVENT_OUTBOX where CORRELATION_ID=:op",op=op);assert q.fetchone()==(1,)
 try:q.execute("delete from RRL_STORE_RETURN_SAP where OPERATION_ID=:op",op=op);c.commit();raise AssertionError("Original deleted")
 except oracledb.DatabaseError as exc:c.rollback();assert "SAP_RETURN_BINDING_IMMUTABLE" in str(exc)
print("PASS093 actual XML import/source/warehouse/hash/original fields/retry/conflict/duplicate binding/immutable/outbox1/events0; assumed gateway, no real SAP ACK",flush=True)
