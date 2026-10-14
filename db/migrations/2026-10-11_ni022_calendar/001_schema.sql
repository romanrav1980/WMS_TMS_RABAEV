create table RRL_SAP_STORE_CAL_EXCEPTION(
 WARE_ID number not null,
 CUSTOMER_STORE_MAP_ID number not null references RRL_CUSTOMER_STORE_MAP(CUSTOMER_STORE_MAP_ID),
 DELIVERY_DATE date not null,VERSION_NO number not null,
 OPERATION_ID varchar2(100)not null unique,ACTOR varchar2(50)not null,
 REQUEST_HASH varchar2(64)not null,DAY_STATE varchar2(10)not null,
 SOURCE_REFERENCE nvarchar2(500)not null,REASON nvarchar2(500)not null,
 RESULT_JSON clob not null check(RESULT_JSON is json),
 CREATED_AT timestamp with time zone default systimestamp not null,
 constraint RRL_SAP_CAL_EX_PK primary key(WARE_ID,CUSTOMER_STORE_MAP_ID,DELIVERY_DATE,VERSION_NO),
 constraint RRL_SAP_CAL_EX_DATE_CK check(DELIVERY_DATE=trunc(DELIVERY_DATE)and VERSION_NO>0),
 constraint RRL_SAP_CAL_EX_STATE_CK check(DAY_STATE in('OPEN','CLOSED'))
);
/
alter table RRL_SAP_STORE_ORDER drop constraint RRL_SAP_STORE_ORDER_CK;
alter table RRL_SAP_STORE_ORDER add constraint RRL_SAP_STORE_ORDER_CK check(ADMISSION_STATUS in('ACCEPTED','PENDING_LATE','PENDING_CALENDAR','REJECTED'));
