declare n number;m number;
begin
 select count(*)into n from RRL_TT_VEHICLE_SOURCE;
 select count(*)into m from RRL_VEHICLE_PROFILE_HIST;
 if n+m!=0 then raise_application_error(-20886,'VEHICLE_PROFILE_SOURCE_FACTS_EXIST_FORWARD_REPAIR_REQUIRED');end if;
end;
/
@@000_before_depart.sql
drop table RRL_TT_VEHICLE_SOURCE;
drop package RRL_VEH_DEPART_SOURCE;
drop table RRL_VEHICLE_PROFILE_HIST;
drop table RRL_VEHICLE_PROFILE_HEAD;
drop package RRL_VEHICLE_PROFILE_API;
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-12-559-vehicle-source-at-departure';
