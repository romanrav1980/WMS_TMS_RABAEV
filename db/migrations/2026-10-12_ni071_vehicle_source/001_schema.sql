begin execute immediate q'[create table RRL_VEHICLE_PROFILE_HEAD(
 VEHICLE_ID number primary key references RRL_TR_VEHICLE(ID),
 VERSION_NO number(19)default 0 not null check(VERSION_NO>=0))]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate q'[create table RRL_VEHICLE_PROFILE_HIST(
 VEHICLE_ID number not null references RRL_VEHICLE_PROFILE_HEAD(VEHICLE_ID),
 VERSION_NO number(19)not null check(VERSION_NO>0),
 OPERATION_ID varchar2(100)not null unique,
 ACTOR nvarchar2(50)not null,VEHICLE_SIZE_CLASS varchar2(40)not null,
 CARGO_LENGTH_MM number(7)not null check(CARGO_LENGTH_MM>0),
 CARGO_WIDTH_MM number(7)not null check(CARGO_WIDTH_MM>0),
 CARGO_HEIGHT_MM number(7)not null check(CARGO_HEIGHT_MM>0),
 SOURCE_JSON clob not null check(SOURCE_JSON is json),
 REQUEST_JSON clob not null check(REQUEST_JSON is json),
 RESULT_JSON clob not null check(RESULT_JSON is json),
 CREATED_AT timestamp with time zone default systimestamp not null,
 primary key(VEHICLE_ID,VERSION_NO))]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate q'[create table RRL_TT_VEHICLE_SOURCE(
 TT_ID number primary key references RRL_TRANSPORT_TASK(ID),
 DEPARTURE_OPERATION_ID varchar2(100)not null unique references RRL_STOCK_OPERATION(OPERATION_ID),
 VEHICLE_ID number not null references RRL_TR_VEHICLE(ID),
 PROFILE_VERSION number(19),
 SOURCE_STATE varchar2(24)not null check(SOURCE_STATE in('READY','NOT_CONFIGURED','BASE_CHANGED')),
 SOURCE_JSON clob not null check(SOURCE_JSON is json),
 CAPTURED_AT timestamp with time zone default systimestamp not null)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
