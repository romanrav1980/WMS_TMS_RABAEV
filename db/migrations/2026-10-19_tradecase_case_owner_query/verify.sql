select NAME,LINE,TEXT from user_errors where NAME='RRL_TRADE_CASE_ACCESS';
select OBJECT_NAME from user_objects where STATUS='INVALID'and OBJECT_NAME not like'BIN$%';
