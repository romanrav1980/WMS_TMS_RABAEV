"""One Oracle transaction; existing plan/native trip/member writers, no stock posting."""
from datetime import date
from typing import Any
import oracledb
from ...platform.public import read_oracle_json

from ..contracts_plan import TransportPlanError

def apply_existing_plan(gateway: Any,plan: int,shipment_day: date,dock: str|None,actor: str) -> dict[str,Any]:
    try:
        with gateway.transaction("Atomic existing transport plan application")as cur:
            result=cur.var(oracledb.DB_TYPE_CLOB)
            cur.callproc("RRL_TRANSPORT_PLAN_API.apply_plan",[plan,shipment_day,dock,actor,result])
            return read_oracle_json(result.getvalue())
    except oracledb.DatabaseError as exc:
        code=getattr(exc.args[0],"code",0)
        if code==1403:raise TransportPlanError("PLAN_CURRENT_SOURCE_NOT_FOUND","План, машина или СТ отсутствует",404) from exc
        if 20800<=code<=20999:raise TransportPlanError("PLAN_APPLICATION_REJECTED",str(exc.args[0]).split("\n",1)[0],403 if code==20882 else 409) from exc
        raise TransportPlanError("PLAN_APPLICATION_UNCONFIRMED","Повторите применение того же плана с исходными параметрами",503) from exc

def assign_validated_sts(gateway: Any,trip: int,numbers: list[str],actor: str) -> dict[str,Any]:
    import json
    selected=sorted(set(numbers))
    if not 1<=len(selected)<=200:raise TransportPlanError("PLAN_SELECT_1_200_STS","Выберите от1 до200 СТ")
    try:
        with gateway.transaction("Shared manual transport plan validation and ST assignment")as cur:
            result=cur.var(oracledb.DB_TYPE_CLOB)
            cur.callproc("RRL_TRANSPORT_PLAN_API.assign_sts",[trip,json.dumps(selected,ensure_ascii=False),actor,result])
            return read_oracle_json(result.getvalue())
    except oracledb.DatabaseError as exc:
        code=getattr(exc.args[0],"code",0)
        if code==1403:raise TransportPlanError("PLAN_CURRENT_SOURCE_NOT_FOUND","Действующий рейс, машина или СТ отсутствует",404) from exc
        if 20800<=code<=20999:raise TransportPlanError("PLAN_ASSIGNMENT_REJECTED",str(exc.args[0]).split("\n",1)[0],403 if code==20882 else 409) from exc
        raise TransportPlanError("PLAN_ASSIGNMENT_UNCONFIRMED","Повторите назначение того же набора СТ",503) from exc
