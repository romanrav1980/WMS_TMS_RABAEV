select INDEX_NAME,UNIQUENESS,STATUS from user_indexes where INDEX_NAME in('RRL_TRADE_BUYOUT_EXT_UK','RRL_TRADE_BUYOUT_DOC_UK');
select object_name,object_type from user_objects where status='INVALID'and object_name not like'BIN$%';
