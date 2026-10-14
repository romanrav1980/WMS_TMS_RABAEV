from pathlib import Path
import sys,json,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select OPERATION_ID,ROOT_UID,SOURCE_WARE_ID,TARGET_WARE_ID,SOURCE_LOAD_OPERATION_ID,SOURCE_TT_ID,TARGET_TT_ID,INBOUND_DOCK,OUTBOUND_DOCK,RESULT_JSON,SOURCE_COMPOSITION_JSON from RRL_INTERWARE_PLAN where OPERATION_ID like 'IW225.PLAN:%'order by CREATED_AT desc fetch first 1 rows only")
 row=q.fetchone();print(json.dumps(row[:9],ensure_ascii=True));value=row[9];print(json.dumps(value if isinstance(value,dict)else json.loads(value.read()if hasattr(value,"read")else value),ensure_ascii=True))
 q.execute("select RRL_INTERWARE_UNIT_SOURCE.issued_manifest(:load_id,:root_id,:snapshot)from dual",load_id=row[4],root_id=row[1],snapshot=row[10]);value=q.fetchone()[0];print(value.read()if hasattr(value,"read")else value)
