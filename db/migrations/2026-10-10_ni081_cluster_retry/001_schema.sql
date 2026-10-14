create table RRL_CLUSTER_CREATE_RESULT(
 OPERATION_ID varchar2(100) primary key, ACTOR varchar2(50)not null,
 REQUEST_HASH varchar2(64)not null, REQUEST_JSON clob not null check(REQUEST_JSON is json),
 TRIP_ID number references RRL_TRANSPORT_TASK(ID), RESULT_JSON clob check(RESULT_JSON is json),
 CREATED_AT timestamp with time zone default systimestamp not null
);
create index RRL_CLUSTER_CREATE_TRIP_IX on RRL_CLUSTER_CREATE_RESULT(TRIP_ID);
/
