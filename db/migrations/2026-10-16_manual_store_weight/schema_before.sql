declare n number;begin
 select count(*)into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_STORE_RECEIPT_WEIGHT';if n!=11 then raise_application_error(-20886,'MANUAL_WEIGHT_BEFORE_COLUMN_COUNT');end if;
 select count(*)into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_STORE_RECEIPT_WEIGHT'and COLUMN_NAME='CAPTURE_KEY'and NULLABLE='N'and DATA_TYPE='VARCHAR2'and DATA_LENGTH=64;if n!=1 then raise_application_error(-20886,'MANUAL_WEIGHT_BEFORE_CAPTURE');end if;
 select count(*)into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_STORE_RECEIPT_WEIGHT'and COLUMN_NAME='MEASUREMENT_ORIGIN';if n!=0 then raise_application_error(-20886,'MANUAL_WEIGHT_BEFORE_ORIGIN');end if;
end;
/
