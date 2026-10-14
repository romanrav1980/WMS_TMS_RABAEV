"""164 existing CASE1031 and personalQ134; temporary own right/ware restore, no goods."""
import sys
from pathlib import Path
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();actor="Q1341a19738325";base="http://127.0.0.1:8088/api/case-pick"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select PASS,USER_GROUP,WARE_ID,DELETED from RUSERS where ID=:id",id=actor);secret,group,ware,deleted=q.fetchone()
 q.execute("select count(*)from RIGHTS where USER_GROUP=:grp and lower(trim(RIGHT1))='case_pick_view'",grp=group);had_right=q.fetchone()[0]
 q.execute("select min(CASE_PICK_TASK_ID)from RRL_CASE_PICK_TASK where WARE_ID!=:ware and WARE_ID is not null",ware=ware);foreign=q.fetchone()[0];assert foreign
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");stock=q.fetchone()
 if not had_right:q.execute("insert into RIGHTS(USER_GROUP,RIGHT1)values(:grp,'case_pick_view')",grp=group);c.commit()
 try:
  with httpx.Client(auth=(actor,secret),timeout=30)as person,httpx.Client(auth=("admin","admin123"),timeout=30)as admin:
   own=person.get(base+"/tasks/1031");assert own.status_code==200,(own.status_code,own.text[:1200])
   assert own.json()["ware_id"]==ware and own.json()["lines"][0]["planned_qty"]=="12"
   standard=admin.get(base+"/tasks/1031");assert standard.status_code==200 and standard.json()==own.json()
   denied=person.get(base+f"/tasks/{foreign}");assert denied.status_code==403,(denied.status_code,denied.text[:900])
   listed=person.get(base+"/tasks",params={"scope":"all","limit":500});assert listed.status_code==200,(listed.status_code,listed.text[:1000])
   assert listed.json() and all(row["ware_id"]==ware for row in listed.json())
   assert person.get(base+"/tasks",params={"scope":"unknown"}).status_code==422
   assert person.get(base+"/tasks/999999999").status_code==404
   q.execute("update RUSERS set WARE_ID=9104 where ID=:id",id=actor);c.commit()
   assert person.get(base+"/tasks/1031").status_code==403
   q.execute("update RUSERS set DELETED=1 where ID=:id",id=actor);c.commit()
   assert person.get(base+"/tasks/1031").status_code in(401,403)
 finally:
  q.execute("update RUSERS set WARE_ID=:ware,DELETED=:deleted where ID=:id",ware=ware,deleted=deleted,id=actor)
  if not had_right:q.execute("delete from RIGHTS where USER_GROUP=:grp and RIGHT1='case_pick_view'",grp=group)
  c.commit()
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==stock==(20,20)
 q.execute("select STATUS,PICKED_QTY from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=1031");assert q.fetchone()==("NEW",0)
 print("PASS164 original1031 CASEdetail/admin exact/own listWARE666, foreign403,currentWAREchange403,inactive401or403, scope422/missing404; ownactor/right restored; P20H20/CASE NEW0 unchanged")
