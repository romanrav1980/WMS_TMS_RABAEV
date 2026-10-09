declare n number;
begin
 select count(*) into n from RRL_STOCK_OPERATION;
 if n>0 then raise_application_error(-20808,'Posting operations exist; preserve arithmetic contract'); end if;
end;
/
drop package RRL_STOCK_MATH;
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-08-015-stock-exact-arithmetic';
commit;
