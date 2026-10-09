-- Existing initial inventory import creates a declared lot; ordinary receipt remains SAP-only.
create or replace package RRL_STOCK_INVENTORY_BIRTH authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
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
  RRL_STOCK_UNIT_CORE.admit_captured(uid,cell);
  RRL_STOCK_BALANCE_CORE.write_leg(uid,null,cell,qty,base,version,1,1,1,p_actor,eventid);
  j.put('operation_id',d.get_string('operation_id'));j.put('revision_id',doc);j.put('uid',uid);j.put('cell',cell);j.put('article',article);
  j.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(qty));j.put('unit',base);j.put('event_id',eventid);j.put('lot_source','INVENTORY');
  p_result:=j.to_clob;
 end;
end;
/
