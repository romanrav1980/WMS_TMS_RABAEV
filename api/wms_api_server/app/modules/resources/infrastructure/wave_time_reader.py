"""Resolve only approved aware windows that still match the original wave."""
from datetime import datetime
from typing import Any
from .workload_config import workload_rows

def approved_wave_windows(cur: Any,warehouse: int) -> dict[int,dict[str,Any]]:
    cur.execute("""select p.WAVE_ID,p.VERSION_NO,
        case when w.WARE_ID=p.WARE_ID and nvl(w.ROUTE_ID,-1)=nvl(p.ROUTE_ID,-1) and nvl(w.DOCK_ID,-1)=nvl(p.DOCK_ID,-1)
          and w.PLANNED_START_AT=p.LEGACY_START_AT and w.PLANNED_FINISH_AT=p.LEGACY_FINISH_AT then 1 else 0 end MATCHES,
        to_char(p.START_AT at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM')START_AT,
        to_char(p.FINISH_AT at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM')FINISH_AT
        from RRL_WAVE_TIME_PLAN p join RRL_PICK_WAVE w on w.PICK_WAVE_ID=p.WAVE_ID
        where w.WARE_ID=:ware and w.STATUS not in('DONE','CANCELLED')
          and p.VERSION_NO=(select max(x.VERSION_NO)from RRL_WAVE_TIME_PLAN x where x.WAVE_ID=p.WAVE_ID)
        order by p.WAVE_ID fetch first 1001 rows only""",ware=warehouse)
    rows=workload_rows(cur)
    from ..contracts_workload import WorkloadError
    if len(rows)>1000:raise WorkloadError("WAVE_TIME_READ_BOUND_1000","Сузьте состав активных волн")
    return {int(row["wave_id"]):{"version":int(row["version_no"]),
        "status":"APPROVED" if row["matches"] else "LEGACY_PLAN_CHANGED",
        "window":(datetime.fromisoformat(row["start_at"]),datetime.fromisoformat(row["finish_at"])) if row["matches"] else None}
        for row in rows}
