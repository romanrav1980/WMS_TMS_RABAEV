"""Bounded immutable review history scoped before reading report contents."""
from datetime import date
from typing import Any
from ...platform.public import read_oracle_json
from ..contracts import LogisticsCostError
from .cost_access import require_warehouse

def history(gateway: Any,ware: int,day: date,region: str,after: int,limit: int,actor: str) -> dict:
    if after<0 or not 1<=limit<=50:
        raise LogisticsCostError("DAY_REVIEW_HISTORY_BOUND","Недопустимая страница журнала.",422)
    with gateway.transaction("Day review bounded history READ ONLY") as cur:
        cur.execute("set transaction read only");require_warehouse(cur,ware,actor,"transport_dispatch_view")
        cur.execute("""select OPERATION_ID,VERSION_NO,ACTOR,SOURCE_HASH,CAPTURED_AT,RECORDED_AT,
            json_value(REQUEST_JSON,'$.reason' returning varchar2(2000))
            from RRL_DAY_REVIEW where WARE_ID=:ware and BUSINESS_DATE=:day and TIMEZONE_REGION=:region and VERSION_NO>:after_version
            order by VERSION_NO fetch first :page_limit rows only""",ware=ware,day=day,region=region,after_version=after,page_limit=limit+1)
        records=cur.fetchall();more=len(records)>limit;records=records[:limit]
        rows=[dict(zip(("operation_id","version","actor","source_hash","captured_at","recorded_at","reason"),row)) for row in records]
        return {"warehouse_id":ware,"business_date":day.isoformat(),"timezone_region":region,"rows":rows,
                "has_more":more,"next_after_version":rows[-1]["version"] if more else None,"consistent_snapshot":True}

def detail(gateway: Any,operation: str,actor: str) -> dict:
    with gateway.transaction("Immutable day review detail READ ONLY") as cur:
        cur.execute("set transaction read only")
        cur.execute("select WARE_ID from RRL_DAY_REVIEW where OPERATION_ID=:operation",operation=operation)
        row=cur.fetchone()
        if row is None:
            raise LogisticsCostError("DAY_REVIEW_NOT_FOUND","Запись сверки не найдена.",404)
        require_warehouse(cur,row[0],actor,"transport_dispatch_view")
        cur.execute("select RESULT_JSON,CAPTURED_AT,RECORDED_AT from RRL_DAY_REVIEW where OPERATION_ID=:operation",operation=operation)
        result,captured,recorded=cur.fetchone()
        return {**read_oracle_json(result),"captured_at":captured,"recorded_at":recorded,"consistent_snapshot":True}
