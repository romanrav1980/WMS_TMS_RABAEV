select object_name,object_type,status from user_objects where object_name in('RRL_STORE_LOAD_CUSTODY','RRL_STOCK_STORE_CUSTODY_CMD','RRL_STOCK_STORE_RECEIPT_CMD','RRL_STOCK_POSTING_API');
select operation_id,receipt_operation_id,load_operation_id from RRL_STORE_LOAD_CUSTODY order by released_at;
select name,type,line,text from user_errors where name not like 'BIN$%';
