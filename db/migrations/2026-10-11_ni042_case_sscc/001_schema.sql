create table RRL_CASE_SSCC_LABEL(
 OPERATION_ID varchar2(100) primary key,
 CASE_PICK_TASK_ID number not null references RRL_CASE_PICK_TASK(CASE_PICK_TASK_ID),
 SSCC varchar2(18) not null,
 ORIGINAL_CARRIER varchar2(64) not null,
 WARE_ID number not null,
 PALLET_TYPE_ID number not null,
 REQUESTED_VERSION number not null,
 CREATED_BY varchar2(50) not null,
 CREATED_AT timestamp with time zone default systimestamp not null,
 REQUEST_JSON clob not null check(REQUEST_JSON is json),
 RESULT_JSON clob not null check(RESULT_JSON is json),
 CONFIRMED_AT timestamp with time zone,
 CONFIRMED_BY varchar2(50),
 constraint RRL_CASE_SSCC_LABEL_CASE_U unique(CASE_PICK_TASK_ID),
 constraint RRL_CASE_SSCC_LABEL_SSCC_U unique(SSCC),
 constraint RRL_CASE_SSCC_LABEL_DIGIT_C check(regexp_like(SSCC,'^[0-9]{18}$')),
 constraint RRL_CASE_SSCC_LABEL_CONF_C check((CONFIRMED_AT is null and CONFIRMED_BY is null)or(CONFIRMED_AT is not null and CONFIRMED_BY is not null))
);
