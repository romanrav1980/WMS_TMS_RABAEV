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
                cur.execute("select TT_ID,WARE_ID,ROOT_UID,COMPOSITION_JSON from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:source",source=source_load)
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
                result = {"operation_id":operation_id,"status":"PLANNED","source_load_operation_id":source_load,"source_st_id":int(members[0][0]),"source_trip_id":int(source[0]),"source_warehouse_id":int(source[1]),"pallet_identifier":source[2],"target_warehouse_id":target_ware,"target_trip_id":target_trip,"inbound_dock":inbound_dock,"outbound_dock":outbound,"arrival_due":arrival.isoformat(),"ready_due":ready.isoformat(),"stock_changed":False,"physical_receipt_confirmed":False}
                cur.execute("select RRL_INTERWARE_UNIT_SOURCE.issued_manifest(:load_id,:root_id,:snapshot) from dual",
                            load_id=source_load,root_id=source[2],snapshot=source[3])
                unit_source=read_oracle_json(cur.fetchone()[0])
                if unit_source["physical_unit_count"]:
                    result.update(physical_unit_count=unit_source["physical_unit_count"],unit_capture_required=True,
                                  original_unit_signature=unit_source["unit_signature"],regulatory_ack_verified=False)
                cur.setinputsizes(result_body=oracledb.DB_TYPE_CLOB,arrival=oracledb.DB_TYPE_TIMESTAMP_TZ,ready=oracledb.DB_TYPE_TIMESTAMP_TZ)
                cur.execute("""insert into RRL_INTERWARE_PLAN(OPERATION_ID,PAYLOAD_HASH,SOURCE_LOAD_OPERATION_ID,SOURCE_ST_ID,SOURCE_TT_ID,SOURCE_WARE_ID,TARGET_WARE_ID,TARGET_TT_ID,ROOT_UID,SOURCE_COMPOSITION_JSON,INBOUND_DOCK,OUTBOUND_DOCK,ARRIVAL_DUE,READY_DUE,REASON_TEXT,DECISION_REFERENCE,ACTOR,RESULT_JSON)
                    select :op,:digest,f.LOAD_OPERATION_ID,:st,f.TT_ID,f.WARE_ID,:ware,:trip,f.ROOT_UID,f.COMPOSITION_JSON,:inbound,:outbound,:arrival,:ready,:reason,:reference,:actor,:result_body from RRL_TT_HU_LOAD_FACT f where f.LOAD_OPERATION_ID=:source""",op=operation_id,digest=digest,st=members[0][0],ware=target_ware,trip=target_trip,inbound=inbound_dock,outbound=outbound,arrival=arrival,ready=ready,reason=reason,reference=reference,actor=actor,result_body=json.dumps(result),source=source_load)
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
        try:
            return self.posting.post(StockCommand(operation_id=operation_id,command_type=kind,actor=actor,source={"plan_operation_id":plan_id},lines=(),metadata=metadata))
        except oracledb.DatabaseError as exc:
            raise StockPostingError("INTERWARE_TECHNICAL_FAILURE",operation_id,getattr(exc.args[0],"code",None)) from exc

    def plan_placement(self, operation_id: str, receipt_id: str, actor: str) -> dict[str, Any]:
        try:
            return self.posting.post(StockCommand(operation_id=operation_id,command_type="INTERWARE_PUTAWAY_PLAN",actor=actor,source={"receipt_operation_id":receipt_id},lines=(),metadata={}))
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

    def queue(self, ware_id: int, actor: str) -> list[dict[str, Any]]:
        allowed = self.gateway.fetch_all("select count(*) ALLOWED from RUSERS where ID=:actor and nvl(DELETED,0)=0 and(WARE_ID=:ware or upper(trim(USER_GROUP))='GLOBAL_ADMIN')",{"actor":actor,"ware":ware_id})
        if allowed[0]["allowed"] != 1:
            raise StoreReturnReceiveError("INTERWARE_WARE_FORBIDDEN","User warehouse binding required",403)
        return self.gateway.fetch_all("""select OPERATION_ID,SOURCE_LOAD_OPERATION_ID,SOURCE_ST_ID,SOURCE_TT_ID,SOURCE_WARE_ID,TARGET_WARE_ID,TARGET_TT_ID,ROOT_UID PALLET_IDENTIFIER,INBOUND_DOCK,OUTBOUND_DOCK,ARRIVAL_DUE,READY_DUE,DECISION_REFERENCE,p.ACTOR,json_value(p.SOURCE_COMPOSITION_JSON,'$.nodes[0].article') ARTICLE,json_value(p.SOURCE_COMPOSITION_JSON,'$.nodes[0].quantity') QUANTITY,json_value(p.SOURCE_COMPOSITION_JSON,'$.nodes[0].base_uom') BASE_UOM,(select t.TRANSPORT from RRL_TRANSPORT_TASK t where t.ID=p.SOURCE_TT_ID) VEHICLE_NUMBER,(select u.OPERATION_ID from RRL_INTERWARE_UNLOAD u where u.PLAN_OPERATION_ID=p.OPERATION_ID) UNLOAD_OPERATION_ID,(select r.OPERATION_ID from RRL_INTERWARE_RECEIPT r where r.PLAN_OPERATION_ID=p.OPERATION_ID) RECEIPT_OPERATION_ID,(select f.TASK_ID from RRL_INTERWARE_PLACEMENT f join RRL_INTERWARE_RECEIPT r on r.OPERATION_ID=f.RECEIPT_OPERATION_ID where r.PLAN_OPERATION_ID=p.OPERATION_ID) PLACED_TASK_ID,(select f.OPERATION_ID from RRL_INTERWARE_CUSTODY_PROOF f join RRL_INTERWARE_RECEIPT r on r.OPERATION_ID=f.RECEIPT_OPERATION_ID where r.PLAN_OPERATION_ID=p.OPERATION_ID) CUSTODY_RELEASE_OPERATION_ID,(select b.ST_IDENTIFIER from RRL_INTERWARE_ONWARD_BIND b join RRL_INTERWARE_RECEIPT r on r.OPERATION_ID=b.RECEIPT_OPERATION_ID where r.PLAN_OPERATION_ID=p.OPERATION_ID) ONWARD_ST_IDENTIFIER from RRL_INTERWARE_PLAN p where SOURCE_WARE_ID=:ware or TARGET_WARE_ID=:ware order by ARRIVAL_DUE,OPERATION_ID fetch first 100 rows only""",{"ware":ware_id})
