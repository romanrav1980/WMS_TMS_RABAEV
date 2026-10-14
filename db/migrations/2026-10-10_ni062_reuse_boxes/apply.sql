@@001_schema.sql
@@006_repl_policy.sql
@@002_reuse.sql
@@003_receiving.sql
@@004_putaway.sql
@@005_guards.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
declare n number;begin select count(*)into n from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_RETURN_REUSE','RRL_STOCK_STORE_RETURN_REC_CMD','RRL_STOCK_STORE_RETURN_PUT','RRL_RETURN_REUSE_ZONE_GUARD','RRL_RETURN_REUSE_PROOF_GUARD')and STATUS='INVALID';if n!=0 then raise_application_error(-20808,'RETURN_REUSE_INVALID');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-107-return-full-good-box-reuse' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Full ordinary good BOX return source batch and exact BOX UOM proof, separate blocked receiving, existing warehouse task to current configured picking/batch/expiry policy',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
