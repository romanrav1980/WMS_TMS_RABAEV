create table RRL_INTERWARE_DECISION(
 OPERATION_ID varchar2(100)constraint RRL_IW_DECISION_PK primary key,
 PLAN_OPERATION_ID varchar2(100)not null references RRL_INTERWARE_PLAN(OPERATION_ID),
 REVISION_NO number(10)not null,DECISION_KIND varchar2(10)not null check(DECISION_KIND in('WAIT','DEFER')),
 PREVIOUS_TT_ID number not null references RRL_TRANSPORT_TASK(ID),
 TARGET_TT_ID number not null references RRL_TRANSPORT_TASK(ID),OUTBOUND_DOCK varchar2(15)not null,
 EXPECTED_ARRIVAL timestamp with time zone not null,READY_DUE timestamp with time zone not null,
 REASON_TEXT nvarchar2(500)not null,DECISION_REFERENCE varchar2(60)not null,ACTOR nvarchar2(50)not null,
 PAYLOAD_HASH raw(32)not null,CANONICAL_REQUEST clob not null check(CANONICAL_REQUEST is json),
 RESULT_JSON clob not null check(RESULT_JSON is json),CREATED_AT timestamp with time zone default systimestamp not null,
 constraint RRL_IW_DECISION_REV_UK unique(PLAN_OPERATION_ID,REVISION_NO)
);
