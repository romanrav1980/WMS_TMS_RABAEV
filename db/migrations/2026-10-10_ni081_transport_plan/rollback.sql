declare n number;begin select count(*)into n from RRL_PLANNER_APPLY_RESULT;
 if n>0 then raise_application_error(-20899,'PLAN136_FORWARD_ONLY_AFTER_APPLY');end if;end;
/
drop table RRL_PLANNER_APPLY_RESULT;
/
drop package RRL_TRANSPORT_PLAN_API;
/
drop package RRL_TRANSPORT_PLAN_RULES;
/
delete from RRL_SCHEMA_MIGRATIONS where MIGRATION_ID='2026-10-10-136-atomic-existing-transport-plan';
commit;
/
