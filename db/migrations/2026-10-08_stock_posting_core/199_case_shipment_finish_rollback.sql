declare n number;begin select count(*) into n from RRL_STOCK_OPERATION; if n>0 then raise_application_error(-20808,'POSTED_OPERATIONS_PREVENT_CODE_ROLLBACK');end if;end;
/
create or replace package RRL_STOCK_SHIPPING_CORE authid definer
 accessible by(package RRL_STOCK_PALLET_QC_CMD,package RRL_STOCK_POSTING_API) as
 procedure compile_shipment(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_shipment(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_STOCK_CASE_MOVE_CMD authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package body RRL_STOCK_SHIPPING_CORE as
 function rows_json(p_kind varchar2,p_id number,p_uid varchar2) return clob is a json_array_t:=json_array_t();v json_object_t;
 begin
  for l in(
   select ID,ARTICUL,COUNT1 QTY,cast(null as varchar2(20)) INPUT_UOM from RRL_OTHOD_NAKLAD_ROWS where p_kind='SHIP_DOCUMENT' and ID_NAKLAD=p_id
   union all select ID,ARTICUL,QUANTITY,EI from RRL_SBORKA_PALLET_ROWS where p_kind='SHIP_PALLET' and PALLET_UID=p_uid
   order by ID
  ) loop
   v:=json_object_t();v.put('id',l.ID);v.put('article',l.ARTICUL);v.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(l.QTY));v.put('input_uom',l.INPUT_UOM);a.append(v);
  end loop;
  return a.to_clob;
 end;
 procedure compile_shipment(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is
  d json_object_t:=json_object_t.parse(p_request);s json_object_t;v json_object_t:=json_object_t();leg json_object_t;
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();a json_array_t;legs json_array_t:=json_array_t();
  l json_object_t;v_kind varchar2(80);v_id number;v_uid varchar2(200);v_ware number;v_cell varchar2(60);v_return_supplier varchar2(255);
  v_article varchar2(160);v_qty number;v_take number;v_base varchar2(20);v_version number;v_row_json clob;v_available number;v_customer_order number;v_order_count number;v_num number;v_den number;v_scale number;v_input varchar2(20);
  v_case_task number;v_case_version number;v_case_cell varchar2(60);v_case_status varchar2(40);v_carrier clob;v_carrier_rows json_array_t;v_carrier_row json_object_t;
  type quantity_map is table of number index by varchar2(2000);used quantity_map;reserved_used quantity_map;k varchar2(2000);sk varchar2(2000);
 begin
  s:=d.get_object('source');v_kind:=d.get_string('command_type');v_id:=s.get_number('document_id');v_uid:=s.get_string('pallet_identifier');
  if v_kind='SHIP_DOCUMENT' then select WARE_ID into v_ware from RRL_OTHOD_NAKLAD where ID=v_id;
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_OTHOD_NAKLAD',RRL_STOCK_PLAN_HELPER.decimal_text(v_id));
  elsif v_kind='SHIP_PALLET' then select ID,WARE_ID,RETURN_SUPPLIER_ID into v_id,v_ware,v_return_supplier from RRL_SBORKA_PALLETS where PALLET_UID=v_uid;
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_SBORKA_PALLETS',RRL_STOCK_PLAN_HELPER.decimal_text(v_id));
  else raise_application_error(-20871,'SHIPPING_SOURCE_TYPE_INVALID');end if;
  if v_kind='SHIP_PALLET' then
   select count(distinct CUSTOMER_ORDER_ID),min(CUSTOMER_ORDER_ID) into v_order_count,v_customer_order from RRL_CUSTOMER_ORDER_FULFILLMENT where LEGACY_SBORKA_PALLET_ID=v_id and PALLET_UID=v_uid;
   if v_order_count>1 then raise_application_error(-20887,'SHIPMENT_CUSTOMER_ORDER_AMBIGUOUS');end if;
   if v_return_supplier is not null and v_customer_order is not null then raise_application_error(-20887,'SUPPLIER_RETURN_CUSTOMER_SOURCE_CONFLICT');end if;
   if v_customer_order is not null then
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_CUSTOMER_ORDER',RRL_STOCK_PLAN_HELPER.decimal_text(v_customer_order));
    for ff in(select FULFILLMENT_ID from RRL_CUSTOMER_ORDER_FULFILLMENT where LEGACY_SBORKA_PALLET_ID=v_id and PALLET_UID=v_uid order by FULFILLMENT_ID) loop
     RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_CUSTOMER_ORDER_FULFILLMENT',RRL_STOCK_PLAN_HELPER.decimal_text(ff.FULFILLMENT_ID));
    end loop;
   end if;
  end if;
  if v_ware is null then raise_application_error(-20886,'SHIPPING_WAREHOUSE_REQUIRED');end if;
  if v_kind='SHIP_PALLET' then
   begin
    select CASE_PICK_TASK_ID,CONTENT_VERSION,CURRENT_CELL,STATUS into v_case_task,v_case_version,v_case_cell,v_case_status
     from RRL_CASE_PICK_TASK where LEGACY_SBORKA_PALLET_ID=v_id;
   exception when no_data_found then v_case_task:=null;end;
   if v_case_task is not null then
    if v_customer_order is null or v_case_status not in('WAIT_CONTROL','CONTROL_IN_PROGRESS','CONTROLLED','READY_TO_SHIP')
     or v_case_cell is null then raise_application_error(-20886,'CASE_SHIPMENT_CARRIER_STATE_REQUIRED');end if;
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_CASE_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(v_case_task));
    RRL_STOCK_PLAN_HELPER.anchor(r,30,'HU','CASE:'||RRL_STOCK_PLAN_HELPER.decimal_text(v_case_task));
    v_carrier:=RRL_STOCK_CASE_PICK_CMD.carrier_rows(v_case_task);v_carrier_rows:=json_array_t.parse(v_carrier);
    if v_carrier_rows.get_size=0 then raise_application_error(-20886,'CASE_SHIPMENT_EMPTY_CARRIER');end if;
    for z in 0..v_carrier_rows.get_size-1 loop
     v_carrier_row:=treat(v_carrier_rows.get(z) as json_object_t);
     if v_carrier_row.get_string('cell')!=v_case_cell then raise_application_error(-20887,'CASE_SHIPMENT_CARRIER_LOCATION_CONFLICT');end if;
     RRL_STOCK_PLAN_HELPER.stock_closure(f,r,v_carrier_row.get_string('uid'),v_carrier_row.get_string('article'),v_case_cell,null);
    end loop;
   end if;
  end if;
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');
  RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
  v_row_json:=rows_json(v_kind,v_id,v_uid);a:=json_array_t.parse(v_row_json);
  if a.get_size<1 or a.get_size>200 then raise_application_error(-20881,'SHIPPING_DOCUMENT_LINE_BOUND');end if;
  for i in 0..a.get_size-1 loop
   l:=treat(a.get(i) as json_object_t);v_article:=l.get_string('article');v_qty:=RRL_STOCK_MATH.quantity(l.get_string('quantity'));
   RRL_STOCK_PLAN_HELPER.row_key(r,case when v_kind='SHIP_DOCUMENT' then 'RRL_OTHOD_NAKLAD_ROWS' else 'RRL_SBORKA_PALLET_ROWS' end,RRL_STOCK_PLAN_HELPER.decimal_text(l.get_number('id')));
   RRL_STOCK_PLAN_HELPER.fence(f,'SKU',v_article);
   if v_customer_order is not null then
    v_input:=l.get_string('input_uom');
    select max(POLICY_VERSION) into v_version from RRL_STOCK_UOM_CONVERSION where ARTICUL=v_article and INPUT_UOM=v_input;
    select BASE_UOM,NUMERATOR,DENOMINATOR,BASE_SCALE into v_base,v_num,v_den,v_scale from RRL_STOCK_UOM_CONVERSION where ARTICUL=v_article and INPUT_UOM=v_input and POLICY_VERSION=v_version;
    v_qty:=RRL_STOCK_MATH.convert_exact(l.get_string('quantity'),v_num,v_den,v_scale);
    for c in(select sr.RESERVATION_ID,sr.SOURCE_LINE_ID,sr.SOURCE_DOC_TYPE,sr.SOURCE_DOC_ID,sr.RESERVATION_VERSION,sr.BASE_QTY,sr.BASE_UOM,rr.UID_POLETA,rr.CELL,rr.REMAIN
     from RRL_STOCK_RESERVATION sr join RRL_REMAINS rr on rr.UID_POLETA=sr.UID_PALLET and rr.CELL=sr.CELL
     join RRL_PALLETS pp on pp.UID_PALLET=sr.UID_PALLET join RRL_CELLS cc on cc.CELL=sr.CELL
     left join RRL_PROD_BATCH_READY_V br on br.PROD_BATCH_ID=pp.PROD_BATCH_ID
     where sr.CUSTOMER_ORDER_ID=v_customer_order and sr.ARTICUL=v_article and sr.RESERVATION_KIND='HARD'
      and sr.RESERVATION_DOMAIN='PICKING' and sr.STATUS in('ACTIVE','ALLOCATED','PICKING') and sr.BASE_QTY>0
      and sr.BASE_UOM=v_base and cc.WARE_ID=v_ware and nvl(cc.BLOCKED_FOR_REMAINS,0)=0 and nvl(cc.BLOCKED_FOR_POPOLNENIE,0)=0
      and nvl(br.IS_SHIPMENT_ALLOWED,1)=1
      and ((v_case_task is null and not exists(select 1 from RRL_CASE_CARRIER_LOT h where h.LOT_UID=sr.UID_PALLET))
       or (v_case_task is not null and sr.CELL=v_case_cell and exists(select 1 from RRL_CASE_CARRIER_LOT h where h.LOT_UID=sr.UID_PALLET and h.CASE_PICK_TASK_ID=v_case_task)))
      and exists(select 1 from RRL_PICK_TASK pt where pt.PICK_TASK_ID=sr.SOURCE_LINE_ID and pt.CUSTOMER_ORDER_ID=v_customer_order and pt.ARTICUL=v_article and pt.STATUS='DONE')
     order by pp.EXPIRY_DATE nulls last,sr.RESERVATION_ID) loop
     exit when v_qty=0;
     sk:=RRL_STOCK_PLAN_HELPER.decimal_text(c.RESERVATION_ID);if not reserved_used.exists(sk) then reserved_used(sk):=0;end if;
     k:=rawtohex(RRL_STOCK_LOCK_API.resource_key('STOCK',c.UID_POLETA,c.CELL));if not used.exists(k) then used(k):=0;end if;
     v_available:=c.BASE_QTY-reserved_used(sk);
     if v_available>0 then
      v_take:=least(v_qty,v_available);
      select max(POLICY_VERSION) into v_version from RRL_STOCK_UOM_CONVERSION where ARTICUL=v_article and INPUT_UOM=c.BASE_UOM and BASE_UOM=c.BASE_UOM and NUMERATOR=1 and DENOMINATOR=1;
      if v_version is null then raise_application_error(-20868,'SHIPPING_BASE_POLICY_REQUIRED');end if;
      RRL_STOCK_PLAN_HELPER.row_key(r,case when c.SOURCE_DOC_TYPE='PICK_WAVE' then 'RRL_PICK_WAVE' else 'RRL_PICK_PLAN' end,RRL_STOCK_PLAN_HELPER.decimal_text(c.SOURCE_DOC_ID));
      RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(c.SOURCE_LINE_ID));
      for pr in(select PICK_RESERVATION_ID from RRL_PICK_RESERVATION where PICK_TASK_ID=c.SOURCE_LINE_ID order by PICK_RESERVATION_ID) loop
       RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_RESERVATION',RRL_STOCK_PLAN_HELPER.decimal_text(pr.PICK_RESERVATION_ID));
      end loop;
      for wr in(select PICK_WAVE_RESERVATION_ID from RRL_PICK_WAVE_RESERVATION where PICK_TASK_ID=c.SOURCE_LINE_ID order by PICK_WAVE_RESERVATION_ID) loop
       RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_WAVE_RESERVATION',RRL_STOCK_PLAN_HELPER.decimal_text(wr.PICK_WAVE_RESERVATION_ID));
      end loop;
      RRL_STOCK_PLAN_HELPER.stock_closure(f,r,c.UID_POLETA,v_article,c.CELL,null);
      leg:=json_object_t();leg.put('row_id',l.get_number('id'));leg.put('uid',c.UID_POLETA);leg.put('cell',c.CELL);leg.put('article',v_article);
      leg.put('source_p',RRL_STOCK_PLAN_HELPER.decimal_text(c.REMAIN-used(k)));leg.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_take));
      leg.put('base_uom',c.BASE_UOM);leg.put('uom_version',v_version);leg.put('reservation_id',c.RESERVATION_ID);leg.put('owner_type',c.SOURCE_DOC_TYPE);leg.put('owner_id',c.SOURCE_DOC_ID);
      leg.put('pick_task_id',c.SOURCE_LINE_ID);leg.put('reservation_version',c.RESERVATION_VERSION);legs.append(leg);used(k):=used(k)+v_take;reserved_used(sk):=reserved_used(sk)+v_take;v_qty:=v_qty-v_take;
      if legs.get_size>200 then raise_application_error(-20881,'SHIPPING_ALLOCATION_BOUND');end if;
     end if;
    end loop;
    if v_qty>0 then raise_application_error(-20868,'SHIPMENT_OWN_PICKED_RESERVATION_INSUFFICIENT');end if;
   else
   if v_return_supplier is not null then
    v_cell:='RETURNS';
    RRL_STOCK_PLAN_HELPER.fence(f,'CELL',v_cell);
    declare v_return_ware number;begin
     select WARE_ID into v_return_ware from RRL_CELLS where CELL=v_cell;
     if v_return_ware is null or v_return_ware!=v_ware then raise_application_error(-20886,'SUPPLIER_RETURN_LOCATION_REQUIRED');end if;
    exception when no_data_found then raise_application_error(-20886,'SUPPLIER_RETURN_LOCATION_REQUIRED');end;
   else select CELL into v_cell from RRL_ARTICULS where ACTICUL=v_article;end if;
   -- Plan only matching article, warehouse and eligible physical cells. No fabricated excess stock.
   for c in(select rr.UID_POLETA,rr.CELL,rr.REMAIN,rr.HARD_RESERVED_BASE,rr.STOCK_VERSION,rr.BASE_UOM,pp.EXPIRY_DATE
    from RRL_REMAINS rr join RRL_PALLETS pp on pp.UID_PALLET=rr.UID_POLETA
    join RRL_CELLS cc on cc.CELL=rr.CELL
    where pp.ARTICUL=v_article and rr.CELL=v_cell and rr.REMAIN>rr.HARD_RESERVED_BASE and cc.WARE_ID=v_ware
     and not exists(select 1 from RRL_CASE_CARRIER_LOT h where h.LOT_UID=rr.UID_POLETA)
     and nvl(cc.BLOCKED_FOR_REMAINS,0)=0 and nvl(cc.BLOCKED_FOR_POPOLNENIE,0)=0
    order by pp.EXPIRY_DATE nulls last,pp.CREATION_DATE nulls last,rr.UID_POLETA
   ) loop
    exit when v_qty=0;
    k:=rawtohex(RRL_STOCK_LOCK_API.resource_key('STOCK',c.UID_POLETA,c.CELL));
    if not used.exists(k) then used(k):=0;end if;
    v_available:=c.REMAIN-c.HARD_RESERVED_BASE-used(k);
    if v_available>0 then
     v_take:=least(v_qty,v_available);
     select max(POLICY_VERSION) into v_version from RRL_STOCK_UOM_CONVERSION where ARTICUL=v_article and INPUT_UOM=c.BASE_UOM and BASE_UOM=c.BASE_UOM and NUMERATOR=1 and DENOMINATOR=1;
     if v_version is null then raise_application_error(-20868,'SHIPPING_BASE_POLICY_REQUIRED');end if;
     RRL_STOCK_PLAN_HELPER.stock_closure(f,r,c.UID_POLETA,v_article,c.CELL,null);
     leg:=json_object_t();leg.put('row_id',l.get_number('id'));leg.put('uid',c.UID_POLETA);leg.put('cell',c.CELL);leg.put('article',v_article);
     leg.put('source_p',RRL_STOCK_PLAN_HELPER.decimal_text(c.REMAIN-used(k)));leg.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_take));
     leg.put('base_uom',c.BASE_UOM);leg.put('uom_version',v_version);
     legs.append(leg);used(k):=used(k)+v_take;v_qty:=v_qty-v_take;
     if legs.get_size>200 then raise_application_error(-20881,'SHIPPING_ALLOCATION_BOUND');end if;
    end if;
   end loop;
   if v_qty>0 then raise_application_error(-20868,'SHIPMENT_AVAILABLE_STOCK_INSUFFICIENT');end if;
   end if;
  end loop;
  if v_case_task is not null then
   for z in 0..v_carrier_rows.get_size-1 loop
    v_carrier_row:=treat(v_carrier_rows.get(z) as json_object_t);
    k:=rawtohex(RRL_STOCK_LOCK_API.resource_key('STOCK',v_carrier_row.get_string('uid'),v_carrier_row.get_string('cell')));
    if not used.exists(k) then raise_application_error(-20886,'CASE_SHIPMENT_CONTENT_MISMATCH');end if;
    if used(k)!=RRL_STOCK_MATH.quantity(v_carrier_row.get_string('quantity')) then raise_application_error(-20886,'CASE_SHIPMENT_CONTENT_MISMATCH');end if;
   end loop;
  end if;
  v.put('case_task',v_case_task);v.put('case_version',v_case_version);v.put('case_carrier',v_carrier_rows);
  v.put('return_supplier_id',v_return_supplier);v.put('customer_order_id',v_customer_order);v.put('document_id',v_id);v.put('pallet_identifier',v_uid);v.put('warehouse',v_ware);
  v.put('rows_signature',rawtohex(sys.dbms_crypto.hash(v_row_json,sys.dbms_crypto.hash_sh256)));v.put('legs',legs);
  p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=v.to_clob;
 end;
 procedure execute_shipment(p_request clob,p_actor varchar2,p_result out clob) is
  d json_object_t:=json_object_t.parse(p_request);v json_object_t;l json_object_t;j json_object_t:=json_object_t();
  a json_array_t;facts json_array_t:=json_array_t();v_plan clob;v_condition number;v_id number;v_uid varchar2(200);
  v_row_json clob;v_p number;v_article varchar2(160);v_units clob;v_row_id number;v_qty number;v_kind varchar2(80);v_ready number;v_pick_task number;v_remaining number;v_return_supplier varchar2(255);sr RRL_STOCK_RESERVATION%rowtype;
 begin
  if RRL_HAS_WRIGHT(p_actor,'CLOSE_OTHOD_NAKLAD')!=1 and RRL_HAS_WRIGHT(p_actor,'stock_posting_shipping')!=1 then raise_application_error(-20882,'SHIPPING_FORBIDDEN');end if;
  v_kind:=d.get_string('command_type');
  declare
 v_json_sql_1_1 varchar2(32767):=d.get_string('operation_id');
begin
select RESOLVED_PLAN_JSON into v_plan from RRL_STOCK_OPERATION where OPERATION_ID=v_json_sql_1_1;
end;
  v:=json_object_t.parse(v_plan).get_object('domain');v_id:=v.get_number('document_id');v_uid:=v.get_string('pallet_identifier');
  if v_kind='SHIP_DOCUMENT' then select CONDITION into v_condition from RRL_OTHOD_NAKLAD where ID=v_id for update;
  else select CONDITION,RETURN_SUPPLIER_ID into v_condition,v_return_supplier from RRL_SBORKA_PALLETS where ID=v_id for update;
   if nvl(v_return_supplier,chr(1))!=nvl(v.get_string('return_supplier_id'),chr(1)) then raise_application_error(-20890,'CLOSURE_CHANGED: supplier return');end if;end if;
  if nvl(v_condition,0)>=2 then raise_application_error(-20886,'SHIPMENT_ALREADY_CLOSED_WITH_OTHER_OPERATION');end if;
  v_row_json:=rows_json(v_kind,v_id,v_uid);
  if rawtohex(sys.dbms_crypto.hash(v_row_json,sys.dbms_crypto.hash_sh256))!=v.get_string('rows_signature') then raise_application_error(-20890,'CLOSURE_CHANGED: shipment rows');end if;
  -- Lock actual document rows before stock DML, consistently with the planned domain.
  if v_kind='SHIP_DOCUMENT' then
   for z in(select ID from RRL_OTHOD_NAKLAD_ROWS where ID_NAKLAD=v_id order by ID for update) loop null;end loop;
  else
   for z in(select ID from RRL_SBORKA_PALLET_ROWS where PALLET_UID=v_uid order by ID for update) loop null;end loop;
  end if;
  v_row_json:=rows_json(v_kind,v_id,v_uid);
  if rawtohex(sys.dbms_crypto.hash(v_row_json,sys.dbms_crypto.hash_sh256))!=v.get_string('rows_signature') then raise_application_error(-20890,'CLOSURE_CHANGED: shipment rows');end if;
  if v.get_number('case_task') is not null then
   declare ct RRL_CASE_PICK_TASK%rowtype;v_task number:=v.get_number('case_task');v_current clob;v_previous clob;begin
    RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_CASE_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(v_task)));
    select * into ct from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=v_task for update;
    if ct.LEGACY_SBORKA_PALLET_ID is null or ct.LEGACY_SBORKA_PALLET_ID!=v_id or ct.CUSTOMER_ORDER_ID!=v.get_number('customer_order_id')
     or ct.WARE_ID is null or ct.WARE_ID!=v.get_number('warehouse')
     or ct.CONTENT_VERSION!=v.get_number('case_version') or ct.STATUS not in('WAIT_CONTROL','CONTROL_IN_PROGRESS','CONTROLLED','READY_TO_SHIP')
     then raise_application_error(-20890,'CLOSURE_CHANGED: CASE shipment');end if;
    v_current:=RRL_STOCK_CASE_PICK_CMD.carrier_rows(v_task);
    v_previous:=v.get_array('case_carrier').to_clob;
    if dbms_lob.compare(v_current,v_previous)!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: CASE contents');end if;
   end;
  end if;
  a:=v.get_array('legs');
  for i in 0..a.get_size-1 loop
   l:=treat(a.get(i) as json_object_t);v_units:=null;v_row_id:=l.get_number('row_id');v_qty:=RRL_STOCK_MATH.quantity(l.get_string('quantity'));
   declare
 v_json_sql_2_1 varchar2(32767):=l.get_string('uid');
begin
select ARTICUL into v_article from RRL_PALLETS where UID_PALLET=v_json_sql_2_1;
end;
   if v_article!=l.get_string('article') then raise_application_error(-20890,'CLOSURE_CHANGED: shipment article');end if;
   declare
 v_json_sql_3_1 varchar2(32767):=l.get_string('uid');
begin
select nvl(br.IS_SHIPMENT_ALLOWED,1) into v_ready from RRL_PALLETS pp left join RRL_PROD_BATCH_READY_V br on br.PROD_BATCH_ID=pp.PROD_BATCH_ID where pp.UID_PALLET=v_json_sql_3_1;
end;
   if v_ready!=1 then raise_application_error(-20886,'SHIPMENT_REGULATORY_NOT_READY');end if;
   if l.has('reservation_id') then
    declare
 v_json_sql_4_1 number:=l.get_number('reservation_id');
begin
select * into sr from RRL_STOCK_RESERVATION where RESERVATION_ID=v_json_sql_4_1 for update;
end;
    if sr.CUSTOMER_ORDER_ID!=v.get_number('customer_order_id') or sr.RESERVATION_KIND!='HARD' or sr.RESERVATION_DOMAIN!='PICKING'
     or sr.STATUS not in('ACTIVE','ALLOCATED','PICKING') or sr.UID_PALLET!=l.get_string('uid') or sr.CELL!=l.get_string('cell') then raise_application_error(-20890,'CLOSURE_CHANGED: shipment owner');end if;
   end if;
   declare
 v_json_sql_5_1 varchar2(32767):=l.get_string('uid');
 v_json_sql_5_2 varchar2(32767):=l.get_string('cell');
begin
select REMAIN into v_p from RRL_REMAINS where UID_POLETA=v_json_sql_5_1 and CELL=v_json_sql_5_2;
end;
   if RRL_STOCK_PLAN_HELPER.decimal_text(v_p)!=l.get_string('source_p') then raise_application_error(-20890,'CLOSURE_CHANGED: shipment stock');end if;
   if d.get_object('metadata').has('units_by_allocation') then
    if d.get_object('metadata').get_object('units_by_allocation').has(RRL_STOCK_PLAN_HELPER.decimal_text(i+1)) then
     v_units:=d.get_object('metadata').get_object('units_by_allocation').get_array(RRL_STOCK_PLAN_HELPER.decimal_text(i+1)).to_clob;
    end if;
   end if;
   RRL_STOCK_EFFECT_CORE.consume(l.get_string('uid'),l.get_string('cell'),v_qty,l.get_string('base_uom'),l.get_number('uom_version'),v.get_number('warehouse'),
    p_actor,i+1,l.get_number('reservation_id'),l.get_string('owner_type'),l.get_number('owner_id'),v_units,case when v_kind='SHIP_DOCUMENT' then v_id end,case when v_kind='SHIP_PALLET' then v_row_id end);
   if v_kind='SHIP_PALLET' then
    declare
 v_json_sql_6_1 varchar2(32767):=l.get_string('uid');
begin
update RRL_SBORKA_PALLET_ROWS set PRIHOD_PALLET_UID=v_json_sql_6_1 where ID=v_row_id;
end;
   end if;
   facts.append(l);
  end loop;
  if v_kind='SHIP_DOCUMENT' then update RRL_OTHOD_NAKLAD set CONDITION=2 where ID=v_id;
  else update RRL_SBORKA_PALLETS set CONDITION=2 where ID=v_id;end if;
  if v.get_number('customer_order_id') is not null then
   declare
 v_json_sql_7_1 number:=v.get_number('customer_order_id');
begin
update RRL_CUSTOMER_ORDER_FULFILLMENT set STATUS='SHIPPED',FACT_QTY=(select sum(QUANTITY) from RRL_SBORKA_PALLET_ROWS where PALLET_UID=v_uid),UPDATED_AT=sysdate,UPDATED_BY=p_actor
    where LEGACY_SBORKA_PALLET_ID=v_id and PALLET_UID=v_uid and CUSTOMER_ORDER_ID=v_json_sql_7_1;
end;
  end if;
  if v.get_number('case_task') is not null then
   declare v_task number:=v.get_number('case_task');v_operation varchar2(100):=d.get_string('operation_id');begin
    update RRL_CASE_PICK_TASK set STATUS='SHIPPED',SHIPPED_OPERATION=v_operation,
     CONTENT_VERSION=CONTENT_VERSION+1,DONE_AT=systimestamp,UPDATED_AT=systimestamp,UPDATED_BY=p_actor
     where CASE_PICK_TASK_ID=v_task;
   end;
  end if;
  j.put('case_pick_task_id',v.get_number('case_task'));
  j.put('operation_id',d.get_string('operation_id'));j.put('status','APPLIED');j.put('document_id',v_id);j.put('allocations',facts);
  p_result:=j.to_clob;
 end;
end;
/

create or replace package body RRL_STOCK_CASE_MOVE_CMD as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');v json_object_t:=json_object_t();
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();a json_array_t;x json_object_t;ct RRL_CASE_PICK_TASK%rowtype;
  task_id number;target varchar2(60);
 begin
  task_id:=d.get_object('source').get_number('case_task_id');select * into ct from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=task_id;
  target:=m.get_string('target_cell');
  if target is null or ct.CURRENT_CELL is null or target=ct.CURRENT_CELL or m.get_number('expected_content_version') is null
   or m.get_number('expected_content_version')!=ct.CONTENT_VERSION then raise_application_error(-20886,'CASE_CARRIER_MOVE_SNAPSHOT_TARGET_REQUIRED');end if;
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');
  RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_CASE_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(task_id));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_WAVE',RRL_STOCK_PLAN_HELPER.decimal_text(ct.PICK_WAVE_ID));
  RRL_STOCK_PLAN_HELPER.anchor(r,30,'HU','CASE:'||RRL_STOCK_PLAN_HELPER.decimal_text(task_id));
  a:=json_array_t.parse(RRL_STOCK_CASE_PICK_CMD.carrier_rows(task_id));
  if a.get_size=0 then raise_application_error(-20886,'CASE_CARRIER_HAS_NO_PHYSICAL_STOCK');end if;
  for i in 0..a.get_size-1 loop
   x:=treat(a.get(i) as json_object_t);
   RRL_STOCK_PLAN_HELPER.stock_closure(f,r,x.get_string('uid'),x.get_string('article'),x.get_string('cell'),target);
  end loop;
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
  v.put('task',task_id);v.put('warehouse',ct.WARE_ID);v.put('from',ct.CURRENT_CELL);v.put('to',target);
  v.put('carrier_identifier',ct.SSCC);v.put('content_version',ct.CONTENT_VERSION);v.put('stocks',a);
  p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=v.to_clob;
 end;
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob) is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');v json_object_t;x json_object_t;j json_object_t:=json_object_t();
  ct RRL_CASE_PICK_TASK%rowtype;a json_array_t;plan clob;oldrows clob;nowrows clob;op varchar2(100);task_id number;ware number;
  target varchar2(60);from_cell varchar2(60);base varchar2(20);article varchar2(160);version number;system_flag number;event_id number;mode_name varchar2(20);
 begin
  if RRL_HAS_WRIGHT(p_actor,'warehouse_task_execute')!=1 and RRL_HAS_WRIGHT(p_actor,'case_pick_execute')!=1 then raise_application_error(-20882,'CASE_CARRIER_MOVE_FORBIDDEN');end if;
  op:=d.get_string('operation_id');select RESOLVED_PLAN_JSON into plan from RRL_STOCK_OPERATION where OPERATION_ID=op;
  v:=json_object_t.parse(plan).get_object('domain');task_id:=v.get_number('task');ware:=v.get_number('warehouse');target:=v.get_string('to');from_cell:=v.get_string('from');
  select * into ct from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=task_id for update;
  if ct.WARE_ID is null or ct.WARE_ID!=ware or ct.CURRENT_CELL is null or ct.CURRENT_CELL!=from_cell
   or ct.CONTENT_VERSION!=v.get_number('content_version') then raise_application_error(-20890,'CLOSURE_CHANGED: carrier move');end if;
  if ct.STATUS is null or ct.STATUS not in('IN_PROGRESS','PARTIAL','WAIT_REPLENISHMENT','WAIT_CONTROL','READY','CONTROLLED') then
   raise_application_error(-20886,'CASE_CARRIER_MOVE_STATE_CONFLICT');end if;
  if m.get_string('scan_container') is null or m.get_string('scan_container')!=ct.SSCC
   or m.get_string('scanned_to_cell') is null or m.get_string('scanned_to_cell')!=target then raise_application_error(-20886,'CASE_CARRIER_DESTINATION_SCAN_REQUIRED');end if;
  select IS_SYSTEM into system_flag from RRL_CELLS where CELL=target;
  if system_flag is null or system_flag!=1 then raise_application_error(-20886,'CASE_CARRIER_CONTROL_OR_STAGING_ZONE_REQUIRED');end if;
  a:=v.get_array('stocks');oldrows:=a.to_clob;nowrows:=RRL_STOCK_CASE_PICK_CMD.carrier_rows(task_id);
  if dbms_lob.compare(oldrows,nowrows)!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: carrier contents');end if;
  mode_name:=case when from_cell='CPT_'||RRL_STOCK_PLAN_HELPER.decimal_text(ware) then 'CASE_EXIT' else 'ORDINARY' end;
  for i in 0..a.get_size-1 loop
   x:=treat(a.get(i) as json_object_t);
   if x.get_string('cell')!=from_cell then raise_application_error(-20887,'CASE_CARRIER_LOCATION_CONFLICT');end if;
   article:=x.get_string('article');base:=x.get_string('base');
   select max(POLICY_VERSION) into version from RRL_STOCK_UOM_CONVERSION where ARTICUL=article and INPUT_UOM=base and BASE_UOM=base and NUMERATOR=1 and DENOMINATOR=1;
   if version is null then raise_application_error(-20868,'CASE_MOVE_BASE_POLICY_REQUIRED');end if;
   RRL_STOCK_TRANSFER_CORE.move(x.get_string('uid'),x.get_string('uid'),from_cell,target,
    RRL_STOCK_MATH.quantity(x.get_string('quantity')),base,version,ware,p_actor,i+1,null,null,null,null,null,mode_name);
  end loop;
  update RRL_CASE_PICK_TASK set CURRENT_CELL=target,CONTENT_VERSION=CONTENT_VERSION+1,UPDATED_AT=systimestamp,UPDATED_BY=p_actor where CASE_PICK_TASK_ID=task_id;
  select RRL_CASE_PICK_EVENT_SQ.nextval into event_id from dual;
  insert into RRL_CASE_PICK_EVENT(CASE_PICK_EVENT_ID,CASE_PICK_TASK_ID,EVENT_TYPE,PAYLOAD_JSON,CREATED_BY)
   values(event_id,task_id,'CARRIER_MOVED',p_request,p_actor);
  j.put('operation_id',op);j.put('case_pick_task_id',task_id);j.put('carrier_identifier',ct.SSCC);j.put('from_cell',from_cell);j.put('cell',target);
  j.put('content_version',ct.CONTENT_VERSION+1);j.put('status','MOVED');j.put('lots',a);p_result:=j.to_clob;
 end;
end;
/
