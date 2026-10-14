exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
import hashlib
f="db/migrations/2026-10-12_ni071_unload_norm_basis/";out={}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();parts=[]
 for kind in ["PACKAGE","PACKAGE BODY"]:
  q.execute("select TEXT from USER_SOURCE where NAME='RRL_TRANSPORT_NORM_API'and TYPE=:kind order by LINE",kind=kind)
  parts.append("create or replace "+"".join(r[0]for r in q.fetchall()).replace("\r","").strip()+"\n/\n")
 old="\n".join(parts);out[f+"000_before_norm.sql"]=old
v=old
def change(a,b):
 global v
 assert v.count(a)==1,(a,v.count(a));v=v.replace(a,b)
change("roll_rate number;manual_rate number;loader_rate number;","roll_rate number;manual_rate number;loader_rate number;pallet_rate number;unload_basis varchar2(16);")
change("if keys.count!=14 then","if keys.count not in(14,16)then")
change("'loader_rate','expected_version','reason','decision_reference')","'loader_rate','expected_version','reason','decision_reference','unload_charge_basis','pallet_unload_rate')")
# After both replay opportunities, require explicit basis and PALLET rate for new versions.
change("if price.PRICE is null or price.PRICE<0", "unload_basis:=d.get_string('unload_charge_basis');\n  if unload_basis is null or unload_basis not in('POINT','PLACE')then raise_application_error(-20886,'TRANSPORT_UNLOAD_BASIS_REQUIRED');end if;\n  pallet_rate:=decimal_value(d,'pallet_unload_rate');\n  if price.PRICE is null or price.PRICE<0")
change("result.put('loader_rate',RRL_STOCK_PLAN_HELPER.decimal_text(loader_rate));","result.put('unload_charge_basis',unload_basis);result.put('pallet_unload_rate',RRL_STOCK_PLAN_HELPER.decimal_text(pallet_rate));\n  result.put('loader_rate',RRL_STOCK_PLAN_HELPER.decimal_text(loader_rate));")
out[f+"001_norm_basis.sql"]=v
out[f+"checkpoint.json"]=json.dumps({"migration_id":"2026-10-12-572-explicit-unload-cost-basis","before_sha256":hashlib.sha256(old.encode()).hexdigest(),"after_sha256":hashlib.sha256(v.encode()).hexdigest(),"recovery":"Original norm source saved. Legacy14-field exact replay retained; new versions require POINT/PLACE and explicit pallet rate. Existing history never rewritten."},indent=2)+"\n"
print(json.dumps(out))
