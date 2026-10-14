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
finish_shift_mode = "--finish-shift" in sys.argv
resource_mode = "--resources" in sys.argv or finish_shift_mode
marked_mode = "--marked" in sys.argv
capacity_mode = "--capacity" in sys.argv
urgent_mode = "--urgent" in sys.argv
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
    if marked_mode:
        article="QM"+tag
        gtin_prefix="0460000000000"
        gtin=gtin_prefix+str((10-sum(int(n)*(3 if i%2==0 else 1) for i,n in enumerate(reversed(gtin_prefix)))%10)%10)
        metadata("declare r RRL_ARTICULS%rowtype;begin select * into r from RRL_ARTICULS where ACTICUL='DS-BASE-D10';r.ACTICUL:=:a;r.BARCODE_SHT:=:gtin;insert into RRL_ARTICULS values r;end;",a=article,gtin=gtin)
        metadata("insert into RRL_STOCK_UOM_CONVERSION(ARTICUL,INPUT_UOM,BASE_UOM,POLICY_VERSION,NUMERATOR,DENOMINATOR,BASE_SCALE,PROVENANCE) select :a,INPUT_UOM,BASE_UOM,POLICY_VERSION,NUMERATOR,DENOMINATOR,BASE_SCALE,'NI03.2 marked QA' from RRL_STOCK_UOM_CONVERSION where ARTICUL='DS-BASE-D10'",a=article)
        metadata("insert into RRL_SKU_RECEIPT_POLICY(ARTICUL,POLICY_VERSION,MARKING_REQUIRED,UPDATED_BY) values(:a,1,1,'admin')",a=article)
        for system,profile in (("CRPT","TOBACCO"),("EGAIS","ALCOHOL")):
            metadata("insert into RRL_SKU_RECEIPT_PROFILE(ARTICUL,SYSTEM_CODE,PROFILE_CODE,PROFILE_VERSION,SCAN_MODE) values(:a,:s,:p,'QA1','UNIT')",a=article,s=system,p=profile)
        metadata("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID) select RRL_STOCK_LOCK_API.resource_key('SKU',:a),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",a=article)
    for cell in (src, dst):
        metadata("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM) values(:cell,1,0,0,0,0,0)", cell=cell)
        metadata("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID) select RRL_STOCK_LOCK_API.resource_key('CELL',:cell),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD", cell=cell)
    revision = int(q.callfunc("REVIZION.create_revizion", oracledb.DB_TYPE_NUMBER, [1, "admin"]))
    connection.commit()
    metadata("insert into RRL_PICK_WAVE(PICK_WAVE_ID,WAVE_CODE,WARE_ID,STATUS,CREATED_BY) values(RRL_PICK_WAVE_SQ.nextval,:code,1,'LAUNCHED','admin')", code=lot)
    q.execute("select PICK_WAVE_ID from RRL_PICK_WAVE where WAVE_CODE=:code", code=lot)
    wave = int(q.fetchone()[0])
    q.execute("select RRL_PICK_WAVE_REPL_SQ.nextval from dual")
    replenishment = int(q.fetchone()[0])
    metadata("insert into RRL_PICK_WAVE_REPLENISH_TASK(PICK_WAVE_REPLENISH_TASK_ID,PICK_WAVE_ID,ARTICUL,QTY,SOURCE_CELL_CODE,TARGET_CELL_CODE,STATUS) values(:id,:wave,:article,3,:src,:dst,'IN_PROGRESS')", id=replenishment, wave=wave, article=article, src=src, dst=dst)
    q.execute("select RRL_WAREHOUSE_TASK_SQ.nextval from dual")
    task = int(q.fetchone()[0])
    metadata("insert into RRL_WAREHOUSE_TASK(TASK_ID,TASK_TYPE,TASK_SOURCE,SOURCE_TASK_ID,SOURCE_DOC_TYPE,SOURCE_DOC_ID,UID_PALLET,FROM_CELL,TO_CELL,FROM_WARE_ID,TO_WARE_ID,QTY,UNIT_CODE,QTY_MODE,STATUS,CREATED_BY,PLANNED_START_AT,PLANNED_FINISH_AT) values(:id,'REPLENISHMENT','WAVE',:repl,'PICK_WAVE',:wave,:lot,:src,:dst,1,1,3,'EA','BOX','IN_PROGRESS','admin',systimestamp,systimestamp)", id=task,repl=replenishment,wave=wave,lot=lot,src=src,dst=dst)
    owner = "admin"; session = None; request_resources = {}
    passed=False
    try:
        birth={"uid":lot,"cell":src,"article":article,"quantity":"3","expiry_date":"2030-01-01","price":0,"reason":"NI03.2 isolated task fixture"}
        if marked_mode:
            from app.modules.inventory.infrastructure.stock_posting_uow import StockPosting
            from app.modules.inventory.contracts_stock import StockCommand
            codes=[{"unit_id":str(i),"codes":[{"system_code":"CRPT","profile_code":"TOBACCO","code":gtin+tag[:5]+str(i).zfill(2)},
                    {"system_code":"EGAIS","profile_code":"ALCOHOL","code":("QA"+tag+str(i)).ljust(68,"X")}]} for i in range(3)]
            birth["birth_captures"]={lot:{"units":codes,"aggregations":[]}}
            StockPosting().post(StockCommand(operation_id="NI032.MARK.BIRTH:"+tag,command_type="INVENTORY_REGISTER_LOT",actor="admin",lines=(),source={"revision_id":revision},metadata=birth))
        else:
            post("INVENTORY_REGISTER_LOT",birth,{"revision_id":revision})
        created=post("RESERVATION_CREATE",{"uid_pallet":lot,"cell":src,"articul":article,"qty":"3","unit_code":"EA","ware_id":1,
            "reservation_kind":"HARD","reservation_scope":"QTY","reservation_domain":"WAVE","source_doc_type":"PICK_WAVE",
            "source_doc_id":wave,"source_line_id":replenishment},{"type":"PICK_WAVE","id":wave})
        metadata("update RRL_PICK_WAVE_REPLENISH_TASK set SOURCE_RESERVATION_ID=:rid,PALLET_UID=:lot,SOURCE_CELL_CODE=:src where PICK_WAVE_REPLENISH_TASK_ID=:id",
            rid=created["reservation_id"],lot=lot,src=src,id=replenishment)
        if capacity_mode:
            from decimal import Decimal
            q.execute("select NUMERATOR,DENOMINATOR from RRL_STOCK_UOM_CONVERSION where ARTICUL=:a and INPUT_UOM='BOX' order by POLICY_VERSION desc fetch first 1 row only",a=article)
            num,den=q.fetchone();box_volume=Decimal(str(num))/Decimal(str(den))*Decimal("0.01")
            q.execute("select RRL_PICK_FACE_SQ.nextval from dual");face=int(q.fetchone()[0])
            metadata("insert into RRL_PICK_FACE(PICK_FACE_ID,WARE_ID,CELL_CODE,MAX_VOLUME,CREATED_BY) values(:id,1,:cell,0.02,'admin')",id=face,cell=dst)
            metadata("insert into RRL_PICK_FACE_ARTICUL(PICK_FACE_ARTICUL_ID,PICK_FACE_ID,ARTICUL,BOX_VOLUME_M3,USE_ARTICUL_REPLENISH_RULE) values(RRL_PICK_FACE_ARTICUL_SQ.nextval,:face,:a,:volume,0)",face=face,a=article,volume=box_volume)
            other_lot=lot+"-R"
            post("INVENTORY_REGISTER_LOT",{"uid":other_lot,"cell":src,"article":article,"quantity":"1","expiry_date":"2030-01-01","price":0,"reason":"Independent scheduled arrival"},{"revision_id":revision})
            reserved=post("RESERVATION_CREATE",{"uid_pallet":other_lot,"cell":src,"articul":article,"qty":"1","unit_code":"EA","ware_id":1,"reservation_kind":"HARD","reservation_scope":"QTY","reservation_domain":"WAVE","source_doc_type":"PICK_WAVE","source_doc_id":wave},{"type":"PICK_WAVE","id":wave})
            reservation_id=reserved["reservation_id"]
            metadata("insert into RRL_PICK_WAVE_REPLENISH_TASK(PICK_WAVE_REPLENISH_TASK_ID,PICK_WAVE_ID,ARTICUL,QTY,SOURCE_CELL_CODE,TARGET_CELL_CODE,PALLET_UID,SOURCE_RESERVATION_ID,STATUS) values(RRL_PICK_WAVE_REPL_SQ.nextval,:wave,:a,1,:src,:dst,:lot,:rid,'RELEASED')",wave=wave,a=article,src=src,dst=dst,lot=other_lot,rid=reservation_id)
            q.execute("select RRL_STOCK_REPL_CAPACITY.remaining_base_quantity(:cell,:article,:repl) from dual",cell=dst,article=article,repl=replenishment)
            assert q.fetchone()==(1,),"Open arrival not deducted in canonical base quantity"
        urgent_deadline=None
        if urgent_mode:
            metadata("update RRL_WAREHOUSE_TASK set PRIORITY=0,PLANNED_FINISH_AT=systimestamp+numtodsinterval(300,'SECOND') where TASK_ID=:id",id=task)
            q.execute("select PLANNED_FINISH_AT from RRL_WAREHOUSE_TASK where TASK_ID=:id",id=task);urgent_deadline=q.fetchone()[0]
        body = {"fact_qty": "1", "scanned_pallet": lot, "scanned_from_cell": src,
                "scanned_to_cell": dst}
        if resource_mode:
            owner, other, group = "QTA" + tag, "QTB" + tag, "QTG" + tag
            metadata("insert into USER_GROUP(ID,NAME) values(:id,'NI03.2 bounded role fixture')", id=group)
            for user in (owner, other):
                metadata("insert into RUSERS(ID,NAME,PASS,USER_GROUP,DELETED) values(:id,'NI03.2 QA','qa-test-only',:g,0)", id=user,g=group)
            for right in ("warehouse_task_execute", "warehouse_task_view"):
                metadata("insert into RIGHTS(ID,RIGHT1,USER_GROUP,DESCR) select nvl(max(ID),0)+1,:right,:g,'NI03.2 QA' from RIGHTS", right=right,g=group)
            resources = ResourceManagementService()
            equipment = resources.create_equipment(ResourceEquipmentCreateRequest(equipment_code=lot,equipment_type="REACHTRUCK",ware_id=1,created_by="admin"))
            resource = resources.create_resource(ResourceCreateRequest(resource_code=lot,resource_name="NI03.2 QA",resource_type="REACHTRUCK",equipment_id=equipment,user_id=owner,ware_id=1,created_by="admin"))
            from app.modules.resources.infrastructure.qualification_admin import QualificationAdmin
            QualificationAdmin(OracleGateway()).set_qualification(resource,"REPLENISHMENT",True,"admin")
            now = datetime.now()
            shift = resources.create_shift(ResourceShiftCreateRequest(shift_code=lot,shift_date=now.date(),start_at=now-timedelta(minutes=1),finish_at=now+timedelta(hours=1),ware_id=1,status="OPEN",created_by="admin"))
            session = resources.login_session(ResourceSessionLoginRequest(shift_id=shift,resource_id=resource,equipment_id=equipment,operator_user_id=owner,created_by="admin"))
            request_resources = {"resource_id": resource,"resource_session_id":session,"equipment_id":equipment}
            metadata("update RRL_WAREHOUSE_TASK set STATUS='PLANNED' where TASK_ID=:id", id=task)
            service = WarehouseTaskService()
            request = WarehouseTaskStatusRequest(updated_by=owner,assigned_to=owner,**request_resources)
            from app.modules.resources.infrastructure.qualified_candidates import QualifiedCandidates
            admin=QualificationAdmin(OracleGateway())
            admin.position(session,src,owner)
            choices=QualifiedCandidates(OracleGateway()).warehouse(task,10)
            assert choices and choices[0]["resource_id"]==resource and choices[0]["distance"]==0,choices
            admin.set_qualification(resource,"REPLENISHMENT",False,"admin")
            assert not any(item["resource_id"]==resource for item in QualifiedCandidates(OracleGateway()).warehouse(task,10))
            try:
                service.assign_task(task,request)
                raise AssertionError("Unqualified resource accepted")
            except HTTPException as exc:
                assert exc.status_code==409 and "QUALIFICATION_REQUIRED" in str(exc.detail),exc
            admin.set_qualification(resource,"REPLENISHMENT",True,"admin")
            service.assign_task(task,request)
            service.assign_task(task,request)
            service.start_task(task,request)
            service.start_task(task,request)
            q.execute("select count(*) from RRL_RESOURCE_FACT_EVENT where TASK_ID=:task and EVENT_TYPE in('ASSIGNED','STARTED')", task=task)
            assert q.fetchone() == (2,), "Repeated metadata action created a duplicate event"
            q.execute("select CURRENT_TASK_ID from RRL_RESOURCE_SESSION where SESSION_ID=:ses", ses=session)
            assert q.fetchone() == (task,)
            try:
                post("TASK_COMPLETE",body,{"task_id":task},actor=other)
                raise AssertionError("Other operator stole the active task")
            except oracledb.DatabaseError as exc:
                assert exc.args[0].code == 20882, exc
            try:
                service.assign_task(task,WarehouseTaskStatusRequest(updated_by=owner,assigned_to=other))
                raise AssertionError("In-progress reassignment was allowed")
            except HTTPException as exc:
                assert exc.status_code == 409, exc
            # A second queued physical step cannot start on the occupied session.
            metadata("insert into RRL_WAREHOUSE_TASK(TASK_ID,TASK_TYPE,TASK_SOURCE,SOURCE_TASK_ID,TO_CELL,QTY,QTY_MODE,STATUS,CREATED_BY) values(RRL_WAREHOUSE_TASK_SQ.nextval,'OTHER','MANUAL',:source,:dst,0,'BOX','PLANNED','admin')",source=task,dst=dst)
            q.execute("select TASK_ID from RRL_WAREHOUSE_TASK where TASK_SOURCE='MANUAL' and SOURCE_TASK_ID=:id",id=task)
            queued=int(q.fetchone()[0])
            try:
                service.start_task(queued,request)
                raise AssertionError("Second physical step occupied the same session")
            except HTTPException as exc:
                assert exc.status_code == 409 and any(note in str(exc.detail) for note in ("FINISH_CURRENT_PHYSICAL_STEP_FIRST","FINISH_OTHER_OPERATOR_PHYSICAL_STEP_FIRST")), exc
            metadata("update RRL_WAREHOUSE_TASK set STATUS='CANCELLED' where TASK_ID=:id",id=queued)
            body.update(request_resources)
            if finish_shift_mode:
                q.execute("select cast(STARTED_AT_INSTANT at time zone STARTED_SHIFT_TIME_ZONE as timestamp) from RRL_WAREHOUSE_TASK where TASK_ID=:id",id=task)
                started=q.fetchone()[0]
                metadata("update RRL_RESOURCE_SHIFT set FINISH_AT=:finished where SHIFT_ID=:id",finished=started+timedelta(seconds=1),id=shift)
                import time
                time.sleep(2)

        if marked_mode:
            from app.modules.inventory.infrastructure.task_scan_drafts import TaskScanDrafts
            drafts=TaskScanDrafts(OracleGateway());ctx=drafts.context(task)
            selected=codes[0]["codes"]
            request={"draft_id":"NI032.SCAN:"+tag,"profile_signature":ctx["profile_signature"],"expected_stock_version":ctx["stock_version"],"scans":selected}
            draft=drafts.save(task,request,owner)
            assert draft["unit_count"]==1 and draft["base_quantity"]=="1",draft
            assert drafts.save(task,request,owner)["idempotent"]
            try:
                drafts.save(task,{**request,"scans":codes[1]["codes"]},owner)
                raise AssertionError("Changed scan draft accepted under same ID")
            except HTTPException as exc:assert exc.status_code==409
            saved=drafts.latest(task,owner)
            assert len(saved["unit_keys"])==1
            body["scan_draft_id"]=request["draft_id"];body["unit_keys"]=saved["unit_keys"]
        operation = "NI032:PART:" + tag
        if marked_mode:
            metadata("update RRL_SKU_RECEIPT_PROFILE set PROFILE_VERSION='QA2' where ARTICUL=:a and SYSTEM_CODE='EGAIS'",a=article)
            try:
                post("TASK_COMPLETE",body,{"task_id":task},operation,actor=owner)
                raise AssertionError("Stale profile draft accepted")
            except HTTPException as exc:
                assert exc.status_code==409 and exc.detail["oracle_code"]==20886,exc
            q.execute("select REMAIN from RRL_REMAINS where UID_POLETA=:lot and CELL=:cell",lot=lot,cell=src)
            assert q.fetchone()==(3,), "Stale draft changed stock"
            metadata("update RRL_SKU_RECEIPT_PROFILE set PROFILE_VERSION='QA1' where ARTICUL=:a and SYSTEM_CODE='EGAIS'",a=article)
        result = post("TASK_COMPLETE", body, {"task_id": task}, operation, actor=owner)
        assert result["remaining_quantity"] == "2", result
        residual = result["residual_task_id"]
        assert post("TASK_COMPLETE", body, {"task_id": task}, operation, actor=owner) == result
        q.execute("select STATUS,QTY,RESOURCE_ID,RESOURCE_SESSION_ID,EQUIPMENT_ID,PLANNED_START_AT,PLANNED_FINISH_AT from RRL_WAREHOUSE_TASK where TASK_ID=:id", id=residual)
        assert q.fetchone() == ("PLANNED", 2, None, None, None, None, urgent_deadline)
        if session is not None:
            q.execute("select CURRENT_TASK_ID from RRL_RESOURCE_SESSION where SESSION_ID=:ses",ses=session)
            assert q.fetchone() == (None,), "Physical completion did not free the session"
        progress = task_progress(OracleGateway(), task)
        assert progress["confirmed_quantity"] == "1" and progress["remaining_quantity"] == "2", progress
        assert progress["next_task_id"] == residual
        if marked_mode:
            residual_context=drafts.context(residual)
            residual_request={"draft_id":"NI032.SCAN.REST:"+tag,"profile_signature":residual_context["profile_signature"],"expected_stock_version":residual_context["stock_version"],"scans":codes[1]["codes"]+codes[2]["codes"]}
            drafts.save(residual,residual_request,owner)
            saved=drafts.latest(residual,owner)
            remainder_body={**body,"fact_qty":"2","scan_draft_id":residual_request["draft_id"],"unit_keys":saved["unit_keys"]}
        else:remainder_body={**body,"fact_qty":"2"}
        if finish_shift_mode:
            try:
                service.start_task(residual,request)
                raise AssertionError("New physical step started outside shift")
            except HTTPException as exc:
                assert exc.status_code==409,exc
            metadata("update RRL_RESOURCE_SHIFT set FINISH_AT=:finished where SHIFT_ID=:id",finished=datetime.now()+timedelta(hours=1),id=shift)
            service.start_task(residual,request)
            print("PASS started physical step finishes after shift end; new residual step is rejected outside shift and starts only after valid window restored",flush=True)
        if capacity_mode:
            try:
                post("TASK_COMPLETE",remainder_body,{"task_id":residual},actor=owner)
                raise AssertionError("Overflow arrival was allowed")
            except oracledb.DatabaseError as exc:assert exc.args[0].code==20886,exc
            q.execute("select REMAIN from RRL_REMAINS where UID_POLETA=:lot and CELL=:src",lot=lot,src=src)
            assert q.fetchone()==(2,)
            metadata("update RRL_PICK_FACE set MAX_VOLUME=0.04 where PICK_FACE_ID=:id",id=face)
        post("TASK_COMPLETE",remainder_body,{"task_id":residual},actor=owner)
        if capacity_mode:
            q.execute("select RRL_STOCK_REPL_CAPACITY.remaining_base_quantity(:cell,:article) from dual",cell=dst,article=article)
            assert q.fetchone()==(0,),"Confirmed stock plus outstanding arrival must consume capacity4"

        progress = task_progress(OracleGateway(), residual)
        assert progress["confirmed_quantity"] == "3" and progress["remaining_quantity"] == "0", progress
        assert progress["status"] == "DONE" and progress["next_task_id"] is None
        q.execute("select STATUS from RRL_PICK_WAVE_REPLENISH_TASK where PICK_WAVE_REPLENISH_TASK_ID=:id", id=replenishment)
        assert q.fetchone() == ("DONE",)
        q.execute("select count(*) from RRL_WAREHOUSE_TASK_STOCK_MOVE where TASK_ID in(:a,:b)", a=task,b=residual)
        assert q.fetchone() == (2,)
        passed=True
        print("PASS NI03.2: partial fact 1 + residual 2 = 3, replay no duplicate, domain DONE only after residual, next action, resource context cleared, urgent deadline preserved when applicable")
    finally:
        if session is not None:
            metadata("update RRL_RESOURCE_SESSION set STATUS='CLOSED',LOGOUT_AT=systimestamp,CURRENT_TASK_ID=null where SESSION_ID=:id",id=session)
            metadata("update RRL_RESOURCE set ACTIVE=0,STATUS='CLOSED' where RESOURCE_ID=:id",id=resource)
            metadata("update RRL_RESOURCE_EQUIPMENT set ACTIVE=0,SERVICE_STATUS='RETIRED' where EQUIPMENT_ID=:id",id=equipment)
            metadata("update RUSERS set DELETED=1 where ID in(:a,:b)",a=owner,b=other)
        q.execute("select RESERVATION_ID from RRL_STOCK_RESERVATION where SOURCE_DOC_TYPE='PICK_WAVE' and SOURCE_DOC_ID=:wave and STATUS in('ACTIVE','ALLOCATED','PICKING') and BASE_QTY>0",wave=wave)
        for (reservation_id,) in q.fetchall():post("RESERVATION_RELEASE",{"reason":"End capacity case"},{"reservation_id":int(reservation_id)})
        metadata("update RRL_PICK_WAVE_REPLENISH_TASK set STATUS='CANCELLED' where PICK_WAVE_ID=:wave and STATUS!='DONE'",wave=wave)
        q.execute("select r.UID_POLETA,r.CELL,r.BASE_UOM,r.STOCK_VERSION from RRL_REMAINS r join RRL_PALLETS p on p.UID_PALLET=r.UID_POLETA where p.UID_PALLET like :lot or p.STOCK_ORIGIN_UID like :lot", lot=lot+"%")
        counts = [{"uid": u, "cell": c, "article": article, "unit": b, "quantity": "0",
                   "expected_stock_version": int(v), "unit_keys": []} for u,c,b,v in q.fetchall()]
        if marked_mode:
            for line in counts:
                q.execute("select PHYSICAL_UNIT_KEY from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:lot and CURRENT_CELL=:cell and STOCK_STATUS!='ISSUED'",lot=line["uid"],cell=line["cell"])
                line["unit_keys"]=[row[0] for row in q.fetchall()]
        if counts:
            post("INVENTORY_COUNT", {"reason": "End NI03.2 fixture", "counts": counts}, {"revision_id": revision})
        metadata("update RRL_WAREHOUSE_TASK set STATUS='CANCELLED' where SOURCE_DOC_ID=:wave and TASK_SOURCE='WAVE' and STATUS!='DONE'", wave=wave)
        metadata("update RRL_PICK_WAVE set STATUS='CANCELLED' where PICK_WAVE_ID=:wave", wave=wave)
        if capacity_mode and passed:
            print("PASS canonical volume: BOX-to-EA conversion, independent arrival budget, overflow rollback, valid residual")
        if marked_mode and passed:
            print("PASS server draft: CRPT+EGAIS aliases count physical units once; 1+2 moved; replay exact; codes preserved in source/residual")
        print("QA task", task, "stock restored; immutable movement history retained")
