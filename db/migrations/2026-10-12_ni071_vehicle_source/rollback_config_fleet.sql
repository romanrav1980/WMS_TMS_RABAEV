declare n number;begin select count(*)into n from RRL_VEHICLE_PROFILE_HIST;
 if n!=0 then raise_application_error(-20886,'VEHICLE_PROFILE_FACTS_REQUIRE_FORWARD_REPAIR');end if;end;
/
@@000_before_config_fleet.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-12-564-config-fleet-permission';
