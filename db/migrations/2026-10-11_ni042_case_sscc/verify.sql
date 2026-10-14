select object_name,object_type,status from user_objects where object_name in('RRL_SSCC_ALLOCATOR','RRL_CASE_SSCC_API','RRL_CASE_SSCC_LABEL_GUARD','RRL_CASE_SSCC_ID_GUARD','RRL_STOCK_CASE_PICK_CMD');
select name,type,line,text from user_errors where name not like 'BIN$%';
