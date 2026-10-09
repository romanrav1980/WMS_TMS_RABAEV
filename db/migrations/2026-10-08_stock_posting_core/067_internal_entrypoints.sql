-- Default-null keeps metadata signature compatibility; active physical writes require a client intent ID.
create or replace function RRL_INTERNAL_MOVE2(pallet_id varchar2,cell_to varchar2,count1 number,user_id1 varchar2,p_operation_id varchar2 default null)
 return varchar2 authid definer is
 d json_object_t:=json_object_t();m json_object_t:=json_object_t();s json_object_t:=json_object_t();v_result clob;v_state varchar2(20);
begin
 select STATE into v_state from RRL_STOCK_RELEASE where RELEASE_ID=1;
 if v_state='PREPARED' then return RRL_INTERNAL_MOVE2_SP_OLD(pallet_id,cell_to,count1,user_id1);end if;
 if p_operation_id is null then raise_application_error(-20871,'OPERATION_ID_REQUIRED: retain ID for retry');end if;
 if count1 is null or count1<0 then raise_application_error(-20871,'INTERNAL_QUANTITY_INVALID');end if;
 d.put('contract_version',2);d.put('operation_id',p_operation_id);d.put('command_type','INTERNAL_MOVE');d.put('actor',user_id1);
 s.put('type','LEGACY_INTERNAL');d.put('source',s);d.put('lines',json_array_t());d.put('units',json_array_t());
 m.put_null('unit');m.put('uid',pallet_id);m.put('target_cell',cell_to);m.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(count1));d.put('metadata',m);
 RRL_STOCK_NATIVE_API.post(d.to_clob,user_id1,v_result);
 return 'ok_'||cell_to;
end;
/
create or replace function RRL_INTERNAL_MOVE3(pallet_id varchar2,cell_to varchar2,count1 number,user_id1 varchar2,p_operation_id varchar2 default null)
 return varchar2 authid definer is v_state varchar2(20);
begin
 select STATE into v_state from RRL_STOCK_RELEASE where RELEASE_ID=1;
 if v_state='PREPARED' then return RRL_INTERNAL_MOVE3_SP_OLD(pallet_id,cell_to,count1,user_id1);end if;
 return RRL_INTERNAL_MOVE2(pallet_id,cell_to,count1,user_id1,p_operation_id);
end;
/
