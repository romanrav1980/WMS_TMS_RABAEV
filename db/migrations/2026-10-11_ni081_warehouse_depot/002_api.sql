create or replace package RRL_WARE_DEPOT_API authid definer as
 function write_allowed return number;
 procedure material(p_ware number,p_result out clob);
 procedure context(p_ware number,p_actor varchar2,p_result out clob);
 procedure apply_setting(p_operation varchar2,p_actor varchar2,p_body clob,p_result out clob);
end;
/
create or replace package body RRL_WARE_DEPOT_API as
 g_tx varchar2(100);
 function write_allowed return number is begin
  if g_tx is not null and g_tx=dbms_transaction.local_transaction_id(false)then return 1;end if;return 0;
 end;
 procedure scope(p_ware number,p_actor varchar2)is n number;begin
  select count(*)into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0 and RRL_HAS_WRIGHT(ID,'warehouse_settings_edit')=1
   and(WARE_ID=p_ware or upper(trim(USER_GROUP))='GLOBAL_ADMIN');
  if n!=1 then raise_application_error(-20882,'WARE_DEPOT_CURRENT_WARE_ACTOR_REQUIRED');end if;
  select count(*)into n from RRL_WARES where ID=p_ware;
  if n!=1 then raise_application_error(-20886,'WARE_DEPOT_WAREHOUSE_NOT_UNIQUE');end if;
 end;
 procedure material(p_ware number,p_result out clob)is
  b json_object_t:=json_object_t();v_version number;v_addr varchar2(200);n number;lat number;lon number;
 begin
  select nvl(max(VERSION_NO),0)into v_version from RRL_WARE_DEPOT_HISTORY where WARE_ID=p_ware;
  if v_version>0 then select DEPOT_ADDR into v_addr from RRL_WARE_DEPOT_HISTORY where WARE_ID=p_ware and VERSION_NO=v_version;end if;
  b.put('warehouse_id',p_ware);b.put('version',v_version);b.put('depot_address',v_addr);
  if v_addr is not null then
   select count(*),min(SHIROTA),min(DOLGOTA)into n,lat,lon from RRL_ADDR where ADDR=v_addr and nvl(DELETED3,0)=0;
  else n:=0;end if;
  if n=1 and lat is not null and lon is not null and lat!=0 and lon!=0 and lat between -90 and 90 and lon between -180 and 180 then
   b.put('latitude',lat);b.put('longitude',lon);b.put('configured',true);b.put('status','CONFIGURED_REFERENCE');
  else
   b.put_null('latitude');b.put_null('longitude');b.put('configured',false);b.put('status',case when v_addr is null then 'NOT_CONFIGURED'else 'ADDRESS_GEOMETRY_UNKNOWN'end);
  end if;
  b.put('physical_site_verified',false);p_result:=b.to_clob;
 end;
 procedure context(p_ware number,p_actor varchar2,p_result out clob)is begin scope(p_ware,p_actor);material(p_ware,p_result);end;
 procedure apply_setting(p_operation varchar2,p_actor varchar2,p_body clob,p_result out clob)is
  b json_object_t;ware number;v_version number;v_addr varchar2(1000);v_reason varchar2(2000);hash varchar2(64);n number;
  saved RRL_WARE_DEPOT_HISTORY%rowtype;entered boolean:=false;sp boolean:=false;answer json_object_t;
 begin
  if p_operation is null or lengthb(p_operation)>100 or not regexp_like(p_operation,'^[A-Za-z0-9_.:-]+$')or p_body is null or dbms_lob.getlength(p_body)>4000 then raise_application_error(-20886,'WARE_DEPOT_REQUEST_BOUND');end if;
  b:=json_object_t.parse(p_body);ware:=b.get_number('warehouse_id');v_addr:=b.get_string('depot_address');v_reason:=b.get_string('reason');
  if b.get_size!=4 or ware is null or ware<=0 or trunc(ware)!=ware or b.get_number('expected_version')is null or b.get_number('expected_version')<0 or trunc(b.get_number('expected_version'))!=b.get_number('expected_version')
   or trim(v_reason)is null or length(trim(v_reason))<8 or length(v_reason)>500 or lengthb(v_addr)>200 then raise_application_error(-20886,'WARE_DEPOT_EXPLICIT_REQUEST_REQUIRED');end if;
  scope(ware,p_actor);hash:=lower(rawtohex(sys.dbms_crypto.hash(p_body,sys.dbms_crypto.hash_sh256)));
  RRL_STOCK_METADATA_TX.begin_change(p_actor,'warehouse_settings_edit');entered:=true;savepoint WARE_DEPOT285;sp:=true;scope(ware,p_actor);
  begin select *into saved from RRL_WARE_DEPOT_HISTORY where OPERATION_ID=p_operation;
   if saved.WARE_ID!=ware or saved.ACTOR!=p_actor or saved.REQUEST_HASH!=hash or dbms_lob.compare(saved.REQUEST_JSON,p_body)!=0 then raise_application_error(-20886,'WARE_DEPOT_OPERATION_PAYLOAD_CONFLICT');end if;
   p_result:=saved.RESULT_JSON;RRL_STOCK_METADATA_TX.end_change;return;
  exception when no_data_found then null;end;
  select nvl(max(VERSION_NO),0)into v_version from RRL_WARE_DEPOT_HISTORY where WARE_ID=ware;
  if v_version!=b.get_number('expected_version')then raise_application_error(-20886,'WARE_DEPOT_VERSION_CHANGED');end if;
  if v_addr is not null then
   select count(*)into n from RRL_ADDR where ADDR=v_addr and nvl(DELETED3,0)=0 and SHIROTA between -90 and 90 and DOLGOTA between -180 and 180 and SHIROTA!=0 and DOLGOTA!=0;
   if n!=1 then raise_application_error(-20886,'WARE_DEPOT_EXISTING_GEOCODED_ADDRESS_REQUIRED');end if;
  end if;
  answer:=json_object_t();answer.put('operation_id',p_operation);answer.put('warehouse_id',ware);answer.put('version',v_version+1);
  answer.put('depot_address',v_addr);answer.put('reason',v_reason);answer.put('actor',p_actor);answer.put('stock_changed',false);answer.put('physical_site_verified',false);
  p_result:=answer.to_clob;g_tx:=dbms_transaction.local_transaction_id(false);
  insert into RRL_WARE_DEPOT_HISTORY(OPERATION_ID,WARE_ID,VERSION_NO,DEPOT_ADDR,ACTOR,REASON_TEXT,REQUEST_HASH,REQUEST_JSON,RESULT_JSON)
   values(p_operation,ware,v_version+1,v_addr,p_actor,v_reason,hash,p_body,p_result);
  g_tx:=null;RRL_STOCK_METADATA_TX.end_change;
 exception when others then g_tx:=null;if sp then rollback to WARE_DEPOT285;end if;if entered then RRL_STOCK_METADATA_TX.end_change;end if;raise;
 end;
end;
/
create or replace trigger RRL_WARE_DEPOT_GUARD before insert or update or delete on RRL_WARE_DEPOT_HISTORY for each row
begin
 if updating or deleting or RRL_WARE_DEPOT_API.write_allowed!=1 then raise_application_error(-20863,'WARE_DEPOT_IMMUTABLE_NATIVE_ONLY');end if;
end;
/
