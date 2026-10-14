@@001_schema.sql
@@003_debt.sql
@@002_command.sql
@@004_tare_command.sql
@@005_resolution_command.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
declare n number;begin select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_TARE_LOSS','RRL_STOCK_TARE_CMD','RRL_STOCK_TARE_RESOLVE','RRL_TARE_STORE_DEBT')and STATUS='INVALID';if n!=0 then raise_application_error(-20808,'TARE_HOLDER_LOSS_INVALID');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-106-store-vehicle-tare-loss' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Current store/driver loss observation, original store claim/custody/balance caps, pending unusable quantity and independent decision',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
