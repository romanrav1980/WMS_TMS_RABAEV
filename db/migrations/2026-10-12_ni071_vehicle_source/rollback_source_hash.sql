declare n number;
begin select count(*)into n from RRL_VEHICLE_PROFILE_HIST;
 if n!=0 then raise_application_error(-20886,'VEHICLE_PROFILE_HISTORY_FORWARD_REPAIR_REQUIRED');end if;
end;
/
@@000_before_source_hash.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-12-561-vehicle-profile-base-hash';
