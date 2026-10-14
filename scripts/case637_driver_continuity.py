import sys
from pathlib import Path
sys.path.insert(0,str(Path("api/wms_api_server").resolve()))
from app.modules.transport.domain.driver_day import planned_day_continuity
def op(key,code,start,end):
 return {"operation_id":key,"operation_code":code,"plan_start_at":start,"plan_end_at":end}
begin,end="2026-10-12T00:00:00+04:00","2026-10-13T00:00:00+04:00"
# Distinct trips remain one driver's chain: 90 + unloading10 + drive40 =130.
chain=[op(1,"DRIVE","2026-10-12T08:00:00+04:00","2026-10-12T09:30:00+04:00"),op(2,"UNLOAD","2026-10-12T09:30:00+04:00","2026-10-12T09:40:00+04:00"),op(3,"DRIVE_BACK","2026-10-12T09:40:00+04:00","2026-10-12T10:20:00+04:00")]
value=planned_day_continuity(chain,begin,end);assert value["violations"][0]["continuous_min"]=="130.0"
# Explicit 15 minute REST resets; work does not.
rest=[chain[0],op(2,"REST","2026-10-12T09:30:00+04:00","2026-10-12T09:45:00+04:00"),op(3,"DRIVE_BACK","2026-10-12T09:45:00+04:00","2026-10-12T10:25:00+04:00")]
assert not planned_day_continuity(rest,begin,end)["violations"]
# Midnight is not a break. Prior recorded120 plus current30 remains150.
night=[op(4,"DRIVE","2026-10-11T22:00:00+04:00","2026-10-12T00:00:00+04:00"),op(5,"DRIVE_BACK","2026-10-12T00:00:00+04:00","2026-10-12T00:30:00+04:00")]
assert planned_day_continuity(night,begin,end)["violations"][0]["continuous_min"]=="150.0"
# The next day's part cannot inflate today's observed continuity.
cross=[op(6,"DRIVE","2026-10-12T22:00:00+04:00","2026-10-13T00:30:00+04:00")]
assert not planned_day_continuity(cross,begin,end)["violations"]
assert planned_day_continuity(chain+[chain[0]],begin,end)==value
assert value["initial_continuity_verified"]is False and value["legal_compliance_verified"]is False
print("PASS637 cross-trip130/work-not-rest/REST15/midnight150/end-boundary120/dedup/no legal admission")
