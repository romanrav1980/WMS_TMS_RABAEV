declare n number;begin select count(*) into n from RRL_STOCK_OPERATION; if n>0 then raise_application_error(-20808,'POSTED_OPERATIONS_PREVENT_CODE_ROLLBACK');end if;end;
/
create or replace package RRL_STOCK_REVISION_ENTRY authid definer
 accessible by(package REVIZION) as
 function count_row(p_article varchar2,p_cell varchar2,p_quantity number,p_unit varchar2,p_row number,p_actor varchar2,p_operation varchar2) return varchar2;
 function count_document(p_cell varchar2,p_document number,p_quantity number,p_unit varchar2,p_actor varchar2,p_operation varchar2) return varchar2;
end;
/

create or replace package RRL_STOCK_INVENTORY_BIRTH authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package body RRL_STOCK_REVISION_ENTRY as
 function count_row(p_article varchar2,p_cell varchar2,p_quantity number,p_unit varchar2,p_row number,p_actor varchar2,p_operation varchar2) return varchar2 is
  requested json_object_t:=json_object_t();d json_object_t;m json_object_t:=json_object_t();s json_object_t:=json_object_t();
  x json_object_t:=json_object_t();a json_array_t:=json_array_t();saved clob;wire clob;old_wire clob;result clob;
  doc number;article varchar2(160);v_cell varchar2(60);uid varchar2(200);other_uid varchar2(200);version number;quantity varchar2(30);
 begin
  if p_actor is null or p_operation is null or p_row is null or p_quantity is null or p_quantity<0 or trunc(p_quantity,9)!=p_quantity then
   raise_application_error(-20871,'INVENTORY_ROW_OPERATION_QUANTITY_REQUIRED');end if;
  quantity:=RRL_STOCK_PLAN_HELPER.decimal_text(p_quantity);
  requested.put('article',p_article);requested.put('cell',p_cell);requested.put('quantity',quantity);requested.put('unit',p_unit);requested.put('revision_row',p_row);
  begin select CANONICAL_REQUEST into saved from RRL_STOCK_OPERATION where OPERATION_ID=p_operation;
  exception when no_data_found then saved:=null;end;
  if saved is not null then
   d:=json_object_t.parse(saved);d.on_error(1);
   if d.get_string('actor')!=p_actor or d.get_string('command_type')!='INVENTORY_COUNT'
    or not d.get_object('metadata').has('requested_revision_row') then raise_application_error(-20872,'OPERATION_CONFLICT');end if;
   wire:=requested.to_clob;old_wire:=d.get_object('metadata').get_object('requested_revision_row').to_clob;
   if dbms_lob.compare(wire,old_wire)!=0 then raise_application_error(-20872,'OPERATION_CONFLICT');end if;
   RRL_STOCK_NATIVE_API.post(saved,p_actor,result);return 'ok';
  end if;
  select REVISION_ID,ARTICUL1,CELL into doc,article,v_cell from RRL_REVISION_ROW where ID=p_row;
  if doc is null or article is null or article!=p_article or v_cell is null or v_cell!=p_cell then
   raise_application_error(-20887,'INVENTORY_REVISION_ROW_IDENTITY_CONFLICT');end if;
  select min(r.UID_POLETA),max(r.UID_POLETA) into uid,other_uid from RRL_REMAINS r
   join RRL_PALLETS p on p.UID_PALLET=r.UID_POLETA where r.CELL=v_cell and p.ARTICUL=article and r.REMAIN>0;
  if uid is null or uid!=other_uid then raise_application_error(-20887,'LOT_SELECTION_REQUIRED: inventory-count.html');end if;
  select STOCK_VERSION into version from RRL_REMAINS where UID_POLETA=uid and CELL=v_cell;
  d:=json_object_t();d.put('contract_version',2);d.put('operation_id',p_operation);d.put('actor',p_actor);d.put('command_type','INVENTORY_COUNT');
  d.put('lines',json_array_t());d.put('units',json_array_t());s.put('revision_id',doc);d.put('source',s);
  m.put('reason','Measured revision row');m.put('revision_row_id',p_row);m.put('requested_revision_row',requested);
  x.put('uid',uid);x.put('article',article);x.put('cell',v_cell);x.put('unit',p_unit);x.put('quantity',quantity);
  x.put('expected_stock_version',version);x.put('unit_keys',json_array_t());a.append(x);m.put('counts',a);d.put('metadata',m);
  RRL_STOCK_NATIVE_API.post(d.to_clob,p_actor,result);return 'ok';
 end;
 function count_document(p_cell varchar2,p_document number,p_quantity number,p_unit varchar2,p_actor varchar2,p_operation varchar2) return varchar2 is
  saved clob;result clob;d json_object_t;r json_object_t;row_id number;other_row number;article varchar2(160);
 begin
  if p_operation is null or p_actor is null or p_quantity is null or p_quantity<0 then raise_application_error(-20871,'INVENTORY_OPERATION_QUANTITY_REQUIRED');end if;
  begin select CANONICAL_REQUEST into saved from RRL_STOCK_OPERATION where OPERATION_ID=p_operation;
  exception when no_data_found then saved:=null;end;
  if saved is not null then
   d:=json_object_t.parse(saved);d.on_error(1);
   if d.get_string('actor')!=p_actor or d.get_string('command_type')!='INVENTORY_COUNT'
    or d.get_object('source').get_number('revision_id')!=p_document
    or not d.get_object('metadata').has('requested_revision_row') then raise_application_error(-20872,'OPERATION_CONFLICT');end if;
   r:=d.get_object('metadata').get_object('requested_revision_row');
   if r.get_string('cell')!=p_cell or r.get_string('unit')!=p_unit
    or r.get_string('quantity')!=RRL_STOCK_PLAN_HELPER.decimal_text(p_quantity) then raise_application_error(-20872,'OPERATION_CONFLICT');end if;
   RRL_STOCK_NATIVE_API.post(saved,p_actor,result);return 'ok';
  end if;
  select min(ID),max(ID) into row_id,other_row from RRL_REVISION_ROW where CELL=p_cell and REVISION_ID=p_document;
  if row_id is null or row_id!=other_row then raise_application_error(-20887,'REVISION_ROW_SELECTION_REQUIRED: inventory-count.html');end if;
  select ARTICUL1 into article from RRL_REVISION_ROW where ID=row_id;
  return count_row(article,p_cell,p_quantity,p_unit,row_id,p_actor,p_operation);
 end;
end;
/

create or replace package body RRL_STOCK_INVENTORY_BIRTH as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');v json_object_t:=json_object_t();
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();doc number;ware number;uid varchar2(200);cell varchar2(60);article varchar2(160);
  base varchar2(20);other_base varchar2(20);qty number;version number;scale number;expiry date;price number;
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
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');
  RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_REVIZION',RRL_STOCK_PLAN_HELPER.decimal_text(doc));
  RRL_STOCK_PLAN_HELPER.stock_closure(f,r,uid,article,cell,null);
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','PALLET:'||uid);
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
  v.put('document',doc);v.put('warehouse',ware);v.put('uid',uid);v.put('cell',cell);v.put('article',article);
  v.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(qty));v.put('base',base);v.put('version',version);v.put('expiry_date',to_char(expiry,'YYYY-MM-DD'));v.put('price',price);
  p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=v.to_clob;
 end;
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob) is
  d json_object_t:=json_object_t.parse(p_request);v json_object_t;j json_object_t:=json_object_t();plan clob;
  doc number;ware number;cond number;uid varchar2(200);cell varchar2(60);article varchar2(160);base varchar2(20);version number;
  qty number;expiry date;price number;n number;eventid number;marked number;current_version number;v_count_cell varchar2(60);
 begin
  if RRL_HAS_WRIGHT(p_actor,'stock_inventory_count')!=1 then raise_application_error(-20882,'INVENTORY_BIRTH_FORBIDDEN');end if;
  uid:=d.get_string('operation_id');select RESOLVED_PLAN_JSON into plan from RRL_STOCK_OPERATION where OPERATION_ID=uid;
  v:=json_object_t.parse(plan).get_object('domain');doc:=v.get_number('document');uid:=v.get_string('uid');cell:=v.get_string('cell');
  article:=v.get_string('article');base:=v.get_string('base');version:=v.get_number('version');qty:=RRL_STOCK_MATH.quantity(v.get_string('quantity'));
  expiry:=to_date(v.get_string('expiry_date'),'FXYYYY-MM-DD');price:=v.get_number('price');
  select WARE_ID,CONDITION into ware,cond from RRL_REVIZION where ID=doc for update;
  if ware!=v.get_number('warehouse') or cond is null or cond not in(0,1) then raise_application_error(-20886,'INVENTORY_DOCUMENT_NOT_OPEN');end if;
  RRL_STOCK_LOCATION_CORE.assert_quarantine(cell,ware);
  select max(POLICY_VERSION) into current_version from RRL_STOCK_UOM_CONVERSION where ARTICUL=article and INPUT_UOM=base and BASE_UOM=base and NUMERATOR=1 and DENOMINATOR=1;
  if current_version!=version then raise_application_error(-20890,'CLOSURE_CHANGED: inventory birth policy');end if;
  select greatest(nvl((select MARKING_REQUIRED from RRL_SKU_RECEIPT_POLICY where ARTICUL=article),0),
    nvl((select CRPT_REQUIRED from RRL_FINISHED_GOODS_SKU where ARTICUL=article),0),
    case when exists(select 1 from RRL_SKU_RECEIPT_PROFILE where ARTICUL=article) then 1 else 0 end) into marked from dual;
  if marked!=0 then raise_application_error(-20884,'MARKED_INVENTORY_CAPTURE_REQUIRED');end if;
  select count(*) into n from RRL_PALLETS where UID_PALLET=uid;
  if n>0 then raise_application_error(-20887,'INVENTORY_PALLET_ALREADY_EXISTS: use measured count for existing identity');end if;
  -- The planned CELL fence serializes birth against existing-lot movements.
  -- A changed input file must not add measured inventory on top of live stock.
  v_count_cell:=cell;
  select count(*) into n from RRL_REMAINS s join RRL_PALLETS p on p.UID_PALLET=s.UID_POLETA
   where s.CELL=v_count_cell and p.ARTICUL=article and s.REMAIN>0;
  if n>0 then raise_application_error(-20887,'INVENTORY_CELL_HAS_STOCK: count existing lots');end if;
  declare
 v_json_sql_1_1 varchar2(32767):=d.get_string('operation_id');
begin
insert into RRL_PALLETS(UID_PALLET,ARTICUL,CREATION_DATE,EXPIRY_DATE,UNIT_COUNT,PRICE,PRIHOD_NAKLAD_ID,STOCK_ORIGIN_UID,CREATED_BY_STOCK_OP)
   values(uid,article,systimestamp,expiry,qty,price,-doc,uid,v_json_sql_1_1);
end;
  RRL_STOCK_BALANCE_CORE.apply_delta(uid,cell,qty,0,base,version,0);
  RRL_STOCK_BALANCE_CORE.write_leg(uid,null,cell,qty,base,version,1,1,1,p_actor,eventid);
  j.put('operation_id',d.get_string('operation_id'));j.put('revision_id',doc);j.put('uid',uid);j.put('cell',cell);j.put('article',article);
  j.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(qty));j.put('unit',base);j.put('event_id',eventid);j.put('lot_source','INVENTORY');
  p_result:=j.to_clob;
 end;
end;
/
