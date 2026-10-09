declare n number;begin select count(*) into n from RRL_STOCK_OPERATION; if n>0 then raise_application_error(-20808,'POSTED_OPERATIONS_PREVENT_CODE_ROLLBACK');end if;end;
/
create or replace package RRL_STOCK_RECEIPT_CORE authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure execute_receipt(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_STOCK_PALLET_UOM authid definer
 accessible by(package RRL_STOCK_INVENTORY_CMD,package RRL_STOCK_INTERNAL_CMD,package RRL_STOCK_TASK_PLAN,package RRL_STOCK_TASK_CORE) as
 procedure resolve_quantity(p_uid varchar2,p_input varchar2,p_quantity varchar2,
  p_base out varchar2,p_quantity_base out number,p_version out number,p_signature out varchar2);
end;
/

create or replace package RRL_STOCK_PLAN_HELPER authid definer as
 procedure fence(p_plan in out nocopy json_array_t,p_kind varchar2,p_id varchar2,p_mode number default 4);
 procedure anchor(p_plan in out nocopy json_array_t,p_rank number,p_kind varchar2,p_a varchar2,p_b varchar2 default null);
 procedure row_key(p_plan in out nocopy json_array_t,p_table varchar2,p_id varchar2);
 procedure stock_closure(p_policies in out nocopy json_array_t,p_resources in out nocopy json_array_t,
  p_uid varchar2,p_article varchar2,p_from varchar2,p_to varchar2);
 function decimal_text(p_value number) return varchar2;
end;
/

create or replace package RRL_STOCK_WAVE_LAUNCH_CMD authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package body RRL_STOCK_RECEIPT_CORE as
 procedure execute_receipt(p_request clob,p_actor varchar2,p_result out clob) is
  d json_object_t:=json_object_t.parse(p_request);h json_object_t;m json_object_t;o RRL_SAP_SUPPLY_ORDER%rowtype;
  v_plan clob;v_result clob;v_response json_object_t;v_policy number;v_qty number;v_planned number;v_done number;v_n number;
  v_base varchar2(20);v_unit varchar2(20);v_article varchar2(160);v_uom_version number;v_num number;v_den number;v_scale number;
  v_uid varchar2(200);v_cell varchar2(60);v_event number;v_task number;v_expiry date;v_header number;
 begin
  if RRL_HAS_WRIGHT(p_actor,'warehouse_receipt_confirm')!=1 then raise_application_error(-20882,'RECEIPT_FORBIDDEN');end if;
  select RESOLVED_PLAN_JSON into v_plan from RRL_STOCK_OPERATION where OPERATION_ID=d.get_string('operation_id');
  h:=json_object_t.parse(v_plan).get_object('domain');m:=d.get_object('metadata');
  RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),4);
  select * into o from RRL_SAP_SUPPLY_ORDER where ORDER_ID=h.get_string('source_order_id') for update;
  if o.REVISION!=h.get_number('order_revision') or o.NAKLAD_ID!=h.get_number('naklad_id')
   or o.WARE_ID!=h.get_number('warehouse_id') or o.RECEIVE_CELL!=h.get_string('receive_cell') then
   raise_application_error(-20890,'CLOSURE_CHANGED: SAP receipt order');end if;
  select CONDITION into v_header from RRL_PRIHOD_NAKLAD where ID=o.NAKLAD_ID for update;
  if nvl(v_header,0)!=0 then raise_application_error(-20886,'RECEIPT_DOCUMENT_CLOSED');end if;
  select ARTICUL,PLANNED_QTY,BASE_UOM into v_article,v_planned,v_unit from RRL_SAP_SUPPLY_LINE
   where ORDER_ID=o.ORDER_ID and LINE_NUMBER=h.get_string('line_number');
  if v_article!=h.get_string('article') or v_unit!=h.get_string('input_uom') then raise_application_error(-20890,'CLOSURE_CHANGED: SAP receipt line');end if;
  select max(POLICY_VERSION) into v_uom_version from RRL_STOCK_UOM_CONVERSION where ARTICUL=v_article and INPUT_UOM=v_unit;
  select BASE_UOM,NUMERATOR,DENOMINATOR,BASE_SCALE into v_base,v_num,v_den,v_scale
   from RRL_STOCK_UOM_CONVERSION where ARTICUL=v_article and INPUT_UOM=v_unit and POLICY_VERSION=v_uom_version;
  v_qty:=RRL_STOCK_MATH.convert_exact(m.get_string('quantity'),v_num,v_den,v_scale);
  v_planned:=RRL_STOCK_MATH.convert_exact(RRL_STOCK_PLAN_HELPER.decimal_text(v_planned),v_num,v_den,v_scale);
  if h.get_number('uom_version')!=v_uom_version or h.get_string('base_uom')!=v_base or
   RRL_STOCK_MATH.quantity(h.get_string('base_quantity'))!=v_qty then raise_application_error(-20890,'CLOSURE_CHANGED: receipt UOM');end if;
  select count(*) into v_n from RRL_SAP_PALLET_RECEIPT where ORDER_ID=o.ORDER_ID and LINE_NUMBER=h.get_string('line_number')
   and (POSTED_BASE_QTY is null or STOCK_BASE_UOM is null or STOCK_BASE_UOM!=v_base);
  if v_n>0 then raise_application_error(-20884,'LEGACY_RECEIPT_BASELINE_REQUIRED');end if;
  select nvl(sum(POSTED_BASE_QTY),0) into v_done from RRL_SAP_PALLET_RECEIPT where ORDER_ID=o.ORDER_ID and LINE_NUMBER=h.get_string('line_number');
  if v_done+v_qty>v_planned then raise_application_error(-20886,'RECEIPT_OVER_SUPPLY');end if;
  select POLICY_VERSION into v_policy from RRL_SKU_RECEIPT_POLICY where ARTICUL=v_article;
  if v_policy!=h.get_number('marking_policy_version') then raise_application_error(-20890,'CLOSURE_CHANGED: marking policy');end if;
  v_uid:=h.get_string('uid');v_cell:=o.RECEIVE_CELL;v_task:=h.get_number('task_id');
  select count(*) into v_n from RRL_PALLETS where UID_PALLET=v_uid and ARTICUL=v_article and PRIHOD_NAKLAD_ID=o.NAKLAD_ID
   and UNIT_COUNT=v_qty and EXPIRY_DATE=to_date(m.get_string('expiry_date'),'YYYY-MM-DD');
  if v_n!=1 then raise_application_error(-20884,'RECEIPT_STAGING_PALLET_CONFLICT');end if;
  select count(*) into v_n from RRL_WAREHOUSE_TASK where TASK_ID=v_task and UID_PALLET=v_uid and STATUS='PLANNED'
   and FROM_CELL=v_cell and TO_CELL=h.get_object('placement').get_string('cell');
  if v_n!=1 then raise_application_error(-20884,'RECEIPT_STAGING_TASK_CONFLICT');end if;
  select count(*) into v_n from RRL_REMAINS where UID_POLETA=v_uid;
  if v_n>0 then raise_application_error(-20886,'RECEIPT_STOCK_ALREADY_EXISTS');end if;
  RRL_STOCK_LOCATION_CORE.assert_receiving(v_cell,o.WARE_ID);
  select count(*) into v_n from RRL_CELLS where CELL=v_cell and WARE_ID=o.WARE_ID and nvl(BLOCKED_FOR_ACCEPT,0)=0;
  if v_n!=1 then raise_application_error(-20886,'RECEIVING_CELL_BLOCKED');end if;
  RRL_STOCK_BALANCE_CORE.apply_delta(v_uid,v_cell,v_qty,0,v_base,v_uom_version);
  RRL_STOCK_UNIT_CORE.assert_composition(v_uid,v_cell);
  RRL_STOCK_UNIT_CORE.admit_captured(v_uid,v_cell);
  update RRL_PALLETS set STOCK_ORIGIN_UID=v_uid,CREATED_BY_STOCK_OP=d.get_string('operation_id') where UID_PALLET=v_uid;
  RRL_STOCK_BALANCE_CORE.write_leg(v_uid,null,v_cell,v_qty,v_base,v_uom_version,1,1,1,p_actor,v_event);
  v_response:=h.get_object('result');v_response.put('task_id',v_task);p_result:=v_response.to_clob;
  insert into RRL_SAP_PALLET_RECEIPT(OPERATION_ID,ORDER_ID,LINE_NUMBER,UID_PALLET,SUPPLIER_BATCH,PAYLOAD_HASH,RESULT_JSON,
   RECEIVED_BY,POSTED_BASE_QTY,STOCK_BASE_UOM,STOCK_OPERATION_ID)
   values(d.get_string('operation_id'),o.ORDER_ID,h.get_string('line_number'),v_uid,m.get_string('supplier_batch'),
    rawtohex(sys.dbms_crypto.hash(p_request,sys.dbms_crypto.hash_sh256)),p_result,p_actor,v_qty,v_base,d.get_string('operation_id'));
  select count(*) into v_n from RRL_SAP_SUPPLY_LINE sl where sl.ORDER_ID=o.ORDER_ID and (
   not exists(select 1 from RRL_STOCK_UOM_CONVERSION u where u.ARTICUL=sl.ARTICUL and u.INPUT_UOM=sl.BASE_UOM)
   or nvl((select sum(rec.POSTED_BASE_QTY) from RRL_SAP_PALLET_RECEIPT rec where rec.ORDER_ID=sl.ORDER_ID and rec.LINE_NUMBER=sl.LINE_NUMBER),0)<
     (select RRL_STOCK_MATH.convert_exact(RRL_STOCK_PLAN_HELPER.decimal_text(sl.PLANNED_QTY),u.NUMERATOR,u.DENOMINATOR,u.BASE_SCALE)
      from RRL_STOCK_UOM_CONVERSION u where u.ARTICUL=sl.ARTICUL and u.INPUT_UOM=sl.BASE_UOM and u.POLICY_VERSION=(select max(x.POLICY_VERSION) from RRL_STOCK_UOM_CONVERSION x where x.ARTICUL=sl.ARTICUL and x.INPUT_UOM=sl.BASE_UOM)));
  if v_n=0 then update RRL_PRIHOD_NAKLAD set CONDITION=1,DATE_OF_ACCEPT=nvl(DATE_OF_ACCEPT,sysdate) where ID=o.NAKLAD_ID;end if;
  insert into RRL_SAP_RECEIPT_OUTBOX(EVENT_ID,EVENT_TYPE,PAYLOAD_JSON)
   values(d.get_string('operation_id'),'PALLET_RECEIVED',p_result);
 end;
end;
/

create or replace package body RRL_STOCK_PALLET_UOM as
 procedure resolve_quantity(p_uid varchar2,p_input varchar2,p_quantity varchar2,
  p_base out varchar2,p_quantity_base out number,p_version out number,p_signature out varchar2) is
  p RRL_PALLETS%rowtype;v_input varchar2(20);v_stock_base varchar2(20);
  v_num number;v_den number;v_scale number;v_pack number;v_provenance varchar2(1000);
  v json_object_t:=json_object_t();
 begin
  select * into p from RRL_PALLETS where UID_PALLET=p_uid;
  select min(BASE_UOM),max(BASE_UOM) into v_stock_base,p_base from RRL_REMAINS where UID_POLETA=p_uid and REMAIN>0;
  if v_stock_base is null or p_base!=v_stock_base then raise_application_error(-20887,'PALLET_BASE_UOM_AMBIGUOUS');end if;
  v_input:=nvl(p_input,p_base);
  select max(POLICY_VERSION) into p_version from RRL_STOCK_UOM_CONVERSION where ARTICUL=p.ARTICUL and INPUT_UOM=v_input;
  select BASE_UOM,NUMERATOR,DENOMINATOR,BASE_SCALE,PROVENANCE into p_base,v_num,v_den,v_scale,v_provenance
   from RRL_STOCK_UOM_CONVERSION where ARTICUL=p.ARTICUL and INPUT_UOM=v_input and POLICY_VERSION=p_version;
  if p_base!=v_stock_base then raise_application_error(-20887,'PALLET_BASE_UOM_CONFLICT');end if;
  -- BOX arithmetic follows the actual pallet pack, never a rounded legacy box count.
  if upper(v_input) in ('BOX','CAR','CS','KAR','KOR','КОР') then
   if upper(p_base) not in ('EA','PCS','ST','ШТ') then
    raise_application_error(-20887,'PALLET_BOX_REQUIRES_EXACT_BASE_ALLOCATION');
   end if;
   if nvl(p.MOD_ID,0)!=0 then
    select SHT_IN_KOR into v_pack from RRL_ARTICUL_MODS where ID=p.MOD_ID and ARTICUL=p.ARTICUL;
    v_provenance:='PALLET.MOD_ID';
   else
    select COUNT_SHT_IN_KOR into v_pack from RRL_ARTICULS where ACTICUL=p.ARTICUL;
    v_provenance:='ARTICLE.DEFAULT_PACK';
   end if;
   if v_pack is null or v_pack<1 or v_pack!=trunc(v_pack) or v_pack>1000000000 then
    raise_application_error(-20887,'PALLET_PACK_FACTOR_INVALID');
   end if;
   v_num:=v_pack;v_den:=1;
  end if;
  p_quantity_base:=RRL_STOCK_MATH.convert_exact(p_quantity,v_num,v_den,v_scale);
  v.put('uid',p_uid);v.put('article',p.ARTICUL);v.put('mod_id',p.MOD_ID);
  v.put('input',v_input);v.put('base',p_base);v.put('version',p_version);
  v.put('numerator',v_num);v.put('denominator',v_den);v.put('scale',v_scale);v.put('provenance',v_provenance);
  p_signature:=rawtohex(sys.dbms_crypto.hash(v.to_clob,sys.dbms_crypto.hash_sh256));
 end;
end;
/

create or replace package body RRL_STOCK_PLAN_HELPER as
 procedure fence(p_plan in out nocopy json_array_t,p_kind varchar2,p_id varchar2,p_mode number default 4) is v json_object_t:=json_object_t();
 begin
  v.put('key_hex',rawtohex(RRL_STOCK_LOCK_API.resource_key(p_kind,p_id)));v.put('mode',p_mode);p_plan.append(v);
 end;
 procedure anchor(p_plan in out nocopy json_array_t,p_rank number,p_kind varchar2,p_a varchar2,p_b varchar2 default null) is v json_object_t:=json_object_t();
 begin
  v.put('rank',p_rank);v.put('key_hex',rawtohex(RRL_STOCK_LOCK_API.resource_key(p_kind,p_a,p_b)));p_plan.append(v);
 end;
 procedure row_key(p_plan in out nocopy json_array_t,p_table varchar2,p_id varchar2) is
 begin anchor(p_plan,20,'ROW',p_table,p_id);end;
 function decimal_text(p_value number) return varchar2 is
 begin return to_char(p_value,'TM9','NLS_NUMERIC_CHARACTERS=''.,''');end;
 procedure stock_closure(p_policies in out nocopy json_array_t,p_resources in out nocopy json_array_t,
  p_uid varchar2,p_article varchar2,p_from varchar2,p_to varchar2) is
 begin
  fence(p_policies,'CONFIG','WAREHOUSE');fence(p_policies,'SKU',p_article);
  if p_from is not null then fence(p_policies,'CELL',p_from);anchor(p_resources,40,'SLOT','CELL:'||p_from);end if;
  if p_to is not null then fence(p_policies,'CELL',p_to);anchor(p_resources,40,'SLOT','CELL:'||p_to);end if;
  anchor(p_resources,30,'HU',p_uid);anchor(p_resources,50,'STOCK',p_uid);
  for r in(select RESERVATION_ID,CELL_SLOT_ID from RRL_STOCK_RESERVATION
    where UID_PALLET=p_uid and STATUS in('ACTIVE','ALLOCATED','PICKING') and RESERVATION_KIND='HARD') loop
   row_key(p_resources,'RRL_STOCK_RESERVATION',decimal_text(r.RESERVATION_ID));
   if r.CELL_SLOT_ID is not null then anchor(p_resources,40,'SLOT',decimal_text(r.CELL_SLOT_ID));end if;
  end loop;
  for c in(select TASK_ID,CELL_SLOT_ID from RRL_RECEIPT_SLOT_CLAIM where UID_PALLET=p_uid and STATUS='OCCUPIED') loop
   row_key(p_resources,'RRL_RECEIPT_SLOT_CLAIM',decimal_text(c.TASK_ID));
   anchor(p_resources,40,'SLOT',decimal_text(c.CELL_SLOT_ID));
  end loop;
  for u in(select PHYSICAL_UNIT_KEY from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=p_uid and STOCK_STATUS!='ISSUED') loop
   if u.PHYSICAL_UNIT_KEY is null then raise_application_error(-20884,'COMPOSITION_BINDING_REQUIRED');end if;
   anchor(p_resources,60,'UNIT',u.PHYSICAL_UNIT_KEY);
  end loop;
 end;
end;
/

create or replace package body RRL_STOCK_WAVE_LAUNCH_CMD as
 function signature(p RRL_PICK_RESERVATION%rowtype) return varchar2 is j json_object_t:=json_object_t();
 begin
  j.put('id',p.PICK_RESERVATION_ID);j.put('plan',p.PICK_PLAN_ID);j.put('line',p.PICK_PLAN_LINE_ID);j.put('task',p.PICK_TASK_ID);
  j.put('uid',p.PALLET_UID);j.put('cell',p.SOURCE_CELL_CODE);j.put('article',p.ARTICUL);j.put('qty',RRL_STOCK_PLAN_HELPER.decimal_text(p.RESERVED_QTY));
  j.put('status',p.RESERVATION_STATUS);j.put('level',p.RESERVATION_LEVEL);
  j.put('customer',p.CUSTOMER_ID);j.put('order',p.CUSTOMER_ORDER_ID);
  return rawtohex(sys.dbms_crypto.hash(j.to_clob,sys.dbms_crypto.hash_sh256));
 end;
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is
  d json_object_t:=json_object_t.parse(p_request);v_wave number;v_ware number;v_id number;v_uom varchar2(20);v_ver number;
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();a json_array_t:=json_array_t();v json_object_t:=json_object_t();x json_object_t;
 begin
  v_wave:=d.get_object('source').get_number('wave_id');select WARE_ID into v_ware from RRL_PICK_WAVE where PICK_WAVE_ID=v_wave;
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');
  RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_WAVE',RRL_STOCK_PLAN_HELPER.decimal_text(v_wave));
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
  for o in(select * from RRL_PICK_WAVE_ORDER where PICK_WAVE_ID=v_wave and STATUS='ACTIVE' order by PICK_WAVE_ORDER_ID) loop
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_WAVE_ORDER',RRL_STOCK_PLAN_HELPER.decimal_text(o.PICK_WAVE_ORDER_ID));
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_PLAN',RRL_STOCK_PLAN_HELPER.decimal_text(o.PICK_PLAN_ID));
   for t in(select PICK_TASK_ID from RRL_PICK_TASK where PICK_PLAN_ID=o.PICK_PLAN_ID order by PICK_TASK_ID) loop
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(t.PICK_TASK_ID));
   end loop;
  end loop;
  for pr in(select pr.* from RRL_PICK_RESERVATION pr join RRL_PICK_WAVE_ORDER wo on wo.PICK_PLAN_ID=pr.PICK_PLAN_ID
   where wo.PICK_WAVE_ID=v_wave and wo.STATUS='ACTIVE' and pr.RESERVATION_STATUS='ACTIVE' and pr.RESERVATION_LEVEL='SOFT' order by pr.PICK_RESERVATION_ID) loop
   if a.get_size>=200 then raise_application_error(-20881,'WAVE_LAUNCH_BATCH_BOUND');end if;
   if pr.PALLET_UID is null or pr.SOURCE_CELL_CODE is null or pr.RESERVED_QTY<=0 then raise_application_error(-20884,'WAVE_SOURCE_IDENTITY_REQUIRED');end if;
   select BASE_UOM into v_uom from RRL_REMAINS where UID_POLETA=pr.PALLET_UID and CELL=pr.SOURCE_CELL_CODE;
   select max(POLICY_VERSION) into v_ver from RRL_STOCK_UOM_CONVERSION where ARTICUL=pr.ARTICUL and INPUT_UOM=v_uom and BASE_UOM=v_uom and NUMERATOR=1 and DENOMINATOR=1;
   if v_ver is null then raise_application_error(-20868,'WAVE_BASE_POLICY_REQUIRED');end if;
   select RRL_STOCK_RESERVATION_SQ.nextval into v_id from dual;
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_RESERVATION',RRL_STOCK_PLAN_HELPER.decimal_text(pr.PICK_RESERVATION_ID));
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STOCK_RESERVATION',RRL_STOCK_PLAN_HELPER.decimal_text(v_id));
   RRL_STOCK_PLAN_HELPER.stock_closure(f,r,pr.PALLET_UID,pr.ARTICUL,pr.SOURCE_CELL_CODE,null);
   x:=json_object_t();x.put('projection_id',pr.PICK_RESERVATION_ID);x.put('reservation_id',v_id);x.put('signature',signature(pr));
   x.put('uom',v_uom);x.put('version',v_ver);a.append(x);
  end loop;
  if a.get_size=0 then raise_application_error(-20886,'WAVE_NO_SOFT_RESERVATIONS');end if;
  v.put('wave',v_wave);v.put('warehouse',v_ware);v.put('reservations',a);p_domain:=v.to_clob;p_policies:=f.to_clob;p_resources:=r.to_clob;
 end;
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob) is
  d json_object_t:=json_object_t.parse(p_request);v json_object_t;x json_object_t;j json_object_t:=json_object_t();details json_object_t;
  a json_array_t;plan clob;status varchar2(30);cnt number;ware number;units clob;pr RRL_PICK_RESERVATION%rowtype;
 begin
  if RRL_HAS_WRIGHT(p_actor,'pick_wave_launch')!=1 then raise_application_error(-20882,'WAVE_LAUNCH_FORBIDDEN');end if;
  select RESOLVED_PLAN_JSON into plan from RRL_STOCK_OPERATION where OPERATION_ID=d.get_string('operation_id');v:=json_object_t.parse(plan).get_object('domain');a:=v.get_array('reservations');
  select STATUS,WARE_ID into status,ware from RRL_PICK_WAVE where PICK_WAVE_ID=v.get_number('wave') for update;
  if status not in('DRAFT','PREVIEW') or ware!=v.get_number('warehouse') then raise_application_error(-20886,'WAVE_NOT_LAUNCHABLE');end if;
  select count(*) into cnt from RRL_PICK_RESERVATION pr join RRL_PICK_WAVE_ORDER wo on wo.PICK_PLAN_ID=pr.PICK_PLAN_ID
   where wo.PICK_WAVE_ID=v.get_number('wave') and wo.STATUS='ACTIVE' and pr.RESERVATION_STATUS='ACTIVE' and pr.RESERVATION_LEVEL='SOFT';
  if cnt!=a.get_size then raise_application_error(-20890,'CLOSURE_CHANGED: wave sources');end if;
  for i in 0..a.get_size-1 loop
   x:=treat(a.get(i) as json_object_t);select * into pr from RRL_PICK_RESERVATION where PICK_RESERVATION_ID=x.get_number('projection_id') for update;
   if signature(pr)!=x.get_string('signature') then raise_application_error(-20890,'CLOSURE_CHANGED: wave reservation');end if;
   RRL_STOCK_LOCATION_CORE.assert_ordinary(pr.SOURCE_CELL_CODE,ware,'SOURCE');
   units:=RRL_STOCK_UNIT_CORE.automatic_units(pr.PALLET_UID,pr.SOURCE_CELL_CODE,pr.RESERVED_QTY);
   details:=json_object_t();details.put('reservation_scope','QTY');details.put('pick_wave_id',v.get_number('wave'));
   details.put('pick_plan_id',pr.PICK_PLAN_ID);details.put('pick_plan_line_id',pr.PICK_PLAN_LINE_ID);
   details.put('customer_order_id',pr.CUSTOMER_ORDER_ID);details.put('customer_id',pr.CUSTOMER_ID);
   RRL_STOCK_RESERVE_CORE.create_hard(x.get_number('reservation_id'),pr.PALLET_UID,pr.SOURCE_CELL_CODE,pr.RESERVED_QTY,x.get_string('uom'),x.get_number('version'),
    'PICK_WAVE',v.get_number('wave'),pr.PICK_TASK_ID,'PICKING',p_actor,details.to_clob);
   RRL_STOCK_UNIT_CORE.reserve_units(pr.PALLET_UID,pr.SOURCE_CELL_CODE,x.get_number('reservation_id'),pr.RESERVED_QTY,units);
  end loop;
  RRL_PICK_WAVE_META.launch_wave(v.get_number('wave'),p_actor);
  j.put('operation_id',d.get_string('operation_id'));j.put('wave_id',v.get_number('wave'));j.put('reserved_count',a.get_size);j.put('status','LAUNCHED');p_result:=j.to_clob;
 end;
end;
/
