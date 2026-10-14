from pathlib import Path
import json
f={};root="db/migrations/2026-10-14_ni022_vehicle_floor_rule/"
p=Path(root+"000_rrl_vehicle_profile_api_spec.sql");s=p.read_text(encoding="utf-8")
point="end;"
assert s.count(point)==1;s=s.replace(point," function check_floor_capacity(p_vehicle number,p_counts clob,p_unknown number)return clob;\n"+point,1)
f[root+"001_profile_spec.sql"]=s
s=Path(root+"000_rrl_vehicle_profile_api_body.sql").read_text(encoding="utf-8")
helper=""" function check_floor_capacity(p_vehicle number,p_counts clob,p_unknown number)return clob is
  profile_value json_object_t;configured json_object_t;matrix json_object_t;variant json_object_t;
  counts json_array_t;variants json_array_t;limits json_array_t;row_value json_object_t;matches json_array_t:=json_array_t();
  result json_object_t:=json_object_t();type_id number;amount number;ceiling number;fits boolean;active_count number;
  element_value json_element_t;keys json_key_list;
  type type_count_map is table of number index by varchar2(100);seen type_count_map;
 begin
  profile_value:=json_object_t.parse(describe_profile(p_vehicle));
  result.put('basis','EXPLICIT_FLOOR_VARIANTS');result.put('operational_admission',false);
  if not profile_value.has('profile')then result.put('status','NOT_CONFIGURED');return result.to_clob;end if;
  configured:=profile_value.get_object('profile');
  if not configured.has('floor_capacity')then result.put('status','NOT_CONFIGURED');return result.to_clob;end if;
  result.put('profile_version',profile_value.get_number('version'));
  if profile_value.get_string('state')!='READY'then result.put('status','PROFILE_CHANGED');return result.to_clob;end if;
  if p_unknown is null or p_unknown<0 or p_unknown>5000 or p_unknown!=trunc(p_unknown)then
   raise_application_error(-20886,'VEHICLE_TARE_UNKNOWN_COUNT_INVALID');end if;
  counts:=json_array_t.parse(p_counts);
  if counts.get_size>200 then raise_application_error(-20886,'VEHICLE_TARE_COUNTS_BOUND_200');end if;
  for i in 0..counts.get_size-1 loop
   element_value:=counts.get(i);
   if not element_value.is_object then raise_application_error(-20886,'VEHICLE_TARE_COUNT_OBJECT_REQUIRED');end if;
   row_value:=treat(element_value as json_object_t);keys:=row_value.get_keys;
   if keys.count!=2 or not row_value.has('pallet_type_id')or not row_value.has('places')then
    raise_application_error(-20886,'VEHICLE_TARE_COUNT_FIELDS_REQUIRED');end if;
   element_value:=row_value.get('pallet_type_id');
   if not element_value.is_number then raise_application_error(-20886,'VEHICLE_TARE_COUNT_INTEGER_REQUIRED');end if;
   element_value:=row_value.get('places');
   if not element_value.is_number then raise_application_error(-20886,'VEHICLE_TARE_COUNT_INTEGER_REQUIRED');end if;
   type_id:=row_value.get_number('pallet_type_id');amount:=row_value.get_number('places');
   if type_id is null or type_id<1 or type_id!=trunc(type_id)or amount is null or amount<1 or amount>5000 or amount!=trunc(amount)then
    raise_application_error(-20886,'VEHICLE_TARE_COUNT_POSITIVE_INTEGER_REQUIRED');end if;
   if seen.exists(to_char(type_id,'TM9'))then raise_application_error(-20886,'VEHICLE_TARE_COUNT_TYPE_DUPLICATE');end if;
   seen(to_char(type_id,'TM9')):=amount;
   select count(*)into active_count from RRL_PALLET_TYPE where PALLET_TYPE_ID=type_id and ACTIVE=1;
   if active_count!=1 then raise_application_error(-20886,'VEHICLE_TARE_ACTIVE_TYPE_REQUIRED');end if;
  end loop;
  result.put('counts',counts);result.put('unconfirmed_places',p_unknown);
  if p_unknown>0 then result.put('status','TARE_TYPE_UNCONFIRMED');return result.to_clob;end if;
  matrix:=configured.get_object('floor_capacity');variants:=matrix.get_array('variants');
  for i in 0..variants.get_size-1 loop
   variant:=treat(variants.get(i) as json_object_t);limits:=variant.get_array('limits');fits:=true;
   for j in 0..counts.get_size-1 loop
    row_value:=treat(counts.get(j) as json_object_t);type_id:=row_value.get_number('pallet_type_id');amount:=row_value.get_number('places');ceiling:=0;
    for k in 0..limits.get_size-1 loop
     row_value:=treat(limits.get(k) as json_object_t);
     if row_value.get_number('pallet_type_id')=type_id then ceiling:=row_value.get_number('max_places');end if;
    end loop;
    if amount>ceiling then fits:=false;end if;
   end loop;
   if fits then matches.append(variant.get_string('code'));end if;
  end loop;
  result.put('matching_variants',matches);
  if matches.get_size>0 then result.put('status','COMPATIBLE');else result.put('status','INCOMPATIBLE');end if;
  return result.to_clob;
 end;
"""
point=" procedure configure(p_request";assert s.count(point)==1;s=s.replace(point,helper+point,1)
f[root+"002_profile_body.sql"]=s
s=Path(root+"000_rrl_transport_plan_rules_body.sql").read_text(encoding="utf-8")
helper=""" procedure prepared_floor_counts(p_sts clob,p_counts out clob,p_unknown out number)is
  numbers json_array_t:=json_array_t.parse(p_sts);wire_counts json_array_t:=json_array_t();entry_value json_object_t;
  query_value varchar2(32767);cursor_no integer;query_result integer;rows_cursor sys_refcursor;
  uid_value varchar2(64);case_count number;type_count number;type_id number;active_value number;row_count number:=0;
  type count_map is table of number index by varchar2(100);counts count_map;key_value varchar2(100);st_value varchar2(100);el json_element_t;
 begin
  if numbers.get_size<1 or numbers.get_size>200 then raise_application_error(-20886,'PLAN_TARE_ST_BOUND_200');end if;
  query_value:='select /* PLAN_TARE_BOUND1186 */ p.PALLET_UID,count(distinct c.CASE_PICK_TASK_ID),count(distinct c.PALLET_TYPE_ID),min(c.PALLET_TYPE_ID),min(t.ACTIVE) from RRL_SBORKA_PALLETS p left join RRL_CASE_PICK_TASK c on c.LEGACY_SBORKA_PALLET_ID=p.ID and c.STATUS!=''CANCELLED'' left join RRL_PALLET_TYPE t on t.PALLET_TYPE_ID=c.PALLET_TYPE_ID where p.ST_NUMBER in (';
  for i in 0..numbers.get_size-1 loop
   if i>0 then query_value:=query_value||',';end if;query_value:=query_value||':st'||to_char(i,'FM999');
  end loop;
  query_value:=query_value||') and not exists(select 1 from RRL_TT_HU_LOAD_ST m join RRL_TT_HU_LOAD_FACT l on l.LOAD_OPERATION_ID=m.LOAD_OPERATION_ID where m.SBORKA_PALLET_ID=p.ID and m.ACTIVE_FLAG=1 and l.STATUS=''LOADED'') group by p.PALLET_UID fetch first 5001 rows only';
  cursor_no:=dbms_sql.open_cursor;dbms_sql.parse(cursor_no,query_value,dbms_sql.native);
  for i in 0..numbers.get_size-1 loop
   el:=numbers.get(i);
   if not el.is_string then raise_application_error(-20886,'PLAN_TARE_ST_NUMBER_REQUIRED');end if;
   st_value:=numbers.get_string(i);
   if st_value is null or length(st_value)>100 then raise_application_error(-20886,'PLAN_TARE_ST_NUMBER_REQUIRED');end if;
   dbms_sql.bind_variable(cursor_no,':st'||to_char(i,'FM999'),st_value);
  end loop;
  query_result:=dbms_sql.execute(cursor_no);rows_cursor:=dbms_sql.to_refcursor(cursor_no);cursor_no:=null;p_unknown:=0;
  loop
   fetch rows_cursor into uid_value,case_count,type_count,type_id,active_value;exit when rows_cursor%notfound;
   row_count:=row_count+1;
   if row_count>5000 then raise_application_error(-20886,'PLAN_TARE_PLACES_BOUND_5000');end if;
   if case_count=1 and type_count=1 and active_value=1 then
    key_value:=to_char(type_id,'TM9');
    if counts.exists(key_value)then counts(key_value):=counts(key_value)+1;else counts(key_value):=1;end if;
   else p_unknown:=p_unknown+1;end if;
  end loop;close rows_cursor;
  key_value:=counts.first;
  while key_value is not null loop
   entry_value:=json_object_t();entry_value.put('pallet_type_id',to_number(key_value));entry_value.put('places',counts(key_value));wire_counts.append(entry_value);
   key_value:=counts.next(key_value);
  end loop;p_counts:=wire_counts.to_clob;
 exception when others then
  if cursor_no is not null then if dbms_sql.is_open(cursor_no)then dbms_sql.close_cursor(cursor_no);end if;end if;
  if rows_cursor%isopen then close rows_cursor;end if;raise;
 end;
"""
point=" procedure check_vehicle(";assert s.count(point)==1;s=s.replace(point,helper+point,1)
s=s.replace("  result json_object_t:=","  floor_value json_object_t;profile_value json_object_t;configured json_object_t;floor_counts clob;unknown_places number;\n  result json_object_t:=",1)
point="  if places>v.PALLETS then"
assert s.count(point)==1
insert="""  profile_value:=json_object_t.parse(RRL_VEHICLE_PROFILE_API.describe_profile(p_vehicle_id));
  floor_counts:='[]';unknown_places:=0;
  if profile_value.has('profile')then
   configured:=profile_value.get_object('profile');
   if configured.has('floor_capacity')then prepared_floor_counts(p_sts,floor_counts,unknown_places);unknown_places:=unknown_places+actual_places;end if;
  end if;
  floor_value:=json_object_t.parse(RRL_VEHICLE_PROFILE_API.check_floor_capacity(p_vehicle_id,floor_counts,unknown_places));
  if floor_value.get_string('status')='INCOMPATIBLE'then
   if p_complete=1 then raise_application_error(-20886,'PLAN_TARE_VARIANT_CAPACITY_EXCEEDED');end if;
   warn.append('Состав мест не соответствует ни одному нормативному сочетанию тары машины');
  elsif floor_value.get_string('status')not in('COMPATIBLE','NOT_CONFIGURED')then
   if p_complete=1 then raise_application_error(-20886,'PLAN_TARE_CURRENT_PLACE_TYPE_REQUIRED');end if;
   warn.append('Типы верхних мест или нормативный профиль тары требуют подтверждения');
  end if;
"""
s=s.replace(point,insert+"  if floor_value.get_string('status')='NOT_CONFIGURED'and places>v.PALLETS then",1)
point="  result.put('validation_status',case";assert point in s;s=s.replace(point,"  result.put('floor_capacity',floor_value);\n"+point,1)
f[root+"003_plan_rule.sql"]=s
f[root+"004_ledger.sql"]="""merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-14-1185-vehicle-floor-rule' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Current shared planning owner checks explicit tare variants; uncertain top place types refused for new configured profiles',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
"""
f[root+"apply.sql"]="@@001_profile_spec.sql\n@@002_profile_body.sql\n@@003_plan_rule.sql\n@@004_ledger.sql\nalter package RRL_TRANSPORT_PLAN_API compile body;\n/\nalter package RRL_STOCK_LOAD_THERMAL compile body;\n/\n"
f[root+"rollback.sql"]="@@000_rrl_vehicle_profile_api_spec.sql\n@@000_rrl_vehicle_profile_api_body.sql\n@@000_rrl_transport_plan_rules_body.sql\nupdate RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-14-1185-vehicle-floor-rule';\n/\nalter package RRL_TRANSPORT_PLAN_API compile body;\n/\nalter package RRL_STOCK_LOAD_THERMAL compile body;\n/\n"
f[root+"verify.sql"]="select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME in('RRL_VEHICLE_PROFILE_API','RRL_TRANSPORT_PLAN_RULES','RRL_TRANSPORT_PLAN_API','RRL_STOCK_LOAD_THERMAL');\n"
p=Path("wiki-raw/wms_admin_ui_reference/customer-orders.js");s=p.read_text(encoding="utf-8")
point=" const warnings=capacity?.warnings||[];"
insert=""" const floor=capacity?.floor_capacity;
 const floorNote=floor?.status==='COMPATIBLE'?' Норматив тары: допустимые варианты '+floor.matching_variants.join(', ')+'.':
  floor?.status==='INCOMPATIBLE'?' Ни один нормативный вариант тары не подходит.':
  floor&&floor.status!=='NOT_CONFIGURED'?' Типы верхних грузовых мест или профиль тары не подтверждены.':'';
"""
assert point in s;s=s.replace(point,insert+point,1)
s=s.replace("+thermalNote+thermalPlanningNote+","+thermalNote+thermalPlanningNote+floorNote+",1)
s=s.replace("PLAN_WEIGHT_CAPACITY_EXCEEDED:","PLAN_TARE_VARIANT_CAPACITY_EXCEEDED:'Состав мест превышает нормативные сочетания тары машины',PLAN_TARE_CURRENT_PLACE_TYPE_REQUIRED:'Нужны подтверждённые типы верхних мест и текущий профиль тары',PLAN_WEIGHT_CAPACITY_EXCEEDED:",1)
f[str(p)]=s
p=Path("wiki/database/nicora_ni022_vehicle_tare_20261014.md");f[str(p)]=p.read_text(encoding="utf-8")+"""
## Подключение1185–1186
Подготовлен общий native check_floor_capacity: целые количества по типам, альтернатива вариантов, несовместимость и явная неизвестность. Его вызывает прежний RRL_TRANSPORT_PLAN_RULES.check_vehicle, следовательно прежний окончательный assign/apply получает то же правило. Для машины без матрицы сохраняется старое ограничение PALLETS; при заданной матрице вместимость берётся из норматива, масса/тип/гидроборт/адрес/временные окна сохраняются.

Источник типов на этой стадии ограничен одним действующим CASE на подготовленное место с активным типом. Несколько CASE, отсутствие типа и физические уже загруженные TOP без отдельной типизации дают unconfirmed; complete=1 отказывает, preview возвращает предупреждение. Вложенные HU не считаются автоматически несколькими CASE; поддержка доказанного типа физического TOP — следующий блок. Это консервативное ограничение, не полный физический допуск. Запрос с200 bind ST /5000мест; без JSON_TABLE на большом join. Snapshot/read vs locked final recheck сохранены. SQL миграции и captured sources в2026-10-14_ni022_vehicle_floor_rule.
"""
p=Path("wiki/index.md");f[str(p)]="- [Общий норматив тары1186](database/nicora_ni022_vehicle_tare_20261014.md): prepared shared native final planning check/preview; unknown top type refuses new configured profiles.\n"+p.read_text(encoding="utf-8")
p=Path("wiki/log.md");f[str(p)]=p.read_text(encoding="utf-8")+"\n- 2026-10-14 /1186: prepared native floor variants evaluator and existing final planner integration; explicit unknown/legacy fallback/no second allocator. Checkpoint1185 captured, application pending.\n"
print(json.dumps(f))
