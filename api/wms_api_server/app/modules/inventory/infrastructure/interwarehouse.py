"""Immutable routing of existing departed cargo; no new assignment or stock effect."""
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any
import json
import oracledb
from ...platform.public import read_oracle_json
from ..contracts_store_returns import StoreReturnReceiveError
from .metadata_transactions import receipt_task_metadata
from ..contracts_stock import StockCommand,StockPostingError
from .stock_posting_uow import StockPosting

class Interwarehouse:
    def __init__(self, gateway: Any, posting: StockPosting) -> None:
        self.gateway = gateway
        self.posting = posting

    def prepare_group_onward(self,operation: str,receipt: str,reason: str,reference: str,actor: str)->dict[str,Any]:
        from .interwarehouse_group_onward import InterwarehouseGroupOnward
        return InterwarehouseGroupOnward(self.gateway).prepare(operation,receipt,reason,reference,actor)

    def group_queue(self,ware: int,actor: str,limit: int=200,after_operation_id: str|None=None)->list[dict[str,Any]]:
        from .interwarehouse_group_read import InterwarehouseGroupRead
        return InterwarehouseGroupRead(self.gateway).queue(ware,actor,limit,after_operation_id)

    def group_detail(self,plan: str,actor: str)->dict[str,Any]:
        from .interwarehouse_group_read import InterwarehouseGroupRead
        return InterwarehouseGroupRead(self.gateway).detail(plan,actor)

    def plan_group_placement(self,operation: str,receipt: str,metadata: dict[str,Any],actor: str)->dict[str,Any]:
        from .interwarehouse_group_placement import InterwarehouseGroupPlacement
        return InterwarehouseGroupPlacement(self.gateway,self.posting).plan(operation,receipt,metadata,actor)

    def plan_group(self,operation: str,body: dict[str,Any],actor: str)->dict[str,Any]:
        from .interwarehouse_group_plan import InterwarehouseGroupPlan
        return InterwarehouseGroupPlan(self.gateway).plan(operation,body,actor)

    def group_source_proof(self,load: str,actor: str)->dict[str,Any]:
        from .interwarehouse_group_plan import InterwarehouseGroupPlan
        return InterwarehouseGroupPlan(self.gateway).source(load,actor)

    def group_source(self,load: str,actor: str)->dict[str,Any]:
        from .interwarehouse_group_source import InterwarehouseGroupSource
        return InterwarehouseGroupSource(self.gateway).read(load,actor)

    def decisions(self, plan_id: str, actor: str, after_revision: int=0) -> dict[str, Any]:
        from .interwarehouse_decisions import InterwarehouseDecisions
        return InterwarehouseDecisions(self.gateway).read(plan_id,actor,after_revision)

    def incoming(self, trip_id: int, actor: str) -> dict[str, Any]:
        from .interwarehouse_incoming import InterwarehouseIncoming
        return InterwarehouseIncoming(self.gateway).read(trip_id,actor)

    def record_temperature(self, operation_id: str, metadata: dict[str, Any], actor: str) -> dict[str, Any]:
        from .interwarehouse_dispatch import InterwarehouseDispatch
        return InterwarehouseDispatch(self.gateway).thermal(operation_id,metadata,actor)

    def record_decision(self, operation_id: str, metadata: dict[str, Any], actor: str) -> dict[str, Any]:
        from .interwarehouse_dispatch import InterwarehouseDispatch
        return InterwarehouseDispatch(self.gateway).record(operation_id,metadata,actor)

    def plan(self, operation_id: str, source_load: str, target_ware: int, target_trip: int, inbound_dock: str, arrival_due: datetime, ready_due: datetime, reason: str, reference: str, actor: str) -> dict[str, Any]:
        arrival = arrival_due.astimezone(timezone.utc)
        ready = ready_due.astimezone(timezone.utc)
        digest = sha256(json.dumps([source_load,target_ware,target_trip,inbound_dock,arrival.isoformat(),ready.isoformat(),reason,reference,actor],ensure_ascii=False,separators=(",",":")).encode()).digest()
        try:
            with receipt_task_metadata(self.gateway,"Existing two-leg cargo plan",actor,"transport_dispatch_edit") as cur:
                cur.callproc("RRL_INTERWARE_UNIT_SOURCE.assert_scope",[source_load,actor])
                cur.execute("select PAYLOAD_HASH,RESULT_JSON from RRL_INTERWARE_PLAN where OPERATION_ID=:op",op=operation_id)
                old = cur.fetchone()
                if old:
                    if old[0] != digest:
                        raise StoreReturnReceiveError("INTERWARE_PAYLOAD_CONFLICT","Operation content changed")
                    return read_oracle_json(old[1])
                cur.execute("select TT_ID,WARE_ID,ROOT_UID from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:source",source=source_load)
                source = cur.fetchone()
                if not source:
                    raise StoreReturnReceiveError("INTERWARE_SOURCE_NOT_FOUND","Actual source load required")
                for trip in sorted({int(source[0]),target_trip}):
                    cur.execute("select ID from RRL_TRANSPORT_TASK where ID=:trip for update wait 5",trip=trip)
                    if not cur.fetchone():
                        raise StoreReturnReceiveError("INTERWARE_TRIP_NOT_FOUND","Existing trip required")
                cur.execute("select SBORKA_PALLET_ID from RRL_TT_HU_LOAD_ST where LOAD_OPERATION_ID=:source and ACTIVE_FLAG=1 order by SBORKA_PALLET_ID",source=source_load)
                members = cur.fetchmany(2)
                if len(members) != 1:
                    raise StoreReturnReceiveError("INTERWARE_SINGLE_ST_REQUIRED","Single original ST required")
                cur.execute("select DOCK from RRL_TRANSPORT_TASK where ID=:trip",trip=target_trip)
                outbound = cur.fetchone()[0]
                stock_uid=cur.callfunc("RRL_IW_HU_SOURCE.stock_uid",str,[source_load])
                hu_wire=cur.var(oracledb.DB_TYPE_CLOB)
                cur.callproc("RRL_IW_HU_SOURCE.capture_context",[source_load,actor,hu_wire])
                source_hu=read_oracle_json(hu_wire.getvalue())if hu_wire.getvalue()is not None else None
                result = {"operation_id":operation_id,"status":"PLANNED","source_load_operation_id":source_load,"source_st_id":int(members[0][0]),"source_trip_id":int(source[0]),"source_warehouse_id":int(source[1]),"pallet_identifier":source[2],"target_warehouse_id":target_ware,"target_trip_id":target_trip,"inbound_dock":inbound_dock,"outbound_dock":outbound,"arrival_due":arrival.isoformat(),"ready_due":ready.isoformat(),"stock_changed":False,"physical_receipt_confirmed":False}
                if source_hu:
                    result.update(stock_pallet_identifier=stock_uid,physical_tree_expected=True,physical_place_identifier=source[2])
                cur.execute("select RRL_INTERWARE_UNIT_SOURCE.issued_manifest(LOAD_OPERATION_ID,:stock_uid,COMPOSITION_JSON) from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:load_id",
                            stock_uid=stock_uid,load_id=source_load)
                unit_source=read_oracle_json(cur.fetchone()[0])
                if unit_source["physical_unit_count"]:
                    result.update(physical_unit_count=unit_source["physical_unit_count"],unit_capture_required=True,
                                  original_unit_signature=unit_source["unit_signature"],regulatory_ack_verified=False)
                cur.setinputsizes(result_body=oracledb.DB_TYPE_CLOB,source_hu=oracledb.DB_TYPE_CLOB,arrival=oracledb.DB_TYPE_TIMESTAMP_TZ,ready=oracledb.DB_TYPE_TIMESTAMP_TZ)
                cur.execute("""insert into RRL_INTERWARE_PLAN(OPERATION_ID,PAYLOAD_HASH,SOURCE_LOAD_OPERATION_ID,SOURCE_ST_ID,SOURCE_TT_ID,SOURCE_WARE_ID,TARGET_WARE_ID,TARGET_TT_ID,ROOT_UID,SOURCE_PLACE_UID,SOURCE_HU_JSON,SOURCE_COMPOSITION_JSON,INBOUND_DOCK,OUTBOUND_DOCK,ARRIVAL_DUE,READY_DUE,REASON_TEXT,DECISION_REFERENCE,ACTOR,RESULT_JSON)
                    select :op,:digest,f.LOAD_OPERATION_ID,:st,f.TT_ID,f.WARE_ID,:ware,:trip,:stock_uid,:source_place,:source_hu,f.COMPOSITION_JSON,:inbound,:outbound,:arrival,:ready,:reason,:reference,:actor,:result_body from RRL_TT_HU_LOAD_FACT f where f.LOAD_OPERATION_ID=:source""",stock_uid=stock_uid,source_place=source[2]if source_hu else None,source_hu=json.dumps(source_hu)if source_hu else None,op=operation_id,digest=digest,st=members[0][0],ware=target_ware,trip=target_trip,inbound=inbound_dock,outbound=outbound,arrival=arrival,ready=ready,reason=reason,reference=reference,actor=actor,result_body=json.dumps(result),source=source_load)
                cur.callproc("RRL_INTERWARE_UNIT_SOURCE.capture_plan",[operation_id,actor])
                return result
        except oracledb.DatabaseError as exc:
            code = getattr(exc.args[0],"code",0)
            if code == 1 or 20800 <= code <= 20999:
                raise StoreReturnReceiveError("INTERWARE_PLAN_REJECTED",str(exc.args[0]).split("\n",1)[0],403 if code == 20882 else 409) from exc
            raise

    def receive_action(self, kind: str, operation_id: str, plan_id: str, metadata: dict[str, Any], actor: str) -> dict[str, Any]:
        if kind not in ("INTERWARE_UNLOAD","INTERWARE_RECEIVE"):
            raise ValueError("Unknown physical interwarehouse action")
        from ..domain.interwarehouse_scans import normalize_interwarehouse_scans
        try:
            metadata=normalize_interwarehouse_scans(metadata)
        except ValueError as exc:
            raise StoreReturnReceiveError("INTERWARE_SCAN_INVALID",str(exc),422)from exc
        try:
            return self.posting.post(StockCommand(operation_id=operation_id,command_type=kind,actor=actor,source={"plan_operation_id":plan_id},lines=(),metadata=metadata))
        except oracledb.DatabaseError as exc:
            raise StockPostingError("INTERWARE_TECHNICAL_FAILURE",operation_id,getattr(exc.args[0],"code",None)) from exc

    def plan_placement(self, operation_id: str, receipt_id: str, actor: str, superseded_task_id: int | None=None, replan_reason: str | None=None) -> dict[str, Any]:
        metadata = {} if superseded_task_id is None else {"superseded_task_id":superseded_task_id,"replan_reason":replan_reason}
        try:
            return self.posting.post(StockCommand(operation_id=operation_id,command_type="INTERWARE_PUTAWAY_PLAN",actor=actor,source={"receipt_operation_id":receipt_id},lines=(),metadata=metadata))
        except oracledb.DatabaseError as exc:
            raise StockPostingError("INTERWARE_TECHNICAL_FAILURE",operation_id,getattr(exc.args[0],"code",None)) from exc

    def release_custody(self, operation_id: str, receipt_id: str, actor: str) -> dict[str, Any]:
        try:
            return self.posting.post(StockCommand(operation_id=operation_id,command_type="INTERWARE_CUSTODY_RELEASE",actor=actor,source={"receipt_operation_id":receipt_id},lines=(),metadata={}))
        except oracledb.DatabaseError as exc:
            raise StockPostingError("INTERWARE_TECHNICAL_FAILURE",operation_id,getattr(exc.args[0],"code",None)) from exc

    def prepare_onward(self, operation_id: str, receipt_id: str, reason: str, reference: str, actor: str, accept_legacy_address: bool=False) -> dict[str, Any]:
        from .interwarehouse_onward import InterwarehouseOnward
        return InterwarehouseOnward(self.gateway).prepare(operation_id,receipt_id,reason,reference,actor,accept_legacy_address)

    def unit_manifest(self, plan_id: str, actor: str) -> dict[str, Any]:
        try:
            with self.gateway.transaction("Current scoped interwarehouse unit source") as q:
                q.execute("set transaction read only")
                q.execute("select RRL_INTERWARE_UNIT_SOURCE.plan_manifest(:plan,:actor) from dual",plan=plan_id,actor=actor)
                result = read_oracle_json(q.fetchone()[0])
                q.execute("select p.SYSTEM_CODE,p.PROFILE_CODE,p.PROFILE_VERSION,p.SCAN_MODE from RRL_SKU_RECEIPT_PROFILE p join RRL_PALLETS l on l.ARTICUL=p.ARTICUL join RRL_INTERWARE_PLAN i on i.ROOT_UID=l.UID_PALLET where i.OPERATION_ID=:plan order by p.SYSTEM_CODE,p.PROFILE_CODE fetch first 51 rows only",plan=plan_id)
                result["profiles"] = [{"system_code":r[0],"profile_code":r[1],"profile_version":r[2],"scan_mode":r[3]} for r in q.fetchall()]
                wire=q.var(oracledb.DB_TYPE_CLOB);wire.setvalue(0,json.dumps(result.get("units",[])))
                q.execute("""select u.PHYSICAL_UNIT_KEY,u.UNIT_ID,j.Q,j.B from
                    json_table(:unit_keys,'$[*]'columns(K varchar2(64)path '$.key',Q varchar2(60)path '$.quantity',B varchar2(20)path '$.base_uom'))j
                    join RRL_WMS_RECEIPT_UNIT u on u.PHYSICAL_UNIT_KEY=j.K order by u.PHYSICAL_UNIT_KEY""",unit_keys=wire)
                result["display_units"]=[{"key":r[0],"unit_id":r[1],"quantity":r[2],"base_uom":r[3]}for r in q.fetchall()]

                return result
        except oracledb.DatabaseError as exc:
            code = getattr(exc.args[0],"code",0)
            raise StoreReturnReceiveError("INTERWARE_MANIFEST_REJECTED",str(exc.args[0]).split("\n",1)[0],403 if code==20882 else 409) from exc

    def queue(self, ware_id: int, actor: str, include_completed: bool=False) -> list[dict[str, Any]]:
        from .interwarehouse_queue import InterwarehouseQueue
        return InterwarehouseQueue(self.gateway).read(ware_id,actor,include_completed)


    def close_incident(self,operation: str,body: dict,actor: str) -> dict:
        from .interwarehouse_incident_close import close_incident
        return close_incident(self.gateway,operation,body,actor)

    def shortage(self,receipt_id: str,actor: str,selected_request: str|None=None) -> dict:
        from .interwarehouse_shortage import read_shortage
        return read_shortage(self.gateway,receipt_id,actor,selected_request)

    def shortage_action(self,kind: str,operation: str,source_id: str,metadata: dict,actor: str) -> dict:
        key="receipt_operation_id"if kind=="INTERWARE_SHORTAGE_REPORT"else "request_operation_id"
        return self.posting.post(StockCommand(operation_id=operation,command_type=kind,actor=actor,source={key:source_id},lines=(),metadata=metadata))

    def recovery_action(self,kind: str,operation: str,source_id: str,metadata: dict,actor: str) -> dict:
        key="loss_operation_id"if kind=="INTERWARE_RECOVERY_REPORT"else "request_operation_id"
        return self.posting.post(StockCommand(operation_id=operation,command_type=kind,actor=actor,source={key:source_id},lines=(),metadata=metadata))

    def receive_recovery(self,operation: str,approval_id: str,metadata: dict,actor: str) -> dict:
        from ..domain.interwarehouse_scans import normalize_interwarehouse_scans
        metadata=normalize_interwarehouse_scans(metadata)
        return self.posting.post(StockCommand(operation_id=operation,command_type="INTERWARE_SHORTAGE_RECOVER",actor=actor,source={"approval_operation_id":approval_id},lines=(),metadata=metadata))

    def plan_recovery_placement(self,operation_id: str,recovery_id: str,actor: str) -> dict[str,Any]:
        return self.posting.post(StockCommand(operation_id=operation_id,command_type="INTERWARE_RECOVERY_PUTAWAY_PLAN",actor=actor,source={"recovery_operation_id":recovery_id},lines=(),metadata={}))

    def prepare_recovery_onward(self,operation_id: str,recovery_id: str,trip_id: int,reason: str,reference: str,actor: str) -> dict[str,Any]:
        from .interwarehouse_recovery_st import prepare_recovery_st
        return prepare_recovery_st(self.gateway,operation_id,recovery_id,trip_id,reason,reference,actor)
