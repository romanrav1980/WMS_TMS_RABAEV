"""176 current HU composition and slots scope; read-only ordinary empty HU, no fake CASE facts."""
import sys
from pathlib import Path
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();actor="Q1341a19738325";root="http://127.0.0.1:8088/api/warehouse-hus"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select PASS,USER_GROUP from RUSERS where ID=:p_actor",p_actor=actor);secret,group=q.fetchone()
 q.execute("select count(*)from RIGHTS where USER_GROUP=:p_group and lower(trim(RIGHT1))='warehouse_task_view'",p_group=group);had=q.fetchone()[0]
 if not had:q.execute("insert into RIGHTS(USER_GROUP,RIGHT1)values(:p_group,'warehouse_task_view')",p_group=group);c.commit()
 try:
  with httpx.Client(auth=("admin","admin123"),timeout=30)as client:
   response=client.get(root+"/composition",params={"identifier":"HU.CASE:cea0ff2dc1"})
   assert response.status_code==200,(response.status_code,response.text[:1600])
   assert response.json()["warehouse"]==13641631 and response.json()["leaf_count"]==0
   assert client.get(root+"/target-slots",params={"cell":"QHcea0ff2dc1","warehouse":13641631}).status_code==200
  with httpx.Client(auth=(actor,secret),timeout=30)as client:
   assert client.get(root+"/composition",params={"identifier":"HU.CASE:cea0ff2dc1"}).status_code==403
   assert client.get(root+"/target-slots",params={"cell":"QHcea0ff2dc1","warehouse":13641631}).status_code==403
 finally:
  if not had:q.execute("delete from RIGHTS where USER_GROUP=:p_group and RIGHT1='warehouse_task_view'",p_group=group);c.commit()
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491")
 assert q.fetchone()==(20,20)
 print("PASS176 actual HTTP empty HU composition/target slots admin200/foreign403, current actor/right/WARE in one READ ONLY snapshot; originalP20H20 unchanged")
