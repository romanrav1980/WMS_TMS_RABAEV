exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
import httpx
from app.modules.platform.public import read_oracle_json
ctx=json.loads(Path("tmp/context669.json").read_text())
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select CANONICAL_REQUEST,RESULT_JSON from RRL_STOCK_OPERATION where OPERATION_ID=:operation and STATE='APPLIED'",operation="IW669.BIRTH:"+ctx["tag"]);row=q.fetchone();command=read_oracle_json(row[0]);expected=read_oracle_json(row[1])
 q.execute("select ID,PASS from RUSERS where ID='admin'and nvl(DELETED,0)=0");user,password=q.fetchone()
body={**command["metadata"],"operation_id":command["operation_id"]}
with httpx.Client(auth=(user,password),base_url="http://127.0.0.1:8088",timeout=20)as client:
 response=client.post("/api/receiving/supply-orders/"+command["source"]["order_id"]+"/pallets",json=body);assert response.status_code==201,response.text
 assert response.json()==expected
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select nvl(sum(REMAIN),0),nvl(sum(HARD_RESERVED_BASE),0)from RRL_REMAINS where UID_POLETA=:p_uid and CELL=:cell",p_uid=ctx["lot"],cell=ctx["shipcell"]);assert q.fetchone()==(0,0)
 q.execute("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),round(BUFFER_GETS/nullif(EXECUTIONS,0),2)
 from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and upper(SQL_TEXT)like 'INSERT INTO RRL_PALLETS(UID_PALLET,SSCC,ARTICUL,CREATION_DATE,EXPIRY_DATE,PRODUCED_DATE,UNIT_COUNT,PRIHOD_NAKLAD_ID,KLADOVSHIK,PRINTED)%'
 order by LAST_ACTIVE_TIME desc fetch first 2 rows only""");stats=q.fetchall()
print(json.dumps({"status":"PASS","legacy_sscc_birth_replay_exact":True,"legacy_shipping_P_H":[0,0],"new_registered_header_stats":stats}))
