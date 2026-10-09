create or replace package RRL_STOCK_QUALITY_ENTRY authid definer as
 function scan(p_pallet varchar2,p_errors number,p_note varchar2,p_picker varchar2,p_actor varchar2,p_operation varchar2) return number;
 function weight(p_kind varchar2,p_pallet varchar2,p_gross varchar2,p_wood varchar2,p_actor varchar2,p_operation varchar2) return number;
end;
/
create or replace package body RRL_STOCK_QUALITY_ENTRY as
 function run(p_pallet varchar2,p_metadata json_object_t,p_actor varchar2,p_operation varchar2) return number is
  d json_object_t:=json_object_t();s json_object_t:=json_object_t();wire clob;j json_object_t;
 begin
  if p_pallet is null or p_actor is null or p_operation is null then raise_application_error(-20871,'QUALITY_ACTOR_AND_OPERATION_REQUIRED');end if;
  d.put('contract_version',2);d.put('command_type','OUTGOING_PALLET_CHECK');d.put('operation_id',p_operation);d.put('actor',p_actor);
  s.put('pallet_identifier',p_pallet);d.put('source',s);d.put('metadata',p_metadata);d.put('lines',json_array_t());d.put('units',json_array_t());
  RRL_STOCK_NATIVE_API.post(d.to_clob,p_actor,wire);j:=json_object_t.parse(wire);return j.get_number('return_code');
 end;
 function scan(p_pallet varchar2,p_errors number,p_note varchar2,p_picker varchar2,p_actor varchar2,p_operation varchar2) return number is m json_object_t:=json_object_t();
 begin
  m.put('quality_kind','SCAN');m.put('error_count',p_errors);m.put('note',p_note);m.put('picker',p_picker);
  return run(p_pallet,m,p_actor,p_operation);
 end;
 function weight(p_kind varchar2,p_pallet varchar2,p_gross varchar2,p_wood varchar2,p_actor varchar2,p_operation varchar2) return number is m json_object_t:=json_object_t();gross number;wood number;
 begin
  gross:=RRL_STOCK_MATH.quantity(replace(trim(p_gross),',','.'));wood:=RRL_STOCK_MATH.quantity(replace(trim(p_wood),',','.'));
  m.put('quality_kind',p_kind);m.put('gross_weight',RRL_STOCK_PLAN_HELPER.decimal_text(gross));m.put('wood_weight',RRL_STOCK_PLAN_HELPER.decimal_text(wood));
  return run(p_pallet,m,p_actor,p_operation);
 end;
end;
/
