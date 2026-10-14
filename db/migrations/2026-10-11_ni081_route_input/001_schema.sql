create table RRL_TT_ROUTE_INPUT(
 TT_ID number not null references RRL_TRANSPORT_TASK(ID),VERSION_NO number not null,
 OPERATION_ID varchar2(100)not null unique,ACTOR varchar2(50)not null,
 REQUEST_HASH varchar2(64)not null,SOURCE_HASH varchar2(64)not null,
 DRIVE_MIN number(8,2)not null,DRIVE_BACK_MIN number(8,2)not null,
 SOURCE_REFERENCE nvarchar2(500)not null,REASON nvarchar2(500)not null,
 RESULT_JSON clob not null check(RESULT_JSON is json),
 CREATED_AT timestamp with time zone default systimestamp not null,
 constraint RRL_TT_ROUTE_INPUT_PK primary key(TT_ID,VERSION_NO),
 constraint RRL_TT_ROUTE_INPUT_VER_CK check(VERSION_NO>0),
 constraint RRL_TT_ROUTE_INPUT_MIN_CK check(DRIVE_MIN>0 and DRIVE_MIN<=1440 and DRIVE_BACK_MIN>0 and DRIVE_BACK_MIN<=1440)
);
/
