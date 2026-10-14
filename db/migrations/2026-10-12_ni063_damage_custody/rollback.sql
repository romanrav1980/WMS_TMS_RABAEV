declare n number;
begin
 select count(*)into n from RRL_TARE_DAMAGE_ORIGIN;
 if n!=0 then raise_application_error(-20886,'TARE_DAMAGE_TRACE_FACTS_EXIST_FORWARD_REPAIR_REQUIRED');end if;
end;
/
@@000_before_tare.sql
@@000_before_resolve.sql
@@000_before_loss.sql
drop table RRL_TARE_DAMAGE_MOVE;
drop table RRL_TARE_DAMAGE_OFFER;
drop table RRL_TARE_DAMAGE_POSITION;
drop table RRL_TARE_DAMAGE_ORIGIN;
drop package RRL_TARE_DAMAGE_TRACE;
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-12-552-tare-damage-custody';
