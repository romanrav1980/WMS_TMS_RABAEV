"""Exact remaining CASE person-hours and merged per-person planned capacity."""
from datetime import datetime,timedelta
from decimal import Decimal,localcontext
from typing import Any

def hours(start: datetime,finish: datetime) -> Decimal:
    span=finish-start
    return Decimal(span.days)*24+Decimal(span.seconds)/3600+Decimal(span.microseconds)/3600000000

def union_hours(spans: list[tuple[datetime,datetime]]) -> Decimal:
    if not spans:return Decimal(0)
    ordered=sorted(spans);total=Decimal(0);begin,end=ordered[0]
    for next_begin,next_end in ordered[1:]:
        if next_begin<=end:end=max(end,next_end)
        else:total+=hours(begin,end);begin,end=next_begin,next_end
    return total+hours(begin,end)

def interval_load(start: datetime,end: datetime,minutes: int,work: list[dict[str,Any]],attendance: list[dict[str,Any]]) -> list[dict[str,Any]]:
    result=[];begin=start;unscheduled=[item["case_pick_line_id"]for item in work if item.get("window")is None]
    with localcontext()as ctx:
        ctx.prec=60
        while begin<end:
            finish=min(begin+timedelta(minutes=minutes),end);required=Decimal(0);blocked=[]
            for item in work:
                window=item.get("window")
                if window is None:continue
                left,right=max(begin,window[0]),min(finish,window[1])
                if right<=left:continue
                if item["base_per_hour"] is None:
                    blocked.append(item["case_pick_line_id"]);continue
                required+=Decimal(item["remaining_quantity"])/Decimal(item["base_per_hour"])*hours(left,right)/hours(*window)
            people: dict[str,list[tuple[datetime,datetime]]]={}
            for plan in attendance:
                left,right=max(begin,plan["start"]),min(finish,plan["finish"])
                if right>left:people.setdefault(plan["person_id"],[]).append((left,right))
            available=sum((union_hours(spans)for spans in people.values()),Decimal(0))
            fmt=lambda value:format(value.quantize(Decimal("0.000000001")),"f")
            result.append({"from_utc":begin.isoformat(),"to_utc":finish.isoformat(),"required_person_hours":None if blocked or unscheduled else fmt(required),
                "known_required_person_hours":fmt(required),"planned_person_hours":fmt(available),"planned_people":len(people),
                "deficit_person_hours":None if blocked or unscheduled else fmt(max(required-available,Decimal(0))),
                "minimum_people_full_interval":None if blocked or unscheduled else int((required/hours(begin,finish)).to_integral_value(rounding="ROUND_CEILING")),
                "missing_norm_line_ids":blocked,"unscheduled_line_ids":unscheduled,"allocation_method":"UNIFORM_WITHIN_EXPLICIT_WAVE_WINDOW"})
            begin=finish
    return result

def outside_view(start: datetime,end: datetime,work: list[dict[str,Any]]) -> list[dict[str,Any]]:
    result=[]
    with localcontext()as ctx:
        ctx.prec=60
        for item in work:
            window=item.get("window")
            if window is None:continue
            overlap=max(Decimal(0),hours(max(start,window[0]),min(end,window[1])))
            fraction=Decimal(1)-overlap/hours(*window)
            if fraction>0:
                value=Decimal(item["remaining_quantity"])*fraction
                result.append({"case_pick_line_id":item["case_pick_line_id"],"pick_wave_id":item["pick_wave_id"],
                    "article":item["article"],"base_uom":item["base_uom"],"estimated_quantity_outside":format(value,"f"),
                    "basis":"UNIFORM_WITHIN_EXPLICIT_WAVE_WINDOW"})
    return result
