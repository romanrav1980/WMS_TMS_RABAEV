@@001_schema.sql
@@002_planning.sql
@@003_availability.sql
@@004_command.sql
@@005_root.sql
@@006_guards.sql
@@007_resolution_command.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
declare n number;begin select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_TARE_LOSS','RRL_STOCK_POSTING_API','RRL_TARE_PLANNING','RRL_TARE_AVAILABILITY','RRL_TARE_LOSS_PENDING','RRL_TARE_LOSS_CLAIM_GUARD','RRL_TARE_LOSS_DEC_GUARD') and STATUS='INVALID';if n!=0 then raise_application_error(-20808,'TARE_LOSS_INVALID');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-105-warehouse-tare-loss' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Warehouse tare loss claim excludes suspected quantity from availability; independent full decision writeoff or rejection, immutable Root history',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
