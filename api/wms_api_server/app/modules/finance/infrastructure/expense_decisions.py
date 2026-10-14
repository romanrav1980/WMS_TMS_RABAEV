from hashlib import sha256
from typing import Any
import json,oracledb
from ...platform.public import read_oracle_json
from ..contracts import LogisticsCostError
from .finance_outbox import enqueue,expense_payload
from .cost_access import require_warehouse
from .expense_correction import lock_correction_root,assert_correction_decision

def decide_expense(gateway: Any,op: str,expense: str,phase: str,outcome: str,basis: str,reference: str,reason: str,actor: str) -> dict[str,Any]:
    digest=sha256(json.dumps([expense,phase,outcome,basis,reference,reason,actor],ensure_ascii=False,separators=(",",":")).encode()).digest()
    with gateway.transaction("Independent additional expense decision") as cur:
        from .normative_correction import lock_root
        cost_root=lock_root(cur,expense)
        root=lock_correction_root(cur,expense)if cost_root is None else None
        cur.execute("select WARE_ID,OBJECT_KIND from RRL_LOGISTICS_EXPENSE where OPERATION_ID=:id for update",{"id":expense});source=cur.fetchone()
        if not source:raise LogisticsCostError("EXPENSE_NOT_FOUND","Расход не найден",404)
        require_warehouse(cur,source[0],actor,"calc_tt_price" if phase=="LOGIST" else "create_tt_price")
        cur.execute("select PAYLOAD_HASH,RESULT_JSON from RRL_LOGISTICS_EXP_DECISION where OPERATION_ID=:op",{"op":op});old=cur.fetchone()
        if old:
            if old[0]!=digest:raise LogisticsCostError("EXPENSE_DECISION_PAYLOAD_CONFLICT","Операция уже имеет другое содержание")
            return read_oracle_json(old[1])
        cur.execute("select count(*)from RRL_LOGISTICS_EXP_DECISION where EXPENSE_OPERATION_ID=:id and PHASE=:phase",{"id":expense,"phase":phase})
        if cur.fetchone()[0]:raise LogisticsCostError("EXPENSE_PHASE_ALREADY_DECIDED","Решение этой стадии уже сохранено")
        if root:assert_correction_decision(cur,expense,root,phase,outcome,basis)
        if source[1]=="VEHICLE" and basis!="NONE":raise LogisticsCostError("EXPENSE_VEHICLE_NOT_ALLOCATED","Расход автомобиля не распределяется на товар")
        status="REJECTED" if outcome=="REJECT" else "LOGIST_APPROVED" if phase=="LOGIST" else "APPROVED_VEHICLE_ONLY" if source[1]=="VEHICLE" else "APPROVED_PENDING_ALLOCATION"
        result={"operation_id":op,"expense_operation_id":expense,"status":status,"phase":phase,"basis":basis,"stock_changed":False}
        cur.setinputsizes(result_body=oracledb.DB_TYPE_CLOB)
        cur.execute("insert into RRL_LOGISTICS_EXP_DECISION(OPERATION_ID,PAYLOAD_HASH,EXPENSE_OPERATION_ID,PHASE,OUTCOME,DISTRIBUTION_BASIS,DECISION_REFERENCE,REASON_TEXT,ACTOR,RESULT_JSON)values(:op,:hash_value,:expense,:phase,:outcome,:basis,:reference,:reason,:actor,:result_body)",{"op":op,"hash_value":digest,"expense":expense,"phase":phase,"outcome":outcome,"basis":basis,"reference":reference,"reason":reason,"actor":actor,"result_body":json.dumps(result)})
        if phase=='FINANCE':
            enqueue(cur,'EXTRA_EXPENSE_RECOGNIZED' if outcome=='APPROVE' else 'EXTRA_EXPENSE_REJECTED',op,expense_payload(cur,expense,{**result,"decision_actor":actor}),'MONETARY_RECOGNITION' if outcome=='APPROVE' else 'NO_POSTING')
        return result
