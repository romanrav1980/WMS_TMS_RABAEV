-- MIGRATION_ID: 2026-10-14-1447-ni051-scoped-quality
declare n number;begin
 select count(*) into n from USER_TABLES where TABLE_NAME='RRL_QC_SCOPE_RULE';
 if n=0 then execute immediate 'create table RRL_QC_SCOPE_RULE(
 WARE_ID number not null, STORE_ADDR varchar2(255) not null,
 PLACE_CATEGORY varchar2(10) not null check(PLACE_CATEGORY in(''ANY'',''STOCK'',''CASE'')),
 RULE_VERSION number not null check(RULE_VERSION>=1), ACTIVE_FLAG number(1) not null check(ACTIVE_FLAG in(0,1)),
 CONTROL_MODE varchar2(10) not null check(CONTROL_MODE in(''NONE'',''ANY'',''SCAN'',''WEIGHT'',''BOTH'')),
 INDEPENDENT_FLAG number(1) not null check(INDEPENDENT_FLAG in(0,1)),
 SAMPLE_PERCENT number(5,2) not null check(SAMPLE_PERCENT between 0 and 100),
 EXEMPT_WHOLE number(1) not null check(EXEMPT_WHOLE in(0,1)),
 EXEMPT_STORAGE number(1) not null check(EXEMPT_STORAGE in(0,1)),
 UPDATED_BY varchar2(100) not null, UPDATED_AT timestamp default systimestamp not null,
 constraint RRL_QC_SCOPE_RULE_PK primary key(WARE_ID,STORE_ADDR,PLACE_CATEGORY))';end if;
 select count(*) into n from USER_TABLES where TABLE_NAME='RRL_QC_SCOPE_CHANGE';
 if n=0 then execute immediate 'create table RRL_QC_SCOPE_CHANGE(
 OPERATION_ID varchar2(100) primary key, ACTOR varchar2(100) not null,
 REQUEST_HASH varchar2(64) not null, REQUEST_JSON clob not null check(REQUEST_JSON is json),
 RESULT_JSON clob not null check(RESULT_JSON is json), CREATED_AT timestamp default systimestamp not null)';end if;
 select count(*) into n from USER_TABLES where TABLE_NAME='RRL_QC_EXEMPT_FACT';
 if n=0 then execute immediate 'create table RRL_QC_EXEMPT_FACT(
 OPERATION_ID varchar2(100) not null references RRL_STOCK_OPERATION(OPERATION_ID),
 DOCUMENT_ID number not null references RRL_SBORKA_PALLETS(ID),
 PAYLOAD_JSON clob not null check(PAYLOAD_JSON is json), CREATED_AT timestamp default systimestamp not null,
 constraint RRL_QC_EXEMPT_FACT_PK primary key(OPERATION_ID,DOCUMENT_ID))';end if;
end;
/
create or replace trigger RRL_QC_SCOPE_RULE_GUARD before insert or update or delete on RRL_QC_SCOPE_RULE for each row
declare n number;begin
 if nvl(sys_context('RRL_STOCK_WRITE_CTX','MODE'),chr(0))!='CONFIG'
 or nvl(sys_context('RRL_STOCK_WRITE_CTX','CONFIG_PERMISSION'),chr(0))!='warehouse_settings_edit'
 or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null
 or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)
 then raise_application_error(-20863,'QUALITY_SCOPE_CONFIGURATION_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),6);
 if not deleting then select count(*) into n from RRL_WARES where ID=:new.WARE_ID;if n!=1 then raise_application_error(-20886,'QUALITY_SCOPE_WAREHOUSE_MISSING_OR_AMBIGUOUS');end if;end if;
end;
/
create or replace trigger RRL_QC_SCOPE_CHANGE_GUARD before insert or update or delete on RRL_QC_SCOPE_CHANGE
begin
 if updating or deleting then raise_application_error(-20863,'QUALITY_SCOPE_HISTORY_IMMUTABLE');end if;
 if nvl(sys_context('RRL_STOCK_WRITE_CTX','MODE'),chr(0))!='CONFIG'
 or nvl(sys_context('RRL_STOCK_WRITE_CTX','CONFIG_PERMISSION'),chr(0))!='warehouse_settings_edit'
 or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null
 or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)
 then raise_application_error(-20863,'QUALITY_SCOPE_CONFIGURATION_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),6);
end;
/
create or replace trigger RRL_QC_EXEMPT_FACT_GUARD before insert or update or delete on RRL_QC_EXEMPT_FACT for each row
begin
 if updating or deleting then raise_application_error(-20863,'QUALITY_EXEMPTION_IMMUTABLE');end if;
 if sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID') is null
 or sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')!=:new.OPERATION_ID
 or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null
 or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)
 then raise_application_error(-20863,'QUALITY_EXEMPTION_ROOT_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_SBORKA_PALLETS',RRL_STOCK_PLAN_HELPER.decimal_text(:new.DOCUMENT_ID)));
end;
/
