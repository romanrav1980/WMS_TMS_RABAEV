declare n number;
begin
 select count(*)into n from USER_INDEXES where INDEX_NAME='RRL_RECEIPT_UNIT_PHYSICAL_UK';
 if n=0 then execute immediate 'create unique index RRL_RECEIPT_UNIT_PHYSICAL_UK on RRL_WMS_RECEIPT_UNIT(PHYSICAL_UNIT_KEY)';end if;
 select count(*)into n from USER_CONSTRAINTS where CONSTRAINT_NAME='RRL_RECEIPT_UNIT_KEY_UK';
 if n=0 then execute immediate 'alter table RRL_WMS_RECEIPT_UNIT add constraint RRL_RECEIPT_UNIT_KEY_UK unique(PHYSICAL_UNIT_KEY) using index RRL_RECEIPT_UNIT_PHYSICAL_UK';end if;
end;
/
create table RRL_STORE_RECEIPT_UNIT(
 OPERATION_ID varchar2(100)not null,
 LOAD_OPERATION_ID varchar2(100)not null,
 PHYSICAL_UNIT_KEY varchar2(64)not null,
 UNIT_DISPOSITION varchar2(20)not null,
 BASE_QTY number(27,9)not null,
 BASE_UOM varchar2(20)not null,
 SOURCE_UNIT_VERSION number not null,
 RECORDED_BY nvarchar2(50)not null,
 RECORDED_AT timestamp with time zone default systimestamp not null,
 constraint RRL_STORE_RUNIT_PK primary key(OPERATION_ID,PHYSICAL_UNIT_KEY),
 constraint RRL_STORE_RUNIT_SOURCE_UK unique(LOAD_OPERATION_ID,PHYSICAL_UNIT_KEY),
 constraint RRL_STORE_RUNIT_FACT_FK foreign key(OPERATION_ID)references RRL_STORE_RECEIPT_FACT(OPERATION_ID),
 constraint RRL_STORE_RUNIT_LOAD_FK foreign key(LOAD_OPERATION_ID)references RRL_TT_HU_LOAD_FACT(LOAD_OPERATION_ID),
 constraint RRL_STORE_RUNIT_UNIT_FK foreign key(PHYSICAL_UNIT_KEY)references RRL_WMS_RECEIPT_UNIT(PHYSICAL_UNIT_KEY),
 constraint RRL_STORE_RUNIT_STATE_CK check(UNIT_DISPOSITION in('ACCEPTED','MISSING','REFUSED','DAMAGED')),
 constraint RRL_STORE_RUNIT_QTY_CK check(BASE_QTY>0 and SOURCE_UNIT_VERSION>=0)
);
