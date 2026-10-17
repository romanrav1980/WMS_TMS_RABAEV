"""Native edits of existing fixture trips are always rolled back with all metadata fixtures."""
import json,secrets,sys
from contextlib import contextmanager
from datetime import datetime,timedelta,timezone,date
from pathlib import Path
from uuid import uuid4
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"api/wms_api_server"),str(ROOT/"scripts")]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from app.db import oracle_connection,rows_as_dicts
from app.modules.platform.public import AccessMetadataService
from app.modules.platform.api.metadata_inputs import Command,normalize
from app.modules.transport.public import update_existing_trip,create_existing_trip,TransportPlanError

class RollbackGateway:
    def __init__(self,cursor): self.cursor=cursor;self.sequence=0
    @contextmanager
    def transaction(self,label):
        self.sequence+=1;point="DS_EDIT_"+str(self.sequence)
        self.cursor.execute("savepoint "+point)
        try: yield self.cursor
        except Exception:
            self.cursor.execute("rollback to savepoint "+point);raise
    def fetch_all(self,sql,params=None):
        self.cursor.execute(sql,params or {});return rows_as_dicts(self.cursor)


def run(gateway):
    access=AccessMetadataService(gateway);prefix="de"+uuid4().hex[:9];actor=prefix+"u";role=prefix+"r"
    now=datetime.now(timezone.utc);checks=[]
    def command(kind,payload):
        return access.command("admin",normalize(Command(operation_id=prefix+":"+uuid4().hex,command_type=kind,payload=payload),"ACCESS"))
    def grant(warehouse):
        command("ASSIGN",dict(assignment_id=prefix+str(warehouse),username=actor,role_id=role,scope_kind="WAREHOUSE",scope_id=str(warehouse),membership="CURRENT",valid_from=(now-timedelta(minutes=1)).isoformat(),valid_until=(now+timedelta(hours=1)).isoformat(),expected_version=0,reason="Rollback-only native edit acceptance"))
    def denied(fn):
        try:fn()
        except TransportPlanError as exc:assert exc.status==403,(exc.status,str(exc))
        else:raise AssertionError("Native foreign edit accepted")
    with gateway.transaction("dispatch.edit.metadata.fixture") as cur:
        cur.execute("insert into RUSERS(ID,NAME,PASS,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:id,'Edit fixture',:password,'NONE',1,0,1)",id=actor,password=secrets.token_urlsafe(24))
    command("ROLE_SAVE",dict(role_id=role,title="Native edit fixture",permissions=["transport_dispatch_edit"],active=True,expected_version=0));grant(9102)
    update_existing_trip(gateway,33641,{"primechanie":prefix},actor)
    assert gateway.fetch_all("select PRIMECHANIE from RRL_TRANSPORT_TASK where ID=33641")[0]["primechanie"]==prefix
    checks.append("native_scoped_note_edit_without_legacy_group")
    denied(lambda:update_existing_trip(gateway,33638,{"primechanie":prefix},actor))
    checks.append("foreign_actual_warehouse_edit_denied")
    grant(9201)
    denied(lambda:update_existing_trip(gateway,31050,{"primechanie":prefix},actor))
    grant(9202);update_existing_trip(gateway,31050,{"primechanie":prefix},actor)
    checks.append("mixed_trip_requires_both_native_edit_grants")
    command("REVOKE",dict(assignment_id=prefix+"9201",expected_version=1,reason="Fixture revoke"))
    denied(lambda:update_existing_trip(gateway,31050,{"primechanie":prefix+"changed"},actor))
    checks.append("revoke_native_edit_denial")
    denied(lambda:create_existing_trip(gateway,"10",date(2030,1,15),actor))
    checks.append("empty_trip_not_created_outside_current_warehouse_mandate")
    grant(1)
    empty=create_existing_trip(gateway,"10",date(2030,1,15),actor)
    update_existing_trip(gateway,empty,{"primechanie":prefix},actor)
    assert gateway.fetch_all("select USER_ID,CONDITION from RRL_TRANSPORT_TASK where ID=:trip",{"trip":empty})[0]=={"user_id":actor,"condition":"Спланирован"}
    other=create_existing_trip(gateway,"10",date(2030,1,15),"admin")
    denied(lambda:update_existing_trip(gateway,other,{"primechanie":prefix},actor))
    checks.extend(["own_warehouse_empty_trip_create_and_edit", "other_author_empty_trip_denied"])
    return checks


def main():
    with oracle_connection() as connection:
        cur=connection.cursor()
        cur.execute("set transaction read only")
        cur.callproc("RRL_TRANSPORT_PLAN_RULES.assert_actor",["admin",9102]);connection.rollback()
        cur.execute("select ID,PRIMECHANIE from RRL_TRANSPORT_TASK where ID in(33641,31050) order by ID");before=cur.fetchall()
        try:checks=run(RollbackGateway(cur))
        finally:connection.rollback()
        cur.execute("select ID,PRIMECHANIE from RRL_TRANSPORT_TASK where ID in(33641,31050) order by ID")
        assert cur.fetchall()==before
    result={"status":"PASS","checks":["pure_actor_check_in_read_only_transaction"]+checks+["business_notes_and_all_fixtures_rolled_back"],"stock_effect":"NONE","fixture_cleaned":True}
    target=ROOT/"reports/retailcase/2026-10-15/dispatch-scope";target.mkdir(parents=True,exist_ok=True)
    (target/"native-edit.json").write_text(json.dumps(result,indent=2),encoding="utf-8");print(json.dumps(result))

if __name__=="__main__":main()
