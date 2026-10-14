select name,type,line,text from user_errors where name not like 'BIN$%';
select object_name,object_type,status from user_objects where status='INVALID'and object_name not like 'BIN$%';
select MEASUREMENT_ORIGIN,count(*)from RRL_TT_LOAD_BOX_WEIGHT group by MEASUREMENT_ORIGIN;
