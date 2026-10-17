-- MIGRATION_ID: 2026-10-15-warehouse-scale-zero-progress
@@before.sql
@@schema.sql
@@spec.sql
@@body.sql
@@guard.sql
alter package RRL_WH_SCALE_API compile body;
alter package RRL_ASSEMBLY_SCALE_API compile body;
alter trigger RRL_WH_WEIGH_REQUEST_GUARD compile;
alter trigger RRL_WH_WEIGH_CLAIM_GUARD compile;
declare n number;begin select count(*)into n from USER_ERRORS where NAME in('RRL_WH_WEIGH_REQUEST_API','RRL_WH_WEIGH_ZERO_GUARD','RRL_WH_SCALE_API','RRL_ASSEMBLY_SCALE_API','RRL_WH_WEIGH_REQUEST_GUARD','RRL_WH_WEIGH_CLAIM_GUARD');if n!=0 then raise_application_error(-20886,'WH_ZERO_COMPILE_ERRORS');end if;select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n!=0 then raise_application_error(-20886,'WH_ZERO_GLOBAL_INVALID');end if;end;
/
@@verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-15-warehouse-scale-zero-progress'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when matched then update set d.STATUS='APPLIED',d.APPLIED_AT=sysdate,d.APPLIED_BY=user where d.STATUS='ROLLED_BACK'
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'Gateway-reported immutable actual zero; current lease/context UX stage, no stock effect',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
