-- Add recovery state to existing shortage/inventory objects; preserve business history.
declare
 procedure add_column(t varchar2,c varchar2,ddl varchar2) is n number;begin
  select count(*) into n from USER_TAB_COLUMNS where TABLE_NAME=t and COLUMN_NAME=c;
  if n=0 then execute immediate ddl;end if;
 end;
begin
 add_column('RRL_CASE_PICK_SHORT','RECOVERY_STATE','alter table RRL_CASE_PICK_SHORT add RECOVERY_STATE varchar2(24)');
 add_column('RRL_CASE_PICK_SHORT','RECOVERY_DEADLINE_AT','alter table RRL_CASE_PICK_SHORT add RECOVERY_DEADLINE_AT timestamp');
 add_column('RRL_CASE_PICK_SHORT','REPLENISH_TASK_ID','alter table RRL_CASE_PICK_SHORT add REPLENISH_TASK_ID number');
 add_column('RRL_CASE_PICK_SHORT','RECOVERY_WORKER','alter table RRL_CASE_PICK_SHORT add RECOVERY_WORKER varchar2(100)');
 add_column('RRL_CASE_PICK_SHORT','RECOVERY_LEASE_UNTIL','alter table RRL_CASE_PICK_SHORT add RECOVERY_LEASE_UNTIL timestamp');
 add_column('RRL_CASE_PICK_SHORT','RECOVERY_ATTEMPTS','alter table RRL_CASE_PICK_SHORT add RECOVERY_ATTEMPTS number default 0 not null');
 add_column('RRL_CASE_PICK_SHORT','RECOVERY_LAST_ERROR','alter table RRL_CASE_PICK_SHORT add RECOVERY_LAST_ERROR varchar2(1000)');
 add_column('RRL_CASE_PICK_SHORT','RECOVERY_SOURCE_REQUEST','alter table RRL_CASE_PICK_SHORT add RECOVERY_SOURCE_REQUEST clob');
 add_column('RRL_CASE_PICK_SHORT','RESTORED_AT','alter table RRL_CASE_PICK_SHORT add RESTORED_AT timestamp');
 add_column('RRL_INVENTORY_TASK','PRIORITY','alter table RRL_INVENTORY_TASK add PRIORITY number default 100 not null');
 add_column('RRL_INVENTORY_TASK','REVISION_ID','alter table RRL_INVENTORY_TASK add REVISION_ID number');
 add_column('RRL_INVENTORY_TASK','COUNT_OPERATION_ID','alter table RRL_INVENTORY_TASK add COUNT_OPERATION_ID varchar2(100)');
 add_column('RRL_CASE_PICK_SETTING','SHORT_CONFIRM_MODE','alter table RRL_CASE_PICK_SETTING add SHORT_CONFIRM_MODE varchar2(20) default ''AUDITOR'' not null');
 add_column('RRL_CASE_PICK_SETTING','SHORT_RECOVERY_SLA_SECONDS','alter table RRL_CASE_PICK_SETTING add SHORT_RECOVERY_SLA_SECONDS number default 300 not null');
end;
/
declare n number;begin
 select count(*) into n from USER_CONSTRAINTS where CONSTRAINT_NAME='RRL_SHORT_RECOVERY_STATE_CK';
 if n=0 then execute immediate 'alter table RRL_CASE_PICK_SHORT add constraint RRL_SHORT_RECOVERY_STATE_CK check(RECOVERY_STATE in(''WAIT_INVENTORY'',''WAIT_REPLENISHMENT'',''READY'',''RESUMED'',''FAILED''))';end if;
 select count(*) into n from USER_CONSTRAINTS where CONSTRAINT_NAME='RRL_SHORT_RECOVERY_SETTING_CK';
 if n=0 then execute immediate 'alter table RRL_CASE_PICK_SETTING add constraint RRL_SHORT_RECOVERY_SETTING_CK check(SHORT_CONFIRM_MODE in(''SELF'',''AUDITOR'') and SHORT_RECOVERY_SLA_SECONDS between 1 and 300 and SHORT_RECOVERY_SLA_SECONDS=trunc(SHORT_RECOVERY_SLA_SECONDS))';end if;
 select count(*) into n from USER_INDEXES where INDEX_NAME='RRL_SHORT_RECOVERY_QUEUE_I';
 if n=0 then execute immediate 'create index RRL_SHORT_RECOVERY_QUEUE_I on RRL_CASE_PICK_SHORT(RECOVERY_STATE,RECOVERY_DEADLINE_AT,CASE_PICK_SHORT_ID)';end if;
 select count(*) into n from USER_INDEXES where INDEX_NAME='RRL_SHORT_REPLENISH_U';
 if n=0 then execute immediate 'create unique index RRL_SHORT_REPLENISH_U on RRL_CASE_PICK_SHORT(REPLENISH_TASK_ID)';end if;
end;
/
