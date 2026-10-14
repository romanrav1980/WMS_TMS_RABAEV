declare n number;
begin
 select count(*) into n from user_tables where table_name='RRL_TT_LOAD_BOX_WEIGHT';
 if n=0 then execute immediate 'create table RRL_TT_LOAD_BOX_WEIGHT(
 LOAD_OPERATION_ID varchar2(100) not null references RRL_TT_HU_LOAD_FACT(LOAD_OPERATION_ID),
 BOX_UID varchar2(200) not null references RRL_PALLETS(UID_PALLET),
 BOX_CONTENT_VERSION number(19) not null,GROSS_WEIGHT_KG number(27,9) not null check(GROSS_WEIGHT_KG>0),
 MEASUREMENT_ORIGIN varchar2(30) not null check(MEASUREMENT_ORIGIN=''MANUAL_CONFIRMED''),
 MEASUREMENT_REF varchar2(100) not null,SCAN_IDENTIFIER varchar2(200) not null,
 RECORDED_BY varchar2(50) not null,RECORDED_AT timestamp with time zone default systimestamp not null,
 primary key(LOAD_OPERATION_ID,BOX_UID))';end if;
end;
/
