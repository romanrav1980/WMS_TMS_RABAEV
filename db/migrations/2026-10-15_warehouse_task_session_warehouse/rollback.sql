@@after_source_guard.sql
declare n number;begin select count(*)into n from RRL_WTASK_RESOURCE_COMMAND;if n!=0 then raise_application_error(-20886,'WTASK_SESSION_RECEIPT_HISTORY_FORWARD_ONLY');end if;end;
/
@@before_body.sql
@@../2026-10-15_warehouse_task_scoped_assignment/after_source_guard.sql
declare n number;begin select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n!=0 then raise_application_error(-20886,'WTASK_SESSION_ROLLBACK_INVALID');end if;end;
/
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-15-warehouse-task-session-warehouse';
commit;
