"""Versioned explicit warehouse policy, with current actor checks before replay."""
from hashlib import sha256
import json
from typing import Any
import oracledb
from ...platform.public import read_oracle_json
from ..contracts import LogisticsCostError
from .cost_access import require_warehouse


def current_policy(cursor: Any, ware: int, *, lock: bool = False) -> dict[str, Any]:
    if lock:
        try:cursor.execute("insert into RRL_LOG_COST_PERIOD_HEAD(WARE_ID,VERSION_NO)select :ware,0 from dual where not exists(select 1 from RRL_LOG_COST_PERIOD_HEAD where WARE_ID=:ware)",ware=ware)
        except oracledb.DatabaseError as exc:
            if getattr(exc.args[0],"code",0)!=1:raise
    cursor.execute("select VERSION_NO from RRL_LOG_COST_PERIOD_HEAD where WARE_ID=:ware"+(" for update"if lock else ""),ware=ware)
    row=cursor.fetchone()
    if not row or row[0]==0:return {"warehouse_id":ware,"version":0,"period_mode":"LOADED_UTC","timezone_region":None,"source":"LEGACY_DEFAULT"}
    cursor.execute("select RESULT_JSON from RRL_LOG_COST_PERIOD_HISTORY where WARE_ID=:ware and VERSION_NO=:version",ware=ware,version=row[0])
    history=cursor.fetchone()
    if not history:raise LogisticsCostError("COST_PERIOD_HISTORY_MISSING","Нет сохранённого решения о расчётном периоде")
    return read_oracle_json(history[0])


def read_policy(gateway: Any,ware: int,actor: str)->dict[str,Any]:
    with gateway.transaction("Read warehouse financial period")as cursor:
        cursor.execute("set transaction read only")
        require_warehouse(cursor,ware,actor,"transport_dispatch_view")
        return current_policy(cursor,ware)


def set_policy(gateway: Any,op: str,ware: int,mode: str,region: str|None,version: int,reason: str,reference: str,actor: str)->dict[str,Any]:
    if mode not in {"LOADED_UTC","CASE_ASSEMBLY"}or(mode=="LOADED_UTC"and region is not None)or(mode=="CASE_ASSEMBLY"and not region):
        raise LogisticsCostError("COST_PERIOD_INVALID","Выберите дату погрузки UTC либо начало CASE с явным часовым поясом",422)
    digest=sha256(json.dumps([ware,mode,region,version,reason,reference,actor],ensure_ascii=False,separators=(",",":")).encode()).digest()
    try:
        with gateway.transaction("Version explicit warehouse financial period")as cursor:
            require_warehouse(cursor,ware,actor,"create_tt_price")
            cursor.execute("select PAYLOAD_HASH,RESULT_JSON from RRL_LOG_COST_PERIOD_HISTORY where OPERATION_ID=:op",op=op)
            old=cursor.fetchone()
            if old:
                if old[0]!=digest:raise LogisticsCostError("COST_PERIOD_PAYLOAD_CONFLICT","Идентификатор решения имеет другое содержание")
                return read_oracle_json(old[1])
            current=current_policy(cursor,ware,lock=True)
            require_warehouse(cursor,ware,actor,"create_tt_price")
            cursor.execute("select PAYLOAD_HASH,RESULT_JSON from RRL_LOG_COST_PERIOD_HISTORY where OPERATION_ID=:op",op=op)
            old=cursor.fetchone()
            if old:
                if old[0]!=digest:raise LogisticsCostError("COST_PERIOD_PAYLOAD_CONFLICT","Идентификатор решения имеет другое содержание")
                return read_oracle_json(old[1])
            if current["version"]!=version:raise LogisticsCostError("COST_PERIOD_VERSION_CONFLICT","Настройка уже изменена")
            if region:
                try:
                    cursor.execute("select to_char(systimestamp at time zone(:region),'TZR')from dual",region=region);cursor.fetchone()
                except oracledb.DatabaseError as exc:
                    if getattr(exc.args[0],"code",0)==1882:raise LogisticsCostError("COST_TIMEZONE_UNKNOWN","Неизвестный часовой пояс",422)from exc
                    raise
            cursor.execute("update RRL_LOG_COST_PERIOD_HEAD set VERSION_NO=VERSION_NO+1 where WARE_ID=:ware and VERSION_NO=:version",ware=ware,version=version)
            result={"operation_id":op,"warehouse_id":ware,"version":version+1,"period_mode":mode,"timezone_region":region,"source":"EXPLICIT_FINANCE_DECISION"}
            cursor.setinputsizes(body=oracledb.DB_TYPE_CLOB)
            cursor.execute("""insert into RRL_LOG_COST_PERIOD_HISTORY(WARE_ID,VERSION_NO,OPERATION_ID,PAYLOAD_HASH,PERIOD_MODE,TIME_ZONE,ACTOR,REASON_TEXT,DECISION_REFERENCE,RESULT_JSON)
                values(:ware,:version,:op,:digest,:period_kind,:region,:actor,:reason,:reference,:body)""",ware=ware,version=version+1,op=op,digest=digest,period_kind=mode,region=region,actor=actor,reason=reason,reference=reference,body=json.dumps(result))
            return result
    except oracledb.DatabaseError as exc:
        code=getattr(exc.args[0],"code",0)
        if code==1:raise LogisticsCostError("COST_PERIOD_VERSION_CONFLICT","Конкурирующее решение уже сохранено")from exc
        if 20800<=code<=20999:raise LogisticsCostError("COST_PERIOD_REJECTED",str(exc.args[0]).split("\n",1)[0],403 if code==20882 else 409)from exc
        raise
