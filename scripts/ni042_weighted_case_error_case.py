import httpx,sys
from pathlib import Path
import oracledb
from uuid import uuid4
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select CASE_PICK_LINE_ID from RRL_CASE_PICK_LINE where CASE_PICK_TASK_ID=1057");line=int(q.fetchone()[0])
 path=f"http://127.0.0.1:8088/api/case-pick/tasks/1057/lines/{line}/weighted-box"
 body={"operation_id":"WEIGHT184.BAD:"+uuid4().hex,"weighted_box_barcode":"invalid","scan_cell":"Q167Dc863807924","scan_container":"own invalid scan fixture"}
 r=httpx.post(path,auth=("admin","admin123"),json=body,timeout=30);assert r.status_code==409,(r.status_code,r.text[:1000])
 r=httpx.post(path,auth=("admin","admin123"),json={**body,"fact_qty":"1"},timeout=30);assert r.status_code==422,(r.status_code,r.text[:1000])
 q.execute("select ID,PASS from RUSERS where ID='Q1341a19738325'and nvl(DELETED,0)=0");user=q.fetchone();assert user
 r=httpx.post(path,auth=user,json=body,timeout=30);assert r.status_code==403,(r.status_code,r.text[:1000])
 q.execute("select count(*)from RRL_STOCK_OPERATION where OPERATION_ID=:p_op",p_op=body["operation_id"]);assert q.fetchone()[0]==0
 print("PASS184 invalid GS1409/manual fact forbidden422/current foreign warehouse403/no operation or stock facts")
