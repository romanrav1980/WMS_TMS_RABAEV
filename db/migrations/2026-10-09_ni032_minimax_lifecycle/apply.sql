@@001_schema.sql
declare n number;begin
 select count(*) into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_PICK_WAVE_REPLENISH_TASK' and COLUMN_NAME='RESERVE_OPERATION_ID';
 if n!=1 then raise_application_error(-20808,'MINIMAX_DURABLE_INTENT_MISSING');end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-09-023-minimax-lifecycle' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Durable source reservation identity for existing minimax replenishment rows',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
