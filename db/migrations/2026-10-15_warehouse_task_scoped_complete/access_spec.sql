create or replace package RRL_WAREHOUSE_TASK_ACCESS authid definer as
 function scoped_stock_executor(p_task number,p_actor varchar2) return number;
 function task_signature(p_task number) return varchar2;
 procedure assert_scope(p_task number,p_actor varchar2,p_assignee varchar2 default null);
 procedure assert_completion(p_request clob,p_actor varchar2);
end;
/
