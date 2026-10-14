"""Small real Oracle partial-task/replay fixture; stock restored through count commands."""
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
    base_article = q.fetchone()[0]
    article="QREPL"+tag
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
    metadata("declare r RRL_ARTICULS%rowtype;begin select * into r from RRL_ARTICULS where ACTICUL=:base;r.ACTICUL:=:a;r.BARCODE_SHT:=:bc;r.ABC_GROUP:='A';insert into RRL_ARTICULS values r;end;",base=base_article,a=article,bc="QR"+tag)
    metadata("insert into RRL_STOCK_UOM_CONVERSION(ARTICUL,INPUT_UOM,BASE_UOM,POLICY_VERSION,NUMERATOR,DENOMINATOR,BASE_SCALE,PROVENANCE) select :a,INPUT_UOM,BASE_UOM,POLICY_VERSION,NUMERATOR,DENOMINATOR,BASE_SCALE,'Category B QA' from RRL_STOCK_UOM_CONVERSION where ARTICUL=:base",a=article,base=base_article)
    metadata("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID) select RRL_STOCK_LOCK_API.resource_key('SKU',:a),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",a=article)
    for cell in (src,dst):
        metadata("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM) values(:cell,1,0,0,0,:pick,0)",cell=cell,pick=int(cell==dst))
        metadata("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID) select RRL_STOCK_LOCK_API.resource_key('CELL',:cell),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",cell=cell)
    from decimal import Decimal
    q.execute("select NUMERATOR,DENOMINATOR from RRL_STOCK_UOM_CONVERSION where ARTICUL=:a and INPUT_UOM='BOX' order by POLICY_VERSION desc fetch first 1 row only",a=article)
    num,den=q.fetchone();box_volume=Decimal(str(num))/Decimal(str(den))*Decimal("0.01")
    q.execute("select RRL_PICK_FACE_SQ.nextval from dual");face=int(q.fetchone()[0])
    metadata("insert into RRL_PICK_FACE(PICK_FACE_ID,WARE_ID,CELL_CODE,MAX_VOLUME,CREATED_BY) values(:id,1,:cell,1,'admin')",id=face,cell=dst)
    metadata("insert into RRL_PICK_FACE_ARTICUL(PICK_FACE_ARTICUL_ID,PICK_FACE_ID,ARTICUL,BOX_VOLUME_M3,USE_ARTICUL_REPLENISH_RULE) values(RRL_PICK_FACE_ARTICUL_SQ.nextval,:face,:a,:volume,0)",face=face,a=article,volume=box_volume)
    revision=int(q.callfunc("REVIZION.create_revizion",oracledb.DB_TYPE_NUMBER,[1,"admin"]));connection.commit()
    metadata("insert into RRL_PICK_WAVE(PICK_WAVE_ID,WAVE_CODE,WARE_ID,STATUS,CREATED_BY) values(RRL_PICK_WAVE_SQ.nextval,:code,1,'LAUNCHED','admin')",code=lot)
    q.execute("select PICK_WAVE_ID from RRL_PICK_WAVE where WAVE_CODE=:code",code=lot);wave=int(q.fetchone()[0])
    q.execute("select RRL_PICK_WAVE_REPL_SQ.nextval from dual");repl=int(q.fetchone()[0])
    metadata("insert into RRL_PICK_WAVE_REPLENISH_TASK(PICK_WAVE_REPLENISH_TASK_ID,PICK_WAVE_ID,ARTICUL,QTY,TARGET_CELL_CODE,STATUS,REPLENISHMENT_QTY_MODE) values(:id,:wave,:a,50,:dst,'RELEASED','FILL_TO_VOLUME')",id=repl,wave=wave,a=article,dst=dst)
    try:
        for uid,cell,qty in ((lot,src,"20"),):
            post("INVENTORY_REGISTER_LOT",{"uid":uid,"cell":cell,"article":article,"quantity":qty,"expiry_date":"2030-01-01","price":0,"reason":"NI03.2 partial capacity case"},{"revision_id":revision})
        from app.modules.inventory.infrastructure.wave_commands import reserve_wave_sources
        reserve_wave_sources(OracleGateway(),wave,"admin")
        q.execute("select RESERVE_REQUEST_JSON from RRL_PICK_WAVE_REPLENISH_TASK where PICK_WAVE_REPLENISH_TASK_ID=:id",id=repl)
        assert q.fetchone()[0] is not None
        q.execute("select QTY,DEMAND_BASE_QTY,SOURCE_RESERVATION_ID from RRL_PICK_WAVE_REPLENISH_TASK where PICK_WAVE_REPLENISH_TASK_ID=:id",id=repl)
        actual,demand,reservation=q.fetchone();assert actual==20 and demand==50,(actual,demand)
        from app.modules.resources.public import sync_existing_wave_tasks
        sync_existing_wave_tasks(OracleGateway(),wave,"admin")
        q.execute("select TASK_ID,UID_PALLET,FROM_CELL,TO_CELL from RRL_WAREHOUSE_TASK where TASK_SOURCE='WAVE' and SOURCE_TASK_ID=:id",id=repl)
        task,uid,from_cell,to_cell=q.fetchone()
        post("TASK_COMPLETE",{"fact_qty":"20","scanned_pallet":uid,"scanned_from_cell":from_cell,"scanned_to_cell":to_cell},{"task_id":int(task)})
        q.execute("select sum(REMAIN) from RRL_REMAINS where CELL=:cell",cell=dst);assert q.fetchone()==(20,)
        q.execute("select REMAIN from RRL_REMAINS where UID_POLETA=:lot and CELL=:cell",lot=lot,cell=src);assert q.fetchone()==(0,)
        q.execute("select STATUS,QTY,DEMAND_BASE_QTY from RRL_PICK_WAVE_REPLENISH_TASK where PICK_WAVE_REPLENISH_TASK_ID=:id",id=repl);assert q.fetchone()==("DONE",20,50)
        q.execute("select PICK_WAVE_REPLENISH_TASK_ID,QTY,DEMAND_BASE_QTY,STATUS,SOURCE_RESERVATION_ID from RRL_PICK_WAVE_REPLENISH_TASK where PARENT_REPLENISH_TASK_ID=:id",id=repl)
        child,qty,need,status,res=q.fetchone();assert (qty,need,status,res)==(30,30,"RELEASED",None)
        q.execute("select RESERVE_REQUEST_JSON from RRL_PICK_WAVE_REPLENISH_TASK where PICK_WAVE_REPLENISH_TASK_ID=:id",id=child)
        assert q.fetchone()==(None,), "Child copied its parent immutable wire"
        from app.replenishment_composition import build_replenishment_continuation
        assert build_replenishment_continuation().reconcile(1,"admin")["processed"]==0
        post("INVENTORY_REGISTER_LOT",{"uid":lot+"N","cell":src,"article":article,"quantity":"30","expiry_date":"2030-01-01","price":0,"reason":"Later source for remaining demand"},{"revision_id":revision})
        build_replenishment_continuation().reconcile(1,"admin")
        q.execute("select SOURCE_RESERVATION_ID,QTY from RRL_PICK_WAVE_REPLENISH_TASK where PICK_WAVE_REPLENISH_TASK_ID=:id",id=child)
        child_res,child_qty=q.fetchone();assert child_res is not None and child_qty==30
        assert build_replenishment_continuation().reconcile(1,"admin")["processed"]==0
        q.execute("select TASK_ID,UID_PALLET,FROM_CELL,TO_CELL from RRL_WAREHOUSE_TASK where TASK_SOURCE='WAVE' and SOURCE_TASK_ID=:id",id=child)
        next_task,next_uid,next_from,next_to=q.fetchone()
        op="QA.CONT.COMPLETE:"+tag
        body={"fact_qty":"30","scanned_pallet":next_uid,"scanned_from_cell":next_from,"scanned_to_cell":next_to}
        completed=post("TASK_COMPLETE",body,{"task_id":int(next_task)},operation=op)
        assert post("TASK_COMPLETE",body,{"task_id":int(next_task)},operation=op)==completed
        q.execute("select sum(REMAIN),sum(HARD_RESERVED_BASE) from RRL_REMAINS where CELL=:cell",cell=dst);assert q.fetchone()==(50,0)
        q.execute("select count(*) from RRL_PICK_WAVE_REPLENISH_TASK where PICK_WAVE_ID=:wave",wave=wave);assert q.fetchone()==(2,)
        print("PASS whole pallet20/demand50 -> durable remaining30 -> wait stock -> later source30 -> total50/H0, no duplicate task or replay",flush=True)
    finally:
        q.execute("select RESERVATION_ID from RRL_STOCK_RESERVATION where SOURCE_DOC_TYPE='PICK_WAVE' and SOURCE_DOC_ID=:wave and BASE_QTY>0 and STATUS in('ACTIVE','ALLOCATED','PICKING')",wave=wave)
        for (rid,) in q.fetchall():post("RESERVATION_RELEASE",{"reason":"End bounded partial case"},{"reservation_id":int(rid)})
        q.execute("select r.UID_POLETA,r.CELL,r.BASE_UOM,r.STOCK_VERSION from RRL_REMAINS r join RRL_PALLETS p on p.UID_PALLET=r.UID_POLETA where p.UID_PALLET like :prefix or p.STOCK_ORIGIN_UID like :prefix",prefix=lot+"%")
        counts=[{"uid":uid,"cell":cell,"article":article,"unit":unit,"quantity":"0","expected_stock_version":int(version),"unit_keys":[]} for uid,cell,unit,version in q.fetchall()]
        if counts:post("INVENTORY_COUNT",{"reason":"End bounded partial capacity case","counts":counts},{"revision_id":revision})
        metadata("update RRL_PICK_WAVE set STATUS='CANCELLED' where PICK_WAVE_ID=:id",id=wave)
        print("QA stock restored; immutable history retained",flush=True)
