create table RRL_TRADE_MARK_EVENT(
 WARE_ID number not null,SKM_ID varchar2(100) not null,EXTERNAL_EVENT_ID varchar2(100) not null,
 OPERATION_ID varchar2(100) not null,PAYLOAD_HASH varchar2(64) not null,
 BODY_JSON clob not null,CREATED_AT timestamp with time zone default systimestamp not null,
 constraint RRL_TRADE_MARK_EVENT_PK primary key(WARE_ID,SKM_ID,EXTERNAL_EVENT_ID),
 constraint RRL_TRADE_MARK_EVENT_SITE_FK foreign key(WARE_ID)references RRL_TRADE_SITE(WARE_ID),
 constraint RRL_TRADE_MARK_EVENT_JSON check(BODY_JSON is json)
);
