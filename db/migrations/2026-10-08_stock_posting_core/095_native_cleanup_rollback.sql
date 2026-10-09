declare n number;begin select count(*) into n from RRL_STOCK_OPERATION; if n>0 then raise_application_error(-20808,'POSTED_OPERATIONS_PREVENT_CODE_ROLLBACK');end if;end;
/
create or replace package RRL_STOCK_NATIVE_API authid definer as
 procedure post(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package body RRL_STOCK_NATIVE_API as
 procedure post(p_request clob,p_actor varchar2,p_result out clob) is
  v_attempt number:=0;v_started timestamp:=systimestamp;v_code number;v_committing boolean:=false;
 begin
  if dbms_transaction.local_transaction_id(false) is not null then
   raise_application_error(-20862,'NATIVE_POST_REQUIRES_CLEAN_TRANSACTION');
  end if;
  loop
   v_attempt:=v_attempt+1;
   begin
    RRL_STOCK_POSTING_API.prepare_command(p_request,p_actor,p_result);
    if p_result is null then RRL_STOCK_POSTING_API.execute_prepared(p_result);end if;
    v_committing:=true;
    commit;
    v_committing:=false;
    RRL_STOCK_POSTING_API.reset_connection;
    return;
   exception when others then
    v_code:=sqlcode;
    rollback;
    RRL_STOCK_POSTING_API.reset_connection;
    if v_committing then raise_application_error(-20891,'RESULT_UNCERTAIN: retry identical operation ID');end if;
    if v_code not in(-60,-54,-30006,-20840,-20890) or v_attempt>=3 or systimestamp>v_started+interval '25' second then raise;end if;
    sys.dbms_lock.sleep(case when v_attempt=1 then 0.1 else 0.3 end);
   end;
  end loop;
 end;
end;
/
