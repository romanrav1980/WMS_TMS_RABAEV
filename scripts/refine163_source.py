from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=root/"api/wms_api_server/app/modules/transport/infrastructure/plan_preflight.py"
s=p.read_text(encoding="utf-8")
a=s.index('    capacity = native_check')
s=s[:a]+'''    cur.execute("select NUM from RRL_TR_VEHICLE where ID=:id", id=route["vehicle_id"])
    vehicle_row = cur.fetchone()
    current_plate = vehicle_row[0] if vehicle_row else None
    if "vehicle_num" in route and (not route["vehicle_num"] or route["vehicle_num"] != current_plate):
        blockers.append({"code": "PLAN_VEHICLE_ID_PLATE_CONFLICT"})
'''+s[a:]
s=s.replace('"vehicle_id": route["vehicle_id"], "st_numbers": numbers,','"vehicle_id": route["vehicle_id"], "current_vehicle_num": current_plate, "st_numbers": numbers,')
p.write_text(s,encoding="utf-8")
