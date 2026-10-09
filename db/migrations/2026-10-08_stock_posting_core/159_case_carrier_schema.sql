-- Physical carrier membership; quantity and location remain in RRL_REMAINS.
declare n number;v varchar2(20);begin
 select STATE into v from RRL_STOCK_RELEASE where RELEASE_ID=1;
 if v!='PREPARED' then raise_application_error(-20808,'DORMANT_SCHEMA_REQUIRES_PREPARED');end if;
 select count(*) into n from USER_TABLES where TABLE_NAME='RRL_CASE_CARRIER_LOT';
 if n=0 then execute immediate 'create table RRL_CASE_CARRIER_LOT(
  LOT_UID varchar2(150) primary key,
  CASE_PICK_TASK_ID number not null references RRL_CASE_PICK_TASK(CASE_PICK_TASK_ID),
  CASE_PICK_LINE_ID number not null references RRL_CASE_PICK_LINE(CASE_PICK_LINE_ID),
  CREATED_OPERATION varchar2(100) not null references RRL_STOCK_OPERATION(OPERATION_ID),
  CREATED_AT timestamp default systimestamp not null,
  CREATED_BY varchar2(100) not null)';end if;
 select count(*) into n from USER_INDEXES where INDEX_NAME='IX_RRL_CASE_CARRIER_TASK';
 if n=0 then execute immediate 'create index IX_RRL_CASE_CARRIER_TASK on RRL_CASE_CARRIER_LOT(CASE_PICK_TASK_ID,CASE_PICK_LINE_ID)';end if;
 select count(*) into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_CASE_PICK_TASK' and COLUMN_NAME='CURRENT_CELL';
 if n=0 then execute immediate 'alter table RRL_CASE_PICK_TASK add(CURRENT_CELL varchar2(60))';end if;
 select count(*) into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_CASE_PICK_TASK' and COLUMN_NAME='CONTENT_VERSION';
 if n=0 then execute immediate 'alter table RRL_CASE_PICK_TASK add(CONTENT_VERSION number default 0 not null)';end if;
end;
/
create or replace trigger RRL_CASE_CARRIER_LOT_GUARD
 before insert or update or delete on RRL_CASE_CARRIER_LOT for each row
declare task_id number;uid varchar2(150);begin
 if sys_context('RRL_STOCK_WRITE_CTX','MODE') is null or sys_context('RRL_STOCK_WRITE_CTX','MODE')!='EXPLICIT'
  or sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null
  or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false) then
  raise_application_error(-20863,'CASE_CARRIER_MEMBERSHIP_POSTING_REQUIRED');end if;
 task_id:=case when deleting then :old.CASE_PICK_TASK_ID else :new.CASE_PICK_TASK_ID end;
 uid:=case when deleting then :old.LOT_UID else :new.LOT_UID end;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_CASE_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(task_id)));
 RRL_STOCK_LOCK_API.assert_held(30,RRL_STOCK_LOCK_API.resource_key('HU',uid));
end;
/
