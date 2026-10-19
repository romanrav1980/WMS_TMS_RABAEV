select name,type,line,position,text from user_errors where name like 'RRL_TRADE%' or name in('RRL_STOCK_POSTING_API','RRL_STOCK_INVARIANT_CORE','RRL_STOCK_ELIGIBILITY');
select object_name,object_type from user_objects where status='INVALID' and object_name not like 'BIN$%';
