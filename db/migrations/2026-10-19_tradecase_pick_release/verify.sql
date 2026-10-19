select name,line,text from user_errors where name like'RRL_TRADE%'or name in('RRL_STOCK_WAVE_READY','RRL_STOCK_WAVE_PICK_CMD');
select object_name,object_type from user_objects where status='INVALID'and object_name not like'BIN$%';
