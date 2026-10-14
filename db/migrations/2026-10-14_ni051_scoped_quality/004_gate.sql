create or replace package body RRL_STOCK_QC_GATE as
 function signature_version_for_plan(p_domain clob)return number is
  d json_object_t:=json_object_t.parse(p_domain);task_no number:=d.get_number('case_task');n number;
 begin
  if task_no is null then return 2;end if;
  select case when p.FINAL_WEIGHT_REQUIRED=1 and upper(p.LOAD_UNIT_CLASS)='CONTAINER'then 3 else 2 end into n
   from RRL_CASE_PICK_TASK c join RRL_PALLET_TYPE p on p.PALLET_TYPE_ID=c.PALLET_TYPE_ID where c.CASE_PICK_TASK_ID=task_no;
  return n;
 end;
 function signature_for_plan(p_domain clob) return varchar2 is
  d json_object_t:=json_object_t.parse(p_domain);j json_object_t:=json_object_t();a json_array_t:=json_array_t();legs json_array_t:=d.get_array('legs');
  l json_object_t;x json_object_t;units json_array_t;links json_array_t;profiles json_array_t;codes json_array_t;c json_object_t;u json_object_t;
  v_uid varchar2(150);v_ware number:=d.get_number('warehouse');v_article varchar2(160);v_case number:=d.get_number('case_task');v_codes number:=0;v_units number:=0;v_links number:=0;v_signature_version number;
 begin
  v_signature_version:=signature_version_for_plan(p_domain);j.put('version',v_signature_version);
  if v_signature_version=3 then
   for z in(select SSCC,PALLET_TYPE_ID from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=v_case)loop j.put('case_identifier',z.SSCC);j.put('case_type_id',z.PALLET_TYPE_ID);end loop;
  end if;j.put('document_id',d.get_number('document_id'));j.put('identifier',d.get_string('pallet_identifier'));
  j.put('warehouse',d.get_number('warehouse'));j.put('customer_order',d.get_number('customer_order_id'));
  declare scoped_policy json_object_t:=json_object_t.parse(RRL_QC_SCOPE_READ.policy_json(p_domain));begin
   if scoped_policy.has('policy_stamp')then j.put('scope_policy_stamp',scoped_policy.get_string('policy_stamp'));end if;end;
  j.put('return_supplier',d.get_string('return_supplier_id'));j.put('rows',d.get_string('rows_signature'));
  for i in 0..legs.get_size-1 loop
   l:=treat(legs.get(i) as json_object_t);v_uid:=l.get_string('uid');x:=json_object_t();
   x.put('row',l.get_number('row_id'));x.put('uid',v_uid);x.put('quantity',l.get_string('quantity'));
   x.put('base_uom',l.get_string('base_uom'));x.put('uom_policy',l.get_number('uom_version'));
   x.put('owner_type',l.get_string('owner_type'));x.put('owner_id',l.get_number('owner_id'));x.put('pick_task',l.get_number('pick_task_id'));
   for p in(select ARTICUL,STOCK_COMPOSITION_VERSION,EXPIRY_DATE,PRODUCED_DATE,PROD_BATCH_ID,STOCK_ORIGIN_UID,SSCC,STOCK_BOX_FACTOR,STOCK_PACK_BASE_UOM
    from RRL_PALLETS where UID_PALLET=v_uid) loop
    for sku in(select BARCODE_SHT,BARCODE_KOR from RRL_ARTICULS where ACTICUL=p.ARTICUL) loop x.put('item_barcode',sku.BARCODE_SHT);x.put('box_barcode',sku.BARCODE_KOR);end loop;
    x.put('article',p.ARTICUL);x.put('stock_composition_version',p.STOCK_COMPOSITION_VERSION);x.put('expiry',to_char(p.EXPIRY_DATE,'YYYY-MM-DD HH24:MI:SS'));
    x.put('produced',to_char(p.PRODUCED_DATE,'YYYY-MM-DD HH24:MI:SS'));x.put('batch',p.PROD_BATCH_ID);x.put('origin',p.STOCK_ORIGIN_UID);
    x.put('sscc',p.SSCC);x.put('box_factor',p.STOCK_BOX_FACTOR);x.put('pack_uom',p.STOCK_PACK_BASE_UOM);
    profiles:=json_array_t();
    for z in(select POLICY_VERSION,MARKING_REQUIRED from RRL_SKU_RECEIPT_POLICY where ARTICUL=p.ARTICUL order by POLICY_VERSION) loop
     u:=json_object_t();u.put('policy',z.POLICY_VERSION);u.put('marking',z.MARKING_REQUIRED);profiles.append(u);
    end loop;
    for z in(select SYSTEM_CODE,PROFILE_CODE,PROFILE_VERSION,SCAN_MODE from RRL_SKU_RECEIPT_PROFILE where ARTICUL=p.ARTICUL order by SYSTEM_CODE,PROFILE_CODE) loop
     u:=json_object_t();u.put('system',z.SYSTEM_CODE);u.put('profile',z.PROFILE_CODE);u.put('version',z.PROFILE_VERSION);u.put('scan_mode',z.SCAN_MODE);profiles.append(u);
    end loop;x.put('profiles',profiles);
    for z in(select CRPT_REQUIRED from RRL_FINISHED_GOODS_SKU where ARTICUL=p.ARTICUL) loop x.put('legacy_crpt_required',z.CRPT_REQUIRED);end loop;
   end loop;
   v_article:=l.get_string('article');
   for z in(select QC_BASE_WEIGHT_KG,QC_BOX_WEIGHT_KG,QC_WEIGHT_VERSION,QC_WEIGHT_BASE_UOM from RRL_RECEIPT_SKU_RULE
    where WARE_ID=v_ware and ARTICUL=v_article) loop
    x.put('weight_base_uom',z.QC_WEIGHT_BASE_UOM);x.put('weight_version',z.QC_WEIGHT_VERSION);x.put('base_weight_kg',z.QC_BASE_WEIGHT_KG);x.put('box_weight_kg',z.QC_BOX_WEIGHT_KG);
   end loop;
   units:=json_array_t();
   for z in(select UID_PALLET,PHYSICAL_UNIT_KEY,UNIT_ID,POLICY_VERSION,BASE_QTY,BASE_UOM from RRL_WMS_RECEIPT_UNIT
    where CURRENT_UID=v_uid and STOCK_STATUS='AVAILABLE' order by PHYSICAL_UNIT_KEY fetch first 10001 rows only) loop
    v_units:=v_units+1;if v_units>10000 then raise_application_error(-20881,'QUALITY_UNIT_BOUND');end if;
    u:=json_object_t();u.put('key',z.PHYSICAL_UNIT_KEY);u.put('id',z.UNIT_ID);u.put('policy',z.POLICY_VERSION);u.put('quantity',z.BASE_QTY);u.put('uom',z.BASE_UOM);units.append(u);
   end loop;x.put('units',units);codes:=json_array_t();
   for code in(select u.PHYSICAL_UNIT_KEY,c.SYSTEM_CODE,c.CODE_HASH,c.PROFILES_JSON from RRL_WMS_RECEIPT_UNIT u
    join RRL_WMS_RECEIPT_CODE c on c.UID_PALLET=u.UID_PALLET and c.UNIT_ID=u.UNIT_ID
    where u.CURRENT_UID=v_uid and u.STOCK_STATUS='AVAILABLE' order by u.PHYSICAL_UNIT_KEY,c.SYSTEM_CODE,c.CODE_HASH fetch first 20001 rows only) loop
    v_codes:=v_codes+1;if v_codes>20000 then raise_application_error(-20881,'QUALITY_CODE_COMPOSITION_BOUND');end if;
    c:=json_object_t();c.put('key',code.PHYSICAL_UNIT_KEY);c.put('system',code.SYSTEM_CODE);c.put('hash',code.CODE_HASH);c.put('profiles',json_array_t.parse(code.PROFILES_JSON));codes.append(c);
   end loop;x.put('codes',codes);links:=json_array_t();
   if v_signature_version=2 then
   for z in(select HU_LINK_ID,PARENT_UID,LINK_VERSION,level DEPTH,connect_by_iscycle CYCLIC from RRL_WMS_HU_LINK
    start with (CHILD_PALLET_UID=v_uid or CHILD_CASE_TASK_ID=v_case) and ACTIVE_FLAG=1
    connect by nocycle prior PARENT_UID=CHILD_PALLET_UID and ACTIVE_FLAG=1 order siblings by HU_LINK_ID) loop
    v_links:=v_links+1;if v_links>3200 or z.DEPTH>16 or z.CYCLIC=1 then raise_application_error(-20881,'QUALITY_HIERARCHY_BOUND');end if;
    u:=json_object_t();u.put('id',z.HU_LINK_ID);u.put('parent',z.PARENT_UID);u.put('version',z.LINK_VERSION);links.append(u);
   end loop;
   end if;x.put('links',links);
   for z in(select CASE_PICK_TASK_ID,CREATED_OPERATION from RRL_CASE_CARRIER_LOT where LOT_UID=v_uid) loop
    x.put('case',z.CASE_PICK_TASK_ID);x.put('case_membership',z.CREATED_OPERATION);
   end loop;a.append(x);
  end loop;
  j.put('allocations',a);return rawtohex(sys.dbms_crypto.hash(j.to_clob,sys.dbms_crypto.hash_sh256));
 end;
 procedure assert_approved(p_domain clob) is
  d json_object_t:=json_object_t.parse(p_domain);v_id number:=d.get_number('document_id');v_mode varchar2(10);v_independent number;
  v_scan number;v_weight number;v_mark_proved number;v_signature varchar2(64);v_scan_sig varchar2(64);v_weight_sig varchar2(64);
  v_scan_op varchar2(100);v_weight_op varchar2(100);v_actor varchar2(100);v_method varchar2(20);v_expected number;v_tolerance number;v_current number;v_current_tolerance number;
  v_full_scan number;v_item_proved number;v_marked number;scan_ok boolean:=false;weight_ok boolean:=false;
 begin
  RRL_STOCK_QC_POLICY.settings_for_plan(p_domain,v_mode,v_independent);v_marked:=RRL_STOCK_QC_MARK.required_for_plan(p_domain);v_full_scan:=RRL_STOCK_QC_POLICY.full_scan_required(p_domain);
  if v_mode='NONE' and v_marked=0 and v_full_scan=0 then return;end if;
  select nvl(PROOVED_BY_SCAN,0),nvl(PROOVED,0),SCAN_MARK_PROVED,SCAN_CONTENT_SIGNATURE,WEIGHT_CONTENT_SIGNATURE,
   SCAN_QC_OPERATION_ID,WEIGHT_QC_OPERATION_ID,WEIGHT_QC_METHOD,WEIGHT_QC_EXPECTED,WEIGHT_QC_TOLERANCE,SCAN_ITEM_PROVED
   into v_scan,v_weight,v_mark_proved,v_scan_sig,v_weight_sig,v_scan_op,v_weight_op,v_method,v_expected,v_tolerance,v_item_proved from RRL_SBORKA_PALLETS where ID=v_id;
  v_signature:=signature_for_plan(p_domain);
  if v_scan=1 and v_scan_sig=v_signature then
   if v_independent=0 then scan_ok:=true;else
    begin select ACTOR into v_actor from RRL_STOCK_OPERATION where OPERATION_ID=v_scan_op and STATE='APPLIED';
     scan_ok:=RRL_STOCK_QC_POLICY.controller_allowed(p_domain,v_actor)=1;
    exception when no_data_found then scan_ok:=false;end;
   end if;
  end if;
  if v_weight=1 and v_weight_sig=v_signature and v_method in('WEIGHT','WEIGHT2') then
   RRL_STOCK_QC_WEIGHT.calculate(p_domain,v_current,v_current_tolerance);
   if v_current=v_expected and v_current_tolerance=v_tolerance then
    if v_independent=0 then weight_ok:=true;else
     begin select ACTOR into v_actor from RRL_STOCK_OPERATION where OPERATION_ID=v_weight_op and STATE='APPLIED';
      weight_ok:=RRL_STOCK_QC_POLICY.controller_allowed(p_domain,v_actor)=1;
     exception when no_data_found then weight_ok:=false;end;
    end if;
   end if;
  end if;
  -- The currently executing QC operation is still POSTING, not APPLIED. Its authenticated context is authoritative.
  if sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')=v_scan_op and v_scan=1 and v_scan_sig=v_signature then
   select ACTOR into v_actor from RRL_STOCK_OPERATION where OPERATION_ID=v_scan_op;scan_ok:=RRL_STOCK_QC_POLICY.controller_allowed(p_domain,v_actor)=1;end if;
  if sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')=v_weight_op and v_weight=1 and v_weight_sig=v_signature then
   select ACTOR into v_actor from RRL_STOCK_OPERATION where OPERATION_ID=v_weight_op;weight_ok:=RRL_STOCK_QC_POLICY.controller_allowed(p_domain,v_actor)=1;end if;
  if weight_ok and RRL_WH_FINAL_SCALE_ADMISSION.approved(p_domain,v_weight_op)!=1 then weight_ok:=false;end if;
  if v_mode in('ANY','WEIGHT','BOTH') and json_object_t.parse(RRL_QC_SCOPE_READ.exemption_json(p_domain)).get_boolean('eligible')then weight_ok:=true;end if;
  if v_marked=1 and (not scan_ok or v_mark_proved!=1) then raise_application_error(-20886,'SHIPMENT_CURRENT_UNIQUE_MARK_CONTROL_REQUIRED');end if;
  if v_full_scan=1 and (not scan_ok or v_item_proved!=1) then raise_application_error(-20886,'SHIPMENT_FULL_COMPOSITION_SCAN_REQUIRED');end if;
  if v_mode='NONE' or(v_mode='ANY' and(scan_ok or weight_ok)) or(v_mode='SCAN' and scan_ok)
   or(v_mode='WEIGHT' and weight_ok) or(v_mode='BOTH' and scan_ok and weight_ok) then return;end if;
  raise_application_error(-20886,'SHIPMENT_CURRENT_COMPOSITION_QUALITY_REQUIRED:'||v_mode);
 end;
 function status_json(p_identifier varchar2) return clob is
  j json_object_t:=json_object_t();d json_object_t:=json_object_t();s json_object_t:=json_object_t();
  domain clob;policies clob;resources clob;v_signature varchar2(64);v_ware number;v_required number;v_id number;v_scan varchar2(64);v_weight varchar2(64);v_expected number;v_tolerance number;profiles json_array_t:=json_array_t();profile json_object_t;v_unit_count number;v_legs clob;v_bucket number;v_percent number;v_selected number;v_rescan number;v_mode varchar2(10);v_independent number;
 begin
  select p.ID,p.WARE_ID,nvl(w.BLOCK_IF_NO_PROOVE,0),p.SCAN_CONTENT_SIGNATURE,p.WEIGHT_CONTENT_SIGNATURE
   into v_id,v_ware,v_required,v_scan,v_weight from RRL_SBORKA_PALLETS p join RRL_WARES w on w.ID=p.WARE_ID where p.PALLET_UID=p_identifier;
  j.put('shipment_identifier',p_identifier);j.put('document_id',v_id);RRL_STOCK_QC_POLICY.settings(v_ware,v_mode,v_independent);j.put('required',v_mode!='NONE');j.put('control_mode',v_mode);j.put('independent_controller_required',v_independent=1);j.put('ready',false);
  d.put('command_type','SHIP_PALLET');s.put('pallet_identifier',p_identifier);d.put('source',s);
  begin
   RRL_STOCK_SHIPPING_CORE.compile_shipment(d.to_clob,'READ.QC:'||RRL_STOCK_PLAN_HELPER.decimal_text(v_id),policies,resources,domain,true);
   RRL_STOCK_QC_POLICY.settings_for_plan(domain,v_mode,v_independent);
   declare dom json_object_t:=json_object_t.parse(domain);task_no number;required_flag number:=0;begin
    task_no:=dom.get_number('case_task');j.put('case_task_id',task_no);j.put('case_content_version',dom.get_number('case_version'));j.put('composition_signature_version',signature_version_for_plan(domain));
    if task_no is not null then select case when p.FINAL_WEIGHT_REQUIRED=1 and upper(p.LOAD_UNIT_CLASS)='CONTAINER'then 1 else 0 end into required_flag
     from RRL_CASE_PICK_TASK c join RRL_PALLET_TYPE p on p.PALLET_TYPE_ID=c.PALLET_TYPE_ID where c.CASE_PICK_TASK_ID=task_no;end if;
    j.put('final_scale_required',required_flag=1);
   end;
   j.put('required',v_mode!='NONE');j.put('control_mode',v_mode);j.put('independent_controller_required',v_independent=1);
   j.put('quality_policy',json_object_t.parse(RRL_QC_SCOPE_READ.policy_json(domain)));
   j.put('weight_exemption',json_object_t.parse(RRL_QC_SCOPE_READ.exemption_json(domain)));
   j.put('unique_mark_control_required',RRL_STOCK_QC_MARK.required_for_plan(domain)=1);
   for z in(select distinct r.SYSTEM_CODE,r.PROFILE_CODE from RRL_SKU_RECEIPT_PROFILE r
    join RRL_SBORKA_PALLET_ROWS sr on sr.ARTICUL=r.ARTICUL where sr.PALLET_UID=p_identifier order by r.SYSTEM_CODE,r.PROFILE_CODE fetch first 51 rows only) loop
    if profiles.get_size>=50 then raise_application_error(-20881,'QUALITY_MARK_PROFILE_BOUND');end if;
    profile:=json_object_t();profile.put('system_code',z.SYSTEM_CODE);profile.put('profile_code',z.PROFILE_CODE);profiles.append(profile);
   end loop;j.put('mark_profiles',profiles);
   declare v_case number:=json_object_t.parse(domain).get_number('case_task');v_case_status varchar2(40);begin
    if v_case is not null then select STATUS into v_case_status from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=v_case;j.put('case_task_id',v_case);j.put('case_status',v_case_status);end if;
   end;
   v_legs:=json_object_t.parse(domain).get_array('legs').to_clob;
   select count(distinct u.PHYSICAL_UNIT_KEY) into v_unit_count from
    json_table(v_legs,'$[*]' columns(U varchar2(150) path '$.uid',C varchar2(60) path '$.cell'))l
    join RRL_WMS_RECEIPT_UNIT u on u.CURRENT_UID=l.U and u.CURRENT_CELL=l.C and u.STOCK_STATUS='AVAILABLE';
   j.put('physical_unit_count',v_unit_count);
   v_signature:=signature_for_plan(domain);j.put('composition_signature',v_signature);
   RRL_STOCK_QC_POLICY.sampling(domain,v_bucket,v_percent,v_selected,v_rescan);
   j.put('sample_percent',v_percent);j.put('sample_selected',v_selected=1);j.put('rescan_required',v_rescan=1);
   j.put('control_plan_required',v_bucket is null and v_percent>0);j.put('full_scan_required',v_mode in('SCAN','BOTH') or v_selected=1 or v_rescan=1);
   j.put('scan_matches',v_scan=v_signature);j.put('weight_matches',v_weight=v_signature);
   begin
    RRL_STOCK_QC_WEIGHT.calculate(domain,v_expected,v_tolerance);
    j.put('expected_weight_kg',RRL_STOCK_PLAN_HELPER.decimal_text(v_expected));
    j.put('tolerance_kg',RRL_STOCK_PLAN_HELPER.decimal_text(v_tolerance));
   exception when others then j.put('weight_policy_reason',substr(sqlerrm,1,1000));end;
   assert_approved(domain);j.put('ready',true);
  exception when others then j.put('reason',substr(sqlerrm,1,1000));end;
  return j.to_clob;
 end;
end;
/
