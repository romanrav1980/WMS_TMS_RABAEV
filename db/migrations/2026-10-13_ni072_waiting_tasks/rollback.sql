declare n number;begin
 select count(*)into n from RRL_ST_DEFER_WAIT_PLAN p join RRL_WAREHOUSE_TASK t on t.TASK_ID=p.TASK_ID where t.STATUS not in('DONE','CANCELLED');
 if n!=0 then raise_application_error(-20886,'DEFER_WAIT_ACTIVE_TASKS_PREVENT_CODE_ROLLBACK');end if;
end;
/
@@000_before_rrl_stock_task_plan_package_body.sql
@@000_before_rrl_stock_task_core_package_body.sql
@@000_before_rrl_stock_task_domain_package_body.sql
@@000_before_cell_guard.sql
@@000_before_rrl_st_defer_physical_package.sql
@@000_before_rrl_st_defer_physical_package_body.sql
alter package RRL_ST_DEFER_API compile body;
/
alter package RRL_STOCK_POSTING_API compile body;
/
drop package RRL_ST_DEFER_WAIT_CORE;
/
create or replace package body RRL_ST_DEFER_WAIT_API as
 function write_allowed return number is begin return 0;end;
 procedure plan_waiting(p_operation varchar2,p_decision varchar2,p_actor varchar2,p_result out clob)is
 begin raise_application_error(-20886,'DEFER_WAIT_PLANNER_CODE_ROLLED_BACK');end;
end;
/
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-13-772-st-defer-wait-task';
/
