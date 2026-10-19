select name,type,line,text from user_errors where NAME in('RRL_TRADE_CASE_ACCESS','RRL_CASE_TASK_ACCESS','RRL_CASE_ASSIGNMENT_API');
select object_name from user_objects where status='INVALID'and object_name not like'BIN$%';
