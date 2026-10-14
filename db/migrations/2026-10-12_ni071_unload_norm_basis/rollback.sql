declare n number;begin
 select count(*)into n from RRL_TRANSPORT_NORM_HISTORY where json_exists(RESULT_JSON,'$.unload_charge_basis');
 if n>0 then raise_application_error(-20886,'EXPLICIT_NORM_FACTS_REQUIRE_FORWARD_REPAIR');end if;
end;
/
@@000_before_norm.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-12-572-explicit-unload-cost-basis';
