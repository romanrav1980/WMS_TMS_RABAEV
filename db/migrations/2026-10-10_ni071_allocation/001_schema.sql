begin execute immediate q'[create table RRL_LOGISTICS_EXP_ALLOCATION(
 OPERATION_ID varchar2(100) primary key,PAYLOAD_HASH raw(32) not null,
 EXPENSE_OPERATION_ID varchar2(100) not null unique references RRL_LOGISTICS_EXPENSE(OPERATION_ID),
 FINANCE_OPERATION_ID varchar2(100) not null references RRL_LOGISTICS_EXP_DECISION(OPERATION_ID),
 DISTRIBUTION_BASIS varchar2(20) not null check(DISTRIBUTION_BASIS in('BASE_QUANTITY','WEIGHT')),
 AMOUNT number(27,2) not null check(AMOUNT>0),CURRENCY varchar2(3) not null,
 ACTOR nvarchar2(50) not null,CREATED_AT timestamp with time zone default systimestamp not null,
 RESULT_JSON clob not null check(RESULT_JSON is json)
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate q'[create table RRL_LOGISTICS_EXP_ALLOC_LINE(
 OPERATION_ID varchar2(100) not null references RRL_LOGISTICS_EXP_ALLOCATION(OPERATION_ID),
 LOAD_OPERATION_ID varchar2(100) not null references RRL_TT_HU_LOAD_FACT(LOAD_OPERATION_ID),
 UID_PALLET varchar2(200) not null,ARTICLE varchar2(160) not null,
 BASE_QTY number(27,9) not null check(BASE_QTY>0),BASE_UOM varchar2(20) not null,
 WEIGHT_KG number(27,9),BASIS_VALUE number(27,9) not null check(BASIS_VALUE>0),
 AMOUNT number(27,2) not null check(AMOUNT>=0),CURRENCY varchar2(3) not null,
 primary key(OPERATION_ID,LOAD_OPERATION_ID,UID_PALLET)
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
