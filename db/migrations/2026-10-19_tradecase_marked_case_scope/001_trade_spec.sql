create or replace package RRL_TRADE_CASE_ACCESS authid definer as
 function execution_allowed(p_task number,p_actor varchar2)return number;
 function allowed(p_task number,p_actor varchar2)return number;
 procedure assert_scope(p_task number,p_actor varchar2,p_write number);
end;
/
