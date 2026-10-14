declare n number;begin select count(*)into n from RRL_TRANSPORT_COST_CLAIM;
 if n!=0 then raise_application_error(-20886,'TRANSPORT_COST_FACTS_REQUIRE_FORWARD_REPAIR');end if;end;
/
drop trigger RRL_TRAN_COST_DETAIL_GUARD;
drop trigger RRL_TRAN_COST_CLAIM_GUARD;
drop table RRL_TRANSPORT_COST_DETAIL;
drop table RRL_TRANSPORT_COST_CLAIM;
drop package RRL_TRANSPORT_COST_API;
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-12-582-transport-q26-recognition';
