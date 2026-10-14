import json
from pathlib import Path
import httpx
c=json.loads(Path("tmp/context519.json").read_text(encoding="utf-8"))
with httpx.Client(auth=("admin","admin123"),timeout=35)as h:
 base="http://127.0.0.1:8088/api/finance/logistics-costs/trips/"+str(c["trip"])
 r=h.get(base+"/transport-tariff-sources",params={"warehouse_id":c["warehouse"]})
 assert r.status_code==200 and r.json()["selection_state"]=="TARIFF_SOURCE_MISSING",r.text
 r=h.get(base+"/assembly-period",params={"warehouse_id":c["warehouse"],"timezone_region":"UTC"})
 assert r.status_code==200 and r.json()["complete"]and r.json()["lines"][0]["source_kind"]=="BOX_PACKING",r.text
 r=h.get(base);assert r.status_code==200 and r.json()["summary"]["currency_totals"]==[dict(currency="GEL",original_amount="2.25")],r.text
print("PASS528 current API: ordinaryBOX native assembly source/2.25 recognized summary/legacy tariff missing explicit, no price/stock writes.")
