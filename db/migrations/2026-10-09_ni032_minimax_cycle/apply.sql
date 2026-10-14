@@001_schema.sql
declare n number;begin
 select count(*) into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_PICK_WAVE_REPLENISH_TASK' and COLUMN_NAME in('MINIMAX_CYCLE_ID','MINIMAX_TARGET_BASE','MINIMAX_FINISHED_AT');
 if n!=3 then raise_application_error(-20808,'MINIMAX_CYCLE_COLUMNS_MISSING');end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-09-024-minimax-cycle' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Keep original minimax target across partial deliveries until physical MAX is reached',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
