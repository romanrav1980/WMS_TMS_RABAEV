create or replace package RRL_WEIGHT_BOX_CHOICE_API authid definer as
 procedure approve_request(p_request clob,p_actor varchar2,p_result out clob);
 procedure cancel_choice(p_choice varchar2,p_actor varchar2,p_reason varchar2,p_result out clob);
end;
/

create or replace package body RRL_WEIGHT_BOX_CHOICE_API as
 procedure clear_context is begin
  dbms_session.set_context('RRL_WEIGHT_CHOICE_CTX','TX_ID',null);
  dbms_session.set_context('RRL_WEIGHT_CHOICE_CTX','CHOICE_ID',null);
  dbms_session.set_context('RRL_WEIGHT_CHOICE_CTX','PHASE',null);
  dbms_session.set_context('RRL_WEIGHT_CHOICE_CTX','ACTOR',null);
 end;
 procedure enter_context(p_choice varchar2,p_phase varchar2,p_actor varchar2)is
 begin
  if sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')is not null or RRL_HAS_WRIGHT(p_actor,'case_pick_short_approve')!=1
   then raise_application_error(-20863,'WEIGHT_CHOICE_BUSINESS_METADATA_OWNER_REQUIRED');end if;
  RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),6);
  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_STOCK_POLICY_GUARD','WAREHOUSE.METADATA'));
  dbms_session.set_context('RRL_WEIGHT_CHOICE_CTX','TX_ID',dbms_transaction.local_transaction_id(true));
  dbms_session.set_context('RRL_WEIGHT_CHOICE_CTX','ACTOR',p_actor);
  dbms_session.set_context('RRL_WEIGHT_CHOICE_CTX','CHOICE_ID',p_choice);
  dbms_session.set_context('RRL_WEIGHT_CHOICE_CTX','PHASE',p_phase);
 end;
 procedure approve_request(p_request clob,p_actor varchar2,p_result out clob)is
  d json_object_t;source_json json_object_t;box_json json_object_t;candidate json_object_t;label_json json_object_t;
  boxes json_array_t;result_json json_object_t:=json_object_t();
  old RRL_PICK_WEIGHT_CHOICE%rowtype;
  choice_value varchar2(100);key_value varchar2(64);mode_value varchar2(24);reason_value varchar2(4000);
  row_id number;order_id number;ware number;article varchar2(160);uid varchar2(150);cell_value varchar2(60);stock_version number;
  mass number;version number;pct number;requested number;remaining number;signature_value varchar2(64);n number;
  source_wire clob;result_wire clob;
 begin
  if p_request is null or dbms_lob.getlength(p_request)>16000 then raise_application_error(-20881,'WEIGHT_CHOICE_REQUEST_BOUND');end if;
  d:=json_object_t.parse(p_request);choice_value:=d.get_string('choice_id');row_id:=d.get_number('customer_order_row_id');
  if choice_value is null or length(choice_value)>100 or not regexp_like(choice_value,'^[A-Za-z0-9_.:-]+$')
   or row_id is null or row_id<1 or row_id!=trunc(row_id)then raise_application_error(-20881,'WEIGHT_CHOICE_IDENTITY_REQUIRED');end if;
  select CUSTOMER_ORDER_ID,ARTICUL into order_id,article from RRL_CUSTOMER_ORDER_ROW where CUSTOMER_ORDER_ROW_ID=row_id;
  RRL_PICK_PLAN_ACCESS.assert_scope(order_id,p_actor,'case_pick_short_approve');
  select WARE_ID into ware from RRL_CUSTOMER_ORDER where CUSTOMER_ORDER_ID=order_id;
  select count(*)into n from RRL_PICK_WEIGHT_CHOICE where CHOICE_ID=choice_value;
  if n>0 then
   select *into old from RRL_PICK_WEIGHT_CHOICE where CHOICE_ID=choice_value;
   if old.APPROVED_BY!=p_actor or old.CUSTOMER_ORDER_ROW_ID!=row_id or dbms_lob.compare(old.REQUEST_JSON,p_request)!=0
    then raise_application_error(-20873,'WEIGHT_CHOICE_ID_CONTENT_CONFLICT');end if;
   if old.WARE_ID!=ware then raise_application_error(-20882,'WEIGHT_CHOICE_ORIGINAL_WARE_CHANGED');end if;
   p_result:=old.RESULT_JSON;return;
  end if;
  source_wire:=RRL_WEIGHT_BOX_PLANNING_READ.snapshot_json(row_id,p_actor,'case_pick_short_approve');source_json:=json_object_t.parse(source_wire);
  signature_value:=source_json.get_string('source_signature');
  if d.get_string('source_signature')is null or d.get_string('source_signature')!=signature_value
   then raise_application_error(-20886,'WEIGHT_CHOICE_CURRENT_SOURCE_CHANGED');end if;
  remaining:=RRL_STOCK_MATH.quantity(source_json.get_string('remaining_row_quantity'));
  key_value:=d.get_string('physical_unit_key');boxes:=source_json.get_array('boxes');n:=0;
  for i in 0..boxes.get_size-1 loop
   candidate:=treat(boxes.get(i)as json_object_t);
   if candidate.get_string('physical_unit_key')=key_value then box_json:=candidate;n:=n+1;end if;
  end loop;
  if n!=1 or box_json is null then raise_application_error(-20886,'WEIGHT_CHOICE_CURRENT_AVAILABLE_BOX_REQUIRED');end if;
  if not box_json.get_boolean('measurements_ready')then raise_application_error(-20886,'WEIGHT_CHOICE_PHYSICAL_MEASUREMENTS_REQUIRED');end if;
  label_json:=json_object_t.parse(RRL_WEIGHT_BOX_READ.decode_json(d.get_string('weighted_box_barcode')));
  RRL_WEIGHT_BOX_READ.assert_sku(article,label_json.get_string('gtin'));
  mass:=RRL_STOCK_MATH.quantity(box_json.get_string('net_weight_kg'));
  if label_json.get_string('identity')!=box_json.get_string('unit_id') or RRL_STOCK_MATH.quantity(label_json.get_string('net_weight_kg'))!=mass
   then raise_application_error(-20886,'WEIGHT_CHOICE_SAME_SCANNED_WHOLE_BOX_REQUIRED');end if;
  mode_value:=d.get_string('choice_mode');reason_value:=d.get_string('reason');
  if reason_value is null or length(trim(reason_value))<3 or length(reason_value)>1000 then raise_application_error(-20886,'WEIGHT_CHOICE_REASON_REQUIRED');end if;
  if mode_value is null or mode_value not in('WITHIN_TOLERANCE','LAST_WHOLE_BOX')
   or(mode_value='WITHIN_TOLERANCE'and not box_json.get_boolean('within_tolerance'))
   or(mode_value='LAST_WHOLE_BOX'and not box_json.get_boolean('exception_required'))
   then raise_application_error(-20886,'WEIGHT_CHOICE_MATCHING_EXPLICIT_DECISION_REQUIRED');end if;
  uid:=box_json.get_string('pallet_identifier');cell_value:=box_json.get_string('source_cell');stock_version:=box_json.get_number('stock_version');
  version:=source_json.get_number('policy_version');pct:=source_json.get_number('tolerance_pct');
  requested:=RRL_STOCK_MATH.quantity(source_json.get_string('requested_order_quantity'));
  result_json.put('choice_id',choice_value);result_json.put('customer_order_row_id',row_id);result_json.put('physical_unit_key',key_value);
  result_json.put('pallet_identifier',uid);result_json.put('source_cell',cell_value);result_json.put('selected_net_weight_kg',RRL_STOCK_PLAN_HELPER.decimal_text(mass));
  result_json.put('original_order_weight_kg',RRL_STOCK_PLAN_HELPER.decimal_text(requested));
  result_json.put('choice_mode',mode_value);result_json.put('status','ACCEPTED');result_json.put('stock_changed',false);result_json.put('plan_created',false);result_json.put('no_split',true);
  result_wire:=result_json.to_clob;
  enter_context(choice_value,'APPROVE',p_actor);
  insert into RRL_PICK_WEIGHT_CHOICE(CHOICE_ID,CUSTOMER_ORDER_ROW_ID,CUSTOMER_ORDER_ID,WARE_ID,ARTICLE,PHYSICAL_UNIT_KEY,SOURCE_UID,SOURCE_CELL,STOCK_VERSION,
   NET_WEIGHT_KG,POLICY_VERSION,TOLERANCE_PCT,ORIGINAL_ORDER_KG,ORIGINAL_REMAINING_KG,CHOICE_MODE,APPROVED_BY,REASON_TEXT,SOURCE_SIGNATURE,SOURCE_JSON,REQUEST_JSON,RESULT_JSON)
   values(choice_value,row_id,order_id,ware,article,key_value,uid,cell_value,stock_version,mass,version,pct,requested,remaining,mode_value,p_actor,reason_value,signature_value,source_wire,p_request,result_wire);
  clear_context;p_result:=result_wire;
 exception when others then clear_context;raise;
 end;
 procedure cancel_choice(p_choice varchar2,p_actor varchar2,p_reason varchar2,p_result out clob)is
  old RRL_PICK_WEIGHT_CHOICE%rowtype;result_json json_object_t:=json_object_t();active_tasks number;
 begin
  select *into old from RRL_PICK_WEIGHT_CHOICE where CHOICE_ID=p_choice for update;
  RRL_PICK_PLAN_ACCESS.assert_scope(old.CUSTOMER_ORDER_ID,p_actor,'case_pick_short_approve');
  if old.STATUS='USED'then
   select count(*)into active_tasks from RRL_PICK_TASK where PICK_PLAN_LINE_ID=old.PICK_PLAN_LINE_ID and STATUS not in('CANCELLED','FAILED');
   if active_tasks>0 then raise_application_error(-20886,'WEIGHT_CHOICE_CANCEL_ASSOCIATED_PLAN_FIRST');end if;
  end if;
  if old.STATUS='CANCELLED'then
   if old.CANCELLED_BY!=p_actor or old.CANCEL_REASON!=p_reason then raise_application_error(-20873,'WEIGHT_CHOICE_CANCEL_CONTENT_CONFLICT');end if;
  else
   if p_reason is null or length(trim(p_reason))<3 or length(p_reason)>1000 then raise_application_error(-20886,'WEIGHT_CHOICE_CANCEL_REASON_REQUIRED');end if;
   enter_context(p_choice,'CANCEL',p_actor);
   update RRL_PICK_WEIGHT_CHOICE set STATUS='CANCELLED',CANCELLED_BY=p_actor,CANCELLED_AT=systimestamp,CANCEL_REASON=p_reason where CHOICE_ID=p_choice;
   clear_context;
  end if;
  result_json.put('choice_id',p_choice);result_json.put('status','CANCELLED');result_json.put('stock_changed',false);p_result:=result_json.to_clob;
 exception when others then clear_context;raise;
 end;
end;
/
