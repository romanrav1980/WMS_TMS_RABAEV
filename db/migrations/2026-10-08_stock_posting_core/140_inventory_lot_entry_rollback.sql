declare n number;begin select count(*) into n from RRL_STOCK_OPERATION; if n>0 then raise_application_error(-20808,'POSTED_OPERATIONS_PREVENT_CODE_ROLLBACK');end if;end;
/
create or replace package RRL_STOCK_INV_ENTRY authid definer
 accessible by(function RRL_INV_CREATE_LINE2,function RRL_INV_CREATE_LINE3,function RRL_INV_CREATE_LINE4) as
 function register_line(p_cell varchar2,p_barcode varchar2,p_article_part varchar2,p_qty number,p_document number,
  p_expiry date,p_actor varchar2,p_operation varchar2) return varchar2;
end;
/

create or replace package body RRL_STOCK_INV_ENTRY as
 function register_line(p_cell varchar2,p_barcode varchar2,p_article_part varchar2,p_qty number,p_document number,
  p_expiry date,p_actor varchar2,p_operation varchar2) return varchar2 is
  d json_object_t:=json_object_t();src json_object_t:=json_object_t();m json_object_t:=json_object_t();x json_object_t;
  requested json_object_t:=json_object_t();a json_array_t:=json_array_t();saved clob;result clob;article varchar2(160);uid varchar2(200);
  base varchar2(20);other_base varchar2(20);version number;n number;quantity_text varchar2(30);wire clob;old_wire clob;
 begin
  if p_document is null or p_document<1 or p_operation is null or p_actor is null or p_qty is null or p_qty<0 or (p_barcode is null and p_article_part is null) then
   raise_application_error(-20871,'INVENTORY_DOCUMENT_ACTOR_OPERATION_REQUIRED');end if;
  RRL_STOCK_MATH.assert_base(p_qty,9);quantity_text:=RRL_STOCK_PLAN_HELPER.decimal_text(p_qty);
  requested.put('cell',p_cell);requested.put('barcode',p_barcode);requested.put('article_part',p_article_part);
  requested.put('quantity',quantity_text);requested.put('document',p_document);requested.put('expiry',to_char(p_expiry,'YYYY-MM-DD'));
  begin
   select CANONICAL_REQUEST into saved from RRL_STOCK_OPERATION where OPERATION_ID=p_operation;
  exception when no_data_found then saved:=null;end;
  if saved is not null then
   d:=json_object_t.parse(saved);
   wire:=requested.to_clob;old_wire:=d.get_object('metadata').get_object('requested_legacy').to_clob;
   if d.get_string('actor')!=p_actor or d.get_string('command_type') not in('INVENTORY_COUNT','INVENTORY_REGISTER_LOT')
    or dbms_lob.compare(wire,old_wire)!=0 then raise_application_error(-20872,'OPERATION_CONFLICT');end if;
   RRL_STOCK_NATIVE_API.post(saved,p_actor,result);return RRL_GIVE_NEXT_CELL(p_cell);
  end if;
  begin
   select ACTICUL into article from RRL_ARTICULS where BARCODE_SHT=p_barcode or BARCODE_KOR=p_barcode or BARCODE_BL=p_barcode;
  exception when no_data_found then
   select ACTICUL into article from RRL_ARTICULS where ACTICUL like '%'||p_article_part;
  end;
  select min(BASE_UOM),max(BASE_UOM) into base,other_base from RRL_STOCK_UOM_CONVERSION
   where ARTICUL=article and INPUT_UOM=BASE_UOM and NUMERATOR=1 and DENOMINATOR=1;
  if base is null or base!=other_base then raise_application_error(-20868,'INVENTORY_BASE_POLICY_AMBIGUOUS');end if;
  uid:='P_'||article||'_G'||to_char(p_document,'TM9')||'_'||p_cell;
  select count(*) into n from RRL_PALLETS where UID_PALLET=uid;
  d:=json_object_t();d.put('contract_version',2);d.put('operation_id',p_operation);d.put('actor',p_actor);
  d.put('lines',json_array_t());d.put('units',json_array_t());src.put('revision_id',p_document);d.put('source',src);
  m.put('reason','Measured legacy inventory');m.put('requested_legacy',requested);
  if n=0 then
   if p_expiry is null or p_qty<=0 then raise_application_error(-20871,'INVENTORY_INITIAL_EXPIRY_QUANTITY_REQUIRED');end if;
   d.put('command_type','INVENTORY_REGISTER_LOT');m.put('uid',uid);m.put('cell',p_cell);m.put('article',article);
   m.put('quantity',quantity_text);m.put('expiry_date',to_char(p_expiry,'YYYY-MM-DD'));m.put('price',1);
  else
   begin select STOCK_VERSION into version from RRL_REMAINS where UID_POLETA=uid and CELL=p_cell;
   exception when no_data_found then version:=0;end;
   d.put('command_type','INVENTORY_COUNT');x:=json_object_t();x.put('uid',uid);x.put('cell',p_cell);x.put('article',article);
   x.put('quantity',quantity_text);x.put('unit',base);x.put('expected_stock_version',version);
   x.put('unit_keys',json_array_t());a.append(x);m.put('counts',a);
  end if;
  d.put('metadata',m);RRL_STOCK_NATIVE_API.post(d.to_clob,p_actor,result);return RRL_GIVE_NEXT_CELL(p_cell);
 end;
end;
/

@@141_revision_cell_rollback.sql
@@014b_recompile.sql
