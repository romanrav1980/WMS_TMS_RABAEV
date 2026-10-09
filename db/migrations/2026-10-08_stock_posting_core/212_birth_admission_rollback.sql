declare n number;begin select count(*) into n from RRL_STOCK_OPERATION; if n>0 then raise_application_error(-20808,'POSTED_OPERATIONS_PREVENT_CODE_ROLLBACK');end if;end;
/
create or replace package RRL_STOCK_INVENTORY_BIRTH authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package RRL_STOCK_MES_MOVEMENT_CORE authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure execute_movements(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package body RRL_STOCK_INVENTORY_BIRTH as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');v json_object_t:=json_object_t();
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();doc number;ware number;uid varchar2(200);cell varchar2(60);article varchar2(160);
  base varchar2(20);other_base varchar2(20);qty number;version number;scale number;expiry date;price number;legacy json_object_t;legacy_doc number;legacy_owner number;v_mod_id number;gross number;net number;boxes number;defect number;
 begin
  doc:=d.get_object('source').get_number('revision_id');uid:=m.get_string('uid');cell:=m.get_string('cell');article:=m.get_string('article');
  if doc is null or uid is null or lengthb(uid)>150 or cell is null or article is null or trim(m.get_string('reason')) is null then raise_application_error(-20871,'INVENTORY_BIRTH_IDENTITY_REQUIRED');end if;
  select WARE_ID into ware from RRL_REVIZION where ID=doc;
  select min(BASE_UOM),max(BASE_UOM) into base,other_base from RRL_STOCK_UOM_CONVERSION where ARTICUL=article and INPUT_UOM=BASE_UOM and NUMERATOR=1 and DENOMINATOR=1;
  if base is null or base!=other_base then raise_application_error(-20868,'INVENTORY_BASE_POLICY_AMBIGUOUS');end if;
  select max(POLICY_VERSION) into version from RRL_STOCK_UOM_CONVERSION where ARTICUL=article and INPUT_UOM=base and BASE_UOM=base and NUMERATOR=1 and DENOMINATOR=1;
  select BASE_SCALE into scale from RRL_STOCK_UOM_CONVERSION where ARTICUL=article and INPUT_UOM=base and POLICY_VERSION=version;
  qty:=RRL_STOCK_MATH.quantity(m.get_string('quantity'));RRL_STOCK_MATH.assert_base(qty,scale);
  expiry:=to_date(m.get_string('expiry_date'),'FXYYYY-MM-DD');price:=m.get_number('price');
  if expiry is null or price<0 then raise_application_error(-20871,'INVENTORY_LOT_DATA_REQUIRED');end if;
  if m.has('legacy_facts') then
   legacy:=m.get_object('legacy_facts');legacy.on_error(1);legacy_doc:=legacy.get_number('receipt_document_id');
   select REV_NAKLAD_ID into legacy_owner from RRL_REVIZION where ID=doc;
   if legacy_doc is null or legacy_owner is null or legacy_doc!=legacy_owner then raise_application_error(-20887,'INVENTORY_SOURCE_DOCUMENT_CONFLICT');end if;
   v_mod_id:=nvl(legacy.get_number('mod_id'),0);gross:=legacy.get_number('gross_weight');net:=legacy.get_number('net_weight');
   boxes:=legacy.get_number('box_count');defect:=legacy.get_number('defect_percent');
   if gross is null or gross<0 or net is null or net<0 or (gross>0 and net>gross) or boxes is null or boxes<0
    or defect is null or defect<0 or defect>100 or v_mod_id<0 then raise_application_error(-20871,'INVENTORY_PALLET_FACTS_INVALID');end if;
   if v_mod_id>0 then select ID into v_mod_id from RRL_ARTICUL_MODS where ID=v_mod_id and ARTICUL=article;end if;
  end if;
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');
  RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_REVIZION',RRL_STOCK_PLAN_HELPER.decimal_text(doc));
  RRL_STOCK_PLAN_HELPER.stock_closure(f,r,uid,article,cell,null);
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','PALLET:'||uid);
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
  if legacy_doc is not null then RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PRIHOD_NAKLAD',RRL_STOCK_PLAN_HELPER.decimal_text(legacy_doc));end if;
  v.put('document',doc);v.put('warehouse',ware);v.put('uid',uid);v.put('cell',cell);v.put('article',article);
  v.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(qty));v.put('base',base);v.put('version',version);v.put('expiry_date',to_char(expiry,'YYYY-MM-DD'));v.put('price',price);
  p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=v.to_clob;
 end;
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob) is
  d json_object_t:=json_object_t.parse(p_request);v json_object_t;j json_object_t:=json_object_t();plan clob;
  doc number;ware number;cond number;uid varchar2(200);cell varchar2(60);article varchar2(160);base varchar2(20);version number;
  qty number;expiry date;price number;n number;eventid number;marked number;current_version number;v_count_cell varchar2(60);legacy json_object_t;legacy_doc number;legacy_owner number;v_mod_id number;gross number;net number;boxes number;defect number;
 begin
  if RRL_HAS_WRIGHT(p_actor,'stock_inventory_count')!=1 then raise_application_error(-20882,'INVENTORY_BIRTH_FORBIDDEN');end if;
  uid:=d.get_string('operation_id');select RESOLVED_PLAN_JSON into plan from RRL_STOCK_OPERATION where OPERATION_ID=uid;
  v:=json_object_t.parse(plan).get_object('domain');doc:=v.get_number('document');uid:=v.get_string('uid');cell:=v.get_string('cell');
  article:=v.get_string('article');base:=v.get_string('base');version:=v.get_number('version');qty:=RRL_STOCK_MATH.quantity(v.get_string('quantity'));
  expiry:=to_date(v.get_string('expiry_date'),'FXYYYY-MM-DD');price:=v.get_number('price');
  select WARE_ID,CONDITION into ware,cond from RRL_REVIZION where ID=doc for update;
  if ware!=v.get_number('warehouse') or cond is null or cond not in(0,1) then raise_application_error(-20886,'INVENTORY_DOCUMENT_NOT_OPEN');end if;
  if d.get_object('metadata').has('legacy_facts') then
   legacy:=d.get_object('metadata').get_object('legacy_facts');legacy_doc:=legacy.get_number('receipt_document_id');
   select REV_NAKLAD_ID into legacy_owner from RRL_REVIZION where ID=doc;
   if legacy_owner is null or legacy_owner!=legacy_doc then raise_application_error(-20890,'CLOSURE_CHANGED: inventory source document');end if;
   v_mod_id:=nvl(legacy.get_number('mod_id'),0);gross:=legacy.get_number('gross_weight');net:=legacy.get_number('net_weight');
   boxes:=legacy.get_number('box_count');defect:=legacy.get_number('defect_percent');
   if v_mod_id>0 then select ID into v_mod_id from RRL_ARTICUL_MODS where ID=v_mod_id and ARTICUL=article;end if;
  end if;
  RRL_STOCK_LOCATION_CORE.assert_quarantine(cell,ware);
  select max(POLICY_VERSION) into current_version from RRL_STOCK_UOM_CONVERSION where ARTICUL=article and INPUT_UOM=base and BASE_UOM=base and NUMERATOR=1 and DENOMINATOR=1;
  if current_version!=version then raise_application_error(-20890,'CLOSURE_CHANGED: inventory birth policy');end if;
  select greatest(nvl((select MARKING_REQUIRED from RRL_SKU_RECEIPT_POLICY where ARTICUL=article),0),
    nvl((select CRPT_REQUIRED from RRL_FINISHED_GOODS_SKU where ARTICUL=article),0),
    case when exists(select 1 from RRL_SKU_RECEIPT_PROFILE where ARTICUL=article) then 1 else 0 end) into marked from dual;

  select count(*) into n from RRL_PALLETS where UID_PALLET=uid;
  if n>0 then
   declare v_owner varchar2(100);v_op varchar2(100):=d.get_string('operation_id');begin
    select CREATED_BY_STOCK_OP into v_owner from RRL_PALLETS where UID_PALLET=uid;
    if v_owner is null or v_owner!=v_op then raise_application_error(-20887,'INVENTORY_PALLET_ALREADY_EXISTS: use measured count');end if;
   end;
  end if;
  -- The planned CELL fence serializes birth against existing-lot movements.
  -- A changed input file must not add measured inventory on top of live stock.
  v_count_cell:=cell;
  select count(*) into n from RRL_REMAINS s join RRL_PALLETS p on p.UID_PALLET=s.UID_POLETA
   where s.CELL=v_count_cell and p.ARTICUL=article and s.REMAIN>0;
  if n>0 and legacy is not null then
   -- Different explicitly identified pallets may be measured within one revision.
   -- A new revision/file must not load inventory over unrelated existing stock.
   select count(*) into n from RRL_REMAINS s join RRL_PALLETS p on p.UID_PALLET=s.UID_POLETA
    where s.CELL=v_count_cell and p.ARTICUL=article and s.REMAIN>0 and not exists(
     select 1 from RRL_STOCK_OPERATION o where o.OPERATION_ID=p.CREATED_BY_STOCK_OP and o.STATE='APPLIED'
      and o.COMMAND_TYPE='INVENTORY_REGISTER_LOT' and json_value(o.CANONICAL_REQUEST,'$.source.revision_id' returning number)=doc);
   if n>0 then raise_application_error(-20887,'INVENTORY_CELL_HAS_OTHER_STOCK: count existing lots');end if;
  end if;
  declare
 v_json_sql_1_1 varchar2(32767):=d.get_string('operation_id');
begin
select count(*) into n from RRL_PALLETS where UID_PALLET=uid;
if n=0 then insert into RRL_PALLETS(UID_PALLET,ARTICUL,CREATION_DATE,EXPIRY_DATE,UNIT_COUNT,PRICE,PRIHOD_NAKLAD_ID,STOCK_ORIGIN_UID,CREATED_BY_STOCK_OP)
   values(uid,article,systimestamp,expiry,qty,price,-doc,uid,v_json_sql_1_1);end if;
end;
  if legacy is not null then
   update RRL_PALLETS set MOD_ID=v_mod_id,WEIGHT_BRUTTO=gross,WEIGHT_TN=net,COUNT_KOR=boxes,DEFECT_PERC=defect where UID_PALLET=uid;
  end if;
  RRL_STOCK_BALANCE_CORE.apply_delta(uid,cell,qty,0,base,version,0);
  RRL_STOCK_UNIT_CORE.assert_composition(uid,cell);
  RRL_STOCK_BALANCE_CORE.write_leg(uid,null,cell,qty,base,version,1,1,1,p_actor,eventid);
  j.put('operation_id',d.get_string('operation_id'));j.put('revision_id',doc);j.put('uid',uid);j.put('cell',cell);j.put('article',article);
  j.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(qty));j.put('unit',base);j.put('event_id',eventid);j.put('lot_source','INVENTORY');
  p_result:=j.to_clob;
 end;
end;
/

create or replace package body RRL_STOCK_MES_MOVEMENT_CORE as
 procedure execute_movements(p_request clob,p_actor varchar2,p_result out clob) is
  d json_object_t:=json_object_t.parse(p_request);h json_object_t;v json_object_t;items json_array_t;m RRL_MES_MOVEMENT%rowtype;
  o RRL_PRODUCTION_ORDER%rowtype;p RRL_PALLETS%rowtype;v_plan clob;v_uid varchar2(200);v_target varchar2(200);
  v_qty number;v_base varchar2(20);v_version number;v_source_ware number;v_target_ware number;v_event number;
  v_reservation number;v_new_reservation number;v_p number;v_article varchar2(160);v_units clob;
  result json_object_t:=json_object_t();facts json_array_t:=json_array_t();fact json_object_t;v_n number;
 begin
  if RRL_HAS_WRIGHT(p_actor,'mes_wms_bridge_apply')!=1 then raise_application_error(-20882,'MES_WMS_APPLY_FORBIDDEN');end if;
  declare
 v_json_sql_1_1 varchar2(32767):=d.get_string('operation_id');
begin
select RESOLVED_PLAN_JSON into v_plan from RRL_STOCK_OPERATION where OPERATION_ID=v_json_sql_1_1;
end;
  h:=json_object_t.parse(v_plan).get_object('domain');items:=h.get_array('movements');
  declare
 v_json_sql_2_1 number:=h.get_number('production_order_id');
begin
select * into o from RRL_PRODUCTION_ORDER where PRODUCTION_ORDER_ID=v_json_sql_2_1 for update;
end;
  if o.STATUS='CANCELLED' then raise_application_error(-20886,'MES_ORDER_CANCELLED');end if;
  for i in 0..items.get_size-1 loop
   v:=treat(items.get(i) as json_object_t);
   declare
 v_json_sql_3_1 number:=v.get_number('movement_id');
begin
select * into m from RRL_MES_MOVEMENT where MOVEMENT_ID=v_json_sql_3_1 for update;
end;
   if RRL_STOCK_MES_MOVEMENT_PLAN.signature(m)!=v.get_string('signature') then raise_application_error(-20890,'CLOSURE_CHANGED: MES movement');end if;
   if m.STATUS not in('MES_POSTED','ERROR') or m.STATUS is null then raise_application_error(-20886,'MES_MOVEMENT_STATE_CONFLICT');end if;
   v_uid:=v.get_string('physical_uid');v_target:=v.get_string('target_uid');v_article:=v.get_string('article');
   v_qty:=RRL_STOCK_MATH.quantity(v.get_string('base_quantity'));v_base:=v.get_string('base_uom');v_version:=v.get_number('uom_version');
   v_reservation:=v.get_number('reservation_id');v_new_reservation:=v.get_number('new_reservation_id');v_units:=null;
   if d.get_object('metadata').has('units_by_movement') then
    if d.get_object('metadata').get_object('units_by_movement').has(RRL_STOCK_PLAN_HELPER.decimal_text(m.MOVEMENT_ID)) then
     v_units:=d.get_object('metadata').get_object('units_by_movement').get_array(RRL_STOCK_PLAN_HELPER.decimal_text(m.MOVEMENT_ID)).to_clob;
    end if;
   end if;
   if m.MOVEMENT_TYPE='FG_PALLET_RELEASE' then
    select WARE_ID into v_target_ware from RRL_CELLS where CELL=m.TARGET_LOCATION;
    if v_target_ware!=o.WARE_ID then raise_application_error(-20886,'MES_FINISHED_WAREHOUSE_CONFLICT');end if;
    RRL_STOCK_LOCATION_CORE.assert_ordinary(m.TARGET_LOCATION,v_target_ware,'TARGET');
    select count(*) into v_n from RRL_REMAINS where UID_POLETA=v_uid;
    if v_n>0 then raise_application_error(-20886,'MES_FINISHED_STOCK_ALREADY_EXISTS');end if;
    select count(*) into v_n from RRL_PALLETS where UID_PALLET=v_uid;
    if v_n=0 then
     insert into RRL_PALLETS(UID_PALLET,ARTICUL,UNIT_COUNT,PRIHOD_NAKLAD_ID,PROD_BATCH_ID,SSCC,QUALITY_STATUS)
      values(v_uid,v_article,v_qty,0,m.PROD_BATCH_ID,m.SSCC,'RELEASED');
    else
     select * into p from RRL_PALLETS where UID_PALLET=v_uid;
     if p.ARTICUL!=v_article or p.PROD_BATCH_ID!=m.PROD_BATCH_ID or p.UNIT_COUNT!=v_qty then raise_application_error(-20887,'MES_FINISHED_LOT_CONFLICT');end if;
    end if;
    RRL_STOCK_BALANCE_CORE.apply_delta(v_uid,m.TARGET_LOCATION,v_qty,0,v_base,v_version);
    RRL_STOCK_UNIT_CORE.assert_composition(v_uid,m.TARGET_LOCATION);
    RRL_STOCK_BALANCE_CORE.write_leg(v_uid,null,m.TARGET_LOCATION,v_qty,v_base,v_version,i+1,1,1,p_actor,v_event);
   else
    select * into p from RRL_PALLETS where UID_PALLET=v_uid;
    if p.ARTICUL!=v_article or (m.RAW_ARTICUL is not null and m.RAW_ARTICUL!=v_article) then raise_application_error(-20887,'MES_RAW_ARTICLE_CONFLICT');end if;
    select WARE_ID into v_source_ware from RRL_CELLS where CELL=m.SOURCE_LOCATION;
    if v_reservation is not null then
     select count(*) into v_n from RRL_STOCK_RESERVATION where RESERVATION_ID=v_reservation and
      SOURCE_DOC_TYPE='PRODUCTION_ORDER' and SOURCE_DOC_ID=o.PRODUCTION_ORDER_ID and UID_PALLET=v_uid and CELL=m.SOURCE_LOCATION;
     if v_n!=1 then raise_application_error(-20869,'MES_RESERVATION_OWNER_CONFLICT');end if;
    end if;
    if m.MOVEMENT_TYPE='RAW_CONSUMPTION' then
     RRL_STOCK_EFFECT_CORE.consume(v_uid,m.SOURCE_LOCATION,v_qty,v_base,v_version,v_source_ware,p_actor,i+1,
      v_reservation,'PRODUCTION_ORDER',o.PRODUCTION_ORDER_ID,v_units);
    else
     select WARE_ID into v_target_ware from RRL_CELLS where CELL=m.TARGET_LOCATION;
     if v_target_ware!=o.WARE_ID then raise_application_error(-20886,'MES_PRODUCTION_WAREHOUSE_CONFLICT');end if;
     select REMAIN into v_p from RRL_REMAINS where UID_POLETA=v_uid and CELL=m.SOURCE_LOCATION;
     if RRL_STOCK_PLAN_HELPER.decimal_text(v_p)!=v.get_string('source_p') then raise_application_error(-20890,'CLOSURE_CHANGED: MES source quantity');end if;
     if v_target!=v_uid then
      p.STOCK_ORIGIN_UID:=nvl(p.STOCK_ORIGIN_UID,p.UID_PALLET);p.CREATED_BY_STOCK_OP:=d.get_string('operation_id');
      if p.WEIGHT_BRUTTO is not null then
       if p.UNIT_COUNT is null or p.UNIT_COUNT<=0 then raise_application_error(-20887,'PALLET_BIRTH_QUANTITY_REQUIRED');end if;
       p.WEIGHT_BRUTTO:=p.WEIGHT_BRUTTO*v_qty/p.UNIT_COUNT;
      end if;
      p.UID_PALLET:=v_target;p.SSCC:=null;p.UNIT_COUNT:=v_qty;p.PRINTED:=0;
      insert into RRL_PALLETS values p;
     end if;
     RRL_STOCK_TRANSFER_CORE.move(v_uid,v_target,m.SOURCE_LOCATION,m.TARGET_LOCATION,v_qty,v_base,v_version,v_target_ware,
      p_actor,i+1,v_reservation,v_units,v_new_reservation,null,v_source_ware);
    end if;
   end if;
   declare
 v_json_sql_4_1 varchar2(32767):=d.get_string('operation_id');
begin
update RRL_MES_MOVEMENT set STATUS='APPLIED_TO_WMS',SOURCE_UID_PALLET=v_uid,TARGET_UID_PALLET=v_target,
    UID_PALLET=case when MOVEMENT_TYPE='RAW_ISSUE_TO_PRODUCTION' then v_target else UID_PALLET end,
    STOCK_OPERATION_ID=v_json_sql_4_1,POSTED_BASE_QTY=v_qty,STOCK_BASE_UOM=v_base,
    WMS_APPLIED_AT=sysdate,WMS_APPLIED_BY=p_actor,UPDATED_AT=sysdate,UPDATED_BY=p_actor,LAST_ERROR=null where MOVEMENT_ID=m.MOVEMENT_ID;
end;
   fact:=json_object_t();fact.put('movement_id',m.MOVEMENT_ID);fact.put('uid',v_target);fact.put('base_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_qty));
   fact.put('base_uom',v_base);facts.append(fact);
  end loop;
  result.put('operation_id',d.get_string('operation_id'));result.put('production_order_id',o.PRODUCTION_ORDER_ID);result.put('movements',facts);p_result:=result.to_clob;
 end;
end;
/
