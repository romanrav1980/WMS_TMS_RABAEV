create table RRL_TRADE_DEFERRED (
 WARE_ID number not null,SOURCE_ID varchar2(100) not null,EVENT_ID varchar2(100) not null,
 STATE varchar2(12) default 'WAITING' not null,ATTEMPTS number default 0 not null,
 RESULT_JSON clob not null,CHANGED_BY varchar2(50) not null,
 CHANGED_AT timestamp with time zone default systimestamp not null,
 constraint RRL_TRADE_DEFERRED_PK primary key(WARE_ID,SOURCE_ID,EVENT_ID),
 constraint RRL_TRADE_DEFERRED_FK foreign key(WARE_ID,SOURCE_ID,EVENT_ID)
  references RRL_TRADE_MESSAGE(WARE_ID,SOURCE_ID,EVENT_ID),
 constraint RRL_TRADE_DEFERRED_STATE check(STATE in('WAITING','ACCEPTED','REJECTED')),
 constraint RRL_TRADE_DEFERRED_JSON check(RESULT_JSON is json),
 constraint RRL_TRADE_DEFERRED_ATT check(ATTEMPTS>=0 and ATTEMPTS=trunc(ATTEMPTS))
);
