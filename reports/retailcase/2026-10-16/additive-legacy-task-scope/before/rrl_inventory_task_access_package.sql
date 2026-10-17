create or replace package RRL_INVENTORY_TASK_ACCESS authid definer as
 procedure claim_task(p_task number,p_actor varchar2);
 procedure assert_count(p_request clob,p_actor varchar2);
 procedure assert_task_count(p_task number,p_actor varchar2,p_operation varchar2,p_revision number);
 procedure assert_read(p_actor varchar2,p_revision number,p_warehouse number,p_task number default null,p_cell varchar2 default null,p_article varchar2 default null);
end;
/
