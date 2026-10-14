"""Existing dynamic assignment reroutes an unstarted CASE wave before physical replenishment; no second planner."""
import json, sys
from pathlib import Path
from uuid import uuid4
import oracledb
from stock_posting_environment import load_local_oracle_environment
ROOT = Path(__file__).resolve().parents[1]
load_local_oracle_environment()
sys.path.insert(0, str(ROOT / "api/wms_api_server"))
from app.config import get_settings
from app.oracle_gateway import OracleGateway
from app.modules.inventory.infrastructure.task_progress import task_progress
from app.services.warehouse_task_service import WarehouseTaskService
from app.services.resource_management_service import ResourceManagementService
from app.schemas import WarehouseTaskStatusRequest, ResourceEquipmentCreateRequest, ResourceCreateRequest, ResourceSessionLoginRequest, ResourceShiftCreateRequest
from fastapi import HTTPException
from datetime import datetime, timedelta
settings = get_settings()
resource_mode = "--resources" in sys.argv
marked_mode = "--marked" in sys.argv
capacity_mode = "--capacity" in sys.argv
tag = uuid4().hex[:10]
lot = "NI032-QA-" + tag
src, dst = "QS" + tag, "QT" + tag
with oracledb.connect(user=settings.oracle_user, password=settings.oracle_password,
                      dsn=settings.oracle_dsn) as connection:
    connection.call_timeout = 15000
    q = connection.cursor()
    q.execute("select user,sys_context('USERENV','SERVICE_NAME') from dual")
    assert q.fetchone() == ("RABAEV", "orcl")
    q.execute("select ARTICUL from RRL_PALLETS where UID_PALLET='DS-BASE-B1'")
    article = q.fetchone()[0]
    def seq(name):
        q.execute("select "+name+".nextval from dual");return int(q.fetchone()[0])
    def metadata(sql, **binds):
        q.callproc("RRL_STOCK_CONFIG_API.begin_change", ["admin", "warehouse_settings_edit"])
        try:
            q.execute(sql, binds); connection.commit()
        except BaseException:
            connection.rollback(); raise
        finally:
            q.callproc("RRL_STOCK_CONFIG_API.end_change")
    def post(kind, body, source, operation=None, actor="admin"):
        if marked_mode and kind=="TASK_COMPLETE":
            from app.modules.inventory.infrastructure.task_completion import complete_existing_task
            return complete_existing_task(OracleGateway(),source["task_id"],
                WarehouseTaskStatusRequest(**body,operation_id=operation,updated_by=actor),actor)
        doc = {"contract_version": 2, "operation_id": operation or "NI032:" + uuid4().hex,
               "command_type": kind, "actor": actor, "source": source, "lines": [],
               "units": [], "metadata": body}
        inp, out = q.var(oracledb.DB_TYPE_CLOB), q.var(oracledb.DB_TYPE_CLOB)
        inp.setvalue(0, json.dumps(doc))
        try:
            q.callproc("RRL_STOCK_POSTING_API.prepare_command", [inp, actor, out, None])
            if out.getvalue() is None:
                q.callproc("RRL_STOCK_POSTING_API.execute_prepared", [out])
            result = out.getvalue()
            result = json.loads(result.read() if hasattr(result, "read") else result)
            connection.commit(); return result
        except BaseException:
            connection.rollback(); raise
        finally:
            q.callproc("RRL_STOCK_POSTING_API.reset_connection")
    for cell in (src,dst):
        metadata("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM) values(:cell,1,0,0,0,0,0)",cell=cell)
        metadata("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID) select RRL_STOCK_LOCK_API.resource_key('CELL',:cell),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",cell=cell)
    from decimal import Decimal
    q.execute("select NUMERATOR,DENOMINATOR from RRL_STOCK_UOM_CONVERSION where ARTICUL=:a and INPUT_UOM='BOX' order by POLICY_VERSION desc fetch first 1 row only",a=article)
    num,den=q.fetchone();box_volume=Decimal(str(num))/Decimal(str(den))*Decimal("0.01")
    q.execute("select RRL_PICK_FACE_SQ.nextval from dual");face=int(q.fetchone()[0])
    metadata("insert into RRL_PICK_FACE(PICK_FACE_ID,WARE_ID,CELL_CODE,MAX_VOLUME,CREATED_BY) values(:id,1,:cell,0.02,'admin')",id=face,cell=dst)
    metadata("insert into RRL_PICK_FACE_ARTICUL(PICK_FACE_ARTICUL_ID,PICK_FACE_ID,ARTICUL,BOX_VOLUME_M3,USE_ARTICUL_REPLENISH_RULE) values(RRL_PICK_FACE_ARTICUL_SQ.nextval,:face,:a,:volume,0)",face=face,a=article,volume=box_volume)
    revision=int(q.callfunc("REVIZION.create_revizion",oracledb.DB_TYPE_NUMBER,[1,"admin"]));connection.commit()
    metadata("insert into RRL_PICK_WAVE(PICK_WAVE_ID,WAVE_CODE,WARE_ID,STATUS,CREATED_BY) values(RRL_PICK_WAVE_SQ.nextval,:code,1,'LAUNCHED','admin')",code=lot)
    q.execute("select PICK_WAVE_ID from RRL_PICK_WAVE where WAVE_CODE=:code",code=lot);wave=int(q.fetchone()[0])
    q.execute("select RRL_PICK_WAVE_REPL_SQ.nextval from dual");repl=int(q.fetchone()[0])
    metadata("insert into RRL_PICK_WAVE_REPLENISH_TASK(PICK_WAVE_REPLENISH_TASK_ID,PICK_WAVE_ID,ARTICUL,QTY,TARGET_CELL_CODE,STATUS,REPLENISHMENT_QTY_MODE) values(:id,:wave,:a,3,:dst,'RELEASED','FILL_TO_VOLUME')",id=repl,wave=wave,a=article,dst=dst)
    carrier=lot+"C"
    q.execute("select min(CUSTOMER_ID) from RRL_CUSTOMER");customer=q.fetchone()[0]
    order,row,plan,pl,pt,unused_wave,wt,ct,cl=[seq(n) for n in ("RRL_CUSTOMER_ORDER_SQ","RRL_CUSTOMER_ORDER_ROW_SQ","RRL_PICK_PLAN_SQ","RRL_PICK_PLAN_LINE_SQ","RRL_PICK_TASK_SQ","RRL_PICK_WAVE_SQ","RRL_PICK_WAVE_TASK_SQ","RRL_CASE_PICK_TASK_SQ","RRL_CASE_PICK_LINE_SQ")]
    metadata("insert into RRL_CUSTOMER_ORDER(CUSTOMER_ORDER_ID,ORDER_NO,CUSTOMER_ID,WARE_ID) values(:id,:no,:customer,1)",id=order,no=carrier,customer=customer)
    metadata("insert into RRL_CUSTOMER_ORDER_ROW(CUSTOMER_ORDER_ROW_ID,CUSTOMER_ORDER_ID,LINE_NO,ARTICUL,ORDER_QTY) values(:id,:o,1,:a,3)",id=row,o=order,a=article)
    metadata("insert into RRL_PICK_PLAN(PICK_PLAN_ID,CUSTOMER_ORDER_ID,CUSTOMER_ID,WARE_ID,STATUS,TOTAL_ORDER_QTY,TOTAL_PLANNED_QTY) values(:id,:o,:customer,1,'RELEASED',3,3)",id=plan,o=order,customer=customer)
    metadata("insert into RRL_PICK_PLAN_LINE(PICK_PLAN_LINE_ID,PICK_PLAN_ID,CUSTOMER_ORDER_ROW_ID,ARTICUL,REQUESTED_QTY,PLANNED_QTY,CASE_PICK_QTY,STATUS) values(:id,:p,:r,:a,3,3,3,'PLANNED_FULL')",id=pl,p=plan,r=row,a=article)
    metadata("insert into RRL_PICK_TASK(PICK_TASK_ID,PICK_PLAN_ID,PICK_PLAN_LINE_ID,CUSTOMER_ORDER_ID,CUSTOMER_ID,TASK_TYPE,STATUS,ARTICUL,SOURCE_CELL_CODE,QTY,PICK_SEQUENCE) values(:id,:p,:pl,:o,:customer,'CASE_PICK','IN_PROGRESS',:a,:c,3,1)",id=pt,p=plan,pl=pl,o=order,customer=customer,a=article,c=dst)
    metadata("insert into RRL_PICK_WAVE_TASK(PICK_WAVE_TASK_ID,PICK_WAVE_ID,PICK_TASK_ID,TASK_TYPE,STATUS,ARTICUL,QTY,SOURCE_CELL_CODE) values(:id,:w,:p,'CASE_PICK','IN_PROGRESS',:a,3,:c)",id=wt,w=wave,p=pt,a=article,c=dst)
    metadata("insert into RRL_CASE_PICK_TASK(CASE_PICK_TASK_ID,PICK_WAVE_ID,PICK_PLAN_ID,CUSTOMER_ORDER_ID,CUSTOMER_ID,SSCC,STATUS,WARE_ID,TOTAL_LINES,PLANNED_QTY,ASSIGNED_TO,CREATED_BY) values(:id,:w,:p,:o,:customer,:carrier,'IN_PROGRESS',1,1,3,'admin','admin')",id=ct,w=wave,p=plan,o=order,customer=customer,carrier=carrier)
    metadata("insert into RRL_CASE_PICK_LINE(CASE_PICK_LINE_ID,CASE_PICK_TASK_ID,PICK_WAVE_ID,PICK_WAVE_TASK_ID,PICK_TASK_ID,PICK_PLAN_LINE_ID,CUSTOMER_ORDER_ID,CUSTOMER_ID,ARTICUL,CELL_CODE,PICK_FACE_ID,PICK_SEQUENCE,PLANNED_QTY,STATUS,CREATED_BY) values(:id,:ct,:w,:wt,:pt,:pl,:o,:customer,:a,:c,:f,1,3,'ACTIVE','admin')",id=cl,ct=ct,w=wave,wt=wt,pt=pt,pl=pl,o=order,customer=customer,a=article,c=dst,f=face)

    alt="QA"+tag
    metadata("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM) values(:cell,1,0,0,0,1,0)",cell=alt)
    metadata("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID) select RRL_STOCK_LOCK_API.resource_key('CELL',:cell),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",cell=alt)
    route=seq("RRL_PICK_ROUTE_SQ");altface=seq("RRL_PICK_FACE_SQ");routecell=seq("RRL_PICK_ROUTE_CELL_SQ")
    metadata("insert into RRL_PICK_ROUTE(PICK_ROUTE_ID,ROUTE_CODE,ROUTE_NAME,WARE_ID) values(:id,:code,'Own alternative face route',1)",id=route,code="ALT"+tag)
    metadata("insert into RRL_PICK_FACE(PICK_FACE_ID,WARE_ID,CELL_CODE,MAX_VOLUME,PICK_FACE_TYPE,PICK_SEQUENCE,CREATED_BY) values(:id,1,:cell,0.03,'DYNAMIC',1,'admin')",id=altface,cell=alt)
    metadata("insert into RRL_PICK_ROUTE_CELL(PICK_ROUTE_CELL_ID,PICK_ROUTE_ID,WARE_ID,CELL_CODE,PICK_SEQUENCE) values(:id,:r,1,:cell,1)",id=routecell,r=route,cell=alt)
    metadata("update RRL_PICK_WAVE set ROUTE_ID=:r where PICK_WAVE_ID=:w",r=route,w=wave)
    try:
        for uid,cell,qty in ((lot,src,"3"),):
            post("INVENTORY_REGISTER_LOT",{"uid":uid,"cell":cell,"article":article,"quantity":qty,"expiry_date":"2030-01-01","price":0,"reason":"NI03.2 partial capacity case"},{"revision_id":revision})

        from app.modules.inventory.infrastructure.wave_pick_release import WavePickRelease
        admission=WavePickRelease(OracleGateway())
        before=admission.preview(wave)
        assert before["ready"] is False and before["tasks"][0]["missing_base"]=="3"
        def denied():
            try:
                post("WAVE_PICK_RELEASE",{},{"wave_id":wave})
                raise AssertionError("Incomplete replenishment or uncovered pick permitted release")
            except oracledb.DatabaseError as exc:
                assert "WAVE_PICK_COVERAGE_OR_REPLENISHMENT_PENDING" in str(exc),str(exc)
        denied()

        from app.modules.inventory.infrastructure.alternative_pick_faces import AlternativePickFaces
        from app.modules.inventory.infrastructure.wave_commands import reserve_wave_sources
        old_dst=dst
        assert AlternativePickFaces(OracleGateway()).route_wave(wave,"admin")==1
        assert AlternativePickFaces(OracleGateway()).route_wave(wave,"admin")==0
        q.execute("select count(*) from RRL_CASE_PICK_EVENT where CASE_PICK_TASK_ID=:ct and EVENT_TYPE='FACE_TARGET_REROUTED'",ct=ct)
        assert q.fetchone()==(1,)
        dst=alt
        q.execute("select CELL_CODE,PICK_FACE_ID,PICK_ROUTE_CELL_ID from RRL_CASE_PICK_LINE where CASE_PICK_LINE_ID=:id",id=cl)
        assert q.fetchone()==(alt,altface,routecell)
        q.execute("select UNIT_VOLUME_M3,BASE_UOM from RRL_PICK_FACE_ASSIGNMENT where PICK_WAVE_ID=:w and STATUS='ACTIVE'",w=wave)
        assigned_volume,assigned_base=q.fetchone();assert Decimal(str(assigned_volume))==Decimal("0.01") and assigned_base=="EA",(assigned_volume,assigned_base)
        reserve_wave_sources(OracleGateway(),wave,"admin")
        reserve_wave_sources(OracleGateway(),wave,"admin")
        q.execute("select RESERVE_OPERATION_ID,RESERVE_REQUEST_JSON from RRL_PICK_WAVE_REPLENISH_TASK where PICK_WAVE_REPLENISH_TASK_ID=:id",id=repl)
        intent,wire=q.fetchone();wire=json.loads(wire.read() if hasattr(wire,"read") else wire)
        assert wire["operation_id"]==intent and wire["metadata"]["requested_row_ids"]==[repl]
        q.execute("select count(*) from RRL_STOCK_OPERATION where OPERATION_ID=:op and STATE='APPLIED'",op=intent)
        assert q.fetchone()==(1,)
        q.execute("select QTY,DEMAND_BASE_QTY,SOURCE_RESERVATION_ID from RRL_PICK_WAVE_REPLENISH_TASK where PICK_WAVE_REPLENISH_TASK_ID=:id",id=repl)
        actual,demand,reservation=q.fetchone();assert actual==3 and demand==3,(actual,demand)
        from app.modules.resources.public import sync_existing_wave_tasks
        sync_existing_wave_tasks(OracleGateway(),wave,"admin")
        q.execute("select TASK_ID,UID_PALLET,FROM_CELL,TO_CELL from RRL_WAREHOUSE_TASK where TASK_SOURCE='WAVE' and SOURCE_TASK_ID=:id",id=repl)
        task,uid,from_cell,to_cell=q.fetchone()

        preparing=admission.preview(wave)
        assert preparing["ready"] is False and preparing["open_replenishments"][0]["warehouse_task_id"]==task
        denied()
        completion_id="GENERIC.QA.COMPLETE:"+tag
        complete_body={"fact_qty":"3","scanned_pallet":uid,"scanned_from_cell":from_cell,"scanned_to_cell":to_cell}
        completed=post("TASK_COMPLETE",complete_body,{"task_id":int(task)},completion_id)
        assert post("TASK_COMPLETE",complete_body,{"task_id":int(task)},completion_id)==completed
        q.execute("select sum(BASE_QTY) from RRL_STOCK_RESERVATION where SOURCE_DOC_TYPE='PICK_WAVE' and SOURCE_DOC_ID=:w and SOURCE_LINE_ID=:p and RESERVATION_DOMAIN='PICKING' and STATUS='ACTIVE'",w=wave,p=pt);assert q.fetchone()==(3,)
        q.execute("select sum(HARD_RESERVED_BASE) from RRL_REMAINS where CELL=:cell",cell=dst);assert q.fetchone()==(3,)
        # original invocation replaced
        #post("TASK_COMPLETE",{"fact_qty":"1","scanned_pallet":uid,"scanned_from_cell":from_cell,"scanned_to_cell":to_cell},{"task_id":int(task)})
        q.execute("select sum(REMAIN) from RRL_REMAINS where CELL=:cell",cell=dst);assert q.fetchone()==(3,)
        q.execute("select REMAIN from RRL_REMAINS where UID_POLETA=:lot and CELL=:cell",lot=lot,cell=src);assert q.fetchone()==(0,)
        q.execute("select STATUS,QTY,DEMAND_BASE_QTY from RRL_PICK_WAVE_REPLENISH_TASK where PICK_WAVE_REPLENISH_TASK_ID=:id",id=repl);assert q.fetchone()==("DONE",3,3)

        ready=admission.preview(wave)
        assert ready["ready"] is True and ready["tasks"][0]["covered_base"]=="3",ready
        op="GATE.RELEASE:"+tag
        released=post("WAVE_PICK_RELEASE",{},{"wave_id":wave},op)
        assert released["released_at"] is not None
        assert post("WAVE_PICK_RELEASE",{},{"wave_id":wave},op)==released
        q.execute("select count(*) from RRL_STOCK_OPERATION where OPERATION_ID=:op and STATE='APPLIED'",op=op)
        assert q.fetchone()==(1,)
        print("PASS primary capacity2/demand3 -> existing dynamic empty cell capacity3 + CASE route/BASE volume; durable source intent once; physical arrival3 -> owned dynamic eligibility -> explicit release/replay",flush=True)

    finally:
        q.execute("select RESERVATION_ID from RRL_STOCK_RESERVATION where SOURCE_DOC_TYPE='PICK_WAVE' and SOURCE_DOC_ID=:wave and BASE_QTY>0 and STATUS in('ACTIVE','ALLOCATED','PICKING')",wave=wave)
        for (rid,) in q.fetchall():post("RESERVATION_RELEASE",{"reason":"End bounded partial case"},{"reservation_id":int(rid)})
        q.execute("select r.UID_POLETA,r.CELL,r.BASE_UOM,r.STOCK_VERSION from RRL_REMAINS r join RRL_PALLETS p on p.UID_PALLET=r.UID_POLETA where p.UID_PALLET like :prefix or p.STOCK_ORIGIN_UID like :prefix",prefix=lot+"%")
        counts=[{"uid":uid,"cell":cell,"article":article,"unit":unit,"quantity":"0","expected_stock_version":int(version),"unit_keys":[]} for uid,cell,unit,version in q.fetchall()]
        if counts:post("INVENTORY_COUNT",{"reason":"End bounded partial capacity case","counts":counts},{"revision_id":revision})
        metadata("update RRL_PICK_WAVE_REPLENISH_TASK set STATUS='CANCELLED' where PICK_WAVE_ID=:id and STATUS not in('DONE','CANCELLED')",id=wave)
        metadata("update RRL_PICK_WAVE set STATUS='CANCELLED' where PICK_WAVE_ID=:id",id=wave)
        print("QA stock restored; immutable history retained",flush=True)
