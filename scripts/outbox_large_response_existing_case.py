"""159 native CLOB response >32K; original numeric/Unicode text unchanged, no real provider."""
import sys,json
from pathlib import Path
from uuid import uuid4
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.services.outbox_service import OutboxService
from app.modules.integrations.public import RegulatoryResponse
s=get_settings();tag=uuid4().hex[:10];target="Q159_"+tag
response='{"simulation":true,"text":"'+("ж"*40000)+'","exact":12345678901234567890123456789.123456789}'
class Simulated:
 mode="MOCK";configured=True;simulated=True;signature_status="MOCK_NOT_SIGNED";cert_alias=None;cert_thumbprint=None
 def send(self,event):return RegulatoryResponse("DONE","SIMULATED_LARGE_RESPONSE","SIMULATED159:"+tag,None,200,response,False)
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select count(*)from RRL_EVENTS");before=q.fetchone()
 payload=q.var(oracledb.DB_TYPE_CLOB);payload.setvalue(0,'{"fixture":"'+tag+'"}')
 event=int(q.callfunc("RRL_TRACEABILITY_API.enqueue_event",oracledb.DB_TYPE_NUMBER,
  ["QA_LARGE_RESPONSE","OUTBOX_TEST",tag,"Q159:"+tag,payload,target,tag,3]));c.commit()
 result=OutboxService(adapter=Simulated()).process_next("QA159:"+tag,target)
 assert result["status"]=="DONE"and result["real_external_ack"]is False,result
 q.execute("select to_clob(RESPONSE_JSON),STATUS,HTTP_STATUS,FINISH_HASH from RRL_ADAPTER_REQUEST_LOG where ADAPTER_REQUEST_ID=:id",id=result["adapter_request_id"])
 row=q.fetchone();raw=row[0].read()if hasattr(row[0],"read")else row[0]
 assert raw==response and len(raw)>32767 and row[1:3]==("DONE",200) and len(row[3])==64
 q.execute("select STATUS from RRL_EVENT_OUTBOX where EVENT_OUTBOX_ID=:id",id=event);assert q.fetchone()==("DONE",)
 q.execute("select count(*)from RRL_EVENTS");assert q.fetchone()==before
 print("PASS159 native response CLOB",len(raw),"chars",len(raw.encode()),"UTF8bytes/exact38digit numeric+Unicode text/eventDONE/mocknotlegalACK/no stock",event,tag,flush=True)
