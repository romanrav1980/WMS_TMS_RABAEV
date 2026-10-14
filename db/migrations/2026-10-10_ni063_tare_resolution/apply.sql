@@001_schema.sql
@@002_participant.sql
@@004_debt_view.sql
@@003_command.sql
@@005_tare_command.sql
@@006_root.sql
@@007_guards.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
declare n number;begin select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_TARE_PARTICIPANT','RRL_STOCK_TARE_RESOLVE','RRL_STOCK_TARE_CMD','RRL_STOCK_POSTING_API','RRL_TARE_STORE_DEBT','RRL_TARE_RESOLUTION_GUARD','RRL_TARE_BALANCE_GUARD') and STATUS='INVALID';if n!=0 then raise_application_error(-20808,'TARE_RESOLUTION_INVALID');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-100-tare-damage-writeoff' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Owned tare GOOD to DAMAGED, independent transport loss decision, original store debt/deadline preserved; immutable resolution/sameRoot/no goods stock',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
