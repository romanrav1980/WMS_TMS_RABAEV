select name,type,line,text from user_errors where NAME like'RRL_TRADE%';
select object_name from user_objects where status='INVALID'and object_name not like'BIN$%';
