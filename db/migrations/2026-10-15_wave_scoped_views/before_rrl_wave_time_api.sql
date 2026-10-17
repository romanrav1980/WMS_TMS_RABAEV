create or replace package body RRL_WAVE_TIME_API as
 g_operation varchar2(100);g_tx varchar2(100);
 function write_allowed(p_operation varchar2)return number is begin
  if g_operation=p_operation and g_tx=dbms_transaction.local_transaction_id(false)then return 1;end if;return 0;
 end;
 procedure actor_allowed(p_actor varchar2,p_ware number,p_right varchar2)is n number;begin
  select count(*)into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0 and
   (WARE_ID=p_ware or upper(trim(USER_GROUP))='GLOBAL_ADMIN')and RRL_HAS_WRIGHT(ID,p_right)=1;
  if n!=1 then raise_application_error(-20882,'WAVE_TIME_CURRENT_WARE_RIGHT_REQUIRED');end if;
 end;
 function token(p_wave RRL_PICK_WAVE%rowtype,p_version number)return varchar2 is v_text varchar2(4000);v_hash varchar2(64);begin
  v_text:=p_wave.PICK_WAVE_ID||'|'||p_wave.WARE_ID||'|'||p_wave.ROUTE_ID||'|'||p_wave.DOCK_ID||'|'||p_wave.STATUS||'|'||
   to_char(p_wave.PLANNED_START_AT,'YYYYMMDDHH24MISS')||'|'||to_char(p_wave.PLANNED_FINISH_AT,'YYYYMMDDHH24MISS')||'|'||
   to_char(p_wave.UPDATED_AT,'YYYYMMDDHH24MISS')||'|'||p_version;
  select lower(rawtohex(standard_hash(v_text,'SHA256')))into v_hash from dual;return v_hash;
 end;
 procedure context(p_wave number,p_actor varchar2,p_result out clob)is
  w RRL_PICK_WAVE%rowtype;v_version number;p RRL_WAVE_TIME_PLAN%rowtype;b json_object_t:=json_object_t();
 begin
  select *into w from RRL_PICK_WAVE where PICK_WAVE_ID=p_wave;
  actor_allowed(p_actor,w.WARE_ID,'pick_wave_view');
  select nvl(max(VERSION_NO),0)into v_version from RRL_WAVE_TIME_PLAN where WAVE_ID=p_wave;
  b.put('wave_id',p_wave);b.put('warehouse_id',w.WARE_ID);b.put('wave_status',w.STATUS);b.put('version',v_version);
  b.put('source_token',token(w,v_version));b.put('plan_status','NO_APPROVED_PLAN');
  if v_version>0 then
   select *into p from RRL_WAVE_TIME_PLAN where WAVE_ID=p_wave and VERSION_NO=v_version;
   if w.WARE_ID=p.WARE_ID and nvl(w.ROUTE_ID,-1)=nvl(p.ROUTE_ID,-1)and nvl(w.DOCK_ID,-1)=nvl(p.DOCK_ID,-1)
     and w.PLANNED_START_AT=p.LEGACY_START_AT and w.PLANNED_FINISH_AT=p.LEGACY_FINISH_AT then
    b.put('plan_status','APPROVED');b.put('time_zone',p.TIME_ZONE);
    b.put('start_at',to_char(p.START_AT at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM'));
    b.put('finish_at',to_char(p.FINISH_AT at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM'));
   else b.put('plan_status','LEGACY_PLAN_CHANGED');end if;
  end if;
  p_result:=b.to_clob;
 end;
 procedure approve(p_operation varchar2,p_actor varchar2,p_body clob,p_result out clob)is
  b json_object_t;w RRL_PICK_WAVE%rowtype;saved RRL_WAVE_TIME_PLAN%rowtype;
  v_wave number;v_version number;v_hash varchar2(64);v_text varchar2(4000);v_zone varchar2(50);
  v_start timestamp with time zone;v_finish timestamp with time zone;v_legacy_start date;v_legacy_finish date;
  n number;result json_object_t:=json_object_t();v_reason varchar2(1000);v_metadata boolean:=false;
 begin
  if p_operation is null or lengthb(p_operation)>100 or p_body is null or dbms_lob.getlength(p_body)>2000 then raise_application_error(-20886,'WAVE_TIME_INPUT_BOUND');end if;
  b:=json_object_t.parse(p_body);v_wave:=b.get_number('wave_id');
  select *into w from RRL_PICK_WAVE where PICK_WAVE_ID=v_wave;actor_allowed(p_actor,w.WARE_ID,'pick_wave_launch');
  v_text:=dbms_lob.substr(p_body,2000,1);select lower(rawtohex(standard_hash(v_text,'SHA256')))into v_hash from dual;
  RRL_STOCK_METADATA_TX.begin_change(p_actor,'pick_wave_launch');v_metadata:=true; savepoint RRL_WAVE_TIME140;
  select *into w from RRL_PICK_WAVE where PICK_WAVE_ID=v_wave for update;actor_allowed(p_actor,w.WARE_ID,'pick_wave_launch');
  begin
   select *into saved from RRL_WAVE_TIME_PLAN where OPERATION_ID=p_operation;
   if saved.ACTOR!=p_actor or saved.REQUEST_HASH!=v_hash or saved.WAVE_ID!=v_wave or saved.WARE_ID!=w.WARE_ID then raise_application_error(-20886,'WAVE_TIME_OPERATION_PAYLOAD_CONFLICT');end if;
   p_result:=saved.RESULT_JSON;RRL_STOCK_METADATA_TX.end_change;return;
  exception when no_data_found then null;end;
  select nvl(max(VERSION_NO),0)into v_version from RRL_WAVE_TIME_PLAN where WAVE_ID=v_wave;
  if b.get_number('expected_version') is null or b.get_string('source_token') is null or b.get_number('expected_version')!=v_version or b.get_string('source_token')!=token(w,v_version)then raise_application_error(-20886,'WAVE_TIME_SOURCE_CHANGED');end if;
  if w.STATUS in('DONE','CANCELLED')then raise_application_error(-20886,'WAVE_TIME_ACTIVE_PLAN_REQUIRED');end if;
  select count(*)into n from RRL_CASE_PICK_TASK where PICK_WAVE_ID=v_wave and STATUS in('IN_PROGRESS','PARTIAL');
  if n>0 then raise_application_error(-20886,'WAVE_TIME_EXECUTION_ALREADY_STARTED');end if;
  select count(*)into n from RRL_WAREHOUSE_TASK where TASK_SOURCE='WAVE'and SOURCE_DOC_ID=v_wave and STATUS='IN_PROGRESS';
  if n>0 then raise_application_error(-20886,'WAVE_TIME_EXECUTION_ALREADY_STARTED');end if;
  v_zone:=b.get_string('time_zone');
  if v_zone not in('UTC','Europe/Moscow','Asia/Tbilisi')or v_zone is null then raise_application_error(-20886,'WAVE_TIME_EXPLICIT_REGION_REQUIRED');end if;
  v_start:=to_timestamp_tz(b.get_string('start_at'),'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM');
  v_finish:=to_timestamp_tz(b.get_string('finish_at'),'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM');
  if v_start is null or v_finish is null or v_finish<=v_start or v_finish-v_start>interval '1'day then raise_application_error(-20886,'WAVE_TIME_POSITIVE_MAX24H_REQUIRED');end if;
  v_reason:=b.get_string('reason');if v_reason is null or length(v_reason)<8 or lengthb(v_reason)>1000 then raise_application_error(-20886,'WAVE_TIME_APPROVAL_REASON_REQUIRED');end if;
  select cast(v_start at time zone (v_zone) as date),cast(v_finish at time zone (v_zone) as date)into v_legacy_start,v_legacy_finish from dual;
  update RRL_PICK_WAVE set PLANNED_START_AT=v_legacy_start,PLANNED_FINISH_AT=v_legacy_finish,UPDATED_AT=sysdate,UPDATED_BY=p_actor where PICK_WAVE_ID=v_wave;
  result.put('wave_id',v_wave);result.put('warehouse_id',w.WARE_ID);result.put('version',v_version+1);
  result.put('operation_id',p_operation);result.put('plan_status','APPROVED');result.put('time_zone',v_zone);
  result.put('start_at',b.get_string('start_at'));result.put('finish_at',b.get_string('finish_at'));
  result.put('stock_changed',false);result.put('task_assignments_changed',false);result.put('capacity_certified',false);
  p_result:=result.to_clob;g_operation:=p_operation;g_tx:=dbms_transaction.local_transaction_id(false);
  insert into RRL_WAVE_TIME_PLAN(WAVE_ID,VERSION_NO,OPERATION_ID,ACTOR,REQUEST_HASH,WARE_ID,ROUTE_ID,DOCK_ID,START_AT,FINISH_AT,TIME_ZONE,LEGACY_START_AT,LEGACY_FINISH_AT,REASON,RESULT_JSON)
   values(v_wave,v_version+1,p_operation,p_actor,v_hash,w.WARE_ID,w.ROUTE_ID,w.DOCK_ID,v_start,v_finish,v_zone,v_legacy_start,v_legacy_finish,v_reason,p_result);
  g_operation:=null;g_tx:=null;RRL_STOCK_METADATA_TX.end_change;
 exception when others then
  if v_metadata then rollback to RRL_WAVE_TIME140;end if;g_operation:=null;g_tx:=null;
  if v_metadata then RRL_STOCK_METADATA_TX.end_change;end if;raise;
 end;
end;
/
