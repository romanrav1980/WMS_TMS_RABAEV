select name,type,line,text from user_errors where name not like 'BIN$%';
select object_name,object_type,status from user_objects where status='INVALID'and object_name not like 'BIN$%';
