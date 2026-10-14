begin execute immediate q'[create table RRL_INTERWARE_PLAN(
 OPERATION_ID varchar2(100) primary key,PAYLOAD_HASH raw(32) not null,
 SOURCE_LOAD_OPERATION_ID varchar2(100) not null unique references RRL_TT_HU_LOAD_FACT(LOAD_OPERATION_ID),
 SOURCE_ST_ID number not null references RRL_SBORKA_PALLETS(ID),
 SOURCE_TT_ID number not null references RRL_TRANSPORT_TASK(ID),SOURCE_WARE_ID number not null,
 TARGET_WARE_ID number not null,TARGET_TT_ID number not null references RRL_TRANSPORT_TASK(ID),
 ROOT_UID varchar2(200) not null,SOURCE_COMPOSITION_JSON clob not null check(SOURCE_COMPOSITION_JSON is json),
 INBOUND_DOCK varchar2(60) not null,OUTBOUND_DOCK varchar2(60) not null,
 ARRIVAL_DUE timestamp with time zone not null,READY_DUE timestamp with time zone not null,
 REASON_TEXT varchar2(2000 byte) not null,DECISION_REFERENCE varchar2(255 byte) not null,
 ACTOR nvarchar2(50) not null,CREATED_AT timestamp with time zone default systimestamp not null,
 RESULT_JSON clob not null check(RESULT_JSON is json),
 check(SOURCE_WARE_ID!=TARGET_WARE_ID),check(SOURCE_TT_ID!=TARGET_TT_ID),check(READY_DUE>=ARRIVAL_DUE)
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate 'create index RRL_INTERWARE_TARGET_IX on RRL_INTERWARE_PLAN(TARGET_WARE_ID,ARRIVAL_DUE)';exception when others then if sqlcode!=-955 then raise;end if;end;
/
