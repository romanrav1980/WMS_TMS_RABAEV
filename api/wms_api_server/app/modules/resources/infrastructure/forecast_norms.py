"""Existing norm owner: bounded projection for forecast quantities in caller's snapshot."""
import json
from typing import Any
import oracledb
from .workload_config import workload_rows

def forecast_norm_basis(cur: Any,ware: int,scope: str,keys: list[dict[str,Any]]) -> dict[str,Any]:
    if len(keys)>500:
        raise ValueError("FORECAST_NORM_BOUND_500")
    cur.execute("""select SITE_CODE,VERSION_NO,ACTIVE,OPERATION_ID,REASON from RRL_WORKLOAD_SCOPE_SITE
        where WARE_ID=:ware and WORK_SCOPE=:scope order by VERSION_NO desc fetch first 1 rows only""",ware=ware,scope=scope)
    values=workload_rows(cur)
    if not values:
        return {"status":"NO_SCOPE_MAPPING","mapping":None,"norms":[]}
    mapping=values[0]
    if mapping["active"]!=1:
        return {"status":"SCOPE_MAPPING_INACTIVE","mapping":mapping,"norms":[]}
    if not keys:
        return {"status":"MAPPED","mapping":mapping,"norms":[]}
    data=cur.var(oracledb.DB_TYPE_CLOB)
    data.setvalue(0,json.dumps([{"article":r["article"],"base_uom":r["base_uom"]}for r in keys],ensure_ascii=False))
    cur.execute("""select n.ARTICLE,n.BASE_UOM,n.VERSION_NO,n.ACTIVE,n.OPERATION_ID,n.REASON,
        to_char(n.BASE_PER_HOUR,'TM9','NLS_NUMERIC_CHARACTERS=''.,''')BASE_PER_HOUR
        from json_table(:keys,'$[*]'columns(ARTICLE varchar2(160)path '$.article',BASE_UOM varchar2(20)path '$.base_uom')) k
        join RRL_WORKLOAD_NORM n on n.WARE_ID=:ware and n.SITE_CODE=:site and n.ARTICLE=k.ARTICLE and n.BASE_UOM=k.BASE_UOM
        where n.VERSION_NO=(select max(x.VERSION_NO)from RRL_WORKLOAD_NORM x where x.WARE_ID=n.WARE_ID and x.SITE_CODE=n.SITE_CODE and x.ARTICLE=n.ARTICLE and x.BASE_UOM=n.BASE_UOM)
        order by n.ARTICLE,n.BASE_UOM""",keys=data,ware=ware,site=mapping["site_code"])
    return {"status":"MAPPED","mapping":mapping,"norms":workload_rows(cur)}
