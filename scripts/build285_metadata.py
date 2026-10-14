exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
out={}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select TEXT from USER_SOURCE where NAME='RRL_STOCK_METADATA_TX'and TYPE='PACKAGE BODY'order by LINE")
 body="".join(r[0]for r in q)
 assert "'warehouse_settings_edit'"not in body
 print(body[:1100],file=sys.stderr)
 changed=body.replace("'transport_dispatch_edit'","'transport_dispatch_edit','warehouse_settings_edit'")
 assert changed!=body
 base="db/migrations/2026-10-11_ni081_warehouse_depot/"
 out[base+"006_before_metadata.sql"]="create or replace "+body+"\n/\n"
 out[base+"007_metadata.sql"]="create or replace "+changed+"\n/\n"
print(json.dumps(out,ensure_ascii=True))
