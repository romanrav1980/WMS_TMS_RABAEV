select name,type,line,text from user_errors where name in('RRL_WAVE_EXEC_ACCESS','RRL_STOCK_POSTING_API','RRL_STOCK_WAVE_LAUNCH_CMD');
select count(*) INVALID_COUNT from user_objects where status='INVALID';
