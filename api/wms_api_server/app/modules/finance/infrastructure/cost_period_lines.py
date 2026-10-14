# Partition one physical load using existing immutable CASE start evidence.
from collections import Counter
from decimal import Decimal
from typing import Any
from ..contracts import LogisticsCostError
from ..domain.amount import cost_amount
from .box_assembly_clocks import box_assembly_clocks


def load_period_lines(cursor: Any, tree: dict[str,Any], boxes: int, load: str, loaded_day: str,
                      ware: int, currency: str, policy: dict[str,Any])->list[dict[str,Any]]:
    counts=Counter({loaded_day:boxes})
    if policy["period_mode"]=="CASE_ASSEMBLY":
        clocks=box_assembly_clocks(cursor,tree,ware,policy["timezone_region"])
        if len(clocks)!=boxes or any(row["state"]!="READY"for row in clocks):
            raise LogisticsCostError("COST_ACTUAL_ASSEMBLY_START_REQUIRED","Каждой коробке нужен достоверный источник начала сборки на этом складе")
        counts=Counter(row["business_date"]for row in clocks)
    # Rate revisions cannot cross a single source calculation while its history is selected.
    cursor.execute("select RATE_KEY from RRL_LOGISTICS_RATE_HEAD where WARE_ID=:ware and CURRENCY=:currency and COST_CODE='WAREHOUSE_PICKING'for update",ware=ware,currency=currency)
    if not cursor.fetchone():
        raise LogisticsCostError("COST_RATE_MISSING","На подтверждённую расчётную дату нет ставки")
    lines=[]
    for day,quantity in sorted(counts.items()):
        cursor.execute("select h.RATE_KEY,h.VERSION_NO,to_char(h.RATE_VALUE,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') "
        "from RRL_LOGISTICS_RATE_HISTORY h join RRL_LOGISTICS_RATE_HEAD r on r.RATE_KEY=h.RATE_KEY "
        "        where r.WARE_ID=:ware and r.CURRENCY=:currency and r.COST_CODE='WAREHOUSE_PICKING' "
        "        and h.EFFECTIVE_FROM<=to_date(:day,'FXYYYY-MM-DD') "
        "        order by h.EFFECTIVE_FROM desc,h.VERSION_NO desc fetch first 1 row only",ware=ware,currency=currency,day=day)
        rate=cursor.fetchone()
        if not rate:
            raise LogisticsCostError("COST_RATE_MISSING","На подтверждённую расчётную дату нет ставки")
        amount=cost_amount(quantity,Decimal(str(rate[2])))
        lines.append({"load_operation_id":load,"rate_key":rate[0],"version":int(rate[1]),"quantity":quantity,
                      "rate":str(rate[2]),"amount":str(amount),"basis":"BOX","cost_code":"WAREHOUSE_PICKING",
                      "rate_date_utc":day if policy["period_mode"]=="LOADED_UTC"else None,"rate_date":day,
                      "period_mode":policy["period_mode"],"period_timezone":policy["timezone_region"],
                      "period_policy_version":policy["version"]})
    return lines
