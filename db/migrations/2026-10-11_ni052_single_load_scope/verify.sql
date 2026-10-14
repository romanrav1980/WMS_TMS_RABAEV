select name,type,line,position,text from user_errors where name not like 'BIN$%';
select object_name,object_type from user_objects where status='INVALID';
