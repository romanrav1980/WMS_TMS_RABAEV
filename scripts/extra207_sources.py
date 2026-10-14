import sys,json,hashlib
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();out={};f=Path("db/migrations/2026-10-11_ni042_case_mass")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();parts=[]
 for kind in("PACKAGE","PACKAGE BODY"):
  q.execute("select TEXT from USER_SOURCE where NAME='RRL_STOCK_STORE_WEIGHT_CORE'and TYPE=:kind order by LINE",kind=kind)
  parts.append("create or replace "+"".join(x[0]for x in q.fetchall()).replace("\r\r\n","\n").replace("\r\n","\n").strip()+"\n/\n")
 out[str(f/"000_before_store_weight.sql")]="\n".join(parts)
p=f/"checkpoint.json";checkpoint=json.loads(p.read_text(encoding="utf-8"));checkpoint["sha256"].update({k:hashlib.sha256(v.encode()).hexdigest()for k,v in out.items()})
out[str(p)]=json.dumps(checkpoint,indent=2)
p=f/"001_schema.sql";text=p.read_text(encoding="utf-8")
text=text.replace(" MEASURED_CONTENT_VERSION number,"," MEASURED_CONTENT_VERSION number,\n COVERAGE_COMPLETE number(1)default 1 not null,")
text=text.replace("  and TARE_WEIGHT_KG>0 and NET_WEIGHT_KG>0","  and TARE_WEIGHT_KG is not null and NET_WEIGHT_KG is not null and DEVICE_MODE is not null and SIGNATURE_VERSION is not null\n  and TARE_WEIGHT_KG>0 and NET_WEIGHT_KG>0")
text+="\nalter table RRL_TT_LOAD_BOX_WEIGHT add constraint RRL_LOAD_BOX_COVER_C check(COVERAGE_COMPLETE in(0,1));\n"
out[str(p)]=text
print(json.dumps(out,ensure_ascii=True))
