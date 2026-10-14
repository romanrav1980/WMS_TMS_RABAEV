declare n number;begin
 select count(*) into n from USER_CONS_COLUMNS where CONSTRAINT_NAME='RRL_WH_TASK_STOCK_MOVE_U1' and COLUMN_NAME='UID_PALLET';
 if n=0 then
  execute immediate 'alter table RRL_WAREHOUSE_TASK_STOCK_MOVE drop constraint RRL_WH_TASK_STOCK_MOVE_U1';
  execute immediate 'alter table RRL_WAREHOUSE_TASK_STOCK_MOVE add constraint RRL_WH_TASK_STOCK_MOVE_U1 unique(TASK_ID,UID_PALLET)';
 end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-070-hu-multi-leaf-fact' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Existing warehouse task movement facts allow one row per unique physical leaf instead of one per whole task',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
