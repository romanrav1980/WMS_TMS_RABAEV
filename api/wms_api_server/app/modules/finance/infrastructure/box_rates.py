from hashlib import sha256
from decimal import Decimal
from typing import Any
import json,oracledb
from ...platform.public import read_oracle_json
from ..contracts import LogisticsCostError
from ..domain.amount import rate_value
from .cost_access import require_warehouse

def set_box_rate(gateway: Any,ware: int,currency: str,value: str,effective: str,version: int,reason: str,reference: str,actor: str, *, components: dict[str,str] | None=None) -> dict[str,Any]:
    try:amount=rate_value(value)
    except ValueError as exc:raise LogisticsCostError("COST_RATE_INVALID",str(exc),422) from exc
    def result() -> dict[str,Any]:
        value={"warehouse_id":ware,"cost_code":"WAREHOUSE_PICKING","currency":currency,"rate_key":key,"version":version+1,"rate":str(amount),"basis":"BOX","effective_from":effective,"common_work_included":True}
        if components is not None:value["components"]=components
        return value
    key=sha256(f"{ware}:WAREHOUSE_PICKING:{currency}".encode()).hexdigest()
    try:
        with gateway.transaction("Version warehouse BOX cost rate") as cur:
            cur.execute("lock table RRL_ACCESS_REV in share mode wait 5")
            require_warehouse(cur,ware,actor,"create_tt_price")
            cur.execute("select VERSION_NO from RRL_LOGISTICS_RATE_HEAD where RATE_KEY=:key for update",{"key":key})
            old=cur.fetchone()
            if (old[0]if old else 0)!=version:
                cur.execute("select to_char(RATE_VALUE,'TM9','NLS_NUMERIC_CHARACTERS=''.,'''),to_char(EFFECTIVE_FROM,'YYYY-MM-DD'),REASON_TEXT,DECISION_REFERENCE,ACTOR,COMPONENTS_JSON from RRL_LOGISTICS_RATE_HISTORY where RATE_KEY=:key and VERSION_NO=:version",{"key":key,"version":version+1})
                prior=cur.fetchone()
                if prior and Decimal(prior[0])==amount and prior[1:5]==(effective,reason,reference,actor) and (read_oracle_json(prior[5])if prior[5]is not None else None)==components:
                    return result()
                raise LogisticsCostError("COST_RATE_VERSION_CONFLICT","Обновите версию ставки")
            if old:
                cur.execute("select to_char(max(EFFECTIVE_FROM),'YYYY-MM-DD')from RRL_LOGISTICS_RATE_HISTORY where RATE_KEY=:key",{"key":key})
                if effective<cur.fetchone()[0]:raise LogisticsCostError("COST_RATE_EFFECTIVE_ORDER","Дата новой редакции не может предшествовать последнему периоду")
                cur.execute("update RRL_LOGISTICS_RATE_HEAD set VERSION_NO=VERSION_NO+1 where RATE_KEY=:key",{"key":key})
            else:
                cur.execute("insert into RRL_LOGISTICS_RATE_HEAD(RATE_KEY,WARE_ID,COST_CODE,CURRENCY,VERSION_NO)values(:key,:ware,'WAREHOUSE_PICKING',:currency,1)",{"key":key,"ware":ware,"currency":currency})
            cur.setinputsizes(components_body=oracledb.DB_TYPE_CLOB)
            cur.execute("insert into RRL_LOGISTICS_RATE_HISTORY(RATE_KEY,VERSION_NO,RATE_VALUE,EFFECTIVE_FROM,REASON_TEXT,DECISION_REFERENCE,ACTOR,COMPONENTS_JSON)values(:key,:version,:value,to_date(:effective,'FXYYYY-MM-DD'),:reason,:reference,:actor,:components_body)",{"key":key,"version":version+1,"value":amount,"effective":effective,"reason":reason,"reference":reference,"actor":actor,"components_body":json.dumps(components,sort_keys=True,separators=(",",":"))if components is not None else None})
            return result()
    except oracledb.DatabaseError as exc:
        code=getattr(exc.args[0],"code",0)
        if code==1:raise LogisticsCostError("COST_RATE_VERSION_CONFLICT","Ставка уже изменена другим сотрудником") from exc
        if 20800<=code<=20999:raise LogisticsCostError("COST_RATE_REJECTED",str(exc.args[0]).split("\n",1)[0],403 if code==20882 else 409) from exc
        raise
