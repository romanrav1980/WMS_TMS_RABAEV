create or replace package RRL_MES_RAW_SUPPLY_API authid definer as
 function release_to_production(p_production_order_id number,p_to_ware_id number default null,
  p_to_cell varchar2 default 'MES_PROD',p_allow_partial number default 0,p_created_by varchar2 default null,p_operation_id varchar2 default null) return number;
end;
/
create or replace package body RRL_MES_RAW_SUPPLY_API as
 function release_to_production(p_production_order_id number,p_to_ware_id number default null,
  p_to_cell varchar2 default 'MES_PROD',p_allow_partial number default 0,p_created_by varchar2 default null,p_operation_id varchar2 default null) return number is
  state varchar2(20);d json_object_t:=json_object_t();s json_object_t:=json_object_t();m json_object_t:=json_object_t();result clob;
 begin
  select STATE into state from RRL_STOCK_RELEASE where RELEASE_ID=1;
  if state='PREPARED' then return RRL_MES_RAW_SUPPLY_OLD.release_to_production(p_production_order_id,p_to_ware_id,p_to_cell,p_allow_partial,p_created_by);end if;
  if p_operation_id is null then raise_application_error(-20871,'OPERATION_ID_REQUIRED: MES release');end if;
  d.put('contract_version',2);d.put('operation_id',p_operation_id);d.put('command_type','MES_RELEASE_TO_PRODUCTION');d.put('actor',p_created_by);
  d.put('lines',json_array_t());d.put('units',json_array_t());s.put('production_order_id',p_production_order_id);d.put('source',s);
  m.put('to_cell',p_to_cell);m.put('to_ware_id',p_to_ware_id);m.put('allow_partial',p_allow_partial);d.put('metadata',m);
  RRL_STOCK_NATIVE_API.post(d.to_clob,p_created_by,result);
  return json_object_t.parse(result).get_number('task_count');
 end;
end;
/
