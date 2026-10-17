create or replace package RRL_CASE_LIFECYCLE_API authid definer as
 procedure begin_close(p_task number,p_actor nvarchar2);
 procedure task_current_scope(p_task number,p_actor nvarchar2);
 procedure assert_new_close(p_task number,p_actor nvarchar2);
 procedure end_close;
end;
/
