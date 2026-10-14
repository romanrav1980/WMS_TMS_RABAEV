exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
d=Path("db/migrations/2026-10-14_ni053_stock_pallet_unload");files={}
assert not (d/"checkpoint.json").exists()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select user,sys_context('USERENV','SERVICE_NAME')from dual");assert q.fetchone()==("RABAEV","orcl")
 q.execute("select TEXT from USER_SOURCE where NAME='RRL_STORE_UNLOAD_CORE'and TYPE='PACKAGE BODY'order by LINE")
 source="".join(r[0]for r in q.fetchall());assert source
 files[str(d/"000_before_body.sql")]="create or replace "+source+"\n/\n"
 q.execute("select f.TYPE_ORIGIN,f.SOURCE_REFERENCE,f.CONFIRMATION_JSON from RRL_TT_LOAD_FLOOR_FACT f where f.LOAD_OPERATION_ID='TT.LOAD:d00a9887-fee3-4c58-938b-5b18cadebfcb'")
 proof=q.fetchone();proof=list(proof);proof[2]=proof[2] if isinstance(proof[2],dict) else json.loads(proof[2].read())
 q.execute("select OBJECT_NAME,OBJECT_TYPE from USER_OBJECTS where STATUS='INVALID'")
 files[str(d/"checkpoint.json")]=json.dumps({"migration_id":"2026-10-14-1316-stock-pallet-unload","target":"RABAEV/orcl","invalid_before":q.fetchall(),"own_load_proof":proof},indent=2)
print(json.dumps(files,ensure_ascii=True))
