create table RRL_TRADE_BUYOUT(
 BUYOUT_ID varchar2(100)not null,WARE_ID number not null,SKU_ID varchar2(100)not null,MRC number(12,2)not null,
 SOURCE_OWNER_ID varchar2(100)not null,TARGET_OWNER_ID varchar2(100)not null,
 BASIS_ORDER_ID varchar2(100)not null,BASIS_LINE_ID varchar2(100)not null,BASIS_VERSION number not null,
 BUYOUT_MODE varchar2(20)not null,DEMAND_ORDER_ID varchar2(100),DEMAND_LINE_ID varchar2(100),LOAD_OPERATION_ID varchar2(100),
 SKM_ID varchar2(100)not null,SITE_VERSION number not null,EXTERNAL_DOCUMENT_ID varchar2(100),
 STATUS varchar2(20)not null,VERSION_NO number not null,REQUESTED_UNITS number not null,CONFIRMED_UNITS number default 0 not null,
 REJECTED_UNITS number default 0 not null,PENDING_UNITS number not null,REQUIRES_SORTING number default 0 not null,
 REQUEST_JOURNAL_ID number,REQUEST_HASH varchar2(64)not null,REQUEST_JSON clob not null,REQUEST_RESULT clob,
 CREATED_BY varchar2(50)not null,CREATED_AT timestamp with time zone default systimestamp not null,
 UPDATED_AT timestamp with time zone default systimestamp not null,
 constraint RRL_TRADE_BUYOUT_PK primary key(BUYOUT_ID),
 constraint RRL_TRADE_BUYOUT_SITE_FK foreign key(WARE_ID)references RRL_TRADE_SITE(WARE_ID),
 constraint RRL_TRADE_BUYOUT_MODE check(BUYOUT_MODE in('BEFORE_PICK','AFTER_PICK','IN_TRANSIT')),
 constraint RRL_TRADE_BUYOUT_STATUS check(STATUS in('PENDING','PARTIAL_PENDING','CONFIRMED','PARTIAL','REJECTED')),
 constraint RRL_TRADE_BUYOUT_COUNTS check(REQUESTED_UNITS>0 and CONFIRMED_UNITS>=0 and REJECTED_UNITS>=0 and PENDING_UNITS>=0 and REQUESTED_UNITS=CONFIRMED_UNITS+REJECTED_UNITS+PENDING_UNITS),
 constraint RRL_TRADE_BUYOUT_JSON check(REQUEST_JSON is json),
 constraint RRL_TRADE_BUYOUT_EXT_UK unique(WARE_ID,SKM_ID,EXTERNAL_DOCUMENT_ID)
);
create index RRL_TRADE_BUYOUT_BASIS_IX on RRL_TRADE_BUYOUT(WARE_ID,BASIS_ORDER_ID,BASIS_LINE_ID);
create index RRL_TRADE_BO_QUEUE_IX on RRL_TRADE_BUYOUT(WARE_ID,REQUEST_JOURNAL_ID);
create table RRL_TRADE_BUYOUT_UNIT(
 BUYOUT_ID varchar2(100)not null,PHYSICAL_UNIT_KEY varchar2(64)not null,INITIAL_ATTRIBUTE_VERSION number not null,
 INITIAL_UID varchar2(200)not null,INITIAL_CELL varchar2(60),OUTCOME varchar2(12)default 'PENDING'not null,
 HOLD_ACTIVE number(1)default 1 not null,EXTERNAL_REASON varchar2(2000),
 constraint RRL_TRADE_BUYOUT_UNIT_PK primary key(BUYOUT_ID,PHYSICAL_UNIT_KEY),
 constraint RRL_TRADE_BO_UNIT_PARENT_FK foreign key(BUYOUT_ID)references RRL_TRADE_BUYOUT(BUYOUT_ID),
 constraint RRL_TRADE_BO_UNIT_STOCK_FK foreign key(PHYSICAL_UNIT_KEY)references RRL_TRADE_STOCK_ATTR(PHYSICAL_UNIT_KEY),
 constraint RRL_TRADE_BO_UNIT_OUTCOME check(OUTCOME in('PENDING','CONFIRMED','REJECTED')),
 constraint RRL_TRADE_BO_UNIT_HOLD check((OUTCOME='PENDING'and HOLD_ACTIVE=1)or(OUTCOME in('CONFIRMED','REJECTED')and HOLD_ACTIVE=0))
);
create unique index RRL_TRADE_BO_ACTIVE_UNIT_UK on RRL_TRADE_BUYOUT_UNIT(case when HOLD_ACTIVE=1 then PHYSICAL_UNIT_KEY end);
create table RRL_TRADE_BUYOUT_EVENT(
 WARE_ID number not null,SKM_ID varchar2(100)not null,EVENT_ID varchar2(100)not null,BUYOUT_ID varchar2(100)not null,
 PAYLOAD_HASH varchar2(64)not null,BODY_JSON clob not null,RESULT_JSON clob not null,
 CREATED_AT timestamp with time zone default systimestamp not null,
 constraint RRL_TRADE_BO_EVENT_PK primary key(WARE_ID,SKM_ID,EVENT_ID),
 constraint RRL_TRADE_BO_EVENT_PARENT_FK foreign key(BUYOUT_ID)references RRL_TRADE_BUYOUT(BUYOUT_ID),
 constraint RRL_TRADE_BO_EVENT_BODY check(BODY_JSON is json),constraint RRL_TRADE_BO_EVENT_RESULT check(RESULT_JSON is json)
);
