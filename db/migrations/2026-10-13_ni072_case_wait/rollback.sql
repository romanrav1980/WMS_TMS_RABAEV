declare n number;begin select count(*)into n from RRL_ST_DEFER_WAIT_PLAN where CASE_TASK_ID is not null;if n>0 then raise_application_error(-20886,'CASE_WAIT_ROLLBACK_REGISTERED_TASKS_EXIST');end if;end;
/
@@000_before_rrl_stock_posting_api.sql
@@000_before_rrl_stock_case_move_cmd.sql
@@000_before_rrl_st_defer_wait_api.sql
@@000_before_rrl_st_defer_api.sql
@@000_before_rrl_st_defer_physical.sql
drop package RRL_ST_DEFER_CASE_WAIT;
alter table RRL_ST_DEFER_WAIT_PLAN drop constraint RRL_DWAIT_CASE_FK;
alter table RRL_ST_DEFER_WAIT_PLAN drop constraint RRL_DWAIT_CASE_CK;
alter table RRL_ST_DEFER_WAIT_PLAN drop column CASE_TASK_ID;
@@008_compile.sql
