@@001_schema.sql
@@002_rules.sql
@@003_apply.sql
@@004_guard.sql
declare n number;begin
 select count(*)into n from USER_OBJECTS where OBJECT_NAME in('RRL_TRANSPORT_PLAN_RULES','RRL_TRANSPORT_PLAN_API','RRL_PLANNER_APPLY_GUARD')and STATUS!='VALID';
 if n!=0 then raise_application_error(-20899,'TRANSPORT_PLAN136_INVALID');end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-136-atomic-existing-transport-plan' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'Same-transaction existing VRP trip/member application, immutable result, shared prospective capacity/type rules; no stock writer',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
