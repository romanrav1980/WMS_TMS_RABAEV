select object_name,object_type,status from user_objects where object_name in('RRL_CASE_WEIGHT_SCAN','RRL_STOCK_CASE_PICK_CMD');
select name,line,text from user_errors where name in('RRL_CASE_WEIGHT_SCAN','RRL_STOCK_CASE_PICK_CMD');
