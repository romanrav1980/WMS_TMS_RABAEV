import sys,json
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();chunks=[]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select user,sys_context('USERENV','SERVICE_NAME')from dual");assert q.fetchone()==("RABAEV","orcl")
 for kind in ("PACKAGE","PACKAGE BODY"):
  q.execute("select TEXT from USER_SOURCE where NAME='RRL_CASE_SCALE_ADMISSION'and TYPE=:p_kind order by LINE",p_kind=kind)
  chunks.append("create or replace "+"".join(r[0]for r in q.fetchall()).replace("\r\r\n","\n").replace("\r\n","\n").strip()+"\n/\n")
old="\n".join(chunks);new=old
a="   select count(*)into n from RRL_SKU_RECEIPT_PROFILE where ARTICUL=l.ARTICUL;"
assert a in old
new=new.replace(a,"""   select greatest(nvl((select CRPT_REQUIRED from RRL_FINISHED_GOODS_SKU where ARTICUL=l.ARTICUL),0),
    case when exists(select 1 from RRL_SKU_RECEIPT_PROFILE where ARTICUL=l.ARTICUL)then 1 else 0 end)into n from dual;""")
a="  delta_qty:=RRL_STOCK_MATH.quantity(m.get_string('fact_qty'))-p_previous;"
new=new.replace(a,a+"""
  select count(*)into n from RRL_ARTICULS where ACTICUL=l.ARTICUL and TYPE_W in(2,3,5,6,7);
  if n!=1 then raise_application_error(-20886,'WAREHOUSE_SCALE_CURRENT_WEIGHTED_SKU_REQUIRED');end if;
  select count(*)into n from RRL_STOCK_UOM_CONVERSION where ARTICUL=l.ARTICUL and INPUT_UOM='KG'and BASE_UOM='KG'and NUMERATOR=1 and DENOMINATOR=1;
  if n!=1 then raise_application_error(-20886,'WAREHOUSE_SCALE_CURRENT_KG_BASE_REQUIRED');end if;
""")
a="   if marked!=0 or n!=0"
new=new.replace(a,"""   if m.get_string('scan_product')is null or m.get_string('scan_product')!=c.SCANNED_PRODUCT then raise_application_error(-20886,'WAREHOUSE_SCALE_ORIGINAL_PRODUCT_REQUIRED');end if;
   if marked!=0 or n!=0""")
f="db/migrations/2026-10-11_ni042_scale_net/"
print(json.dumps({f+"000_before_admission.sql":old,f+"001_admission.sql":new,
 f+"apply.sql":"@@001_admission.sql\n",f+"rollback.sql":"@@000_before_admission.sql\n"},ensure_ascii=True))
