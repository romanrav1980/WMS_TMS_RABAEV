declare n number;begin
 select count(*)into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_STORE_RECEIPT_WEIGHT';if n!=12 then raise_application_error(-20886,'MANUAL_WEIGHT_AFTER_COLUMN_COUNT');end if;
 select count(*)into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_STORE_RECEIPT_WEIGHT'and COLUMN_NAME='CAPTURE_KEY'and NULLABLE='Y';if n!=1 then raise_application_error(-20886,'MANUAL_WEIGHT_AFTER_CAPTURE');end if;
 select count(*)into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_STORE_RECEIPT_WEIGHT'and COLUMN_NAME='MEASUREMENT_ORIGIN'and NULLABLE='N'and DATA_TYPE='VARCHAR2'and DATA_LENGTH=20;if n!=1 then raise_application_error(-20886,'MANUAL_WEIGHT_AFTER_ORIGIN');end if;
 select count(*)into n from USER_CONSTRAINTS where TABLE_NAME='RRL_STORE_RECEIPT_WEIGHT'and CONSTRAINT_NAME='RRL_STORE_WEIGHT_ORIGIN_CK'and STATUS='ENABLED'and VALIDATED='VALIDATED';if n!=1 then raise_application_error(-20886,'MANUAL_WEIGHT_AFTER_CONSTRAINT');end if;
end;
/
