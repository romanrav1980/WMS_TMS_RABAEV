create or replace package body RRL_OPC_EVIDENCE_API as
 procedure clear_context is begin
  dbms_session.set_context('RRL_OPC_EVIDENCE_CTX','TX_ID',null);
  dbms_session.set_context('RRL_OPC_EVIDENCE_CTX','HASH',null);
 end;
 procedure assert_sender(p_kind varchar2,p_device varchar2,p_actor nvarchar2,p_scope out varchar2,p_post out varchar2)is
  sender_value nvarchar2(50);right_value varchar2(100);n number;
 begin
  if p_kind='STORE_RECEIPT'then
   select SENDER_ID,STORE_ADDR,null into sender_value,p_scope,p_post from RRL_STORE_SCALE_DEVICE where DEVICE_ID=p_device;
   right_value:='store_scale_ingest';
  elsif p_kind in('WAREHOUSE_PICK','WAREHOUSE_FINAL')then
   select SENDER_ID,to_char(WARE_ID),POST_CELL into sender_value,p_scope,p_post from RRL_WH_SCALE_DEVICE where DEVICE_ID=p_device;
   right_value:='warehouse_scale_ingest';
  else raise_application_error(-20881,'OPC_EVIDENCE_KIND_REQUIRED');end if;
  if p_actor is null or sender_value is null or sender_value!=p_actor then raise_application_error(-20882,'OPC_EVIDENCE_DEVICE_SENDER_REQUIRED');end if;
  select count(*)into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0
   and upper(trim(USER_GROUP))!='GLOBAL_ADMIN'and RRL_HAS_WRIGHT(ID,right_value)=1
   and(p_kind='STORE_RECEIPT'or to_char(WARE_ID)=p_scope);
  if n!=1 then raise_application_error(-20882,'OPC_EVIDENCE_CURRENT_SENDER_REQUIRED');end if;
 exception when no_data_found then raise_application_error(-20882,'OPC_EVIDENCE_CURRENT_DEVICE_REQUIRED');
 end;
 function binding(r RRL_OPC_SCALE_EVIDENCE%rowtype)return varchar2 is h varchar2(64);purpose varchar2(30);sender_value nvarchar2(50);
 begin
  if r.CAPTURE_KIND='STORE_RECEIPT'then
   select SOURCE_SHA256,RECORDED_BY into h,sender_value from RRL_STORE_SCALE_CAPTURE
    where DEVICE_ID=r.CAPTURE_DEVICE and CAPTURE_ID=r.CAPTURE_ID and STORE_ADDR=r.DEVICE_SCOPE;
  else
   select SOURCE_SHA256,CAPTURE_PURPOSE,RECORDED_BY into h,purpose,sender_value from RRL_WH_SCALE_CAPTURE
    where DEVICE_ID=r.CAPTURE_DEVICE and CAPTURE_ID=r.CAPTURE_ID and to_char(WARE_ID)=r.DEVICE_SCOPE and POST_CELL=r.DEVICE_POST;
   if(r.CAPTURE_KIND='WAREHOUSE_PICK'and purpose!='PICK')or(r.CAPTURE_KIND='WAREHOUSE_FINAL'and purpose not in('EMPTY_TARE','FINAL_GROSS'))then
    raise_application_error(-20886,'OPC_EVIDENCE_CAPTURE_PURPOSE_CONFLICT');end if;
  end if;
  if sender_value is null or sender_value!=r.RECORDED_BY then raise_application_error(-20882,'OPC_EVIDENCE_ORIGINAL_SENDER_REQUIRED');end if;
  if h is null or h!=r.CAPTURE_SHA256 then raise_application_error(-20886,'OPC_EVIDENCE_CAPTURE_HASH_CONFLICT');end if;
  return 'MATCHED';
 exception when no_data_found then return 'PENDING';
 end;
 function result_json(r RRL_OPC_SCALE_EVIDENCE%rowtype)return clob is j json_object_t:=json_object_t();
 begin
  j.put('protocol_version','1.0');j.put('capture_kind',r.CAPTURE_KIND);j.put('device_id',r.CAPTURE_DEVICE);j.put('capture_id',r.CAPTURE_ID);
  j.put('capture_sha256',r.CAPTURE_SHA256);j.put('evidence_sha256',r.EVIDENCE_SHA256);
  j.put('status','ARCHIVED');j.put('binding',binding(r));j.put('provenance','GATEWAY_REPORTED');j.put('stock_posted',false);
  j.put('recorded_at',to_char(r.RECORDED_AT,'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM'));return j.to_clob;
 end;
 procedure describe(p_kind varchar2,p_device varchar2,p_capture varchar2,p_actor nvarchar2,p_result out clob)is
  r RRL_OPC_SCALE_EVIDENCE%rowtype;scope_value varchar2(255);post_value varchar2(100);
 begin
  assert_sender(p_kind,p_device,p_actor,scope_value,post_value);
  select *into r from RRL_OPC_SCALE_EVIDENCE where CAPTURE_KIND=p_kind and CAPTURE_DEVICE=p_device and CAPTURE_ID=p_capture;
  if r.RECORDED_BY!=p_actor or r.DEVICE_SCOPE!=scope_value or nvl(r.DEVICE_POST,chr(1))!=nvl(post_value,chr(1))then
   raise_application_error(-20882,'OPC_EVIDENCE_ORIGINAL_SCOPE_REQUIRED');end if;
  p_result:=result_json(r);
 exception when no_data_found then raise_application_error(-20884,'OPC_EVIDENCE_NOT_FOUND');
 end;
 procedure archive(p_source clob,p_actor nvarchar2,p_result out clob)is
  j json_object_t;r RRL_OPC_SCALE_EVIDENCE%rowtype;scope_value varchar2(255);post_value varchar2(100);n number;state_value varchar2(20);
 begin
  if sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')is not null then raise_application_error(-20886,'OPC_EVIDENCE_OUTSIDE_STOCK_REQUIRED');end if;
  if p_source is null or dbms_lob.getlength(p_source)>131072 then raise_application_error(-20881,'OPC_EVIDENCE_BOUND_128K');end if;
  j:=json_object_t.parse(p_source);j.on_error(1);
  if j.get_string('protocol_version')is null or j.get_string('protocol_version')!='1.0'
   or j.get_string('model_namespace_uri')is null or j.get_string('model_namespace_uri')!='http://opcfoundation.org/UA/Scales/V2/'then
   raise_application_error(-20881,'OPC_EVIDENCE_PROTOCOL_REQUIRED');end if;
  if not j.has('observations')or not j.get('observations').is_array
   or not j.has('zero_observation')or not j.get('zero_observation').is_object
   or not j.has('nodes')or not j.get('nodes').is_object
   or not j.has('opc_server')or not j.get('opc_server').is_object then
   raise_application_error(-20881,'OPC_EVIDENCE_OBSERVATIONS_REQUIRED');end if;
  n:=j.get_array('observations').get_size;
  if n<5 or n>25 then raise_application_error(-20881,'OPC_EVIDENCE_OBSERVATION_BOUND');end if;
  if j.get_string('profile_sha256')is null or not regexp_like(j.get_string('profile_sha256'),'^[A-F0-9]{64}$')
   or j.get_string('station_id')is null then raise_application_error(-20881,'OPC_EVIDENCE_PROFILE_REQUIRED');end if;
  r.CAPTURE_KIND:=j.get_string('capture_kind');r.CAPTURE_DEVICE:=j.get_string('device_id');r.CAPTURE_ID:=j.get_string('capture_id');
  r.CAPTURE_SHA256:=j.get_string('capture_sha256');
  if r.CAPTURE_KIND is null or r.CAPTURE_DEVICE is null or r.CAPTURE_ID is null or r.CAPTURE_SHA256 is null
   or not regexp_like(r.CAPTURE_SHA256,'^[A-F0-9]{64}$')then raise_application_error(-20881,'OPC_EVIDENCE_IDENTITY_REQUIRED');end if;
  assert_sender(r.CAPTURE_KIND,r.CAPTURE_DEVICE,p_actor,scope_value,post_value);
  lock table RRL_ACCESS_REV in share mode wait 2;
  -- Device row serializes archive identity without holding any human/OPC wait.
  if r.CAPTURE_KIND='STORE_RECEIPT'then
   declare d varchar2(100);begin select DEVICE_ID into d from RRL_STORE_SCALE_DEVICE where DEVICE_ID=r.CAPTURE_DEVICE for update wait 2;end;
  else
   declare d varchar2(100);begin select DEVICE_ID into d from RRL_WH_SCALE_DEVICE where DEVICE_ID=r.CAPTURE_DEVICE for update wait 2;end;
  end if;
  -- Recheck sender after the device lock, not only at preflight.
  assert_sender(r.CAPTURE_KIND,r.CAPTURE_DEVICE,p_actor,scope_value,post_value);
  r.EVIDENCE_SHA256:=rawtohex(sys.dbms_crypto.hash(p_source,sys.dbms_crypto.hash_sh256));
  select count(*)into n from RRL_OPC_SCALE_EVIDENCE where CAPTURE_KIND=r.CAPTURE_KIND and CAPTURE_DEVICE=r.CAPTURE_DEVICE and CAPTURE_ID=r.CAPTURE_ID;
  if n=1 then
   declare saved RRL_OPC_SCALE_EVIDENCE%rowtype;begin
    select *into saved from RRL_OPC_SCALE_EVIDENCE where CAPTURE_KIND=r.CAPTURE_KIND and CAPTURE_DEVICE=r.CAPTURE_DEVICE and CAPTURE_ID=r.CAPTURE_ID;
    if saved.EVIDENCE_SHA256!=r.EVIDENCE_SHA256 or dbms_lob.compare(saved.SOURCE_JSON,p_source)!=0 then raise_application_error(-20886,'OPC_EVIDENCE_PAYLOAD_CONFLICT');end if;
   end;
   describe(r.CAPTURE_KIND,r.CAPTURE_DEVICE,r.CAPTURE_ID,p_actor,p_result);return;
  end if;
  r.DEVICE_SCOPE:=scope_value;r.DEVICE_POST:=post_value;r.RECORDED_BY:=p_actor;r.RECORDED_AT:=systimestamp;r.SOURCE_JSON:=p_source;
  state_value:=binding(r);
  dbms_session.set_context('RRL_OPC_EVIDENCE_CTX','TX_ID',dbms_transaction.local_transaction_id(true));
  dbms_session.set_context('RRL_OPC_EVIDENCE_CTX','HASH',r.EVIDENCE_SHA256);
  insert into RRL_OPC_SCALE_EVIDENCE values r;
  clear_context;p_result:=result_json(r);
 exception when others then clear_context;raise;
 end;
end;
/
