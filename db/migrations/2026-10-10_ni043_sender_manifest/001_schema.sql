begin execute immediate q'[create table RRL_TRACE_SENDER_MANIFEST(
 OPERATION_ID varchar2(100) primary key,PAYLOAD_HASH raw(32) not null,
 SOURCE_KIND varchar2(15) not null check(SOURCE_KIND in('INVENTORY','MES')),SOURCE_DOC_ID number not null,
 WARE_ID number not null,UID_PALLET varchar2(200) not null,ARTICLE varchar2(160) not null,
 BASE_UOM varchar2(20) not null,DECLARED_BASE_QTY number(27,9) not null check(DECLARED_BASE_QTY>0),
 POLICY_VERSION number not null,PROFILES_JSON clob not null check(PROFILES_JSON is json),
 RAW_JSON clob not null check(RAW_JSON is json),RAW_SHA256 varchar2(64) not null,DOCUMENT_REFERENCE varchar2(255) not null,
 ACTOR nvarchar2(50) not null,CREATED_AT timestamp with time zone default systimestamp not null,
 RESULT_JSON clob not null check(RESULT_JSON is json),
 unique(WARE_ID,SOURCE_KIND,SOURCE_DOC_ID,UID_PALLET,RAW_SHA256)
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate q'[create table RRL_TRACE_SENDER_AGG(
 MANIFEST_OPERATION_ID varchar2(100) not null references RRL_TRACE_SENDER_MANIFEST(OPERATION_ID),
 AGGREGATION_ID varchar2(100) not null,SYSTEM_CODE varchar2(40) not null,PROFILE_CODE varchar2(80) not null,
 PROFILE_VERSION varchar2(40) not null,AGG_LEVEL varchar2(10) not null check(AGG_LEVEL in('BOX','PALLET')),
 CODE_HASH varchar2(64) not null,RAW_CODE clob not null,UNITS_JSON clob not null check(UNITS_JSON is json),
 primary key(MANIFEST_OPERATION_ID,SYSTEM_CODE,PROFILE_CODE,CODE_HASH,AGG_LEVEL)
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate q'[create table RRL_TRACE_MANIFEST_USE(
 MANIFEST_OPERATION_ID varchar2(100) primary key references RRL_TRACE_SENDER_MANIFEST(OPERATION_ID),
 STOCK_OPERATION_ID varchar2(100) not null references RRL_STOCK_OPERATION(OPERATION_ID),
 UID_PALLET varchar2(200) not null,ACTOR nvarchar2(50) not null,CREATED_AT timestamp with time zone default systimestamp not null
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate 'create index RRL_TRACE_SENDER_WARE_IX on RRL_TRACE_SENDER_MANIFEST(WARE_ID,CREATED_AT,OPERATION_ID)';exception when others then if sqlcode!=-955 then raise;end if;end;
/

declare v_type varchar2(30);n number;begin
 select DATA_TYPE into v_type from USER_TAB_COLUMNS where TABLE_NAME='RRL_TRACE_SENDER_AGG'and COLUMN_NAME='PROFILE_VERSION';
 if v_type='NUMBER' then
  select count(*)into n from RRL_TRACE_SENDER_AGG;if n!=0 then raise_application_error(-20899,'TRACE_PROFILE_TEXT_SCHEMA_HISTORY_REQUIRES_EXPLICIT_CONVERSION');end if;
  execute immediate 'alter table RRL_TRACE_SENDER_AGG modify(PROFILE_VERSION varchar2(40))';
 end if;
end;
/
