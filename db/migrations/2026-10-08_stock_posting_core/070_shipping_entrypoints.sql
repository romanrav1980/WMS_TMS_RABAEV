create or replace function RRL_CLOSE_OTHOD_NAKLAD(naklad_num int,iser_id21 varchar2,p_operation_id varchar2 default null)
 return varchar2 authid definer is d json_object_t:=json_object_t();s json_object_t:=json_object_t();v clob;v_state varchar2(20);
begin
 select STATE into v_state from RRL_STOCK_RELEASE where RELEASE_ID=1;
 if v_state='PREPARED' then return RRL_CLOSE_OTHOD_NAKLAD_SP_OLD(naklad_num,iser_id21);end if;
 d.put('contract_version',2);d.put('operation_id',nvl(p_operation_id,'SHIP.DOC:'||RRL_STOCK_PLAN_HELPER.decimal_text(naklad_num)));
 d.put('command_type','SHIP_DOCUMENT');d.put('actor',iser_id21);s.put('document_id',naklad_num);s.put('type','OUTGOING_DOCUMENT');
 d.put('source',s);d.put('lines',json_array_t());d.put('units',json_array_t());d.put('metadata',json_object_t());
 RRL_STOCK_NATIVE_API.post(d.to_clob,iser_id21,v);
 return 'ok';
end;
/
create or replace function RRL_CLOSE_OTHOD_PALLET(PALLET_ID1 varchar2,iser_id21 varchar2,p_operation_id varchar2 default null)
 return varchar2 authid definer is d json_object_t:=json_object_t();s json_object_t:=json_object_t();v clob;v_state varchar2(20);v_id number;
begin
 select STATE into v_state from RRL_STOCK_RELEASE where RELEASE_ID=1;
 if v_state='PREPARED' then return RRL_CLOSE_OTHOD_PALLET_SP_OLD(PALLET_ID1,iser_id21);end if;
 select ID into v_id from RRL_SBORKA_PALLETS where PALLET_UID=PALLET_ID1;
 d.put('contract_version',2);d.put('operation_id',nvl(p_operation_id,'SHIP.PAL:'||RRL_STOCK_PLAN_HELPER.decimal_text(v_id)));
 d.put('command_type','SHIP_PALLET');d.put('actor',iser_id21);s.put('pallet_identifier',PALLET_ID1);s.put('type','OUTGOING_PALLET');
 d.put('source',s);d.put('lines',json_array_t());d.put('units',json_array_t());d.put('metadata',json_object_t());
 RRL_STOCK_NATIVE_API.post(d.to_clob,iser_id21,v);
 return 'ok';
end;
/
