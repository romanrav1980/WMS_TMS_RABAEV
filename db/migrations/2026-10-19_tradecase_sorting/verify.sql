select object_name,object_type,status from user_objects where status<>'VALID' and object_name not like 'BIN$%';
select name,line,position,text from user_errors where name in('RRL_TRADE_SORT_GUARD','RRL_STOCK_INTERNAL_CMD','RRL_STOCK_POSTING_API');
