create sequence RRL_TRADE_TOPUP_PROPOSAL_SQ start with 1 increment by 1 nocache;
create table RRL_TRADE_TOPUP_PROPOSAL(
 PROPOSAL_ID number not null,WARE_ID number not null,TRIP_ID varchar2(100)not null,TRIP_VERSION number not null,
 NEED_ID varchar2(100)not null,NEED_VERSION number not null,NEED_SIGNATURE varchar2(64)not null,NEED_SNAPSHOT_AT timestamp with time zone not null,
 MAX_AGE_MINUTES number not null,PRIORITY number not null,RECIPIENT_ID varchar2(100)not null,SKU_ID varchar2(100)not null,ARTICLE varchar2(160)not null,
 UNITS_PER_BOX number not null,SOURCE_OWNER_ID varchar2(100)not null,TARGET_OWNER_ID varchar2(100)not null,MRC number(12,2)not null,MIN_EXPIRY date not null,
 NEED_BOXES number not null,PROPOSED_BOXES number not null,APPROVED_BOXES number not null,CAPACITY_BASIS varchar2(64)not null,
 CALC_SIGNATURE varchar2(64)not null,CALC_JSON clob not null,STATUS varchar2(20)not null,VERSION_NO number not null,
 SAP_ORDER_ID varchar2(100),SAP_REASON varchar2(2000),REQUEST_OUTBOX_ID number,CONFIRM_OPERATION_ID varchar2(100),
 CREATED_BY varchar2(50)not null,CREATED_AT timestamp with time zone default systimestamp not null,
 UPDATED_BY varchar2(50)not null,UPDATED_AT timestamp with time zone default systimestamp not null,
 constraint RRL_TRADE_TOPUP_PK primary key(PROPOSAL_ID),
 constraint RRL_TRADE_TOPUP_SITE_FK foreign key(WARE_ID)references RRL_TRADE_SITE(WARE_ID),
 constraint RRL_TRADE_TOPUP_STATUS check(STATUS in('PROPOSED','ADJUSTED','REJECTED','SUPERSEDED','CONFIRMED','SAP_ACCEPTED','SAP_REJECTED','CANCELLED')),
 constraint RRL_TRADE_TOPUP_QTY check(NEED_BOXES>=0 and PROPOSED_BOXES>=0 and APPROVED_BOXES>=0 and APPROVED_BOXES<=PROPOSED_BOXES
  and APPROVED_BOXES=trunc(APPROVED_BOXES)and PROPOSED_BOXES=trunc(PROPOSED_BOXES)and UNITS_PER_BOX>0 and UNITS_PER_BOX=trunc(UNITS_PER_BOX)),
 constraint RRL_TRADE_TOPUP_CONFIRMED_QTY check(STATUS not in('CONFIRMED','SAP_ACCEPTED')or APPROVED_BOXES>0),
 constraint RRL_TRADE_TOPUP_AGE check(MAX_AGE_MINUTES between 1 and 1440),
 constraint RRL_TRADE_TOPUP_VER check(VERSION_NO>0 and VERSION_NO=trunc(VERSION_NO)),
 constraint RRL_TRADE_TOPUP_JSON check(CALC_JSON is json),
 constraint RRL_TRADE_TOPUP_SAP_ORDER check(STATUS<>'SAP_ACCEPTED'or SAP_ORDER_ID is not null),
 constraint RRL_TRADE_TOPUP_SAP_ORDER_UK unique(WARE_ID,SAP_ORDER_ID)
);
create index RRL_TRADE_TOPUP_TRIP_IX on RRL_TRADE_TOPUP_PROPOSAL(WARE_ID,TRIP_ID,STATUS);
create index RRL_TRADE_TOPUP_NEED_IX on RRL_TRADE_TOPUP_PROPOSAL(WARE_ID,NEED_ID,STATUS);
-- One open (undecided) proposal per trip and demand: a repeated calculation reuses or supersedes it, never duplicates.
create unique index RRL_TRADE_TOPUP_OPEN_UK on RRL_TRADE_TOPUP_PROPOSAL(case when STATUS in('PROPOSED','ADJUSTED')then WARE_ID end,
 case when STATUS in('PROPOSED','ADJUSTED')then TRIP_ID end,case when STATUS in('PROPOSED','ADJUSTED')then NEED_ID end);
create table RRL_TRADE_TOPUP_DECISION(
 OPERATION_ID varchar2(100)not null,WARE_ID number not null,PROPOSAL_ID number,ACTION varchar2(20)not null,BOXES number,
 REQUEST_HASH varchar2(64)not null,ACTOR varchar2(50)not null,RESULT_JSON clob not null,
 CREATED_AT timestamp with time zone default systimestamp not null,
 constraint RRL_TRADE_TOPUP_DEC_PK primary key(OPERATION_ID),
 constraint RRL_TRADE_TOPUP_DEC_PROP_FK foreign key(PROPOSAL_ID)references RRL_TRADE_TOPUP_PROPOSAL(PROPOSAL_ID),
 constraint RRL_TRADE_TOPUP_DEC_ACTION check(ACTION in('SAVE','ADJUST','REJECT','CONFIRM','RELEASE','SAP_ACCEPT','SAP_REJECT')),
 constraint RRL_TRADE_TOPUP_DEC_JSON check(RESULT_JSON is json)
);
create index RRL_TRADE_TOPUP_DEC_PROP_IX on RRL_TRADE_TOPUP_DECISION(PROPOSAL_ID,CREATED_AT);
create table RRL_TRADE_TOPUP_HOLD(
 RESERVATION_ID number not null,PROPOSAL_ID number not null,UID_PALLET varchar2(200)not null,CELL varchar2(60)not null,
 BASE_QTY number not null,STATUS varchar2(12)not null,CREATED_OPERATION_ID varchar2(100)not null,RELEASED_OPERATION_ID varchar2(100),
 constraint RRL_TRADE_TOPUP_HOLD_PK primary key(RESERVATION_ID),
 constraint RRL_TRADE_TOPUP_HOLD_PROP_FK foreign key(PROPOSAL_ID)references RRL_TRADE_TOPUP_PROPOSAL(PROPOSAL_ID),
 constraint RRL_TRADE_TOPUP_HOLD_RES_FK foreign key(RESERVATION_ID)references RRL_STOCK_RESERVATION(RESERVATION_ID),
 constraint RRL_TRADE_TOPUP_HOLD_STATUS check(STATUS in('ACTIVE','RELEASED','ADOPTED')),
 constraint RRL_TRADE_TOPUP_HOLD_QTY check(BASE_QTY>0),
 constraint RRL_TRADE_TOPUP_HOLD_REL check((STATUS='ACTIVE'and RELEASED_OPERATION_ID is null)or(STATUS<>'ACTIVE'and RELEASED_OPERATION_ID is not null))
);
create index RRL_TRADE_TOPUP_HOLD_PROP_IX on RRL_TRADE_TOPUP_HOLD(PROPOSAL_ID,STATUS);
create table RRL_TRADE_TOPUP_EVENT(
 WARE_ID number not null,SOURCE_ID varchar2(100)not null,EVENT_ID varchar2(100)not null,PROPOSAL_ID number not null,
 PAYLOAD_HASH varchar2(64)not null,BODY_JSON clob not null,RESULT_JSON clob not null,
 CREATED_AT timestamp with time zone default systimestamp not null,
 constraint RRL_TRADE_TOPUP_EVENT_PK primary key(WARE_ID,SOURCE_ID,EVENT_ID),
 constraint RRL_TRADE_TOPUP_EVENT_PROP_FK foreign key(PROPOSAL_ID)references RRL_TRADE_TOPUP_PROPOSAL(PROPOSAL_ID),
 constraint RRL_TRADE_TOPUP_EVENT_BODY check(BODY_JSON is json),constraint RRL_TRADE_TOPUP_EVENT_RESULT check(RESULT_JSON is json)
);
