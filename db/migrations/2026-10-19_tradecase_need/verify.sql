select NAME,TYPE,LINE,TEXT from user_errors where NAME='RRL_TRADE_DOCUMENT_API';
select OBJECT_NAME from user_objects where STATUS='INVALID'and OBJECT_NAME not like'BIN$%';
select SEARCH_CONDITION from user_constraints where CONSTRAINT_NAME='RRL_TRADE_DOC_KIND';
