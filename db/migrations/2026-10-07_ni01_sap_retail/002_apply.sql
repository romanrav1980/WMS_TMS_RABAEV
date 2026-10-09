prompt NI01 article application and warehouse supply plans
declare
 procedure ensure_table(p_name varchar2,p_ddl varchar2) is n number;
 begin
 select count(*) into n from user_tables where table_name=p_name;
 if n=0 then execute immediate p_ddl; end if;
 end;
 procedure ensure_column(p_name varchar2,p_ddl varchar2) is n number;
 begin
 select count(*) into n from user_tab_columns where table_name='RRL_SAP_IDOC_INBOX' and column_name=p_name;
 if n=0 then execute immediate p_ddl; end if;
 end;
begin
 if user!='RABAEV' or lower(sys_context('USERENV','SERVICE_NAME'))!='orcl' then
 raise_application_error(-20801,'Existing RABAEV/orcl only'); end if;
 ensure_column('LAST_ERROR','alter table RRL_SAP_IDOC_INBOX add LAST_ERROR varchar2(2000)');
 ensure_column('RESULT_JSON','alter table RRL_SAP_IDOC_INBOX add RESULT_JSON clob');
 ensure_table('RRL_SAP_ARTICLE_META',q'[
 create table RRL_SAP_ARTICLE_META(
 ARTICUL varchar2(40) not null,BASE_UOM varchar2(20) not null,SENDER varchar2(100) not null,
 SOURCE_STAMP varchar2(14) not null,SOURCE_DOCNUM varchar2(16) not null,UNITS_JSON clob not null,
 constraint RRL_SAP_ART_META_PK primary key(ARTICUL),constraint RRL_SAP_ART_META_JSON check(UNITS_JSON is json))]');
 ensure_table('RRL_SAP_SUPPLY_ORDER',q'[
 create table RRL_SAP_SUPPLY_ORDER(
 ORDER_ID varchar2(32) not null,SENDER varchar2(100) not null,ORDER_NUMBER varchar2(20) not null,
 NAKLAD_ID number not null,REVISION number not null,PAYLOAD_HASH varchar2(64) not null,
 WARE_ID number not null,RECEIVE_CELL varchar2(60) not null,
 UPDATED_AT timestamp default systimestamp not null,
 constraint RRL_SAP_SUP_ORD_PK primary key(ORDER_ID),
 constraint RRL_SAP_SUP_ORD_UK unique(SENDER,ORDER_NUMBER),
 constraint RRL_SAP_SUP_NAK_UK unique(NAKLAD_ID),constraint RRL_SAP_SUP_REV_CK check(REVISION>0))]');
 ensure_table('RRL_SAP_SUPPLY_LINE',q'[
 create table RRL_SAP_SUPPLY_LINE(
 ORDER_ID varchar2(32) not null,LINE_NUMBER varchar2(20) not null,ROW_ID number not null,
 ARTICUL varchar2(40) not null,PLANNED_QTY number not null,BASE_UOM varchar2(20) not null,
 SOURCE_QTY number not null,SOURCE_UOM varchar2(20) not null,
 constraint RRL_SAP_SUP_LINE_PK primary key(ORDER_ID,LINE_NUMBER),
 constraint RRL_SAP_SUP_ROW_UK unique(ROW_ID),constraint RRL_SAP_SUP_ART_UK unique(ORDER_ID,ARTICUL),
 constraint RRL_SAP_SUP_LINE_FK foreign key(ORDER_ID) references RRL_SAP_SUPPLY_ORDER(ORDER_ID),
 constraint RRL_SAP_SUP_QTY_CK check(PLANNED_QTY>0 and SOURCE_QTY>0))]');
 ensure_table('RRL_SAP_SUPPLY_MESSAGE',q'[
 create table RRL_SAP_SUPPLY_MESSAGE(
 SENDER varchar2(100) not null,MESSAGE_ID varchar2(100) not null,ORDER_ID varchar2(32) not null,
 PAYLOAD_HASH varchar2(64) not null,RAW_XML clob not null,RESULT_JSON clob not null,
 RECEIVED_AT timestamp default systimestamp not null,RECEIVED_BY varchar2(100) not null,
 constraint RRL_SAP_SUP_MSG_PK primary key(SENDER,MESSAGE_ID),
 constraint RRL_SAP_SUP_MSG_FK foreign key(ORDER_ID) references RRL_SAP_SUPPLY_ORDER(ORDER_ID),
 constraint RRL_SAP_SUP_MSG_JSON check(RESULT_JSON is json))]');
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-07-002-ni01-sap-supply' MIGRATION_ID from dual)s
on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'NI01 article application and SAP warehouse supply plans',sysdate,user,'002_apply.sql','002_rollback.sql','APPLIED');
commit;
