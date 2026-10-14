declare n number;begin select count(*)into n from RRL_IW_GROUP_PUT_PLAN;if n!=0 then raise_application_error(-20899,'GROUP_PLACEMENT_TASKS_REQUIRE_FORWARD_RECOVERY');end if;end;
/
@@000_before_hu_task.sql
@@000_before_hu_cmd.sql
drop trigger RRL_IW_GROUP_PLACEMENT_GUARD;
drop trigger RRL_IW_GROUP_PUT_PLAN_GUARD;
drop package RRL_IW_GROUP_PUT_GUARD;
drop package RRL_IW_GROUP_PUT;
drop table RRL_IW_GROUP_PLACEMENT;
drop table RRL_IW_GROUP_PUT_PLAN;
alter package RRL_STOCK_POSTING_API compile body;
delete from RRL_SCHEMA_MIGRATIONS where MIGRATION_ID='2026-10-12-417-grouped-interware-placement';
commit;
