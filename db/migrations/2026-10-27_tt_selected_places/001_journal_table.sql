create table RRL_TT_PLACE_REMOVAL_CMD(
 OPERATION_ID varchar2(100) not null,
 ACTOR varchar2(50) not null,
 REQUEST_HASH varchar2(64) not null,
 TRIP_ID number not null,
 ST_NUMBER varchar2(200) not null,
 RESULT_JSON clob not null check(RESULT_JSON is json),
 CREATED_AT timestamp default systimestamp not null,
 constraint RRL_TT_PLACE_REMOVAL_CMD_PK primary key(OPERATION_ID));
