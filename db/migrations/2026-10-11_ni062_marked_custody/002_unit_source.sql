create or replace package RRL_STORE_RETURN_UNIT_CORE authid definer as
 function approved_proof(p_approval varchar2)return clob;
 function custody_proof(p_approval varchar2,p_metadata json_object_t)return clob;
 function accepted_units(p_receipt varchar2,p_uid varchar2,p_uom varchar2)return clob;
 function select_units(p_receipt varchar2,p_uid varchar2,p_uom varchar2,p_qty number,p_keys clob)return clob;
 procedure persist(p_approval varchar2,p_receipt varchar2,p_uid varchar2,p_cell varchar2,p_units clob);
end;
/

create or replace package body RRL_STORE_RETURN_UNIT_CORE as
 function approved_proof(p_approval varchar2)return clob is
  a RRL_STORE_RETURN_APPROVAL%rowtype;n number;bad number;eligible number;total number;profiles clob;units clob;proof json_object_t;lines json_array_t:=json_array_t();line_value json_object_t:=json_object_t();resolved json_array_t;
 begin
  select *into a from RRL_STORE_RETURN_APPROVAL where OPERATION_ID=p_approval;
  select count(*)into n from RRL_STORE_RETURN_UNIT where APPROVAL_OPERATION_ID=p_approval;
  select count(*),sum(case when SCAN_MODE='UNIT'then 0 else 1 end),json_arrayagg(json_object('system_code'value SYSTEM_CODE,'profile_code'value PROFILE_CODE,'profile_version'value PROFILE_VERSION,'scan_mode'value SCAN_MODE)order by SYSTEM_CODE,PROFILE_CODE returning clob)
   into eligible,bad,profiles from RRL_SKU_RECEIPT_PROFILE where ARTICUL=a.ARTICLE;
  if n=0 and eligible=0 then
   return null;
  end if;
  if n<1 or n>10000 or eligible<1 or eligible>50 or bad!=0 or n*eligible>20000 then raise_application_error(-20886,'STORE_RETURN_APPROVED_CURRENT_UNIT_PROFILES_REQUIRED');end if;
  select count(*),sum(u.BASE_QTY),json_arrayagg(json_object('key'value u.PHYSICAL_UNIT_KEY,'quantity'value RRL_STOCK_PLAN_HELPER.decimal_text(u.BASE_QTY),'base_uom'value u.BASE_UOM,'version'value u.UNIT_VERSION)order by u.PHYSICAL_UNIT_KEY returning clob)
   into eligible,total,units from RRL_STORE_RETURN_UNIT b join RRL_WMS_RECEIPT_UNIT u on u.PHYSICAL_UNIT_KEY=b.PHYSICAL_UNIT_KEY
   where b.APPROVAL_OPERATION_ID=p_approval and u.CURRENT_UID=b.ORIGINAL_UID and u.CURRENT_CELL=b.SOURCE_CELL and u.BASE_QTY=b.BASE_QTY and u.BASE_UOM=b.BASE_UOM and u.UNIT_VERSION=b.SOURCE_UNIT_VERSION and u.STOCK_STATUS='ISSUED'and u.HARD_RESERVATION_ID is null;
  if eligible!=n or total!=a.BASE_QTY then raise_application_error(-20890,'CLOSURE_CHANGED: exact approved return units');end if;
  proof:=json_object_t();proof.put('units',json_array_t.parse(units));proof.put('profiles',json_array_t.parse(profiles));proof.put('physical_unit_count',n);
  line_value.put('accepted',RRL_STOCK_PLAN_HELPER.decimal_text(a.BASE_QTY));line_value.put('missing','0');line_value.put('refused','0');line_value.put('damaged','0');line_value.put('extra','0');lines.append(line_value);
  proof.put('supported',true);proof.put('expected_scan_count',n*proof.get_array('profiles').get_size);return proof.to_clob;
 end;
 function custody_proof(p_approval varchar2,p_metadata json_object_t)return clob is
  wire clob:=approved_proof(p_approval);proof json_object_t;qty number;lines json_array_t:=json_array_t();x json_object_t:=json_object_t();resolved json_array_t;
 begin
  if wire is null then
   if p_metadata.has('unit_scans')and p_metadata.get_array('unit_scans').get_size>0 then raise_application_error(-20886,'STORE_RETURN_ORDINARY_UNEXPECTED_UNIT_SCANS');end if;
   return null;
  end if;
  proof:=json_object_t.parse(wire);select BASE_QTY into qty from RRL_STORE_RETURN_APPROVAL where OPERATION_ID=p_approval;
  x.put('accepted',RRL_STOCK_PLAN_HELPER.decimal_text(qty));x.put('missing','0');x.put('refused','0');x.put('damaged','0');x.put('extra','0');lines.append(x);
  RRL_STORE_MARK_CORE.resolve_disposition(proof,p_metadata,lines,resolved);proof.put('units',resolved);return proof.to_clob;
 end;
 function accepted_units(p_receipt varchar2,p_uid varchar2,p_uom varchar2)return clob is
  proof clob;cell_text varchar2(60);state_text varchar2(30);fact_count number;wire clob;
 begin
  select json_value(COMPOSITION_JSON,'$.cell'),RECEIPT_STATE into cell_text,state_text from RRL_STORE_RECEIPT_FACT where OPERATION_ID=p_receipt;
  select RESOLVED_PLAN_JSON into proof from RRL_STOCK_OPERATION where OPERATION_ID=p_receipt and COMMAND_TYPE='STORE_RECEIPT'and STATE='APPLIED';
  select count(*)into fact_count from RRL_STORE_RECEIPT_UNIT where OPERATION_ID=p_receipt;
  if fact_count=0 and not json_object_t.parse(proof).get_object('domain').has('marked_unit_proof')then return to_clob('[]');end if;
  if fact_count=0 and state_text!='ACCEPTED'then raise_application_error(-20886,'STORE_RETURN_ACCEPTED_UNIT_EVIDENCE_REQUIRED');end if;
  select json_arrayagg(json_object('key'value u.PHYSICAL_UNIT_KEY,'unit_id'value u.UNIT_ID,'origin_uid'value u.UID_PALLET,'quantity'value RRL_STOCK_PLAN_HELPER.decimal_text(u.BASE_QTY),'base_uom'value u.BASE_UOM,'version'value u.UNIT_VERSION)order by u.PHYSICAL_UNIT_KEY returning clob)into wire
   from RRL_WMS_RECEIPT_UNIT u join(
    select PHYSICAL_UNIT_KEY K,BASE_QTY Q,BASE_UOM B,SOURCE_UNIT_VERSION V from RRL_STORE_RECEIPT_UNIT where OPERATION_ID=p_receipt and UNIT_DISPOSITION='ACCEPTED'
    union all
    select j.K,RRL_STOCK_MATH.quantity(j.Q),j.B,j.V from json_table(proof,'$.domain.marked_unit_proof.units[*]'columns(K varchar2(64)path '$.key',Q varchar2(60)path '$.quantity',B varchar2(20)path '$.base_uom',V number path '$.version'))j where fact_count=0 and state_text='ACCEPTED'
   )source on source.K=u.PHYSICAL_UNIT_KEY and source.Q=u.BASE_QTY and source.B=u.BASE_UOM and source.V=u.UNIT_VERSION
   where u.CURRENT_UID=p_uid and u.CURRENT_CELL=cell_text and u.BASE_UOM=p_uom and u.STOCK_STATUS='ISSUED'and u.HARD_RESERVATION_ID is null
   and not exists(select 1 from RRL_STORE_RETURN_UNIT b where b.RECEIPT_OPERATION_ID=p_receipt and b.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY);
  return nvl(wire,to_clob('[]'));
 end;
 function select_units(p_receipt varchar2,p_uid varchar2,p_uom varchar2,p_qty number,p_keys clob)return clob is
  wire clob:=accepted_units(p_receipt,p_uid,p_uom);n number;distinct_count number;chosen number;total number;result_wire clob;
 begin
  select count(*),count(distinct K)into n,distinct_count from json_table(p_keys,'$[*]'columns(K varchar2(64)path '$'));
  if n<1 or n>10000 or n!=distinct_count then raise_application_error(-20886,'STORE_RETURN_EXACT_UNIT_SELECTION_REQUIRED');end if;
  select count(*),sum(RRL_STOCK_MATH.quantity(j.Q)),
   json_arrayagg(json_object('key'value j.K,'quantity'value j.Q,'base_uom'value j.B,'version'value j.V)order by j.K returning clob)
   into chosen,total,result_wire from json_table(wire,'$[*]'columns(K varchar2(64)path '$.key',Q varchar2(60)path '$.quantity',B varchar2(20)path '$.base_uom',V number path '$.version'))j
   where j.K in(select K from json_table(p_keys,'$[*]'columns(K varchar2(64)path '$')));
  if chosen!=n or total!=p_qty then raise_application_error(-20886,'STORE_RETURN_ACCEPTED_SELECTED_UNIT_QUANTITY_REQUIRED');end if;
  return result_wire;
 end;
 procedure persist(p_approval varchar2,p_receipt varchar2,p_uid varchar2,p_cell varchar2,p_units clob)is
  a json_array_t:=json_array_t.parse(p_units);x json_object_t;k varchar2(64);qty number;uom varchar2(20);v number;
 begin
  for i in 0..a.get_size-1 loop
   x:=treat(a.get(i)as json_object_t);k:=x.get_string('key');qty:=RRL_STOCK_MATH.quantity(x.get_string('quantity'));uom:=x.get_string('base_uom');v:=x.get_number('version');
   insert into RRL_STORE_RETURN_UNIT(APPROVAL_OPERATION_ID,RECEIPT_OPERATION_ID,PHYSICAL_UNIT_KEY,ORIGINAL_UID,SOURCE_CELL,BASE_QTY,BASE_UOM,SOURCE_UNIT_VERSION)
    values(p_approval,p_receipt,k,p_uid,p_cell,qty,uom,v);
  end loop;
 end;
end;
/
