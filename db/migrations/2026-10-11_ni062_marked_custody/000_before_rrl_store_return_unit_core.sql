create or replace package RRL_STORE_RETURN_UNIT_CORE authid definer as
 function accepted_units(p_receipt varchar2,p_uid varchar2,p_uom varchar2)return clob;
 function select_units(p_receipt varchar2,p_uid varchar2,p_uom varchar2,p_qty number,p_keys clob)return clob;
 procedure persist(p_approval varchar2,p_receipt varchar2,p_uid varchar2,p_cell varchar2,p_units clob);
end;
/

create or replace package body RRL_STORE_RETURN_UNIT_CORE as
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
