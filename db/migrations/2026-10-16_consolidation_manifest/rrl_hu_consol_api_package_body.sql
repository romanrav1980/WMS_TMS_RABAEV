create or replace package body RRL_HU_CONSOL_API as
 g_tx varchar2(200);g_plan varchar2(100);g_operation varchar2(100);g_mutating boolean:=false;g_owned boolean:=false;
 procedure fail(p_reason varchar2,p_code number default -20886)is begin raise_application_error(p_code,p_reason);end;
 procedure assert_write(p_plan varchar2,p_operation varchar2 default null)is begin
  if not g_mutating or g_tx is null or g_tx!=nvl(dbms_transaction.local_transaction_id(false),chr(1))or nvl(p_plan,chr(1))!=g_plan
   or(p_operation is not null and p_operation!=g_operation)then fail('CONSOLIDATION_OWNER_CONTEXT_REQUIRED');end if;
  RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),6);
 end;
 procedure end_owned is begin
  g_mutating:=false;g_tx:=null;g_plan:=null;g_operation:=null;
  if g_owned then RRL_STOCK_LOCK_API.clear_plan;g_owned:=false;end if;
 end;
 procedure begin_owned is f json_array_t:=json_array_t();r json_array_t:=json_array_t();release_state varchar2(20);begin
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE',6);
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STOCK_POLICY_GUARD','WAREHOUSE.METADATA');
  RRL_STOCK_LOCK_API.begin_plan;g_owned:=true;lock table RRL_ACCESS_REV in share mode wait 2;
  RRL_STOCK_LOCK_API.acquire_policies(f.to_clob);RRL_STOCK_LOCK_API.acquire_resources(r.to_clob);
  select STATE into release_state from RRL_STOCK_RELEASE where RELEASE_ID=1;
  if release_state is null or release_state not in('PREPARED','ACTIVE')then fail('CONSOLIDATION_RELEASE_CLOSED',-20860);end if;
  g_tx:=dbms_transaction.local_transaction_id(true);
 end;
 procedure validate_keys(p_value json_object_t,p_names varchar2)is keys json_key_list:=p_value.get_keys;a json_array_t:=json_array_t(p_names);ok boolean;begin
  if keys.count!=a.get_size then fail('CONSOLIDATION_EXACT_INPUT_REQUIRED',-20881);end if;
  for i in 1..keys.count loop ok:=false;for k in 0..a.get_size-1 loop if keys(i)=a.get_string(k)then ok:=true;exit;end if;end loop;
   if not ok then fail('CONSOLIDATION_EXACT_INPUT_REQUIRED',-20881);end if;
  end loop;
 end;
 procedure execute_command(p_actor nvarchar2,p_command clob,p_result out clob)is
  d json_object_t;members json_array_t;operation_value varchar2(400);plan_value varchar2(400);kind_value varchar2(80);kind_status varchar2(60);reason_value varchar2(4000);
  root_value varchar2(800);cell_value varchar2(240);ware_value number;expected_version number;version_value number;n number;id number;row_count number:=0;
  old_plan RRL_HU_CONSOL_PLAN%rowtype;old_exists boolean:=false;old_receipt RRL_HU_CONSOL_RECEIPT%rowtype;
  ff RRL_CUSTOMER_ORDER_FULFILLMENT%rowtype;st RRL_SBORKA_PALLETS%rowtype;signature_value varchar2(64);request_hash varchar2(64);
  type id_set is table of boolean index by varchar2(100);seen id_set;k varchar2(100);result_value json_object_t:=json_object_t();frozen_value clob;
  procedure authorize_current is st_seen id_set;st_key varchar2(100);begin
   begin select *into old_plan from RRL_HU_CONSOL_PLAN where PLAN_ID=plan_value;old_exists:=true;
    RRL_HU_CONSOL_READ.assert_plan_scope(plan_value,p_actor,'warehouse_task_execute');
   exception when no_data_found then old_exists:=false;end;
   if kind_value='SAVE'then
    RRL_HU_CONSOL_READ.assert_scope(p_actor,ware_value,'warehouse_task_execute');
    select count(*)into n from RRL_CELLS where CELL=cell_value and WARE_ID=ware_value;if n!=1 then fail('CONSOLIDATION_TARGET_CELL_WARE_REQUIRED');end if;
    for i in 0..members.get_size-1 loop
     id:=members.get_number(i);select *into ff from RRL_CUSTOMER_ORDER_FULFILLMENT where FULFILLMENT_ID=id;
     if ff.LEGACY_SBORKA_PALLET_ID is null or ff.PALLET_UID is null then fail('CONSOLIDATION_PREPARED_FULFILLMENT_REQUIRED');end if;
     select *into st from RRL_SBORKA_PALLETS where ID=ff.LEGACY_SBORKA_PALLET_ID;
     st_key:=RRL_STOCK_PLAN_HELPER.decimal_text(st.ID);if st_seen.exists(st_key)then fail('CONSOLIDATION_DUPLICATE_ST',-20881);end if;st_seen(st_key):=true;
     RRL_HU_CONSOL_READ.assert_scope(p_actor,st.WARE_ID,'warehouse_task_view');
     if st.PALLET_UID is null or st.PALLET_UID!=ff.PALLET_UID then fail('CONSOLIDATION_ST_REFERENCE_CHANGED');end if;
    end loop;
    for w in(select c.WARE_ID from RRL_PALLETS pp join RRL_CELLS c on c.CELL=pp.HU_CURRENT_CELL where pp.UID_PALLET=root_value)loop RRL_HU_CONSOL_READ.assert_scope(p_actor,w.WARE_ID,'warehouse_task_view');end loop;
   elsif not old_exists then fail('CONSOLIDATION_PLAN_NOT_FOUND',-20884);end if;
  end;
 begin
  if g_owned or g_tx is not null then fail('CONSOLIDATION_NESTED_CONTEXT_FORBIDDEN');end if;
  if p_command is null or dbms_lob.getlength(p_command)>262144 then fail('CONSOLIDATION_INPUT_BOUND',-20881);end if;
  d:=json_object_t.parse(p_command);operation_value:=d.get_string('operation_id');plan_value:=d.get_string('plan_id');kind_value:=d.get_string('command_type');
  expected_version:=d.get_number('expected_version');reason_value:=d.get_string('reason');
  if p_actor is null or operation_value is null or not regexp_like(operation_value,'^[A-Za-z0-9_.:-]{1,100}$')
   or plan_value is null or not regexp_like(plan_value,'^[A-Za-z0-9_.:-]{1,100}$')or expected_version is null or expected_version<0 or expected_version!=trunc(expected_version)
   or reason_value is null or length(reason_value)>1000 then fail('CONSOLIDATION_ID_VERSION_REASON_REQUIRED',-20881);end if;
  if kind_value='SAVE'then
   validate_keys(d,'["command_type","operation_id","plan_id","expected_version","reason","root_identifier","warehouse_id","cell","fulfillment_ids"]');
   root_value:=d.get_string('root_identifier');ware_value:=d.get_number('warehouse_id');cell_value:=d.get_string('cell');
   RRL_HU_CONSOL_READ.assert_scope(p_actor,ware_value,'warehouse_task_execute');
   if not d.get('fulfillment_ids').is_array then fail('CONSOLIDATION_MEMBER_ARRAY_REQUIRED',-20881);end if;members:=d.get_array('fulfillment_ids');
   if root_value is null or lengthb(root_value)>200 or root_value!=trim(root_value)or cell_value is null or lengthb(cell_value)>60
    or members.get_size<1 or members.get_size>200 then fail('CONSOLIDATION_ROOT_CELL_MEMBER_BOUND',-20881);end if;
   for i in 0..members.get_size-1 loop
    if not members.get(i).is_number then fail('CONSOLIDATION_POSITIVE_FULFILLMENT_ID_REQUIRED',-20881);end if;
    id:=members.get_number(i);if id is null or id<1 or id!=trunc(id)then fail('CONSOLIDATION_POSITIVE_FULFILLMENT_ID_REQUIRED',-20881);end if;
    k:=RRL_STOCK_PLAN_HELPER.decimal_text(id);if seen.exists(k)then fail('CONSOLIDATION_DUPLICATE_FULFILLMENT',-20881);end if;seen(k):=true;
   end loop;
   select count(*)into n from RRL_PALLETS where UID_PALLET=root_value or SSCC=root_value;
   if n>1 then fail('CONSOLIDATION_AMBIGUOUS_ROOT');elsif n=1 then
    select UID_PALLET into root_value from RRL_PALLETS where(UID_PALLET=root_value or SSCC=root_value)and HU_KIND='CONTAINER';
   end if;
  elsif kind_value='CANCEL'then validate_keys(d,'["command_type","operation_id","plan_id","expected_version","reason"]');
  else fail('CONSOLIDATION_COMMAND_REQUIRED',-20881);end if;
  authorize_current;
  begin
   begin_owned;authorize_current;
   request_hash:=rawtohex(sys.dbms_crypto.hash(p_command,sys.dbms_crypto.hash_sh256));
   begin select *into old_receipt from RRL_HU_CONSOL_RECEIPT where OPERATION_ID=operation_value;
    if old_receipt.ACTOR!=p_actor or old_receipt.PLAN_ID!=plan_value or old_receipt.REQUEST_HASH!=request_hash then fail('CONSOLIDATION_OPERATION_CONTENT_CONFLICT',-20890);end if;
    p_result:=old_receipt.RESULT_JSON;end_owned;return;
   exception when no_data_found then null;end;
   if(old_exists and old_plan.PLAN_VERSION!=expected_version)or(not old_exists and expected_version!=0)then fail('CONSOLIDATION_VERSION_CONFLICT',-20890);end if;
   if old_exists and old_plan.STATUS='CANCELLED'then fail('CONSOLIDATION_CANCELLED_PLAN_IMMUTABLE');end if;
   if kind_value='SAVE'then
    select count(*)into n from RRL_HU_CONSOL_PLAN where ROOT_UID=root_value and STATUS='ACTIVE'and PLAN_ID!=plan_value;
    if n>0 then fail('CONSOLIDATION_ACTIVE_ROOT_ALREADY_PLANNED',-20890);end if;
    select count(*)into n from RRL_PALLETS where UID_PALLET=root_value and HU_SHIPPED_OPERATION is not null;
    if n>0 then fail('CONSOLIDATION_DEPARTED_ROOT_IMMUTABLE');end if;
    for i in 0..members.get_size-1 loop id:=members.get_number(i);select STATUS into kind_status from RRL_CUSTOMER_ORDER_FULFILLMENT where FULFILLMENT_ID=id;
     if kind_status not in('PLANNED','PICKED')then fail('CONSOLIDATION_PREPARED_FULFILLMENT_REQUIRED');end if;end loop;
   end if;
   g_plan:=plan_value;g_operation:=operation_value;g_mutating:=true;version_value:=expected_version+1;
   if not old_exists then
    insert into RRL_HU_CONSOL_PLAN(PLAN_ID,ROOT_UID,TARGET_WARE_ID,TARGET_CELL,STATUS,PLAN_VERSION,REASON,CREATED_BY,UPDATED_BY)
     values(plan_value,root_value,ware_value,cell_value,'ACTIVE',version_value,reason_value,p_actor,p_actor);
   elsif kind_value='SAVE'then
    update RRL_HU_CONSOL_PLAN set ROOT_UID=root_value,TARGET_WARE_ID=ware_value,TARGET_CELL=cell_value,PLAN_VERSION=version_value,REASON=reason_value,UPDATED_BY=p_actor,UPDATED_AT=systimestamp where PLAN_ID=plan_value;
   else update RRL_HU_CONSOL_PLAN set STATUS='CANCELLED',PLAN_VERSION=version_value,REASON=reason_value,UPDATED_BY=p_actor,UPDATED_AT=systimestamp where PLAN_ID=plan_value;end if;
   if kind_value='SAVE'then
    delete from RRL_HU_CONSOL_MEMBER where PLAN_ID=plan_value;
    for i in 0..members.get_size-1 loop
     id:=members.get_number(i);select *into ff from RRL_CUSTOMER_ORDER_FULFILLMENT where FULFILLMENT_ID=id;
     select *into st from RRL_SBORKA_PALLETS where ID=ff.LEGACY_SBORKA_PALLET_ID;signature_value:=RRL_HU_CONSOL_READ.rows_signature(st.PALLET_UID);
     select count(*)into n from RRL_SBORKA_PALLET_ROWS where PALLET_UID=st.PALLET_UID;row_count:=row_count+n;if row_count>2000 then fail('CONSOLIDATION_TOTAL_ST_ROW_BOUND_2000',-20881);end if;
     insert into RRL_HU_CONSOL_MEMBER(PLAN_ID,FULFILLMENT_ID,EXPECTED_ST_ID,EXPECTED_PALLET_UID,SOURCE_WARE_ID,ROWS_SIGNATURE)
      values(plan_value,id,st.ID,st.PALLET_UID,st.WARE_ID,signature_value);
    end loop;
   end if;
   frozen_value:=RRL_HU_CONSOL_READ.frozen_plan(plan_value);result_value.put('operation_id',operation_value);result_value.put('plan_id',plan_value);
   result_value.put('version',version_value);result_value.put('status',case kind_value when 'SAVE'then'ACTIVE'else'CANCELLED'end);
   result_value.put('expectation_signature',rawtohex(sys.dbms_crypto.hash(frozen_value,sys.dbms_crypto.hash_sh256)));result_value.put('stock_changed',false);
   p_result:=result_value.to_clob;
   insert into RRL_HU_CONSOL_RECEIPT(OPERATION_ID,PLAN_ID,ACTOR,REQUEST_HASH,REQUEST_JSON,FROZEN_PLAN_JSON,RESULT_JSON)
    values(operation_value,plan_value,p_actor,request_hash,p_command,frozen_value,p_result);
   end_owned;
  exception when others then end_owned;raise;end;
 end;
end;
/
