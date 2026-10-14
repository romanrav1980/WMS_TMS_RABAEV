create or replace package RRL_STOCK_LOAD_RECONCILE_CMD authid definer accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/
create or replace package body RRL_STOCK_LOAD_RECONCILE_CMD as
 function digest(s clob) return varchar2 is begin return rawtohex(sys.dbms_crypto.hash(s,sys.dbms_crypto.hash_sh256));end;
 procedure read_history(p_original varchar2,p_tree out json_object_t,p_shipments out json_array_t) is
  result clob;plan clob;original_kind varchar2(80);original_state varchar2(20);j json_object_t;domain_json json_object_t;n number;
 begin
  select COMMAND_TYPE,STATE,RESULT_JSON,RESOLVED_PLAN_JSON into original_kind,original_state,result,plan from RRL_STOCK_OPERATION where OPERATION_ID=p_original;
  if original_kind!='HU_SHIP' or original_state!='APPLIED' then raise_application_error(-20886,'RECONCILE_APPLIED_WHOLE_HU_SHIPMENT_REQUIRED');end if;
  j:=json_object_t.parse(result);domain_json:=json_object_t.parse(plan).get_object('domain');
  if j.has('physical_load') and not j.get('physical_load').is_null then raise_application_error(-20886,'RECONCILE_ALREADY_HAS_PHYSICAL_LOAD');end if;
  p_tree:=j.get_object('composition_at_departure');p_shipments:=domain_json.get_array('shipments');
  if p_tree.get_array('nodes').get_size<2 or p_tree.get_array('nodes').get_size>200 or p_shipments.get_size=0 or p_shipments.get_size>200
   or p_tree.get_array('ancestors').get_size!=0 then raise_application_error(-20886,'RECONCILE_WHOLE_HU_HISTORY_REQUIRED');end if;
  select count(*) into n from RRL_TT_LOAD_RECONCILE where SHIPPING_OPERATION_ID=p_original;
  if n>0 then raise_application_error(-20886,'RECONCILE_ORIGINAL_ALREADY_LINKED');end if;
 exception when no_data_found then raise_application_error(-20886,'RECONCILE_ORIGINAL_SHIPMENT_NOT_FOUND');
 end;
 procedure assert_departed(p_tree json_object_t,p_shipments json_array_t,p_original varchar2) is
  nodes json_array_t:=p_tree.get_array('nodes');links json_array_t:=p_tree.get_array('links');x json_object_t;
  uid_text varchar2(200);case_no number;node_version number;kind_text varchar2(20);n number;st_no number;original_plan clob;epochs clob;expected_epoch number;actual_epoch number;
 begin
  select RESOLVED_PLAN_JSON into original_plan from RRL_STOCK_OPERATION where OPERATION_ID=p_original;
  epochs:=json_object_t.parse(original_plan).get_array('physical_before').to_clob;
  for i in 0..nodes.get_size-1 loop
   x:=treat(nodes.get(i) as json_object_t);uid_text:=x.get_string('uid');kind_text:=x.get_string('kind');node_version:=x.get_number('version');
   if kind_text='CONTAINER' then
    select count(*) into n from RRL_PALLETS where UID_PALLET=uid_text and HU_SHIPPED_OPERATION=p_original and HU_CURRENT_CELL is null and HU_CONTENT_VERSION=node_version+1;
    if n!=1 then raise_application_error(-20890,'CLOSURE_CHANGED: reconciled container departure');end if;
   elsif kind_text='CASE' then
    case_no:=x.get_number('case_task_id');
    select count(*) into n from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=case_no and STATUS='SHIPPED' and SHIPPED_OPERATION=p_original;
    if n!=1 then raise_application_error(-20890,'CLOSURE_CHANGED: reconciled CASE shipment');end if;
   elsif kind_text!='STOCK' then raise_application_error(-20886,'RECONCILE_NODE_KIND_UNSUPPORTED');end if;
   if kind_text='STOCK' then
    select VERSION_NO into expected_epoch from json_table(epochs,'$[*]' columns(UID_TEXT varchar2(200) path '$.uid',VERSION_NO number path '$.version')) where UID_TEXT=uid_text;
    select STOCK_COMPOSITION_VERSION into actual_epoch from RRL_PALLETS where UID_PALLET=uid_text;
    if actual_epoch!=expected_epoch+1 then raise_application_error(-20890,'CLOSURE_CHANGED: reconciled stock composition epoch');end if;
    select count(*) into n from RRL_REMAINS where UID_POLETA=uid_text and (REMAIN!=0 or HARD_RESERVED_BASE!=0);
    if n>0 then raise_application_error(-20890,'CLOSURE_CHANGED: reconciled stock returned or reused');end if;
    select count(*) into n from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=uid_text and STOCK_STATUS!='ISSUED';
    if n>0 then raise_application_error(-20890,'CLOSURE_CHANGED: reconciled physical units returned');end if;
   end if;
  end loop;
  for i in 0..links.get_size-1 loop
   x:=treat(links.get(i) as json_object_t);case_no:=x.get_number('id');node_version:=x.get_number('version');
   if case_no is not null then
    select count(*) into n from RRL_WMS_HU_LINK where HU_LINK_ID=case_no and ACTIVE_FLAG=0 and UNLINKED_OPERATION_ID=p_original;
    if n!=1 then raise_application_error(-20890,'CLOSURE_CHANGED: reconciled departure link');end if;
   end if;
  end loop;
  for i in 0..p_shipments.get_size-1 loop
   x:=treat(p_shipments.get(i) as json_object_t).get_object('domain');st_no:=x.get_number('document_id');
   select count(*) into n from RRL_SBORKA_PALLETS where ID=st_no and CONDITION=2;
   if n!=1 then raise_application_error(-20890,'CLOSURE_CHANGED: reconciled ST status');end if;
   if x.get_number('case_task') is null then
    select count(*) into n from RRL_CUSTOMER_ORDER_FULFILLMENT where LEGACY_SBORKA_PALLET_ID=st_no and STATUS='SHIPPED' and SHIPPED_OPERATION_ID=p_original;
    if n=0 then raise_application_error(-20886,'RECONCILE_PHYSICAL_OWNER_PROOF_REQUIRED');end if;
   end if;
  end loop;
 end;
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');original_op varchar2(100):=d.get_object('source').get_string('shipping_operation_id');
  tree json_object_t;ships json_array_t;f json_array_t:=json_array_t();r json_array_t:=json_array_t();nodes json_array_t;links json_array_t;x json_object_t;loading json_object_t;v json_object_t:=json_object_t();uid_text varchar2(200);case_no number;st_no number;
 begin
  read_history(original_op,tree,ships);assert_departed(tree,ships,original_op);
  if m.get_number('expected_version') is null or m.get_number('expected_version')!=treat(tree.get_array('nodes').get(0) as json_object_t).get_number('version') or m.get_string('expected_composition_signature') is null or m.get_string('expected_composition_signature')!=digest(tree.to_clob) then raise_application_error(-20890,'CLOSURE_CHANGED: reconciliation history signature');end if;
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');
  RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','TT.RECONCILE:'||original_op);
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TT_LOAD_RECONCILE',p_operation);
  nodes:=tree.get_array('nodes');links:=tree.get_array('links');
  for i in 0..nodes.get_size-1 loop
   x:=treat(nodes.get(i) as json_object_t);uid_text:=x.get_string('uid');
   RRL_STOCK_PLAN_HELPER.anchor(r,30,'HU',uid_text);
   if x.get_string('kind')='CASE' then
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_CASE_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(x.get_number('case_task_id')));
   else RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PALLETS',uid_text);end if;
   if x.get_string('kind')='STOCK' then RRL_STOCK_PLAN_HELPER.anchor(r,50,'STOCK',uid_text);end if;
  end loop;
  for i in 0..links.get_size-1 loop
   x:=treat(links.get(i) as json_object_t);case_no:=x.get_number('id');
   if case_no is not null then RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_WMS_HU_LINK',RRL_STOCK_PLAN_HELPER.decimal_text(case_no));end if;
  end loop;
  for i in 0..ships.get_size-1 loop
   x:=treat(ships.get(i) as json_object_t).get_object('domain');st_no:=x.get_number('document_id');
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_SBORKA_PALLETS',RRL_STOCK_PLAN_HELPER.decimal_text(st_no));
  end loop;
  RRL_STOCK_HU_LOAD_CORE.compile_load(p_request,tree.to_clob,ships.to_clob,f,r,loading);
  if loading is null then raise_application_error(-20886,'RECONCILE_CURRENT_LOADING_CONTEXT_REQUIRED');end if;
  v.put('original_operation',original_op);v.put('snapshot',tree);v.put('shipments',ships);v.put('loading',loading);v.put('signature',digest(tree.to_clob));
  p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=v.to_clob;
 end;
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob) is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');op varchar2(100):=d.get_string('operation_id');plan clob;
  v json_object_t;tree json_object_t;ships json_array_t;fresh json_object_t;fresh_ships json_array_t;nodes clob;ships_json clob;x json_object_t;alias_text varchar2(200);n number;original_op varchar2(100);j json_object_t:=json_object_t();
 begin
  if RRL_HAS_WRIGHT(p_actor,'stock_posting_shipping')!=1 then raise_application_error(-20882,'PHYSICAL_LOAD_FORBIDDEN');end if;
  select RESOLVED_PLAN_JSON into plan from RRL_STOCK_OPERATION where OPERATION_ID=op;v:=json_object_t.parse(plan).get_object('domain');
  original_op:=v.get_string('original_operation');tree:=v.get_object('snapshot');ships:=v.get_array('shipments');x:=treat(tree.get_array('nodes').get(0) as json_object_t);alias_text:=x.get_string('sscc');
  if m.get_string('scan_container') is null or(m.get_string('scan_container')!=tree.get_string('root') and(alias_text is null or m.get_string('scan_container')!=alias_text))
   or m.get_string('scan_cell') is null or m.get_string('scan_cell')!=tree.get_string('cell') then raise_application_error(-20886,'RECONCILE_PHYSICAL_PLACE_CELL_SCAN_REQUIRED');end if;
  RRL_STOCK_HU_LOAD_CORE.begin_load(v.get_object('loading').to_clob);
  ships_json:=ships.to_clob;
  for z in(select ID from RRL_SBORKA_PALLETS where ID in(select ID from json_table(ships_json,'$[*]' columns(ID number path '$.domain.document_id'))) order by ID)loop select ID into n from RRL_SBORKA_PALLETS where ID=z.ID for update;end loop;
  nodes:=tree.get_array('nodes').to_clob;
  for z in(select CASE_PICK_TASK_ID from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID in(select ID from json_table(nodes,'$[*]' columns(ID number path '$.case_task_id')))order by CASE_PICK_TASK_ID)loop select CASE_PICK_TASK_ID into n from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=z.CASE_PICK_TASK_ID for update;end loop;
  read_history(original_op,fresh,fresh_ships);
  if digest(fresh.to_clob)!=v.get_string('signature') then raise_application_error(-20890,'CLOSURE_CHANGED: reconciliation historical manifest');end if;
  assert_departed(tree,ships,original_op);
  RRL_STOCK_HU_LOAD_CORE.finish_load(v.get_object('loading').to_clob,tree.to_clob,op,p_actor);
  insert into RRL_TT_LOAD_RECONCILE(LOAD_OPERATION_ID,SHIPPING_OPERATION_ID,RECONCILED_BY) values(op,original_op,p_actor);
  j.put('operation_id',op);j.put('shipping_operation_id',original_op);j.put('status','LOADED');j.put('physical_load',v.get_object('loading'));j.put('composition_at_departure',tree);j.put('stock_consumed_again',false);p_result:=j.to_clob;
 end;
end;
/
