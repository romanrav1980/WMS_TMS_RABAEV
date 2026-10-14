from pathlib import Path
import json
p=Path("db/migrations/2026-10-11_ni081_trip_time/002_api.sql");s=p.read_text(encoding="utf-8")
needle="  select count(*)into n from RRL_TT_OPERATIONS where TT_ID=v_trip and(PLAN_START"
assert s.count(needle)==1
s=s.replace(needle,"  if w.SHIPMENT_DATE is null or w.SHIPMENT_TIME is null or v_start!=trunc(w.SHIPMENT_DATE)+(w.SHIPMENT_TIME-trunc(w.SHIPMENT_TIME))then raise_application_error(-20886,'TT_TIME_CHAIN_DEPARTURE_CHANGED');end if;\n"+needle)
print(json.dumps({str(p):s},ensure_ascii=True))
