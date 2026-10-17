-- Preserve immutable intent, claim and evidence history.
declare n number;begin
 select (select count(*)from RRL_WH_WEIGH_REQUEST)+(select count(*)from RRL_WH_WEIGH_CLAIM)into n from dual;
 if n!=0 then raise_application_error(-20886,'WH_WEIGH_HISTORY_EXPORT_EXPLICIT_RECOVERY_REQUIRED');end if;
end;
/
@@000_before_wh_scale_api.sql
@@000_before_assembly_body.sql
drop trigger RRL_WH_WEIGH_CLAIM_GUARD;
drop trigger RRL_WH_WEIGH_REQUEST_GUARD;
drop package RRL_WH_WEIGH_REQUEST_API;
drop table RRL_WH_WEIGH_CLAIM;
drop table RRL_WH_WEIGH_REQUEST;
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-15-warehouse-scale-requests';
commit;

