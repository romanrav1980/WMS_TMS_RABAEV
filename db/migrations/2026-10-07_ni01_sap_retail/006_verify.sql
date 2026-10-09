select column_name,data_length,nullable from user_tab_columns where (table_name='RRL_REG_OPERATION_JOURNAL' and column_name='SYSTEM_CODE') or (table_name='RRL_WMS_RECEIPT_CODE' and column_name='CANONICAL_CODE');
select index_name,status from user_indexes where index_name='RRL_WMS_REC_CODE_PAL_IX';
