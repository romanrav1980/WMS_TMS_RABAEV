import hashlib,json,sys
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
ROOT=Path(__file__).resolve().parents[1];load_local_oracle_environment();sys.path.insert(0,str(ROOT/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();old=[]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as conn:
 cur=conn.cursor();cur.execute("select user,sys_context('USERENV','SERVICE_NAME') from dual")
 if cur.fetchone()!=("RABAEV","orcl"):raise RuntimeError("Unexpected target")
 cur.execute("select STATE from RRL_STOCK_RELEASE where RELEASE_ID=1")
 if cur.fetchone()!=("PREPARED",):raise RuntimeError("Dormant refresh only")
 for name in ("RRL_INTERNAL_MOVE2","RRL_INTERNAL_MOVE3"):
  cur.execute("select TEXT from USER_SOURCE where NAME=:n and TYPE='FUNCTION' order by LINE",n=name)
  old.append("create or replace "+"".join(r[0] for r in cur)+"\n/\n")
cp=ROOT/"runtime/stock_posting_20261008/182_internal-null-unit-checkpoint";cp.mkdir(parents=True,exist_ok=False)
(cp/"source.sql").write_text("\n".join(old),encoding="utf-8")
p="db/migrations/2026-10-08_stock_posting_core/"
print(json.dumps({p+"182_internal_null_unit_apply.sql":"@@067_internal_entrypoints.sql\n@@014b_recompile.sql\n",
p+"182_internal_null_unit_rollback.sql":"declare n number;begin select count(*) into n from RRL_STOCK_OPERATION;if n>0 then raise_application_error(-20808,'POSTED_OPERATIONS_PREVENT_CODE_ROLLBACK');end if;end;\n/\n"+"\n".join(old)+"\n@@014b_recompile.sql\n"},ensure_ascii=True))
