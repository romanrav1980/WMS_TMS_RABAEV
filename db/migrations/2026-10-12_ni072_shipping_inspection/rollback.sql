declare n number;begin
 select count(*)into n from RRL_DAY_INSPECTION;
 if n!=0 then raise_application_error(-20886,'DAY_INSPECTION_HISTORY_PREVENTS_ROLLBACK');end if;
 execute immediate 'drop trigger RRL_DAY_INSPECT_GUARD';
 execute immediate 'drop package RRL_DAY_INSPECT_API';
 execute immediate 'drop table RRL_DAY_INSPECTION';
 delete from RIGHTS where upper(RIGHT1)='WAREHOUSE_DAY_INSPECT'and USER_GROUP='GLOBAL_ADMIN';
 update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-12-692-shipping-zone-inspection';
end;
/
