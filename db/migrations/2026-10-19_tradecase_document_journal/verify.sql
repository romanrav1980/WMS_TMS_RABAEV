select name,type,line,text from user_errors where name='RRL_TRADE_DOCUMENT_API';
select count(*) current_invalid from user_objects where status='INVALID' and object_name not like 'BIN$%';
