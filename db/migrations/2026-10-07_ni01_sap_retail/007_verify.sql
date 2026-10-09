select column_name,data_type,nullable from user_tab_columns where table_name='RRL_WMS_RECEIPT_UNIT' and column_name='BASE_QTY';
select constraint_name,status from user_constraints where constraint_name='RRL_WMS_REC_UNIT_QTY_CK';
