create or replace package RRL_VEHICLE_PROFILE_API authid definer as
 procedure configure(p_request clob,p_actor varchar2,p_result out clob);
 function describe_profile(p_vehicle number)return clob;
 procedure assert_writing;
end;
/
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
 procedure configure(p_request clob,p_actor varchar2,p_result out clob)is
  d json_object_t:=json_object_t.parse(p_request);v RRL_TR_VEHICLE%rowtype;j json_object_t:=json_object_t();
  op varchar2(100):=d.get_string('operation_id');vid number:=d.get_number('vehicle_id');expected number:=d.get_number('expected_version');
  size_class varchar2(32767):=trim(d.get_string('vehicle_size_class'));reason_value varchar2(32767):=trim(d.get_string('reason'));
  reference_value varchar2(32767):=trim(d.get_string('evidence_reference'));
  len_mm number:=d.get_number('cargo_length_mm');width_mm number:=d.get_number('cargo_width_mm');height_mm number:=d.get_number('cargo_height_mm');
  expected_hash varchar2(32767):=d.get_string('expected_source_hash');current_version number;old_request clob;old_actor nvarchar2(50);source_value clob;n number;entered boolean:=false;savepoint_ready boolean:=false;keys json_key_list;
 begin
  keys:=d.get_keys;
  if keys.count!=10 or op is null or lengthb(op)>100 or not regexp_like(op,'^[A-Za-z0-9_.:-]+$')
   or expected_hash is null or not regexp_like(expected_hash,'^[0-9A-F]{64}$')
   or vid is null or vid<1 or vid!=trunc(vid)or expected is null or expected<0 or expected!=trunc(expected)
   or size_class is null or lengthb(size_class)>40 or reason_value is null or lengthb(reason_value)>2000
   or reference_value is null or lengthb(reference_value)>255
   or len_mm is null or len_mm<1 or len_mm>1000000 or len_mm!=trunc(len_mm)
   or width_mm is null or width_mm<1 or width_mm>1000000 or width_mm!=trunc(width_mm)
   or height_mm is null or height_mm<1 or height_mm>1000000 or height_mm!=trunc(height_mm)
   then raise_application_error(-20886,'VEHICLE_PROFILE_EXPLICIT_FIELDS_REQUIRED');end if;
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
  current_version:=current_version+1;
  j.put('operation_id',op);j.put('vehicle_id',vid);j.put('version',current_version);j.put('vehicle_size_class',size_class);
  j.put('cargo_length_mm',len_mm);j.put('cargo_width_mm',width_mm);j.put('cargo_height_mm',height_mm);
  j.put('source',json_object_t.parse(source_value));j.put('actor',p_actor);j.put('evidence_reference',reference_value);
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
