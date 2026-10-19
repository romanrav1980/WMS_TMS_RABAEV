create table RRL_TRADE_SITE (
 WARE_ID number not null references RRL_WARES(ID), SOURCE_ID varchar2(100) not null,
 ACTIVE_SKM varchar2(100) not null, PLANNING_SOURCE varchar2(12) not null,
 ENABLED number(1) not null, VERSION_NO number not null, REASON varchar2(2000) not null,
 CHANGED_BY varchar2(50) not null, CHANGED_AT timestamp with time zone default systimestamp not null,
 constraint RRL_TRADE_SITE_PK primary key(WARE_ID),
 constraint RRL_TRADE_SITE_MODE check(PLANNING_SOURCE in('SAP','INTERNAL')),
 constraint RRL_TRADE_SITE_ON check(ENABLED in(0,1)),
 constraint RRL_TRADE_SITE_VER check(VERSION_NO>=0 and VERSION_NO=trunc(VERSION_NO))
);
create table RRL_TRADE_DOCUMENT (
 WARE_ID number not null references RRL_TRADE_SITE(WARE_ID), ENTITY_TYPE varchar2(12) not null,
 EXTERNAL_ID varchar2(100) not null, SOURCE_ID varchar2(100) not null, VERSION_NO number not null,
 CONTENT_HASH varchar2(64) not null, BODY_JSON clob not null, STATUS varchar2(12) not null,
 FIRST_SCAN_AT timestamp with time zone, CHANGED_BY varchar2(50) not null,
 CHANGED_AT timestamp with time zone default systimestamp not null,
 constraint RRL_TRADE_DOC_PK primary key(WARE_ID,ENTITY_TYPE,EXTERNAL_ID),
 constraint RRL_TRADE_DOC_KIND check(ENTITY_TYPE in('OWNER','SKU','RECIPIENT','ORDER','TRIP')),
 constraint RRL_TRADE_DOC_JSON check(BODY_JSON is json),
 constraint RRL_TRADE_DOC_STATUS check(STATUS in('ACCEPTED','CANCELLED')),
 constraint RRL_TRADE_DOC_VER check(VERSION_NO>0 and VERSION_NO=trunc(VERSION_NO))
);
create table RRL_TRADE_MESSAGE (
 WARE_ID number not null references RRL_TRADE_SITE(WARE_ID), SOURCE_ID varchar2(100) not null,
 EVENT_ID varchar2(100) not null, ENTITY_TYPE varchar2(12) not null, EXTERNAL_ID varchar2(100) not null,
 VERSION_NO number not null, PAYLOAD_HASH varchar2(64) not null, BUSINESS_HASH varchar2(64) not null,
 REQUEST_JSON clob not null, RESULT_JSON clob not null, ACTOR varchar2(50) not null,
 CREATED_AT timestamp with time zone default systimestamp not null,
 constraint RRL_TRADE_MSG_PK primary key(WARE_ID,SOURCE_ID,EVENT_ID),
 constraint RRL_TRADE_MSG_REQ check(REQUEST_JSON is json),
 constraint RRL_TRADE_MSG_RESULT check(RESULT_JSON is json)
);
create index RRL_TRADE_MSG_DOC_IX on RRL_TRADE_MESSAGE(WARE_ID,ENTITY_TYPE,EXTERNAL_ID,VERSION_NO);