from pathlib import Path
import json
f={};root="db/migrations/2026-10-14_ni052_loading_floor/"
p=Path(root+"002_floor_api.sql");s=p.read_text(encoding="utf-8")
point=" procedure assert_load(p_vehicle"
s=s.replace(point," function planning_counts(p_vehicle number,p_sts clob,p_base_counts clob,p_unknown number)return clob;\n"+point,1)
point=" procedure assert_load(p_vehicle"
# The previous insertion only touched spec; insert implementation before second occurrence.
helper=""" function planning_counts(p_vehicle number,p_sts clob,p_base_counts clob,p_unknown number)return clob is
  numbers json_array_t:=json_array_t.parse(p_sts);base_counts json_array_t:=json_array_t.parse(p_base_counts);wire_counts json_array_t:=json_array_t();
  entry_value json_object_t;result json_object_t:=json_object_t();el json_element_t;
  query_value varchar2(32767);cursor_no integer;ran integer;rc sys_refcursor;load_id varchar2(100);type_id number;vehicle_id number;floor_vehicle number;
  unknown_no number:=p_unknown;load_count number:=0;st_value varchar2(100);key_value varchar2(100);
  type count_map is table of number index by varchar2(100);counts count_map;
 begin
  if numbers.get_size<1 or numbers.get_size>200 or base_counts.get_size>200 then raise_application_error(-20881,'PLAN_FLOOR_SOURCE_BOUND_200');end if;
  for i in 0..base_counts.get_size-1 loop
   entry_value:=treat(base_counts.get(i) as json_object_t);key_value:=to_char(entry_value.get_number('pallet_type_id'),'TM9');
   counts(key_value):=entry_value.get_number('places');
  end loop;
  query_value:='select /* PLAN_LOADED_TOP_BOUND1197 */ l.LOAD_OPERATION_ID,f.PALLET_TYPE_ID,l.VEHICLE_ID,f.VEHICLE_ID from RRL_TT_HU_LOAD_FACT l left join RRL_TT_LOAD_FLOOR_FACT f on f.LOAD_OPERATION_ID=l.LOAD_OPERATION_ID where l.STATUS=''LOADED''and l.LOAD_OPERATION_ID in(select m.LOAD_OPERATION_ID from RRL_TT_HU_LOAD_ST m join RRL_SBORKA_PALLETS p on p.ID=m.SBORKA_PALLET_ID where m.ACTIVE_FLAG=1 and p.ST_NUMBER in(';
  for i in 0..numbers.get_size-1 loop
   if i>0 then query_value:=query_value||',';end if;query_value:=query_value||':st'||to_char(i,'FM999');
  end loop;
  query_value:=query_value||'))order by l.LOAD_OPERATION_ID fetch first 201 rows only';
  cursor_no:=dbms_sql.open_cursor;dbms_sql.parse(cursor_no,query_value,dbms_sql.native);
  for i in 0..numbers.get_size-1 loop
   el:=numbers.get(i);
   if not el.is_string then raise_application_error(-20886,'PLAN_FLOOR_ST_REQUIRED');end if;
   st_value:=numbers.get_string(i);
   if st_value is null then raise_application_error(-20886,'PLAN_FLOOR_ST_REQUIRED');end if;
   dbms_sql.bind_variable(cursor_no,':st'||to_char(i,'FM999'),st_value);
  end loop;
  ran:=dbms_sql.execute(cursor_no);rc:=dbms_sql.to_refcursor(cursor_no);cursor_no:=null;
  loop
   fetch rc into load_id,type_id,vehicle_id,floor_vehicle;exit when rc%notfound;
   load_count:=load_count+1;
   if load_count>200 then raise_application_error(-20881,'PLAN_FLOOR_LOADED_BOUND_200');end if;
   if vehicle_id!=p_vehicle then raise_application_error(-20886,'PLAN_FLOOR_LOADED_VEHICLE_CONFLICT');end if;
   if type_id is null or floor_vehicle!=p_vehicle then unknown_no:=unknown_no+1;
   else
    key_value:=to_char(type_id,'TM9');
    if counts.exists(key_value)then counts(key_value):=counts(key_value)+1;else counts(key_value):=1;end if;
   end if;
  end loop;close rc;
  key_value:=counts.first;
  while key_value is not null loop
   entry_value:=json_object_t();entry_value.put('pallet_type_id',to_number(key_value));entry_value.put('places',counts(key_value));wire_counts.append(entry_value);
   key_value:=counts.next(key_value);
  end loop;
  result.put('counts',wire_counts);result.put('unconfirmed_places',unknown_no);return result.to_clob;
 exception when others then
  if cursor_no is not null then if dbms_sql.is_open(cursor_no)then dbms_sql.close_cursor(cursor_no);end if;end if;
  if rc%isopen then close rc;end if;raise;
 end;
"""
pos=s.find(point,s.find("create or replace package body"));assert pos>=0;s=s[:pos]+helper+s[pos:]
f[str(p)]=s
s=Path(root+"000_rrl_transport_plan_rules_body.sql").read_text(encoding="utf-8")
s=s.replace("floor_value json_object_t;","floor_value json_object_t;loaded_floor json_object_t;",1)
old="prepared_floor_counts(p_sts,floor_counts,unknown_places);unknown_places:=unknown_places+actual_places;"
new="""prepared_floor_counts(p_sts,floor_counts,unknown_places);
    loaded_floor:=json_object_t.parse(RRL_STOCK_LOAD_FLOOR.planning_counts(p_vehicle_id,p_sts,floor_counts,unknown_places));
    floor_counts:=loaded_floor.get_array('counts').to_clob;unknown_places:=loaded_floor.get_number('unconfirmed_places');"""
assert old in s;s=s.replace(old,new,1);f[root+"007_plan_loaded_top.sql"]=s
f[root+"apply_loaded_top.sql"]="@@002_floor_api.sql\n@@007_plan_loaded_top.sql\nalter package RRL_TRANSPORT_PLAN_API compile body;\n/\nalter package RRL_STOCK_HU_LOAD_CORE compile body;\n/\nalter package RRL_STOCK_TRIP_DEPART_CMD compile body;\n/\n"
p=Path(root+"apply.sql");f[str(p)]=p.read_text(encoding="utf-8")+"@@007_plan_loaded_top.sql\nalter package RRL_TRANSPORT_PLAN_API compile body;\n/\n"
p=Path("wiki/database/nicora_ni052_loading_floor_20261014.md");f[str(p)]=p.read_text(encoding="utf-8")+"\n1197: final planning merges typed prepared places with selected immutable physical LOAD TOP proofs, once per LOAD operation rather than per ST/CASE; old LOADED without proof stays unknown. Bounded200ST/200physical TOP, loaded lookup uses bindIN. Application/typed read-through verification next; physical1195/1196 already passed on private33637, oneTOP/two nodes/3EA/outerrollback/replay/depart/no repeated stock.\n"
p=Path("wiki/index.md");f[str(p)]="- [Physical1195–1197](database/nicora_ni052_loading_floor_20261014.md): actual33637 one typed TOP/rollback/replay/depart; shared planned loaded TOP merge prepared.\n"+p.read_text(encoding="utf-8")
p=Path("wiki/log.md");f[str(p)]=p.read_text(encoding="utf-8")+"\n- 2026-10-14 /1197: physical LOAD floor proof installed1192; fixed Oracle JSON methods in INSERT1195, retained same fixture after rollback, corrected quantity read to SUM(allcells), loaded1195/depart1196 actual33637/oneTOP/type1/P0H0/protectedP20H20; current UI typed row. Prepared shared planner typed LOAD merge, not newallocator.\n"
print(json.dumps(f))
