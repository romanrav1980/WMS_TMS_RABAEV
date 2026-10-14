create or replace package RRL_CASE_SSCC_API authid definer as
 procedure issue(p_task number,p_request clob,p_actor varchar2,p_result out clob);
 procedure confirm_label(p_task number,p_sscc varchar2,p_actor varchar2,p_result out clob);
 procedure assert_ready(p_task number);
end;
/
create or replace package body RRL_CASE_SSCC_API as
 procedure fence is begin
  RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),6);
  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_STOCK_POLICY_GUARD','WAREHOUSE.METADATA'));
 end;
 procedure trusted(p_actor varchar2)is begin
  dbms_session.set_context('RRL_CASE_SSCC_CTX','TX_ID',dbms_transaction.local_transaction_id(true));
  dbms_session.set_context('RRL_CASE_SSCC_CTX','ACTOR',p_actor);
 end;
 procedure clear_context is begin dbms_session.clear_context('RRL_CASE_SSCC_CTX',null);end;
 procedure issue(p_task number,p_request clob,p_actor varchar2,p_result out clob)is
  d json_object_t:=json_object_t.parse(p_request);ct RRL_CASE_PICK_TASK%rowtype;
  op varchar2(100);code varchar2(18);old RRL_CASE_SSCC_LABEL%rowtype;n number;r json_object_t:=json_object_t();
 begin
  fence;RRL_CASE_TASK_ACCESS.assert_scope(p_task,p_actor,'case_pick_execute');
  op:=d.get_string('operation_id');
  if op is null or length(op)>100 or not regexp_like(op,'^[ -~]+$')or d.get_size!=3 then raise_application_error(-20887,'CASE_LABEL_REQUEST_REQUIRED');end if;
  select *into ct from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=p_task for update;
  RRL_CASE_TASK_ACCESS.assert_scope(p_task,p_actor,'case_pick_execute');
  begin
   select *into old from RRL_CASE_SSCC_LABEL where OPERATION_ID=op;
   if old.CASE_PICK_TASK_ID!=p_task or old.CREATED_BY!=p_actor or dbms_lob.compare(old.REQUEST_JSON,p_request)!=0 then raise_application_error(-20873,'CASE_LABEL_OPERATION_CONFLICT');end if;
   p_result:=old.RESULT_JSON;return;
  exception when no_data_found then null;end;
  if (ct.ASSIGNED_TO is not null and ct.ASSIGNED_TO!=p_actor)or ct.STATUS not in('NEW','ASSIGNED')or nvl(ct.PICKED_QTY,0)!=0 or ct.CONTENT_VERSION!=d.get_number('expected_content_version')
   or ct.SSCC!=d.get_string('scan_container')or ct.LEGACY_SBORKA_PALLET_ID is not null then raise_application_error(-20873,'CASE_LABEL_EMPTY_CURRENT_CARRIER_REQUIRED');end if;
  select count(*)into n from RRL_WMS_HU_LINK where CHILD_CASE_TASK_ID=p_task and ACTIVE_FLAG=1;
  if n>0 then raise_application_error(-20873,'CASE_LABEL_ALREADY_PACKED');end if;
  select count(*)into n from RRL_CASE_SSCC_LABEL where CASE_PICK_TASK_ID=p_task;
  if n>0 then raise_application_error(-20873,'CASE_LABEL_REPRINT_EXISTING');end if;
  code:=RRL_SSCC_ALLOCATOR.allocate(ct.WARE_ID,p_actor,'case_pick_execute');
  r.put('case_pick_task_id',p_task);r.put('sscc',code);r.put('original_carrier',ct.SSCC);r.put('content_version',ct.CONTENT_VERSION+1);
  r.put('operation_id',op);r.put('confirmed',false);p_result:=r.to_clob;
  trusted(p_actor);
  insert into RRL_CASE_SSCC_LABEL(OPERATION_ID,CASE_PICK_TASK_ID,SSCC,ORIGINAL_CARRIER,WARE_ID,PALLET_TYPE_ID,REQUESTED_VERSION,CREATED_BY,REQUEST_JSON,RESULT_JSON)
   values(op,p_task,code,ct.SSCC,ct.WARE_ID,ct.PALLET_TYPE_ID,ct.CONTENT_VERSION,p_actor,p_request,p_result);
  update RRL_CASE_PICK_TASK set SSCC=code,CONTENT_VERSION=CONTENT_VERSION+1,UPDATED_AT=systimestamp,UPDATED_BY=p_actor where CASE_PICK_TASK_ID=p_task;
  clear_context;
 exception when others then clear_context;raise;
 end;
 procedure confirm_label(p_task number,p_sscc varchar2,p_actor varchar2,p_result out clob)is
  ct RRL_CASE_PICK_TASK%rowtype;lbl RRL_CASE_SSCC_LABEL%rowtype;r json_object_t:=json_object_t();
 begin
  fence;RRL_CASE_TASK_ACCESS.assert_scope(p_task,p_actor,'case_pick_execute');
  select *into ct from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=p_task for update;
  RRL_CASE_TASK_ACCESS.assert_scope(p_task,p_actor,'case_pick_execute');
  select *into lbl from RRL_CASE_SSCC_LABEL where CASE_PICK_TASK_ID=p_task for update;
  if p_sscc is null or p_sscc!=lbl.SSCC or ct.SSCC!=lbl.SSCC then raise_application_error(-20873,'SCAN_ATTACHED_CASE_SSCC');end if;
  if lbl.CONFIRMED_AT is null then
   if ct.STATUS not in('NEW','ASSIGNED','IN_PROGRESS')or nvl(ct.PICKED_QTY,0)!=0 then raise_application_error(-20873,'CASE_LABEL_CONFIRM_BEFORE_FILL');end if;
   trusted(p_actor);
   update RRL_CASE_SSCC_LABEL set CONFIRMED_AT=systimestamp,CONFIRMED_BY=p_actor where CASE_PICK_TASK_ID=p_task;
   clear_context;
  end if;
  r.put('case_pick_task_id',p_task);r.put('sscc',lbl.SSCC);r.put('confirmed',true);p_result:=r.to_clob;
 exception when others then clear_context;raise;
 end;
 procedure assert_ready(p_task number)is
  required number;carrier varchar2(64);code varchar2(18);confirmed timestamp with time zone;
 begin
  select case when p.FINAL_WEIGHT_REQUIRED=1 and upper(p.LOAD_UNIT_CLASS)='CONTAINER'then 1 else 0 end,c.SSCC into required,carrier
   from RRL_CASE_PICK_TASK c join RRL_PALLET_TYPE p on p.PALLET_TYPE_ID=c.PALLET_TYPE_ID where c.CASE_PICK_TASK_ID=p_task;
  begin select SSCC,CONFIRMED_AT into code,confirmed from RRL_CASE_SSCC_LABEL where CASE_PICK_TASK_ID=p_task;
  exception when no_data_found then if required=0 then return;end if;raise_application_error(-20887,'SMALL_BOX_CONFIRMED_SSCC_REQUIRED');end;
  if carrier!=code or confirmed is null then raise_application_error(-20887,'CASE_ATTACHED_SSCC_CONFIRM_REQUIRED');end if;
 end;
end;
/
create or replace context RRL_CASE_SSCC_CTX using RRL_CASE_SSCC_API;
