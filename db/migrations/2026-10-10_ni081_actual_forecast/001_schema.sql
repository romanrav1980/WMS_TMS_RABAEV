declare n number;
 procedure create_table_if_absent(name varchar2,definition clob)is begin select count(*)into n from USER_TABLES where TABLE_NAME=name;if n=0 then execute immediate definition;end if;end;
begin
 create_table_if_absent('RRL_FORECAST_LOAD',q'[create table RRL_FORECAST_LOAD(
 LOAD_OPERATION_ID varchar2(100)primary key references RRL_TT_HU_LOAD_FACT(LOAD_OPERATION_ID),
 WARE_ID number not null,DAY_UTC date not null,DEPARTED_AT timestamp with time zone not null,SOURCE_HASH varchar2(64)not null,
 LEAF_COUNT number not null,TOP_PLACES number not null,PROJECTED_BY nvarchar2(50)not null,
 PROJECTED_AT timestamp with time zone default systimestamp not null,RESULT_JSON clob not null check(RESULT_JSON is json),
 check(LEAF_COUNT between 1 and 200),check(TOP_PLACES=1),check(DAY_UTC=trunc(DAY_UTC))) ]');
 create_table_if_absent('RRL_FORECAST_LEAF',q'[create table RRL_FORECAST_LEAF(
 LOAD_OPERATION_ID varchar2(100)not null references RRL_FORECAST_LOAD(LOAD_OPERATION_ID),LINE_NO number not null,
 UID_PALLET varchar2(200)not null,ARTICLE varchar2(160)not null,BASE_UOM varchar2(20)not null,
 BASE_QTY number(38,9)not null check(BASE_QTY>0),WORK_KIND varchar2(20)not null,CASE_PICK_TASK_ID number,
 primary key(LOAD_OPERATION_ID,LINE_NO),unique(LOAD_OPERATION_ID,UID_PALLET),
 check(WORK_KIND in('CASE_DISPATCH','FULLPAL_DISPATCH','TRANSIT_CASE','CASE_RELOADED')))]');
 create_table_if_absent('RRL_FORECAST_CASE_ORIGIN',q'[create table RRL_FORECAST_CASE_ORIGIN(
 CASE_PICK_TASK_ID number not null,LOT_UID varchar2(200)not null,
 FIRST_LOAD_OPERATION varchar2(100)not null references RRL_FORECAST_LOAD(LOAD_OPERATION_ID),WARE_ID number not null,
 ARTICLE varchar2(160)not null,BASE_UOM varchar2(20)not null,BASE_QTY number(38,9)not null check(BASE_QTY>0),
 primary key(CASE_PICK_TASK_ID,LOT_UID))]');
 create_table_if_absent('RRL_FORECAST_DAY',q'[create table RRL_FORECAST_DAY(
 WARE_ID number not null,DAY_UTC date not null,LOAD_COUNT number(20)not null,TOP_PLACES number(20)not null,
 LAST_LOAD_OPERATION varchar2(100)not null references RRL_FORECAST_LOAD(LOAD_OPERATION_ID),
 primary key(WARE_ID,DAY_UTC),check(LOAD_COUNT>0),check(TOP_PLACES>0),check(DAY_UTC=trunc(DAY_UTC)))]');
 create_table_if_absent('RRL_FORECAST_SKU_DAY',q'[create table RRL_FORECAST_SKU_DAY(
 WARE_ID number not null,DAY_UTC date not null,ARTICLE varchar2(160)not null,BASE_UOM varchar2(20)not null,
 WORK_KIND varchar2(20)not null,BASE_QTY number(38,9)not null,LEAF_COUNT number(20)not null,SOURCE_COUNT number(20)not null,
 primary key(WARE_ID,DAY_UTC,ARTICLE,BASE_UOM,WORK_KIND),
 check(BASE_QTY>0),check(LEAF_COUNT>0),check(SOURCE_COUNT>0),
 check(WORK_KIND in('CASE_DISPATCH','FULLPAL_DISPATCH','TRANSIT_CASE','CASE_RELOADED')),check(DAY_UTC=trunc(DAY_UTC)))]');
 select count(*)into n from USER_INDEXES where INDEX_NAME='RRL_FORECAST_LOAD_WD_I1';
 if n=0 then execute immediate 'create index RRL_FORECAST_LOAD_WD_I1 on RRL_FORECAST_LOAD(WARE_ID,DAY_UTC,LOAD_OPERATION_ID)';end if;
 select count(*)into n from USER_INDEXES where INDEX_NAME='RRL_LOAD_FORECAST_WD_I1';
 if n=0 then execute immediate 'create index RRL_LOAD_FORECAST_WD_I1 on RRL_TT_HU_LOAD_FACT(WARE_ID,STATUS,DEPARTED_AT,LOAD_OPERATION_ID)';end if;
end;
/
