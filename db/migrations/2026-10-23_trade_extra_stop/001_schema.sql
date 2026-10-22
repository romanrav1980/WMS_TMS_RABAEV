-- Per-trip ban on new points (program section 12: with the ban on, such an extra stop is not proposed).
create table RRL_TRADE_ROUTE_STOP_POLICY(
 TRIP_ID number not null,NEW_STOPS_FORBIDDEN number(1)not null,VERSION_NO number not null,UPDATED_BY varchar2(50)not null,
 UPDATED_AT timestamp with time zone not null,
 constraint RRL_TRADE_ROUTE_STOP_POLICY_PK primary key(TRIP_ID),
 constraint RRL_TRADE_ROUTE_STOP_POLICY_FLAG check(NEW_STOPS_FORBIDDEN in(0,1)),
 constraint RRL_TRADE_ROUTE_STOP_POLICY_VER check(VERSION_NO>0 and VERSION_NO=trunc(VERSION_NO))
);
-- Journal of extra-stop decisions and policy changes, bound to the route source hash and time-context version they were made on.
create table RRL_TRADE_EXTRA_STOP_EVENT(
 OPERATION_ID varchar2(100)not null,TRIP_ID number not null,ACTION varchar2(12)not null,ADDRESS varchar2(255),POSITION_NO number,
 DECISION varchar2(12)not null,SOURCE_HASH varchar2(64),TIME_VERSION number,PROPOSAL_FINGERPRINT varchar2(64),REQUEST_HASH varchar2(64)not null,ACTOR varchar2(50)not null,
 EVENT_AT timestamp with time zone not null,RESULT_JSON clob not null,
 constraint RRL_TRADE_EXTRA_STOP_EVENT_PK primary key(OPERATION_ID),
 constraint RRL_TRADE_EXTRA_STOP_EVENT_ACTION check(ACTION in('APPROVE','DECLINE','SET_POLICY')),
 constraint RRL_TRADE_EXTRA_STOP_EVENT_DECISION check(DECISION in('APPROVED','DECLINED','POLICY')),
 constraint RRL_TRADE_EXTRA_STOP_EVENT_BIND check(ACTION='SET_POLICY'or(ADDRESS is not null and SOURCE_HASH is not null and TIME_VERSION is not null)),
 -- An approval is bound to the exact proposal (full AFTER source), not only to the base route.
 constraint RRL_TRADE_EXTRA_STOP_EVENT_PRINT check(ACTION<>'APPROVE'or PROPOSAL_FINGERPRINT is not null),
 constraint RRL_TRADE_EXTRA_STOP_EVENT_JSON check(RESULT_JSON is json)
);
create index RRL_TRADE_EXTRA_STOP_EVENT_TRIP_IX on RRL_TRADE_EXTRA_STOP_EVENT(TRIP_ID,ADDRESS,EVENT_AT);
create or replace trigger RRL_TRADE_EXTRA_STOP_EVENT_APPEND before update or delete on RRL_TRADE_EXTRA_STOP_EVENT
begin raise_application_error(-20911,'EXTRA_STOP_EVENT_APPEND_ONLY');end;
/
