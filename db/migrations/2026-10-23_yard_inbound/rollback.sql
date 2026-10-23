whenever sqlerror exit failure rollback
@@verify.sql
declare n number;begin select count(*)into n from RRL_YARD_VISIT where VISIT_KIND='INBOUND';if n<>0 then raise_application_error(-20999,'INBOUND_HISTORY_PRESENT');end if;end;
/
@@before_spec.sql
@@before_body.sql
drop trigger RRL_YARD_SUPPLY_GUARD;
drop package RRL_YARD_SUPPLY_API;
drop table RRL_YARD_VISIT_SUPPLY purge;
@@recompile_dependents.sql
@@rollback_verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-23-yard-inbound' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)when matched then update set STATUS='ROLLED_BACK',APPLIED_AT=sysdate,APPLIED_BY=user when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'Inbound yard visits from accepted supplies, operator vehicle and current owner access',sysdate,user,'apply.sql','rollback.sql','ROLLED_BACK');
commit;
