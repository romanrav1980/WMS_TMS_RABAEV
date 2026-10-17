-- Reviewed additive rollback; same exact-source and empty-history criteria.
-- Quiesce CASE/TASK metadata writers and disable new HTTP composition first.
@@after_source_guard.sql
declare n number;begin select count(*)into n from RRL_RESOURCE_INTENT_ABANDON;
 if n!=0 then raise_application_error(-20886,'RESOURCE_INTENT_HISTORY_FORWARD_ONLY');end if;end;
/
@@before_case_spec.sql
@@before_task_spec.sql
@@before_case_body.sql
@@before_task_body.sql
drop trigger RRL_RESOURCE_INTENT_GUARD;
drop context RRL_RESOURCE_INTENT_CTX;
drop package RRL_RESOURCE_INTENT_API;
drop table RRL_RESOURCE_INTENT_ABANDON;
begin dbms_utility.compile_schema(schema=>user,compile_all=>false);end;
/
@@rollback_verify_current.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-15-resource-metadata-intents';
commit;
