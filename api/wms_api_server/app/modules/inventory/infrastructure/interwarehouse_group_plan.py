"""Immutable plan for an entire existing departed multi-ST handling unit."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from typing import Any
import oracledb
from ...platform.public import read_oracle_json
from ..contracts_store_returns import StoreReturnReceiveError
from .metadata_transactions import receipt_task_metadata


class InterwarehouseGroupPlan:
    def __init__(self,gateway: Any)->None:
        self.gateway=gateway

    def plan(self,operation: str,body: dict[str,Any],actor: str)->dict[str,Any]:
        arrival=body["arrival_due"].astimezone(timezone.utc)
        ready=body["ready_due"].astimezone(timezone.utc)
        payload=dict(body,arrival_due=arrival.isoformat(),ready_due=ready.isoformat(),actor=actor)
        digest=sha256(json.dumps(payload,sort_keys=True,ensure_ascii=False,separators=(",",":")).encode()).digest()
        load=body["source_load_operation_id"]
        try:
            with receipt_task_metadata(self.gateway,"Whole multi-ST interwarehouse plan",actor,"transport_dispatch_edit")as q:
                q.callproc("RRL_INTERWARE_UNIT_SOURCE.assert_scope",[load,actor])
                q.execute("select PAYLOAD_HASH,RESULT_JSON from RRL_IW_GROUP_PLAN where OPERATION_ID=:op",op=operation)
                old=q.fetchone()
                if old:
                    if old[0]!=digest:
                        raise StoreReturnReceiveError("INTERWARE_GROUP_PAYLOAD_CONFLICT","Operation content changed")
                    return read_oracle_json(old[1])
                q.execute("select RRL_IW_GROUP_SOURCE.source_json(:load_id,:actor)from dual",load_id=load,actor=actor)
                wire=q.fetchone()[0]; wire=wire.read()if hasattr(wire,"read")else wire
                source=read_oracle_json(wire)
                signature=sha256(wire.encode("utf-8")).hexdigest()
                if signature!=body["expected_source_signature"]:
                    raise StoreReturnReceiveError("INTERWARE_GROUP_SOURCE_CHANGED","Refresh the whole source composition")
                for trip in sorted({source["source_trip_id"],body["target_trip_id"]}):
                    q.execute("select ID from RRL_TRANSPORT_TASK where ID=:trip_id for update wait 5",trip_id=trip)
                    if q.fetchone()is None:
                        raise StoreReturnReceiveError("INTERWARE_GROUP_TRIP_NOT_FOUND","Existing trip required")
                q.execute("select DOCK from RRL_TRANSPORT_TASK where ID=:trip_id",trip_id=body["target_trip_id"])
                outbound=q.fetchone()[0]
                result=dict(operation_id=operation,status="PLANNED",source_load_operation_id=load,
                    source_trip_id=source["source_trip_id"],source_warehouse_id=source["source_warehouse_id"],
                    target_trip_id=body["target_trip_id"],target_warehouse_id=body["target_warehouse_id"],
                    physical_place_identifier=source["physical_place_identifier"],stock_leaf_count=source["stock_leaf_count"],
                    source_signature=signature,inbound_dock=body["inbound_dock"],outbound_dock=outbound,
                    arrival_due=arrival.isoformat(),ready_due=ready.isoformat(),stock_changed=False,
                    physical_receipt_confirmed=False,grouped_receipt_available=False,regulatory_ack_verified=False)
                q.setinputsizes(source_json=oracledb.DB_TYPE_CLOB,result_json=oracledb.DB_TYPE_CLOB,
                                arrival=oracledb.DB_TYPE_TIMESTAMP_TZ,ready=oracledb.DB_TYPE_TIMESTAMP_TZ)
                q.execute("""insert into RRL_IW_GROUP_PLAN(OPERATION_ID,PAYLOAD_HASH,SOURCE_LOAD_OPERATION_ID,
                    SOURCE_WARE_ID,TARGET_WARE_ID,SOURCE_TT_ID,TARGET_TT_ID,ROOT_UID,INBOUND_DOCK,OUTBOUND_DOCK,
                    ARRIVAL_DUE,READY_DUE,SOURCE_JSON,RESULT_JSON,REASON_TEXT,DECISION_REFERENCE,ACTOR)
                    values(:op,:digest,:load_id,:source_ware,:target_ware,:source_trip,:target_trip,:root_uid,
                    :inbound,:outbound,:arrival,:ready,:source_json,:result_json,:reason,:reference,:actor)""",
                    op=operation,digest=digest,load_id=load,source_ware=source["source_warehouse_id"],
                    target_ware=body["target_warehouse_id"],source_trip=source["source_trip_id"],
                    target_trip=body["target_trip_id"],root_uid=source["physical_place_identifier"],
                    inbound=body["inbound_dock"],outbound=outbound,arrival=arrival,ready=ready,source_json=wire,
                    result_json=json.dumps(result),reason=body["reason"],reference=body["decision_reference"],actor=actor)
                return result
        except oracledb.DatabaseError as exc:
            code=getattr(exc.args[0],"code",0)
            if code in(1,2290)or 20800<=code<=20999:
                raise StoreReturnReceiveError("INTERWARE_GROUP_PLAN_REJECTED",str(exc.args[0]).split("\n",1)[0],
                                              403 if code==20882 else 409)from exc
            raise

    def source(self,load: str,actor: str)->dict[str,Any]:
        try:
            with self.gateway.transaction("Authoritative grouped source snapshot")as q:
                q.execute("set transaction read only")
                q.execute("select RRL_IW_GROUP_SOURCE.source_json(:load_id,:actor)from dual",load_id=load,actor=actor)
                wire=q.fetchone()[0];wire=wire.read()if hasattr(wire,"read")else wire
                return dict(source=read_oracle_json(wire),source_signature=sha256(wire.encode("utf-8")).hexdigest(),
                            stock_changed=False,grouped_receipt_available=False)
        except oracledb.DatabaseError as exc:
            code=getattr(exc.args[0],"code",0)
            if 20800<=code<=20999:
                raise StoreReturnReceiveError("INTERWARE_GROUP_SOURCE_REJECTED",str(exc.args[0]).split("\n",1)[0],
                                              403 if code==20882 else 409)from exc
            raise
