prompt NI01 physical marking units and sender aggregation manifests
declare
 procedure ensure_table(p_name varchar2,p_ddl varchar2) is n number;
 begin select count(*) into n from user_tables where table_name=p_name;
 if n=0 then execute immediate p_ddl; end if; end;
begin
 if user!='RABAEV' or lower(sys_context('USERENV','SERVICE_NAME'))!='orcl' then raise_application_error(-20801,'Existing RABAEV/orcl only'); end if;
 ensure_table('RRL_SAP_TRACE_AGG',q'[
 create table RRL_SAP_TRACE_AGG(
 ORDER_ID varchar2(32) not null,LINE_NUMBER varchar2(20) not null,SYSTEM_CODE varchar2(40) not null,
 PROFILE_CODE varchar2(80) not null,CODE_HASH varchar2(64) not null,AGG_LEVEL varchar2(10) not null,
 RAW_CODE clob not null,UNITS_JSON clob not null,
 constraint RRL_SAP_TAGG_PK primary key(ORDER_ID,SYSTEM_CODE,PROFILE_CODE,CODE_HASH),
 constraint RRL_SAP_TAGG_LINE_FK foreign key(ORDER_ID,LINE_NUMBER) references RRL_SAP_SUPPLY_LINE(ORDER_ID,LINE_NUMBER),
 constraint RRL_SAP_TAGG_LVL check(AGG_LEVEL in('BOX','PALLET')),constraint RRL_SAP_TAGG_JSON check(UNITS_JSON is json))]');
 ensure_table('RRL_WMS_RECEIPT_UNIT',q'[
 create table RRL_WMS_RECEIPT_UNIT(
 UID_PALLET varchar2(200) not null,UNIT_ID varchar2(100) not null,POLICY_VERSION number not null,
 constraint RRL_WMS_REC_UNIT_PK primary key(UID_PALLET,UNIT_ID),
 constraint RRL_WMS_REC_UNIT_FK foreign key(UID_PALLET) references RRL_SAP_PALLET_RECEIPT(UID_PALLET) deferrable initially deferred)]');
 ensure_table('RRL_WMS_RECEIPT_CODE',q'[
 create table RRL_WMS_RECEIPT_CODE(
 SYSTEM_CODE varchar2(40) not null,CODE_HASH varchar2(64) not null,UID_PALLET varchar2(200) not null,
 UNIT_ID varchar2(100) not null,RAW_CODE clob not null,PROFILES_JSON clob not null,
 constraint RRL_WMS_REC_CODE_PK primary key(SYSTEM_CODE,CODE_HASH),
 constraint RRL_WMS_REC_CODE_FK foreign key(UID_PALLET,UNIT_ID) references RRL_WMS_RECEIPT_UNIT(UID_PALLET,UNIT_ID),
 constraint RRL_WMS_REC_CODE_JSON check(PROFILES_JSON is json))]');
 ensure_table('RRL_WMS_RECEIPT_AGG',q'[
 create table RRL_WMS_RECEIPT_AGG(
 SYSTEM_CODE varchar2(40) not null,CODE_HASH varchar2(64) not null,UID_PALLET varchar2(200) not null,
 PROFILE_CODE varchar2(80) not null,AGG_LEVEL varchar2(10) not null,RAW_CODE clob not null,
 constraint RRL_WMS_REC_AGG_PK primary key(SYSTEM_CODE,CODE_HASH),
 constraint RRL_WMS_REC_AGG_FK foreign key(UID_PALLET) references RRL_SAP_PALLET_RECEIPT(UID_PALLET) deferrable initially deferred,
 constraint RRL_WMS_REC_AGG_LVL check(AGG_LEVEL in('BOX','PALLET')))]');
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-07-004-ni01-receipt-marking' MIGRATION_ID from dual)s
on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'NI01 physical unit code capture and known source aggregation composition',sysdate,user,'004_apply.sql','004_rollback.sql','APPLIED');
commit;
