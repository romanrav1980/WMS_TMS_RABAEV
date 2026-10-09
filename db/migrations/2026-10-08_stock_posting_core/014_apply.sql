prompt Stock posting foundation in RABAEV; preparation only, does not activate posting
declare n number;
 procedure ensure_table(p_name varchar2,p_sql varchar2) is
 begin
  select count(*) into n from USER_TABLES where TABLE_NAME=p_name;
  if n=0 then execute immediate p_sql; end if;
 end;
 procedure ensure_column(p_table varchar2,p_col varchar2,p_def varchar2) is
 begin
  select count(*) into n from USER_TAB_COLUMNS where TABLE_NAME=p_table and COLUMN_NAME=p_col;
  if n=0 then execute immediate 'alter table '||p_table||' add ('||p_def||')'; end if;
 end;
begin
 if user!='RABAEV' or lower(sys_context('USERENV','SERVICE_NAME'))!='orcl' then raise_application_error(-20801,'RABAEV/orcl only'); end if;
 ensure_table('RRL_STOCK_RELEASE',q'[create table RRL_STOCK_RELEASE(
  RELEASE_ID number primary key,STATE varchar2(20) not null,BASELINE_ID varchar2(100),
  CHANGED_AT timestamp default systimestamp not null,CHANGED_BY varchar2(50) not null,
  constraint RRL_STOCK_RELEASE_STATE_CK check(STATE in('PREPARED','CUTOVER','ACTIVE')),
  constraint RRL_STOCK_RELEASE_ONE_CK check(RELEASE_ID=1))]');
 ensure_table('RRL_STOCK_OPERATION',q'[create table RRL_STOCK_OPERATION(
  OPERATION_ID varchar2(100) primary key,CONTRACT_VERSION number not null,COMMAND_TYPE varchar2(80) not null,
  ACTOR varchar2(50) not null,REQUEST_HASH varchar2(64) not null,CANONICAL_REQUEST clob not null,
  RESULT_JSON clob,STATE varchar2(20) not null,CREATED_AT timestamp default systimestamp not null,
  APPLIED_AT timestamp,BASELINE_ID varchar2(100),
  constraint RRL_STOCK_OP_REQ_CK check(CANONICAL_REQUEST is json),
  constraint RRL_STOCK_OP_RES_CK check(RESULT_JSON is json),
  constraint RRL_STOCK_OP_STATE_CK check(STATE in('IN_FLIGHT','APPLIED')),
  constraint RRL_STOCK_OP_DONE_CK check(STATE!='APPLIED' or(RESULT_JSON is not null and APPLIED_AT is not null)))]');
 ensure_table('RRL_STOCK_GUARD',q'[create table RRL_STOCK_GUARD(
  RESOURCE_RANK number(3) not null,RESOURCE_KEY raw(1000) not null,
  RESOURCE_VERSION number default 0 not null,CREATED_AT timestamp default systimestamp not null,
  constraint RRL_STOCK_GUARD_PK primary key(RESOURCE_RANK,RESOURCE_KEY),
  constraint RRL_STOCK_GUARD_RANK_CK check(RESOURCE_RANK in(10,20,30,40,50,60,70)))]');
 ensure_table('RRL_STOCK_POLICY_GUARD',q'[create table RRL_STOCK_POLICY_GUARD(
  POLICY_KEY raw(1000) primary key,LOCK_ID number not null,POLICY_VERSION number default 1 not null,
  CREATED_AT timestamp default systimestamp not null,
  constraint RRL_STOCK_POLICY_ID_UK unique(LOCK_ID),
  constraint RRL_STOCK_POLICY_ID_CK check(LOCK_ID between 900000000 and 949999999))]');
 ensure_table('RRL_STOCK_UOM_CONVERSION',q'[create table RRL_STOCK_UOM_CONVERSION(
  ARTICUL varchar2(160) not null,INPUT_UOM varchar2(20) not null,BASE_UOM varchar2(20) not null,
  POLICY_VERSION number not null,NUMERATOR number not null,DENOMINATOR number not null,
  BASE_SCALE number(2) not null,PROVENANCE varchar2(1000) not null,
  constraint RRL_STOCK_UOM_PK primary key(ARTICUL,INPUT_UOM,POLICY_VERSION),
  constraint RRL_STOCK_UOM_RATIO_CK check(NUMERATOR=trunc(NUMERATOR) and DENOMINATOR=trunc(DENOMINATOR)
   and NUMERATOR between 1 and 1000000000 and DENOMINATOR between 1 and 1000000000),
  constraint RRL_STOCK_UOM_SCALE_CK check(BASE_SCALE between 0 and 9))]');
 ensure_table('RRL_STOCK_WRITER_REGISTRY',q'[create table RRL_STOCK_WRITER_REGISTRY(
  WRITER_KEY varchar2(400) primary key,OWNER_DOMAIN varchar2(40) not null,
  SOURCE_HASH varchar2(64) not null,ADAPTER_REFERENCE varchar2(1000),STATE varchar2(20) not null,
  UPDATED_AT timestamp default systimestamp not null,
  constraint RRL_STOCK_WRITER_STATE_CK check(STATE in('UNCONVERTED','ADAPTED','RETIRED')))]');
 ensure_table('RRL_STOCK_BASELINE',q'[create table RRL_STOCK_BASELINE(
  BASELINE_ID varchar2(100) primary key,SNAPSHOT_SCN number not null,CREATED_AT timestamp default systimestamp not null,
  CREATED_BY varchar2(50) not null,STATE varchar2(20) not null,MANIFEST_HASH varchar2(64) not null,
  constraint RRL_STOCK_B0_STATE_CK check(STATE in('PREPARING','READY')))]');
 ensure_table('RRL_STOCK_B0_ROWS',q'[create table RRL_STOCK_B0_ROWS(
  BASELINE_ID varchar2(100) not null,UID_PALLET varchar2(200) not null,CELL varchar2(60) not null,
  BASE_QTY number not null,HARD_RESERVED_BASE number not null,BASE_UOM varchar2(20) not null,
  STOCK_VERSION number not null,
  constraint RRL_STOCK_B0_ROW_PK primary key(BASELINE_ID,UID_PALLET,CELL),
  constraint RRL_STOCK_B0_ROW_FK foreign key(BASELINE_ID) references RRL_STOCK_BASELINE(BASELINE_ID))]');
 ensure_column('RRL_REMAINS','HARD_RESERVED_BASE','HARD_RESERVED_BASE number default 0 not null');
 ensure_column('RRL_REMAINS','STOCK_VERSION','STOCK_VERSION number default 0 not null');
 ensure_column('RRL_REMAINS','BASE_UOM','BASE_UOM varchar2(20)');
 ensure_column('RRL_STOCK_RESERVATION','BASE_QTY','BASE_QTY number');
 ensure_column('RRL_STOCK_RESERVATION','BASE_UOM','BASE_UOM varchar2(20)');
 ensure_column('RRL_STOCK_RESERVATION','RESERVATION_VERSION','RESERVATION_VERSION number default 0 not null');
 ensure_column('RRL_EVENTS','OPERATION_ID','OPERATION_ID varchar2(100)');
 ensure_column('RRL_EVENTS','LINE_NO','LINE_NO number');
 ensure_column('RRL_EVENTS','LEG_NO','LEG_NO number');
 ensure_column('RRL_EVENTS','BASE_QTY','BASE_QTY number');
 ensure_column('RRL_EVENTS','BASE_UOM','BASE_UOM varchar2(20)');
 ensure_column('RRL_EVENTS','UOM_POLICY_VERSION','UOM_POLICY_VERSION number');
 ensure_column('RRL_EVENTS','ORIGINAL_OPERATION_ID','ORIGINAL_OPERATION_ID varchar2(100)');
 select count(*) into n from user_tab_columns where TABLE_NAME='RRL_REMAINS' and COLUMN_NAME='CELL' and DATA_LENGTH<60;
 if n>0 then execute immediate 'alter table RRL_REMAINS modify(CELL varchar2(60))'; end if;
 select count(*) into n from user_tab_columns where TABLE_NAME='RRL_EVENTS' and COLUMN_NAME='CELL_FROM' and DATA_LENGTH<60;
 if n>0 then execute immediate 'alter table RRL_EVENTS modify(CELL_FROM varchar2(60),CELL_TO varchar2(60))'; end if;
 select count(*) into n from user_constraints where CONSTRAINT_NAME='RRL_REMAINS_HARD_CK';
 if n=0 then execute immediate 'alter table RRL_REMAINS add constraint RRL_REMAINS_HARD_CK check(HARD_RESERVED_BASE>=0 and HARD_RESERVED_BASE<=REMAIN)'; end if;
 select count(*) into n from user_constraints where CONSTRAINT_NAME='RRL_EVENTS_OPERATION_UK';
 if n=0 then execute immediate 'alter table RRL_EVENTS add constraint RRL_EVENTS_OPERATION_UK unique(OPERATION_ID,LINE_NO,LEG_NO)'; end if;
end;
/
merge into RRL_STOCK_RELEASE d using(select 1 RELEASE_ID from dual)s on(d.RELEASE_ID=s.RELEASE_ID)
when not matched then insert(RELEASE_ID,STATE,CHANGED_BY) values(1,'PREPARED',user);
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-08-014-stock-posting-foundation' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Stock posting metadata foundation; release PREPARED, no writer activation',sysdate,user,'014_apply.sql','014_rollback.sql','APPLIED');
commit;