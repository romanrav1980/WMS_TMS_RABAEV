create sequence RRL_TRADE_QUALITY_CASE_SQ start with 1 increment by 1 nocache;
-- Process record of one quarantined pallet: the controller decides DEFECT or RELEASED, management approves the write-off of a DEFECT.
-- Not a second ledger: quantities and owners stay in RRL_REMAINS / RRL_WMS_RECEIPT_UNIT / RRL_TRADE_STOCK_ATTR; the hold itself is the
-- existing RRL_QUALITY_HOLD (RRL_TRACEABILITY_API). No stock is written off here: an approved write-off WAITS for a native posting owner.
create table RRL_TRADE_QUALITY_CASE(
 CASE_ID number not null,WARE_ID number not null,PALLET_UID varchar2(200)not null,CELL varchar2(60)not null,
 QUALITY_HOLD_ID number not null,STATE varchar2(16)not null,VERSION_NO number not null,STOCK_VERSION number not null,
 COMPOSITION_HASH varchar2(64)not null,REASON_TEXT varchar2(1000)not null,DECISION_TEXT varchar2(1000),APPROVAL_TEXT varchar2(1000),
 OPENED_BY varchar2(50)not null,OPENED_AT timestamp with time zone not null,
 DECIDED_BY varchar2(50),DECIDED_AT timestamp with time zone,APPROVED_BY varchar2(50),APPROVED_AT timestamp with time zone,
 constraint RRL_TRADE_QUALITY_CASE_PK primary key(CASE_ID),
 constraint RRL_TRADE_QUALITY_CASE_SITE_FK foreign key(WARE_ID)references RRL_TRADE_SITE(WARE_ID),
 constraint RRL_TRADE_QUALITY_CASE_HOLD_FK foreign key(QUALITY_HOLD_ID)references RRL_QUALITY_HOLD(QUALITY_HOLD_ID),
 constraint RRL_TRADE_QUALITY_CASE_STATE check(STATE in('OPEN','DEFECT','RELEASED','WAITING_POSTING')),
 constraint RRL_TRADE_QUALITY_CASE_VER check(VERSION_NO>0 and VERSION_NO=trunc(VERSION_NO)),
 -- Each state carries the fact that produced it.
 constraint RRL_TRADE_QUALITY_CASE_FACTS check((STATE='OPEN'and DECIDED_AT is null and APPROVED_AT is null)
  or(STATE in('DEFECT','RELEASED')and DECIDED_AT is not null and DECIDED_BY is not null and APPROVED_AT is null)
  or(STATE='WAITING_POSTING'and DECIDED_AT is not null and APPROVED_AT is not null and APPROVED_BY is not null))
);
-- One active case per pallet (a released pallet may get a new case later).
create unique index RRL_TRADE_QUALITY_CASE_ACTIVE_UK on RRL_TRADE_QUALITY_CASE(case when STATE<>'RELEASED'then PALLET_UID end);
create index RRL_TRADE_QUALITY_CASE_WARE_IX on RRL_TRADE_QUALITY_CASE(WARE_ID,STATE,CASE_ID);
-- Frozen code composition at opening: physical unit keys and their versions only (no quantity copy).
create table RRL_TRADE_QUALITY_CASE_UNIT(
 CASE_ID number not null,PHYSICAL_UNIT_KEY varchar2(200)not null,UNIT_VERSION number not null,
 constraint RRL_TRADE_QUALITY_CASE_UNIT_PK primary key(CASE_ID,PHYSICAL_UNIT_KEY),
 constraint RRL_TRADE_QUALITY_CASE_UNIT_FK foreign key(CASE_ID)references RRL_TRADE_QUALITY_CASE(CASE_ID)
);
create table RRL_TRADE_QUALITY_CASE_EVENT(
 OPERATION_ID varchar2(100)not null,WARE_ID number not null,CASE_ID number not null,ACTION varchar2(12)not null,
 FROM_STATE varchar2(16),TO_STATE varchar2(16)not null,REQUEST_HASH varchar2(64)not null,ACTOR varchar2(50)not null,
 EVENT_AT timestamp with time zone not null,RESULT_JSON clob not null,
 constraint RRL_TRADE_QUALITY_CASE_EVENT_PK primary key(OPERATION_ID),
 constraint RRL_TRADE_QUALITY_CASE_EVENT_FK foreign key(CASE_ID)references RRL_TRADE_QUALITY_CASE(CASE_ID),
 constraint RRL_TRADE_QUALITY_CASE_EVENT_ACTION check(ACTION in('OPEN','DECIDE','APPROVE')),
 constraint RRL_TRADE_QUALITY_CASE_EVENT_JSON check(RESULT_JSON is json)
);
create index RRL_TRADE_QUALITY_CASE_EVENT_CASE_IX on RRL_TRADE_QUALITY_CASE_EVENT(CASE_ID,EVENT_AT);
-- Composition and history are evidence: never rewritten or removed.
create or replace trigger RRL_TRADE_QUALITY_CASE_EVENT_APPEND before update or delete on RRL_TRADE_QUALITY_CASE_EVENT
begin raise_application_error(-20911,'QUALITY_EVENT_APPEND_ONLY');end;
/
create or replace trigger RRL_TRADE_QUALITY_CASE_UNIT_FROZEN before update or delete on RRL_TRADE_QUALITY_CASE_UNIT
begin raise_application_error(-20911,'QUALITY_COMPOSITION_FROZEN');end;
/
