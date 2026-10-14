create or replace package body RRL_STOCK_STORE_RECEIPT_CMD as

 procedure assert_input(m json_object_t,v in out nocopy json_object_t) is scan_text varchar2(200):=m.get_string('scan_place');root_node json_object_t;proof json_object_t;

 begin

  if v.get_boolean('already_received') then raise_application_error(-20886,'STORE_PLACE_ALREADY_RECEIVED');end if;

  if v.get_string('mode') is null or v.get_string('mode') not in('BARCODE','WEIGHT_PHOTO') then raise_application_error(-20886,'STORE_RECEIPT_MODE_UNSUPPORTED');end if;

  if v.get_boolean('requires_marked_recipient_flow') then RRL_STORE_MARK_CORE.verify_scans(v,m,proof);v.put('marked_unit_proof',proof);elsif m.has('unit_scans')and m.get_array('unit_scans').get_size>0 then raise_application_error(-20886,'STORE_UNEXPECTED_UNIT_SCANS');end if;

  if not m.has('before_cameras') or m.get_boolean('before_cameras') is null or not m.get_boolean('before_cameras') then raise_application_error(-20886,'STORE_RECEIPT_BEFORE_CAMERAS_REQUIRED');end if;

  if m.get_string('expected_composition_signature') is null or m.get_string('expected_composition_signature')!=v.get_string('composition_signature') then raise_application_error(-20890,'CLOSURE_CHANGED: store receipt manifest signature');end if;

  root_node:=treat(v.get_object('snapshot').get_array('nodes').get(0) as json_object_t);

  if scan_text is null or(scan_text!=v.get_string('root_scan_identifier') and(root_node.get_string('kind')='CASE' or v.get_string('root_sscc') is null or scan_text!=v.get_string('root_sscc'))) then raise_application_error(-20886,'STORE_RECEIPT_PHYSICAL_PLACE_SCAN_REQUIRED');end if;

 end;

 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is

  d json_object_t:=json_object_t.parse(p_request);src json_object_t:=d.get_object('source');m json_object_t:=d.get_object('metadata');

  f json_array_t:=json_array_t();r json_array_t:=json_array_t();v json_object_t;raw_domain clob;load_op varchar2(100):=src.get_string('load_operation_id');addr_text varchar2(255):=src.get_string('store_address');nodes json_array_t;x json_object_t;line_no number:=0;disposition json_array_t;has_issue boolean;weight_proof json_object_t;weight_issue boolean;unit_dispositions json_array_t;unit_value json_object_t;

 begin

  RRL_STOCK_STORE_RECEIPT_READ.describe_load(load_op,d.get_string('actor'),addr_text,raw_domain);v:=json_object_t.parse(raw_domain);assert_input(m,v);RRL_STORE_UNLOAD_CORE.validate_input(m,v);

  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');

  RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);

  if v.has('marked_unit_proof')then RRL_STORE_MARK_CORE.declare_rows(v,f,r);end if;

  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STORE.RECEIPT.LOAD:'||load_op);

  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));

  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TRANSPORT_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(v.get_number('trip_id')));

  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TT_HU_LOAD_FACT',load_op);

  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STORE_RECEIPT_FACT',p_operation);
  if m.has('unloading')and not m.get('unloading').is_null then RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STORE_UNLOAD_START',m.get_object('unloading').get_string('start_operation_id'));end if;

  RRL_STOCK_STORE_CUSTODY_CMD.declare_receipt(p_operation,load_op,v.get_string('root'),r);

  nodes:=v.get_object('snapshot').get_array('nodes');

  for i in 0..nodes.get_size-1 loop

   x:=treat(nodes.get(i) as json_object_t);

   if x.get_string('kind')='STOCK' then

    line_no:=line_no+1;RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STORE_RECEIPT_LINE',p_operation||':'||RRL_STOCK_PLAN_HELPER.decimal_text(line_no));

   end if;

  end loop;

  if line_no=0 then raise_application_error(-20886,'STORE_RECEIPT_PHYSICAL_LINES_REQUIRED');end if;

  RRL_STOCK_STORE_DISPOSITION.resolve_counts(v.get_object('snapshot').to_clob,m.to_clob,disposition,has_issue);

  RRL_STOCK_STORE_WEIGHT_CORE.resolve_weight(v.to_clob,m.to_clob,d.get_string('actor'),weight_proof,weight_issue);

  has_issue:=has_issue or weight_issue;

  if v.has('marked_unit_proof')then

   RRL_STORE_MARK_CORE.resolve_disposition(v.get_object('marked_unit_proof'),m,disposition,unit_dispositions);v.put('marked_unit_dispositions',unit_dispositions);

   for i in 0..unit_dispositions.get_size-1 loop unit_value:=treat(unit_dispositions.get(i)as json_object_t);RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STORE_RECEIPT_UNIT',p_operation||':'||unit_value.get_string('key'));end loop;

  end if;

  if weight_proof is null then v.put_null('weight');else v.put('weight',weight_proof);end if;

  RRL_STOCK_STORE_WEIGHT_CORE.declare_rows(p_operation,weight_proof,r);

  v.put('disposition',disposition);v.put('has_discrepancy',has_issue);v.put('case_note',m.get_string('case_note'));

  RRL_STOCK_STORE_DISPOSITION.declare_rows(p_operation,disposition,has_issue,r);

  p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=v.to_clob;

 end;

 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob) is

  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');op varchar2(100):=d.get_string('operation_id');plan clob;v json_object_t;fresh clob;now_v json_object_t;

  load_op varchar2(100);addr_text varchar2(255);root_text varchar2(200);signature_text varchar2(64);version_no number;trip_no number;n number;tree clob;j json_object_t:=json_object_t();lines json_array_t;state_text varchar2(30);fresh_disposition json_array_t;has_issue boolean;fresh_weight json_object_t;weight_issue boolean;fresh_units json_array_t;

 begin

  select RESOLVED_PLAN_JSON into plan from RRL_STOCK_OPERATION where OPERATION_ID=op;v:=json_object_t.parse(plan).get_object('domain');

  load_op:=v.get_string('load_operation_id');addr_text:=v.get_string('store_address');trip_no:=v.get_number('trip_id');

  select ID into n from RRL_TRANSPORT_TASK where ID=trip_no for update;

  select TT_ID into n from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=load_op for update;

  if n!=trip_no then raise_application_error(-20890,'CLOSURE_CHANGED: store receipt trip');end if;

  RRL_STOCK_STORE_RECEIPT_READ.describe_load(load_op,p_actor,addr_text,fresh);now_v:=json_object_t.parse(fresh);

  if now_v.get_string('composition_signature')!=v.get_string('composition_signature') or now_v.get_number('policy_version')!=v.get_number('policy_version') or now_v.get_string('mode')!=v.get_string('mode') or now_v.get_boolean('requires_marked_recipient_flow')!=v.get_boolean('requires_marked_recipient_flow') then raise_application_error(-20890,'CLOSURE_CHANGED: store receipt configuration or load');end if;

  assert_input(m,now_v);RRL_STORE_UNLOAD_CORE.validate_input(m,now_v);

  if v.has('marked_unit_proof')and(not now_v.has('marked_unit_proof')or dbms_lob.compare(v.get_object('marked_unit_proof').to_clob,now_v.get_object('marked_unit_proof').to_clob)!=0)then raise_application_error(-20890,'CLOSURE_CHANGED: store marked unit proof');end if;

  RRL_STOCK_STORE_DISPOSITION.resolve_counts(now_v.get_object('snapshot').to_clob,m.to_clob,fresh_disposition,has_issue);

  if dbms_lob.compare(fresh_disposition.to_clob,v.get_array('disposition').to_clob)!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: store disposition');end if;

  RRL_STOCK_STORE_WEIGHT_CORE.resolve_weight(now_v.to_clob,m.to_clob,p_actor,fresh_weight,weight_issue);

  if fresh_weight is null then

   if not v.get('weight').is_null then raise_application_error(-20890,'CLOSURE_CHANGED: receipt weight evidence');end if;

  elsif v.get('weight').is_null or dbms_lob.compare(fresh_weight.to_clob,v.get_object('weight').to_clob)!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: receipt weight evidence');end if;

  has_issue:=has_issue or weight_issue;

  if v.has('marked_unit_proof')then

   RRL_STORE_MARK_CORE.resolve_disposition(now_v.get_object('marked_unit_proof'),m,fresh_disposition,fresh_units);

   if dbms_lob.compare(fresh_units.to_clob,v.get_array('marked_unit_dispositions').to_clob)!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: store unit disposition');end if;

  end if;

  state_text:=case when has_issue then 'DISCREPANCY' else 'ACCEPTED' end;

  root_text:=v.get_string('root');signature_text:=v.get_string('composition_signature');version_no:=v.get_number('policy_version');tree:=v.get_object('snapshot').to_clob;

  insert into RRL_STORE_RECEIPT_FACT(OPERATION_ID,LOAD_OPERATION_ID,STORE_ADDR,ROOT_KEY,POLICY_VERSION,RECEIPT_STATE,CAMERA_CONFIRMED,COMPOSITION_SIGNATURE,COMPOSITION_JSON,RECEIVED_BY)

   values(op,load_op,addr_text,root_text,version_no,state_text,1,signature_text,tree,p_actor);

  RRL_STOCK_STORE_DISPOSITION.persist(op,v,p_actor,lines);

  if v.has('marked_unit_dispositions')then RRL_STORE_MARK_CORE.persist(op,load_op,v.get_array('marked_unit_dispositions'),p_actor);j.put('unit_dispositions',v.get_array('marked_unit_dispositions'));end if;

  RRL_STOCK_STORE_WEIGHT_CORE.persist(op,fresh_weight,p_actor);

  if state_text='ACCEPTED'then RRL_STOCK_STORE_CUSTODY_CMD.release_accepted(op,p_actor);j.put('load_custody_released',true);else j.put('load_custody_released',false);end if;

  if fresh_weight is not null then j.put('weight',fresh_weight);end if;

  if v.has('marked_unit_proof')then j.put('physical_unit_count',v.get_object('marked_unit_proof').get_number('physical_unit_count'));j.put('original_unit_signature',v.get_object('marked_unit_proof').get_string('unit_signature'));j.put('mark_scan_confirmed',true);j.put('regulatory_ack_verified',false);end if;

  RRL_STORE_UNLOAD_CORE.capture(p_request,p_actor);
  if m.has('unloading')and not m.get('unloading').is_null then j.put('unloading',m.get_object('unloading'));end if;
  j.put('operation_id',op);j.put('load_operation_id',load_op);j.put('store_address',addr_text);j.put('root',root_text);j.put('status',state_text);if has_issue then j.put('discrepancy_case_id',op);end if;j.put('accepted_lines',lines);j.put('warehouse_stock_consumed_again',false);j.put('government_ack_created',false);p_result:=j.to_clob;

 end;

end;


/
