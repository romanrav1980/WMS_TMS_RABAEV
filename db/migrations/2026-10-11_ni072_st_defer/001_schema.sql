create table RRL_ST_DEFER_DECISION(
 OPERATION_ID varchar2(100) primary key,ST_NUMBER varchar2(100) not null,VERSION_NO number not null,
 SOURCE_TT_ID number not null,TARGET_TT_ID number not null,WARE_ID number not null,
 ACTOR varchar2(50) not null,REQUEST_HASH varchar2(64) not null,REQUEST_JSON clob not null,
 SOURCE_HASH varchar2(64) not null,SOURCE_JSON clob not null,RESULT_JSON clob not null,
 CREATED_AT timestamp with time zone default systimestamp not null,
 constraint RRL_ST_DEFER_VER_U unique(ST_NUMBER,VERSION_NO),
 constraint RRL_ST_DEFER_VER_C check(VERSION_NO>0 and VERSION_NO=trunc(VERSION_NO)and SOURCE_TT_ID!=TARGET_TT_ID),
 constraint RRL_ST_DEFER_REQ_J check(REQUEST_JSON is json),
 constraint RRL_ST_DEFER_SRC_J check(SOURCE_JSON is json),
 constraint RRL_ST_DEFER_RES_J check(RESULT_JSON is json)
);
