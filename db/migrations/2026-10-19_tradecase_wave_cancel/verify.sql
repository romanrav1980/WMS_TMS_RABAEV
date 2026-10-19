select name,type,line,text from user_errors where NAME='RRL_TRADE_STOCK_GUARD';
select object_name from user_objects where status='INVALID'and object_name not like'BIN$%';
