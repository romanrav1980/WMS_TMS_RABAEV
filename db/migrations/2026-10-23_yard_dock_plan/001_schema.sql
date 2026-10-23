-- C-0158: planned interval [PLANNED_FROM,PLANNED_TO) of one dock for one yard visit. A plan is neither a fact nor a guarantee of a free
-- dock: arrival/dock/work facts and real occupancy stay in RRL_YARD_VISIT. One ACTIVE plan per visit; history in the append-only events.
create sequence RRL_YARD_DOCK_PLAN_SQ;
create table RRL_YARD_DOCK_PLAN(
 PLAN_ID number not null,WARE_ID number not null,VISIT_ID number not null,DOCK varchar2(50)not null,
 PLANNED_FROM timestamp with time zone not null,PLANNED_TO timestamp with time zone not null,
 STATUS varchar2(12)not null,VERSION_NO number not null,CANCEL_REASON varchar2(500),
 CREATED_BY varchar2(50)not null,CREATED_AT timestamp with time zone default systimestamp not null,
 UPDATED_BY varchar2(50)not null,UPDATED_AT timestamp with time zone not null,
 constraint RRL_YARD_DOCK_PLAN_PK primary key(PLAN_ID),
 constraint RRL_YARD_DOCK_PLAN_VISIT_FK foreign key(VISIT_ID)references RRL_YARD_VISIT(VISIT_ID),
 constraint RRL_YARD_DOCK_PLAN_STATUS check(STATUS in('ACTIVE','CANCELLED')),
 constraint RRL_YARD_DOCK_PLAN_RANGE check(PLANNED_TO>PLANNED_FROM),
 constraint RRL_YARD_DOCK_PLAN_VERSION check(VERSION_NO>0 and VERSION_NO=trunc(VERSION_NO)),
 constraint RRL_YARD_DOCK_PLAN_REASON check(STATUS='ACTIVE'and CANCEL_REASON is null or STATUS='CANCELLED'and CANCEL_REASON is not null)
);
create unique index RRL_YARD_DOCK_PLAN_VISIT_UK on RRL_YARD_DOCK_PLAN(case when STATUS='ACTIVE'then VISIT_ID end);
create index RRL_YARD_DOCK_PLAN_DOCK_IX on RRL_YARD_DOCK_PLAN(WARE_ID,DOCK,STATUS,PLANNED_FROM);
create index RRL_YARD_DOCK_PLAN_WINDOW_IX on RRL_YARD_DOCK_PLAN(WARE_ID,STATUS,PLANNED_FROM,PLANNED_TO);
create table RRL_YARD_DOCK_PLAN_EVENT(
 OPERATION_ID varchar2(100)not null,WARE_ID number not null,PLAN_ID number not null,VISIT_ID number not null,ACTION varchar2(10)not null,
 DOCK varchar2(50)not null,PLANNED_FROM timestamp with time zone not null,PLANNED_TO timestamp with time zone not null,
 REQUEST_HASH varchar2(64)not null,ACTOR varchar2(50)not null,RESULT_JSON clob not null,CREATED_AT timestamp with time zone default systimestamp not null,
 constraint RRL_YARD_DOCK_PLAN_EVENT_PK primary key(OPERATION_ID),
 constraint RRL_YARD_DOCK_PLAN_EVENT_FK foreign key(PLAN_ID)references RRL_YARD_DOCK_PLAN(PLAN_ID),
 constraint RRL_YARD_DOCK_PLAN_EVENT_ACT check(ACTION in('PLAN','MOVE','CANCEL')),
 constraint RRL_YARD_DOCK_PLAN_EVENT_JSON check(RESULT_JSON is json)
);
create index RRL_YARD_DOCK_PLAN_EVENT_IX on RRL_YARD_DOCK_PLAN_EVENT(PLAN_ID,CREATED_AT);
-- A recorded plan event (and its replay answer) is never rewritten or removed.
create or replace trigger RRL_YARD_DOCK_PLAN_EVENT_APPEND before update or delete on RRL_YARD_DOCK_PLAN_EVENT
begin raise_application_error(-20911,'YARD_PLAN_EVENT_APPEND_ONLY');end;
/
