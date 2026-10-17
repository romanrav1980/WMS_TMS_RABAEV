"""Resource session warehouse/owner filtering happens before the row limit."""
import json,secrets,sys
from datetime import datetime,timedelta,timezone
from pathlib import Path
from uuid import uuid4
import httpx
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"api/wms_api_server"),str(ROOT/"scripts")]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from app.oracle_gateway import OracleGateway
from app.modules.platform.public import AccessMetadataService
from app.modules.platform.api.metadata_inputs import Command,normalize


def main():
 g=OracleGateway();access=AccessMetadataService(g);prefix="rs"+uuid4().hex[:9];actor=prefix+"u";role=prefix+"r";assignment=prefix+"a";password=secrets.token_urlsafe(24);now=datetime.now(timezone.utc);checks=[]
 def command(kind,payload):return access.command("admin",normalize(Command(operation_id=prefix+":"+uuid4().hex,command_type=kind,payload=payload),"ACCESS"))
 try:
  with g.transaction("session.scope.fixture")as cur:
   cur.execute("insert into RUSERS(ID,NAME,PASS,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:id,'Session fixture',:password,'NONE',2,0,1)",id=actor,password=password)
  command("ROLE_SAVE",dict(role_id=role,title="Scoped session reader",permissions=["resource_session_view"],active=True,expected_version=0))
  command("ASSIGN",dict(assignment_id=assignment,username=actor,role_id=role,scope_kind="WAREHOUSE",scope_id="1",membership="CURRENT",valid_from=(now-timedelta(minutes=1)).isoformat(),valid_until=(now+timedelta(hours=1)).isoformat(),expected_version=0,reason="Isolated resource session read acceptance"))
  with httpx.Client(base_url="http://127.0.0.1:8088",auth=(actor,password),timeout=30)as c:
   r=c.get("/api/resources/sessions?ware_id=1&limit=500");assert r.status_code==200,r.text[:300]
   rows=r.json();assert rows and all(row["ware_id"]==1 for row in rows)
   checks.append("native_only_session_view_actual_warehouse")
   r=c.get("/api/resources/sessions?limit=1");assert r.status_code==200,r.text[:300]
   assert len(r.json())==1 and r.json()[0]["ware_id"]==1
   checks.append("scope_filter_before_top_one")
   assert c.get("/api/resources/sessions?ware_id=51365792").status_code==403
   assert c.get("/api/resources/sessions?session_id=40").json()==[]
   checks.append("foreign_explicit_warehouse_and_session_hidden")
   command("REVOKE",dict(assignment_id=assignment,expected_version=1,reason="Revoke fixture"))
   assert c.get("/api/resources/sessions?ware_id=1").status_code==403
   checks.append("native_revoke_immediate")
 finally:
  with g.transaction("session.scope.cleanup")as cur:
   cur.execute("delete from RRL_ACCESS_ASSIGNMENT where USERNAME=:actor",actor=actor)
   for table in ("RRL_ACCESS_ROLE_RIGHT","RRL_ACCESS_ROLE"):cur.execute("delete from "+table+" where ROLE_ID=:role",role=role)
   cur.execute("delete from RRL_ACCESS_AUDIT where OPERATION_ID like :prefix",prefix=prefix+":%")
   cur.execute("delete from RRL_PLATFORM_COMMAND where OPERATION_ID like :prefix",prefix=prefix+":%")
   cur.execute("delete from RUSERS where ID=:actor",actor=actor)
 result={"status":"PASS","checks":checks,"fixture_cleaned":True,"business_data":"READ_ONLY","stock_effect":"NONE"}
 target=ROOT/"reports/retailcase/2026-10-15/resource-timeline";target.mkdir(parents=True,exist_ok=True)
 (target/"sessions-native.json").write_text(json.dumps(result,indent=2),encoding="utf-8");print(json.dumps(result))

if __name__=="__main__":main()
