from hashlib import sha256
from decimal import Decimal
from typing import Any
import json,oracledb
from ...platform.public import read_oracle_json
from ..contracts import LogisticsCostError
from ..domain.amount import rate_value
from ..domain.expense_value import signed_amount
from .expense_correction import correction_source
from .cost_access import require_warehouse

def report_expense(gateway: Any,op: str,ware: int,code: str,kind: str,object_id: int,value: str,currency: str,day: str,reference: str,reason: str,actor: str,correction: str|None=None,expected: str|None=None,cost_correction: str|None=None) -> dict[str,Any]:
    try:amount=signed_amount(value,correction is not None or cost_correction is not None)
    except ValueError as exc:raise LogisticsCostError("EXPENSE_AMOUNT_INVALID",str(exc),422) from exc
    if correction is not None and cost_correction is not None:raise LogisticsCostError("ONE_FINANCIAL_CORRECTION_SOURCE_REQUIRED","Укажите один исходник коррекции",422)
    if (correction is not None or cost_correction is not None)!=(expected is not None):raise LogisticsCostError("EXPENSE_CORRECTION_TOTAL_REQUIRED","Для коррекции нужны исходный расход и ожидаемый итог",422)
    try:expected_value=rate_value(expected) if expected is not None else None
    except ValueError as exc:raise LogisticsCostError("EXPENSE_CORRECTION_TOTAL_INVALID",str(exc),422) from exc
    sign=-1 if amount<0 else 1;quantity=format(amount,".2f")
    source_values=[ware,code,kind,object_id,quantity,currency,day,reference,reason,actor]
    if correction is not None:source_values.extend([correction,format(expected_value,".2f")])
    if cost_correction is not None:source_values.extend(["NORMATIVE_COST",cost_correction,format(expected_value,".2f")])
    digest=sha256(json.dumps(source_values,ensure_ascii=False,separators=(",",":")).encode()).digest()
    with gateway.transaction("Register immutable additional expense") as cur:
        require_warehouse(cur,ware,actor,"edit_bill_tt")
        cur.execute("select PAYLOAD_HASH,RESULT_JSON from RRL_LOGISTICS_EXPENSE where OPERATION_ID=:op",{"op":op});old=cur.fetchone()
        if old:
            if old[0]!=digest:raise LogisticsCostError("EXPENSE_PAYLOAD_CONFLICT","Операция уже имеет другое содержание")
            return read_oracle_json(old[1])
        if cost_correction:
            from .normative_correction import validate_report
            validate_report(cur,cost_correction,ware,kind,object_id,currency,amount,expected_value)
        if correction:
            name,version=correction_source(cur,correction,expected_value,amount,ware,code,kind,object_id,currency);article=(name,version)
        else:
            cur.execute("select NAME,VERSION_NO,OBJECT_SCOPE,INCLUDED_IN_RATE,ACTIVE_FLAG from RRL_LOGISTICS_EXP_ARTICLE where CODE=:code",{"code":code});article=cur.fetchone()
            if not article or article[2]not in(kind,"BOTH")or article[3]!=0 or article[4]!=1:raise LogisticsCostError("EXPENSE_EXTRA_ARTICLE_REQUIRED","Выберите активную дополнительную статью, не включённую в ставку")
        if kind=="TRIP":
            cur.execute("""select count(*)from RRL_TRANSPORT_TASK t where t.ID=:id and(exists(select 1 from RRL_TT_HU_LOAD_FACT l where l.TT_ID=t.ID and l.WARE_ID=:ware)or exists(select 1 from RRL_SBORKA_PALLETS s where s.TRANSTASK_ID=t.ID and s.WARE_ID=:ware))""",{"id":object_id,"ware":ware})
            if cur.fetchone()[0]!=1:raise LogisticsCostError("EXPENSE_TRIP_WAREHOUSE_REQUIRED","Рейс не связан с выбранным складом")
        result={"operation_id":op,"status":"REPORTED","object_kind":kind,"object_id":object_id,"amount":quantity,"currency":currency,"warehouse_id":ware,"stock_changed":False}
        if cost_correction:result.update(cost_correction_of_operation_id=cost_correction,expected_confirmed_total=format(expected_value,".2f"))
        if correction:result.update(correction_of_operation_id=correction,expected_confirmed_total=format(expected_value,".2f"))
        cur.setinputsizes(result_body=oracledb.DB_TYPE_CLOB)
        cur.execute("insert into RRL_LOGISTICS_EXPENSE(OPERATION_ID,PAYLOAD_HASH,ARTICLE_CODE,ARTICLE_VERSION,ARTICLE_NAME,WARE_ID,OBJECT_KIND,OBJECT_ID,AMOUNT,CURRENCY,EXPENSE_DATE,DOCUMENT_REFERENCE,REASON_TEXT,ACTOR,RESULT_JSON,ADJUSTMENT_SIGN,CORRECTION_OF_OP,EXPECTED_CONFIRMED_TOTAL,COST_CORRECTION_OF_OP)values(:op,:hash_value,:code,:version,:name,:ware,:kind,:object_id,:amount,:currency,to_date(:day,'FXYYYY-MM-DD'),:reference,:reason,:actor,:result_body,:sign,:correction,:expected,:cost_correction)",{"op":op,"hash_value":digest,"code":code,"version":article[1],"name":article[0],"ware":ware,"kind":kind,"object_id":object_id,"amount":abs(amount),"currency":currency,"day":day,"reference":reference,"reason":reason,"actor":actor,"result_body":json.dumps(result),"sign":sign,"correction":correction,"expected":expected_value,"cost_correction":cost_correction})
        return result
