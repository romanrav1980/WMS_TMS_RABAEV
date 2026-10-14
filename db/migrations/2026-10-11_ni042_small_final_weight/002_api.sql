create or replace package RRL_PALLET_TYPE_API authid definer as
 procedure upsert_request(p_request clob,p_actor varchar2,p_id out number);
end;
/
create or replace package body RRL_PALLET_TYPE_API as
 procedure clear_context is begin dbms_session.clear_context('RRL_PALLET_TYPE_CTX',null,'TX_ID');dbms_session.clear_context('RRL_PALLET_TYPE_CTX',null,'ACTOR');dbms_session.clear_context('RRL_PALLET_TYPE_CTX',null,'TYPE_ID');end;
 procedure upsert_request(p_request clob,p_actor varchar2,p_id out number)is
  j json_object_t:=json_object_t.parse(p_request);v_id number;v_code varchar2(50);name_value varchar2(160);class_value varchar2(20);
  v_volume number;v_weight number;len_mm number;v_width_mm number;v_height_mm number;v_max_clients number;v_active number;v_required number;n number;current_version number:=0;expected_version number;old_required number;
 begin
  if p_request is null or dbms_lob.getlength(p_request)>16000 then raise_application_error(-20881,'PALLET_TYPE_REQUEST_BOUND');end if;
  select count(*)into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0;
  if n!=1 or RRL_HAS_WRIGHT(p_actor,'case_pick_manage')!=1 then raise_application_error(-20882,'PALLET_TYPE_MANAGE_FORBIDDEN');end if;
  RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),6);
  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_STOCK_POLICY_GUARD','WAREHOUSE.METADATA'));
  v_id:=j.get_number('pallet_type_id');v_code:=upper(trim(j.get_string('pallet_type_code')));name_value:=trim(j.get_string('pallet_type_name'));
  class_value:=upper(trim(j.get_string('load_unit_class')));v_volume:=j.get_number('default_volume_m3');v_weight:=j.get_number('default_weight_kg');
  len_mm:=j.get_number('length_mm');v_width_mm:=j.get_number('width_mm');v_height_mm:=j.get_number('height_mm');
  v_max_clients:=j.get_number('default_max_client_pallets');v_active:=j.get_number('active');
  if v_code is null or name_value is null or class_value is null or nvl(v_volume,0)<0 or nvl(v_weight,0)<0 or nvl(len_mm,0)<0
   or nvl(v_width_mm,0)<0 or nvl(v_height_mm,0)<0 or v_max_clients is null or v_max_clients not between 1 and 3 or v_max_clients!=trunc(v_max_clients)
   or v_active is null or v_active not in(0,1) then raise_application_error(-20886,'PALLET_TYPE_FIELDS_INVALID');end if;
  if v_id is null then
   begin select PALLET_TYPE_ID into v_id from RRL_PALLET_TYPE where PALLET_TYPE_CODE=v_code;
   exception when no_data_found then select RRL_PALLET_TYPE_SQ.nextval into v_id from dual;end;
  elsif v_id<1 or v_id!=trunc(v_id)then raise_application_error(-20886,'PALLET_TYPE_ID_INVALID');end if;
  expected_version:=j.get_number('expected_version');
  begin select TYPE_VERSION,FINAL_WEIGHT_REQUIRED into current_version,old_required from RRL_PALLET_TYPE where PALLET_TYPE_ID=v_id;
  exception when no_data_found then current_version:=0;old_required:=0;end;
  if expected_version is not null and expected_version!=current_version then raise_application_error(-20873,'PALLET_TYPE_VERSION_CHANGED');end if;
  v_required:=null;
  if j.has('final_weight_required')and not j.get('final_weight_required').is_null then v_required:=case when j.get_boolean('final_weight_required')then 1 else 0 end;end if;
  if v_required is not null and v_required!=old_required and expected_version is null then raise_application_error(-20886,'PALLET_TYPE_EXPECTED_VERSION_REQUIRED_FOR_FINAL_WEIGHT');end if;
  dbms_session.set_context('RRL_PALLET_TYPE_CTX','TX_ID',dbms_transaction.local_transaction_id(true));
  dbms_session.set_context('RRL_PALLET_TYPE_CTX','ACTOR',p_actor);dbms_session.set_context('RRL_PALLET_TYPE_CTX','TYPE_ID',RRL_STOCK_PLAN_HELPER.decimal_text(v_id));
  merge into RRL_PALLET_TYPE d using(select v_id PALLET_TYPE_ID from dual)s on(d.PALLET_TYPE_ID=s.PALLET_TYPE_ID)
  when matched then update set PALLET_TYPE_CODE=v_code,PALLET_TYPE_NAME=name_value,LOAD_UNIT_CLASS=class_value,
   DEFAULT_VOLUME_M3=v_volume,DEFAULT_WEIGHT_KG=v_weight,LENGTH_MM=len_mm,WIDTH_MM=v_width_mm,HEIGHT_MM=v_height_mm,
   DEFAULT_MAX_CLIENT_PALLETS=v_max_clients,ACTIVE=v_active,FINAL_WEIGHT_REQUIRED=nvl(v_required,d.FINAL_WEIGHT_REQUIRED),TYPE_VERSION=d.TYPE_VERSION+1,UPDATED_AT=systimestamp,UPDATED_BY=p_actor
  when not matched then insert(PALLET_TYPE_ID,PALLET_TYPE_CODE,PALLET_TYPE_NAME,LOAD_UNIT_CLASS,DEFAULT_VOLUME_M3,DEFAULT_WEIGHT_KG,
   LENGTH_MM,WIDTH_MM,HEIGHT_MM,DEFAULT_MAX_CLIENT_PALLETS,ACTIVE,FINAL_WEIGHT_REQUIRED,CREATED_AT,CREATED_BY)
   values(v_id,v_code,name_value,class_value,v_volume,v_weight,len_mm,v_width_mm,v_height_mm,v_max_clients,v_active,nvl(v_required,0),systimestamp,p_actor);
  clear_context;p_id:=v_id;
 exception when others then clear_context;raise;
 end;
end;
/
create context RRL_PALLET_TYPE_CTX using RRL_PALLET_TYPE_API;
