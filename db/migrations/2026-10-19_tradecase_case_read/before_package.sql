create or replace package RRL_TRADE_CASE_ACCESS authid definer accessible by(package RRL_CASE_TASK_ACCESS)as
 procedure assert_scope(p_task number,p_actor varchar2,p_write number);
end;

/
