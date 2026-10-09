-- 2026-10-09-001: physical CASE carrier -> existing prepared ST pallet.
declare n number;s varchar2(20);begin
 select STATE into s from RRL_STOCK_RELEASE where RELEASE_ID=1;
 if s!='PREPARED' then raise_application_error(-20808,'DORMANT_SCHEMA_REQUIRES_PREPARED');end if;
 select count(*) into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_CASE_PICK_TASK' and COLUMN_NAME='LEGACY_SBORKA_PALLET_ID';
 if n=0 then execute immediate 'alter table RRL_CASE_PICK_TASK add(
  LEGACY_SBORKA_PALLET_ID number,
  SHIPPED_OPERATION varchar2(100) references RRL_STOCK_OPERATION(OPERATION_ID))';end if;
 select count(*) into n from USER_CONSTRAINTS where CONSTRAINT_NAME='RRL_CASE_SHIPMENT_UK';
 if n=0 then execute immediate 'alter table RRL_CASE_PICK_TASK add constraint RRL_CASE_SHIPMENT_UK unique(LEGACY_SBORKA_PALLET_ID)';end if;
 execute immediate 'alter table RRL_CASE_PICK_TASK drop constraint RRL_CASE_PICK_TASK_CHK1';
 execute immediate q'[alter table RRL_CASE_PICK_TASK add constraint RRL_CASE_PICK_TASK_CHK1 check(
 STATUS in ('NEW','ASSIGNED','IN_PROGRESS','WAIT_REPLENISHMENT','PARTIAL','PICKED',
 'WAIT_CONTROL','CONTROL_IN_PROGRESS','CONTROLLED','READY_TO_SHIP','SYNC_CONFLICT','CANCELLED','FAILED','SHIPPED'))]';
end;
/
