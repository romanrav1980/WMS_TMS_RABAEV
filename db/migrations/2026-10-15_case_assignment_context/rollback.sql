declare n number;begin select count(*)into n from RRL_CASE_RESOURCE_COMMAND;if n!=0 then raise_application_error(-20886,'CASE_ASSIGNMENT_CONTEXT_HISTORY_RETAIN');end if;end;
/
drop context RRL_CASE_ASSIGNMENT_CTX;
/
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-15-case-assignment-context';
commit;
