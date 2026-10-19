create table RRL_TRADE_TRIP_LINK(
 WARE_ID number not null,TRIP_ID varchar2(100)not null,TRIP_VERSION number not null,NATIVE_TASK_ID number not null,
 VERSION_NO number not null,SOURCE_ID varchar2(100)not null,REQUEST_HASH varchar2(64)not null,RESULT_JSON clob not null,
 constraint RRL_TRADE_TRIP_LINK_PK primary key(WARE_ID,TRIP_ID),constraint RRL_TRADE_TRIP_NATIVE_UK unique(WARE_ID,NATIVE_TASK_ID),
 constraint RRL_TRADE_TRIP_SITE_FK foreign key(WARE_ID)references RRL_TRADE_SITE(WARE_ID),constraint RRL_TRADE_TRIP_TT_FK foreign key(NATIVE_TASK_ID)references RRL_TRANSPORT_TASK(ID),
 constraint RRL_TRADE_TRIP_LINK_JSON check(RESULT_JSON is json)
);
create table RRL_TRADE_TRIP_DOC_EVENT(
 WARE_ID number not null,SOURCE_ID varchar2(100)not null,EVENT_ID varchar2(100)not null,TRIP_ID varchar2(100)not null,
 TRIP_VERSION number not null,BINDING_VERSION number not null,DOCUMENT_VERSION number not null,DOCUMENT_STATUS varchar2(10)not null,
 EXTERNAL_DOCUMENT_ID varchar2(100),MANIFEST_SIGNATURE varchar2(64)not null,ERROR_REASON varchar2(2000),REQUEST_HASH varchar2(64)not null,
 REQUEST_JSON clob not null,RESULT_JSON clob not null,CREATED_AT timestamp with time zone default systimestamp not null,
 constraint RRL_TRADE_TD_EVENT_PK primary key(WARE_ID,SOURCE_ID,EVENT_ID),constraint RRL_TRADE_TD_PARENT_FK foreign key(WARE_ID,TRIP_ID)references RRL_TRADE_TRIP_LINK(WARE_ID,TRIP_ID),
 constraint RRL_TRADE_TD_VERSION_UK unique(WARE_ID,TRIP_ID,DOCUMENT_VERSION),constraint RRL_TRADE_TD_STATUS check(DOCUMENT_STATUS in('READY','ERROR','REVOKED')),
 constraint RRL_TRADE_TD_DOC_REQUIRED check(DOCUMENT_STATUS<>'READY'or EXTERNAL_DOCUMENT_ID is not null),
 constraint RRL_TRADE_TD_REQUEST_JSON check(REQUEST_JSON is json),constraint RRL_TRADE_TD_RESULT_JSON check(RESULT_JSON is json)
);
