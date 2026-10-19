select object_name,object_type,status from user_objects where object_name like 'RRL_TRADE%' order by object_name,object_type;
select name,type,line,position,text from user_errors where name like 'RRL_TRADE%' order by name,type,sequence;
select constraint_name,status from user_constraints where table_name in('RRL_TRADE_SITE','RRL_TRADE_DOCUMENT','RRL_TRADE_MESSAGE') order by table_name,constraint_name;
select count(*) as current_invalid from user_objects where status='INVALID' and object_name not like 'BIN$%';