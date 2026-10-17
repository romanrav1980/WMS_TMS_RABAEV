"""Root-approved pure-read CASE scope admission via native ACCESS owners, all rollback.
No CASE command/StockPosting follows dirty ACCESS writes. No persistent group/config change.
"""
import json
import sys
import time
from contextlib import contextmanager
from datetime import datetime,timedelta,timezone
from pathlib import Path
from typing import Any
import oracledb
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"api/wms_api_server")]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from app.oracle_gateway import OracleGateway
from app.db import oracle_connection
from app.modules.platform.public import AccessMetadataService
from app.modules.platform.api.metadata_inputs import Command,normalize
from app.modules.resources.infrastructure.case_resource_commands import oracle_json
from case_resource_commands_native_smoke import snapshot
FOLDER=ROOT/"reports/retailcase/2026-10-15/case-resource-commands"
PREFIX="CRES15.SCOPE."
GROUP="CRES15.QA.WAREGROUP";DC="CRES15.QA.DC";DCGROUP="CRES15.QA.DCGROUP"


def metadata_snapshot(g:Any)->dict[str,Any]:
    return dict(revision=g.fetch_all("select *from RRL_ACCESS_REV"),
        assignments=g.fetch_all("select *from RRL_ACCESS_ASSIGNMENT where USERNAME='CRES15.OP'order by ASSIGNMENT_ID"),
        objects=g.fetch_all("select *from RRL_ACCESS_OBJECT where (KIND='WAREHOUSE'and OBJECT_ID='13583852')or OBJECT_ID like 'CRES15.QA.%'order by KIND,OBJECT_ID"),
        groups=g.fetch_all("select *from RRL_ACCESS_GROUP where GROUP_ID like 'CRES15.QA.%'order by GROUP_ID"),
        members=g.fetch_all("select *from RRL_ACCESS_GROUP_MEMBER where GROUP_ID like 'CRES15.QA.%'order by GROUP_ID,VERSION_NO,KIND,OBJECT_ID"),
        commands=g.fetch_all("select OPERATION_ID from RRL_PLATFORM_COMMAND where OPERATION_ID like 'CRES15.SCOPE.%'order by OPERATION_ID"),
        audit=g.fetch_all("select OPERATION_ID from RRL_ACCESS_AUDIT where OPERATION_ID like 'CRES15.SCOPE.%'order by OPERATION_ID"))


def main()->None:
    ctx=json.loads((FOLDER/"fixture.json").read_text(encoding="utf-8"));assert ctx["task_id"]==1138 and ctx["actor"]=="CRES15.OP"
    g=OracleGateway();before=snapshot(g,ctx);metadata_before=metadata_snapshot(g)
    assert not metadata_before["commands"]and not metadata_before["groups"]and len(metadata_before["objects"])==1
    original=metadata_before["objects"][0];assert original["kind"]=="WAREHOUSE"and original["object_id"]=="13583852"
    assert all(a["version_no"]==1 and a["revoked_at"]is None for a in metadata_before["assignments"])
    now=datetime.now(timezone.utc);checks=[];receipts=[];began=time.monotonic()
    with oracle_connection()as conn:
        c=conn.cursor()
        class CallerGateway:
            @contextmanager
            def transaction(self,label:Any)->Any:yield c
        owner=AccessMetadataService(CallerGateway());sequence=0
        def command(kind:str,payload:dict[str,Any])->dict[str,Any]:
            nonlocal sequence
            sequence+=1;op=PREFIX+str(sequence)
            result=owner.command("admin",normalize(Command(operation_id=op,command_type=kind,payload=payload),"ACCESS"));receipts.append(dict(operation=op,kind=kind,result=result));return result
        def admission(label:str,allowed:bool)->None:
            c.execute("select RRL_HAS_WRIGHT(:a,'case_pick_execute'),RRL_CASE_TASK_ACCESS.has_current_scoped_execute(:t,:a)from dual",a=ctx["actor"],t=ctx["task_id"])
            flat,current=c.fetchone();assert flat==0 and current==int(allowed),(label,flat,current)
            out=c.var(oracledb.DB_TYPE_CLOB)
            try:
                c.callproc("RRL_CASE_ASSIGNMENT_API.task_context",[ctx["task_id"],ctx["actor"],out]);data=oracle_json(out.getvalue());assert allowed and data["task_id"]==ctx["task_id"]and data["current_actor"]==ctx["actor"],label
            except oracledb.DatabaseError as error:assert not allowed and error.args[0].code==20882,(label,str(error))
            checks.append(dict(case=label,allowed=allowed,native_scope=current))
        def group(group_id:str,kind:str,members:list[dict[str,str]],active:bool,version:int)->None:
            command("GROUP_SAVE",dict(group_id=group_id,title="TEST caller rollback group admission",member_kind=kind,members=members,active=active,expected_version=version))
        def assign(identity:str,scope:str,scope_id:str|None,expired:bool=False)->None:
            command("ASSIGN",dict(assignment_id=identity,username=ctx["actor"],role_id="CRES15.CASE.EXEC",scope_kind=scope,scope_id=scope_id,membership="CURRENT",snapshot_version=None,valid_from=(now-timedelta(hours=2)if expired else now-timedelta(minutes=1)).isoformat(),valid_until=(now-timedelta(hours=1)if expired else now+timedelta(minutes=10)).isoformat(),reason="TEST caller rollback pure-read group/DC/network admission",expected_version=0))
        def object_ware(parent_kind:str|None,parent_id:str|None,version:int)->None:
            command("OBJECT_SAVE",dict(kind="WAREHOUSE",object_id=original["object_id"],title=original["title"],parent_kind=parent_kind,parent_id=parent_id,active=bool(original["active"]),expected_version=version))
        try:
            for existing in metadata_before["assignments"]:command("REVOKE",dict(assignment_id=existing["assignment_id"],reason="TEST scoped admission isolation caller rollback",expected_version=1))
            admission("original WARE and SELF revoked inside caller TX",False)
            group(GROUP,"WAREHOUSE",[dict(kind="WAREHOUSE",object_id="13583852")],True,0)
            assign("CRES15.QA.GROUP.ASSIGN","GROUP",GROUP);admission("CURRENT warehouse group actual CASE warehouse",True)
            group(GROUP,"WAREHOUSE",[],True,1);admission("CURRENT member removal immediately denies",False)
            group(GROUP,"WAREHOUSE",[dict(kind="WAREHOUSE",object_id="13583852")],False,2);admission("inactive warehouse group denies",False)
            group(GROUP,"WAREHOUSE",[dict(kind="WAREHOUSE",object_id="1")],True,3);admission("foreign warehouse group denies",False)
            assign("CRES15.QA.NETWORK.ASSIGN","NETWORK",None);admission("NETWORK current grant allows actual warehouse",True)
            command("REVOKE",dict(assignment_id="CRES15.QA.NETWORK.ASSIGN",reason="TEST caller rollback revoke network",expected_version=1));admission("NETWORK revoke immediately denies",False)
            assign("CRES15.QA.EXPIRED.ASSIGN","NETWORK",None,expired=True);admission("expired NETWORK grant denies",False)
            command("OBJECT_SAVE",dict(kind="DC",object_id=DC,title="TEST temporary DC caller rollback",parent_kind=None,parent_id=None,active=True,expected_version=0))
            object_ware("DC",DC,int(original["version_no"]))
            group(DCGROUP,"DC",[dict(kind="DC",object_id=DC)],True,0)
            assign("CRES15.QA.DCGROUP.ASSIGN","GROUP",DCGROUP);admission("CURRENT DC group includes descendant actual warehouse",True)
            object_ware(original["parent_kind"],original["parent_id"],int(original["version_no"])+1);admission("warehouse removed from DC branch immediately denies",False)
        finally:conn.rollback();c.callproc("RRL_STOCK_LOCK_API.clear_plan")
    duration=time.monotonic()-began
    assert snapshot(g,ctx)==before and metadata_snapshot(g)==metadata_before,"ACL or CASE/source/journal effect escaped rollback"
    report=dict(status="PASS",groups=len(checks),checks=checks,owner_receipts_inside_rolledback_tx=receipts,duration_seconds=round(duration,3),all_rollback=True,case_stock_events_receipts_exact=True,access_revision_assignments_objects_groups_members_command_audit_exact=True,original_warehouse_object=original,quantity_commands=0,metadata_commits=0,limitations="Pure-read CASE task_context/current scoped authorization only. No CLAIM/START/Stock command after dirty ACCESS transaction. Existing10 actual HTTP CLAIM/START cases remain WARE+SELF; GROUP/NETWORK/DC command execution/hardware not claimed.")
    (FOLDER/"group-network-dc-native-scope.json").write_text(json.dumps(report,indent=2,default=str),encoding="utf-8")
    print(json.dumps({"status":"PASS","groups":len(checks),"all_rollback":True,"metadata_commits":0,"duration_seconds":round(duration,3)}))


if __name__=="__main__":main()
