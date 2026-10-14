exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
out={};base="db/migrations/2026-10-11_ni061_partial_receiving/"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for name in ["RRL_INTERWARE_DEPART_GATE","RRL_INTERWARE_ROUTING","RRL_STOCK_INTERWARE_NEXT"]:
  q.execute("select TEXT from USER_SOURCE where NAME=:object_name and TYPE='PACKAGE BODY'order by LINE",object_name=name)
  out[base+"000_before_"+name.lower()+"_body.sql"]="create or replace "+"".join(r[0]for r in q)+"\n/\n"
 q.execute("select TEXT from USER_SOURCE where NAME='RRL_TT_HU_LOAD_FACT_GUARD'and TYPE='TRIGGER'order by LINE")
 out[base+"000_before_rrl_tt_hu_load_fact_guard.sql"]="create or replace "+"".join(r[0]for r in q)+"\n/\n"
print(json.dumps(out,ensure_ascii=True))
