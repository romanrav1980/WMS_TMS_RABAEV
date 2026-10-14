import sys,json,hashlib
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();parts=[]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for kind in("PACKAGE","PACKAGE BODY"):
  q.execute("select TEXT from USER_SOURCE where NAME='RRL_STOCK_POSTING_API'and TYPE=:kind order by LINE",kind=kind)
  parts.append("create or replace "+"".join(x[0]for x in q.fetchall()).replace("\r\r\n","\n").replace("\r\n","\n").strip()+"\n/\n")
f=Path("db/migrations/2026-10-11_ni042_final_qc");text="\n".join(parts)
p=f/"checkpoint.json";checkpoint=json.loads(p.read_text(encoding="utf-8"));checkpoint["sha256"][str(f/"000_before_root.sql")]=hashlib.sha256(text.encode()).hexdigest()
print(json.dumps({str(f/"000_before_root.sql"):text,str(p):json.dumps(checkpoint,indent=2)},ensure_ascii=True))
