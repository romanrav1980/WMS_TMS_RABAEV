from pathlib import Path
p=Path("api/wms_api_server/app/modules/finance/infrastructure/reconciliation_sources.py");v=p.read_text(encoding="utf-8")
a='("warehouse_cost_runs","select count(*)from RRL_LOGISTICS_COST_RUN where WARE_ID=:ware and CREATED_AT>=:day_from and CREATED_AT<:day_to")'
b='("warehouse_cost_runs","select count(*)from RRL_LOGISTICS_COST_RUN r where r.WARE_ID=:ware and r.CREATED_AT>=:day_from and r.CREATED_AT<:day_to and not exists(select 1 from RRL_TRANSPORT_COST_CLAIM c where c.OPERATION_ID=r.OPERATION_ID)"),\n ("transport_cost_runs","select count(*)from RRL_LOGISTICS_COST_RUN r join RRL_TRANSPORT_COST_CLAIM c on c.OPERATION_ID=r.OPERATION_ID where r.WARE_ID=:ware and r.CREATED_AT>=:day_from and r.CREATED_AT<:day_to")'
assert a in v;v=v.replace(a,b)
v=v.replace("BACKLOG=[","BACKLOG=[\n (\"transport_cost_unrecognized\",\"select count(*)from RRL_TT_VEHICLE_SOURCE s where exists(select 1 from RRL_TT_HU_LOAD_FACT l where l.TT_ID=s.TT_ID and l.DEPARTURE_OPERATION_ID=s.DEPARTURE_OPERATION_ID and l.WARE_ID=:ware)and not exists(select 1 from RRL_TRANSPORT_COST_CLAIM c where c.DEPARTURE_OPERATION_ID=s.DEPARTURE_OPERATION_ID)\"),")
p.write_text(v,encoding="utf-8")
p=Path("wiki-raw/wms_admin_ui_reference/day-reconciliation.js");v=p.read_text(encoding="utf-8")
v=v.replace('warehouse_cost_runs:"Складских расчётов",','warehouse_cost_runs:"Складских расчётов",transport_cost_runs:"Нормативных транспортных начислений",transport_cost_unrecognized:"Архивные выезды без нормативного транспортного начисления",');p.write_text(v,encoding="utf-8")
print("588 existing day board distinguishes warehouse/transport recognition and unrecognised archived departures.")
