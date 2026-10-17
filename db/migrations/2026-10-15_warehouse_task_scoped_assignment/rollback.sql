@@after_source_guard.sql
declare n number;begin
 select count(*)into n from RRL_WTASK_RESOURCE_COMMAND;if n!=0 then raise_application_error(-20886,'WTASK_RECEIPT_HISTORY_FORWARD_ONLY');end if;
 select count(*)into n from RRL_WTASK_ASSIGN_VERSION;if n!=0 then raise_application_error(-20886,'WTASK_VERSION_HISTORY_FORWARD_ONLY');end if;
end;
/
drop trigger RRL_WTASK_IDENTITY_GUARD;
drop trigger RRL_WTASK_ASSIGN_DERIVE;
drop trigger RRL_WTASK_COMMAND_GUARD;
drop trigger RRL_WTASK_VERSION_GUARD;
@@before_access_spec.sql
@@before_access_body.sql
@@before_resource_policy.sql
alter package RRL_STOCK_TASK_PLAN compile body;
alter package RRL_STOCK_TASK_CORE compile body;
alter package RRL_STOCK_POSTING_API compile body;
alter package RRL_STOCK_HU_TASK compile body;
alter package RRL_ST_DEFER_CASE_WAIT compile body;
drop context RRL_WTASK_ASSIGN_CTX;
drop package RRL_WTASK_ASSIGN_API;
drop package RRL_WTASK_VERSION_API;
drop table RRL_WTASK_RESOURCE_COMMAND;
drop table RRL_WTASK_ASSIGN_VERSION;
@@rollback_verify.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-15-warehouse-task-scoped-assignment';
commit;
