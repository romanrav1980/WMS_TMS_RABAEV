"""Even an outer PL/SQL caller that catches failure cannot commit a half-created trip."""
import sys,json
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.modules.platform.public import read_oracle_json
s=get_settings();op="CLUSTER139:b40b0303ee3b.ROLLBACK"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select REQUEST_JSON,RESULT_JSON from RRL_CLUSTER_CREATE_RESULT where OPERATION_ID=:op",op="CLUSTER139:b40b0303ee3b")
 request,result=map(read_oracle_json,q.fetchone())
 q.execute("select count(*)from RRL_TRANSPORT_TASK");before=q.fetchone()[0]
 out=q.var(oracledb.DB_TYPE_CLOB)
 q.execute("begin begin RRL_CLUSTER_CREATE_API.create_cluster(:op,'admin',:body,:sts,:result);exception when others then null;end;end;",
   op=op,body=json.dumps(request,sort_keys=True,separators=(",",":"),ensure_ascii=False),sts=json.dumps(result["source_st_numbers"]),result=out)
 c.commit()
 q.execute("select count(*)from RRL_CLUSTER_CREATE_RESULT where OPERATION_ID=:op",op=op);assert q.fetchone()==(0,)
 q.execute("select count(*)from RRL_TRANSPORT_TASK");assert q.fetchone()[0]==before
 print("PASS139 native savepoint: outer PL/SQL catches unavailable retired vehicle and commits, but no partial TT/operation survived",flush=True)
