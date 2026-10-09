@@067_internal_legacy_checkpoint.sql
@@067_internal_entrypoints.sql
declare n number;begin
 select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_INTERNAL_MOVE2','RRL_INTERNAL_MOVE3','RRL_INTERNAL_MOVE2_SP_OLD','RRL_INTERNAL_MOVE3_SP_OLD') and OBJECT_TYPE='FUNCTION' and STATUS='VALID';
 if n!=4 then raise_application_error(-20808,'INTERNAL_ENTRYPOINTS_NOT_VALID');end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-08-027-internal-entrypoints' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Existing internal move entrypoints switch globally to stock coordinator; PREPARED legacy fallback',sysdate,user,'067_internal_entrypoints_apply.sql','067_internal_entrypoints_rollback.sql','APPLIED');
commit;
