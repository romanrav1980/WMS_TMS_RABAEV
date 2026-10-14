exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.inventory.public import build_wave_queue_reads
from app.services.picking_service import PickingService
from fastapi import HTTPException
reader=build_wave_queue_reads()
header=reader.wave(403,"admin",lambda gateway:PickingService(gateway).get_wave_header(403))
assert header["pick_wave_id"]==403 and "orders" not in header
rows=reader.waves("admin",header["ware_id"],lambda gateway,ware:PickingService(gateway).list_waves(ware_id=ware,limit=10))
assert rows and all(row["ware_id"]==header["ware_id"]for row in rows)
try:reader.wave(403,"nonexistent_actor889",lambda gateway:{"UNREACHABLE":True});raise AssertionError("Inactive actor allowed")
except HTTPException as exc:assert exc.status_code==403
try:reader.wave(551,"QA172_KRO",lambda gateway:{"UNREACHABLE":True});raise AssertionError("Foreign view allowed")
except HTTPException as exc:assert exc.status_code==403
print("889 PASS lean existing header/current warehouse list/global admin scoped snapshot; inactive and foreign wave view refused before legacy reader",header["ware_id"],len(rows))
