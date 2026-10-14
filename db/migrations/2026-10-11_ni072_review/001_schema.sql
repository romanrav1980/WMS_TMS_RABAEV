create table RRL_DAY_REVIEW(
 OPERATION_ID varchar2(100) primary key,
 WARE_ID number not null,BUSINESS_DATE date not null,TIMEZONE_REGION varchar2(64) not null,
 VERSION_NO number not null,ACTOR varchar2(50) not null,
 REQUEST_HASH varchar2(64) not null,REQUEST_JSON clob not null,SOURCE_HASH varchar2(64) not null,
 REPORT_JSON clob not null,RESULT_JSON clob not null,
 CAPTURED_AT timestamp with time zone not null,RECORDED_AT timestamp with time zone default systimestamp not null,
 constraint RRL_DAY_REVIEW_VER_U unique(WARE_ID,BUSINESS_DATE,TIMEZONE_REGION,VERSION_NO),
 constraint RRL_DAY_REVIEW_VER_C check(VERSION_NO>0 and VERSION_NO=trunc(VERSION_NO)and BUSINESS_DATE=trunc(BUSINESS_DATE)),
 constraint RRL_DAY_REVIEW_REQ_J check(REQUEST_JSON is json),
 constraint RRL_DAY_REVIEW_REPORT_J check(REPORT_JSON is json),
 constraint RRL_DAY_REVIEW_RESULT_J check(RESULT_JSON is json)
);
