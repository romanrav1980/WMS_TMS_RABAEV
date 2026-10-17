-- MIGRATION_ID: 2026-10-15-store-scale-requests
-- Export request history first. Never destroy recorded intent as routine rollback.
declare n number;
begin
 select count(*) into n from RRL_STORE_WEIGH_REQUEST;
 if n!=0 then raise_application_error(-20886,'STORE_WEIGH_REQUEST_EXPORT_AND_EXPLICIT_RECOVERY_REQUIRED');end if;
end;
/
drop trigger RRL_STORE_WEIGH_GUARD;
drop context RRL_STORE_WEIGH_CTX;
drop package RRL_STORE_WEIGH_API;
drop table RRL_STORE_WEIGH_REQUEST;
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-15-store-scale-requests';
commit;
