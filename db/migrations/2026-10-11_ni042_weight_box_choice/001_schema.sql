create table RRL_PICK_WEIGHT_CHOICE(
 CHOICE_ID varchar2(100)primary key,CUSTOMER_ORDER_ROW_ID number not null references RRL_CUSTOMER_ORDER_ROW(CUSTOMER_ORDER_ROW_ID),
 CUSTOMER_ORDER_ID number not null,WARE_ID number not null,ARTICLE varchar2(160)not null,
 PHYSICAL_UNIT_KEY varchar2(64)not null,SOURCE_UID varchar2(150)not null,SOURCE_CELL varchar2(60)not null,STOCK_VERSION number not null,
 NET_WEIGHT_KG number(27,9)not null check(NET_WEIGHT_KG>0),POLICY_VERSION number not null,
 TOLERANCE_PCT number(5,2)not null check(TOLERANCE_PCT between 0 and 100),
 ORIGINAL_ORDER_KG number(27,9)not null check(ORIGINAL_ORDER_KG>0),ORIGINAL_REMAINING_KG number(27,9)not null check(ORIGINAL_REMAINING_KG>0),
 CHOICE_MODE varchar2(24)not null check(CHOICE_MODE in('WITHIN_TOLERANCE','LAST_WHOLE_BOX')),
 STATUS varchar2(16)default 'ACCEPTED'not null check(STATUS in('ACCEPTED','USED','CANCELLED')),
 APPROVED_BY varchar2(50)not null,APPROVED_AT timestamp with time zone default systimestamp not null,REASON_TEXT varchar2(1000 char)not null,
 SOURCE_SIGNATURE varchar2(64)not null,SOURCE_JSON clob not null check(SOURCE_JSON is json),REQUEST_JSON clob not null check(REQUEST_JSON is json),
 RESULT_JSON clob not null check(RESULT_JSON is json),
 PICK_PLAN_ID number references RRL_PICK_PLAN(PICK_PLAN_ID),PICK_PLAN_LINE_ID number references RRL_PICK_PLAN_LINE(PICK_PLAN_LINE_ID),
 USED_AT timestamp with time zone,CANCELLED_BY varchar2(50),CANCELLED_AT timestamp with time zone,CANCEL_REASON varchar2(1000 char));
create unique index RRL_WEIGHT_CHOICE_ROW_I on RRL_PICK_WEIGHT_CHOICE(case when STATUS in('ACCEPTED','USED')then CUSTOMER_ORDER_ROW_ID end);
create unique index RRL_WEIGHT_CHOICE_UNIT_I on RRL_PICK_WEIGHT_CHOICE(case when STATUS in('ACCEPTED','USED')then PHYSICAL_UNIT_KEY end);
