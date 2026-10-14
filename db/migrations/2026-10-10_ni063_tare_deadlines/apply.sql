@@001_schema.sql
@@002_policy_helper.sql
@@003_tare_command.sql
@@004_debt_view.sql
@@005_guards.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
declare n number;begin select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_TARE_POLICY','RRL_STOCK_TARE_CMD','RRL_TARE_STORE_DEBT','RRL_TARE_POLICY_GUARD','RRL_TARE_DELIVERY_POLICY_GUARD') and STATUS='INVALID';if n!=0 then raise_application_error(-20808,'TARE_DEADLINE_INVALID');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-099-tare-return-deadlines' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Frozen store/client return policy in actual tare delivery, explicit timezone, read-only FIFO debt and real next-store-delivery deadline; no retrospective deadline invention',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
