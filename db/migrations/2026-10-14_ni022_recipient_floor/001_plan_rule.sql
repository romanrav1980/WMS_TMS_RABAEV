create or replace package body RRL_TRANSPORT_PLAN_RULES as
 procedure assert_actor(p_actor varchar2,p_ware number)is n number;begin
  select count(*)into n from RRL_WARES where ID=p_ware;
  if n!=1 then raise_application_error(-20886,'PLAN_CURRENT_WARE_REQUIRED');end if;
  select count(*)into n from RUSERS u where u.ID=p_actor and nvl(u.DELETED,0)=0
   and(u.WARE_ID=p_ware or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN')and RRL_HAS_WRIGHT(u.ID,'transport_dispatch_edit')=1;
  if n!=1 or p_ware is null then raise_application_error(-20882,'PLAN_CURRENT_WARE_ACTOR_REQUIRED');end if;
 end;
 procedure prepared_floor_counts(p_sts clob,p_counts out clob,p_unknown out number)is
  numbers json_array_t:=json_array_t.parse(p_sts);wire_counts json_array_t:=json_array_t();entry_value json_object_t;
  query_value varchar2(32767);cursor_no integer;query_result integer;rows_cursor sys_refcursor;
  uid_value varchar2(64);case_count number;type_count number;type_id number;active_value number;planned_count number;planned_type number;planned_active number;row_count number:=0;
  type count_map is table of number index by varchar2(100);counts count_map;key_value varchar2(100);st_value varchar2(100);el json_element_t;
 begin
  if numbers.get_size<1 or numbers.get_size>200 then raise_application_error(-20886,'PLAN_TARE_ST_BOUND_200');end if;
  query_value:='select /* PLAN_TARE_RECIPIENT1208 */ p.PALLET_UID,count(distinct c.CASE_PICK_TASK_ID),count(distinct c.PALLET_TYPE_ID),min(c.PALLET_TYPE_ID),min(t.ACTIVE),count(distinct rt.PALLET_TYPE_ID),min(rt.PALLET_TYPE_ID),min(pt.ACTIVE) from RRL_SBORKA_PALLETS p left join RRL_CASE_PICK_TASK c on c.LEGACY_SBORKA_PALLET_ID=p.ID and c.STATUS!=''CANCELLED'' left join RRL_PALLET_TYPE t on t.PALLET_TYPE_ID=c.PALLET_TYPE_ID left join RRL_CUSTOMER_ORDER_FULFILLMENT ff on ff.LEGACY_SBORKA_PALLET_ID=p.ID left join RRL_CUSTOMER_ORDER co on co.CUSTOMER_ORDER_ID=ff.CUSTOMER_ORDER_ID left join RRL_CUSTOMER_PALLET_TYPE_RULE rt on rt.CUSTOMER_PALLET_TYPE_RULE_ID=(select rr.CUSTOMER_PALLET_TYPE_RULE_ID from RRL_CUSTOMER_PALLET_TYPE_RULE rr where rr.CUSTOMER_ID=co.CUSTOMER_ID and (rr.CUSTOMER_STORE_MAP_ID=co.CUSTOMER_STORE_MAP_ID or (rr.CUSTOMER_STORE_MAP_ID is null and rr.CUSTOMER_ADDRESS_ID is null)) and rr.ACTIVE=1 and trunc(sysdate) between rr.VALID_FROM and nvl(rr.VALID_TO,date ''2999-12-31'') order by case when rr.CUSTOMER_STORE_MAP_ID=co.CUSTOMER_STORE_MAP_ID then 0 else 1 end,rr.IS_DEFAULT desc,rr.CUSTOMER_PALLET_TYPE_RULE_ID fetch first 1 row only) left join RRL_PALLET_TYPE pt on pt.PALLET_TYPE_ID=rt.PALLET_TYPE_ID where p.ST_NUMBER in (';
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
   fetch rows_cursor into uid_value,case_count,type_count,type_id,active_value,planned_count,planned_type,planned_active;exit when rows_cursor%notfound;
   row_count:=row_count+1;
   if row_count>5000 then raise_application_error(-20886,'PLAN_TARE_PLACES_BOUND_5000');end if;
   if case_count=0 and planned_count=1 and planned_active=1 then type_id:=planned_type;type_count:=1;active_value:=1;case_count:=1;end if;
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
 procedure check_vehicle(p_vehicle_id number,p_sts clob,p_complete number,p_result out clob)is
  v RRL_TR_VEHICLE%rowtype;places number;weight number;unknown_weight number;strict_windows number;bad number;actual_places number;actual_weight number;actual_bad number;
  floor_value json_object_t;loaded_floor json_object_t;profile_value json_object_t;configured json_object_t;floor_counts clob;unknown_places number;
  result json_object_t:=json_object_t();warn json_array_t:=json_array_t();
 begin
  if p_vehicle_id is null then
   if p_complete=1 then raise_application_error(-20886,'PLAN_CURRENT_VEHICLE_REQUIRED');end if;
  result.put('validation_status','DRAFT_VEHICLE_REQUIRED');warn.append('Машина не назначена; вместимость и сроки не подтверждены');
   result.put('warnings',warn);p_result:=result.to_clob;return;
  end if;
  select *into v from RRL_TR_VEHICLE where ID=p_vehicle_id;
  if nvl(v.BLOCKED,0)!=0 or nvl(v.DELETED,0)!=0 or nvl(v.PALLETS,0)<=0 or nvl(v.MAX_WEIGHT_KG,0)<=0 or v.TR_TYPE is null then raise_application_error(-20886,'PLAN_ACTIVE_VEHICLE_CAPACITY_REQUIRED');end if;
  select count(distinct p.PALLET_UID),sum(r.ORDER_WEIGHT),
   sum(case when r.ID is null or r.ORDER_WEIGHT is null or r.ORDER_WEIGHT<=0 then 1 else 0 end)
   into places,weight,unknown_weight from RRL_SBORKA_PALLETS p
   left join RRL_SBORKA_PALLET_ROWS r on r.PALLET_UID=p.PALLET_UID
   where p.ST_NUMBER in(select ST_NUMBER from json_table(p_sts,'$[*]'columns(ST_NUMBER varchar2(100)path '$')))
    and not exists(select 1 from RRL_TT_HU_LOAD_ST m join RRL_TT_HU_LOAD_FACT l on l.LOAD_OPERATION_ID=m.LOAD_OPERATION_ID where m.SBORKA_PALLET_ID=p.ID and m.ACTIVE_FLAG=1 and l.STATUS='LOADED');
   select count(*),nvl(sum(l.GROSS_WEIGHT_KG),0),
    nvl(sum(case when l.GROSS_WEIGHT_KG is null or l.GROSS_WEIGHT_KG<=0 or o.STATE!='APPLIED' or o.STATE is null then 1 else 0 end),0)
    into actual_places,actual_weight,actual_bad from RRL_TT_HU_LOAD_FACT l
    left join RRL_STOCK_OPERATION o on o.OPERATION_ID=l.LOAD_OPERATION_ID
    where l.STATUS='LOADED'and l.LOAD_OPERATION_ID in(
     select m.LOAD_OPERATION_ID from RRL_TT_HU_LOAD_ST m join RRL_SBORKA_PALLETS p on p.ID=m.SBORKA_PALLET_ID
     where m.ACTIVE_FLAG=1 and p.ST_NUMBER in(select ST_NUMBER from json_table(p_sts,'$[*]'columns(ST_NUMBER varchar2(100)path '$')))
    );
   if actual_bad>0 then raise_application_error(-20886,'PLAN_LOADED_PHYSICAL_CAPACITY_PROOF_REQUIRED');end if;
   places:=nvl(places,0)+actual_places;weight:=nvl(weight,0)+actual_weight;unknown_weight:=nvl(unknown_weight,0);
   if weight>v.MAX_WEIGHT_KG then raise_application_error(-20886,'PLAN_WEIGHT_CAPACITY_EXCEEDED');end if;
  profile_value:=json_object_t.parse(RRL_VEHICLE_PROFILE_API.describe_profile(p_vehicle_id));
  floor_counts:='[]';unknown_places:=0;
  if profile_value.has('profile')then
   configured:=profile_value.get_object('profile');
   if configured.has('floor_capacity')then prepared_floor_counts(p_sts,floor_counts,unknown_places);
    loaded_floor:=json_object_t.parse(RRL_STOCK_LOAD_FLOOR.planning_counts(p_vehicle_id,p_sts,floor_counts,unknown_places));
    floor_counts:=loaded_floor.get_array('counts').to_clob;unknown_places:=loaded_floor.get_number('unconfirmed_places');end if;
  end if;
  floor_value:=json_object_t.parse(RRL_VEHICLE_PROFILE_API.check_floor_capacity(p_vehicle_id,floor_counts,unknown_places));
  if floor_value.get_string('status')='INCOMPATIBLE'then
   if p_complete=1 then raise_application_error(-20886,'PLAN_TARE_VARIANT_CAPACITY_EXCEEDED');end if;
   warn.append('Состав мест не соответствует ни одному нормативному сочетанию тары машины');
  elsif floor_value.get_string('status')not in('COMPATIBLE','NOT_CONFIGURED')then
   if p_complete=1 then raise_application_error(-20886,'PLAN_TARE_CURRENT_PLACE_TYPE_REQUIRED');end if;
   warn.append('Типы верхних мест или нормативный профиль тары требуют подтверждения');
  end if;
  if floor_value.get_string('status')='NOT_CONFIGURED'and places>v.PALLETS then raise_application_error(-20886,'PLAN_PALLET_CAPACITY_EXCEEDED');end if;
  if unknown_weight>0 then
   if p_complete=1 then raise_application_error(-20886,'PLAN_DECLARED_WEIGHT_REQUIRED');end if;
   warn.append('Плановая масса части товара отсутствует; окончательная готовность не подтверждена');
  elsif weight>v.MAX_WEIGHT_KG then raise_application_error(-20886,'PLAN_WEIGHT_CAPACITY_EXCEEDED');end if;
  select count(*)into bad from RRL_SBORKA_PALLETS p join RRL_ADDR a on a.ADDR=p.ADDR
   where p.ST_NUMBER in(select ST_NUMBER from json_table(p_sts,'$[*]'columns(ST_NUMBER varchar2(100)path '$')))
   and((a.TRANSPORT_TYPE is not null and trim(a.TRANSPORT_TYPE)not in('0',trim(v.TR_TYPE)))
    or(nvl(a.STOL,0)>0 and nvl(v.GIDROBORT,0)!=1));
  if bad>0 then raise_application_error(-20886,'PLAN_ADDRESS_VEHICLE_TYPE_OR_HYDRO_CONFLICT');end if;
  select count(*)into bad from RRL_SBORKA_PALLETS p join RRL_ADDR a on a.ADDR=p.ADDR
   where p.ST_NUMBER in(select ST_NUMBER from json_table(p_sts,'$[*]'columns(ST_NUMBER varchar2(100)path '$')))
   and a.MAX_VEHICLE_TONS is not null and v.MAX_WEIGHT_KG>1000*a.MAX_VEHICLE_TONS;
  if bad>0 then raise_application_error(-20886,'PLAN_ADDRESS_VEHICLE_LIMIT_EXCEEDED');end if;
  select count(*)into strict_windows from RRL_SBORKA_PALLETS p join RRL_ADDR a on a.ADDR=p.ADDR
   where p.ST_NUMBER in(select ST_NUMBER from json_table(p_sts,'$[*]'columns(ST_NUMBER varchar2(100)path '$')))and nvl(a.TW_STRICT,0)=1;
  if strict_windows>0 then
   if p_complete=1 then raise_application_error(-20886,'PLAN_STRICT_TIME_SCHEDULE_REQUIRED');end if;
   warn.append('Жёсткие временные окна требуют подтверждённого расписания');
  end if;
  result.put('floor_capacity',floor_value);
  result.put('validation_status',case when warn.get_size=0 then 'CAPACITY_TYPE_CHECKED'else'DRAFT_INCOMPLETE'end);
  result.put('frozen_loaded_places',actual_places);result.put('frozen_loaded_weight_kg',to_char(actual_weight,'TM9','NLS_NUMERIC_CHARACTERS=''.,'''));result.put('declared_places',places);result.put('declared_weight_kg',to_char(weight,'TM9','NLS_NUMERIC_CHARACTERS=''.,'''));
  result.put('warnings',warn);result.put('physical_stock_changed',false);result.put('physical_load_admission',false);
  p_result:=result.to_clob;
 end;
end;

/
