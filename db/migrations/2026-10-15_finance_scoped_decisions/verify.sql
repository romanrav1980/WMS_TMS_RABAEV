select name,type,line,text from user_errors where name in('RRL_LOG_EXPENSE_GUARD','RRL_LOG_EXP_DECISION_GUARD');
select object_name,status from user_objects where object_name in('RRL_LOG_EXPENSE_GUARD','RRL_LOG_EXP_DECISION_GUARD');
select count(*) INVALID_COUNT from user_objects where status='INVALID';
