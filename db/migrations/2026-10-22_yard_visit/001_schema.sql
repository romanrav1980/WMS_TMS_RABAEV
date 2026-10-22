create sequence RRL_YARD_VISIT_SQ start with 1 increment by 1 nocache;
create table RRL_YARD_VISIT(
 VISIT_ID number not null,WARE_ID number not null,VISIT_KIND varchar2(12)not null,TRIP_ID varchar2(100),NATIVE_TASK_ID number,
 VEHICLE varchar2(50),DOCK varchar2(50),STATE varchar2(12)not null,VERSION_NO number not null,
 PLANNED_ARRIVAL_AT timestamp with time zone,ARRIVED_AT timestamp with time zone,DOCKED_AT timestamp with time zone,
 WORK_STARTED_AT timestamp with time zone,WORK_FINISHED_AT timestamp with time zone,DEPARTED_AT timestamp with time zone,
 CANCELLED_AT timestamp with time zone,CANCEL_REASON varchar2(500),
 CREATED_BY varchar2(50)not null,CREATED_AT timestamp with time zone default systimestamp not null,
 UPDATED_BY varchar2(50)not null,UPDATED_AT timestamp with time zone default systimestamp not null,
 constraint RRL_YARD_VISIT_PK primary key(VISIT_ID),
 constraint RRL_YARD_VISIT_SITE_FK foreign key(WARE_ID)references RRL_TRADE_SITE(WARE_ID),
 constraint RRL_YARD_VISIT_KIND check(VISIT_KIND in('OUTBOUND','INBOUND')),
 constraint RRL_YARD_VISIT_STATE check(STATE in('EXPECTED','ARRIVED','AT_DOCK','WORKING','WORK_DONE','DEPARTED','CANCELLED')),
 constraint RRL_YARD_VISIT_VER check(VERSION_NO>0 and VERSION_NO=trunc(VERSION_NO)),
 -- A state never exists without the fact that produced it; the dock is held exactly from docking to departure.
 constraint RRL_YARD_VISIT_FACTS check((STATE='EXPECTED'and ARRIVED_AT is null)
  or(STATE='ARRIVED'and ARRIVED_AT is not null and DOCK is null)
  or(STATE in('AT_DOCK','WORKING','WORK_DONE')and ARRIVED_AT is not null and DOCK is not null and DOCKED_AT is not null)
  or(STATE='DEPARTED'and DEPARTED_AT is not null)or(STATE='CANCELLED'and CANCELLED_AT is not null and CANCEL_REASON is not null)),
 constraint RRL_YARD_VISIT_WORK check((STATE<>'WORKING'or WORK_STARTED_AT is not null)and(STATE<>'WORK_DONE'or WORK_FINISHED_AT is not null)),
 constraint RRL_YARD_VISIT_TRIP check(VISIT_KIND<>'OUTBOUND'or TRIP_ID is not null),
 -- One spelling per vehicle: case and spaces cannot slip past the occupancy index; arrival needs an identified vehicle.
 constraint RRL_YARD_VISIT_VEHICLE check(VEHICLE is null or VEHICLE=upper(trim(VEHICLE))),
 constraint RRL_YARD_VISIT_ARRIVAL check(STATE in('EXPECTED','CANCELLED')or VEHICLE is not null)
);
-- One dock, one vehicle, one trip: at most one active visit each (the database is the final guard against two dispatchers).
-- The vehicle guard is global: one truck cannot stand in two warehouse yards at once; EXPECTED holds nothing.
create unique index RRL_YARD_VISIT_DOCK_UK on RRL_YARD_VISIT(case when STATE in('AT_DOCK','WORKING','WORK_DONE')then WARE_ID end,
 case when STATE in('AT_DOCK','WORKING','WORK_DONE')then DOCK end);
create unique index RRL_YARD_VISIT_VEHICLE_UK on RRL_YARD_VISIT(case when STATE in('ARRIVED','AT_DOCK','WORKING','WORK_DONE')then VEHICLE end);
create unique index RRL_YARD_VISIT_TRIP_UK on RRL_YARD_VISIT(case when STATE not in('DEPARTED','CANCELLED')and TRIP_ID is not null then WARE_ID end,
 case when STATE not in('DEPARTED','CANCELLED')and TRIP_ID is not null then TRIP_ID end);
create index RRL_YARD_VISIT_STATE_IX on RRL_YARD_VISIT(WARE_ID,STATE,PLANNED_ARRIVAL_AT);
create index RRL_YARD_VISIT_ARRIVED_IX on RRL_YARD_VISIT(WARE_ID,ARRIVED_AT);
create table RRL_YARD_VISIT_EVENT(
 OPERATION_ID varchar2(100)not null,WARE_ID number not null,VISIT_ID number not null,ACTION varchar2(20)not null,
 FROM_STATE varchar2(12),TO_STATE varchar2(12)not null,DOCK varchar2(50),VEHICLE varchar2(50),REQUEST_HASH varchar2(64)not null,ACTOR varchar2(50)not null,
 -- EVENT_AT is the fact time written to the visit in the same command: the timeline rebuilds dock/vehicle intervals from it.
 EVENT_AT timestamp with time zone not null,
 RESULT_JSON clob not null,CREATED_AT timestamp with time zone default systimestamp not null,
 constraint RRL_YARD_VISIT_EVENT_PK primary key(OPERATION_ID),
 constraint RRL_YARD_VISIT_EVENT_VISIT_FK foreign key(VISIT_ID)references RRL_YARD_VISIT(VISIT_ID),
 constraint RRL_YARD_VISIT_EVENT_ACTION check(ACTION in('EXPECT','ARRIVE','ASSIGN_DOCK','REASSIGN_DOCK','START','FINISH','DEPART','CANCEL')),
 constraint RRL_YARD_VISIT_EVENT_JSON check(RESULT_JSON is json)
);
create index RRL_YARD_VISIT_EVENT_VISIT_IX on RRL_YARD_VISIT_EVENT(VISIT_ID,EVENT_AT);
-- Event history is append-only: a recorded yard event (and its replay answer) is never rewritten or removed.
create or replace trigger RRL_YARD_VISIT_EVENT_APPEND before update or delete on RRL_YARD_VISIT_EVENT
begin raise_application_error(-20911,'YARD_EVENT_APPEND_ONLY');end;
/
