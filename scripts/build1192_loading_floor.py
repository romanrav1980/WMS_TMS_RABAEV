from pathlib import Path
import json
f={};root="db/migrations/2026-10-14_ni052_loading_floor/"
p=Path(root+"002_floor_api.sql");s=p.read_text(encoding="utf-8")
s=s.replace("procedure assert_load(p_snapshot clob,p_vehicle number,p_trip number,p_frozen clob)","procedure assert_load(p_vehicle number,p_trip number,p_frozen clob)")
s=s.replace("rows_value json_array_t:=json_array_t();current_value json_object_t;current_wire clob;n number;capacity_wire clob;",
"rows_value json_array_t:=json_array_t();current_value json_object_t;current_wire clob;n number;capacity_wire clob;frozen json_object_t;tree json_object_t:=json_object_t();node_value json_object_t:=json_object_t();nodes json_array_t:=json_array_t();")
old="  current_value:=compile_load(p_snapshot,p_vehicle,rows_value);"
new="""  if p_frozen is null then
   current_value:=current_matrix(p_vehicle);
   if current_value is not null then raise_application_error(-20890,'CLOSURE_CHANGED: new load floor profile');end if;
   return;
  end if;
  frozen:=json_object_t.parse(p_frozen);tree.put('root',frozen.get_string('root'));tree.put('warehouse',frozen.get_number('warehouse'));
  node_value.put('uid',frozen.get_string('root'));node_value.put('depth',0);
  if frozen.get_string('type_origin')='CASE_TYPE'then
   node_value.put('kind','CASE');node_value.put('case_task_id',to_number(frozen.get_string('source_reference')));
  else node_value.put('kind','CONTAINER');end if;
  nodes.append(node_value);tree.put('nodes',nodes);
  current_value:=compile_load(tree.to_clob,p_vehicle,rows_value);"""
assert old in s;s=s.replace(old,new,1);f[str(p)]=s
s=Path(root+"000_rrl_stock_hu_load_core_body.sql").read_text(encoding="utf-8")
s=s.replace("thermal_value json_object_t;","thermal_value json_object_t;floor_value json_object_t;",1)
point="  p_domain:=json_object_t();";assert s.count(point)==1
s=s.replace(point,"  floor_value:=RRL_STOCK_LOAD_FLOOR.compile_load(p_snapshot,veh.ID,r);\n"+point,1)
point="  if thermal_value is null then"
s=s.replace(point,"  if floor_value is null then p_domain.put_null('floor_at_loading');else p_domain.put('floor_at_loading',floor_value);end if;\n"+point,1)
s=s.replace("dock_name varchar2(50):=j.get_string('dock');thermal_wire clob;thermal_element json_element_t;",
"dock_name varchar2(50):=j.get_string('dock');thermal_wire clob;thermal_element json_element_t;floor_wire clob;floor_element json_element_t;",1)
point="  select count(*),nvl(sum(GROSS_WEIGHT_KG),0) into places,mass_no"
s=s.replace(point,"  if j.has('floor_at_loading')then floor_element:=j.get('floor_at_loading');if not floor_element.is_null then floor_wire:=floor_element.to_clob;end if;end if;\n  RRL_STOCK_LOAD_FLOOR.assert_load(vehicle_no,trip_no,floor_wire);\n"+point,1)
s=s.replace("or places+1>veh.PALLETS or","or(floor_wire is null and places+1>veh.PALLETS)or",1)
point="  if j.has('temperature_at_loading')then thermal_element:=j.get('temperature_at_loading');if not thermal_element.is_null then RRL_STOCK_LOAD_THERMAL.persist_confirmation"
assert point in s;s=s.replace(point,"  if j.has('floor_at_loading')then thermal_element:=j.get('floor_at_loading');if not thermal_element.is_null then RRL_STOCK_LOAD_FLOOR.persist_confirmation(p_operation,thermal_element.to_clob,p_actor);end if;end if;\n"+point,1)
f[root+"003_load_core.sql"]=s
s=Path(root+"000_rrl_stock_trip_depart_cmd_body.sql").read_text(encoding="utf-8")
s=s.replace("thermal_value json_object_t;","thermal_value json_object_t;floor_wire clob;",1)
point="  RRL_STOCK_LOAD_THERMAL.compile_confirmation("
s=s.replace(point,"  floor_wire:=RRL_STOCK_LOAD_FLOOR.checked_trip(trip_no,vehicle_no);\n  if floor_wire is null then v.put_null('floor_at_departure');else v.put('floor_at_departure',json_object_t.parse(floor_wire));end if;\n"+point,1)
s=s.replace("thermal_element json_element_t;thermal_wire clob;","thermal_element json_element_t;thermal_wire clob;floor_wire clob;floor_element json_element_t;",1)
point="  select nvl(MIN_PALLET_LOAD,0) into minimum_no"
s=s.replace(point,"  if v.has('floor_at_departure')then floor_element:=v.get('floor_at_departure');if not floor_element.is_null then floor_wire:=floor_element.to_clob;end if;end if;\n  RRL_STOCK_LOAD_FLOOR.assert_departure(trip_no,vehicle_no,floor_wire);\n"+point,1)
s=s.replace("or places>veh.PALLETS or","or(floor_wire is null and places>veh.PALLETS)or",1)
point="  if thermal_wire is not null then j.put('temperature_at_departure'"
assert point in s;s=s.replace(point,"  if floor_wire is not null then j.put('floor_at_departure',json_object_t.parse(floor_wire));end if;\n"+point,1)
f[root+"004_depart_command.sql"]=s
f[root+"006_ledger.sql"]="""merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-14-1191-loading-floor' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Immutable physical TOP tare proof in same Root loading transaction and current normative departure check; no child count multiplication',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
"""
f[root+"apply.sql"]="@@001_schema.sql\n@@002_floor_api.sql\n@@003_load_core.sql\n@@004_depart_command.sql\n@@005_guard.sql\n@@006_ledger.sql\n"
f[root+"rollback.sql"]="begin\n raise_application_error(-20863,'Forward-only: removing physical floor guard requires retained facts/currentscope recovery; do not restore unprotected load/depart bodies');\nend;\n/\n"
f[root+"verify.sql"]="select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME in('RRL_STOCK_LOAD_FLOOR','RRL_STOCK_HU_LOAD_CORE','RRL_STOCK_TRIP_DEPART_CMD','RRL_LOAD_FLOOR_FACT_GUARD');\nselect OBJECT_NAME,OBJECT_TYPE,STATUS from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_LOAD_FLOOR','RRL_STOCK_HU_LOAD_CORE','RRL_STOCK_TRIP_DEPART_CMD','RRL_LOAD_FLOOR_FACT_GUARD');\n"
p=Path("wiki/database/retailcase_ni052_loading_floor_20261014.md");f[str(p)]=p.read_text(encoding="utf-8")+"\n1192: implementation prepared in captured core/depart owners and private physical-floor helper. Schema empty additive; paired rollback refuses to disable retained guard/facts and requires forward correction. Compile source excludes current load counts: concurrent independent roots on same vehicle can be rechecked against latest capacity rather than falsely marked stale. Before effect assert uses current matrix/type/book under CFG/vehicle fence; old untyped pending plan refuses new matrix. Application/physical result pending.\n"
p=Path("wiki/index.md");f[str(p)]="- [Prepared1192: физический TOP/type](database/retailcase_ni052_loading_floor_20261014.md): same Root immutable proof/vehicle-lock normative check/departure; no child multiplication, not yet applied.\n"+p.read_text(encoding="utf-8")
p=Path("wiki/log.md");f[str(p)]=p.read_text(encoding="utf-8")+"\n- 2026-10-14 /1192: prepared physical TOP typed proof/native load+depart check, captured1191/case or HELD HU tare/no default STOCK type; no new stock writer. Apply next; one focused retained/private case, no broad factories.\n"
print(json.dumps(f))
