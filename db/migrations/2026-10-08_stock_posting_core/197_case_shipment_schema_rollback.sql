declare n number;begin
 select count(*) into n from RRL_CASE_PICK_TASK where LEGACY_SBORKA_PALLET_ID is not null or SHIPPED_OPERATION is not null or STATUS='SHIPPED';
 if n>0 then raise_application_error(-20808,'CASE_SHIPMENT_BINDINGS_PREVENT_SCHEMA_ROLLBACK');end if;
 execute immediate 'alter table RRL_CASE_PICK_TASK drop constraint RRL_CASE_PICK_TASK_CHK1';
 execute immediate q'[alter table RRL_CASE_PICK_TASK add constraint RRL_CASE_PICK_TASK_CHK1 check(
 STATUS in ('NEW','ASSIGNED','IN_PROGRESS','WAIT_REPLENISHMENT','PARTIAL','PICKED',
 'WAIT_CONTROL','CONTROL_IN_PROGRESS','CONTROLLED','READY_TO_SHIP','SYNC_CONFLICT','CANCELLED','FAILED'))]';
 execute immediate 'alter table RRL_CASE_PICK_TASK drop constraint RRL_CASE_SHIPMENT_UK';
 execute immediate 'alter table RRL_CASE_PICK_TASK drop column SHIPPED_OPERATION';
 execute immediate 'alter table RRL_CASE_PICK_TASK drop column LEGACY_SBORKA_PALLET_ID';
end;
/
