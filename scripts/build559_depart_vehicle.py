import json
from pathlib import Path
folder="db/migrations/2026-10-12_ni071_vehicle_source/"
v=Path(folder+"000_before_depart.sql").read_text(encoding="utf-8")
def change(a,b):
 global v
 assert v.count(a)==1,(a,v.count(a));v=v.replace(a,b)
change("RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TR_VEHICLE',RRL_STOCK_PLAN_HELPER.decimal_text(vehicle_no));","RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TR_VEHICLE',RRL_STOCK_PLAN_HELPER.decimal_text(vehicle_no));\n  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TR_VODITEL',RRL_STOCK_PLAN_HELPER.decimal_text(tt.VODITEL_ID));\n  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TT_VEHICLE_SOURCE',RRL_STOCK_PLAN_HELPER.decimal_text(trip_no));")
change("dock_name varchar2(50);promise_wire clob;","dock_name varchar2(50);promise_wire clob;depart_instant timestamp with time zone;")
change("select count(*) into n from RRL_TR_VODITEL where ID=tt.VODITEL_ID;","select ID into n from RRL_TR_VODITEL where ID=tt.VODITEL_ID and nvl(DELETED,0)=0 for update;\n  n:=1;")
change("for ld in(select ID from json_table(load_ids", "depart_instant:=systimestamp;\n  for ld in(select ID from json_table(load_ids")
change("DEPARTED_AT=systimestamp","DEPARTED_AT=depart_instant")
change("j.put('operation_id',op);j.put('task_id',trip_no);","RRL_VEH_DEPART_SOURCE.capture_source(op,trip_no,vehicle_no,depart_instant);\n  j.put('operation_id',op);j.put('task_id',trip_no);")
print(json.dumps({folder+"004_depart_command.sql":v}))
