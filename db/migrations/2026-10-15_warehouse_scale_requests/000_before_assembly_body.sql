create or replace package body RRL_ASSEMBLY_SCALE_API as
 procedure permit(p_kind varchar2)is begin
  dbms_session.set_context('RRL_ASSEMBLY_CTX','TX_ID',dbms_transaction.local_transaction_id(true));
  dbms_session.set_context('RRL_ASSEMBLY_CTX','KIND',p_kind);
 end;
 procedure clear_context is begin
  dbms_session.set_context('RRL_ASSEMBLY_CTX','TX_ID',null);dbms_session.set_context('RRL_ASSEMBLY_CTX','KIND',null);
 end;
 function write_allowed(p_kind varchar2)return number is k varchar2(20):=sys_context('RRL_ASSEMBLY_CTX','KIND');begin
  if sys_context('RRL_ASSEMBLY_CTX','TX_ID')is null or sys_context('RRL_ASSEMBLY_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)then return 0;end if;
  if(p_kind='POLICY'and k='CONFIG')or(p_kind='STATE'and k in('META','USE'))or(p_kind='CAPTURE'and k='META')or(p_kind='USE'and k='USE')then return 1;end if;
  return 0;
 end;
 procedure begin_meta(p_actor nvarchar2)is begin
  if sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')is not null then raise_application_error(-20886,'ASSEMBLY_METADATA_OUTSIDE_STOCK_REQUIRED');end if;
  RRL_STOCK_METADATA_TX.begin_change(p_actor,'case_pick_execute');
  lock table RRL_ACCESS_REV in share mode wait 2;permit('META');
 end;
 procedure end_meta is begin clear_context;RRL_STOCK_METADATA_TX.end_change;end;
 procedure assert_task(p_task number,p_actor nvarchar2)is t RRL_CASE_PICK_TASK%rowtype;n number;begin
  if p_task is null or p_actor is null then raise_application_error(-20882,'ASSEMBLY_ASSIGNED_OPERATOR_REQUIRED');end if;
  RRL_CASE_TASK_ACCESS.assert_scope(p_task,p_actor,'case_pick_execute');
  select *into t from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=p_task;
  select count(*)into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0;
  if n!=1 or t.ASSIGNED_TO is null or t.ASSIGNED_TO!=p_actor then raise_application_error(-20882,'ASSEMBLY_ASSIGNED_OPERATOR_REQUIRED');end if;
 end;
 procedure assert_sender(p_device varchar2,p_sender nvarchar2)is d RRL_WH_SCALE_DEVICE%rowtype;n number;begin
  if p_device is null or p_sender is null then raise_application_error(-20882,'ASSEMBLY_CURRENT_DEDICATED_SENDER_REQUIRED');end if;
  select *into d from RRL_WH_SCALE_DEVICE where DEVICE_ID=p_device;
  select count(*)into n from RUSERS where ID=p_sender and nvl(DELETED,0)=0 and WARE_ID=d.WARE_ID
   and upper(trim(USER_GROUP))!='GLOBAL_ADMIN'and RRL_HAS_WRIGHT(ID,'warehouse_scale_ingest')=1;
  if n!=1 or p_sender is null or d.SENDER_ID!=p_sender then raise_application_error(-20882,'ASSEMBLY_CURRENT_DEDICATED_SENDER_REQUIRED');end if;
 end;
 procedure assert_device(s RRL_ASSEMBLY_SESSION%rowtype)is d RRL_WH_SCALE_DEVICE%rowtype;p RRL_ASSEMBLY_STATION%rowtype;begin
  select *into d from RRL_WH_SCALE_DEVICE where DEVICE_ID=s.DEVICE_ID;
  select *into p from RRL_ASSEMBLY_STATION where DEVICE_ID=s.DEVICE_ID;
  if d.ACTIVE_FLAG!=1 or d.MEASUREMENT_BASIS!='GROSS'or d.CALIBRATED_UNTIL<systimestamp
   or d.WARE_ID!=s.WARE_ID or d.POST_CELL!=s.POST_CELL or d.DEVICE_MODE!=s.DEVICE_MODE
   or d.POLICY_VERSION!=s.DEVICE_POLICY_VERSION or d.CALIBRATION_REF!=s.CALIBRATION_REF or d.SENDER_ID!=s.SENDER_ID
   or p.ACTIVE_FLAG!=1 or p.VERSION_NO!=s.STATION_POLICY_VERSION or p.CONFIRMATION_MODE!=s.CONFIRMATION_MODE then
   raise_application_error(-20886,'ASSEMBLY_DEVICE_OR_STATION_POLICY_CHANGED');end if;
  assert_sender(s.DEVICE_ID,s.SENDER_ID);
 end;
 procedure assert_open(s RRL_ASSEMBLY_SESSION%rowtype)is t RRL_CASE_PICK_TASK%rowtype;begin
  assert_task(s.CASE_PICK_TASK_ID,s.OPERATOR_ID);assert_device(s);
  select *into t from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=s.CASE_PICK_TASK_ID;
  if s.STATE is null or s.STATE!='OPEN'or s.EXPIRES_AT is null or s.EXPIRES_AT<systimestamp or t.SSCC is null or t.SSCC!=s.CARRIER_IDENTIFIER or t.CONTENT_VERSION is null or t.CONTENT_VERSION!=s.LAST_CONTENT_VERSION then
   raise_application_error(-20886,'ASSEMBLY_SESSION_RECONCILIATION_REQUIRED');end if;
 end;
 procedure assert_count_sku(p_article varchar2,p_base varchar2)is n number;flags number;begin
  select count(*)into n from RRL_ARTICULS where ACTICUL=p_article and nvl(TYPE_W,0)not in(2,3,5,6,7);
  if n!=1 or p_base!='EA'then raise_application_error(-20886,'ASSEMBLY_ORDINARY_COUNT_SKU_REQUIRED');end if;
  select count(*)into n from RRL_STOCK_UOM_CONVERSION where ARTICUL=p_article and INPUT_UOM='EA'and BASE_UOM='EA'and NUMERATOR=1 and DENOMINATOR=1;
  if n!=1 then raise_application_error(-20886,'ASSEMBLY_EXPLICIT_EA_BASE_REQUIRED');end if;
  select greatest(nvl((select max(SERIALIZED_WEIGHT_BOXES)from RRL_SKU_RECEIPT_POLICY where ARTICUL=p_article),0),
   nvl((select max(MARKING_REQUIRED)from RRL_SKU_RECEIPT_POLICY where ARTICUL=p_article),0),
   nvl((select max(CRPT_REQUIRED)from RRL_FINISHED_GOODS_SKU where ARTICUL=p_article),0),
   case when exists(select 1 from RRL_SKU_RECEIPT_PROFILE where ARTICUL=p_article)then 1 else 0 end)into flags from dual;
  if flags!=0 then raise_application_error(-20886,'ASSEMBLY_UNMARKED_UNSERIALIZED_SKU_REQUIRED');end if;
 end;
 function step_json(t RRL_ASSEMBLY_STEP%rowtype)return json_object_t is j json_object_t:=json_object_t();s RRL_ASSEMBLY_SESSION%rowtype;begin
  select *into s from RRL_ASSEMBLY_SESSION where SESSION_ID=t.SESSION_ID;
  j.put('step_id',t.STEP_ID);j.put('session_id',t.SESSION_ID);j.put('operation_id',t.OPERATION_ID);j.put('sequence',t.SEQUENCE_NO);
  j.put('case_line_id',t.CASE_PICK_LINE_ID);j.put('article',t.ARTICUL);j.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(t.QUANTITY));
  j.put('state',t.STATE);j.put('confirmation_mode',s.CONFIRMATION_MODE);j.put('content_version',t.SOURCE_VERSION);
  j.put('before_capture_id',t.BEFORE_CAPTURE_ID);j.put('after_capture_id',t.AFTER_CAPTURE_ID);
  j.put('before_weight_kg',RRL_STOCK_PLAN_HELPER.decimal_text(t.BEFORE_WEIGHT_KG));j.put('after_weight_kg',RRL_STOCK_PLAN_HELPER.decimal_text(t.AFTER_WEIGHT_KG));
  j.put('delta_kg',RRL_STOCK_PLAN_HELPER.decimal_text(t.DELTA_KG));j.put('min_delta_kg',RRL_STOCK_PLAN_HELPER.decimal_text(t.MIN_DELTA_KG));
  j.put('expected_delta_min_kg',RRL_STOCK_PLAN_HELPER.decimal_text(t.LOWER_DELTA_KG));j.put('expected_delta_max_kg',RRL_STOCK_PLAN_HELPER.decimal_text(t.UPPER_DELTA_KG));
  j.put('button_intent',t.BUTTON_INTENT_AT is not null);j.put('consent_to_auto',t.CONSENT_TO_AUTO=1);j.put('block_reason',t.BLOCK_REASON);j.put('stock_posted',t.STATE='APPLIED');
  return j;
 end;
 function session_json(s RRL_ASSEMBLY_SESSION%rowtype)return json_object_t is j json_object_t:=json_object_t();steps json_array_t:=json_array_t();has_older boolean:=false;begin
  j.put('session_id',s.SESSION_ID);j.put('task_id',s.CASE_PICK_TASK_ID);j.put('device_id',s.DEVICE_ID);j.put('post_cell',s.POST_CELL);
  j.put('operator_id',s.OPERATOR_ID);j.put('warehouse_id',s.WARE_ID);j.put('scan_container',s.CARRIER_IDENTIFIER);
  j.put('cumulative_tolerance_kg',RRL_STOCK_PLAN_HELPER.decimal_text(s.CUMULATIVE_TOLERANCE_KG));
  j.put('state',s.STATE);j.put('confirmation_mode',s.CONFIRMATION_MODE);j.put('content_version',s.LAST_CONTENT_VERSION);
  j.put('tare_capture_key',s.TARE_CAPTURE_KEY);j.put('tare_weight_kg',RRL_STOCK_PLAN_HELPER.decimal_text(s.TARE_WEIGHT_KG));j.put('last_weight_kg',RRL_STOCK_PLAN_HELPER.decimal_text(s.LAST_WEIGHT_KG));
  j.put('expires_at',to_char(s.EXPIRES_AT at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM'));j.put('block_reason',s.BLOCK_REASON);
  for t in(select *from RRL_ASSEMBLY_STEP where SESSION_ID=s.SESSION_ID order by SEQUENCE_NO desc fetch first 51 rows only)loop
   if steps.get_size<50 then steps.append(step_json(t));else has_older:=true;end if;
  end loop;j.put('steps',steps);j.put('has_older',has_older);j.put_null('reconciliation');
  for v in(select *from RRL_ASM_RECONCILIATION where SESSION_ID=s.SESSION_ID order by REQUESTED_AT desc fetch first 1 row only)loop
   declare o json_object_t:=json_object_t();begin
    o.put('case_task_id',s.CASE_PICK_TASK_ID);o.put('reconciliation_id',v.RECONCILIATION_ID);o.put('session_id',s.SESSION_ID);o.put('step_id',v.STEP_ID);o.put('state',v.STATE);
    o.put('requester_id',v.REQUESTER_ID);o.put('controller_id',v.CONTROLLER_ID);o.put('expected_content_version',v.EXPECTED_CONTENT_VERSION);
    o.put('expected_weight_kg',RRL_STOCK_PLAN_HELPER.decimal_text(v.EXPECTED_WEIGHT_KG));o.put('reason',json_object_t.parse(v.REQUEST_JSON).get_string('reason'));j.put('reconciliation',o);end;
  end loop;return j;
 end;
 procedure read_session(p_session varchar2,p_actor nvarchar2,p_result out clob)is s RRL_ASSEMBLY_SESSION%rowtype;begin
  select *into s from RRL_ASSEMBLY_SESSION where SESSION_ID=p_session;assert_task(s.CASE_PICK_TASK_ID,p_actor);
  if s.OPERATOR_ID!=p_actor then raise_application_error(-20882,'ASSEMBLY_SESSION_OPERATOR_REQUIRED');end if;p_result:=session_json(s).to_clob;
 end;
 procedure read_step(p_step varchar2,p_actor nvarchar2,p_result out clob)is t RRL_ASSEMBLY_STEP%rowtype;s RRL_ASSEMBLY_SESSION%rowtype;begin
  select *into t from RRL_ASSEMBLY_STEP where STEP_ID=p_step;select *into s from RRL_ASSEMBLY_SESSION where SESSION_ID=t.SESSION_ID;
  assert_task(s.CASE_PICK_TASK_ID,p_actor);if s.OPERATOR_ID!=p_actor then raise_application_error(-20882,'ASSEMBLY_SESSION_OPERATOR_REQUIRED');end if;p_result:=step_json(t).to_clob;
 end;
 procedure assert_config_actor(p_actor nvarchar2,p_ware number)is n number;own_ware number;group_value varchar2(100);begin
  if p_actor is null or p_ware is null then raise_application_error(-20882,'ASSEMBLY_CURRENT_CONFIGURATION_SCOPE_REQUIRED');end if;
  select count(*)into n from RRL_WARES where ID=p_ware;
  if n!=1 then raise_application_error(-20886,'ASSEMBLY_CONFIGURATION_WAREHOUSE_REQUIRED');end if;
  select WARE_ID,upper(trim(USER_GROUP))into own_ware,group_value from RUSERS where ID=p_actor and nvl(DELETED,0)=0;
  if RRL_HAS_WRIGHT(p_actor,'warehouse_settings_edit')!=1 or group_value is null or(group_value!='GLOBAL_ADMIN'and(own_ware is null or own_ware!=p_ware))then
   raise_application_error(-20882,'ASSEMBLY_CURRENT_CONFIGURATION_SCOPE_REQUIRED');end if;
 exception when no_data_found then raise_application_error(-20882,'ASSEMBLY_CURRENT_CONFIGURATION_SCOPE_REQUIRED');end;
 function policy_receipt(p_request clob,p_actor nvarchar2,p_kind varchar2,p_key varchar2)return clob is j json_object_t:=json_object_t.parse(p_request);e RRL_ASSEMBLY_POLICY_EVENT%rowtype;r json_object_t:=json_object_t();op varchar2(100):=j.get_string('operation_id');begin
  select *into e from RRL_ASSEMBLY_POLICY_EVENT where OPERATION_ID=op;
  if p_actor is null or e.ACTOR!=p_actor or e.POLICY_KIND!=p_kind or e.POLICY_KEY!=p_key or dbms_lob.compare(e.SOURCE_JSON,p_request)!=0 then raise_application_error(-20886,'ASSEMBLY_POLICY_OPERATION_CONFLICT');end if;
  r.put('version',e.VERSION_NO);r.put('policy_kind',e.POLICY_KIND);r.put('operation_id',e.OPERATION_ID);return r.to_clob;
 exception when no_data_found then return null;end;
 procedure station_policy(p_device varchar2,p_request clob,p_actor nvarchar2,p_result out clob)is
  j json_object_t:=json_object_t.parse(p_request);d RRL_WH_SCALE_DEVICE%rowtype;version_no number;active_no number;mode_value varchar2(10);duration_no number;cumulative_no number;op varchar2(100);r json_object_t:=json_object_t();
 begin
  RRL_STOCK_CONFIG_API.begin_change(p_actor,'warehouse_settings_edit');permit('CONFIG');
  select *into d from RRL_WH_SCALE_DEVICE where DEVICE_ID=p_device for update;assert_config_actor(p_actor,d.WARE_ID);
  p_result:=policy_receipt(p_request,p_actor,'STATION',p_device);if p_result is not null then clear_context;RRL_STOCK_CONFIG_API.end_change;return;end if;
  if d.MEASUREMENT_BASIS!='GROSS'then raise_application_error(-20886,'ASSEMBLY_GROSS_STATION_REQUIRED');end if;
  select nvl(max(VERSION_NO),0)into version_no from RRL_ASSEMBLY_STATION where DEVICE_ID=p_device;
  if j.get_number('expected_version')is null or j.get_number('expected_version')!=version_no then raise_application_error(-20886,'ASSEMBLY_POLICY_VERSION_CONFLICT');end if;
  mode_value:=j.get_string('confirmation_mode');duration_no:=j.get_number('max_session_seconds');op:=j.get_string('operation_id');
  if mode_value is null or mode_value not in('AUTO','BUTTON')or duration_no is null or duration_no!=trunc(duration_no)or duration_no not between 60 and 28800
   or op is null or lengthb(op)>100 then raise_application_error(-20886,'ASSEMBLY_EXPLICIT_STATION_POLICY_REQUIRED');end if;
  if regexp_like(j.get_string('cumulative_tolerance_kg'),'^0{1,18}([.]0{1,9})?$','c')then cumulative_no:=0;else cumulative_no:=RRL_STOCK_MATH.quantity(j.get_string('cumulative_tolerance_kg'));end if;
  if cumulative_no is null or cumulative_no<0 then raise_application_error(-20886,'ASSEMBLY_EXPLICIT_CUMULATIVE_TOLERANCE_REQUIRED');end if;
  if j.get_boolean('active')then active_no:=1;else active_no:=0;end if;
  merge into RRL_ASSEMBLY_STATION t using(select p_device DEVICE_ID from dual)x on(t.DEVICE_ID=x.DEVICE_ID)
   when matched then update set VERSION_NO=version_no+1,CONFIRMATION_MODE=mode_value,MAX_SESSION_SECONDS=duration_no,CUMULATIVE_TOLERANCE_KG=cumulative_no,ACTIVE_FLAG=active_no,CHANGED_BY=p_actor,CHANGED_AT=systimestamp
   when not matched then insert(DEVICE_ID,VERSION_NO,CONFIRMATION_MODE,MAX_SESSION_SECONDS,CUMULATIVE_TOLERANCE_KG,ACTIVE_FLAG,CHANGED_BY)values(p_device,1,mode_value,duration_no,cumulative_no,active_no,p_actor);
  insert into RRL_ASSEMBLY_POLICY_EVENT(OPERATION_ID,POLICY_KIND,POLICY_KEY,VERSION_NO,SOURCE_JSON,ACTOR)
   values(op,'STATION',p_device,version_no+1,p_request,p_actor);
  r.put('version',version_no+1);r.put('policy_kind','STATION');r.put('operation_id',op);p_result:=r.to_clob;clear_context;RRL_STOCK_CONFIG_API.end_change;
 exception when others then clear_context;RRL_STOCK_CONFIG_API.end_change;raise;end;
 procedure sku_policy(p_request clob,p_actor nvarchar2,p_result out clob)is
  j json_object_t:=json_object_t.parse(p_request);ware number:=j.get_number('warehouse_id');article varchar2(100):=j.get_string('article');
  version_no number;active_no number;lower_no number;upper_no number;minimum_no number;tolerance_no number;reference_value varchar2(200);base_value varchar2(20);op varchar2(100);r json_object_t:=json_object_t();
 begin
  RRL_STOCK_CONFIG_API.begin_change(p_actor,'warehouse_settings_edit');permit('CONFIG');assert_config_actor(p_actor,ware);
  p_result:=policy_receipt(p_request,p_actor,'SKU',to_char(ware)||':'||article);if p_result is not null then clear_context;RRL_STOCK_CONFIG_API.end_change;return;end if;
  base_value:=j.get_string('base_uom');assert_count_sku(article,base_value);
  select nvl(max(VERSION_NO),0)into version_no from RRL_ASSEMBLY_SKU_POLICY where WARE_ID=ware and ARTICUL=article;
  if j.get_number('expected_version')is null or j.get_number('expected_version')!=version_no then raise_application_error(-20886,'ASSEMBLY_POLICY_VERSION_CONFLICT');end if;
  lower_no:=RRL_STOCK_MATH.quantity(j.get_string('min_unit_kg'));upper_no:=RRL_STOCK_MATH.quantity(j.get_string('max_unit_kg'));
  minimum_no:=RRL_STOCK_MATH.quantity(j.get_string('min_delta_kg'));if regexp_like(j.get_string('tolerance_kg'),'^0{1,18}([.]0{1,9})?$','c')then tolerance_no:=0;else tolerance_no:=RRL_STOCK_MATH.quantity(j.get_string('tolerance_kg'));end if;
  reference_value:=j.get_string('evidence_reference');op:=j.get_string('operation_id');
  if ware is null or lower_no<=0 or upper_no<lower_no or minimum_no<=0 or tolerance_no<0 or reference_value is null or length(reference_value)<8 or op is null or lengthb(op)>100 then
   raise_application_error(-20886,'ASSEMBLY_EXPLICIT_SKU_MASS_POLICY_REQUIRED');end if;
  if j.get_boolean('active')then active_no:=1;else active_no:=0;end if;
  merge into RRL_ASSEMBLY_SKU_POLICY t using(select ware WARE_ID,article ARTICUL from dual)x on(t.WARE_ID=x.WARE_ID and t.ARTICUL=x.ARTICUL)
   when matched then update set VERSION_NO=version_no+1,BASE_UOM=base_value,MIN_UNIT_KG=lower_no,MAX_UNIT_KG=upper_no,MIN_DELTA_KG=minimum_no,TOLERANCE_KG=tolerance_no,ACTIVE_FLAG=active_no,EVIDENCE_REFERENCE=reference_value,CHANGED_BY=p_actor,CHANGED_AT=systimestamp
   when not matched then insert(WARE_ID,ARTICUL,BASE_UOM,VERSION_NO,MIN_UNIT_KG,MAX_UNIT_KG,MIN_DELTA_KG,TOLERANCE_KG,ACTIVE_FLAG,EVIDENCE_REFERENCE,CHANGED_BY)
    values(ware,article,base_value,1,lower_no,upper_no,minimum_no,tolerance_no,active_no,reference_value,p_actor);
  insert into RRL_ASSEMBLY_POLICY_EVENT(OPERATION_ID,POLICY_KIND,POLICY_KEY,VERSION_NO,SOURCE_JSON,ACTOR)
   values(op,'SKU',to_char(ware)||':'||article,version_no+1,p_request,p_actor);
  r.put('version',version_no+1);r.put('policy_kind','SKU');r.put('operation_id',op);p_result:=r.to_clob;clear_context;RRL_STOCK_CONFIG_API.end_change;
 exception when others then clear_context;RRL_STOCK_CONFIG_API.end_change;raise;end;
 procedure open_session(p_request clob,p_actor nvarchar2,p_result out clob)is
  j json_object_t:=json_object_t.parse(p_request);t RRL_CASE_PICK_TASK%rowtype;d RRL_WH_SCALE_DEVICE%rowtype;p RRL_ASSEMBLY_STATION%rowtype;
  tare RRL_WH_SCALE_CAPTURE%rowtype;s RRL_ASSEMBLY_SESSION%rowtype;sid varchar2(100):=j.get_string('session_id');task_no number:=j.get_number('task_id');device_value varchar2(100):=j.get_string('device_id');tare_key varchar2(64):=j.get_string('tare_capture_key');n number;
 begin
  begin_meta(p_actor);assert_task(task_no,p_actor);
  begin select *into s from RRL_ASSEMBLY_SESSION where SESSION_ID=sid;
   if s.OPERATOR_ID!=p_actor or s.CASE_PICK_TASK_ID!=task_no or dbms_lob.compare(s.REQUEST_JSON,p_request)!=0 then raise_application_error(-20886,'ASSEMBLY_SESSION_PAYLOAD_CONFLICT');end if;
   p_result:=session_json(s).to_clob;end_meta;return;
  exception when no_data_found then null;end;
  select *into t from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=task_no for update;
  select *into d from RRL_WH_SCALE_DEVICE where DEVICE_ID=device_value for update;
  select *into p from RRL_ASSEMBLY_STATION where DEVICE_ID=device_value;
  select *into tare from RRL_WH_SCALE_CAPTURE where CAPTURE_KEY=tare_key;
  if sid is null or lengthb(sid)>100 or t.STATUS is null or t.STATUS not in('IN_PROGRESS','PARTIAL','WAIT_REPLENISHMENT')or t.WARE_ID!=d.WARE_ID
   or j.get_number('expected_content_version')is null or t.CONTENT_VERSION is null or t.CONTENT_VERSION!=j.get_number('expected_content_version')
   or j.get_string('scan_container')is null or t.SSCC is null or t.SSCC!=j.get_string('scan_container')or nvl(t.PICKED_QTY,0)!=0
   or d.ACTIVE_FLAG!=1 or d.MEASUREMENT_BASIS!='GROSS'or d.CALIBRATED_UNTIL<systimestamp or p.ACTIVE_FLAG!=1
   or d.SENDER_ID=p_actor then raise_application_error(-20886,'ASSEMBLY_INITIAL_ASSIGNED_GROSS_CONTEXT_REQUIRED');end if;
  if tare.CAPTURE_PURPOSE!='EMPTY_TARE'or tare.CASE_PICK_TASK_ID!=task_no or tare.CARRIER_IDENTIFIER!=t.SSCC
   or tare.DEVICE_ID!=device_value or tare.WARE_ID!=t.WARE_ID or tare.POST_CELL!=d.POST_CELL or tare.DEVICE_MODE!=d.DEVICE_MODE
   or tare.DEVICE_POLICY_VERSION!=d.POLICY_VERSION or tare.CASE_CONTENT_VERSION!=t.CONTENT_VERSION
   or tare.RECORDED_BY is null or tare.RECORDED_BY!=d.SENDER_ID or tare.CALIBRATION_REF is null or tare.CALIBRATION_REF!=d.CALIBRATION_REF
   or tare.MEASUREMENT_BASIS!='GROSS'or tare.PALLET_TYPE_ID!=t.PALLET_TYPE_ID
   or tare.MEASURED_AT<systimestamp-numtodsinterval(120,'SECOND')or tare.MEASURED_AT>systimestamp+numtodsinterval(2,'SECOND')then
   raise_application_error(-20886,'ASSEMBLY_CURRENT_MEASURED_EMPTY_TARE_REQUIRED');end if;
  assert_sender(device_value,d.SENDER_ID);
  s.SESSION_ID:=sid;s.CASE_PICK_TASK_ID:=task_no;s.DEVICE_ID:=device_value;s.WARE_ID:=t.WARE_ID;s.POST_CELL:=d.POST_CELL;
  s.OPERATOR_ID:=p_actor;s.SENDER_ID:=d.SENDER_ID;s.CARRIER_IDENTIFIER:=t.SSCC;s.TARE_CAPTURE_KEY:=tare.CAPTURE_KEY;
  s.DEVICE_POLICY_VERSION:=d.POLICY_VERSION;s.STATION_POLICY_VERSION:=p.VERSION_NO;s.DEVICE_MODE:=d.DEVICE_MODE;s.CALIBRATION_REF:=d.CALIBRATION_REF;
  s.CUMULATIVE_TOLERANCE_KG:=p.CUMULATIVE_TOLERANCE_KG;s.CONFIRMATION_MODE:=p.CONFIRMATION_MODE;s.INITIAL_CONTENT_VERSION:=t.CONTENT_VERSION;s.LAST_CONTENT_VERSION:=t.CONTENT_VERSION;s.LAST_SEQUENCE:=0;
  s.TARE_WEIGHT_KG:=tare.WEIGHT_KG;s.LAST_WEIGHT_KG:=tare.WEIGHT_KG;s.STATE:='OPEN';s.OPENED_AT:=systimestamp;
  s.EXPIRES_AT:=systimestamp+numtodsinterval(p.MAX_SESSION_SECONDS,'SECOND');s.REQUEST_JSON:=p_request;
  insert into RRL_ASSEMBLY_SESSION values s;p_result:=session_json(s).to_clob;end_meta;
 exception when others then end_meta;raise;end;
 procedure open_step(p_session varchar2,p_request clob,p_actor nvarchar2,p_result out clob)is
  j json_object_t:=json_object_t.parse(p_request);s RRL_ASSEMBLY_SESSION%rowtype;t RRL_ASSEMBLY_STEP%rowtype;
  l RRL_CASE_PICK_LINE%rowtype;ct RRL_CASE_PICK_TASK%rowtype;policy RRL_ASSEMBLY_SKU_POLICY%rowtype;device RRL_WH_SCALE_DEVICE%rowtype;
  step_value varchar2(100):=j.get_string('step_id');line_no number:=j.get_number('case_line_id');n number;barcode varchar2(512):=j.get_string('scan_product');
  quantity_no number:=RRL_STOCK_MATH.quantity(j.get_string('quantity'));identity json_array_t:=json_array_t();
 begin
  begin_meta(p_actor);select *into s from RRL_ASSEMBLY_SESSION where SESSION_ID=p_session;
  select *into ct from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=s.CASE_PICK_TASK_ID for update;
  select *into s from RRL_ASSEMBLY_SESSION where SESSION_ID=p_session for update;
  assert_task(s.CASE_PICK_TASK_ID,p_actor);if s.OPERATOR_ID!=p_actor then raise_application_error(-20882,'ASSEMBLY_SESSION_OPERATOR_REQUIRED');end if;
  begin select *into t from RRL_ASSEMBLY_STEP where STEP_ID=step_value;
   if t.SESSION_ID!=p_session or dbms_lob.compare(t.REQUEST_JSON,p_request)!=0 then raise_application_error(-20886,'ASSEMBLY_STEP_PAYLOAD_CONFLICT');end if;
   p_result:=step_json(t).to_clob;end_meta;return;
  exception when no_data_found then null;end;
  assert_open(s);
  select count(*)into n from RRL_ASSEMBLY_STEP where SESSION_ID=p_session and STATE not in('APPLIED','CANCELLED');
  if n!=0 then raise_application_error(-20886,'ASSEMBLY_PREVIOUS_STEP_UNRESOLVED');end if;
  select *into l from RRL_CASE_PICK_LINE where CASE_PICK_LINE_ID=line_no and CASE_PICK_TASK_ID=s.CASE_PICK_TASK_ID;
  select *into policy from RRL_ASSEMBLY_SKU_POLICY where WARE_ID=s.WARE_ID and ARTICUL=l.ARTICUL;
  select *into device from RRL_WH_SCALE_DEVICE where DEVICE_ID=s.DEVICE_ID;assert_count_sku(l.ARTICUL,policy.BASE_UOM);
  if policy.ACTIVE_FLAG!=1 or l.STATUS is null or l.STATUS not in('NEW','ACTIVE','SKIPPED','IN_PROGRESS','PARTIAL','WAIT_REPLENISHMENT')
   or j.get_number('expected_content_version')is null or j.get_number('expected_content_version')!=ct.CONTENT_VERSION
   or j.get_string('scan_source_cell')is null or j.get_string('scan_source_cell')!=l.CELL_CODE
   or j.get_string('scan_container')is null or j.get_string('scan_container')!=ct.SSCC
   or quantity_no is null or quantity_no<=0 or quantity_no!=trunc(quantity_no)or quantity_no+nvl(l.PICKED_QTY,0)>l.PLANNED_QTY then
   raise_application_error(-20886,'ASSEMBLY_CURRENT_LINE_SCAN_QUANTITY_REQUIRED');end if;
  select count(*)into n from RRL_ARTICULS where ACTICUL=l.ARTICUL and barcode in(ACTICUL,BARCODE_SHT,BARCODE_KOR,BARCODE_BL);
  if n!=1 then raise_application_error(-20886,'ASSEMBLY_PRODUCT_SCAN_REQUIRED');end if;
  t.CONSENT_TO_AUTO:=0;if j.get_boolean('consent_to_auto')then t.CONSENT_TO_AUTO:=1;end if;
  if s.CONFIRMATION_MODE='AUTO'and t.CONSENT_TO_AUTO!=1 then raise_application_error(-20886,'ASSEMBLY_EXPLICIT_AUTO_CONSENT_REQUIRED');end if;
  t.MIN_DELTA_KG:=greatest(policy.MIN_DELTA_KG,device.RESOLUTION_KG*2);
  t.LOWER_DELTA_KG:=quantity_no*policy.MIN_UNIT_KG-policy.TOLERANCE_KG;t.UPPER_DELTA_KG:=quantity_no*policy.MAX_UNIT_KG+policy.TOLERANCE_KG;
  if t.LOWER_DELTA_KG<t.MIN_DELTA_KG or t.UPPER_DELTA_KG<t.LOWER_DELTA_KG then raise_application_error(-20886,'ASSEMBLY_DELTA_NOT_RELIABLY_DISTINGUISHABLE');end if;
  t.STEP_ID:=step_value;t.SESSION_ID:=p_session;t.OPERATION_ID:=j.get_string('operation_id');t.SEQUENCE_NO:=s.LAST_SEQUENCE+1;
  t.CASE_PICK_LINE_ID:=line_no;t.ARTICUL:=l.ARTICUL;t.SOURCE_VERSION:=ct.CONTENT_VERSION;t.PREVIOUS_QTY:=nvl(l.PICKED_QTY,0);t.QUANTITY:=quantity_no;t.FACT_QTY:=t.PREVIOUS_QTY+quantity_no;
  t.SCAN_SOURCE_CELL:=l.CELL_CODE;t.SCAN_PRODUCT:=barcode;t.SCAN_CONTAINER:=ct.SSCC;t.SKU_POLICY_VERSION:=policy.VERSION_NO;t.STATE:='WAITING_BEFORE';
  identity.append(p_session);identity.append(step_value);identity.append('BEFORE');t.BEFORE_CAPTURE_ID:='ASM.'||rawtohex(sys.dbms_crypto.hash(identity.to_clob,sys.dbms_crypto.hash_sh256));
  identity:=json_array_t();identity.append(p_session);identity.append(step_value);identity.append('AFTER');t.AFTER_CAPTURE_ID:='ASM.'||rawtohex(sys.dbms_crypto.hash(identity.to_clob,sys.dbms_crypto.hash_sh256));
  t.OPENED_AT:=systimestamp;t.REQUEST_JSON:=p_request;
  insert into RRL_ASSEMBLY_STEP values t;update RRL_ASSEMBLY_SESSION set LAST_SEQUENCE=t.SEQUENCE_NO where SESSION_ID=p_session;
  p_result:=step_json(t).to_clob;end_meta;
 exception when no_data_found then end_meta;raise_application_error(-20886,'ASSEMBLY_EXPLICIT_LINE_MASS_POLICY_REQUIRED');
 when others then end_meta;raise;end;
 procedure capture(p_request clob,p_sender nvarchar2,p_result out clob)is
  j json_object_t:=json_object_t.parse(p_request);s RRL_ASSEMBLY_SESSION%rowtype;t RRL_ASSEMBLY_STEP%rowtype;c RRL_ASSEMBLY_CAPTURE%rowtype;old RRL_ASSEMBLY_CAPTURE%rowtype;
  device RRL_WH_SCALE_DEVICE%rowtype;reading json_object_t;r json_object_t:=json_object_t();identity json_array_t:=json_array_t();
  sid varchar2(100):=j.get_string('session_id');step_value varchar2(100):=j.get_string('step_id');device_value varchar2(100):=j.get_string('device_id');capture_value varchar2(100):=j.get_string('capture_id');
  hash_value varchar2(64):=rawtohex(sys.dbms_crypto.hash(p_request,sys.dbms_crypto.hash_sh256));before_at timestamp with time zone;span_no number;state_value varchar2(30);reason_value varchar2(200);ct RRL_CASE_PICK_TASK%rowtype;
 begin
  if sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')is not null then raise_application_error(-20886,'ASSEMBLY_ARCHIVE_OUTSIDE_STOCK_REQUIRED');end if;
  if p_request is null or dbms_lob.getlength(p_request)>32000 then raise_application_error(-20881,'ASSEMBLY_PACKET_BOUND_32000');end if;
  assert_sender(device_value,p_sender);
  -- Dedicated sender never acquires an operator permission by presenting its name.
  select *into s from RRL_ASSEMBLY_SESSION where SESSION_ID=sid;
  if s.DEVICE_ID!=device_value or s.SENDER_ID!=p_sender or s.OPERATOR_ID=p_sender then raise_application_error(-20882,'ASSEMBLY_SESSION_SENDER_REQUIRED');end if;
  begin select *into old from RRL_ASSEMBLY_CAPTURE where DEVICE_ID=device_value and CAPTURE_ID=capture_value;
   if old.RECORDED_BY!=p_sender or old.SESSION_ID!=sid or old.STEP_ID!=step_value or old.SOURCE_SHA256!=hash_value or dbms_lob.compare(old.SOURCE_JSON,p_request)!=0 then
    raise_application_error(-20886,'ASSEMBLY_CAPTURE_PAYLOAD_CONFLICT');end if;
   lock table RRL_ACCESS_REV in share mode wait 2;
   select *into device from RRL_WH_SCALE_DEVICE where DEVICE_ID=device_value for update wait 2;assert_sender(device_value,p_sender);
   if device.WARE_ID!=old.WARE_ID or device.POST_CELL!=old.POST_CELL then raise_application_error(-20882,'ASSEMBLY_ORIGINAL_CAPTURE_SCOPE_CHANGED');end if;
   p_result:=old.RESULT_JSON;return;
  exception when no_data_found then null;end;
  RRL_STOCK_METADATA_TX.begin_change(s.OPERATOR_ID,'case_pick_execute');lock table RRL_ACCESS_REV in share mode wait 2;permit('META');
  select *into ct from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=s.CASE_PICK_TASK_ID for update;
  select *into s from RRL_ASSEMBLY_SESSION where SESSION_ID=sid for update;
  select *into t from RRL_ASSEMBLY_STEP where STEP_ID=step_value and SESSION_ID=sid for update;assert_open(s);assert_sender(device_value,p_sender);
  select *into device from RRL_WH_SCALE_DEVICE where DEVICE_ID=device_value;
  if j.get_number('device_policy_version')is null or j.get_number('device_policy_version')!=s.DEVICE_POLICY_VERSION
   or j.get_string('calibration_ref')is null or j.get_string('calibration_ref')!=s.CALIBRATION_REF or t.SOURCE_VERSION!=ct.CONTENT_VERSION then
   raise_application_error(-20886,'ASSEMBLY_CAPTURE_SOURCE_CHANGED');end if;
  c.PHASE:=j.get_string('phase');
  if(c.PHASE='BEFORE'and(t.STATE!='WAITING_BEFORE'or capture_value!=t.BEFORE_CAPTURE_ID))
   or(c.PHASE='AFTER'and(t.STATE!='ARMED'or capture_value!=t.AFTER_CAPTURE_ID))or c.PHASE is null or c.PHASE not in('BEFORE','AFTER')then
   raise_application_error(-20886,'ASSEMBLY_CAPTURE_PHASE_REQUIRED');end if;
  if c.PHASE='AFTER'and s.CONFIRMATION_MODE='BUTTON'and t.BUTTON_INTENT_AT is null then raise_application_error(-20886,'ASSEMBLY_BUTTON_INTENT_REQUIRED');end if;
  reading:=json_object_t.parse(RRL_SCALE_PACKET_READ.validate_series_json(p_request,device.CAPACITY_KG,device.RESOLUTION_KG));
  c.WEIGHT_KG:=RRL_STOCK_MATH.quantity(reading.get_string('weight_kg'));c.MEASURED_AT:=RRL_SCALE_PACKET_READ.utc_stamp(j.get_string('measured_at'));span_no:=reading.get_number('span_ms');
  if c.MEASURED_AT-numtodsinterval(span_no/1000,'SECOND')<t.OPENED_AT then raise_application_error(-20886,'ASSEMBLY_PREARM_WINDOW_AFTER_OPEN_REQUIRED');end if;
  if c.PHASE='BEFORE'then
   if abs(c.WEIGHT_KG-s.LAST_WEIGHT_KG)>device.RESOLUTION_KG then state_value:='DISCREPANCY';reason_value:='ASSEMBLY_UNEXPECTED_MASS_OUTSIDE_STEP';
   else state_value:='ARMED';end if;
   update RRL_ASSEMBLY_STEP set BEFORE_WEIGHT_KG=c.WEIGHT_KG,STATE=state_value,BLOCK_REASON=reason_value where STEP_ID=step_value;
  else
   select MEASURED_AT into before_at from RRL_ASSEMBLY_CAPTURE where STEP_ID=step_value and PHASE='BEFORE';
   if c.MEASURED_AT-numtodsinterval(span_no/1000,'SECOND')<before_at then raise_application_error(-20886,'ASSEMBLY_AFTER_WINDOW_FOLLOWS_PREARM_REQUIRED');end if;
   t.DELTA_KG:=c.WEIGHT_KG-t.BEFORE_WEIGHT_KG;
   if t.DELTA_KG<t.MIN_DELTA_KG or t.DELTA_KG<t.LOWER_DELTA_KG or t.DELTA_KG>t.UPPER_DELTA_KG then
    state_value:='DISCREPANCY';reason_value:='ASSEMBLY_MEASURED_DELTA_OUTSIDE_POLICY';else state_value:='READY';end if;
   update RRL_ASSEMBLY_STEP set AFTER_WEIGHT_KG=c.WEIGHT_KG,DELTA_KG=t.DELTA_KG,STATE=state_value,BLOCK_REASON=reason_value where STEP_ID=step_value;
  end if;
  if state_value='DISCREPANCY'then update RRL_ASSEMBLY_SESSION set STATE='BLOCKED',BLOCK_REASON=reason_value where SESSION_ID=sid;end if;
  c.DEVICE_ID:=device_value;c.CAPTURE_ID:=capture_value;c.SESSION_ID:=sid;c.STEP_ID:=step_value;c.WARE_ID:=s.WARE_ID;c.POST_CELL:=s.POST_CELL;c.DEVICE_POLICY_VERSION:=s.DEVICE_POLICY_VERSION;
  c.SOURCE_SHA256:=hash_value;c.SOURCE_JSON:=p_request;c.RECORDED_BY:=p_sender;c.RECORDED_AT:=systimestamp;
  identity.append(device_value);identity.append(capture_value);r.put('capture_key',rawtohex(sys.dbms_crypto.hash(identity.to_clob,sys.dbms_crypto.hash_sh256)));
  r.put('status','ARCHIVED');r.put('device_id',device_value);r.put('capture_id',capture_value);r.put('session_id',sid);r.put('step_id',step_value);r.put('phase',c.PHASE);
  r.put('source_sha256',hash_value);r.put('weight_kg',reading.get_string('weight_kg'));r.put('measured_at',j.get_string('measured_at'));
  r.put('device_policy_version',s.DEVICE_POLICY_VERSION);r.put('calibration_ref',s.CALIBRATION_REF);r.put('stock_posted',false);
  c.RESULT_JSON:=r.to_clob;insert into RRL_ASSEMBLY_CAPTURE values c;p_result:=c.RESULT_JSON;end_meta;
 exception when others then end_meta;raise;end;
 procedure placed(p_step varchar2,p_actor nvarchar2,p_result out clob)is t RRL_ASSEMBLY_STEP%rowtype;s RRL_ASSEMBLY_SESSION%rowtype;ct RRL_CASE_PICK_TASK%rowtype;begin
  begin_meta(p_actor);select *into t from RRL_ASSEMBLY_STEP where STEP_ID=p_step;
  select *into s from RRL_ASSEMBLY_SESSION where SESSION_ID=t.SESSION_ID;
  assert_task(s.CASE_PICK_TASK_ID,p_actor);
  if s.OPERATOR_ID!=p_actor or s.CONFIRMATION_MODE!='BUTTON'then raise_application_error(-20882,'ASSEMBLY_BUTTON_OPERATOR_REQUIRED');end if;
  if t.STATE='APPLIED'then p_result:=step_json(t).to_clob;end_meta;return;end if;
  select *into ct from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=s.CASE_PICK_TASK_ID for update;
  select *into s from RRL_ASSEMBLY_SESSION where SESSION_ID=t.SESSION_ID for update;assert_open(s);
  select *into t from RRL_ASSEMBLY_STEP where STEP_ID=p_step for update;
  if t.STATE not in('ARMED','READY')then raise_application_error(-20886,'ASSEMBLY_PREARM_REQUIRED_BEFORE_BUTTON');end if;
  if t.BUTTON_INTENT_AT is null then update RRL_ASSEMBLY_STEP set BUTTON_INTENT_AT=systimestamp where STEP_ID=p_step;t.BUTTON_INTENT_AT:=systimestamp;end if;
  p_result:=step_json(t).to_clob;end_meta;
 exception when others then end_meta;raise;end;
 function stock_metadata(t RRL_ASSEMBLY_STEP%rowtype,s RRL_ASSEMBLY_SESSION%rowtype)return json_object_t is m json_object_t:=json_object_t();begin
  m.put('fact_qty',RRL_STOCK_PLAN_HELPER.decimal_text(t.FACT_QTY));m.put('scan_cell',t.SCAN_SOURCE_CELL);m.put('scan_product',t.SCAN_PRODUCT);m.put('scan_container',t.SCAN_CONTAINER);
  m.put_null('offline_event_id');m.put('assembly_step_id',t.STEP_ID);m.put('assembly_consent_id',t.STEP_ID);
  m.put('automation_origin',case when s.CONFIRMATION_MODE='AUTO'then'ASSEMBLY_GATEWAY_AUTO'else'ASSEMBLY_BUTTON'end);m.put('automation_sender',s.SENDER_ID);return m;
 end;
 procedure posting_request(p_step varchar2,p_caller nvarchar2,p_result out clob)is t RRL_ASSEMBLY_STEP%rowtype;s RRL_ASSEMBLY_SESSION%rowtype;j json_object_t:=json_object_t();src json_object_t:=json_object_t();wire clob;d json_object_t;begin
  select *into t from RRL_ASSEMBLY_STEP where STEP_ID=p_step;select *into s from RRL_ASSEMBLY_SESSION where SESSION_ID=t.SESSION_ID;
  if p_caller is null then raise_application_error(-20882,'ASSEMBLY_SESSION_CALLER_REQUIRED');end if;
  if p_caller!=s.OPERATOR_ID then assert_sender(s.DEVICE_ID,p_caller);if p_caller!=s.SENDER_ID then raise_application_error(-20882,'ASSEMBLY_SESSION_SENDER_REQUIRED');end if;end if;
  assert_task(s.CASE_PICK_TASK_ID,s.OPERATOR_ID);j.put('step',step_json(t));j.put('eligible',false);j.put('operation_id',t.OPERATION_ID);
  if t.STATE='APPLIED'then
   select CANONICAL_REQUEST into wire from RRL_STOCK_OPERATION where OPERATION_ID=t.OPERATION_ID and STATE='APPLIED';d:=json_object_t.parse(wire);
   if d.get_string('actor')!=s.OPERATOR_ID or d.get_object('metadata').get_string('assembly_step_id')!=t.STEP_ID then raise_application_error(-20886,'ASSEMBLY_ORIGINAL_POST_CONFLICT');end if;
   j.put('command',d);j.put('eligible',true);p_result:=j.to_clob;return;
  end if;
  if t.STATE!='READY'then p_result:=j.to_clob;return;end if;assert_open(s);
  if(s.CONFIRMATION_MODE='AUTO'and t.CONSENT_TO_AUTO!=1)or(s.CONFIRMATION_MODE='BUTTON'and t.BUTTON_INTENT_AT is null)then p_result:=j.to_clob;return;end if;
  src.put('case_task_id',s.CASE_PICK_TASK_ID);src.put('case_line_id',t.CASE_PICK_LINE_ID);
  d:=json_object_t();d.put('operation_id',t.OPERATION_ID);d.put('actor',s.OPERATOR_ID);d.put('source',src);d.put('metadata',stock_metadata(t,s));j.put('command',d);j.put('eligible',true);p_result:=j.to_clob;
 end;
 procedure assert_post(p_request clob,p_previous number)is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');t RRL_ASSEMBLY_STEP%rowtype;s RRL_ASSEMBLY_SESSION%rowtype;
  l RRL_CASE_PICK_LINE%rowtype;policy RRL_ASSEMBLY_SKU_POLICY%rowtype;n number;step_value varchar2(100):=m.get_string('assembly_step_id');expected_metadata clob;actual_metadata clob;
 begin
  if step_value is null then raise_application_error(-20886,'ASSEMBLY_STEP_ID_REQUIRED');end if;
  select *into t from RRL_ASSEMBLY_STEP where STEP_ID=step_value;select *into s from RRL_ASSEMBLY_SESSION where SESSION_ID=t.SESSION_ID;assert_open(s);
  select *into l from RRL_CASE_PICK_LINE where CASE_PICK_LINE_ID=t.CASE_PICK_LINE_ID and CASE_PICK_TASK_ID=s.CASE_PICK_TASK_ID;
  select *into policy from RRL_ASSEMBLY_SKU_POLICY where WARE_ID=s.WARE_ID and ARTICUL=t.ARTICUL;assert_count_sku(t.ARTICUL,policy.BASE_UOM);
  if t.STATE!='READY'or d.get_string('operation_id')is null or t.OPERATION_ID!=d.get_string('operation_id')or d.get_string('actor')is null or s.OPERATOR_ID!=d.get_string('actor')
   or d.get_object('source').get_number('case_task_id')is null or d.get_object('source').get_number('case_task_id')!=s.CASE_PICK_TASK_ID
   or d.get_object('source').get_number('case_line_id')is null or d.get_object('source').get_number('case_line_id')!=t.CASE_PICK_LINE_ID
   or t.SOURCE_VERSION!=s.LAST_CONTENT_VERSION or l.ARTICUL!=t.ARTICUL or l.CELL_CODE!=t.SCAN_SOURCE_CELL
   or nvl(l.PICKED_QTY,0)!=t.PREVIOUS_QTY or p_previous is null or p_previous!=t.PREVIOUS_QTY or t.FACT_QTY>l.PLANNED_QTY
   or policy.ACTIVE_FLAG!=1 or policy.VERSION_NO!=t.SKU_POLICY_VERSION
   or m.get_string('fact_qty')is null or RRL_STOCK_MATH.quantity(m.get_string('fact_qty'))!=t.FACT_QTY
   or m.get_string('scan_cell')is null or m.get_string('scan_cell')!=t.SCAN_SOURCE_CELL
   or m.get_string('scan_container')is null or m.get_string('scan_container')!=t.SCAN_CONTAINER
   or m.get_string('scan_product')is null or m.get_string('scan_product')!=t.SCAN_PRODUCT
   or m.get_string('assembly_consent_id')is null or m.get_string('assembly_consent_id')!=t.STEP_ID
   or m.get_string('automation_origin')is null or m.get_string('automation_sender')is null or m.get_string('automation_sender')!=s.SENDER_ID
   or d.get_array('units').get_size!=0 then raise_application_error(-20886,'ASSEMBLY_POST_SOURCE_POLICY_CONFLICT');end if;
  if(s.CONFIRMATION_MODE='AUTO'and(t.CONSENT_TO_AUTO!=1 or m.get_string('automation_origin')!='ASSEMBLY_GATEWAY_AUTO'))
   or(s.CONFIRMATION_MODE='BUTTON'and(t.BUTTON_INTENT_AT is null or m.get_string('automation_origin')!='ASSEMBLY_BUTTON'))then
   raise_application_error(-20886,'ASSEMBLY_CURRENT_OPERATOR_CONSENT_REQUIRED');end if;
  select count(*)into n from RRL_ASSEMBLY_STEP_USE where STEP_ID=t.STEP_ID;
  if n!=0 then raise_application_error(-20886,'ASSEMBLY_STEP_ALREADY_POSTED');end if;
  select count(*)into n from RRL_ASSEMBLY_CAPTURE where STEP_ID=t.STEP_ID and PHASE in('BEFORE','AFTER');
  if n!=2 or t.DELTA_KG is null or t.DELTA_KG<t.MIN_DELTA_KG or t.DELTA_KG<t.LOWER_DELTA_KG or t.DELTA_KG>t.UPPER_DELTA_KG then raise_application_error(-20886,'ASSEMBLY_ADMITTED_DELTA_REQUIRED');end if;
 end;
 procedure claim_post(p_request clob,p_operation varchar2,p_previous number)is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');t RRL_ASSEMBLY_STEP%rowtype;s RRL_ASSEMBLY_SESSION%rowtype;step_value varchar2(100):=m.get_string('assembly_step_id');
 begin
  RRL_STOCK_LOCK_API.assert_held(70,RRL_STOCK_LOCK_API.resource_key('UNIQUE','ASSEMBLY.STEP:'||step_value));
  -- Canonical prepare takes the current rights revision fence immediately after begin_plan, before CASE.
  assert_post(p_request,p_previous);
  select *into t from RRL_ASSEMBLY_STEP where STEP_ID=step_value;
  select *into s from RRL_ASSEMBLY_SESSION where SESSION_ID=t.SESSION_ID for update;
  select *into t from RRL_ASSEMBLY_STEP where STEP_ID=step_value for update;
  if p_operation!=t.OPERATION_ID or sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')!=p_operation then raise_application_error(-20882,'ASSEMBLY_CANONICAL_STOCK_TRANSACTION_REQUIRED');end if;
  permit('USE');insert into RRL_ASSEMBLY_STEP_USE(STEP_ID,STOCK_OPERATION_ID,OPERATOR_ID)values(t.STEP_ID,p_operation,s.OPERATOR_ID);
  update RRL_ASSEMBLY_STEP set STATE='APPLIED'where STEP_ID=t.STEP_ID;
  update RRL_ASSEMBLY_SESSION set LAST_WEIGHT_KG=t.AFTER_WEIGHT_KG,LAST_CONTENT_VERSION=t.SOURCE_VERSION+1 where SESSION_ID=s.SESSION_ID;
  clear_context;
 exception when others then clear_context;raise;end;
 procedure finish(p_session varchar2,p_request clob,p_actor nvarchar2,p_result out clob)is
  j json_object_t:=json_object_t.parse(p_request);s RRL_ASSEMBLY_SESSION%rowtype;c RRL_WH_SCALE_CAPTURE%rowtype;n number;key_value varchar2(64):=j.get_string('final_capture_key');d RRL_WH_SCALE_DEVICE%rowtype;ct RRL_CASE_PICK_TASK%rowtype;last_after timestamp with time zone;accepted_delta number;begin
  if key_value is null or not regexp_like(key_value,'^[0-9A-Fa-f]{64}$','c')then raise_application_error(-20886,'ASSEMBLY_FINAL_CAPTURE_KEY_REQUIRED');end if;
  begin_meta(p_actor);select *into s from RRL_ASSEMBLY_SESSION where SESSION_ID=p_session;
  select *into ct from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=s.CASE_PICK_TASK_ID for update;
  select *into s from RRL_ASSEMBLY_SESSION where SESSION_ID=p_session for update;assert_task(s.CASE_PICK_TASK_ID,p_actor);
  if s.OPERATOR_ID!=p_actor then raise_application_error(-20882,'ASSEMBLY_SESSION_OPERATOR_REQUIRED');end if;
  if s.STATE='FINALIZED'then
   if s.FINAL_CAPTURE_KEY is null or s.FINAL_CAPTURE_KEY!=key_value then raise_application_error(-20886,'ASSEMBLY_FINAL_CAPTURE_CONFLICT');end if;p_result:=session_json(s).to_clob;end_meta;return;end if;
  assert_open(s);select count(*)into n from RRL_ASSEMBLY_STEP where SESSION_ID=p_session and STATE not in('APPLIED','CANCELLED');
  if n!=0 or s.LAST_SEQUENCE=0 then raise_application_error(-20886,'ASSEMBLY_UNRESOLVED_STEPS_BEFORE_FINAL');end if;
  select *into c from RRL_WH_SCALE_CAPTURE where CAPTURE_KEY=key_value;select *into d from RRL_WH_SCALE_DEVICE where DEVICE_ID=s.DEVICE_ID;
  select max(MEASURED_AT)into last_after from RRL_ASSEMBLY_CAPTURE where SESSION_ID=p_session and PHASE='AFTER';
  select sum(DELTA_KG)into accepted_delta from RRL_ASSEMBLY_STEP where SESSION_ID=p_session and STATE='APPLIED';
  if c.CAPTURE_PURPOSE!='FINAL_GROSS'or c.CASE_PICK_TASK_ID!=s.CASE_PICK_TASK_ID or c.CASE_CONTENT_VERSION!=s.LAST_CONTENT_VERSION
   or c.DEVICE_ID!=s.DEVICE_ID or c.TARE_CAPTURE_KEY!=s.TARE_CAPTURE_KEY or c.CARRIER_IDENTIFIER!=s.CARRIER_IDENTIFIER
   or c.DEVICE_POLICY_VERSION!=s.DEVICE_POLICY_VERSION or c.DEVICE_MODE!=s.DEVICE_MODE
   or c.WARE_ID!=s.WARE_ID or c.POST_CELL!=s.POST_CELL or c.RECORDED_BY is null or c.RECORDED_BY!=s.SENDER_ID
   or c.CALIBRATION_REF is null or c.CALIBRATION_REF!=s.CALIBRATION_REF or c.MEASUREMENT_BASIS!='GROSS'
   or last_after is null or c.MEASURED_AT<=last_after or c.MEASURED_AT>systimestamp+numtodsinterval(2,'SECOND')
   or c.MEASURED_AT<systimestamp-numtodsinterval(120,'SECOND')or c.COMPOSITION_SIGNATURE is null or abs(c.WEIGHT_KG-s.LAST_WEIGHT_KG)>d.RESOLUTION_KG then
   raise_application_error(-20886,'ASSEMBLY_NEW_CURRENT_FINAL_GROSS_REQUIRED');end if;
  if accepted_delta is null or abs(c.WEIGHT_KG-s.TARE_WEIGHT_KG-accepted_delta)>s.CUMULATIVE_TOLERANCE_KG then raise_application_error(-20886,'ASSEMBLY_CUMULATIVE_RECONCILIATION_REQUIRED');end if;
  update RRL_ASSEMBLY_SESSION set STATE='FINALIZED',FINAL_CAPTURE_KEY=key_value where SESSION_ID=p_session;s.STATE:='FINALIZED';s.FINAL_CAPTURE_KEY:=key_value;
  p_result:=session_json(s).to_clob;end_meta;
 exception when others then end_meta;raise;end;
 procedure context(p_task number,p_actor nvarchar2,p_result out clob)is
  t RRL_CASE_PICK_TASK%rowtype;j json_object_t:=json_object_t();lines json_array_t:=json_array_t();stations json_array_t:=json_array_t();o json_object_t;tares json_array_t;active_value json_object_t;n number:=0;
 begin
  assert_task(p_task,p_actor);select *into t from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=p_task;
  j.put('task_id',p_task);j.put('task_state',t.STATUS);j.put('content_version',t.CONTENT_VERSION);j.put('scan_container',t.SSCC);j.put('warehouse_id',t.WARE_ID);
  for l in(select c.CASE_PICK_LINE_ID,c.ARTICUL,a.NAME,c.PLANNED_QTY,nvl(c.PICKED_QTY,0) PICKED_QTY,p.BASE_UOM,p.ACTIVE_FLAG
   from RRL_CASE_PICK_LINE c left join RRL_ARTICULS a on a.ACTICUL=c.ARTICUL
   left join RRL_ASSEMBLY_SKU_POLICY p on p.WARE_ID=t.WARE_ID and p.ARTICUL=c.ARTICUL
   where c.CASE_PICK_TASK_ID=p_task order by c.CASE_PICK_LINE_ID fetch first 201 rows only)loop
   n:=n+1;if n>200 then raise_application_error(-20886,'ASSEMBLY_CONTEXT_LINE_BOUND_200');end if;
   o:=json_object_t();o.put('case_line_id',l.CASE_PICK_LINE_ID);o.put('article',l.ARTICUL);o.put('name',l.NAME);
   o.put('remaining_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(greatest(0,l.PLANNED_QTY-l.PICKED_QTY)));o.put('base_uom',nvl(l.BASE_UOM,'UNKNOWN'));
   o.put('policy_state',case when l.ACTIVE_FLAG=1 then 'CONFIGURED'else'UNCONFIGURED'end);lines.append(o);
  end loop;j.put('lines',lines);n:=0;
  for d in(select v.*,p.CONFIRMATION_MODE from RRL_WH_SCALE_DEVICE v join RRL_ASSEMBLY_STATION p on p.DEVICE_ID=v.DEVICE_ID
   where v.WARE_ID=t.WARE_ID and v.ACTIVE_FLAG=1 and v.MEASUREMENT_BASIS='GROSS'and v.CALIBRATED_UNTIL>=systimestamp and p.ACTIVE_FLAG=1
   order by v.POST_CELL,v.DEVICE_ID fetch first 51 rows only)loop
   n:=n+1;if n>50 then raise_application_error(-20886,'ASSEMBLY_CONTEXT_STATION_BOUND_50');end if;
   o:=json_object_t();o.put('device_id',d.DEVICE_ID);o.put('post_cell',d.POST_CELL);o.put('confirmation_mode',d.CONFIRMATION_MODE);o.put('device_mode',d.DEVICE_MODE);
   o.put('device_policy_version',d.POLICY_VERSION);o.put('calibration_ref',d.CALIBRATION_REF);tares:=json_array_t();
   for c in(select CAPTURE_KEY,WEIGHT_KG,MEASURED_AT from RRL_WH_SCALE_CAPTURE where DEVICE_ID=d.DEVICE_ID and CASE_PICK_TASK_ID=p_task
    and CAPTURE_PURPOSE='EMPTY_TARE'and CASE_CONTENT_VERSION=t.CONTENT_VERSION and CARRIER_IDENTIFIER=t.SSCC and DEVICE_POLICY_VERSION=d.POLICY_VERSION
    and MEASURED_AT>=systimestamp-numtodsinterval(120,'SECOND')order by RECEIVED_AT desc fetch first 10 rows only)loop
    declare v json_object_t:=json_object_t();begin v.put('capture_key',c.CAPTURE_KEY);v.put('weight_kg',RRL_STOCK_PLAN_HELPER.decimal_text(c.WEIGHT_KG));
     v.put('measured_at',to_char(c.MEASURED_AT,'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM'));tares.append(v);end;
   end loop;o.put('tare_captures',tares);stations.append(o);
  end loop;j.put('stations',stations);j.put_null('active_session');
  for s in(select *from RRL_ASSEMBLY_SESSION where CASE_PICK_TASK_ID=p_task and OPERATOR_ID=p_actor and STATE in('OPEN','BLOCKED')order by OPENED_AT desc fetch first 1 row only)loop
   j.put('active_session',session_json(s));end loop;p_result:=j.to_clob;
 end;
 procedure assert_recovery_context(p_session varchar2,p_step varchar2,p_actor nvarchar2,p_permission varchar2)is
  s RRL_ASSEMBLY_SESSION%rowtype;t RRL_ASSEMBLY_STEP%rowtype;ct RRL_CASE_PICK_TASK%rowtype;n number;begin
  select *into s from RRL_ASSEMBLY_SESSION where SESSION_ID=p_session;select *into t from RRL_ASSEMBLY_STEP where STEP_ID=p_step and SESSION_ID=p_session;
  assert_task(s.CASE_PICK_TASK_ID,s.OPERATOR_ID);assert_device(s);
  select count(*)into n from RRL_ASSEMBLY_SKU_POLICY where WARE_ID=s.WARE_ID and ARTICUL=t.ARTICUL and VERSION_NO=t.SKU_POLICY_VERSION and ACTIVE_FLAG=1;
  if n!=1 then raise_application_error(-20886,'ASSEMBLY_RECOVERY_SKU_POLICY_CHANGED');end if;assert_count_sku(t.ARTICUL,'EA');
  if p_permission='warehouse_scale_ingest'then assert_sender(s.DEVICE_ID,p_actor);
   if p_actor!=s.SENDER_ID then raise_application_error(-20882,'ASSEMBLY_SESSION_SENDER_REQUIRED');end if;
  elsif p_permission in('case_pick_execute','case_pick_manage')then
   RRL_CASE_TASK_ACCESS.assert_scope(s.CASE_PICK_TASK_ID,p_actor,p_permission);
   if p_permission='case_pick_execute'and p_actor!=s.OPERATOR_ID then raise_application_error(-20882,'ASSEMBLY_SESSION_OPERATOR_REQUIRED');end if;
  else raise_application_error(-20882,'ASSEMBLY_RECOVERY_PERMISSION_REQUIRED');end if;
  select *into ct from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=s.CASE_PICK_TASK_ID;
  if s.STATE not in('OPEN','BLOCKED')or s.EXPIRES_AT<systimestamp or ct.STATUS is null or ct.STATUS not in('IN_PROGRESS','PARTIAL','WAIT_REPLENISHMENT')or ct.SSCC is null or ct.SSCC!=s.CARRIER_IDENTIFIER
   or ct.CONTENT_VERSION is null or ct.CONTENT_VERSION!=s.LAST_CONTENT_VERSION or t.SOURCE_VERSION!=s.LAST_CONTENT_VERSION or t.SEQUENCE_NO!=s.LAST_SEQUENCE then
   raise_application_error(-20886,'ASSEMBLY_RECOVERY_CURRENT_SESSION_REQUIRED');end if;
 end;
 procedure read_gateway_state(p_session varchar2,p_step varchar2,p_sender nvarchar2,p_result out clob)is
  s RRL_ASSEMBLY_SESSION%rowtype;t RRL_ASSEMBLY_STEP%rowtype;d RRL_WH_SCALE_DEVICE%rowtype;j json_object_t:=json_object_t();begin
  select *into s from RRL_ASSEMBLY_SESSION where SESSION_ID=p_session;select *into t from RRL_ASSEMBLY_STEP where STEP_ID=p_step and SESSION_ID=p_session;
  assert_sender(s.DEVICE_ID,p_sender);select *into d from RRL_WH_SCALE_DEVICE where DEVICE_ID=s.DEVICE_ID;
  if p_sender!=s.SENDER_ID or d.WARE_ID!=s.WARE_ID or d.POST_CELL!=s.POST_CELL then raise_application_error(-20882,'ASSEMBLY_SESSION_SENDER_REQUIRED');end if;
  j.put('step',step_json(t));j.put('session',session_json(s));p_result:=j.to_clob;
 end;
 procedure apply_reconciliation(p_id varchar2,p_session varchar2,p_step varchar2)is state_value varchar2(20);begin
  RRL_ASSEMBLY_RECOVERY_API.assert_apply(p_id,p_session,p_step);select STATE into state_value from RRL_ASM_RECONCILIATION where RECONCILIATION_ID=p_id;permit('META');
  if state_value='REQUESTED'then
   update RRL_ASSEMBLY_SESSION set STATE='BLOCKED',BLOCK_REASON='RECOVERY_REQUESTED'where SESSION_ID=p_session;clear_context;return;end if;
  update RRL_ASSEMBLY_STEP set STATE='CANCELLED',BLOCK_REASON='RECONCILED_UNPOSTED_STEP'where STEP_ID=p_step and SESSION_ID=p_session and STATE!='APPLIED';
  if sql%rowcount!=1 then raise_application_error(-20886,'ASSEMBLY_RECOVERY_UNPOSTED_STEP_REQUIRED');end if;
  update RRL_ASSEMBLY_SESSION set STATE='OPEN',BLOCK_REASON=null where SESSION_ID=p_session;clear_context;
 exception when others then clear_context;raise;end;
 procedure gateway_requests(p_device varchar2,p_sender nvarchar2,p_result out clob)is
  j json_object_t:=json_object_t();items json_array_t:=json_array_t();o json_object_t;s RRL_ASSEMBLY_SESSION%rowtype;
 begin
  assert_sender(p_device,p_sender);RRL_ASSEMBLY_RECOVERY_API.gateway_requests(p_device,p_sender,p_result);
  if json_object_t.parse(p_result).get_array('items').get_size>0 then return;end if;
  for current_session in(select *from RRL_ASSEMBLY_SESSION where DEVICE_ID=p_device and STATE='OPEN'and EXPIRES_AT>=systimestamp order by OPENED_AT desc fetch first 1 row only)loop
   s:=current_session;if s.SENDER_ID!=p_sender then raise_application_error(-20882,'ASSEMBLY_SESSION_SENDER_REQUIRED');end if;assert_open(s);
   for t in(select *from RRL_ASSEMBLY_STEP where SESSION_ID=s.SESSION_ID and(STATE='WAITING_BEFORE'or(STATE='ARMED'and(s.CONFIRMATION_MODE='AUTO'or BUTTON_INTENT_AT is not null)))
    order by SEQUENCE_NO fetch first 1 row only)loop
    o:=json_object_t();o.put('session_id',s.SESSION_ID);o.put('step_id',t.STEP_ID);o.put('operation_id',t.OPERATION_ID);o.put('case_task_id',s.CASE_PICK_TASK_ID);o.put('scan_container',s.CARRIER_IDENTIFIER);
    o.put('capture_id',case when t.STATE='WAITING_BEFORE'then t.BEFORE_CAPTURE_ID else t.AFTER_CAPTURE_ID end);o.put('phase',case when t.STATE='WAITING_BEFORE'then'BEFORE'else'AFTER'end);
    o.put('device_id',s.DEVICE_ID);o.put('device_policy_version',s.DEVICE_POLICY_VERSION);o.put('calibration_ref',s.CALIBRATION_REF);o.put('confirmation_mode',s.CONFIRMATION_MODE);
    o.put('expected_before_kg',RRL_STOCK_PLAN_HELPER.decimal_text(case when t.STATE='WAITING_BEFORE'then s.LAST_WEIGHT_KG else t.BEFORE_WEIGHT_KG end));
    o.put('min_delta_kg',RRL_STOCK_PLAN_HELPER.decimal_text(t.MIN_DELTA_KG));o.put('expected_content_version',t.SOURCE_VERSION);o.put('tare_capture_key',s.TARE_CAPTURE_KEY);
    o.put('expires_at',to_char(s.EXPIRES_AT at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM'));items.append(o);
   end loop;
  end loop;j.put('items',items);p_result:=j.to_clob;
 end;
end;
/
