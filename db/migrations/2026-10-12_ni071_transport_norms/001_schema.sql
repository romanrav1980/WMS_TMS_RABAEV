begin execute immediate q'[create table RRL_TRANSPORT_NORM_HEAD(
 SOURCE_PRICE_ID number primary key,WARE_ID number not null,VERSION_NO number(19)default 0 not null check(VERSION_NO>=0))]';
exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate q'[create table RRL_TRANSPORT_NORM_HISTORY(
 SOURCE_PRICE_ID number not null references RRL_TRANSPORT_NORM_HEAD(SOURCE_PRICE_ID),
 VERSION_NO number(19)not null check(VERSION_NO>0),OPERATION_ID varchar2(100)not null unique,
 WARE_ID number not null,ACTOR nvarchar2(50)not null,
 EFFECTIVE_FROM date not null,CURRENCY varchar2(3)not null,TIME_ZONE varchar2(64)not null,
 VEHICLE_TYPE varchar2(40)not null,VEHICLE_SIZE_CLASS varchar2(40)not null,
 REQUEST_JSON clob not null check(REQUEST_JSON is json),
 SOURCE_JSON clob not null check(SOURCE_JSON is json),RESULT_JSON clob not null check(RESULT_JSON is json),
 CREATED_AT timestamp with time zone default systimestamp not null,
 primary key(SOURCE_PRICE_ID,VERSION_NO))]';
exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate 'create index RRL_TRANSPORT_NORM_DATE_IX on RRL_TRANSPORT_NORM_HISTORY(SOURCE_PRICE_ID,EFFECTIVE_FROM desc,VERSION_NO desc)';
exception when others then if sqlcode!=-955 then raise;end if;end;
/
