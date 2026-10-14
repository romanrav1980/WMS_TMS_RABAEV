create or replace package RRL_STOCK_LOAD_THERMAL authid definer
 accessible by(package RRL_STOCK_HU_LOAD_CORE,package RRL_STOCK_TRIP_DEPART_CMD,trigger RRL_LOAD_THERMAL_FACT_GUARD) as
 procedure compile_confirmation(p_members clob,p_vehicle number,p_context clob,p_domain out json_object_t,p_phase varchar2 default 'MANUAL_AT_LOADING');
 procedure assert_current(p_members clob,p_vehicle number,p_domain clob,p_phase varchar2 default 'MANUAL_AT_LOADING');
 procedure persist_confirmation(p_operation varchar2,p_domain clob,p_actor varchar2);
 procedure assert_writing(p_operation varchar2);
end;
/

create or replace package body RRL_STOCK_LOAD_THERMAL as
 g_writing boolean:=false;g_operation varchar2(100);g_tx varchar2(100);
 function signed_decimal(p_value varchar2)return number is
 begin
  if p_value is null or not regexp_like(p_value,'^-?[0-9]{1,6}(\.[0-9]{1,3})?$')
   then raise_application_error(-20886,'LOAD_THERMAL_DECIMAL_TEXT_REQUIRED');end if;
  return to_number(p_value,'999999D999','NLS_NUMERIC_CHARACTERS=''.,''');
 end;
 procedure compile_confirmation(p_members clob,p_vehicle number,p_context clob,p_domain out json_object_t,p_phase varchar2 default 'MANUAL_AT_LOADING')is
  ctx json_object_t:=json_object_t.parse(p_context);observation json_object_t;profile json_object_t;capability json_object_t;
  rules json_array_t:=json_array_t();rule_value json_object_t;lo number;hi number;vlo number;vhi number;observed number;
  known_count number:=0;unknown_count number:=0;row_count number:=0;version_no number;keys json_key_list;
  source_value clob;reference_value varchar2(32767);mode_value varchar2(100);observed_element json_element_t;member_values json_array_t:=json_array_t.parse(p_members);
  query_value varchar2(32767);cursor_no integer;query_result integer;rows_cursor sys_refcursor;
  item_ware number;item_article varchar2(32767);item_lo number;item_hi number;member_no number;
 begin
  p_domain:=null;
  if p_phase is null or p_phase not in('MANUAL_AT_LOADING','MANUAL_AT_DEPARTURE')then raise_application_error(-20886,'THERMAL_PHASE_REQUIRED');end if;
  if member_values.get_size<1 or member_values.get_size>200
   then raise_application_error(-20881,'LOAD_THERMAL_MEMBER_BOUND_200');end if;
  query_value:='select /* CURRENT_LOAD_THERMAL_IN1173 */ distinct p.WARE_ID,r.ARTICUL,cfg.TEMP_MIN,cfg.TEMP_MAX from RRL_SBORKA_PALLETS p join RRL_SBORKA_PALLET_ROWS r on r.PALLET_UID=p.PALLET_UID left join RRL_RECEIPT_SKU_RULE cfg on cfg.WARE_ID=p.WARE_ID and cfg.ARTICUL=r.ARTICUL where p.ID in (';
  for i in 0..member_values.get_size-1 loop
   if i>0 then query_value:=query_value||',';end if;query_value:=query_value||':id'||to_char(i,'FM999');
  end loop;
  query_value:=query_value||') order by p.WARE_ID,r.ARTICUL fetch first 1001 rows only';
  cursor_no:=dbms_sql.open_cursor;dbms_sql.parse(cursor_no,query_value,dbms_sql.native);
  for i in 0..member_values.get_size-1 loop
   member_no:=member_values.get_number(i);
   if member_no is null or member_no<1 or member_no!=trunc(member_no)then raise_application_error(-20881,'LOAD_THERMAL_MEMBER_ID_REQUIRED');end if;
   dbms_sql.bind_variable(cursor_no,':id'||to_char(i,'FM999'),member_no);
  end loop;
  query_result:=dbms_sql.execute(cursor_no);rows_cursor:=dbms_sql.to_refcursor(cursor_no);cursor_no:=null;
  loop
   fetch rows_cursor into item_ware,item_article,item_lo,item_hi;exit when rows_cursor%notfound;
   row_count:=row_count+1;
   if row_count>1000 then raise_application_error(-20881,'LOAD_THERMAL_SKU_BOUND_1000');end if;
   if item_article is null then raise_application_error(-20886,'LOAD_THERMAL_ARTICLE_REQUIRED');end if;
   if item_lo is not null and item_hi is not null and item_lo>item_hi
    then raise_application_error(-20886,'LOAD_THERMAL_SKU_RANGE_INVALID');end if;
   rule_value:=json_object_t();rule_value.put('warehouse_id',item_ware);rule_value.put('articul',item_article);
   rule_value.put('temp_min_c',RRL_STOCK_PLAN_HELPER.decimal_text(item_lo));
   rule_value.put('temp_max_c',RRL_STOCK_PLAN_HELPER.decimal_text(item_hi));rules.append(rule_value);
   if item_lo is null and item_hi is null then unknown_count:=unknown_count+1;
   else
    known_count:=known_count+1;
    if item_lo is not null then if lo is null or item_lo>lo then lo:=item_lo;end if;end if;
    if item_hi is not null then if hi is null or item_hi<hi then hi:=item_hi;end if;end if;
   end if;
  end loop;close rows_cursor;
  if row_count=0 then raise_application_error(-20886,'LOAD_THERMAL_SOURCE_ROWS_REQUIRED');end if;
  if known_count=0 and not ctx.has('temperature_confirmation')then return;end if;
  if lo is not null and hi is not null and lo>hi then raise_application_error(-20886,'LOAD_THERMAL_SKU_RANGES_CONFLICT');end if;
  if not ctx.has('temperature_confirmation')then
   if p_phase='MANUAL_AT_DEPARTURE'then raise_application_error(-20886,'DEPART_THERMAL_CURRENT_CONFIRMATION_REQUIRED');else raise_application_error(-20886,'LOAD_THERMAL_CURRENT_CONFIRMATION_REQUIRED');end if;
  end if;
  observation:=ctx.get_object('temperature_confirmation');keys:=observation.get_keys;
  if keys.count!=4 then raise_application_error(-20886,'LOAD_THERMAL_EXPLICIT_FIELDS_REQUIRED');end if;
  for k in 1..keys.count loop
   if keys(k)not in('origin','observed_c','vehicle_profile_version','observation_reference')
    then raise_application_error(-20886,'LOAD_THERMAL_UNKNOWN_FIELD');end if;
  end loop;
  mode_value:=observation.get_string('origin');reference_value:=trim(observation.get_string('observation_reference'));
  if mode_value is null or mode_value!=p_phase or reference_value is null or length(reference_value)>100
   then raise_application_error(-20886,'LOAD_THERMAL_MANUAL_REFERENCE_REQUIRED');end if;
  observed_element:=observation.get('observed_c');
  if observed_element is null or not observed_element.is_string then raise_application_error(-20886,'LOAD_THERMAL_DECIMAL_TEXT_REQUIRED');end if;
  observed:=signed_decimal(observation.get_string('observed_c'));
  version_no:=observation.get_number('vehicle_profile_version');
  profile:=json_object_t.parse(RRL_VEHICLE_PROFILE_API.describe_profile(p_vehicle));
  if profile.get_string('state') is null or profile.get_string('state')!='READY'
   or version_no is null or version_no!=profile.get_number('version')
   then raise_application_error(-20886,'LOAD_THERMAL_CURRENT_VEHICLE_PROFILE_REQUIRED');end if;
  capability:=profile.get_object('profile');
  if not capability.has('temperature_capability')then raise_application_error(-20886,'LOAD_THERMAL_VEHICLE_RANGE_REQUIRED');end if;
  capability:=capability.get_object('temperature_capability');
  vlo:=signed_decimal(capability.get_string('temp_min_c'));vhi:=signed_decimal(capability.get_string('temp_max_c'));
  if vlo>vhi or observed<vlo or observed>vhi
   or(lo is not null and observed<lo)or(hi is not null and observed>hi)
   then raise_application_error(-20886,'LOAD_THERMAL_OBSERVATION_INCOMPATIBLE');end if;
  p_domain:=json_object_t();p_domain.put('vehicle_id',p_vehicle);p_domain.put('profile_version',version_no);
  p_domain.put('profile_base_hash',profile.get_string('base_hash'));p_domain.put('rules',rules);
  p_domain.put('configured_sku_count',known_count);p_domain.put('unconfirmed_sku_count',unknown_count);
  p_domain.put('observed_c',RRL_STOCK_PLAN_HELPER.decimal_text(observed));p_domain.put('observation_reference',reference_value);
  p_domain.put('origin',p_phase);p_domain.put('sensor_verified',false);
  p_domain.put('temperature_confirmation',observation);
 exception when others then
  if cursor_no is not null then if dbms_sql.is_open(cursor_no)then dbms_sql.close_cursor(cursor_no);end if;end if;
  if rows_cursor%isopen then close rows_cursor;end if;raise;
 end;
 procedure assert_current(p_members clob,p_vehicle number,p_domain clob,p_phase varchar2 default 'MANUAL_AT_LOADING')is
  frozen json_object_t;ctx json_object_t:=json_object_t();current_value json_object_t;n number;current_wire clob;
 begin
  RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),4);
  if p_domain is not null then frozen:=json_object_t.parse(p_domain);ctx.put('temperature_confirmation',frozen.get_object('temperature_confirmation'));end if;
  compile_confirmation(p_members,p_vehicle,ctx.to_clob,current_value,p_phase);
  if p_domain is null and current_value is null then return;end if;
  if p_domain is null or current_value is null then raise_application_error(-20890,'CLOSURE_CHANGED: load thermal requirements');end if;
  current_wire:=current_value.to_clob;select count(*)into n from dual where json_equal(p_domain,current_wire);
  if n!=1 then raise_application_error(-20890,'CLOSURE_CHANGED: load thermal profile/rules');end if;
 end;
 procedure assert_writing(p_operation varchar2)is
 begin
  if not g_writing or g_operation is null or g_operation!=p_operation or g_tx is null
   or g_tx!=dbms_transaction.local_transaction_id(false)
   or sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID') is null
   or sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')!=p_operation
   then raise_application_error(-20863,'LOAD_THERMAL_ROOT_OWNER_REQUIRED');end if;
  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_TT_HU_LOAD_FACT',p_operation));
 end;
 procedure persist_confirmation(p_operation varchar2,p_domain clob,p_actor varchar2)is
  d json_object_t;n number;vehicle_no number;version_no number;observed_no number;reference_value nvarchar2(100);
 begin
  if p_domain is null then return;end if;
  d:=json_object_t.parse(p_domain);vehicle_no:=d.get_number('vehicle_id');version_no:=d.get_number('profile_version');
  observed_no:=signed_decimal(d.get_string('observed_c'));reference_value:=d.get_string('observation_reference');
  select count(*)into n from RRL_TT_HU_LOAD_FACT l join RRL_STOCK_OPERATION o on o.OPERATION_ID=l.LOAD_OPERATION_ID
   where l.LOAD_OPERATION_ID=p_operation and l.VEHICLE_ID=vehicle_no
    and l.LOADED_BY=p_actor and l.STATUS='LOADED'and o.STATE='IN_FLIGHT';
  if n!=1 then raise_application_error(-20863,'LOAD_THERMAL_CURRENT_LOAD_FACT_REQUIRED');end if;
  g_writing:=true;g_operation:=p_operation;g_tx:=dbms_transaction.local_transaction_id(false);
  insert into RRL_TT_LOAD_THERMAL_FACT(LOAD_OPERATION_ID,VEHICLE_ID,PROFILE_VERSION,OBSERVED_C,OBSERVATION_REFERENCE,OBSERVATION_BASIS,ACTOR,CONFIRMATION_JSON)
   values(p_operation,vehicle_no,version_no,observed_no,reference_value,'MANUAL_AT_LOADING',p_actor,p_domain);
  g_writing:=false;g_operation:=null;g_tx:=null;
 exception when others then g_writing:=false;g_operation:=null;g_tx:=null;raise;
 end;
end;
/
