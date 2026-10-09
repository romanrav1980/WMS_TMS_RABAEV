"""Record the five removed automatic receipt paths and their concrete replacement."""
import hashlib
import json
import sys
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
ROOT=Path(__file__).resolve().parents[1]
load_local_oracle_environment()
sys.path.insert(0,str(ROOT/"api/wms_api_server"))
from app.config import get_settings
s=get_settings()
items=[("RRL_ACCEPT_ORDER2","PROCEDURE"),("RRL_ACCEPT_ORDER2_2","PROCEDURE"),
 ("RRL_ACCEPT_ORDER2_3","FUNCTION"),("RRL_ACCEPT_ORDER3","PROCEDURE"),("RRL_OTKAT_ORDER2","PROCEDURE")]
statements=["declare v varchar2(20);begin select STATE into v from RRL_STOCK_RELEASE where RELEASE_ID=1;if v!='PREPARED' then raise_application_error(-20808,'REGISTRY_REQUIRES_PREPARED');end if;end;\n/\n"]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as conn:
 cur=conn.cursor()
 for name,kind in items:
  cur.execute("select STATUS from USER_OBJECTS where OBJECT_NAME=:n and OBJECT_TYPE=:t",n=name,t=kind)
  if cur.fetchone()!=("VALID",):raise RuntimeError("Invalid adapter: "+name)
  cur.execute("select TEXT from USER_SOURCE where NAME=:n and TYPE=:t order by LINE",n=name,t=kind)
  source="create or replace "+"".join(row[0] for row in cur).rstrip()+"\n/\n"
  if "SAP_SCANNED_RECEIPT_REQUIRED" not in source or "state='PREPARED'" not in source:
   raise RuntimeError("Replacement entrypoint missing: "+name)
  digest=hashlib.sha256(source.encode("utf-8")).hexdigest()
  statements.append("update RRL_STOCK_WRITER_REGISTRY set STATE='RETIRED',SOURCE_HASH='"+digest+"',ADAPTER_REFERENCE='db/migrations/2026-10-08_stock_posting_core/147_receipt_entrypoints.sql; wiki-raw/wms_admin_ui_reference/receiving.html',UPDATED_AT=systimestamp where WRITER_KEY='ORACLE:"+kind+":"+name+"';")
statements.append("commit;\n")
print(json.dumps({"149_receipt_writer_registry.sql":"\n".join(statements)},ensure_ascii=True))
