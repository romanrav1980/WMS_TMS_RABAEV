from pathlib import Path
import json
out={}
for side in["a","b"]:
 s=Path("scripts/continue230_to_store.py").read_text(encoding="utf-8").replace("context230.json","context241"+side+".json").replace("IW230","IW241"+side.upper()).replace("QI230","QI241").replace("Own230","Own241").replace("READY230","READY241")
 s=s.replace('"transport_task_id":ctx["target_trip"],"scan_vehicle":"QL"+tag','"transport_task_id":ctx["target_trip"],"scan_vehicle":ctx["target_vehicle_number"]')
 depart=' api("POST",f"/api/transport/loading/{ctx[\'target_trip\']}/depart",{"operation_id":"IW241'+side.upper()+'.DEPART:"+tag})'
 if side=="a":
  addition=''' result=api("GET",f"/api/inventory/interwarehouse/trips/{ctx['target_trip']}/incoming");assert result["expected_deliveries"]==2 and result["ready_deliveries"]==1 and not result["incoming_ready"]and not result["departure_authorized"],result
 denied=api("POST",f"/api/transport/loading/{ctx['target_trip']}/depart",{"operation_id":"IW241A.EARLY:"+tag},409);assert "DEPART_EXPECTED_INTERWARE_CARGO_NOT_READY"in json.dumps(denied),denied
 print("PASS241 first source loaded/second not received/both original promises remain/target departure blocked/count2-ready1/no new quantity")
'''
 else:
  addition=''' result=api("GET",f"/api/inventory/interwarehouse/trips/{ctx['target_trip']}/incoming");assert result["expected_deliveries"]==2 and result["ready_deliveries"]==2 and result["incoming_ready"]and not result["departure_authorized"],result
 assert len(result["expected_quantities"])==2 and all(x["quantity"]=="3" for x in result["expected_quantities"])
 q.execute("select MAX_WEIGHT_KG,PALLETS from RRL_TR_VEHICLE where NUM=:plate",plate=ctx["target_vehicle_number"]);assert q.fetchone()==(200,2)
'''+depart+'''
 q.execute("select count(*),sum(PHYSICAL_PLACES),sum(GROSS_WEIGHT_KG)from RRL_TT_HU_LOAD_FACT where TT_ID=:tt and STATUS='DEPARTED'",tt=ctx["target_trip"]);assert q.fetchone()==(2,2,20)
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=6667491");assert q.fetchone()==(20,20)
 print("PASS241 two independent sources/one existing target TT/2 separate physical pallets/2SKU totals3each/current promises2-ready2/native capacities200kg2places unchanged/QC12/original loading-depart/each3 same units6codes/no repeated customer fulfillment/protected20-20")
'''
 assert depart in s,side;s=s.replace(depart,addition,1)
 out["scripts/continue241"+side+".py"]=s
print(json.dumps(out,ensure_ascii=True))
