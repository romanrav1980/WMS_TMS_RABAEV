"""Calendar exposure and exact advisory quantity; never a stock command."""
from datetime import datetime,timedelta,timezone
from decimal import Decimal,localcontext,ROUND_CEILING
from typing import Any

def history_window(now: datetime,days: int,current: bool) -> tuple[datetime,datetime,Decimal]:
    now=now.astimezone(timezone.utc)
    today=now.replace(hour=0,minute=0,second=0,microsecond=0)
    start=today-timedelta(days=days-1 if current else days)
    end=now if current else today
    elapsed=end-start
    with localcontext() as ctx:
        ctx.prec=60
        exposure=Decimal(elapsed.days)+Decimal(elapsed.seconds)/Decimal(86400)+Decimal(elapsed.microseconds)/Decimal(86400000000)
    return start,end,exposure

def forecast_quantity(series: dict[str,Any],exposure: Decimal,horizon: int,minimum: int,complete: bool) -> dict[str,Any]:
    reason="READY"
    if not complete:
        reason="NEEDS_PROJECTION"
    elif exposure<=0 or series["active_days"]<minimum:
        reason="INSUFFICIENT_ACTIVE_HISTORY"
    elif series["base_scale"] is None:
        reason="BASE_POLICY_REQUIRED"
    with localcontext() as ctx:
        ctx.prec=60
        rate=Decimal(series["observed_quantity"])/exposure if exposure>0 else None
        estimate=(rate*Decimal(horizon)).quantize(Decimal(10)**-int(series["base_scale"]),rounding=ROUND_CEILING) if reason=="READY"and rate is not None else None
        return {**series,"status":reason,"daily_rate":format(rate.quantize(Decimal("0.000000001")),"f")if rate is not None else None,
            "estimated_quantity":format(estimate,"f")if estimate is not None else None,"horizon_days":horizon,"method":"CALENDAR_DAY_MEAN"}
