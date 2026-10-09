create or replace package RRL_STOCK_REVISION_ENTRY authid definer
 accessible by(package REVIZION) as
 function count_row(p_article varchar2,p_cell varchar2,p_quantity number,p_unit varchar2,p_row number,p_actor varchar2,p_operation varchar2) return varchar2;
 function count_document(p_cell varchar2,p_document number,p_quantity number,p_unit varchar2,p_actor varchar2,p_operation varchar2) return varchar2;
 function birth_legacy(p_facts clob,p_actor varchar2,p_operation varchar2) return varchar2;
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
 function birth_legacy(p_facts clob,p_actor varchar2,p_operation varchar2) return varchar2 is
  requested json_object_t:=json_object_t.parse(p_facts);d json_object_t;m json_object_t;s json_object_t:=json_object_t();
  saved clob;result clob;old_wire clob;wire clob;doc number;other_doc number;naklad number;uid varchar2(200);
 begin
  if p_actor is null or p_operation is null then raise_application_error(-20871,'INVENTORY_OPERATION_ACTOR_REQUIRED');end if;
  begin select CANONICAL_REQUEST into saved from RRL_STOCK_OPERATION where OPERATION_ID=p_operation;
  exception when no_data_found then saved:=null;end;
  if saved is not null then
   d:=json_object_t.parse(saved);d.on_error(1);
   if d.get_string('actor')!=p_actor or d.get_string('command_type')!='INVENTORY_REGISTER_LOT'
    or not d.get_object('metadata').has('legacy_facts') then raise_application_error(-20872,'OPERATION_CONFLICT');end if;
   wire:=requested.to_clob;old_wire:=d.get_object('metadata').get_object('legacy_facts').to_clob;
   if dbms_lob.compare(wire,old_wire)!=0 then raise_application_error(-20872,'OPERATION_CONFLICT');end if;
   RRL_STOCK_NATIVE_API.post(saved,p_actor,result);return d.get_object('metadata').get_string('uid');
  end if;
  naklad:=requested.get_number('receipt_document_id');
  select min(ID),max(ID) into doc,other_doc from RRL_REVIZION where REV_NAKLAD_ID=naklad;
  if doc is null or doc!=other_doc then raise_application_error(-20887,'INVENTORY_REVISION_DOCUMENT_AMBIGUOUS');end if;
  if requested.get_number('pallet_number') is null or requested.get_number('pallet_number')<1
   or requested.get_number('pallet_number')!=trunc(requested.get_number('pallet_number')) then raise_application_error(-20871,'INVENTORY_PALLET_NUMBER_REQUIRED');end if;
  uid:='P_'||requested.get_string('article')||'_G3_'||requested.get_string('cell')||'_'||RRL_STOCK_PLAN_HELPER.decimal_text(requested.get_number('pallet_number'));
  d:=json_object_t();d.put('contract_version',2);d.put('operation_id',p_operation);d.put('actor',p_actor);d.put('command_type','INVENTORY_REGISTER_LOT');
  d.put('lines',json_array_t());d.put('units',json_array_t());s.put('revision_id',doc);d.put('source',s);
  m:=json_object_t();m.put('reason','Measured inventory pallet');m.put('uid',uid);m.put('article',requested.get_string('article'));
  m.put('cell',requested.get_string('cell'));m.put('quantity',requested.get_string('quantity'));m.put('expiry_date',requested.get_string('expiry_date'));
  m.put('price',1);m.put('legacy_facts',requested);d.put('metadata',m);
  RRL_STOCK_NATIVE_API.post(d.to_clob,p_actor,result);return uid;
 end;
end;
/
