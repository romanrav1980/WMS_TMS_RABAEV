create or replace package body RRL_VEHICLE_PROFILE_API as
 g_writing boolean:=false;g_tx varchar2(100);
 function base_json(v RRL_TR_VEHICLE%rowtype)return clob is j json_object_t:=json_object_t();
 begin
  j.put('vehicle_id',v.ID);j.put('vehicle_number',v.NUM);j.put('vehicle_type',v.TR_TYPE);
  j.put('pallet_capacity',RRL_STOCK_PLAN_HELPER.decimal_text(v.PALLETS));
  j.put('max_weight_kg',RRL_STOCK_PLAN_HELPER.decimal_text(v.MAX_WEIGHT_KG));
  return j.to_clob;
 end;
 procedure assert_writing is
 begin
  if not g_writing or g_tx is null or g_tx!=dbms_transaction.local_transaction_id(false)
   then raise_application_error(-20863,'VEHICLE_PROFILE_OWNER_REQUIRED');end if;
 end;
 function source_hash(p_source clob)return varchar2 is
 begin return rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(dbms_lob.substr(p_source,32767,1),'AL32UTF8'),sys.dbms_crypto.hash_sh256));end;
 function describe_profile(p_vehicle number)return clob is v RRL_TR_VEHICLE%rowtype;h RRL_VEHICLE_PROFILE_HIST%rowtype;
  j json_object_t:=json_object_t();current_base clob;
 begin
  select *into v from RRL_TR_VEHICLE where ID=p_vehicle;
  current_base:=base_json(v);j.put('base_hash',source_hash(current_base));j.put('vehicle_id',p_vehicle);j.put('base',json_object_t.parse(current_base));
  begin
   select hist.*into h from RRL_VEHICLE_PROFILE_HIST hist join RRL_VEHICLE_PROFILE_HEAD head
    on head.VEHICLE_ID=hist.VEHICLE_ID and head.VERSION_NO=hist.VERSION_NO where head.VEHICLE_ID=p_vehicle;
   j.put('profile',json_object_t.parse(h.RESULT_JSON));j.put('version',h.VERSION_NO);
   if dbms_lob.compare(current_base,h.SOURCE_JSON)=0 then j.put('state','READY');else j.put('state','BASE_CHANGED');end if;
  exception when no_data_found then j.put('state','NOT_CONFIGURED');j.put('version',0);end;
  return j.to_clob;
 end;
 function validated_floor_variants(p_value json_element_t)return json_array_t is
  variants json_array_t;variant json_object_t;limits json_array_t;lim json_object_t;
  code_value varchar2(40);type_id number;places number;n number;keys json_key_list;
  el json_element_t;
  type seen_map is table of boolean index by varchar2(100);seen_codes seen_map;seen_types seen_map;
 begin
  if p_value is null or not p_value.is_array then raise_application_error(-20886,'VEHICLE_TARE_VARIANTS_ARRAY_REQUIRED');end if;
  variants:=treat(p_value as json_array_t);
  if variants.get_size<1 or variants.get_size>20 then raise_application_error(-20886,'VEHICLE_TARE_VARIANTS_BOUND_20');end if;
  for i in 0..variants.get_size-1 loop
   el:=variants.get(i);
   if not el.is_object then raise_application_error(-20886,'VEHICLE_TARE_VARIANT_OBJECT_REQUIRED');end if;
   variant:=treat(el as json_object_t);keys:=variant.get_keys;
   if keys.count!=2 or not variant.has('code')or not variant.has('limits')then
    raise_application_error(-20886,'VEHICLE_TARE_VARIANT_FIELDS_REQUIRED');end if;
   el:=variant.get('code');
   if not el.is_string then raise_application_error(-20886,'VEHICLE_TARE_VARIANT_CODE_REQUIRED');end if;
   code_value:=variant.get_string('code');
   if code_value is null or not regexp_like(code_value,'^[A-Za-z0-9_.:-]{1,40}$')then
    raise_application_error(-20886,'VEHICLE_TARE_VARIANT_CODE_REQUIRED');end if;
   if seen_codes.exists(code_value)then raise_application_error(-20886,'VEHICLE_TARE_VARIANT_CODE_DUPLICATE');end if;
   seen_codes(code_value):=true;seen_types.delete;
   el:=variant.get('limits');
   if not el.is_array then raise_application_error(-20886,'VEHICLE_TARE_LIMITS_ARRAY_REQUIRED');end if;
   limits:=treat(el as json_array_t);
   if limits.get_size<1 or limits.get_size>8 then raise_application_error(-20886,'VEHICLE_TARE_TYPES_BOUND_8');end if;
   for k in 0..limits.get_size-1 loop
    el:=limits.get(k);
    if not el.is_object then raise_application_error(-20886,'VEHICLE_TARE_LIMIT_OBJECT_REQUIRED');end if;
    lim:=treat(el as json_object_t);keys:=lim.get_keys;
    if keys.count!=2 or not lim.has('pallet_type_id')or not lim.has('max_places')then
     raise_application_error(-20886,'VEHICLE_TARE_LIMIT_FIELDS_REQUIRED');end if;
    el:=lim.get('pallet_type_id');
    if not el.is_number then raise_application_error(-20886,'VEHICLE_TARE_INTEGER_TYPE_REQUIRED');end if;
    el:=lim.get('max_places');
    if not el.is_number then raise_application_error(-20886,'VEHICLE_TARE_INTEGER_PLACES_REQUIRED');end if;
    type_id:=lim.get_number('pallet_type_id');places:=lim.get_number('max_places');
    if type_id is null or type_id<1 or type_id!=trunc(type_id)or places is null or places<1 or places>1000 or places!=trunc(places)then
     raise_application_error(-20886,'VEHICLE_TARE_POSITIVE_INTEGER_LIMIT_REQUIRED');end if;
    if seen_types.exists(to_char(type_id,'TM9'))then raise_application_error(-20886,'VEHICLE_TARE_TYPE_DUPLICATE');end if;
    seen_types(to_char(type_id,'TM9')):=true;
    select count(*)into n from RRL_PALLET_TYPE where PALLET_TYPE_ID=type_id and ACTIVE=1;
    if n!=1 then raise_application_error(-20886,'VEHICLE_TARE_ACTIVE_TYPE_REQUIRED');end if;
   end loop;
  end loop;
  return variants;
 end;
 procedure configure(p_request clob,p_actor varchar2,p_result out clob)is
  d json_object_t:=json_object_t.parse(p_request);v RRL_TR_VEHICLE%rowtype;j json_object_t:=json_object_t();
  op varchar2(100):=d.get_string('operation_id');vid number:=d.get_number('vehicle_id');expected number:=d.get_number('expected_version');
  size_class varchar2(32767):=trim(d.get_string('vehicle_size_class'));reason_value varchar2(32767):=trim(d.get_string('reason'));
  reference_value varchar2(32767):=trim(d.get_string('evidence_reference'));
  len_mm number:=d.get_number('cargo_length_mm');width_mm number:=d.get_number('cargo_width_mm');height_mm number:=d.get_number('cargo_height_mm');
  floor_value json_object_t;floor_variants json_array_t;
  thermal_min varchar2(100);thermal_max varchar2(100);thermal_lo number;thermal_hi number;thermal json_object_t;thermal_min_element json_element_t;thermal_max_element json_element_t;
  expected_hash varchar2(32767):=d.get_string('expected_source_hash');current_version number;old_request clob;old_actor nvarchar2(50);source_value clob;n number;entered boolean:=false;savepoint_ready boolean:=false;keys json_key_list;
 begin
  keys:=d.get_keys;
  if keys.count not in(10,11,12,13) or op is null or lengthb(op)>100 or not regexp_like(op,'^[A-Za-z0-9_.:-]+$')
   or expected_hash is null or not regexp_like(expected_hash,'^[0-9A-F]{64}$')
   or vid is null or vid<1 or vid!=trunc(vid)or expected is null or expected<0 or expected!=trunc(expected)
   or size_class is null or lengthb(size_class)>40 or reason_value is null or lengthb(reason_value)>2000
   or reference_value is null or lengthb(reference_value)>255
   or len_mm is null or len_mm<1 or len_mm>1000000 or len_mm!=trunc(len_mm)
   or width_mm is null or width_mm<1 or width_mm>1000000 or width_mm!=trunc(width_mm)
   or height_mm is null or height_mm<1 or height_mm>1000000 or height_mm!=trunc(height_mm)
   then raise_application_error(-20886,'VEHICLE_PROFILE_EXPLICIT_FIELDS_REQUIRED');end if;
  for k in 1..keys.count loop
   if keys(k) not in('operation_id','vehicle_id','expected_version','expected_source_hash','vehicle_size_class','cargo_length_mm','cargo_width_mm','cargo_height_mm','reason','evidence_reference','temp_min_c','temp_max_c','floor_variants')
    then raise_application_error(-20886,'VEHICLE_PROFILE_UNKNOWN_FIELD');end if;
  end loop;
  if d.has('temp_min_c') or d.has('temp_max_c') then
   if not d.has('temp_min_c') or not d.has('temp_max_c')
    then raise_application_error(-20886,'VEHICLE_THERMAL_BOTH_BOUNDS_REQUIRED');end if;
   thermal_min_element:=d.get('temp_min_c');thermal_max_element:=d.get('temp_max_c');
   if not thermal_min_element.is_string or not thermal_max_element.is_string
    then raise_application_error(-20886,'VEHICLE_THERMAL_DECIMAL_TEXT_REQUIRED');end if;
   thermal_min:=d.get_string('temp_min_c');thermal_max:=d.get_string('temp_max_c');
   if thermal_min is null or thermal_max is null
    or not regexp_like(thermal_min,'^-?[0-9]{1,6}(\.[0-9]{1,3})?$')
    or not regexp_like(thermal_max,'^-?[0-9]{1,6}(\.[0-9]{1,3})?$')
    then raise_application_error(-20886,'VEHICLE_THERMAL_DECIMAL_TEXT_REQUIRED');end if;
   thermal_lo:=to_number(thermal_min,'999999D999','NLS_NUMERIC_CHARACTERS=''.,''');
   thermal_hi:=to_number(thermal_max,'999999D999','NLS_NUMERIC_CHARACTERS=''.,''');
   if thermal_lo>thermal_hi then raise_application_error(-20886,'VEHICLE_THERMAL_RANGE_INVALID');end if;
  end if;
  select count(*)into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0 and RRL_HAS_WRIGHT(ID,'transport_fleet_edit')=1;
  if n!=1 then raise_application_error(-20882,'VEHICLE_PROFILE_FLEET_AUTHORITY_REQUIRED');end if;
  RRL_STOCK_CONFIG_API.begin_change(p_actor,'transport_fleet_edit');entered:=true;
  savepoint vehicle_profile_effect;savepoint_ready:=true;
  begin
   select REQUEST_JSON,ACTOR,RESULT_JSON into old_request,old_actor,p_result from RRL_VEHICLE_PROFILE_HIST where OPERATION_ID=op;
   select count(*)into n from dual where json_equal(old_request,p_request);
   if n!=1 or old_actor!=p_actor then raise_application_error(-20864,'VEHICLE_PROFILE_OPERATION_CONFLICT');end if;
   RRL_STOCK_CONFIG_API.end_change;entered:=false;return;
  exception when no_data_found then null;end;
  select *into v from RRL_TR_VEHICLE where ID=vid for update;
  if nvl(v.DELETED,0)!=0 or v.NUM is null or v.TR_TYPE is null or v.PALLETS is null or v.MAX_WEIGHT_KG is null
   then raise_application_error(-20886,'VEHICLE_PROFILE_EXISTING_BASE_REQUIRED');end if;
  source_value:=base_json(v);
  if source_hash(source_value)!=expected_hash then raise_application_error(-20890,'VEHICLE_PROFILE_BASE_CHANGED');end if;
  g_tx:=dbms_transaction.local_transaction_id(false);g_writing:=true;
  merge into RRL_VEHICLE_PROFILE_HEAD h using(select vid ID from dual)s on(h.VEHICLE_ID=s.ID)
   when not matched then insert(VEHICLE_ID,VERSION_NO)values(vid,0);
  select VERSION_NO into current_version from RRL_VEHICLE_PROFILE_HEAD where VEHICLE_ID=vid for update;
  if current_version!=expected then raise_application_error(-20886,'VEHICLE_PROFILE_VERSION_CONFLICT');end if;
  if d.has('floor_variants')then floor_variants:=validated_floor_variants(d.get('floor_variants'));end if;
  current_version:=current_version+1;
  j.put('operation_id',op);j.put('vehicle_id',vid);j.put('version',current_version);j.put('vehicle_size_class',size_class);
  j.put('cargo_length_mm',len_mm);j.put('cargo_width_mm',width_mm);j.put('cargo_height_mm',height_mm);
  j.put('source',json_object_t.parse(source_value));j.put('actor',p_actor);j.put('evidence_reference',reference_value);
  if thermal_min is not null then
   thermal:=json_object_t();thermal.put('temp_min_c',RRL_STOCK_PLAN_HELPER.decimal_text(thermal_lo));
   thermal.put('temp_max_c',RRL_STOCK_PLAN_HELPER.decimal_text(thermal_hi));
   thermal.put('basis','FLEET_DECLARED_CAPABILITY');thermal.put('evidence_reference',reference_value);
   thermal.put('measurement_verified',false);j.put('temperature_capability',thermal);
  end if;
  if floor_variants is not null then
   floor_value:=json_object_t();floor_value.put('variants',floor_variants);
   floor_value.put('basis','FLEET_DECLARED_FLOOR_VARIANTS');floor_value.put('evidence_reference',reference_value);
   j.put('floor_capacity',floor_value);
  end if;
  j.put('status','CONFIGURED');j.put('stock_changed',false);p_result:=j.to_clob;
  insert into RRL_VEHICLE_PROFILE_HIST(VEHICLE_ID,VERSION_NO,OPERATION_ID,ACTOR,VEHICLE_SIZE_CLASS,CARGO_LENGTH_MM,CARGO_WIDTH_MM,CARGO_HEIGHT_MM,SOURCE_JSON,REQUEST_JSON,RESULT_JSON)
   values(vid,current_version,op,p_actor,size_class,len_mm,width_mm,height_mm,source_value,p_request,p_result);
  update RRL_VEHICLE_PROFILE_HEAD set VERSION_NO=current_version where VEHICLE_ID=vid;
  g_writing:=false;g_tx:=null;RRL_STOCK_CONFIG_API.end_change;entered:=false;
 exception when others then
  g_writing:=false;g_tx:=null;
  if savepoint_ready then rollback to vehicle_profile_effect;end if;
  if entered then RRL_STOCK_CONFIG_API.end_change;end if;
  raise;
 end;
end;
/
