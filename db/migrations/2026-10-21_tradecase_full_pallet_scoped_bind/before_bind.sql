create or replace package body RRL_STOCK_FULLPAL_BIND_CMD as
 function snapshot(p_task number,p_st varchar2,p_scan varchar2,p_expected number) return clob is
  t RRL_WAREHOUSE_TASK%rowtype;pt RRL_PICK_TASK%rowtype;m RRL_WAREHOUSE_TASK_STOCK_MOVE%rowtype;
  sr RRL_REMAINS%rowtype;st RRL_SBORKA_PALLETS%rowtype;ff RRL_CUSTOMER_ORDER_FULFILLMENT%rowtype;
  j json_object_t:=json_object_t();a json_array_t:=json_array_t();x json_object_t;qty number:=0;n number;
  v_pick number;v_article varchar2(160);v_ware number;v_block number;v_order number;v_hard number;
  v_policy number;v_base varchar2(20);v_num number;v_den number;v_scale number;v_rows number:=0;v_released number;
 begin
  if p_expected is null or p_expected<0 then raise_application_error(-20881,'EXPECTED_PHYSICAL_STOCK_VERSION_REQUIRED');end if;
  select * into t from RRL_WAREHOUSE_TASK where TASK_ID=p_task;
  if t.TASK_SOURCE!='WAVE' or t.TASK_TYPE!='PICKING_MOVE' or t.STATUS!='DONE' then raise_application_error(-20886,'FULLPAL_CONFIRMED_MOVE_REQUIRED');end if;
  select PICK_TASK_ID into v_pick from RRL_PICK_WAVE_TASK where PICK_WAVE_TASK_ID=t.SOURCE_TASK_ID and PICK_WAVE_ID=t.SOURCE_DOC_ID;
  select * into pt from RRL_PICK_TASK where PICK_TASK_ID=v_pick;
  if pt.TASK_TYPE!='FULL_PALLET' or pt.STATUS!='DONE' then raise_application_error(-20886,'FULLPAL_PICK_TASK_NOT_DONE');end if;
  select count(*) into v_released from RRL_PICK_WAVE where PICK_WAVE_ID=t.SOURCE_DOC_ID and PICK_RELEASED_AT is not null and STATUS in('LAUNCHED','DONE');
  if v_released!=1 then raise_application_error(-20886,'WAVE_PICK_RELEASE_REQUIRED');end if;
  select * into m from RRL_WAREHOUSE_TASK_STOCK_MOVE where TASK_ID=p_task;
  select count(*) into n from RRL_STOCK_OPERATION where OPERATION_ID=m.OPERATION_ID and STATE='APPLIED' and COMMAND_TYPE='TASK_COMPLETE';
  if n!=1 or m.TARGET_UID_PALLET is null or p_scan is null or p_scan!=m.TARGET_UID_PALLET then raise_application_error(-20886,'SCAN_CONFIRMED_PHYSICAL_PALLET');end if;
  select * into sr from RRL_REMAINS where UID_POLETA=m.TARGET_UID_PALLET and CELL=m.TO_CELL;
  if sr.STOCK_VERSION!=p_expected or sr.REMAIN!=m.BASE_QTY or sr.REMAIN<=0 or sr.BASE_UOM!=m.BASE_UOM then raise_application_error(-20886,'FULLPAL_PHYSICAL_VERSION_OR_COMPOSITION_CHANGED');end if;
  select p.ARTICUL,c.WARE_ID,greatest(nvl(c.BLOCKED_FOR_REMAINS,0),nvl(c.BLOCKED_FOR_POPOLNENIE,0)) into v_article,v_ware,v_block
   from RRL_PALLETS p join RRL_CELLS c on c.CELL=sr.CELL where p.UID_PALLET=sr.UID_POLETA;
  if v_block!=0 or v_article!=pt.ARTICUL then raise_application_error(-20886,'FULLPAL_LOCATION_OR_ARTICLE_CONFLICT');end if;
  select * into st from RRL_SBORKA_PALLETS where PALLET_UID=p_st;
  if st.WARE_ID is null or st.WARE_ID!=v_ware or nvl(st.CONDITION,0)>=2 or st.RETURN_SUPPLIER_ID is not null then raise_application_error(-20886,'FULLPAL_ST_STATE_OR_WAREHOUSE_CONFLICT');end if;
  select * into ff from RRL_CUSTOMER_ORDER_FULFILLMENT where LEGACY_SBORKA_PALLET_ID=st.ID and PALLET_UID=p_st and CUSTOMER_ORDER_ID=pt.CUSTOMER_ORDER_ID;
  if ff.STATUS not in('PLANNED','PICKED') or ff.STATUS is null or ff.PICKED_CASE_TASK_ID is not null then raise_application_error(-20886,'FULLPAL_FULFILLMENT_STATE_CONFLICT');end if;
  if ff.PICKED_PALLET_UID is not null and (ff.PICKED_PALLET_UID!=p_scan or ff.PICKED_WAREHOUSE_TASK_ID!=p_task or ff.PICKED_STOCK_VERSION!=p_expected) then raise_application_error(-20886,'FULLPAL_ST_ALREADY_BOUND');end if;
  select count(*) into n from RRL_CUSTOMER_ORDER_FULFILLMENT where PICKED_PALLET_UID=p_scan and FULFILLMENT_ID!=ff.FULFILLMENT_ID and STATUS in('PICKED','SHIPPED');
  if n>0 then raise_application_error(-20886,'FULLPAL_PHYSICAL_PALLET_ALREADY_BOUND');end if;
  select nvl(sum(BASE_QTY),0) into v_hard from RRL_STOCK_RESERVATION where UID_PALLET=p_scan and CELL=sr.CELL
   and CUSTOMER_ORDER_ID=pt.CUSTOMER_ORDER_ID and SOURCE_LINE_ID=v_pick and SOURCE_DOC_TYPE='PICK_WAVE' and SOURCE_DOC_ID=t.SOURCE_DOC_ID
   and RESERVATION_KIND='HARD' and RESERVATION_DOMAIN='PICKING' and STATUS in('ACTIVE','ALLOCATED','PICKING') and BASE_UOM=sr.BASE_UOM;
  if v_hard!=sr.REMAIN or v_hard!=sr.HARD_RESERVED_BASE then raise_application_error(-20886,'FULLPAL_WHOLE_OWNED_RESERVATION_REQUIRED');end if;
  for r in(select * from RRL_SBORKA_PALLET_ROWS where PALLET_UID=p_st order by ID fetch first 201 rows only) loop
   v_rows:=v_rows+1;if v_rows>200 then raise_application_error(-20881,'FULLPAL_ST_ROW_BOUND');end if;
   if r.ARTICUL!=v_article or r.QUANTITY<=0 or r.EI is null then raise_application_error(-20886,'FULLPAL_ST_COMPOSITION_MISMATCH');end if;
   select max(POLICY_VERSION) into v_policy from RRL_STOCK_UOM_CONVERSION where ARTICUL=r.ARTICUL and INPUT_UOM=r.EI;
   select BASE_UOM,NUMERATOR,DENOMINATOR,BASE_SCALE into v_base,v_num,v_den,v_scale from RRL_STOCK_UOM_CONVERSION where ARTICUL=r.ARTICUL and INPUT_UOM=r.EI and POLICY_VERSION=v_policy;
   if v_base!=sr.BASE_UOM then raise_application_error(-20886,'FULLPAL_ST_BASE_UOM_MISMATCH');end if;
   qty:=qty+RRL_STOCK_MATH.convert_exact(RRL_STOCK_PLAN_HELPER.decimal_text(r.QUANTITY),v_num,v_den,v_scale);
   x:=json_object_t();x.put('row_id',r.ID);x.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(r.QUANTITY));x.put('input_uom',r.EI);x.put('policy_version',v_policy);a.append(x);
  end loop;
  if v_rows=0 or qty!=sr.REMAIN then raise_application_error(-20886,'FULLPAL_ST_COMPOSITION_MISMATCH');end if;
  j.put('task_id',p_task);j.put('wave_id',t.SOURCE_DOC_ID);j.put('pick_task_id',v_pick);j.put('source_operation_id',m.OPERATION_ID);
  j.put('shipment_id',st.ID);j.put('shipment_identifier',p_st);j.put('fulfillment_id',ff.FULFILLMENT_ID);j.put('fulfillment_status',ff.STATUS);
  j.put('physical_uid',p_scan);j.put('cell',sr.CELL);j.put('stock_version',sr.STOCK_VERSION);
  j.put('article',v_article);j.put('base_uom',sr.BASE_UOM);j.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(sr.REMAIN));j.put('rows',a);
  return j.to_clob;
 exception when no_data_found then raise_application_error(-20887,'FULLPAL_BIND_IDENTITY_MISSING');
  when too_many_rows then raise_application_error(-20887,'FULLPAL_BIND_IDENTITY_AMBIGUOUS');
 end;
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');v json_object_t;
  s clob;a json_array_t;x json_object_t;f json_array_t:=json_array_t();r json_array_t:=json_array_t();
 begin
  s:=snapshot(d.get_object('source').get_number('task_id'),m.get_string('shipment_identifier'),m.get_string('scanned_pallet'),m.get_number('expected_stock_version'));
  v:=json_object_t.parse(s);
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');
  RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_WAVE',RRL_STOCK_PLAN_HELPER.decimal_text(v.get_number('wave_id')));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_WAREHOUSE_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(v.get_number('task_id')));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(v.get_number('pick_task_id')));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_SBORKA_PALLETS',RRL_STOCK_PLAN_HELPER.decimal_text(v.get_number('shipment_id')));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_CUSTOMER_ORDER_FULFILLMENT',RRL_STOCK_PLAN_HELPER.decimal_text(v.get_number('fulfillment_id')));
  RRL_STOCK_PLAN_HELPER.stock_closure(f,r,v.get_string('physical_uid'),v.get_string('article'),v.get_string('cell'),null);
  a:=v.get_array('rows');for i in 0..a.get_size-1 loop
   x:=treat(a.get(i) as json_object_t);RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_SBORKA_PALLET_ROWS',RRL_STOCK_PLAN_HELPER.decimal_text(x.get_number('row_id')));
  end loop;
  v.put('snapshot_signature',rawtohex(sys.dbms_crypto.hash(s,sys.dbms_crypto.hash_sh256)));
  p_domain:=v.to_clob;p_policies:=f.to_clob;p_resources:=r.to_clob;
 end;
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob) is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');v json_object_t;j json_object_t;
  plan clob;s clob;op varchar2(100);fid number;tid number;stockver number;srcop varchar2(100);puid varchar2(150);base varchar2(20);
  quantity number;comp clob;a json_array_t:=json_array_t();x json_object_t:=json_object_t();
 begin
  if RRL_HAS_WRIGHT(p_actor,'warehouse_task_execute')!=1 then raise_application_error(-20882,'FULLPAL_BIND_FORBIDDEN');end if;
  op:=d.get_string('operation_id');select RESOLVED_PLAN_JSON into plan from RRL_STOCK_OPERATION where OPERATION_ID=op;
  v:=json_object_t.parse(plan).get_object('domain');tid:=v.get_number('task_id');
  s:=snapshot(tid,m.get_string('shipment_identifier'),m.get_string('scanned_pallet'),m.get_number('expected_stock_version'));
  if rawtohex(sys.dbms_crypto.hash(s,sys.dbms_crypto.hash_sh256))!=v.get_string('snapshot_signature') then raise_application_error(-20890,'CLOSURE_CHANGED: whole pallet shipment binding');end if;
  fid:=v.get_number('fulfillment_id');stockver:=v.get_number('stock_version');srcop:=v.get_string('source_operation_id');puid:=v.get_string('physical_uid');
  quantity:=RRL_STOCK_MATH.quantity(v.get_string('quantity'));base:=v.get_string('base_uom');
  x.put('article',v.get_string('article'));x.put('base_uom',base);x.put('quantity',v.get_string('quantity'));a.append(x);comp:=a.to_clob;
  update RRL_CUSTOMER_ORDER_FULFILLMENT set STATUS='PICKED',FACT_QTY=quantity,FACT_UOM=base,FACT_COMPOSITION_JSON=comp,
   PICKED_WAREHOUSE_TASK_ID=tid,PICKED_OPERATION_ID=srcop,PICKED_PALLET_UID=puid,PICKED_STOCK_VERSION=stockver,
   PICKED_AT=systimestamp,PICKED_BY=p_actor,UPDATED_AT=sysdate,UPDATED_BY=p_actor where FULFILLMENT_ID=fid;
  j:=json_object_t();j.put('operation_id',op);j.put('fulfillment_id',fid);j.put('shipment_identifier',v.get_string('shipment_identifier'));
  j.put('pallet_identifier',puid);j.put('status','PICKED');j.put('quantity',v.get_string('quantity'));j.put('base_uom',base);
  j.put('physical_composition',a);j.put('warehouse_task_id',tid);j.put('physical_operation_id',srcop);p_result:=j.to_clob;
 end;
end;
/
