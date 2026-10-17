create or replace package RRL_CASE_TASK_ACCESS authid definer as
 procedure assert_scope(p_task number,p_actor varchar2,p_permission varchar2,p_assignee varchar2 default null);
 procedure assert_command(p_request clob,p_actor varchar2);
end;
/
