create table RRL_WH_WEIGH_ZERO(
 CLAIM_ID varchar2(100) primary key references RRL_WH_WEIGH_CLAIM(CLAIM_ID),
 REQUEST_ID varchar2(100) not null references RRL_WH_WEIGH_REQUEST(REQUEST_ID),
 DEVICE_ID varchar2(100) not null references RRL_WH_SCALE_DEVICE(DEVICE_ID),
 RECORDED_BY nvarchar2(50) not null,
 ZERO_OBSERVED_AT timestamp with time zone not null,
 RECEIVED_AT timestamp with time zone not null,
 ZERO_SOURCE_SHA256 varchar2(64) not null,
 PROFILE_SHA256 varchar2(64) not null,
 ZERO_EVIDENCE_JSON clob not null check(ZERO_EVIDENCE_JSON is json),
 SOURCE_JSON clob not null check(SOURCE_JSON is json),
 RESULT_JSON clob not null check(RESULT_JSON is json)
);
