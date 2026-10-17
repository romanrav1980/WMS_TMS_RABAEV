create table RRL_IW_CASE_CARRIER(
 CARRIER_UID varchar2(200) primary key,
 CASE_TASK_ID number not null unique references RRL_CASE_PICK_TASK(CASE_PICK_TASK_ID),
 SOURCE_LOAD_OPERATION_ID varchar2(100) not null references RRL_TT_HU_LOAD_FACT(LOAD_OPERATION_ID),
 RECEIPT_OPERATION_ID varchar2(100) not null references RRL_IW_GROUP_RECEIPT(OPERATION_ID),
 SOURCE_WARE_ID number not null,
 TARGET_WARE_ID number not null,
 PALLET_IDENTIFIER varchar2(64) not null,
 SOURCE_CASE_VERSION number not null,
 SOURCE_JSON clob not null check(SOURCE_JSON is json),
 CREATED_BY nvarchar2(128) not null,
 CREATED_AT timestamp with time zone default systimestamp not null,
 constraint RRL_IW_CASE_CURRENT_HU_FK foreign key(CARRIER_UID)references RRL_PALLETS(UID_PALLET),
 constraint RRL_IW_CASE_WARE_DIFF check(SOURCE_WARE_ID!=TARGET_WARE_ID)
);
create index RRL_IW_CASE_RECEIPT_IX on RRL_IW_CASE_CARRIER(RECEIPT_OPERATION_ID);
alter table RRL_IW_GROUP_RECEIPT_LINE drop constraint RRL_IW_GROUP_REC_ST_UQ;
create index RRL_IW_GREC_SOURCE_ST_IX on RRL_IW_GROUP_RECEIPT_LINE(OPERATION_ID,ST_ID);
