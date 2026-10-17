create table RRL_HU_CONSOL_PLAN(
 PLAN_ID varchar2(100)not null,ROOT_UID varchar2(200)not null,TARGET_WARE_ID number not null,TARGET_CELL varchar2(60)not null,
 STATUS varchar2(12)not null,PLAN_VERSION number not null,REASON varchar2(1000 char)not null,
 CREATED_BY nvarchar2(50)not null,CREATED_AT timestamp with time zone default systimestamp not null,
 UPDATED_BY nvarchar2(50)not null,UPDATED_AT timestamp with time zone default systimestamp not null,
 constraint RRL_HU_CONSOL_PLAN_PK primary key(PLAN_ID),
 constraint RRL_HU_CONSOL_PLAN_CK check(STATUS in('ACTIVE','CANCELLED')and PLAN_VERSION>=1 and PLAN_VERSION=trunc(PLAN_VERSION))
);
create unique index RRL_HU_CONSOL_ROOT_U1 on RRL_HU_CONSOL_PLAN(case when STATUS='ACTIVE'then ROOT_UID end);
create table RRL_HU_CONSOL_MEMBER(
 PLAN_ID varchar2(100)not null,FULFILLMENT_ID number not null,EXPECTED_ST_ID number not null,
 EXPECTED_PALLET_UID varchar2(200)not null,SOURCE_WARE_ID number not null,ROWS_SIGNATURE varchar2(64)not null,
 constraint RRL_HU_CONSOL_MEMBER_PK primary key(PLAN_ID,FULFILLMENT_ID),
 constraint RRL_HU_CONSOL_MEMBER_ST_U1 unique(PLAN_ID,EXPECTED_ST_ID),
 constraint RRL_HU_CONSOL_MEMBER_FK foreign key(PLAN_ID)references RRL_HU_CONSOL_PLAN(PLAN_ID),
 constraint RRL_HU_CONSOL_MEMBER_FF_FK foreign key(FULFILLMENT_ID)references RRL_CUSTOMER_ORDER_FULFILLMENT(FULFILLMENT_ID)
);
create table RRL_HU_CONSOL_RECEIPT(
 OPERATION_ID varchar2(100)not null,PLAN_ID varchar2(100)not null,ACTOR nvarchar2(50)not null,
 REQUEST_HASH varchar2(64)not null,REQUEST_JSON clob not null,FROZEN_PLAN_JSON clob not null,RESULT_JSON clob not null,
 CREATED_AT timestamp with time zone default systimestamp not null,
 constraint RRL_HU_CONSOL_RECEIPT_PK primary key(OPERATION_ID),
 constraint RRL_HU_CONSOL_RECEIPT_FK foreign key(PLAN_ID)references RRL_HU_CONSOL_PLAN(PLAN_ID)
);

