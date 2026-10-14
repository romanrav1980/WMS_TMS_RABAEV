@@001_schema.sql
@@004_metadata_permission.sql
@@002_api.sql
@@003_guards.sql
declare n number;begin
 select count(*)into n from USER_OBJECTS where OBJECT_NAME in('RRL_WORKLOAD_CONFIG_API','RRL_WORKLOAD_OPERATION_G','RRL_WORKLOAD_NORM_G','RRL_WORKLOAD_ATTEND_G','RRL_WORKLOAD_CANCEL_G')and STATUS!='VALID';
 if n!=0 then raise_application_error(-20899,'WORKLOAD134_INVALID');end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-134-workload-norm-planned-attendance' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'Versioned SKU BASE picking norm, person-level aware planned attendance; original resource registry retained; no stock writes',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
