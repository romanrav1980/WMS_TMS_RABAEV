exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
d=Path("db/migrations/2026-10-11_ni061_loss_recovery");d.mkdir(exist_ok=True)
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for name in["RRL_STOCK_POSTING_API","RRL_STOCK_BALANCE_CORE","RRL_STOCK_LOCATION_CORE","RRL_STOCK_UNIT_CORE","RRL_STOCK_INTERWARE_PART"]:
  for kind in["PACKAGE","PACKAGE BODY"]:
   q.execute("select TEXT from USER_SOURCE where NAME=:pkg and TYPE=:kind order by LINE",pkg=name,kind=kind);source="".join(r[0]for r in q).replace(chr(13)," ").strip();assert source
   (d/("000_before_"+name.lower()+"_"+kind.lower().replace(" ","_")+".sql")).write_text("create or replace "+source+"\n/\n",encoding="utf-8")
 for name in["RRL_STOCK_UNIT_GUARD","RRL_SAP_PALLET_GUARD"]:
  q.execute("select TEXT from USER_SOURCE where NAME=:pkg and TYPE='TRIGGER'order by LINE",pkg=name);source="".join(r[0]for r in q).replace(chr(13)," ").strip()
  if source:(d/("000_before_"+name.lower()+".sql")).write_text("create or replace "+source+"\n/\n",encoding="utf-8")
print("Captured299 current root/balance/location/unit/partial and available guards; no copy/mutation")
