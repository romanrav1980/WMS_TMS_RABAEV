"""Publish bounded versions through the existing-source native finance owner."""
import json
from typing import Any
import oracledb
from ...platform.public import read_oracle_json
from ..contracts import LogisticsCostError
from .cost_access import require_warehouse


def publish_transport_norm(gateway: Any,body: dict[str,Any],actor: str)->dict[str,Any]:
    try:
        with gateway.transaction("Publish immutable existing transport tariff norm")as cursor:
            result=cursor.var(oracledb.DB_TYPE_CLOB)
            cursor.callproc("RRL_TRANSPORT_NORM_API.publish",[
                json.dumps(body,sort_keys=True,separators=(",",":"),ensure_ascii=False),actor,result])
            return read_oracle_json(result.getvalue())
    except oracledb.DatabaseError as exc:
        code=getattr(exc.args[0],"code",0)
        if 20800<=code<=20999:
            raise LogisticsCostError("TRANSPORT_NORM_REJECTED",str(exc.args[0]).split("\n",1)[0],403 if code==20882 else 409)from exc
        if code in(1841,1843,1861,1882):
            raise LogisticsCostError("TRANSPORT_NORM_PERIOD_INVALID","Некорректная дата или часовой пояс",422)from exc
        raise


def transport_norm_history(gateway: Any,ware: int,price_id: int,before: int|None,limit: int,
                           actor: str)->dict[str,Any]:
    if not 1<=limit<=100 or price_id<1 or before is not None and before<1:
        raise LogisticsCostError("TRANSPORT_NORM_HISTORY_BOUND","Не более 100 версий, корректный исходный тариф",422)
    with gateway.transaction("Read published transport norm history")as cursor:
        cursor.execute("set transaction read only")
        require_warehouse(cursor,ware,actor,"transport_dispatch_view")
        cursor.execute("""select VERSION_NO,ACTOR,to_char(CREATED_AT,'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM'),
        REQUEST_JSON,RESULT_JSON from RRL_TRANSPORT_NORM_HISTORY where WARE_ID=:ware and SOURCE_PRICE_ID=:price_id
        and(:before_version is null or VERSION_NO<:before_version)order by VERSION_NO desc fetch first :bound rows only""",
                       ware=ware,price_id=price_id,before_version=before,bound=limit+1)
        rows=cursor.fetchall();has_more=len(rows)>limit;items=[]
        for version,actor_id,created,request,result in rows[:limit]:
            body=read_oracle_json(request)
            items.append({"version":version,"actor":actor_id,"created_at":created,
                          "reason":body["reason"],"decision_reference":body["decision_reference"],
                          "norm":read_oracle_json(result)})
        return {"warehouse_id":ware,"source_price_id":price_id,"items":items,"has_more":has_more,
                "next_before_version":items[-1]["version"]if has_more else None,"cost_posted":False}
