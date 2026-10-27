create table RRL_YARD_DOCK_STATUS_EVENT(
 OPERATION_ID varchar2(100)not null,WARE_ID number not null,DOCK varchar2(15)not null,ACTION varchar2(10)not null,
 BLOCKED number(1)not null,REASON varchar2(500)not null,REQUEST_HASH varchar2(64)not null,ACTOR varchar2(50)not null,
 RESULT_JSON clob not null,CREATED_AT timestamp with time zone default systimestamp not null,
 constraint RRL_YARD_DOCK_STATUS_EVENT_PK primary key(OPERATION_ID),
 constraint RRL_YARD_DOCK_STATUS_EVENT_ACTION check(ACTION in('BLOCK','UNBLOCK')),
 constraint RRL_YARD_DOCK_STATUS_EVENT_BLOCKED check(BLOCKED in(0,1)),
 constraint RRL_YARD_DOCK_STATUS_EVENT_JSON check(RESULT_JSON is json)
);
create index RRL_YARD_DOCK_STATUS_EVENT_DOCK_IX on RRL_YARD_DOCK_STATUS_EVENT(WARE_ID,DOCK,CREATED_AT);
create or replace trigger RRL_YARD_DOCK_STATUS_EVENT_APPEND before update or delete on RRL_YARD_DOCK_STATUS_EVENT
begin raise_application_error(-20911,'YARD_DOCK_STATUS_APPEND_ONLY');end;
/
