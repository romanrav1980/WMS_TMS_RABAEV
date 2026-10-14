declare n number;begin select count(*)into n from RRL_IW_GROUP_PLAN;if n!=0 then raise_application_error(-20899,'GROUP_PLANS_REQUIRE_FORWARD_RECOVERY');end if;end;
/
@@000_before_plan_guard.sql
drop trigger RRL_IW_GROUP_PLAN_GUARD;
drop package RRL_IW_GROUP_SOURCE;
drop table RRL_IW_GROUP_PLAN;
delete from RRL_SCHEMA_MIGRATIONS where MIGRATION_ID='2026-10-12-403-grouped-interware-plan';
commit;
