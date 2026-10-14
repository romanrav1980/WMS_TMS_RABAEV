declare n number;
begin
 select count(*) into n from user_tables where table_name='RRL_STORE_RECEIPT_WEIGHT';
 if n=0 then execute immediate 'create table RRL_STORE_RECEIPT_WEIGHT(
 OPERATION_ID varchar2(100) primary key references RRL_STORE_RECEIPT_FACT(OPERATION_ID),
 CAPTURE_KEY varchar2(64) not null references RRL_STORE_SCALE_CAPTURE(CAPTURE_KEY),
 SHIPPING_GROSS_KG number(27,9) not null,OBSERVED_GROSS_KG number(27,9) not null,
 TOLERANCE_KG number(28,10) not null check(TOLERANCE_KG>0),DELTA_KG number(27,9) not null,
 IN_TOLERANCE number(1) not null check(IN_TOLERANCE in(0,1)),ACT_CONFIRMED number(1) not null check(ACT_CONFIRMED in(0,1)),
 PHOTOS_JSON clob not null check(PHOTOS_JSON is json),RECORDED_BY varchar2(50) not null,
 RECORDED_AT timestamp with time zone default systimestamp not null)';end if;
 select count(*) into n from user_tables where table_name='RRL_STORE_RECEIPT_WEIGHT_PHOTO';
 if n=0 then execute immediate 'create table RRL_STORE_RECEIPT_WEIGHT_PHOTO(
 OPERATION_ID varchar2(100) not null references RRL_STORE_RECEIPT_WEIGHT(OPERATION_ID),
 PHOTO_ID varchar2(64) not null references RRL_STORE_RECEIPT_PHOTO(PHOTO_ID),
 primary key(OPERATION_ID,PHOTO_ID))';end if;
end;
/
