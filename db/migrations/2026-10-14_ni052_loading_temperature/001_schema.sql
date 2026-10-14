begin execute immediate q'[create table RRL_TT_LOAD_THERMAL_FACT(
 LOAD_OPERATION_ID varchar2(100) primary key references RRL_TT_HU_LOAD_FACT(LOAD_OPERATION_ID),
 VEHICLE_ID number not null,
 PROFILE_VERSION number(19) not null,
 OBSERVED_C number(9,3) not null,
 OBSERVATION_REFERENCE nvarchar2(100) not null,
 OBSERVATION_BASIS varchar2(24) not null check(OBSERVATION_BASIS='MANUAL_AT_LOADING'),
 ACTOR nvarchar2(50) not null,
 RECORDED_AT timestamp with time zone default systimestamp not null,
 SENSOR_VERIFIED number(1) default 0 not null check(SENSOR_VERIFIED=0),
 CONFIRMATION_JSON clob not null check(CONFIRMATION_JSON is json),
 foreign key(VEHICLE_ID,PROFILE_VERSION) references RRL_VEHICLE_PROFILE_HIST(VEHICLE_ID,VERSION_NO))]';end;
/
