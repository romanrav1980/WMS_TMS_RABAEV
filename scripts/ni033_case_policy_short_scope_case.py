"""166 existing unmarked1031/foreign line/short histories; no stock or CASE changes."""
import sys
from pathlib import Path
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();actor="Q1341a19738325";base="http://127.0.0.1:8088/api/case-pick"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select PASS,USER_GROUP,WARE_ID,DELETED from RUSERS where ID=:id",id=actor);secret,group,ware,deleted=q.fetchone()
 q.execute("select count(*)from RIGHTS where USER_GROUP=:grp and lower(trim(RIGHT1))='case_pick_view'",grp=group);had=q.fetchone()[0]
 q.execute("select min(CASE_PICK_LINE_ID)from RRL_CASE_PICK_LINE where CASE_PICK_TASK_ID=1031");line=q.fetchone()[0]
 q.execute("""select ct.CASE_PICK_TASK_ID,l.CASE_PICK_LINE_ID from RRL_CASE_PICK_TASK ct join RRL_CASE_PICK_LINE l on l.CASE_PICK_TASK_ID=ct.CASE_PICK_TASK_ID
  where ct.WARE_ID!=:ware and ct.WARE_ID is not null order by ct.CASE_PICK_TASK_ID fetch first 1 rows only""",ware=ware);foreign,foreignline=q.fetchone()
 q.execute("select count(*)from RRL_CASE_PICK_SHORT s join RRL_CASE_PICK_TASK t on t.CASE_PICK_TASK_ID=s.CASE_PICK_TASK_ID where t.WARE_ID!=:ware",ware=ware);other_shorts=q.fetchone()[0]
 if not had:q.execute("insert into RIGHTS(USER_GROUP,RIGHT1)values(:grp,'case_pick_view')",grp=group);c.commit()
 try:
  with httpx.Client(auth=(actor,secret),timeout=30)as person,httpx.Client(auth=("admin","admin123"),timeout=30)as admin:
   path=base+f"/tasks/1031/lines/{line}/marking-policy"
   own=person.get(path);assert own.status_code==200,(own.status_code,own.text[:1300])
   assert own.json()==admin.get(path).json() and own.json()["marking_required"]is False
   denied=person.get(base+f"/tasks/{foreign}/lines/{foreignline}/marking-policy")
   assert denied.status_code==403,(denied.status_code,denied.text[:1300])
   missing=person.get(base+"/tasks/1031/lines/999999999/marking-policy");assert missing.status_code==404
   shorts=person.get(base+"/shorts",params={"limit":500});assert shorts.status_code==200,(shorts.status_code,shorts.text[:1300])
   for row in shorts.json():
    q.execute("select WARE_ID from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:id",id=row["case_pick_task_id"]);assert q.fetchone()[0]==ware
   assert person.get(base+"/shorts",params={"limit":501}).status_code==422
   q.execute("update RUSERS set WARE_ID=9104 where ID=:id",id=actor);c.commit()
   assert person.get(path).status_code==403
 finally:
  q.execute("update RUSERS set WARE_ID=:ware,DELETED=:deleted where ID=:id",ware=ware,deleted=deleted,id=actor)
  if not had:q.execute("delete from RIGHTS where USER_GROUP=:grp and RIGHT1='case_pick_view'",grp=group)
  c.commit()
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
 print("PASS166 own1031 marking card exact/unmarked/foreign403/line404/currentWARE403; shortages currentWARE-only/limit501422; foreignshorts present",other_shorts,"ownrights restored/no stock")
