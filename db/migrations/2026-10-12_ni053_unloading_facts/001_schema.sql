begin execute immediate q'[create table RRL_STORE_UNLOAD_START(
 OPERATION_ID varchar2(100)primary key,LOAD_OPERATION_ID varchar2(100)not null unique references RRL_TT_HU_LOAD_FACT(LOAD_OPERATION_ID),
 STORE_ADDR varchar2(255)not null,ROOT_KEY varchar2(200)not null,COMPOSITION_SIGNATURE varchar2(64)not null,
 ACTOR nvarchar2(50)not null,STARTED_AT_INSTANT timestamp with time zone default systimestamp not null,
 REQUEST_JSON clob not null check(REQUEST_JSON is json),RESULT_JSON clob not null check(RESULT_JSON is json))]';
exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate q'[create table RRL_STORE_UNLOAD_FACT(
 RECEIPT_OPERATION_ID varchar2(100)primary key references RRL_STORE_RECEIPT_FACT(OPERATION_ID),
 START_OPERATION_ID varchar2(100)not null unique references RRL_STORE_UNLOAD_START(OPERATION_ID),
 LOAD_OPERATION_ID varchar2(100)not null unique references RRL_TT_HU_LOAD_FACT(LOAD_OPERATION_ID),
 STORE_ADDR varchar2(255)not null,METHOD varchar2(20)not null check(METHOD in('ROLL_CAGE','PALLET','MANUAL')),
 ROLLING_DIFFICULT number(1)not null check(ROLLING_DIFFICULT in(0,1)),
 LOADER_PRESENT number(1)not null check(LOADER_PRESENT in(0,1)),
 EVIDENCE_REFERENCE varchar2(255)not null,ACTOR nvarchar2(50)not null,
 FINISHED_AT_INSTANT timestamp with time zone default systimestamp not null,
 PAYLOAD_JSON clob not null check(PAYLOAD_JSON is json))]';
exception when others then if sqlcode!=-955 then raise;end if;end;
/
