create table RRL_WARE_DEPOT_HISTORY(
 OPERATION_ID varchar2(100)primary key,WARE_ID number not null,VERSION_NO number not null,
 DEPOT_ADDR varchar2(200),ACTOR varchar2(50)not null,REASON_TEXT varchar2(500 char)not null,
 REQUEST_HASH varchar2(64)not null,REQUEST_JSON clob not null,RESULT_JSON clob not null,
 CREATED_AT timestamp with time zone default systimestamp not null,
 constraint RRL_WARE_DEPOT_VER_U unique(WARE_ID,VERSION_NO),
 constraint RRL_WARE_DEPOT_VER_C check(VERSION_NO>0 and VERSION_NO=trunc(VERSION_NO)),
 constraint RRL_WARE_DEPOT_REQ_J check(REQUEST_JSON is json),
 constraint RRL_WARE_DEPOT_RES_J check(RESULT_JSON is json)
);
