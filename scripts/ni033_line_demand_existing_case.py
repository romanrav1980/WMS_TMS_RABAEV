"""171 compare captured old read algorithm with current data in the SAME read-only snapshot."""
import sys,json
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();source=Path("db/migrations/2026-10-11_ni033_line_demand/000_before_pool.sql").read_text(encoding="utf-8-sig")
start=source.index(" function snapshot_json(",source.index("create or replace package body"))
legacy=source[start:source.rindex("\nend;\n/")]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("set transaction read only")
 for ware,article in[(6667491,"QNATIVED9A5C53B54"),(20052672,"QC16700CDC0EF51")]:
  out=q.var(oracledb.DB_TYPE_CLOB)
  q.execute("declare "+legacy+"\nbegin :p_result:=snapshot_json(:p_ware,:p_article);end;",p_result=out,p_ware=ware,p_article=article)
  raw=out.getvalue();before=json.loads(raw.read()if hasattr(raw,"read")else raw)
  q.execute("select RRL_STOCK_POOL_READ.snapshot_json(:p_ware,:p_article)from dual",p_ware=ware,p_article=article);raw=q.fetchone()[0];current=json.loads(raw.read()if hasattr(raw,"read")else raw)
  assert current==before,(ware,article)
  for order in current["orders"]:
   q.execute("select RRL_STOCK_POOL_READ.line_snapshot_json(:p_line)from dual",p_line=order["line_id"]);raw=q.fetchone()[0];line=json.loads(raw.read()if hasattr(raw,"read")else raw)
   assert all(line[k]==v for k,v in order.items()if k!="dispatch_order"),(order,line)
   assert line["warehouse"]==ware and line["article"]==article and line["open"]
   assert line["quantity_semantics"]=="UNALLOCATED_BASE_NOT_SHIPPED_PROOF"
  print("PASS171 original captured algorithm equals current pool on current data",ware,"rows",len(current["orders"]))
 c.rollback()
print("PASS171 targeted line uses same native formula/units/overlap; no DML or snapshot reset")
