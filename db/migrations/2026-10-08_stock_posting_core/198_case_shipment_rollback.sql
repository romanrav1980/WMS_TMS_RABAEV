declare n number;begin select count(*) into n from RRL_STOCK_OPERATION; if n>0 then raise_application_error(-20808,'POSTED_OPERATIONS_PREVENT_CODE_ROLLBACK');end if;end;
/
create or replace package RRL_STOCK_SHIPPING_CORE authid definer
 accessible by(package RRL_STOCK_PALLET_QC_CMD,package RRL_STOCK_POSTING_API) as
 procedure compile_shipment(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_shipment(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_STOCK_CASE_PICK_CMD authid definer
 accessible by(package RRL_STOCK_CASE_SHORT_CMD,package RRL_STOCK_CASE_MOVE_CMD,package RRL_STOCK_POSTING_API) as
 function carrier_rows(p_task number) return clob;
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
  j.put('operation_id',d.get_string('operation_id'));j.put('status','APPLIED');j.put('document_id',v_id);j.put('allocations',facts);
  p_result:=j.to_clob;
 end;
end;
/

create or replace package body RRL_STOCK_CASE_PICK_CMD as
 function carrier_rows(p_task number) return clob is
  a json_array_t:=json_array_t();x json_object_t;
 begin
  for r in(select h.LOT_UID,s.CELL,s.REMAIN,s.STOCK_VERSION,s.BASE_UOM,p.ARTICUL,h.CASE_PICK_LINE_ID
   from RRL_CASE_CARRIER_LOT h join RRL_REMAINS s on s.UID_POLETA=h.LOT_UID join RRL_PALLETS p on p.UID_PALLET=h.LOT_UID
   where h.CASE_PICK_TASK_ID=p_task and s.REMAIN>0 order by h.LOT_UID,s.CELL fetch first 201 rows only) loop
   if a.get_size=200 then raise_application_error(-20881,'CASE_CARRIER_LOT_BOUND');end if;
   x:=json_object_t();x.put('uid',r.LOT_UID);x.put('cell',r.CELL);x.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(r.REMAIN));
   x.put('version',r.STOCK_VERSION);x.put('base',r.BASE_UOM);x.put('article',r.ARTICUL);x.put('case_line',r.CASE_PICK_LINE_ID);a.append(x);
  end loop;
  return a.to_clob;
 end;
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');v json_object_t:=json_object_t();
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();a json_array_t;chunks json_array_t:=json_array_t();x json_object_t;selected_wire clob;
  ct RRL_CASE_PICK_TASK%rowtype;l RRL_CASE_PICK_LINE%rowtype;pt RRL_PICK_TASK%rowtype;
  task_id number;line_id number;fact number;remaining number;q number;basever number;newres number;target varchar2(150);n number:=0;v_cell varchar2(60);target_cell varchar2(60);
  type source_numbers is table of number index by varchar2(150);consumed source_numbers;steps source_numbers;
 begin
  task_id:=d.get_object('source').get_number('case_task_id');line_id:=d.get_object('source').get_number('case_line_id');
  select * into ct from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=task_id;
  select * into l from RRL_CASE_PICK_LINE where CASE_PICK_LINE_ID=line_id and CASE_PICK_TASK_ID=task_id;
  select * into pt from RRL_PICK_TASK where PICK_TASK_ID=l.PICK_TASK_ID;
  if ct.WARE_ID is null or ct.WARE_ID<1 or ct.SSCC is null or l.CELL_CODE is null or l.ARTICUL is null or l.PICK_TASK_ID is null or l.PICK_WAVE_TASK_ID is null or l.CUSTOMER_ORDER_ID is null then raise_application_error(-20887,'CASE_TASK_IDENTITY_REQUIRED');end if;
  fact:=RRL_STOCK_MATH.quantity(m.get_string('fact_qty'));remaining:=fact-nvl(l.PICKED_QTY,0);v_cell:=l.CELL_CODE;target_cell:='CPT_'||RRL_STOCK_PLAN_HELPER.decimal_text(ct.WARE_ID);
  if remaining<=0 or fact>l.PLANNED_QTY then raise_application_error(-20886,'CASE_PICK_FACT_NOT_INCREASING_OR_EXCEEDS_PLAN');end if;
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');
  RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_CASE_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(task_id));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_CASE_PICK_LINE',RRL_STOCK_PLAN_HELPER.decimal_text(line_id));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(l.PICK_TASK_ID));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_WAVE_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(l.PICK_WAVE_TASK_ID));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_WAVE',RRL_STOCK_PLAN_HELPER.decimal_text(l.PICK_WAVE_ID));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_CUSTOMER_ORDER',RRL_STOCK_PLAN_HELPER.decimal_text(l.CUSTOMER_ORDER_ID));
  RRL_STOCK_PLAN_HELPER.anchor(r,30,'HU','CASE:'||RRL_STOCK_PLAN_HELPER.decimal_text(task_id));
  a:=json_array_t.parse(carrier_rows(task_id));
  for i in 0..a.get_size-1 loop
   x:=treat(a.get(i) as json_object_t);
   RRL_STOCK_PLAN_HELPER.stock_closure(f,r,x.get_string('uid'),x.get_string('article'),x.get_string('cell'),target_cell);
  end loop;
  selected_wire:=d.get_array('units').to_clob;
  for sr in(select sr.RESERVATION_ID,sr.UID_PALLET,sr.CELL,sr.BASE_QTY,sr.BASE_UOM,s.REMAIN,s.STOCK_VERSION,p.EXPIRY_DATE
   from RRL_STOCK_RESERVATION sr join RRL_REMAINS s on s.UID_POLETA=sr.UID_PALLET and s.CELL=sr.CELL
    join RRL_PALLETS p on p.UID_PALLET=sr.UID_PALLET
   where sr.SOURCE_DOC_TYPE='PICK_WAVE' and sr.SOURCE_DOC_ID=l.PICK_WAVE_ID and sr.SOURCE_LINE_ID=l.PICK_TASK_ID
    and sr.RESERVATION_KIND='HARD' and sr.STATUS in('ACTIVE','ALLOCATED','PICKING') and sr.CELL=v_cell
    and p.ARTICUL=l.ARTICUL and not exists(select 1 from RRL_CASE_CARRIER_LOT h where h.LOT_UID=sr.UID_PALLET)
   order by p.EXPIRY_DATE nulls last,sr.UID_PALLET,sr.RESERVATION_ID fetch first 201 rows only) loop
   exit when remaining=0;n:=n+1;
   if n>200 or sr.BASE_QTY is null or sr.BASE_QTY<=0 then raise_application_error(-20881,'CASE_SOURCE_RESERVATION_BOUND_OR_INVALID');end if;
   if d.get_array('units').get_size>0 then
    select nvl(sum(u.BASE_QTY),0) into q from RRL_WMS_RECEIPT_UNIT u
     join json_table(selected_wire,'$[*]' columns(K varchar2(64) path '$'))j on j.K=u.PHYSICAL_UNIT_KEY
     where u.CURRENT_UID=sr.UID_PALLET and u.CURRENT_CELL=v_cell and u.HARD_RESERVATION_ID=sr.RESERVATION_ID and u.STOCK_STATUS!='ISSUED';
    if q=0 then continue;end if;
    if q>remaining or q>sr.BASE_QTY then raise_application_error(-20884,'CASE_SCANNED_UNIT_QUANTITY_CONFLICT');end if;
   else q:=least(remaining,sr.BASE_QTY);end if;
   remaining:=remaining-q;
   select max(POLICY_VERSION) into basever from RRL_STOCK_UOM_CONVERSION where ARTICUL=l.ARTICUL and INPUT_UOM=sr.BASE_UOM and BASE_UOM=sr.BASE_UOM and NUMERATOR=1 and DENOMINATOR=1;
   if basever is null then raise_application_error(-20868,'CASE_BASE_POLICY_REQUIRED');end if;
   target:='CASELOT:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256))||':'||RRL_STOCK_PLAN_HELPER.decimal_text(n);
   select RRL_STOCK_RESERVATION_SQ.nextval into newres from dual;
   RRL_STOCK_PLAN_HELPER.stock_closure(f,r,sr.UID_PALLET,l.ARTICUL,v_cell,target_cell);
   RRL_STOCK_PLAN_HELPER.anchor(r,30,'HU',target);RRL_STOCK_PLAN_HELPER.anchor(r,50,'STOCK',target);
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STOCK_RESERVATION',RRL_STOCK_PLAN_HELPER.decimal_text(newres));
   RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','PALLET:'||target);
   x:=json_object_t();x.put('source_uid',sr.UID_PALLET);x.put('target_uid',target);x.put('reservation',sr.RESERVATION_ID);x.put('new_reservation',newres);
   x.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(q));x.put('base',sr.BASE_UOM);x.put('policy',basever);
   if not consumed.exists(sr.UID_PALLET) then consumed(sr.UID_PALLET):=0;steps(sr.UID_PALLET):=0;end if;
   x.put('stock_version',sr.STOCK_VERSION+steps(sr.UID_PALLET));x.put('source_p',RRL_STOCK_PLAN_HELPER.decimal_text(sr.REMAIN-consumed(sr.UID_PALLET)));
   consumed(sr.UID_PALLET):=consumed(sr.UID_PALLET)+q;steps(sr.UID_PALLET):=steps(sr.UID_PALLET)+1;chunks.append(x);
  end loop;
  if remaining!=0 then raise_application_error(-20869,'CASE_OWN_HARD_IN_PICK_CELL_INSUFFICIENT');end if;
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
  v.put('task_id',task_id);v.put('line_id',line_id);v.put('pick_task',l.PICK_TASK_ID);v.put('wave_task',l.PICK_WAVE_TASK_ID);
  v.put('wave_id',l.PICK_WAVE_ID);v.put('customer_order',l.CUSTOMER_ORDER_ID);v.put('warehouse',ct.WARE_ID);v.put('cell',v_cell);v.put('transit_cell',target_cell);v.put('article',l.ARTICUL);
  v.put('previous_qty',RRL_STOCK_PLAN_HELPER.decimal_text(nvl(l.PICKED_QTY,0)));v.put('planned_qty',RRL_STOCK_PLAN_HELPER.decimal_text(l.PLANNED_QTY));
  v.put('content_version',ct.CONTENT_VERSION);v.put('carrier_identifier',ct.SSCC);v.put('carrier',a);v.put('chunks',chunks);
  p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=v.to_clob;
 end;
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob) is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');v json_object_t;x json_object_t;
  a json_array_t;chunks json_array_t;facts json_array_t:=json_array_t();factx json_object_t;keys json_array_t;selected json_array_t;keyx json_element_t;unit_wire clob;
  ct RRL_CASE_PICK_TASK%rowtype;l RRL_CASE_PICK_LINE%rowtype;pt RRL_PICK_TASK%rowtype;p RRL_PALLETS%rowtype;
  plan clob;nowrows clob;oldrows clob;op varchar2(100);task_id number;line_id number;ware number;v_cell varchar2(60);article varchar2(160);target_cell varchar2(60);
  qty number;fact number;before_qty number;ver number;stockver number;physical number;owned number;base varchar2(20);uid varchar2(150);target varchar2(150);sid number;new_sid number;
  wave_status varchar2(40);n number;posted number;line_no number:=0;unit_key varchar2(64);matched number;scan_product varchar2(4000);newstatus varchar2(20);eventid number;offline varchar2(100);
 begin
  if RRL_HAS_WRIGHT(p_actor,'case_pick_execute')!=1 then raise_application_error(-20882,'CASE_PICK_FORBIDDEN');end if;
  op:=d.get_string('operation_id');select RESOLVED_PLAN_JSON into plan from RRL_STOCK_OPERATION where OPERATION_ID=op;v:=json_object_t.parse(plan).get_object('domain');
  task_id:=v.get_number('task_id');line_id:=v.get_number('line_id');ware:=v.get_number('warehouse');v_cell:=v.get_string('cell');article:=v.get_string('article');target_cell:=v.get_string('transit_cell');
  declare
 v_json_sql_1_1 number:=v.get_number('wave_id');
begin
select STATUS into wave_status from RRL_PICK_WAVE where PICK_WAVE_ID=v_json_sql_1_1 for update;
end;
  if wave_status in('CANCELLED','CLOSED','DRAFT','PREVIEW') or wave_status is null then raise_application_error(-20886,'CASE_WAVE_STATE_CONFLICT');end if;
  select * into ct from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=task_id for update;
  select * into l from RRL_CASE_PICK_LINE where CASE_PICK_LINE_ID=line_id for update;
  select * into pt from RRL_PICK_TASK where PICK_TASK_ID=l.PICK_TASK_ID for update;
  if ct.WARE_ID!=ware or ct.CONTENT_VERSION!=v.get_number('content_version') or ct.SSCC!=v.get_string('carrier_identifier')
   or l.CASE_PICK_TASK_ID!=task_id or l.PICK_TASK_ID!=v.get_number('pick_task') or l.PICK_WAVE_TASK_ID!=v.get_number('wave_task')
   or l.PICK_WAVE_ID!=v.get_number('wave_id') or l.CUSTOMER_ORDER_ID!=v.get_number('customer_order') or l.CELL_CODE!=v_cell or l.ARTICUL!=article
   or RRL_STOCK_PLAN_HELPER.decimal_text(l.PLANNED_QTY)!=v.get_string('planned_qty')
   or RRL_STOCK_PLAN_HELPER.decimal_text(nvl(l.PICKED_QTY,0))!=v.get_string('previous_qty') then raise_application_error(-20890,'CLOSURE_CHANGED: case task identity');end if;
  if ct.STATUS is null or ct.STATUS not in('IN_PROGRESS','PARTIAL','WAIT_REPLENISHMENT') or l.STATUS is null or l.STATUS not in('NEW','ACTIVE','SKIPPED','IN_PROGRESS','PARTIAL','WAIT_REPLENISHMENT')
   or pt.TASK_TYPE is null or pt.TASK_TYPE!='CASE_PICK' or pt.STATUS is null or pt.STATUS in('DONE','CANCELLED','FAILED') or pt.CUSTOMER_ORDER_ID!=l.CUSTOMER_ORDER_ID or pt.ARTICUL!=article then raise_application_error(-20886,'CASE_TASK_LINE_STATE_CONFLICT');end if;
  -- Reporting/rejecting a short uses CONFIG exclusive; this command holds CONFIG shared
  -- and the same task/line anchors, so the pending decision cannot change this fact mid-post.
  select count(*) into n from RRL_CASE_PICK_SHORT where CASE_PICK_LINE_ID=line_id
   and STATUS in('CREATED','PENDING_APPROVAL');
  if n>0 then raise_application_error(-20886,'CASE_SHORT_DECISION_PENDING');end if;
  if ct.ASSIGNED_TO is not null and ct.ASSIGNED_TO!=p_actor and RRL_HAS_WRIGHT(p_actor,'case_pick_manage')!=1 then raise_application_error(-20882,'CASE_TASK_ACTOR_CONFLICT');end if;
  if m.get_string('scan_cell') is null or upper(m.get_string('scan_cell'))!=upper(v_cell)
   or m.get_string('scan_container') is null or m.get_string('scan_container')!=ct.SSCC then raise_application_error(-20886,'CASE_CELL_CARRIER_SCAN_REQUIRED');end if;
  scan_product:=m.get_string('scan_product');
  select count(*) into n from RRL_ARTICULS where ACTICUL=article and scan_product in(ACTICUL,BARCODE_SHT,BARCODE_KOR,BARCODE_BL);
  if n!=1 and d.get_array('units').get_size=0 then raise_application_error(-20886,'CASE_PRODUCT_SCAN_CONFLICT');end if;
  nowrows:=carrier_rows(task_id);a:=v.get_array('carrier');oldrows:=a.to_clob;
  if dbms_lob.compare(nowrows,oldrows)!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: case carrier stock');end if;
  before_qty:=nvl(l.PICKED_QTY,0);posted:=0;
  for i in 0..a.get_size-1 loop
   x:=treat(a.get(i) as json_object_t);
   if x.get_number('case_line')=line_id then posted:=posted+RRL_STOCK_MATH.quantity(x.get_string('quantity'));end if;
  end loop;
  if posted!=before_qty then raise_application_error(-20886,'CASE_PRIOR_FACT_WITHOUT_PHYSICAL_POSTING');end if;
  fact:=RRL_STOCK_MATH.quantity(m.get_string('fact_qty'));
  if fact<=before_qty or fact>l.PLANNED_QTY then raise_application_error(-20886,'CASE_PICK_FACT_CONFLICT');end if;
  keys:=d.get_array('units');unit_wire:=keys.to_clob;matched:=0;
  -- Move already picked contents with their carrier to the newly scanned pick v_cell.
  for i in 0..a.get_size-1 loop
   x:=treat(a.get(i) as json_object_t);uid:=x.get_string('uid');
   if ct.CURRENT_CELL is null or ct.CURRENT_CELL!=x.get_string('cell') then raise_application_error(-20887,'CASE_CARRIER_LOCATION_CONFLICT');end if;
   if x.get_string('cell')!=target_cell then
    base:=x.get_string('base');
    declare
 v_json_sql_2_1 varchar2(32767):=x.get_string('article');
begin
select max(POLICY_VERSION) into ver from RRL_STOCK_UOM_CONVERSION where ARTICUL=v_json_sql_2_1 and INPUT_UOM=base and BASE_UOM=base and NUMERATOR=1 and DENOMINATOR=1;
end;
    line_no:=line_no+1;
    RRL_STOCK_TRANSFER_CORE.move(uid,uid,x.get_string('cell'),target_cell,RRL_STOCK_MATH.quantity(x.get_string('quantity')),base,ver,ware,p_actor,line_no,null,null,null,null,null,'CASE_TRANSIT');
   end if;
  end loop;
  chunks:=v.get_array('chunks');
  for i in 0..chunks.get_size-1 loop
   x:=treat(chunks.get(i) as json_object_t);uid:=x.get_string('source_uid');target:=x.get_string('target_uid');
   qty:=RRL_STOCK_MATH.quantity(x.get_string('quantity'));base:=x.get_string('base');sid:=x.get_number('reservation');new_sid:=x.get_number('new_reservation');
   select REMAIN,STOCK_VERSION into physical,stockver from RRL_REMAINS where UID_POLETA=uid and CELL=v_cell;
   if stockver!=x.get_number('stock_version') or RRL_STOCK_PLAN_HELPER.decimal_text(physical)!=x.get_string('source_p') then raise_application_error(-20890,'CLOSURE_CHANGED: case source stock');end if;
   select BASE_QTY into owned from RRL_STOCK_RESERVATION where RESERVATION_ID=sid and UID_PALLET=uid and CELL=v_cell
    and SOURCE_DOC_TYPE='PICK_WAVE' and SOURCE_DOC_ID=l.PICK_WAVE_ID and SOURCE_LINE_ID=l.PICK_TASK_ID
    and RESERVATION_KIND='HARD' and STATUS in('ACTIVE','ALLOCATED','PICKING');
   if owned<qty then raise_application_error(-20869,'CASE_OWN_HARD_INSUFFICIENT');end if;
   select max(POLICY_VERSION) into ver from RRL_STOCK_UOM_CONVERSION where ARTICUL=article and INPUT_UOM=base and BASE_UOM=base and NUMERATOR=1 and DENOMINATOR=1;
   if ver is null or ver!=x.get_number('policy') then raise_application_error(-20890,'CLOSURE_CHANGED: case UOM policy');end if;
   selected:=json_array_t();
   for selected_unit in(select u.PHYSICAL_UNIT_KEY from RRL_WMS_RECEIPT_UNIT u
    join json_table(unit_wire,'$[*]' columns(K varchar2(64) path '$'))j on j.K=u.PHYSICAL_UNIT_KEY
    where u.CURRENT_UID=uid and u.CURRENT_CELL=v_cell and u.HARD_RESERVATION_ID=sid and u.STOCK_STATUS!='ISSUED'
    order by u.PHYSICAL_UNIT_KEY) loop
    selected.append(selected_unit.PHYSICAL_UNIT_KEY);matched:=matched+1;
   end loop;
   select count(*) into n from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=uid and CURRENT_CELL=v_cell and STOCK_STATUS!='ISSUED';
   if n>0 and selected.get_size=0 then raise_application_error(-20884,'CASE_MARKED_UNIT_SCANS_REQUIRED');end if;
   select * into p from RRL_PALLETS where UID_PALLET=uid;
   if p.ARTICUL!=article then raise_application_error(-20887,'CASE_LOT_ARTICLE_CONFLICT');end if;
   p.STOCK_ORIGIN_UID:=nvl(p.STOCK_ORIGIN_UID,p.UID_PALLET);p.CREATED_BY_STOCK_OP:=op;p.UID_PALLET:=target;p.SSCC:=null;p.PRINTED:=0;
   if p.WEIGHT_BRUTTO is not null or p.WEIGHT_TN is not null or p.COUNT_KOR is not null then
    if p.UNIT_COUNT is null or p.UNIT_COUNT<=0 then raise_application_error(-20887,'CASE_LOT_BIRTH_QUANTITY_REQUIRED');end if;
    p.WEIGHT_BRUTTO:=p.WEIGHT_BRUTTO*qty/p.UNIT_COUNT;
    p.WEIGHT_TN:=p.WEIGHT_TN*qty/p.UNIT_COUNT;p.COUNT_KOR:=p.COUNT_KOR*qty/p.UNIT_COUNT;
   end if;
   p.UNIT_COUNT:=qty;insert into RRL_PALLETS values p;
   line_no:=line_no+1;
   RRL_STOCK_TRANSFER_CORE.move(uid,target,v_cell,target_cell,qty,base,ver,ware,p_actor,line_no,sid,
    case when selected.get_size>0 then selected.to_clob else null end,new_sid,null,null,'CASE_TRANSIT');
   insert into RRL_CASE_CARRIER_LOT(LOT_UID,CASE_PICK_TASK_ID,CASE_PICK_LINE_ID,CREATED_OPERATION,CREATED_BY)
    values(target,task_id,line_id,op,p_actor);
   factx:=json_object_t();factx.put('uid',target);factx.put('source_uid',uid);factx.put('quantity',x.get_string('quantity'));factx.put('unit',base);facts.append(factx);
  end loop;
  if matched!=keys.get_size then raise_application_error(-20884,'CASE_SELECTED_UNIT_NOT_OWNED');end if;
  newstatus:=case when fact=l.PLANNED_QTY then 'PICKED' else 'PARTIAL' end;offline:=m.get_string('offline_event_id');
  update RRL_CASE_PICK_LINE set PICKED_QTY=fact,STATUS=newstatus,LAST_OFFLINE_EVENT_ID=offline,
   STARTED_AT=nvl(STARTED_AT,systimestamp),DONE_AT=case when newstatus='PICKED' then systimestamp else DONE_AT end,UPDATED_AT=systimestamp,UPDATED_BY=p_actor where CASE_PICK_LINE_ID=line_id;
  update RRL_PICK_TASK set FACT_QTY=fact,STATUS=case when newstatus='PICKED' then 'DONE' else 'IN_PROGRESS' end,
   DONE_AT=case when newstatus='PICKED' then sysdate else DONE_AT end,DONE_BY=p_actor,UPDATED_AT=sysdate,UPDATED_BY=p_actor where PICK_TASK_ID=l.PICK_TASK_ID;
  update RRL_PICK_WAVE_TASK set FACT_QTY=fact,STATUS=case when newstatus='PICKED' then 'DONE' else 'IN_PROGRESS' end,
   DONE_AT=case when newstatus='PICKED' then sysdate else DONE_AT end,DONE_BY=p_actor,UPDATED_AT=sysdate,UPDATED_BY=p_actor where PICK_WAVE_TASK_ID=l.PICK_WAVE_TASK_ID;
  update RRL_CASE_PICK_TASK t set CURRENT_CELL=target_cell,CONTENT_VERSION=CONTENT_VERSION+1,
   (TOTAL_LINES,PICKED_LINES,PLANNED_QTY,PICKED_QTY)=(select count(*),nvl(sum(case when STATUS in('PICKED','SHORT_PICKED','CANCELLED') then 1 else 0 end),0),nvl(sum(PLANNED_QTY),0),nvl(sum(PICKED_QTY),0) from RRL_CASE_PICK_LINE z where z.CASE_PICK_TASK_ID=task_id),
   UPDATED_AT=systimestamp,UPDATED_BY=p_actor where t.CASE_PICK_TASK_ID=task_id;
  select RRL_CASE_PICK_EVENT_SQ.nextval into eventid from dual;
  insert into RRL_CASE_PICK_EVENT(CASE_PICK_EVENT_ID,CASE_PICK_TASK_ID,CASE_PICK_LINE_ID,EVENT_TYPE,OFFLINE_EVENT_ID,PAYLOAD_JSON,CREATED_BY)
   values(eventid,task_id,line_id,'LINE_CONFIRMED',offline,p_request,p_actor);
  v:=json_object_t();v.put('operation_id',op);v.put('case_pick_task_id',task_id);v.put('case_pick_line_id',line_id);v.put('status',newstatus);
  v.put('fact_qty',RRL_STOCK_PLAN_HELPER.decimal_text(fact));v.put('carrier_identifier',ct.SSCC);v.put('cell',target_cell);v.put('picked_from_cell',v_cell);v.put('lots',facts);p_result:=v.to_clob;
 end;
end;
/
