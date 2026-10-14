from pathlib import Path
import json
f={}
p=Path("api/wms_api_server/app/modules/inventory/public.py");s=p.read_text(encoding="utf-8")
s+="\nfrom .infrastructure.shipping_temperature_read import read_shipping_temperature_requirements\n"
f[str(p)]=s
p=Path("api/wms_api_server/app/modules/transport/infrastructure/plan_preflight.py");s=p.read_text(encoding="utf-8")
s=s.replace("from .preflight_scope import dispatcher","from .preflight_scope import dispatcher\nfrom ...inventory.public import read_shipping_temperature_requirements")
s=s.replace('cur.execute("select NUM from RRL_TR_VEHICLE where ID=:id",','cur.execute("select NUM,REF_REJIM from RRL_TR_VEHICLE where ID=:id",',1)
needle='    capacity = native_check(cur, route["vehicle_id"], numbers, 0)'
new='''    try:
        thermal = read_shipping_temperature_requirements(cur, [int(row["id"]) for row in selected], actor)
    except PermissionError as exc:
        raise TransportPlanError("PLAN_THERMAL_CURRENT_SCOPE_REQUIRED", str(exc), 403) from exc
    except ValueError as exc:
        raise TransportPlanError("PLAN_THERMAL_READ_REJECTED", str(exc), 409) from exc
    thermal["vehicle_legacy_mode"] = vehicle_row[1] if vehicle_row else None
'''
# route_result needs the existing authenticated actor passed explicitly.
s=s.replace("rows: list[dict[str, Any]], trip: int | None) -> dict[str, Any]:","rows: list[dict[str, Any]], trip: int | None, actor: str) -> dict[str, Any]:",1)
s=s.replace(needle,new+needle,1)
s=s.replace('"source_blockers": blockers, "capacity_and_type": capacity,','"source_blockers": blockers, "capacity_and_type": capacity, "temperature_requirements": thermal,')
s=s.replace('["AWARE_TIME_SCHEDULE", "DRIVER_AND_BREAKS", "WAREHOUSE_RELEASE_AND_LOADING"]','["AWARE_TIME_SCHEDULE", "DRIVER_AND_BREAKS", "WAREHOUSE_RELEASE_AND_LOADING", "VEHICLE_TEMPERATURE_RANGE_AND_FACT"]')
# Observed two route_result consumers in the same implementation.
s=s.replace("route_result(cur, route, sources, None)","route_result(cur, route, sources, None, actor)")
s=s.replace('route_result(cur, {"vehicle_id": header[4], "stops": numbers}, sources, trip)','route_result(cur, {"vehicle_id": header[4], "stops": numbers}, sources, trip, actor)')
f[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/customer-orders.js");s=p.read_text(encoding="utf-8")
needle=" const warnings=capacity?.warnings||[];"
s=s.replace(needle,needle+'''
 const thermal=route?.temperature_requirements;
 const thermalNote=thermal?(
  thermal.ranges_conflict?' Температурные диапазоны товаров несовместимы.':
  thermal.all_ranges_configured?' Текущие складские диапазоны товара: от '+(thermal.common_min_c??'не задано')+' до '+(thermal.common_max_c??'не задано')+' °C.':
  ' Температурные диапазоны части товаров не настроены; это не означает отсутствие требований.')+
  ' Режим машины: '+(thermal.vehicle_legacy_mode||'не задан')+'. Его название не подтверждает допустимый диапазон или фактическую температуру.':'';
''')
s=s.replace("  (warnings.length?' '+warnings.join('; '):'')+","  (warnings.length?' '+warnings.join('; '):'')+thermalNote+")
f[str(p)]=s
p=Path("wiki/components/nicora_ni022_source_layout_20261011.md");f[str(p)]=p.read_text(encoding="utf-8")+"\n1140: prepared sameREADONLY originalTMSpreflight adds existingwarehouseSKU TEMP_MIN/MAX via inventorypublic/currentrole+WARE, bounded1000SKU/5000memberIDs. Existingvehicle REF_REJIM returned as legacylabel only, notnumericenvelope/measurement. Exactcommonrange/conflict/missingconfiguration visible; physical/temperatureadmission staysfalse. No newcoldpolicy/writer/DDL/nativeassignmentchanged; runtimepending.\n"
p=Path("wiki/index.md");f[str(p)]="- [NI02.2 thermal requirements1140](components/nicora_ni022_source_layout_20261011.md): prepared existing SKU ranges/current scope/legacy vehicle label; no invented temperature admission.\n"+p.read_text(encoding="utf-8")
p=Path("wiki/log.md");f[str(p)]=p.read_text(encoding="utf-8")+"\n- 2026-10-13 /1140: existingthermalcontracts1138/1139 found warehouse SKU range +legacyREF_REJIM(cold/hot/text0/1/corruptlabels), no numericvehicleproof. Implemented prepared scopedinventorypublic reader +existingTMSpreflight/UI range/conflict/unknown information, sameREADONLY snapshot. NoDDL/nativewrite change; runtimepending.1137 removed ellipsis checker falsepositive without relaxing encodinggate.\n"
print(json.dumps(f,ensure_ascii=True))
