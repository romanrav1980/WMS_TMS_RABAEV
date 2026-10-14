begin execute immediate q'[create table RRL_LOGISTICS_RATE_HEAD(
 RATE_KEY varchar2(64) primary key,WARE_ID number not null,
 COST_CODE varchar2(40) not null check(COST_CODE='WAREHOUSE_PICKING'),
 CURRENCY varchar2(3) not null check(regexp_like(CURRENCY,'^[A-Z]{3}$')),
 VERSION_NO number(19) not null check(VERSION_NO>0),
 unique(WARE_ID,COST_CODE,CURRENCY)
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate q'[create table RRL_LOGISTICS_RATE_HISTORY(
 RATE_KEY varchar2(64) not null references RRL_LOGISTICS_RATE_HEAD(RATE_KEY),VERSION_NO number(19) not null,
 RATE_VALUE number(27,9) not null check(RATE_VALUE>=0),BASIS varchar2(20) default 'BOX' not null check(BASIS='BOX'),
 EFFECTIVE_FROM date not null,REASON_TEXT varchar2(2000 byte) not null,DECISION_REFERENCE varchar2(255 byte) not null,
 ACTOR nvarchar2(50) not null,CREATED_AT timestamp with time zone default systimestamp not null,
 primary key(RATE_KEY,VERSION_NO),unique(RATE_KEY,EFFECTIVE_FROM)
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate q'[create table RRL_LOGISTICS_COST_RUN(
 OPERATION_ID varchar2(100) primary key,PAYLOAD_HASH raw(32) not null,
 TT_ID number not null references RRL_TRANSPORT_TASK(ID),WARE_ID number not null,
 CURRENCY varchar2(3) not null,ACTOR nvarchar2(50) not null,
 CREATED_AT timestamp with time zone default systimestamp not null,
 RESULT_JSON clob not null check(RESULT_JSON is json)
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate q'[create table RRL_LOGISTICS_COST_LINE(
 OPERATION_ID varchar2(100) not null references RRL_LOGISTICS_COST_RUN(OPERATION_ID),
 LOAD_OPERATION_ID varchar2(100) not null references RRL_TT_HU_LOAD_FACT(LOAD_OPERATION_ID),
 COST_CODE varchar2(40) not null,CURRENCY varchar2(3) not null,RATE_KEY varchar2(64) not null,VERSION_NO number(19) not null,
 QUANTITY number(19) not null check(QUANTITY>0),RATE_VALUE number(27,9) not null check(RATE_VALUE>=0),
 AMOUNT number(27,2) not null check(AMOUNT>=0),BASIS varchar2(20) not null check(BASIS='BOX'),
 primary key(OPERATION_ID,LOAD_OPERATION_ID,COST_CODE),unique(LOAD_OPERATION_ID,COST_CODE,CURRENCY),
 foreign key(RATE_KEY,VERSION_NO)references RRL_LOGISTICS_RATE_HISTORY(RATE_KEY,VERSION_NO),
 check(AMOUNT=round(QUANTITY*RATE_VALUE,2))
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
