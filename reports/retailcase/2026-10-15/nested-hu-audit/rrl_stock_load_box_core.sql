package body RRL_STOCK_LOAD_BOX_CORE as
 procedure compile_boxes(p_snapshot clob,p_context clob,p_operation varchar2,p_gross number,r in out nocopy json_array_t,p_boxes out json_array_t) is
  tree json_object_t:=json_object_t.parse(p_snapshot);ctx json_object_t:=json_object_t.parse(p_context);nodes json_array_t:=tree.get_array('nodes');links json_array_t:=tree.get_array('links');observed json_array_t:=json_array_t();
  type node_map is table of json_object_t index by varchar2(200);by_uid node_map;
  type parent_map is table of varchar2(200) index by varchar2(200);parent_by_child parent_map;
  type number_map is table of number index by varchar2(200);leaf_count number_map;lower_by_box number_map;weight_by_box number_map;
  node_json json_object_t;x json_object_t;o json_object_t;item json_object_t;uid_text varchar2(200);owner_uid varchar2(200);cursor_uid varchar2(200);key_uid varchar2(200);box_count number:=0;v_mass number;outer_tare number:=0;measured_total number:=0;v_ref varchar2(100);v_scan varchar2(200);v_version number;manual_no number:=0;uncovered_no number:=0;unknown_case_no number:=0;coverage_no number:=1;proof json_object_t;required_complete boolean:=false;
  function closest_box(p_uid varchar2) return varchar2 is current_uid varchar2(200):=p_uid;n number:=0;candidate json_object_t;
  begin
   loop
    n:=n+1;if n>17 then raise_application_error(-20886,'LOAD_BOX_PARENT_DEPTH_INVALID');end if;
    if not by_uid.exists(current_uid) then raise_application_error(-20886,'LOAD_BOX_PARENT_UNKNOWN');end if;
    candidate:=by_uid(current_uid);
    if(candidate.get_string('kind')='CONTAINER'and candidate.get_string('type')='BOX')or(candidate.get_string('kind')='CASE'and candidate.has('scale_qc'))then return current_uid;end if;
    if not parent_by_child.exists(current_uid) then return null;end if;current_uid:=parent_by_child(current_uid);
   end loop;
  end;
 begin
  p_boxes:=json_array_t();
  if ctx.has('require_complete_box_mass')then required_complete:=ctx.get_boolean('require_complete_box_mass');end if;
  if ctx.has('physical_boxes')and not ctx.get('physical_boxes').is_null then
   if not ctx.get('physical_boxes').is_array then raise_application_error(-20886,'LOAD_PHYSICAL_BOX_ARRAY_REQUIRED');end if;
   observed:=ctx.get_array('physical_boxes');manual_no:=observed.get_size;
  end if;
  if observed.get_size>200 or nodes.get_size>200 then raise_application_error(-20881,'LOAD_PHYSICAL_BOX_BOUND_200');end if;
  for i in 0..nodes.get_size-1 loop
   node_json:=treat(nodes.get(i)as json_object_t);uid_text:=node_json.get_string('uid');by_uid(uid_text):=node_json;
   if node_json.get_string('kind')='CASE'then
    if node_json.has('scale_qc')then
     for k in 0..manual_no-1 loop
      if treat(observed.get(k)as json_object_t).get_string('box_uid')=uid_text then raise_application_error(-20886,'LOAD_CASE_BOX_SERVER_SOURCE_REQUIRED');end if;
     end loop;
     proof:=node_json.get_object('scale_qc');o:=json_object_t();
     o.put('box_uid',uid_text);o.put('content_version',node_json.get_number('version'));o.put('scan_box',node_json.get_string('sscc'));
     o.put('gross_weight_kg',proof.get_string('gross_weight_kg'));o.put('origin','WAREHOUSE_SCALE_QC');o.put('measurement_ref',proof.get_string('measurement_ref'));
     o.put('case_task_id',proof.get_number('case_task_id'));o.put('final_scale_capture',proof.get_string('capture_key'));o.put('warehouse_qc_operation',proof.get_string('qc_operation_id'));
     o.put('tare_weight_kg',proof.get_string('tare_weight_kg'));o.put('net_weight_kg',proof.get_string('net_weight_kg'));o.put('device_mode',proof.get_string('device_mode'));
     o.put('composition_signature',proof.get_string('composition_signature'));o.put('signature_version',proof.get_number('signature_version'));o.put('measured_content_version',proof.get_number('measured_content_version'));
     observed.append(o);
    else unknown_case_no:=unknown_case_no+1;end if;
   end if;
  end loop;
  if observed.get_size=0 then return;end if;
  if observed.get_size>200 then raise_application_error(-20881,'LOAD_PHYSICAL_BOX_BOUND_200');end if;
  if unknown_case_no>0 and(required_complete or manual_no>0)then raise_application_error(-20886,'LOAD_BOX_MANIFEST_CASE_FLOW_REQUIRED');end if;
  for i in 0..links.get_size-1 loop x:=treat(links.get(i) as json_object_t);parent_by_child(x.get_string('child')):=x.get_string('parent');end loop;
  for i in 0..nodes.get_size-1 loop
   node_json:=treat(nodes.get(i) as json_object_t);uid_text:=node_json.get_string('uid');owner_uid:=closest_box(uid_text);
   if node_json.get_string('kind')='STOCK' then
    if owner_uid is null then
     uncovered_no:=uncovered_no+1;if required_complete or manual_no>0 then raise_application_error(-20886,'LOAD_PHYSICAL_BOX_COMPLETE_LEAF_COVERAGE_REQUIRED');end if;continue;end if;
    if not leaf_count.exists(owner_uid) then leaf_count(owner_uid):=0;lower_by_box(owner_uid):=0;end if;leaf_count(owner_uid):=leaf_count(owner_uid)+1;
   end if;
  end loop;
  for i in 0..nodes.get_size-1 loop
   node_json:=treat(nodes.get(i) as json_object_t);uid_text:=node_json.get_string('uid');owner_uid:=closest_box(uid_text);
   v_mass:=nvl(node_json.get_number('tare_weight_kg'),0);
   if node_json.get_string('kind')='STOCK' and node_json.get_string('base_uom')='KG' then v_mass:=v_mass+RRL_STOCK_MATH.quantity(node_json.get_string('quantity'));end if;
   if owner_uid is not null and leaf_count.exists(owner_uid) then lower_by_box(owner_uid):=lower_by_box(owner_uid)+v_mass;else outer_tare:=outer_tare+v_mass;end if;
  end loop;
  coverage_no:=case when uncovered_no=0 and unknown_case_no=0 then 1 else 0 end;
  key_uid:=leaf_count.first;while key_uid is not null loop
   box_count:=box_count+1;cursor_uid:=key_uid;
   while parent_by_child.exists(cursor_uid) loop cursor_uid:=parent_by_child(cursor_uid);if leaf_count.exists(cursor_uid) then raise_application_error(-20886,'LOAD_PHYSICAL_BOX_NESTED_COUNT_CONFLICT');end if;end loop;
   key_uid:=leaf_count.next(key_uid);
  end loop;
  if box_count!=observed.get_size then raise_application_error(-20886,'LOAD_PHYSICAL_BOX_EXACT_COVERAGE_REQUIRED');end if;
  for i in 0..observed.get_size-1 loop
   o:=treat(observed.get(i) as json_object_t);uid_text:=o.get_string('box_uid');
   if uid_text is null or not leaf_count.exists(uid_text) or weight_by_box.exists(uid_text) then raise_application_error(-20886,'LOAD_PHYSICAL_BOX_FOREIGN_OR_DUPLICATE');end if;
   node_json:=by_uid(uid_text);v_scan:=o.get_string('scan_box');v_ref:=o.get_string('measurement_ref');v_version:=o.get_number('content_version');
   if o.get_string('origin') is null or o.get_string('origin')not in('MANUAL_CONFIRMED','WAREHOUSE_SCALE_QC') or trim(v_ref) is null or v_version is null or v_version!=node_json.get_number('version') or v_scan is null
     or(v_scan!=uid_text and(node_json.get_string('sscc') is null or v_scan!=node_json.get_string('sscc'))) then raise_application_error(-20886,'LOAD_PHYSICAL_BOX_CURRENT_MEASUREMENT_SCAN_REQUIRED');end if;
   v_mass:=RRL_STOCK_MATH.quantity(o.get_string('gross_weight_kg'));if v_mass<lower_by_box(uid_text) then raise_application_error(-20886,'LOAD_BOX_GROSS_BELOW_NET_AND_TARE');end if;
   weight_by_box(uid_text):=v_mass;measured_total:=measured_total+v_mass;
   item:=json_object_t();item.put('box_uid',uid_text);item.put('content_version',v_version);item.put('gross_weight_kg',RRL_STOCK_PLAN_HELPER.decimal_text(v_mass));item.put('origin',o.get_string('origin'));item.put('coverage_complete',coverage_no);item.put('measurement_ref',v_ref);item.put('scan_box',v_scan);
   if node_json.get_string('kind')='CASE'then
    if o.get_string('origin')!='WAREHOUSE_SCALE_QC' or not node_json.has('scale_qc')then raise_application_error(-20886,'LOAD_CASE_BOX_CURRENT_QC_SOURCE_REQUIRED');end if;
    for field_no in 1..9 loop
     case field_no
      when 1 then item.put('case_task_id',o.get_number('case_task_id'));
      when 2 then item.put('final_scale_capture',o.get_string('final_scale_capture'));
      when 3 then item.put('warehouse_qc_operation',o.get_string('warehouse_qc_operation'));
      when 4 then item.put('tare_weight_kg',o.get_string('tare_weight_kg'));
      when 5 then item.put('net_weight_kg',o.get_string('net_weight_kg'));
      when 6 then item.put('device_mode',o.get_string('device_mode'));
      when 7 then item.put('composition_signature',o.get_string('composition_signature'));
      when 8 then item.put('signature_version',o.get_number('signature_version'));
      when 9 then item.put('measured_content_version',o.get_number('measured_content_version'));
     end case;
    end loop;
   elsif o.get_string('origin')!='MANUAL_CONFIRMED'then raise_application_error(-20886,'LOAD_ORDINARY_BOX_MANUAL_SOURCE_REQUIRED');end if;
   p_boxes.append(item);
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TT_LOAD_BOX_WEIGHT',p_operation||':'||uid_text);
  end loop;
  if p_gross<measured_total+outer_tare then raise_application_error(-20886,'LOAD_GROSS_BELOW_MEASURED_BOXES_AND_OUTER_TARE');end if;
 end;
 procedure assert_policy(p_destinations clob,p_boxes json_array_t) is v_count number;
 begin
  select count(*) into v_count from RRL_STORE_RECEIPT_POLICY policy
   where policy.RECEIPT_MODE='WEIGHT_PHOTO' and policy.STORE_ADDR in(select ADDR_TEXT from json_table(p_destinations,'$[*]' columns(ADDR_TEXT varchar2(255) path '$.address')));
  if v_count>0 and p_boxes.get_size=0 then raise_application_error(-20886,'LOAD_STORE_WEIGHT_REQUIRES_PHYSICAL_BOX_MASSES');end if;
  if v_count>0 then
   for i in 0..p_boxes.get_size-1 loop
    if nvl(treat(p_boxes.get(i)as json_object_t).get_number('coverage_complete'),1)!=1 then raise_application_error(-20886,'LOAD_STORE_WEIGHT_REQUIRES_COMPLETE_BOX_MASSES');end if;
   end loop;
  end if;
 end;

 procedure persist_boxes(p_operation varchar2,p_boxes json_array_t,p_actor varchar2)is
  x json_object_t;uid_value varchar2(200);version_value number;gross_value number;ref_value varchar2(100);scan_value varchar2(200);origin_value varchar2(20);
  case_value number;capture_value varchar2(64);qc_value varchar2(100);tare_value number;net_value number;mode_value varchar2(10);sig_value varchar2(64);sig_version number;measured_version number;coverage_value number;
 begin
  for i in 0..p_boxes.get_size-1 loop
   x:=treat(p_boxes.get(i)as json_object_t);uid_value:=x.get_string('box_uid');version_value:=x.get_number('content_version');
   gross_value:=RRL_STOCK_MATH.quantity(x.get_string('gross_weight_kg'));ref_value:=x.get_string('measurement_ref');scan_value:=x.get_string('scan_box');origin_value:=x.get_string('origin');
   case_value:=x.get_number('case_task_id');capture_value:=x.get_string('final_scale_capture');qc_value:=x.get_string('warehouse_qc_operation');
   tare_value:=null;net_value:=null;mode_value:=null;sig_value:=null;sig_version:=null;measured_version:=null;coverage_value:=nvl(x.get_number('coverage_complete'),1);
   if origin_value='WAREHOUSE_SCALE_QC'then
    tare_value:=RRL_STOCK_MATH.quantity(x.get_string('tare_weight_kg'));net_value:=RRL_STOCK_MATH.quantity(x.get_string('net_weight_kg'));
    mode_value:=x.get_string('device_mode');sig_value:=x.get_string('composition_signature');sig_version:=x.get_number('signature_version');measured_version:=x.get_number('measured_content_version');
   end if;
   insert into RRL_TT_LOAD_BOX_WEIGHT(LOAD_OPERATION_ID,BOX_UID,BOX_CONTENT_VERSION,GROSS_WEIGHT_KG,MEASUREMENT_ORIGIN,MEASUREMENT_REF,SCAN_IDENTIFIER,RECORDED_BY,
    CASE_BOX_TASK_ID,FINAL_SCALE_CAPTURE,WAREHOUSE_QC_OPERATION,TARE_WEIGHT_KG,NET_WEIGHT_KG,DEVICE_MODE,COMPOSITION_SIGNATURE,SIGNATURE_VERSION,MEASURED_CONTENT_VERSION,COVERAGE_COMPLETE)
   values(p_operation,uid_value,version_value,gross_value,origin_value,ref_value,scan_value,p_actor,
    case_value,capture_value,qc_value,tare_value,net_value,mode_value,sig_value,sig_version,measured_version,coverage_value);
  end loop;
 end;
end;
