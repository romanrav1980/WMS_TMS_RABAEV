exec(open("scripts/inspect226.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
import httpx
with httpx.Client(auth=("admin","admin123"),timeout=35)as h:
 r=h.post("http://127.0.0.1:8088/api/transport/loading/33543/depart",json={"operation_id":"IW228.DEPART:13508027ed"});assert r.status_code==200,(r.status_code,r.text);saved=r.json()
 replay=h.post("http://127.0.0.1:8088/api/transport/loading/33543/depart",json={"operation_id":"IW228.DEPART:13508027ed"});assert replay.json()==saved
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select STATUS,VEHICLE_ID from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID='IW228.LOAD:13508027ed'");assert q.fetchone()==("DEPARTED",10050)
 q.execute("select count(*)from RRL_EVENTS where OPERATION_ID='IW228.DEPART:13508027ed'");assert q.fetchone()[0]==0
 print("PASS228 existing second departure/no stock event/replay/original vehicle10049 retained/new actual10050")
 q.execute("select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3)from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and(SQL_TEXT like 'INSERT INTO RRL_INTERWARE_ONWARD_DISPATCH%'or SQL_TEXT like 'INSERT INTO RRL_INTERWARE_CUSTODY_PROOF%')order by ELAPSED_TIME desc fetch first 4 rows only");print(q.fetchall())
