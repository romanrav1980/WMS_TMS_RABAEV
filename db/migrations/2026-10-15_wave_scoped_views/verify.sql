select name,type,line,text from user_errors where name in('RRL_WAVE_EXEC_ACCESS','RRL_WAVE_TIME_API');
select object_name,status from user_objects where object_name in('RRL_WAVE_EXEC_ACCESS','RRL_WAVE_TIME_API');
select count(*) INVALID_COUNT from user_objects where status='INVALID';
