@@001_schema.sql
@@002_command.sql
@@003_load_guard.sql
@@004_root.sql
@@005_active_index.sql
@@006_proof_guard.sql
alter trigger RRL_TT_HU_LOAD_FACT_GUARD compile;
declare n number;begin select count(*)into n from user_objects where OBJECT_NAME in('RRL_STOCK_INTERWARE_CUSTODY','RRL_STOCK_POSTING_API','RRL_TT_HU_LOAD_FACT_GUARD','RRL_INTERWARE_CUSTODY_GUARD','RRL_TT_HU_LOAD_UID_U1')and STATUS!='VALID';if n!=0 then raise_application_error(-20899,'INTERWARE121_INVALID_OBJECTS');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-121-interwarehouse-first-leg-custody-release' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'Explicit native custody release on actual target receipt while preserving original departure history and active UID uniqueness',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
