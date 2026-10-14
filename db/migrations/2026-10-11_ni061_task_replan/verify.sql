select name,type,line,text from user_errors where name not like 'BIN$%';
select TASK_ID,STATUS,CANCELLED_BY from RRL_WAREHOUSE_TASK where TASK_ID in(970,972);
select TASK_ID,TASK_TEMP_MIN,TASK_TEMP_MAX from RRL_INTERWARE_PUT_PLAN where TASK_ID in(970,972);
