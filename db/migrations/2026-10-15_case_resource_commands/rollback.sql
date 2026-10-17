-- Quiesce CASE metadata writers. Preserve any successful/rejected receipt or derived revision history.
declare n number;begin
 select count(*)into n from RRL_CASE_RESOURCE_COMMAND;if n!=0 then raise_application_error(-20886,'CASE_RESOURCE_RECEIPT_HISTORY_FORWARD_REPAIR');end if;
 select count(*)into n from RRL_CASE_PICK_TASK where ASSIGNMENT_VERSION!=0;if n!=0 then raise_application_error(-20886,'CASE_RESOURCE_REVISION_HISTORY_FORWARD_REPAIR');end if;
end;
/
@@before_start_guard.sql
@@before_resource_policy_body.sql
@@before_case_access_spec.sql
@@before_case_access_body.sql
drop trigger RRL_CASE_RESOURCE_CMD_GUARD;
drop trigger RRL_CASE_ASSIGN_VERSION_GUARD;
drop context RRL_CASE_ASSIGNMENT_CTX;
drop package RRL_CASE_ASSIGNMENT_API;
drop table RRL_CASE_RESOURCE_COMMAND;
alter table RRL_CASE_PICK_TASK drop column ASSIGNMENT_VERSION;
begin dbms_utility.compile_schema(schema=>user,compile_all=>false);end;
/
declare n number;begin
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n!=0 then raise_application_error(-20886,'CASE_RESOURCE_ROLLBACK_INVALID');end if;
 select count(*)into n from USER_ERRORS where NAME in('RRL_CASE_TASK_ACCESS','RRL_CASE_RESOURCE_POLICY','RRL_CASE_START_TIME_GUARD');if n!=0 then raise_application_error(-20886,'CASE_RESOURCE_ROLLBACK_ERRORS');end if;
end;
/
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-15-case-resource-commands';
commit;
