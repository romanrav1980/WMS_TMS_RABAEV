"""Prepare only until coordinator RELEASE. Native empty CASE cancellation, no goods pick.
Keep immutable metadata receipts/type/SSCC/start history; never reset CASE fields directly.
"""
import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any
import oracledb
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"api/wms_api_server")]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from app.oracle_gateway import OracleGateway
from app.db import oracle_connection
from app.modules.inventory.public import StockCommand,StockPosting
from app.modules.platform.public import stock_configuration_transaction
from app.modules.resources.infrastructure.qualification_admin import QualificationAdmin
from app.services.resource_management_service import ResourceManagementService
from app.schemas import ResourceSessionStatusRequest
from case_resource_commands_fixture import access,NOTE
from case_resource_commands_native_smoke import snapshot
from app.modules.resources.infrastructure.case_resource_commands import oracle_json
FOLDER=ROOT/"reports/retailcase/2026-10-15/case-resource-commands"
REPORT=FOLDER/"cleanup.json"


def save(r:dict[str,Any])->None:REPORT.write_text(json.dumps(r,indent=2,default=str),encoding="utf-8")


def frozen(r:dict[str,Any],name:str,kind:str,source:dict[str,Any],metadata:dict[str,Any])->StockCommand:
    cmd=StockCommand("CRES15.CLEANUP."+name,kind,"admin",(),source,metadata=metadata)
    existing=r.setdefault("commands",{}).get(name)
    if existing is None:r["commands"][name]=cmd.canonical_json();save(r)
    else:
        d=json.loads(existing);cmd=StockCommand(d["operation_id"],d["command_type"],d["actor"],(),d["source"],metadata=d["metadata"]);assert cmd.canonical_json()==existing
        expected=json.loads(StockCommand("CRES15.CLEANUP."+name,kind,"admin",(),source,metadata=metadata).canonical_json())
        retained=json.loads(existing)
        # Only server versions may have advanced after a committed retry. All targets stay frozen.
        for key in ("expected_version","expected_content_version"):
            if key in expected["metadata"]:
                old=retained["metadata"].get(key)
                assert type(old)is int and old>=0,"Invalid retained version"
                expected["metadata"][key]=old
        assert retained==expected,"Stored cleanup intent differs from the exact owned fixture"
    return cmd


def trial(g:Any,ctx:dict[str,Any],cmd:StockCommand,r:dict[str,Any])->None:
    before=snapshot(g,ctx)
    with oracle_connection()as conn:
        c=conn.cursor()
        try:
            out=c.var(oracledb.DB_TYPE_CLOB);c.callproc("RRL_STOCK_POSTING_API.prepare_command",[cmd.canonical_json(),cmd.actor,out])
            if out.getvalue()is None:c.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
            result=oracle_json(out.getvalue());assert result["physical_quantity_changed"]is False and result["status"]=="CANCELLED_EMPTY",result
            c.execute("select STATUS,PICKED_QTY from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:t",t=ctx["task_id"]);assert c.fetchone()==("CANCELLED",0)
            c.execute("select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS where UID_POLETA=:u",u=ctx["source"]);assert c.fetchone()==(23,0)
        finally:conn.rollback();c.callproc("RRL_STOCK_POSTING_API.reset_connection")
    assert snapshot(g,ctx)==before
    assert not g.fetch_all("select OPERATION_ID from RRL_STOCK_OPERATION where OPERATION_ID=:o",{"o":cmd.operation_id})
    assert not g.fetch_all("select OPERATION_ID from RRL_STOCK_OP_CLOCK where OPERATION_ID=:o",{"o":cmd.operation_id})
    assert not g.fetch_all("select IDEMPOTENCY_KEY from RRL_EVENT_OUTBOX where IDEMPOTENCY_KEY=:k",{"k":"STOCK:"+hashlib.sha256(cmd.operation_id.encode()).hexdigest().upper()})
    r["empty_cancel_caller_rollback"]="PASS source/case/events/receipts restored; op/clock/outbox absent";save(r)


def lineage(g:Any,ctx:dict[str,Any])->list[dict[str,Any]]:
    return g.fetch_all("select r.UID_POLETA,r.CELL,r.REMAIN,r.HARD_RESERVED_BASE,r.STOCK_VERSION,p.STOCK_ORIGIN_UID,p.CREATED_BY_STOCK_OP from RRL_REMAINS r join RRL_PALLETS p on p.UID_PALLET=r.UID_POLETA where r.UID_POLETA in(:parent,:child)order by r.UID_POLETA,r.CELL",{"parent":ctx["source"],"child":"CASELOT:E8EAB9A962B9D19BA5AC8FCEE19D8021895BD0:1"})


def verify_lineage(before:list[dict[str,Any]],after:list[dict[str,Any]],ctx:dict[str,Any])->None:
    assert all(row["stock_origin_uid"]=="300000034518661218"for row in before+after)
    child_before=[row for row in before if row["uid_poleta"]!=ctx["source"]]
    child_after=[row for row in after if row["uid_poleta"]!=ctx["source"]]
    assert child_before==child_after and sum(row["remain"]for row in child_after)==1
    assert sum(row["hard_reserved_base"]for row in child_after)==0
    assert all(row["created_by_stock_op"]=="WHREQ15.ASM.PICK1136"for row in child_after)
    assert any(row["cell"]=="QIPcdbf4c0962"and row["remain"]==1 for row in child_after)
    stable=lambda rows:[{k:v for k,v in row.items()if k not in("hard_reserved_base","stock_version")}for row in rows]
    assert stable(before)==stable(after),"Physical quantity, cell or lineage changed during empty cancellation"
    assert sum(row["remain"]for row in after)==24 and sum(row["hard_reserved_base"]for row in after)==0


def execute(g:Any,ctx:dict[str,Any],r:dict[str,Any],empty:StockCommand)->None:
    if "lineage_before"not in r:r["lineage_before"]=lineage(g,ctx);save(r)
    if not g.fetch_all("select OPERATION_ID from RRL_STOCK_OPERATION where OPERATION_ID=:o",{"o":empty.operation_id}):trial(g,ctx,empty,r)
    r["empty_cancel"]=StockPosting().post(empty);assert r["empty_cancel"]["physical_quantity_changed"]is False;save(r)
    for name,kind,source,metadata in [("WAVE","WAVE_CANCEL",{"document_type":"PICK_WAVE","document_id":ctx["wave"]},{"reason":NOTE,"only_cancelled_replenishment":0,"reservation_kind":None}),("PLAN","PICK_PLAN_CANCEL",{"document_type":"PICK_PLAN","document_id":ctx["plan"]},{"reason":NOTE,"only_cancelled_replenishment":0,"reservation_kind":None}),("BOOK","TARE_BOOK_CANCEL",{"booking_operation_id":"CRES15.AK06.TARE.BOOK"},{})]:
        r[name]=StockPosting().post(frozen(r,name,kind,source,metadata));save(r)
    rows=g.fetch_all("select PHYSICAL_QTY,ASSEMBLY_QTY,AVAILABLE_QTY,BALANCE_VERSION from RRL_TARE_AVAILABILITY where OWNER_WARE_ID=:w and PALLET_TYPE_ID=32",{"w":ctx["warehouse_id"]});b=rows[0]
    if "COUNT"not in r["commands"]:assert(b["physical_qty"],b["assembly_qty"],b["available_qty"])==(1,0,1)
    r["COUNT"]=StockPosting().post(frozen(r,"COUNT","TARE_COUNT",{},{"owner_ware_id":ctx["warehouse_id"],"pallet_type_id":32,"condition":"GOOD","observed_quantity":"0","expected_version":int(b["balance_version"]),"reason":NOTE,"decision_reference":"TEST_CRES15_RESTORE0"}));save(r)
    sessions=g.fetch_all("select STATUS from RRL_RESOURCE_SESSION where SESSION_ID=:s",{"s":ctx["session_id"]})
    if sessions[0]["status"]!="CLOSED":ResourceManagementService(g).logout_session(ctx["session_id"],ResourceSessionStatusRequest(updated_by="admin"))
    r["qualification_retired"]=QualificationAdmin(g).set_qualification(ctx["resource_id"],"CASE_PICK",False,"admin");save(r)
    if "role_retired"not in r:
        r["role_retired"]=access(g,"CRES15.ROLE.RETIRE","ROLE_SAVE",dict(role_id="CRES15.CASE.EXEC",title=NOTE,permissions=["case_pick_execute"],active=False,expected_version=3));save(r)
    with stock_configuration_transaction(g,"Retire exact owned CRES15 TEST resource/actor only","admin","warehouse_settings_edit")as c:
        c.execute("update RRL_RESOURCE set ACTIVE=0 where RESOURCE_ID=:r and RESOURCE_CODE='CRES15.CASE'and USER_ID=:a and WARE_ID=:w",r=ctx["resource_id"],a=ctx["actor"],w=ctx["warehouse_id"]);assert c.rowcount==1
        c.execute("update RUSERS set DELETED=1 where ID=:a and USER_GROUP=:a and WARE_ID=:w",a=ctx["actor"],w=ctx["warehouse_id"]);assert c.rowcount==1
    after=snapshot(g,ctx);assert sum(row["remain"]for row in after["stock"])==23 and sum(row["hard_reserved_base"]for row in after["stock"])==0
    assert after["task"][0]["status"]=="CANCELLED"and after["task"][0]["picked_qty"]==0 and str(after["task"][0]["started_at_instant"])==str(r["before"]["task"][0]["started_at_instant"])
    assert not g.fetch_all("select RESERVATION_ID from RRL_STOCK_RESERVATION where SOURCE_DOC_TYPE='PICK_WAVE'and SOURCE_DOC_ID=:w and STATUS in('ACTIVE','ALLOCATED','PICKING')and BASE_QTY>0",{"w":ctx["wave"]})
    assert not g.fetch_all("select PICK_RESERVATION_ID from RRL_PICK_RESERVATION where PICK_PLAN_ID=:p and RESERVATION_STATUS='ACTIVE'",{"p":ctx["plan"]})
    assert g.fetch_all("select STATUS from RRL_RESOURCE_SESSION where SESSION_ID=:s",{"s":ctx["session_id"]})==[{"status":"CLOSED"}]
    assert g.fetch_all("select PHYSICAL_QTY,ASSEMBLY_QTY,AVAILABLE_QTY from RRL_TARE_AVAILABILITY where OWNER_WARE_ID=:w and PALLET_TYPE_ID=32",{"w":ctx["warehouse_id"]})==[{"physical_qty":0,"assembly_qty":0,"available_qty":0}]
    r["lineage_after"]=lineage(g,ctx);verify_lineage(r["lineage_before"],r["lineage_after"],ctx)
    r.update(status="RETIRED_CANONICAL_EMPTY_CANCEL_NO_GOODS_PICK",after=after,retained="TYPE32/SSCC/start/version/shift/order/metadata receipts and ACL history preserved; no direct CASE reset or physical hardware claim",source_parent23_child1_lineage_unchanged=True);save(r)


def main()->None:
    parser=argparse.ArgumentParser();parser.add_argument("--root-release-execute",action="store_true");args=parser.parse_args();g=OracleGateway()
    ctx=json.loads((FOLDER/"fixture.json").read_text(encoding="utf-8"));assert ctx["task_id"]==1138 and ctx["actor"]=="CRES15.OP"
    r=json.loads(REPORT.read_text(encoding="utf-8"))if REPORT.exists()else dict(status="PREPARED_HOLD_FOR_ROOT_UI_RELEASE",before=snapshot(g,ctx),quantity_pick_commands=0,hardware_verified=False)
    task=g.fetch_all("select SSCC,CONTENT_VERSION,PICKED_QTY from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:t",{"t":ctx["task_id"]})[0];assert task["picked_qty"]==0
    empty=frozen(r,"EMPTY","CASE_CARRIER_RETURN",{"case_task_id":ctx["task_id"]},{"allow_empty":True,"destinations":{},"scan_container":task["sscc"],"expected_content_version":task["content_version"],"reason":NOTE})
    if args.root_release_execute:
        assert os.environ.get("CRES15_ROOT_UI_RELEASED")=="1"and os.environ.get("ZERO_OWNER_CLEANUP_WINDOW_RELEASED")=="1","Root UI +ZEROsourcewindow release required"
        execute(g,ctx,r,empty)
    save(r);print(json.dumps({"status":r["status"],"executed":args.root_release_execute}))


if __name__=="__main__":main()
