@@001_schema.sql
@@002_key.sql
@@004_package.sql
@@005_root.sql
@@006_guards.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
declare n number;begin select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_TARE_BALANCE_KEY','RRL_TARE_ASSERT_WRITE','RRL_STOCK_TARE_CMD','RRL_STOCK_POSTING_API','RRL_TARE_BALANCE_GUARD','RRL_TARE_OFFER_GUARD','RRL_TARE_ACCEPT_GUARD','RRL_TARE_JOURNAL_GUARD') and STATUS='INVALID';if n!=0 then raise_application_error(-20808,'TARE_LEDGER_INVALID');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-098-tare-quantity-ledger' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Separate owned tare counts and two-participant existing-trip custody transfers through one Root; no goods stock or nested HU duplication',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
