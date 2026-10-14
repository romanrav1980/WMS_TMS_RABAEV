select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME not like 'BIN$%';
select TASK_ID,CASE_TASK_ID,PLAN_OPERATION_ID from RRL_ST_DEFER_WAIT_PLAN where CASE_TASK_ID is not null order by TASK_ID;
