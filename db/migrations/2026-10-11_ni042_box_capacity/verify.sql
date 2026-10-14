select object_name,object_type,status from user_objects where object_name in('RRL_STOCK_REPL_CAPACITY','RRL_WEIGHT_BOX_CAPACITY');
select name,line,text from user_errors where name in('RRL_STOCK_REPL_CAPACITY','RRL_WEIGHT_BOX_CAPACITY');
