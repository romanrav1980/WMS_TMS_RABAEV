select constraint_name,status from user_constraints where constraint_name='RRL_UNIT_BOX_MEASURES_CK';
select column_name,data_type from user_tab_columns where table_name='RRL_WMS_RECEIPT_UNIT'and column_name in('GROSS_WEIGHT_KG','BOX_VOLUME_M3','MEASUREMENT_REFERENCE','WEIGHT_LABEL_SCAN');
