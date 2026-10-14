procedure RRL_TARE_ASSERT_WRITE(p_table varchar2,p_key varchar2,p_kind varchar2) authid definer is
 op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');v_kind varchar2(80);v_state varchar2(20);
begin
 if op is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false) then raise_application_error(-20863,'TARE_ROOT_TRANSACTION_REQUIRED');end if;
 select COMMAND_TYPE,STATE into v_kind,v_state from RRL_STOCK_OPERATION where OPERATION_ID=op;
 if v_state!='IN_FLIGHT' or(v_kind!=p_kind and not(p_kind='COUNT_OR_ACCEPT' and v_kind in('TARE_COUNT','TARE_ACCEPT','TARE_DAMAGE','TARE_WRITE_OFF','TARE_BOOK','TARE_BOOK_CANCEL','TARE_LOSS_REPORT','TARE_LOSS_DECIDE')))then raise_application_error(-20863,'TARE_ROOT_COMMAND_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW',p_table,p_key));
end;
