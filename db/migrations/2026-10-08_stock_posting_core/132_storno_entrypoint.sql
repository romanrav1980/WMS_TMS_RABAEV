create or replace procedure RRL_STORNO_ORDER3(
 order_id int,user_id1 varchar2,p_operation_id varchar2 default null,p_reason varchar2 default 'Reverse incoming document')
authid definer as
 state varchar2(20);operation varchar2(100);j json_object_t:=json_object_t();s json_object_t:=json_object_t();m json_object_t:=json_object_t();result clob;
begin
 select STATE into state from RRL_STOCK_RELEASE where RELEASE_ID=1;
 if state='PREPARED' then RRL_STORNO_ORDER3_SP_OLD(order_id,user_id1);return;end if;
 operation:=nvl(p_operation_id,'RECEIPT.REVERSE:'||to_char(order_id,'TM9'));
 j.put('contract_version',2);j.put('operation_id',operation);j.put('command_type','RECEIPT_REVERSE');j.put('actor',user_id1);
 s.put('receipt_document_id',order_id);j.put('source',s);j.put('lines',json_array_t());j.put('units',json_array_t());
 m.put('reason',p_reason);j.put('metadata',m);
 RRL_STOCK_NATIVE_API.post(j.to_clob,user_id1,result);
end;
/
