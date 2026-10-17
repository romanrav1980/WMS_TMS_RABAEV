create or replace package RRL_CASE_TASK_ACCESS authid definer as
 function has_current_scoped_execute(p_task number,p_actor varchar2)return number;
 function ordinary_execution_task(p_task number)return number;
 function scoped_metadata_actor(p_task number,p_action varchar2,p_actor varchar2)return number;
 function scoped_executor(p_task number,p_actor varchar2)return number;
 procedure assert_scope(p_task number,p_actor varchar2,p_permission varchar2,p_assignee varchar2 default null);
 procedure assert_command(p_request clob,p_actor varchar2);
 function scoped_assembly_executor(p_task number,p_actor varchar2)return number;
end;
/
